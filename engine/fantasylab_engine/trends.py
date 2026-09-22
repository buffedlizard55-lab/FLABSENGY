"""Trends engine.

Public behavior mirrored from FantasyLabs' free-Trends documentation [S14][S18]:

    Count, Avg Expected Pts, Avg Actual Pts, Points +/-, Consistency
    - Points +/- = actual - expected
    - Consistency = share of matches meeting/exceeding expectations
    - larger Count => more confidence; warn below a small-sample threshold

Filters are simple equality/membership/range predicates supplied by the
caller — the "essentially unlimited" filter space [S14] is modeled as a
predicate list, not cloned filter catalogs (I15: their UI filter list is
proprietary surface we do not enumerate).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence

import numpy as np

from .metrics import consistency_rate, plus_minus

Predicate = Callable[[Dict[str, Any]], bool]


@dataclass
class TrendQuery:
    name: str = "trend"
    predicates: List[Predicate] = field(default_factory=list)
    min_count_confidence: int = 30  # guidance from [S14]: small samples unreliable

    def matches(self, row: Dict[str, Any]) -> bool:
        return all(p(row) for p in self.predicates)


@dataclass
class TrendResult:
    name: str
    count: int
    avg_expected: float
    avg_actual: float
    points_plus_minus: float  # per-game [S14]
    consistency: float
    confident: bool  # count >= min_count_confidence
    notes: List[str]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "count": self.count,
            "avg_expected": self.avg_expected,
            "avg_actual": self.avg_actual,
            "points_plus_minus": self.points_plus_minus,
            "consistency": self.consistency,
            "confident": self.confident,
            "notes": list(self.notes),
        }


def run_trend(rows: Sequence[Dict[str, Any]],
              query: TrendQuery,
              expected_key: str = "expected_pts",
              actual_key: str = "actual_pts") -> TrendResult:
    """Evaluate a trend over historical rows.

    Each row must carry `expected_key` and `actual_key`. Zero matches returns
    a structured empty result (never raises on count=0; see VERIFICATION P2-11).
    """
    hits = [r for r in rows if query.matches(r)]
    notes: List[str] = []
    if not hits:
        return TrendResult(
            name=query.name, count=0,
            avg_expected=float("nan"), avg_actual=float("nan"),
            points_plus_minus=float("nan"), consistency=float("nan"),
            confident=False,
            notes=["no historical matches — no inference possible [S14]"],
        )
    exp = np.array([float(h[expected_key]) for h in hits])
    act = np.array([float(h[actual_key]) for h in hits])
    pm = plus_minus(act, exp, per_game=True)
    cons = consistency_rate(act, exp)
    confident = len(hits) >= query.min_count_confidence
    if not confident:
        notes.append(
            f"count={len(hits)} < {query.min_count_confidence}: sample too "
            "small for confident inference [S14]"
        )
    if pm > 0 and confident:
        notes.append("positive Plus/Minus with adequate sample — candidate edge")
    elif pm <= 0:
        notes.append("non-positive Plus/Minus — historically no value")
    return TrendResult(
        name=query.name,
        count=len(hits),
        avg_expected=float(np.mean(exp)),
        avg_actual=float(np.mean(act)),
        points_plus_minus=float(pm),
        consistency=float(cons),
        confident=confident,
        notes=notes,
    )


# -- common predicate helpers ------------------------------------------------

def eq(key: str, value: Any) -> Predicate:
    return lambda row: row.get(key) == value


def one_of(key: str, values: Sequence[Any]) -> Predicate:
    vals = set(values)
    return lambda row: row.get(key) in vals


def gte(key: str, value: float) -> Predicate:
    return lambda row: float(row.get(key, float("-inf"))) >= value


def lte(key: str, value: float) -> Predicate:
    return lambda row: float(row.get(key, float("inf"))) <= value
