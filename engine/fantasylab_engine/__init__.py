"""fantasylab_engine — an ORIGINAL DFS projection toolkit.

Clean-room implementations of metric *definitions* that FantasyLabs publishes
openly in its support glossaries (research/SOURCES.md S11-S14). No FantasyLabs
code, no subscription data, no proprietary weights are included or derived.

Every public definition mirrored here is cited in the module docstrings.
"""

from .metrics import (
    plus_minus,
    implied_points_from_expectation,
    projected_plus_minus,
    points_per_salary,
    consistency_rate,
    upside_rate_half_sd,
    dud_rate_half_expectation,
    dud_rate_half_sd,
    bargain_rating,
    opponent_plus_minus,
    salary_change,
    percentile_rank,
)
from .expectation import ExpectationModel
from .model import WeightedPlayerModel, ModelFactor
from .trends import TrendQuery, TrendResult, run_trend
from .optimizer import (
    LineupOptimizer,
    PlayerRow,
    RosterSlot,
    OptimizerConfig,
)
from .simulation import SlateSimulator, SimConfig, SimResult
from .scoring import dk_nfl_points, fd_nfl_points, ScoringTable, DK_NFL, FD_NFL
from .data import load_players_csv

__version__ = "0.1.0"

__all__ = [
    "plus_minus",
    "implied_points_from_expectation",
    "projected_plus_minus",
    "points_per_salary",
    "consistency_rate",
    "upside_rate_half_sd",
    "dud_rate_half_expectation",
    "dud_rate_half_sd",
    "bargain_rating",
    "opponent_plus_minus",
    "salary_change",
    "percentile_rank",
    "ExpectationModel",
    "WeightedPlayerModel",
    "ModelFactor",
    "TrendQuery",
    "TrendResult",
    "run_trend",
    "LineupOptimizer",
    "PlayerRow",
    "RosterSlot",
    "OptimizerConfig",
    "SlateSimulator",
    "SimConfig",
    "SimResult",
    "dk_nfl_points",
    "fd_nfl_points",
    "ScoringTable",
    "DK_NFL",
    "FD_NFL",
    "load_players_csv",
]
