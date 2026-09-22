"""Metric implementations from FantasyLabs' *public* glossary definitions.

Source map (research/SOURCES.md):
  S11 = NFL Glossary  https://support.fantasylabs.com/hc/en-us/articles/214870428-Glossary-of-Terms-NFL
  S12 = NBA Glossary  https://support.fantasylabs.com/hc/en-us/articles/214870378-NBA-Glossary-of-Terms
  S13 = MLB Glossary  https://support.fantasylabs.com/hc/en-us/articles/214870358-MLB-Glossary-of-Terms
  S14 = Trends how-to  https://www.fantasylabs.com/articles/using-fantasylabs-free-dfs-trends-tool/

This module implements the *published definitions* only. It contains no
FantasyLabs source code, weights, or data.
"""

from __future__ import annotations

import math
from typing import Optional, Sequence

import numpy as np


# ---------------------------------------------------------------------------
# Plus/Minus family  [S11][S12][S13][S14]
# ---------------------------------------------------------------------------

def plus_minus(actual_points: Sequence[float],
               expected_points: Sequence[float],
               per_game: bool = True) -> float:
    """Plus/Minus = actual fantasy points - expected fantasy points (salary-based).

    Official: "a player's plus/minus is his actual points minus his expected
    points" [S11]. If `per_game`, returned per game (the glossary reports both
    total and per-game forms: "50 total points, or +5.0 points per game" [S11]).
    """
    actual = np.asarray(actual_points, dtype=float)
    expected = np.asarray(expected_points, dtype=float)
    if actual.shape != expected.shape:
        raise ValueError("actual_points and expected_points must align")
    if actual.size == 0:
        raise ValueError("empty input")
    diff = float(np.sum(actual - expected))
    return diff / actual.size if per_game else diff


def implied_points_from_expectation(expected_points: Sequence[float]) -> float:
    """Implied Points = expected fantasy points historically based on cost [S11].

    Here we simply surface the fitted expectation (mean over the window).
    """
    expected = np.asarray(expected_points, dtype=float)
    if expected.size == 0:
        raise ValueError("empty input")
    return float(np.mean(expected))


def projected_plus_minus(median_projection: float,
                         expected_points: float) -> float:
    """Projected Plus/Minus = median projection - salary-based expectation [S11]."""
    return float(median_projection - expected_points)


def points_per_salary(projected_points: float, salary: float,
                      unit: float = 1000.0) -> float:
    """Pts/Sal = projected points for every `unit` dollars of salary [S11].

    Glossary unit is $1,000 ("projected points for every $1000 of salary").
    """
    if salary <= 0:
        raise ValueError("salary must be positive")
    if unit <= 0:
        raise ValueError("unit must be positive")
    return float(projected_points * unit / salary)


# ---------------------------------------------------------------------------
# Consistency / Upside / Duds  [S11][S12]
# ---------------------------------------------------------------------------

def consistency_rate(actual_points: Sequence[float],
                     expected_points: Sequence[float],
                     stdev: Optional[float] = None) -> float:
    """Consistency = % of games produced WITHIN one SD of expected points [S11].

    "The percentage of games in which a player has produced within a standard
    deviation of his expected points based off of historical scoring and
    pricing." [S11]

    `stdev`: if None, uses the sample SD of (actual - expected) residuals —
    the spread of performance around salary-based expectation.
    """
    actual = np.asarray(actual_points, dtype=float)
    expected = np.asarray(expected_points, dtype=float)
    if actual.shape != expected.shape or actual.size == 0:
        raise ValueError("aligned non-empty inputs required")
    resid = actual - expected
    sd = float(np.std(resid, ddof=1)) if stdev is None and actual.size > 1 else \
        (float(stdev) if stdev is not None else 0.0)
    if stdev is not None:
        sd = float(stdev)
    if sd == 0.0:
        # Degenerate: every game exactly at expectation => 100% within 0 SD.
        return 1.0
    hits = np.abs(resid) <= sd
    return float(np.mean(hits))


def upside_rate_half_sd(actual_points: Sequence[float],
                        expected_points: Sequence[float],
                        stdev: Optional[float] = None) -> float:
    """Upside = % of games >= 0.5 SD ABOVE salary-based implied total [S12].

    NBA glossary: "Upside figures show the percentage of games in which a
    player has finished at least one-half standard deviation above his
    salary-based implied total." [S12]  (2016 glossary article agrees [S18].)
    NOTE: the NFL glossary words Upside/Breakout differently [S11] — see
    research/IRREGULARITIES.md I5; use `upside_rate_highest_pm` for a
    Plus/Minus-ranked alternative.
    """
    actual = np.asarray(actual_points, dtype=float)
    expected = np.asarray(expected_points, dtype=float)
    if actual.shape != expected.shape or actual.size == 0:
        raise ValueError("aligned non-empty inputs required")
    resid = actual - expected
    sd = _resid_sd(resid, stdev)
    if sd is None:
        return float("nan")  # insufficient sample — documented behavior
    return float(np.mean(resid >= 0.5 * sd))


def upside_rate_highest_pm(actual_points: Sequence[float],
                           expected_points: Sequence[float],
                           top_fraction: float = 0.5) -> float:
    """NFL-flavored Breakout proxy: share of games in the top `top_fraction`
    of this player's own Plus/Minus distribution.

    NFL glossary wording: "Matches players who have most frequently posted the
    highest Plus/Minus scores." [S11] — vague; we operationalize it as the
    share of appearances whose per-game PM >= (1 - top_fraction) quantile.
    """
    if not 0.0 < top_fraction < 1.0:
        raise ValueError("top_fraction must be in (0, 1)")
    actual = np.asarray(actual_points, dtype=float)
    expected = np.asarray(expected_points, dtype=float)
    if actual.shape != expected.shape or actual.size == 0:
        raise ValueError("aligned non-empty inputs required")
    resid = actual - expected
    cutoff = float(np.quantile(resid, 1.0 - top_fraction))
    return float(np.mean(resid >= cutoff))


def dud_rate_half_expectation(actual_points: Sequence[float],
                              expected_points: Sequence[float]) -> float:
    """Duds (NFL wording) = % of games scoring FEWER THAN HALF of expectation.

    NFL glossary: "the percentage of games in which a player has scored fewer
    than half his salary-based expectation." [S11]  See IRREGULARITIES I4 —
    this conflicts with the NBA wording; both variants are provided.
    """
    actual = np.asarray(actual_points, dtype=float)
    expected = np.asarray(expected_points, dtype=float)
    if actual.shape != expected.shape or actual.size == 0:
        raise ValueError("aligned non-empty inputs required")
    return float(np.mean(actual < 0.5 * expected))


def dud_rate_half_sd(actual_points: Sequence[float],
                     expected_points: Sequence[float],
                     stdev: Optional[float] = None) -> float:
    """Duds (NBA wording) = % of games >= 0.5 SD BELOW implied total.

    NBA glossary: "finishes at least one-half a standard deviation below his
    salary-based implied total." [S12]  See IRREGULARITIES I4.
    """
    actual = np.asarray(actual_points, dtype=float)
    expected = np.asarray(expected_points, dtype=float)
    if actual.shape != expected.shape or actual.size == 0:
        raise ValueError("aligned non-empty inputs required")
    resid = actual - expected
    sd = _resid_sd(resid, stdev)
    if sd is None:
        return float("nan")
    return float(np.mean(resid <= -0.5 * sd))


# ---------------------------------------------------------------------------
# Bargain Rating  [S11][S12]
# ---------------------------------------------------------------------------

def percentile_rank(value: float, reference: Sequence[float]) -> float:
    """Percentile of `value` within `reference` (0..100), tie-aware."""
    ref = np.asarray(reference, dtype=float)
    if ref.size == 0:
        raise ValueError("reference must be non-empty")
    if math.isnan(value):
        return float("nan")
    below = np.sum(ref < value)
    equal = np.sum(ref == value)
    return float(100.0 * (below + 0.5 * equal) / ref.size)


def bargain_rating(salary_site_a: float,
                   salary_site_b: float,
                   historical_position_deltas: Sequence[float],
                   site_a_is_cheaper_reference: bool = True) -> float:
    """Bargain Rating = historical percentile rank of a player's cross-site
    salary bargain at his position [S11][S12].

    Glossary: "We look at the typical difference in site salaries at a
    position and then rank a player based on how much of a bargain he is in a
    particular game relative to the historical data." [S11]

    We operationalize:
      raw_bargain(a vs b) = (salary_b - salary_a) / salary_b
        (positive => site A cheaper => better bargain for A)
      BR_A = percentile of raw_bargain among historical_position_deltas.

    `historical_position_deltas` must be the historical distribution of the
    SAME raw statistic for that position. Returns 0..100 for site A.
    """
    if salary_site_a <= 0 or salary_site_b <= 0:
        raise ValueError("salaries must be positive")
    deltas = np.asarray(historical_position_deltas, dtype=float)
    if deltas.size < 2:
        raise ValueError("need >=2 historical deltas for a percentile")
    raw = (salary_site_b - salary_site_a) / salary_site_b
    hist_raw = deltas  # caller supplies deltas already in same orientation
    return percentile_rank(float(raw), hist_raw)


# ---------------------------------------------------------------------------
# Opponent Plus/Minus, Salary Change  [S11][S12]
# ---------------------------------------------------------------------------

def opponent_plus_minus(actual_points_allowed: Sequence[float],
                        expected_points_allowed: Sequence[float]) -> float:
    """Opponent Plus/Minus Allowed = (actual fantasy pts allowed to a position)
    - (expected allowed, salary-adjusted) [S11][S12].

    The glossary's key property: expectation is salary-based, so facing
    expensive (good) opponents raises the expected bar automatically. The
    caller supplies salary-adjusted expectations from `ExpectationModel`.
    """
    return plus_minus(actual_points_allowed, expected_points_allowed,
                      per_game=True)


def salary_change(current_salary: float, previous_salary: float) -> float:
    """Salary Change = player's change in salary over a period [S11]."""
    return float(current_salary - previous_salary)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _resid_sd(resid: np.ndarray, stdev: Optional[float]) -> Optional[float]:
    if stdev is not None:
        sd = float(stdev)
        return sd if sd > 0 else None
    if resid.size < 2:
        return None
    sd = float(np.std(resid, ddof=1))
    return sd if sd > 0 else None
