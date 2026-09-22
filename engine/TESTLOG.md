# Test Log

## Run — Pass 1→2 (2026-09-22)

```
python3 -m venv .venv
.venv/bin/pip install pytest numpy
cd engine && .venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

**Result after fixes: `79 passed in 20.86s`**

### Failures found in first run (Pass 1) and fixed (folded into Pass 2)

| Test | Root cause | Fix |
|------|-----------|-----|
| `test_stack_rule` (2 QBs in lineup) | `_default_flex` made QB/DST FLEX-eligible (flex_positions contained primary pos) | FLEX-eligibility now empty for non-RB/WR/TE in `data.py` + test helpers |
| `test_exclude_and_require` (`AttributeError: 'list' object has no attribute 'ids'`) | `require_ids` search branch returned raw `List[PlayerRow]` | Wrapped with `self._to_lineup(...)` |
| `test_bargain_rating_prefers_cheaper_site` | Test assumed max-percentile for a tie at top; implementation is tie-aware | Test corrected to 90 for tie, added strict-100 case |

## Coverage targets

| Test file | Verifies |
|-----------|----------|
| `test_metrics.py` | Every metric vs hand-computed glossary fixtures (S11–S14); I4/I5 variants both tested. |
| `test_expectation.py` | Monotone fit, mean fallback, non-positive salary guards (P2-3). |
| `test_model.py` | R² semantics per S17 (perfect alignment ⇒ 1.0; small n ⇒ NaN). |
| `test_trends.py` | S14 fields, zero-match behavior (P2-11), small-sample flags. |
| `test_optimizer.py` | Cap/min-spend/stacks/groups/bans/excludes/require/flex/duplicates/empty (P2-2). |
| `test_scoring.py` | Official DK/FD tables incl. FD yardage bonuses (I12 regression test). |
| `test_simulation.py` | Seed reproducibility (P2-12), param guards, rating bounds. |
| `test_data.py` | CSV schema, bad/zero salary, empty file (input guards). |
