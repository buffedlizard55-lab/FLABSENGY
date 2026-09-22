"""Expectation model tests — monotonicity, guards, edge cases (P2-3)."""

import numpy as np
import pytest

from fantasylab_engine.expectation import ExpectationModel, _pava


def _synthetic(n=500, seed=0):
    rng = np.random.default_rng(seed)
    salaries = rng.uniform(3000, 10000, n)
    # points grow sublinearly with salary + noise
    points = 5 + 0.002 * salaries + rng.normal(0, 3, n)
    points = np.clip(points, 0, None)
    return salaries, points


def test_fit_and_interpolate():
    s, p = _synthetic()
    m = ExpectationModel().fit(s, p)
    assert m.fitted
    e_low = m.expected(3500)
    e_high = m.expected(9500)
    assert e_high > e_low  # monotone expectation


def test_monotone_across_grid():
    s, p = _synthetic()
    m = ExpectationModel().fit(s, p)
    grid = np.linspace(3000, 10000, 50)
    vals = m.expected_many(grid)
    assert np.all(np.diff(vals) >= -1e-9)


def test_small_sample_falls_back_to_mean():
    s = np.array([4000.0, 5000.0])
    p = np.array([10.0, 20.0])
    m = ExpectationModel(min_rows=30).fit(s, p)
    assert not m.fitted
    assert m.expected(7000.0) == pytest.approx(15.0)


def test_all_identical_salaries_fallback():
    s = np.full(100, 5000.0)
    p = np.linspace(0, 20, 100)
    m = ExpectationModel().fit(s, p)
    assert not m.fitted


def test_rejects_nonpositive_salary_on_fit():
    m = ExpectationModel()
    with pytest.raises(ValueError):
        m.fit(np.array([0.0, 1.0]), np.array([1.0, 2.0]))


def test_rejects_nonpositive_salary_on_predict():
    m = ExpectationModel().fit(*_synthetic())
    with pytest.raises(ValueError):
        m.expected(-100.0)


def test_pava_non_decreasing():
    y = np.array([3.0, 1.0, 2.0, 5.0, 4.0])
    out = _pava(y)
    assert np.all(np.diff(out) >= -1e-12)


def test_plus_minus_helper():
    s, p = _synthetic()
    m = ExpectationModel().fit(s, p)
    # single game: actual 30 at salary 5000
    pm = m.plus_minus(5000.0, actual_points=30.0, per_game=True, games=1)
    assert pm == pytest.approx(30.0 - m.expected(5000.0))
