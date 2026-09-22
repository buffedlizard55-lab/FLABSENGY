"""Scoring tests — official numbers only (S33/S34/S46). Guards I12."""

import pytest

from fantasylab_engine.scoring import (
    DK_NFL,
    FD_NFL,
    OffensiveLine,
    dk_nfl_points,
    dst_points,
    fd_nfl_points,
)


def test_dk_basic_passing():
    s = OffensiveLine(pass_yards=250, pass_tds=2, interceptions=1)
    # 250*0.04=10, TD=8, INT=-1 => 17
    assert dk_nfl_points(s) == pytest.approx(17.0)


def test_dk_pass_300_bonus():
    s = OffensiveLine(pass_yards=300, pass_tds=0)
    assert dk_nfl_points(s) == pytest.approx(300 * 0.04 + 3)


def test_dk_rec_100_bonus_full_ppr():
    s = OffensiveLine(receptions=8, rec_yards=100, rec_tds=1)
    # 8*1 + 100*0.1 + 6 + 3 = 8+10+6+3 = 27
    assert dk_nfl_points(s) == pytest.approx(27.0)


def test_dk_no_bonus_at_99_yards():
    s = OffensiveLine(receptions=8, rec_yards=99, rec_tds=0)
    assert dk_nfl_points(s) == pytest.approx(8 + 9.9)


def test_fd_half_ppr_differs_from_dk():
    s = OffensiveLine(receptions=10, rec_yards=50, rec_tds=0)
    assert fd_nfl_points(s) == pytest.approx(10 * 0.5 + 5.0)
    assert dk_nfl_points(s) == pytest.approx(10 * 1.0 + 5.0)


def test_fd_has_yardage_bonuses_official_I12():
    """Official FD page (S34) lists 100+ rush/rec and 300+ pass bonuses."""
    s = OffensiveLine(rush_yards=100)
    assert fd_nfl_points(s) == pytest.approx(10 + 3)
    s2 = OffensiveLine(pass_yards=300)
    assert fd_nfl_points(s2) == pytest.approx(12 + 3)


def test_fumble_difference_official():
    s = OffensiveLine(fumbles_lost=1)
    assert dk_nfl_points(s) == pytest.approx(-1.0)
    assert fd_nfl_points(s) == pytest.approx(-2.0)


def test_dst_points_allowed_bands_shared():
    # 0 allowed => +10 both
    assert dst_points(DK_NFL, points_allowed=0) == pytest.approx(10)
    assert dst_points(FD_NFL, points_allowed=0) == pytest.approx(10)
    assert dst_points(DK_NFL, points_allowed=35) == pytest.approx(-4)
    assert dst_points(DK_NFL, points_allowed=27, sacks=3) == pytest.approx(3)


def test_dst_mid_band():
    assert dst_points(DK_NFL, points_allowed=10) == pytest.approx(4)
    assert dst_points(DK_NFL, points_allowed=21) == pytest.approx(0)
