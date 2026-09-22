"""Official DFS scoring tables — transcribed from OFFICIAL rules pages only.

Sources (Class A, research/SOURCES.md):
  DK_NFL  <- DraftKings official rules + DK Network scoring chart
            S33 https://www.draftkings.com/help/rules/nfl
            S46 https://dknetwork.draftkings.com/2026/05/19/draftkings-best-ball-fantasy-football-guide/
            (classic DK chart: 1 pt / 25 pass yds == 0.04; INT -1; fumble lost -1;
             bonuses 300+ pass +3, 100+ rush +3, 100+ rec +3)
  FD_NFL  <- FanDuel official rules page (fetched 2026-09-22)
            S34 https://www.fanduel.com/rules
            NOTE: official FD page NOW lists the three yardage bonuses (+3 each).
            Secondary guides claiming "no FD bonuses" are wrong/outdated — I12.

Secondary blogs are deliberately NOT used (I12).
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Dict


@dataclass(frozen=True)
class ScoringTable:
    name: str
    # offense
    pass_yd: float = 0.0
    pass_td: float = 0.0
    pass_int: float = 0.0
    rush_yd: float = 0.0
    rush_td: float = 0.0
    rec: float = 0.0
    rec_yd: float = 0.0
    rec_td: float = 0.0
    fumble_lost: float = 0.0
    two_pt: float = 0.0
    # bonuses
    bonus_pass_300: float = 0.0
    bonus_rush_100: float = 0.0
    bonus_rec_100: float = 0.0
    # dst (subset commonly shared)
    sack: float = 1.0
    int_dst: float = 2.0
    fum_rec: float = 2.0
    safety: float = 2.0
    blocked_kick: float = 2.0
    dst_td: float = 6.0
    pa_0: float = 10.0
    pa_1_6: float = 7.0
    pa_7_13: float = 4.0
    pa_14_20: float = 1.0
    pa_21_27: float = 0.0
    pa_28_34: float = -1.0
    pa_35: float = -4.0
    # kicking (FanDuel official; DK classic classic slate has no K in current
    # classic NFL — kept 0 for DK)
    fg_0_39: float = 0.0
    fg_40_49: float = 0.0
    fg_50: float = 0.0
    xp: float = 0.0


DK_NFL = ScoringTable(
    name="DraftKings NFL (official chart)",
    pass_yd=0.04,        # 1 pt / 25 yds
    pass_td=4.0,
    pass_int=-1.0,
    rush_yd=0.1,
    rush_td=6.0,
    rec=1.0,             # full PPR
    rec_yd=0.1,
    rec_td=6.0,
    fumble_lost=-1.0,
    two_pt=2.0,
    bonus_pass_300=3.0,
    bonus_rush_100=3.0,
    bonus_rec_100=3.0,
)

FD_NFL = ScoringTable(
    name="FanDuel NFL (official rules page, 2026-09-22)",
    pass_yd=0.04,
    pass_td=4.0,
    pass_int=-1.0,
    rush_yd=0.1,
    rush_td=6.0,
    rec=0.5,             # half PPR (official)
    rec_yd=0.1,
    rec_td=6.0,
    fumble_lost=-2.0,    # official: "Fumble = -2 Points"
    two_pt=2.0,
    bonus_pass_300=3.0,  # official lists these — I12
    bonus_rush_100=3.0,
    bonus_rec_100=3.0,
    # kickers per official page
    fg_0_39=3.0,
    fg_40_49=4.0,
    fg_50=5.0,
    xp=1.0,
)


@dataclass
class OffensiveLine:
    pass_yards: float = 0.0
    pass_tds: int = 0
    interceptions: int = 0
    rush_yards: float = 0.0
    rush_tds: int = 0
    receptions: int = 0
    rec_yards: float = 0.0
    rec_tds: int = 0
    fumbles_lost: int = 0
    two_pt: int = 0


def _points(stats: OffensiveLine, table: ScoringTable) -> float:
    pts = 0.0
    pts += stats.pass_yards * table.pass_yd
    pts += stats.pass_tds * table.pass_td
    pts += stats.interceptions * table.pass_int
    pts += stats.rush_yards * table.rush_yd
    pts += stats.rush_tds * table.rush_td
    pts += stats.receptions * table.rec
    pts += stats.rec_yards * table.rec_yd
    pts += stats.rec_tds * table.rec_td
    pts += stats.fumbles_lost * table.fumble_lost
    pts += stats.two_pt * table.two_pt
    if table.bonus_pass_300 and stats.pass_yards >= 300:
        pts += table.bonus_pass_300
    if table.bonus_rush_100 and stats.rush_yards >= 100:
        pts += table.bonus_rush_100
    if table.bonus_rec_100 and stats.rec_yards >= 100:
        pts += table.bonus_rec_100
    return float(pts)


def dk_nfl_points(stats: OffensiveLine) -> float:
    """DraftKings offense score (official chart S33/S46)."""
    return _points(stats, DK_NFL)


def fd_nfl_points(stats: OffensiveLine) -> float:
    """FanDuel offense score (official rules S34, incl. yardage bonuses I12)."""
    return _points(stats, FD_NFL)


def dst_points(table: ScoringTable, *, sacks: int = 0, ints: int = 0,
               fum_recoveries: int = 0, safeties: int = 0,
               blocked_kicks: int = 0, dst_tds: int = 0,
               points_allowed: int) -> float:
    pts = (sacks * table.sack + ints * table.int_dst
           + fum_recoveries * table.fum_rec + safeties * table.safety
           + blocked_kicks * table.blocked_kick + dst_tds * table.dst_td)
    if points_allowed == 0:
        pts += table.pa_0
    elif points_allowed <= 6:
        pts += table.pa_1_6
    elif points_allowed <= 13:
        pts += table.pa_7_13
    elif points_allowed <= 20:
        pts += table.pa_14_20
    elif points_allowed <= 27:
        pts += table.pa_21_27
    elif points_allowed <= 34:
        pts += table.pa_28_34
    else:
        pts += table.pa_35
    return float(pts)
