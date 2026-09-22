"""Simulation tests — reproducibility (P2-12), guards, structure."""

import numpy as np
import pytest

from fantasylab_engine.optimizer import OptimizerConfig, PlayerRow
from fantasylab_engine.simulation import SimConfig, SlateSimulator


def P(pid, team, opp, pos, salary, proj, own=None):
    # flex_positions = FLEX-only eligibility (empty for QB/DST).
    flex = frozenset({"RB", "WR", "TE"}) if pos in {"RB", "WR", "TE"} else frozenset()
    return PlayerRow(id=pid, name=pid, team=team, opp=opp, position=pos,
                     flex_positions=flex, salary=salary, projection=proj,
                     ownership=own, game=f"{team}x{opp}")


def _pool():
    ps = [
        P("qb1", "A", "B", "QB", 7000, 22, 18),
        P("qb2", "C", "D", "QB", 6200, 17, 9),
        P("rb1", "C", "D", "RB", 8000, 19, 22),
        P("rb2", "A", "B", "RB", 6500, 14, 12),
        P("rb3", "E", "F", "RB", 5000, 11, 8),
        P("rb4", "G", "H", "RB", 4000, 9, 5),
        P("rb5", "I", "J", "RB", 3000, 7, 3),
        P("wr1", "A", "B", "WR", 7500, 17, 20),
        P("wr2", "C", "D", "WR", 6000, 14, 11),
        P("wr3", "E", "F", "WR", 5000, 12, 7),
        P("wr4", "G", "H", "WR", 4000, 10, 6),
        P("wr5", "I", "J", "WR", 3000, 8, 4),
        P("te1", "A", "B", "TE", 5500, 11, 9),
        P("te2", "C", "D", "TE", 3500, 8, 5),
        P("dst1", "A", "B", "DST", 3000, 8, 10),
        P("dst2", "E", "F", "DST", 2400, 6, 6),
        P("dst3", "G", "H", "DST", 2000, 5, 4),
    ]
    return ps


def _cfg_slots():
    return OptimizerConfig(
        slots=["QB", "RB", "RB", "WR", "WR", "WR", "TE", "FLEX", "DST"],
        salary_cap=50000,
        rng_seed=7,
    )


def test_sim_runs_and_rates():
    sim = SlateSimulator(_pool(), SimConfig(n_sims=500, n_lineups=5,
                                            field_size=200, seed=1))
    result = sim.run(_cfg_slots())
    assert result.lineups
    top = result.lineups[0]
    assert top.sim_totals.shape == (500,)
    assert top.p95_total >= top.p05_total
    assert 0.0 <= top.opt_rate <= 1.0
    assert 0 <= top.project_rel <= 99


def test_reproducible_with_seed():
    r1 = SlateSimulator(_pool(), SimConfig(n_sims=300, n_lineups=3,
                                           field_size=100, seed=42)).run(_cfg_slots())
    r2 = SlateSimulator(_pool(), SimConfig(n_sims=300, n_lineups=3,
                                           field_size=100, seed=42)).run(_cfg_slots())
    assert r1.summary() == r2.summary()
    assert np.allclose(r1.lineups[0].sim_totals, r2.lineups[0].sim_totals)


def test_different_seed_differs():
    r1 = SlateSimulator(_pool(), SimConfig(n_sims=300, n_lineups=3,
                                           field_size=100, seed=1)).run(_cfg_slots())
    r2 = SlateSimulator(_pool(), SimConfig(n_sims=300, n_lineups=3,
                                           field_size=100, seed=2)).run(_cfg_slots())
    assert not np.allclose(r1.lineups[0].sim_totals, r2.lineups[0].sim_totals)


def test_low_sims_rejected():
    with pytest.raises(ValueError):
        SlateSimulator(_pool(), SimConfig(n_sims=10))


def test_bad_vol_rejected():
    with pytest.raises(ValueError):
        SlateSimulator(_pool(), SimConfig(vol=0.0))


def test_empty_pool_rejected():
    with pytest.raises(ValueError):
        SlateSimulator([])


def test_summary_keys():
    res = SlateSimulator(_pool(), SimConfig(n_sims=300, n_lineups=3,
                                            field_size=100, seed=5)).run(_cfg_slots())
    s = res.summary()
    assert {"n_sims", "candidate_lineups", "field_p90", "best_mean"} <= set(s)
