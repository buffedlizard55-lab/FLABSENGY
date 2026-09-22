"""Player model + R2 backtest tests (S17 semantics)."""

import numpy as np
import pytest

from fantasylab_engine.model import ModelFactor, WeightedPlayerModel, vegas_score_percentile


def test_ratings_weighted_zscores():
    factors = [
        ModelFactor("median", 10.0),
        ModelFactor("bargain", 5.0, higher_is_better=True),
    ]
    mat = {
        "median": np.array([10.0, 20.0, 30.0]),
        "bargain": np.array([0.0, 50.0, 100.0]),
    }
    model = WeightedPlayerModel(factors).fit(mat)
    r = model.ratings(mat)
    assert r.shape == (3,)
    # highest median + highest bargain => highest rating
    assert r[2] > r[1] > r[0]


def test_higher_is_better_false_inverts():
    factors = [ModelFactor("salary", 1.0, higher_is_better=False)]
    mat = {"salary": np.array([4000.0, 8000.0])}
    model = WeightedPlayerModel(factors).fit(mat)
    r = model.ratings(mat)
    # cheaper player gets higher rating
    assert r[0] > r[1]


def test_backtest_r2_perfect_alignment():
    """Ratings == historical PM => r2 == 1.0 (S17: 1 = perfect)."""
    col = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    mat = {"f": col.copy()}
    model = WeightedPlayerModel([ModelFactor("f", 1.0)]).fit(mat)
    out = model.backtest(mat, historical_plus_minus=col)
    assert out["r2"] == pytest.approx(1.0, abs=1e-9)
    assert out["n"] == 5


def test_backtest_small_sample_nan():
    col = np.array([1.0, 2.0])
    mat = {"f": col}
    model = WeightedPlayerModel([ModelFactor("f", 1.0)], min_history=5).fit(mat)
    out = model.backtest(mat, np.array([1.0, 2.0]))
    assert np.isnan(out["r2"])


def test_backtest_missing_factor_raises():
    model = WeightedPlayerModel([ModelFactor("nope", 1.0)])
    with pytest.raises(KeyError):
        model.fit({"other": np.array([1.0])})


def test_ragged_columns_raise():
    model = WeightedPlayerModel([
        ModelFactor("a", 1.0),
        ModelFactor("b", 1.0),
    ])
    model.fit({"a": np.array([1.0, 2.0]), "b": np.array([1.0])})
    with pytest.raises(ValueError):
        model.ratings({"a": np.array([1.0, 2.0]), "b": np.array([1.0])})


def test_unfitted_ratings_raise():
    model = WeightedPlayerModel([ModelFactor("a", 1.0)])
    with pytest.raises(RuntimeError):
        model.ratings({"a": np.array([1.0])})


def test_vegas_score_opponent_orientation():
    """S17: low opponent implied => high Vegas Score (93 ~ bottom 7%)."""
    hist = list(range(3, 10))  # 3..9
    # opponent implied at bottom of history => high score
    vs_low = vegas_score_percentile(3.0, hist, opponent=True)
    vs_high = vegas_score_percentile(9.0, hist, opponent=True)
    assert vs_low < vs_high
