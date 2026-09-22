"""Optimizer tests — feasibility, constraints, edge cases (P2-2)."""

import pytest

from fantasylab_engine.optimizer import (
    LineupOptimizer,
    OptimizerConfig,
    PlayerRow,
    qb_stack_with_receiver_and_opponent,
)


def P(pid, name, team, opp, pos, salary, proj, game="", own=None):
    # flex_positions = FLEX-only eligibility (empty for QB/DST).
    flex = frozenset({"RB", "WR", "TE"}) if pos in {"RB", "WR", "TE"} else frozenset()
    return PlayerRow(id=pid, name=name, team=team, opp=opp, position=pos,
                     flex_positions=flex, salary=salary, projection=proj,
                     ownership=own, game=game or f"{team}x{opp}")


def _pool():
    players = []
    # QBs
    players += [
        P("qb1", "Alpha", "AAA", "BBB", "QB", 7000, 22.0),
        P("qb2", "Bravo", "CCC", "DDD", "QB", 6000, 18.0),
    ]
    # pass catchers on qb1's team + bring-back
    players += [
        P("wr1", "WR1", "AAA", "BBB", "WR", 7000, 16.0),
        P("wr2", "WR2", "AAA", "BBB", "WR", 5000, 12.0),
        P("wr3", "OppWR", "BBB", "AAA", "WR", 6000, 14.0),
        P("te1", "TE1", "CCC", "DDD", "TE", 4000, 9.0),
        P("wr4", "WR4", "EEE", "FFF", "WR", 4500, 11.0),
        P("wr5", "WR5", "GGG", "HHH", "WR", 3000, 8.0),
    ]
    # RBs / FLEX
    players += [
        P("rb1", "RB1", "CCC", "DDD", "RB", 8000, 18.0),
        P("rb2", "RB2", "EEE", "FFF", "RB", 5500, 13.0),
        P("rb3", "RB3", "GGG", "HHH", "RB", 4000, 10.0),
        P("rb4", "RB4", "III", "JJJ", "RB", 3500, 9.5),
    ]
    # TE extra + DST
    players += [
        P("te2", "TE2", "KKK", "LLL", "TE", 3500, 8.5),
        P("dst1", "D1", "AAA", "BBB", "DST", 3000, 8.0),
        P("dst2", "D2", "EEE", "FFF", "DST", 2500, 7.0),
        P("dst3", "D3", "GGG", "HHH", "DST", 2000, 6.0),
    ]
    return players


def _cfg(**kw):
    base = dict(
        slots=["QB", "RB", "RB", "WR", "WR", "WR", "TE", "FLEX", "DST"],
        salary_cap=50000,
        rng_seed=7,
    )
    base.update(kw)
    return OptimizerConfig(**base)


def test_best_returns_feasible_lineup():
    opt = LineupOptimizer(_pool(), _cfg())
    lineups = opt.best(n=1)
    assert len(lineups) == 1
    lu = lineups[0]
    assert len(lu.players) == 9
    assert lu.salary <= 50000
    assert lu.salary > 0
    # positional validity via matching
    assert opt._assignable(lu.players)
    # uniqueness
    assert len({p.id for p in lu.players}) == 9


def test_min_spend_ratio_enforced():
    opt = LineupOptimizer(_pool(), _cfg(min_spend_ratio=0.99))
    lu = opt.best(n=1)[0]
    assert lu.salary >= 0.99 * 50000


def test_infeasible_min_spend_raises():
    with pytest.raises(ValueError):
        LineupOptimizer(_pool(), _cfg(min_spend=60000))  # > cap


def test_empty_pool_raises():
    with pytest.raises(ValueError):
        LineupOptimizer([], _cfg())


def test_duplicate_ids_raise():
    pool = _pool()
    pool.append(pool[0])
    with pytest.raises(ValueError):
        LineupOptimizer(pool, _cfg())


def test_empty_pool_best_none_behavior():
    # pool with no DST eligibility -> infeasible roster => best() returns []
    pool = [p for p in _pool() if p.position != "DST"]
    opt = LineupOptimizer(pool, _cfg())
    assert opt.best(n=1) == []


def test_group_max_count():
    pool = _pool()
    # at most 1 of wr1/wr2
    cfg = _cfg(groups=[({"wr1", "wr2"}, 1)])
    opt = LineupOptimizer(pool, cfg)
    lu = opt.best(n=1)[0]
    used = {"wr1", "wr2"} & {p.id for p in lu.players}
    assert len(used) <= 1


def test_exclude_and_require():
    pool = _pool()
    cfg = _cfg(exclude_ids={"qb1"}, require_ids={"qb2"})
    opt = LineupOptimizer(pool, cfg)
    lu = opt.best(n=1)[0]
    ids = {p.id for p in lu.players}
    assert "qb1" not in ids
    assert "qb2" in ids


def test_max_from_team():
    cfg = _cfg(max_from_team=2)
    opt = LineupOptimizer(_pool(), cfg)
    lu = opt.best(n=1)[0]
    counts = {}
    for p in lu.players:
        counts[p.team] = counts.get(p.team, 0) + 1
    assert max(counts.values()) <= 2


def test_stack_rule():
    cfg = _cfg(stack_rules=[
        qb_stack_with_receiver_and_opponent(min_receivers=1, bring_back=True)
    ])
    opt = LineupOptimizer(_pool(), cfg)
    lu = opt.best(n=1)[0]
    qbs = [p for p in lu.players if p.position == "QB"]
    assert len(qbs) == 1
    qb = qbs[0]
    stack = [p for p in lu.players if p.team == qb.team
             and p.position in {"WR", "RB", "TE"} and p.id != qb.id]
    bring = [p for p in lu.players if p.team == qb.opp and p.id != qb.id]
    assert stack and bring


def test_banned_sets():
    cfg = _cfg(banned_sets=[{"qb1", "dst1"}])
    opt = LineupOptimizer(_pool(), cfg)
    lu = opt.best(n=1)[0]
    ids = {p.id for p in lu.players}
    assert not {"qb1", "dst1"} <= ids


def test_multiple_distinct_lineups():
    opt = LineupOptimizer(_pool(), _cfg())
    lus = opt.best(n=3, jitter=2.0)
    assert 1 <= len(lus) <= 3
    keys = {tuple(sorted(l.ids)) for l in lus}
    assert len(keys) == len(lus)  # distinct


def test_n_must_be_positive():
    opt = LineupOptimizer(_pool(), _cfg())
    with pytest.raises(ValueError):
        opt.best(n=0)


def test_flex_eligibility():
    """FLEX must hold RB/WR/TE only."""
    opt = LineupOptimizer(_pool(), _cfg())
    lu = opt.best(n=1)[0]
    # rebuild slot assignment
    assert opt._assignable(lu.players)


def test_seed_deterministic():
    a = LineupOptimizer(_pool(), _cfg(rng_seed=99)).best(n=1, jitter=1.5)
    b = LineupOptimizer(_pool(), _cfg(rng_seed=99)).best(n=1, jitter=1.5)
    assert [p.id for p in a[0].players] == [p.id for p in b[0].players]
