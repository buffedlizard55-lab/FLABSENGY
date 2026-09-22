# fantasylab-engine

**Original** Python DFS projection toolkit. Clean-room implementation of metric
*definitions* FantasyLabs publishes openly in its support glossaries — with
source IDs from [`research/SOURCES.md`](../research/SOURCES.md) cited in every
docstring.

> This package contains **no** FantasyLabs code, **no** subscription data, **no**
> proprietary weights. See [`research/PAYWALL_POLICY.md`](../research/PAYWALL_POLICY.md).

## Modules

| Module | Implements | Public source |
|--------|------------|---------------|
| `metrics` | Plus/Minus, Implied Points, Projected +/-, Pts/Sal, Consistency, Upside (½-SD + PM-rank variants), Duds (both official variants), Bargain Rating, Opponent +/-, Salary Change, percentile ranks | S11–S14, S18 |
| `expectation` | Salary → expected points model (monotone binned fit) powering every +/- metric | S11–S13 description |
| `model` | User-weighted factor model + R² backtest vs historical Plus/Minus; Vegas Score helper | S16, S17 |
| `trends` | Count / Avg Expected / Avg Actual / Points +/- / Consistency trend runner with small-sample flags | S14, S18 |
| `optimizer` | Constrained lineup optimizer (cap, min-spend, stacks, groups, exclusions, exposures) | input set from S16 |
| `simulation` | Seeded Monte-Carlo slate sim: player draws → lineup pool → field model → 0–99 rel ratings | steps from S19–S21 |
| `scoring` | Official DK/FD NFL scoring tables | S33, S34, S46 (official pages only; I12) |
| `data` | CSV pool loader with validation; data-source policy documented | repo policy |

## Quick start

```bash
cd engine
pip install -e ".[test]"
pytest -q
```

```python
from fantasylab_engine import ExpectationModel, plus_minus, consistency_rate
import numpy as np

sal = np.random.uniform(3000, 10000, 500)
pts = 5 + 0.002 * sal + np.random.normal(0, 3, 500)
model = ExpectationModel().fit(sal, np.clip(pts, 0, None))

exp = model.expected(7500)
print("Implied points at $7,500:", round(exp, 2))
print("Projected +/- if median 20:", round(20 - exp, 2))
```

Optimizer example:

```python
from fantasylab_engine import LineupOptimizer, OptimizerConfig
from fantasylab_engine.optimizer import PlayerRow, qb_stack_with_receiver_and_opponent

# Build PlayerRow objects (or load via fantasylab_engine.load_players_csv).
cfg = OptimizerConfig(
    slots=["QB","RB","RB","WR","WR","WR","TE","FLEX","DST"],
    salary_cap=50_000,
    min_spend_ratio=0.99,
    stack_rules=[qb_stack_with_receiver_and_opponent()],
    rng_seed=7,
)
# opt = LineupOptimizer(players, cfg)
# lineups = opt.best(n=20, jitter=150)
```

## What is NOT here (and why)

- FantasyLabs projection numbers / ownership / Pro Trend definitions — not public (I15).
- Scraped fantasylabs.com content — ToS prohibits it (I1–I3, S27).
- DraftKings/FanDuel undocumented API clients — ToS-risky (I16). Export your
  own contest CSVs instead.
