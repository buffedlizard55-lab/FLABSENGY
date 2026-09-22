"""Salary-based expectation model.

FantasyLabs' core publicly described idea [S11][S12][S13]:

    "we use historic performance data to help calculate exactly what to
     expect out of a player based on his cost. So if Mahomes costs $10,000,
     we know he should produce X points, on average."

Their regression parameters are NOT public (F10.5). This is an original
implementation: fit E[points | salary] on historical (salary, fantasy points)
pairs with a monotone piecewise-linear / isotone-style approach, then use it
to drive Plus/Minus, Consistency, Upside, Duds, Implied Points, and Opponent
Plus/Minus.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np


@dataclass
class ExpectationModel:
    """Fit E[fantasy_points | salary] from historical rows.

    Strategy:
      1. Bin salaries into quantile buckets (default 20).
      2. Mean points per bucket.
      3. Pool-adjacent-violators style monotone cleanup (PAVA) so expectation
         never *decreases* as salary increases (economic prior).
      4. Linear interpolation for new salaries; clamp outside range.

    Parameters
    ----------
    n_bins : number of salary quantile buckets.
    min_rows : minimum rows required to fit; below this the model stays
        unfitted and `expected()` falls back to the global mean (documented
        fallback, keeps callers divide-by-zero safe).
    """

    n_bins: int = 20
    min_rows: int = 30
    _bin_edges: Optional[np.ndarray] = field(default=None, repr=False)
    _bin_values: Optional[np.ndarray] = field(default=None, repr=False)
    _global_mean: float = field(default=0.0, repr=False)
    _fitted: bool = field(default=False, repr=False)

    # -- fit ---------------------------------------------------------------
    def fit(self, salaries: np.ndarray, points: np.ndarray) -> "ExpectationModel":
        salaries = np.asarray(salaries, dtype=float)
        points = np.asarray(points, dtype=float)
        if salaries.shape != points.shape or salaries.ndim != 1:
            raise ValueError("salaries and points must be 1-D and aligned")
        if np.any(salaries <= 0):
            raise ValueError("salaries must be positive")
        if salaries.size == 0:
            raise ValueError("empty training set")

        self._global_mean = float(np.mean(points))
        if salaries.size < self.min_rows:
            self._fitted = False
            return self

        n_bins = max(2, min(self.n_bins, salaries.size // 5))
        quantiles = np.linspace(0.0, 1.0, n_bins + 1)
        edges = np.unique(np.quantile(salaries, quantiles))
        if edges.size < 3:  # all salaries nearly identical
            self._fitted = False
            return self

        idx = np.digitize(salaries, edges[1:-1], right=False)
        means = np.array([points[idx == b].mean() if np.any(idx == b) else np.nan
                          for b in range(edges.size - 1)])
        centers = np.array([
            salaries[idx == b].mean() if np.any(idx == b)
            else 0.5 * (edges[b] + edges[b + 1])
            for b in range(edges.size - 1)
        ])
        # drop empty bins
        mask = ~np.isnan(means)
        centers, means = centers[mask], means[mask]
        if centers.size < 2:
            self._fitted = False
            return self

        means = _pava(means)
        self._bin_edges = centers
        self._bin_values = means
        self._fitted = True
        return self

    # -- use ---------------------------------------------------------------
    @property
    def fitted(self) -> bool:
        return self._fitted

    def expected(self, salary: float) -> float:
        if salary <= 0:
            raise ValueError("salary must be positive")
        if not self._fitted:
            return self._global_mean
        return float(np.interp(salary, self._bin_edges, self._bin_values))

    def expected_many(self, salaries: np.ndarray) -> np.ndarray:
        return np.array([self.expected(float(s))
                         for s in np.asarray(salaries, dtype=float)])

    def plus_minus(self, salary: float, actual_points: float,
                   per_game: bool = True, games: int = 1) -> float:
        """Convenience: Plus/Minus of one span against this expectation."""
        if games < 1:
            raise ValueError("games must be >= 1")
        exp_total = self.expected(salary) * games
        if per_game:
            return float((actual_points - exp_total) / games)
        return float(actual_points - exp_total)


def _pava(y: np.ndarray) -> np.ndarray:
    """Pool-adjacent-violators: isotone (non-decreasing) regression of y."""
    y = y.astype(float).copy()
    n = y.size
    weights = np.ones(n)
    i = 0
    levels: list[float] = []
    weights_l: list[float] = []
    while i < n:
        cur, w = y[i], weights[i]
        while levels and cur < levels[-1]:
            cur = (cur * w + levels[-1] * weights_l[-1]) / (w + weights_l[-1])
            w = w + weights_l[-1]
            levels.pop()
            weights_l.pop()
        levels.append(cur)
        weights_l.append(w)
        i += 1
    out = np.empty(n)
    k = 0
    for lev, w in zip(levels, weights_l):
        out[k:k + int(w)] = lev
        k += int(w)
    return out
