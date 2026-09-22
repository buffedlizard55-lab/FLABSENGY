"""Monte-Carlo slate simulator.

Mirrors the *publicly described steps* of simulation-based lineup tools
(SimLabs FAQ [S19][S20][S21]):

  1. simulate player/game outcomes many times,
  2. build a large pool of lineups from those draws,
  3. approximate an ownership/field distribution,
  4. score each lineup against the simulated field ("universe") to produce
     relative ratings (their tiles are 0-99 projection / pOWN [S19]).

Field-shaping parameters and their proprietary calibration are NOT public
(I15). This is an original, seeded, dependency-free implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

from .optimizer import Lineup, LineupOptimizer, OptimizerConfig, PlayerRow


@dataclass
class SimConfig:
    n_sims: int = 2000
    n_lineups: int = 20
    field_size: int = 1000          # simulated contest field size
    seed: Optional[int] = 42
    contest_type: str = "gpp"       # "gpp" | "cash" — shapes field model
    # player outcome model: points ~ lognormal around projection with
    # volatility `vol` (coefficient of variation). Original choice; their
    # per-sport vol calibration is proprietary.
    vol: float = 0.45
    # ownership model: softmax over projections (chalkier fields for cash)
    ownership_temperature: float = 8.0


@dataclass
class SimPlayerOutcome:
    player_id: str
    mean: float
    p15: float
    p85: float
    sim_points: np.ndarray  # shape (n_sims,)


@dataclass
class SimLineupResult:
    lineup: Lineup
    sim_totals: np.ndarray       # (n_sims,)
    mean_total: float
    p95_total: float             # ceiling-like statistic
    p05_total: float             # floor-like statistic
    opt_rate: float              # share of sims where this lineup beats field p90
    project_rel: int             # 0-99 projection rel rating (cf. [S19])
    own_rel: Optional[int]       # 0-99 ownership rel rating


@dataclass
class SimResult:
    players: Dict[str, SimPlayerOutcome]
    lineups: List[SimLineupResult]
    field_p90: float
    config: SimConfig

    def summary(self) -> Dict[str, object]:
        return {
            "n_sims": self.config.n_sims,
            "candidate_lineups": len(self.lineups),
            "field_p90": round(self.field_p90, 2),
            "best_mean": round(max((L.mean_total for L in self.lineups),
                                   default=float("nan")), 2),
        }


class SlateSimulator:
    def __init__(self, players: Sequence[PlayerRow], config: Optional[SimConfig] = None):
        if not players:
            raise ValueError("empty pool")
        self.players = list(players)
        self.config = config or SimConfig()
        if self.config.n_sims < 100:
            raise ValueError("n_sims too small for stable ratings")
        if self.config.vol <= 0:
            raise ValueError("vol must be positive")

    def run(self, optimizer_config: Optional[OptimizerConfig] = None) -> SimResult:
        cfg = self.config
        rng = np.random.default_rng(cfg.seed)

        # --- 1. simulate player outcomes --------------------------------
        outcomes: Dict[str, SimPlayerOutcome] = {}
        for p in self.players:
            mu = max(p.projection, 0.1)
            # lognormal parameterized to mean=mu, CV=vol
            sigma2 = np.log(1.0 + cfg.vol ** 2)
            sigma = np.sqrt(sigma2)
            shape = np.log(mu) - 0.5 * sigma2
            draws = rng.lognormal(mean=shape, sigma=sigma, size=cfg.n_sims)
            outcomes[p.id] = SimPlayerOutcome(
                player_id=p.id, mean=float(mu),
                p15=float(np.percentile(draws, 15)),
                p85=float(np.percentile(draws, 85)),
                sim_points=draws,
            )

        # --- 2. candidate lineup pool ------------------------------------
        opt_cfg = optimizer_config or OptimizerConfig(
            slots=_default_slots(self.players),
            salary_cap=50000.0,
            rng_seed=cfg.seed,
        )
        optimizer = LineupOptimizer(self.players, opt_cfg)
        jitter = 0.05 * max(p.projection for p in self.players)
        lineups = optimizer.best(n=cfg.n_lineups, jitter=jitter)
        if not lineups:
            raise RuntimeError("no feasible lineups for simulation")

        # --- 3. field model ----------------------------------------------
        # Cash fields: chalk-heavy (low temperature => sharper softmax).
        temp = cfg.ownership_temperature
        if cfg.contest_type == "cash":
            temp = temp * 0.5
        logits = np.array([p.projection / 10.0 for p in self.players]) / max(temp / 8.0, 1e-6)
        exp = np.exp(logits - logits.max())
        weights = exp / exp.sum()

        # Build `field_size` random lineups lazily via projection-weighted
        # greedy sampling — approximates a chalky human field.
        field_totals = np.empty(cfg.field_size, dtype=float)
        pool_ids = [p.id for p in self.players]
        idx_of = {p.id: i for i, p in enumerate(self.players)}
        for i in range(cfg.field_size):
            picks: List[PlayerRow] = []
            salary = 0.0
            used: Set[str] = set()
            # sample players proportional to weights until roster full
            tries = 0
            need = len(opt_cfg.slots)
            while len(picks) < need and tries < need * 50:
                tries += 1
                j = int(rng.choice(len(pool_ids), p=weights))
                p = self.players[j]
                if p.id in used:
                    continue
                if salary + p.salary > opt_cfg.salary_cap:
                    continue
                # slot feasibility quick check
                if any(not p.eligible(s) for s in [_first_free_slot(opt_cfg.slots, picks)]):
                    continue
                picks.append(p)
                used.add(p.id)
                salary += p.salary
            if len(picks) == need and _all_slots_ok(picks, opt_cfg.slots):
                field_totals[i] = sum(outcomes[p.id].sim_points[rng.integers(cfg.n_sims)]
                                      for p in picks)
            else:
                # fallback: sum top projections (keeps distribution defined)
                field_totals[i] = sum(p.projection for p in picks)
        field_p90 = float(np.percentile(field_totals, 90 if cfg.contest_type == "gpp" else 50))

        # --- 4. rate candidate lineups vs universe ------------------------
        results: List[SimLineupResult] = []
        own_means = np.array([
            (p.ownership if p.ownership is not None else float(np.mean(weights[idx_of[p.id]] * 1000)))
            for p in self.players
        ])
        for lu in lineups:
            # sum aligned sim draws: re-draw independently per player
            totals = np.zeros(cfg.n_sims)
            for p in lu.players:
                totals += outcomes[p.id].sim_points
            opt_rate = float(np.mean(totals > field_p90))
            results.append(SimLineupResult(
                lineup=lu,
                sim_totals=totals,
                mean_total=float(totals.mean()),
                p95_total=float(np.percentile(totals, 95)),
                p05_total=float(np.percentile(totals, 5)),
                opt_rate=opt_rate,
                project_rel=_rel90([r.mean_total for r in results], float(totals.mean()))
                if results else 50,
                own_rel=_rel90(list(own_means[
                    [idx_of[p.id] for p in lu.players]
                ]), float(np.mean([
                    own_means[idx_of[p.id]] for p in lu.players
                ]))) if True else None,
            ))

        # normalize rel ratings to full 0-99 across pool
        means = [r.mean_total for r in results]
        lo, hi = min(means), max(means)
        for r in results:
            r.project_rel = int(round(99 * (r.mean_total - lo) / (hi - lo))) if hi > lo else 50
        own_vals = [r.own_rel for r in results if r.own_rel is not None]
        if own_vals:
            olo, ohi = min(own_vals), max(own_vals)
            for r in results:
                if r.own_rel is not None:
                    r.own_rel = int(round(99 * (r.own_rel - olo) / (ohi - olo))) if ohi > olo else 50

        results.sort(key=lambda r: r.mean_total, reverse=True)
        return SimResult(players=outcomes, lineups=results,
                         field_p90=field_p90, config=cfg)


def _rel90(history: List[float], value: float) -> int:
    if not history:
        return 50
    lo, hi = min(min(history), value), max(max(history), value)
    if hi <= lo:
        return 50
    return int(round(99 * (value - lo) / (hi - lo)))


def _default_slots(players: Sequence[PlayerRow]) -> List[str]:
    positions = {p.position for p in players}
    if {"QB", "RB", "WR", "TE", "DST"} <= positions:
        return ["QB", "RB", "RB", "WR", "WR", "WR", "TE", "FLEX", "DST"]
    # fallback generic
    return sorted(positions)


def _first_free_slot(slots: List[str], picks: List[PlayerRow]) -> str:
    remaining = list(slots)
    for p in picks:
        for i, s in enumerate(remaining):
            if p.eligible(s):
                remaining.pop(i)
                break
    return remaining[0] if remaining else slots[0]


def _all_slots_ok(picks: List[PlayerRow], slots: List[str]) -> bool:
    if len(picks) != len(slots):
        return False
    # exact matching
    def match(i: int, avail: List[str]) -> bool:
        if i == len(picks):
            return True
        p = picks[i]
        for j, s in enumerate(avail):
            if p.eligible(s):
                if match(i + 1, avail[:j] + avail[j + 1:]):
                    return True
        return False
    return match(0, list(slots))
