"""Trends engine tests (S14 semantics: count/avg/PM/consistency, small-sample)."""

import pytest

from fantasylab_engine.trends import (
    TrendQuery,
    eq,
    gte,
    lte,
    one_of,
    run_trend,
)


def _rows():
    return [
        {"pos": "QB", "site": "DK", "home": True, "salary": 7000,
         "expected_pts": 20.0, "actual_pts": 24.0},
        {"pos": "QB", "site": "DK", "home": True, "salary": 7200,
         "expected_pts": 20.0, "actual_pts": 18.0},
        {"pos": "QB", "site": "FD", "home": False, "salary": 6800,
         "expected_pts": 18.0, "actual_pts": 25.0},
        {"pos": "RB", "site": "DK", "home": True, "salary": 6000,
         "expected_pts": 15.0, "actual_pts": 15.0},
    ]


def test_trend_basic_fields():
    q = TrendQuery(name="DK home QBs", predicates=[eq("pos", "QB"), eq("site", "DK")])
    res = run_trend(_rows(), q)
    assert res.count == 2
    assert res.avg_expected == pytest.approx(20.0)
    assert res.avg_actual == pytest.approx(21.0)
    # PM = mean(actual - expected) = mean(4, -2) = +1.0
    assert res.points_plus_minus == pytest.approx(1.0)
    assert res.as_dict()["name"] == "DK home QBs"


def test_small_count_not_confident():
    q = TrendQuery(name="FD QBs", predicates=[eq("site", "FD")],
                   min_count_confidence=30)
    res = run_trend(_rows(), q)
    assert res.count == 1
    assert not res.confident
    assert any("sample too small" in n for n in res.notes)


def test_zero_matches_structured_empty():
    q = TrendQuery(name="none", predicates=[eq("pos", "K")])
    res = run_trend(_rows(), q)
    assert res.count == 0
    assert not res.confident
    assert res.notes
    assert res.points_plus_minus != res.points_plus_minus  # NaN


def test_predicate_range_and_membership():
    q = TrendQuery(name="expensive", predicates=[gte("salary", 6800),
                                                  one_of("site", ["DK", "FD"])])
    res = run_trend(_rows(), q)
    assert res.count == 3


def test_lte_predicate():
    q = TrendQuery(name="cheap", predicates=[lte("salary", 6000)])
    assert run_trend(_rows(), q).count == 1


def test_all_rows_pass_when_no_predicates():
    q = TrendQuery(name="all")
    assert run_trend(_rows(), q).count == 4
