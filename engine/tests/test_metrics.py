"""Metric tests — hand-computed fixtures verify each public definition."""

import math

import numpy as np
import pytest

from fantasylab_engine.metrics import (
    bargain_rating,
    consistency_rate,
    dud_rate_half_expectation,
    dud_rate_half_sd,
    implied_points_from_expectation,
    opponent_plus_minus,
    percentile_rank,
    plus_minus,
    points_per_salary,
    projected_plus_minus,
    salary_change,
    upside_rate_half_sd,
    upside_rate_highest_pm,
)


# ---------------------------------------------------------------------------
# Plus/Minus family
# ---------------------------------------------------------------------------

def test_plus_minus_glossary_example():
    """S11 example: 300 actual vs 250 expected over 10 games => +5.0/game."""
    actual = [30.0] * 10
    expected = [25.0] * 10
    assert plus_minus(actual, expected, per_game=True) == pytest.approx(5.0)
    assert plus_minus(actual, expected, per_game=False) == pytest.approx(50.0)


def test_plus_minus_length_mismatch():
    with pytest.raises(ValueError):
        plus_minus([1.0], [1.0, 2.0])


def test_plus_minus_empty():
    with pytest.raises(ValueError):
        plus_minus([], [])


def test_implied_points_is_mean_expectation():
    assert implied_points_from_expectation([10.0, 20.0, 30.0]) == pytest.approx(20.0)


def test_projected_plus_minus():
    # S11: "median projection minus salary-based expectation"
    assert projected_plus_minus(22.5, 18.0) == pytest.approx(4.5)


def test_points_per_salary_unit_1000():
    # S11: projected points per $1000 of salary
    assert points_per_salary(20.0, 8000.0) == pytest.approx(2.5)
    with pytest.raises(ValueError):
        points_per_salary(20.0, 0.0)


# ---------------------------------------------------------------------------
# Consistency / Upside / Duds
# ---------------------------------------------------------------------------

def test_consistency_within_one_sd():
    # residuals: [-2, -1, 0, 1, 2]; sample sd = sqrt(2.5) ~= 1.581
    actual = np.array([8.0, 9.0, 10.0, 11.0, 12.0])
    expected = np.array([10.0] * 5)
    rate = consistency_rate(actual, expected)
    # |resid| <= 1.581 => residuals -1,0,1 (and -2,2 excluded): 3/5
    assert rate == pytest.approx(0.6)


def test_consistency_zero_sd_all_hits():
    actual = [10.0, 10.0]
    expected = [10.0, 10.0]
    assert consistency_rate(actual, expected) == 1.0


def test_upside_half_sd_definition_nba():
    """S12: >= 0.5 SD above implied total."""
    resid = np.array([-2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, -3.0, 5.0, -4.0])
    expected = np.full(10, 10.0)
    actual = expected + resid
    sd = float(np.std(resid, ddof=1))
    want = float(np.mean(resid >= 0.5 * sd))
    assert upside_rate_half_sd(actual, expected) == pytest.approx(want)


def test_upside_insufficient_sample_is_nan_not_crash():
    # single game: sd undefined -> NaN (documented)
    val = upside_rate_half_sd([20.0], [10.0])
    assert math.isnan(val)


def test_dud_half_expectation_nfl_wording():
    """S11: fewer than half of salary-based expectation."""
    actual = [4.0, 9.0, 10.0, 11.0]
    expected = [10.0, 10.0, 10.0, 10.0]
    # only 4.0 < 5.0 => 1/4
    assert dud_rate_half_expectation(actual, expected) == pytest.approx(0.25)


def test_dud_half_sd_nba_wording():
    """S12: >= 0.5 SD below implied."""
    resid = np.array([-3.0, -1.0, 0.0, 1.0, 3.0])
    expected = np.full(5, 8.0)
    actual = expected + resid
    sd = float(np.std(resid, ddof=1))
    want = float(np.mean(resid <= -0.5 * sd))
    assert dud_rate_half_sd(actual, expected) == pytest.approx(want)


def test_upside_pm_variant_runs():
    resid = [0.0, 1.0, 2.0, 3.0, 4.0]
    actual = [10 + r for r in resid]
    expected = [10.0] * 5
    v = upside_rate_highest_pm(actual, expected, top_fraction=0.5)
    assert 0.0 <= v <= 1.0


def test_upside_pm_bad_fraction():
    with pytest.raises(ValueError):
        upside_rate_highest_pm([1.0], [1.0], top_fraction=1.5)


# ---------------------------------------------------------------------------
# Bargain Rating / percentile
# ---------------------------------------------------------------------------

def test_percentile_rank_basic():
    ref = [10.0, 20.0, 30.0, 40.0]
    assert percentile_rank(25.0, ref) == pytest.approx(50.0)  # 2 below + 0 equal => 2.5/4... wait
    # below=2 (10,20), equal=0 => (2+0)/4*100 = 50 ✓
    assert percentile_rank(10.0, ref) == pytest.approx(12.5)  # 0 below + 0.5*1 => 0.5/4*100
    assert percentile_rank(50.0, ref) == pytest.approx(100.0)


def test_bargain_rating_requires_history():
    with pytest.raises(ValueError):
        bargain_rating(5000.0, 6000.0, [0.1])


def test_bargain_rating_prefers_cheaper_site():
    # historical raw deltas in orientation (b-a)/b
    hist = [0.0, 0.05, 0.10, 0.15, 0.20]
    # site A = 8000, site B = 10000 => raw = 0.2 => ties top of history
    # tie-aware percentile: (4 below + 0.5 * 1 equal) / 5 = 90
    br_a = bargain_rating(8000.0, 10000.0, hist)
    assert br_a == pytest.approx(90.0)
    # strictly better than all history => 100
    br_above = bargain_rating(7500.0, 10000.0, hist)  # raw = 0.25
    assert br_above == pytest.approx(100.0)
    # site A more expensive: raw negative => bottom
    br_a2 = bargain_rating(10000.0, 8000.0, hist)
    assert br_a2 == pytest.approx(0.0)


def test_bargain_rating_invalid_salaries():
    with pytest.raises(ValueError):
        bargain_rating(0.0, 5000.0, [0.1, 0.2])


# ---------------------------------------------------------------------------
# misc
# ---------------------------------------------------------------------------

def test_salary_change():
    assert salary_change(5500.0, 5000.0) == pytest.approx(500.0)


def test_opponent_pm_delegates():
    v = opponent_plus_minus([20.0, 22.0], [18.0, 18.0])
    assert v == pytest.approx(3.0)
