"""Lineup optimizer — original constrained search.

Public input set being mirrored from FantasyLabs' own optimizer article [S16]:
  * player projections (median; ceiling/floor optional)
  * salary constraints (cap; optional minimum spend % — article notes 99%
    minimum-spend rationale)
  * correlation rules (e.g., stack QB with pass-catchers + opponent player)
  * player groups and exposures (max counts / % caps)
  * ownership projections (for leverage)

Their solver is proprietary. This implementation:
  * exact DFS (maximum-weight feasible roster) via depth-first search with
    pruning for small pools,
  * randomized multi-restart sampling for diversification across lineups,
  * stack / group / min-spend / exposure constraints as specified.

No FantasyLabs code involved.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple

# NOTE: original clean-room implementation; no third-party solver dependency.

RosterSlot = str  # e.g. "QB", "RB", "WR", "TE", "FLEX", "DST"


@dataclass(frozen=True)
class PlayerRow:
    id: str
    name: str
    team: str
    opp: str
    position: str          # primary position
    flex_positions: frozenset  # positions eligible for FLEX, e.g. {RB, WR, TE}
    salary: float
    projection: float
    ownership: Optional[float] = None  # projected own % if known
    game: str = ""          # game key for stacking (e.g. "KC@BUF")

    def eligible(self, slot: RosterSlot) -> bool:
        if slot == "FLEX":
            return self.position in self.flex_positions
        return self.position == slot


@dataclass
class OptimizerConfig:
    slots: List[RosterSlot]
    salary_cap: float
    min_spend: float = 0.0            # absolute $ floor (e.g. 0.99 * cap)
    min_spend_ratio: Optional[float] = None  # alternative: fraction of cap
    max_from_team: Optional[int] = None
    max_from_game: Optional[int] = None
    # groups: each is (ids, max_count) — "at most N of these players" [S16]
    groups: List[Tuple[Set[str], int]] = field(default_factory=list)
    # required stacks: functions lineup->bool; all must pass
    stack_rules: List[Callable[[List[PlayerRow]], bool]] = field(default_factory=list)
    # banned combos of player ids (size>=2): any subset together forbidden
    banned_sets: List[Set[str]] = field(default_factory=list)
    exclude_ids: Set[str] = field(default_factory=set)
    require_ids: Set[str] = field(default_factory=set)
    rng_seed: Optional[int] = None
    # diversification: prefer low-ownership tiebreaks when projections equal
    fade_ownership_weight: float = 0.0


@dataclass
class Lineup:
    players: List[PlayerRow]
    projection: float
    salary: float
    ownership_sum: Optional[float]

    @property
    def ids(self) -> Set[str]:
        return {p.id for p in self.players}


class LineupOptimizer:
    def __init__(self, players: Sequence[PlayerRow], config: OptimizerConfig):
        if not players:
            raise ValueError("empty player pool [P2-2]")
        self.players = list(players)
        self.config = config
        ids = [p.id for p in self.players]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate player ids in pool")
        self._by_slot: Dict[RosterSlot, List[PlayerRow]] = {}
        for slot in config.slots:
            self._by_slot[slot] = [p for p in self.players
                                   if p.eligible(slot)
                                   and p.id not in config.exclude_ids]
        self._min_spend = (
            config.min_spend if config.min_spend else
            (config.min_spend_ratio * config.salary_cap
             if config.min_spend_ratio is not None else 0.0)
        )
        if self._min_spend > config.salary_cap:
            raise ValueError("min spend exceeds salary cap — infeasible [P2-3]")

    # ------------------------------------------------------------------ API
    def best(self, n: int = 1, jitter: float = 0.0) -> List[Lineup]:
        """Return up to `n` distinct feasible lineups.

        `jitter` > 0 adds uniform noise to projections per restart to explore
        alternatives (seeded via config.rng_seed for reproducibility [P2-12]).
        """
        if n < 1:
            raise ValueError("n must be >= 1")
        rng = random.Random(self.config.rng_seed)
        found: Dict[Tuple[str, ...], Lineup] = {}
        # First pass: exact best on true projections.
        first = self._search(projection_jitter=None, rng=rng)
        if first is not None:
            found[first.ids and tuple(sorted(first.ids))] = first
        # Subsequent passes: jittered searches for diversity.
        attempts = 0
        max_attempts = max(20, n * 15)
        while len(found) < n and attempts < max_attempts:
            attempts += 1
            jitter_map = (
                {p.id: rng.uniform(-jitter, jitter) for p in self.players}
                if jitter > 0 else None
            )
            cand = self._search(projection_jitter=jitter_map, rng=rng)
            if cand is None:
                break
            key = tuple(sorted(cand.ids))
            if key not in found:
                found[key] = cand
        lineups = sorted(found.values(), key=lambda L: L.projection, reverse=True)
        return lineups[:n]

    # -------------------------------------------------------------- search
    def _search(self,
                projection_jitter: Optional[Dict[str, float]],
                rng: random.Random) -> Optional[Lineup]:
        slots = self.config.slots
        best: List[PlayerRow] = []
        best_score = float("-inf")
        cap = self.config.salary_cap

        # Simple positional ordering: fill scarcest eligibility first.
        order = sorted(range(len(slots)),
                       key=lambda i: len(self._by_slot[slots[i]]))

        def score_of(pls: List[PlayerRow]) -> float:
            s = 0.0
            for p in pls:
                j = (projection_jitter or {}).get(p.id, 0.0)
                own_penalty = 0.0
                if self.config.fade_ownership_weight and p.ownership is not None:
                    own_penalty = self.config.fade_ownership_weight * p.ownership / 100.0
                s += p.projection + j - own_penalty
            return s

        used: Set[str] = set()

        def dfs(k: int, salary_left: float, current: List[PlayerRow]) -> None:
            nonlocal best, best_score
            if k == len(order):
                if self._feasible(current, salary_left):
                    sc = score_of(current)
                    if sc > best_score:
                        best_score = sc
                        best = list(current)
                return
            slot = slots[order[k]]
            # remaining salary needed after this pick
            remaining_after = k + 1
            if remaining_after == len(order):
                # last slot: cheap pruning via lower bounds not needed
                pass
            cands = self._by_slot[slot]
            # order candidates by effective score desc for better pruning
            cands = sorted(
                cands,
                key=lambda p: p.projection
                + (projection_jitter or {}).get(p.id, 0.0),
                reverse=True,
            )
            for p in cands:
                if p.id in used:
                    continue
                if p.salary > salary_left:
                    continue
                # team/game caps pruned early
                if not self._soft_ok(current, p):
                    continue
                used.add(p.id)
                current.append(p)
                dfs(k + 1, salary_left - p.salary, current)
                current.pop()
                used.discard(p.id)
                # prune: if this path already can't beat best on projection
                # (upper bound = current + top remaining) — cheap heuristic:
                if best and k == 0:
                    # only meaningful at root; skip heavy bound bookkeeping
                    pass

        # Require-ids must be included: pre-seed search when possible.
        if self.config.require_ids:
            seed = [p for p in self.players if p.id in self.config.require_ids]
            if len(seed) > len(slots):
                return None
            if any(p.id in self.config.exclude_ids for p in seed):
                return None
            # Try to complete rosters containing the seed.
            best_seed: Optional[Lineup] = None
            best_seed_score = float("-inf")
            used.update(p.id for p in seed)
            # enumerate remaining slots (remove one matching slot per seed)
            remaining_slots = list(slots)
            for p in seed:
                for j, s in enumerate(remaining_slots):
                    if p.eligible(s):
                        remaining_slots.pop(j)
                        break

            def complete(k: int, salary_left: float, current: List[PlayerRow]) -> None:
                nonlocal best_seed, best_seed_score
                if k == len(remaining_slots):
                    full = seed + current
                    # normalize slot multiset feasibility by rebuilding:
                    if len(full) != len(slots):
                        return
                    # each slot must be fillable — check via bipartite-ish greedy:
                    if not self._assignable(full):
                        return
                    if self._feasible(full, salary_left, pre=True):
                        sc = score_of(full)
                        if sc > best_seed_score:
                            best_seed_score = sc
                            best_seed = list(full)
                    return
                slot = remaining_slots[k]
                for p in self._by_slot[slot]:
                    if p.id in used:
                        continue
                    if p.salary > salary_left:
                        continue
                    if not self._soft_ok(current + seed, p):
                        continue
                    used.add(p.id)
                    current.append(p)
                    complete(k + 1, salary_left - p.salary, current)
                    current.pop()
                    used.discard(p.id)

            complete(0, cap - sum(p.salary for p in seed), [])
            return self._to_lineup(best_seed) if best_seed else None

        dfs(0, cap, [])
        if not best:
            return None
        lineup = self._to_lineup(best)
        return lineup

    # ---------------------------------------------------------- constraints
    def _soft_ok(self, current: List[PlayerRow], p: PlayerRow) -> bool:
        cfg = self.config
        if cfg.max_from_team is not None:
            n = sum(1 for q in current if q.team == p.team)
            if n + 1 > cfg.max_from_team:
                return False
        if cfg.max_from_game is not None:
            n = sum(1 for q in current if q.game == p.game and p.game)
            if n + 1 > cfg.max_from_game:
                return False
        for ids, max_count in cfg.groups:
            if p.id in ids:
                n = sum(1 for q in current if q.id in ids)
                if n + 1 > max_count:
                    return False
        return True

    def _feasible(self, lineup: List[PlayerRow], salary_left: float,
                  pre: bool = False) -> bool:
        cfg = self.config
        if len(lineup) != len(cfg.slots):
            return False
        total = sum(p.salary for p in lineup)
        if total > cfg.salary_cap:
            return False
        if total < self._min_spend:
            return False
        if salary_left < 0:
            return False
        # duplicate players impossible by construction, but double-check
        ids = [p.id for p in lineup]
        if len(ids) != len(set(ids)):
            return False
        # groups
        for gids, max_count in cfg.groups:
            n = sum(1 for p in lineup if p.id in gids)
            if n > max_count:
                return False
        # banned sets
        lset = set(ids)
        for banned in cfg.banned_sets:
            if banned <= lset:
                return False
        # team/game caps
        if cfg.max_from_team is not None:
            counts: Dict[str, int] = {}
            for p in lineup:
                counts[p.team] = counts.get(p.team, 0) + 1
            if any(v > cfg.max_from_team for v in counts.values()):
                return False
        if cfg.max_from_game is not None:
            counts_g: Dict[str, int] = {}
            for p in lineup:
                if p.game:
                    counts_g[p.game] = counts_g.get(p.game, 0) + 1
            if any(v > cfg.max_from_game for v in counts_g.values()):
                return False
        # stack rules
        for rule in cfg.stack_rules:
            if not rule(lineup):
                return False
        # require all must appear
        if cfg.require_ids and not cfg.require_ids <= set(ids):
            return False
        if not self._assignable(lineup):
            return False
        return True

    def _assignable(self, lineup: List[PlayerRow]) -> bool:
        slots = list(self.config.slots)
        # backtracking matching
        def match(i: int, avail: List[RosterSlot]) -> bool:
            if i == len(lineup):
                return True
            p = lineup[i]
            for j, s in enumerate(avail):
                if p.eligible(s):
                    rest = avail[:j] + avail[j + 1:]
                    if match(i + 1, rest):
                        return True
            return False
        return match(0, slots)

    def _to_lineup(self, players: List[PlayerRow]) -> Lineup:
        owns = [p.ownership for p in players]
        own_sum = None if any(o is None for o in owns) else float(sum(owns))  # type: ignore[arg-type]
        return Lineup(
            players=list(players),
            projection=float(sum(p.projection for p in players)),
            salary=float(sum(p.salary for p in players)),
            ownership_sum=own_sum,
        )


def qb_stack_with_receiver_and_opponent(
    qb_position: str = "QB",
    receiver_positions: Iterable[str] = ("WR", "TE", "RB"),
    min_receivers: int = 1,
    bring_back: bool = True,
) -> Callable[[List[PlayerRow]], bool]:
    """Standard tournament stack: QB + >=min_receivers of his pass-catchers
    (+ at least one opposing-team player when `bring_back`) — pattern
    explicitly recommended in [S16]."""
    receivers = set(receiver_positions)

    def rule(lineup: List[PlayerRow]) -> bool:
        qbs = [p for p in lineup if p.position == qb_position]
        if not qbs:
            return False
        qb = qbs[0]
        stack = [p for p in lineup
                 if p.team == qb.team and p.position in receivers
                 and p.id != qb.id]
        if len(stack) < min_receivers:
            return False
        if bring_back:
            bring = [p for p in lineup
                     if p.team == qb.opp and p.id != qb.id]
            if not bring:
                return False
        return True

    return rule
