# FLABSENGY

**Verified reverse-engineering notes + an original projection engine for FantasyLabs-style DFS analytics.**

🎯 **Live site (GitHub Pages):** https://buffedlizard55-lab.github.io/FLABSENGY/

---

## What this is

A line-by-line, source-verified study of
[`fantasylabs.com/articles/`](https://www.fantasylabs.com/articles/) and the
data-quality system behind its projections — plus `engine/`, an **original**
Python toolkit that rebuilds every metric definition FantasyLabs publishes
openly (clean-room: no their-code, no subscription data, no proprietary weights).

| | |
|---|---|
| 📄 **[Source ledger](docs/ledger.html)** | 50 sources, Class A = official/primary, every claim ID'd |
| 📐 **[Metric library](docs/metrics.html)** | All 19 publicly documented metrics with formulas + engine function |
| ⚖️ **[Paywall & legal](docs/paywall.html)** | What was rebuilt, what was refused, and the ToS clauses that decided it |
| 🚩 **[16 irregularities](docs/limitations.html)** | Official-doc contradictions, pricing opacity, exposed endpoints, ToS conflicts |
| 🧭 **[Roadmap](docs/roadmap.html)** | 8 prioritized tasks for the next session |
| 🧰 **`engine/`** | Expectation model · 14 metrics · weighted model + R² · trends · optimizer · Monte-Carlo simulator · official DK/FD scoring — **79 tests passing** |

## Quick start

```bash
# engine
cd engine
python -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"
pytest -q          # 79 passed
```

```python
from fantasylab_engine import ExpectationModel, projected_plus_minus
import numpy as np

# Fit salary → expected fantasy points (the core of the metric family)
sal = np.random.uniform(3000, 10000, 500)
pts = np.clip(5 + 0.002 * sal + np.random.normal(0, 3, 500), 0, None)
model = ExpectationModel().fit(sal, pts)

exp = model.expected(7500)                       # implied points at $7,500
print(projected_plus_minus(20.0, exp))           # projected Plus/Minus
```

View the docs site locally:

```bash
python -m http.server 8080 --directory docs
# open http://localhost:8080
```

## Repository layout

```
FLABSENGY/
├── docs/                  # GitHub Pages site (clean static UI, no build step)
│   ├── index.html         # Overview
│   ├── features.html      # Site & feature map
│   ├── metrics.html       # Metric library (official definitions ↔ engine)
│   ├── methodology.html   # End-to-end projection pipeline
│   ├── data-sources.html  # Green/Yellow/Red lawful data sources
│   ├── ledger.html        # Searchable source ledger (S1–S50)
│   ├── paywall.html       # Paywall policy & ToS analysis
│   ├── limitations.html   # Irregularities I1–I16
│   ├── roadmap.html       # Next-session work
│   ├── requirements.html  # R1–R17 acceptance checklist
│   └── assets/            # styles.css, app.js
├── engine/                # Original projection toolkit + tests
│   ├── fantasylab_engine/ # metrics, expectation, model, trends, optimizer,
│   │                      # simulation, scoring, data
│   ├── tests/             # 79 tests (pytest)
│   └── README.md
├── research/              # Verification documents
│   ├── SOURCES.md         # Every claim → URL (manual review links)
│   ├── FINDINGS.md        # Verified facts F0–F10
│   ├── IRREGULARITIES.md  # Flags I1–I16
│   ├── PAYWALL_POLICY.md  # What/why we refused to copy
│   ├── REQUIREMENTS.md    # Requirement → proof matrix
│   └── VERIFICATION.md    # Pass 1/2/3 audit trail
└── README.md
```

## Hard rules this repo follows

1. **No scraping** of fantasylabs.com — their [Terms](https://www.actionnetwork.com/terms) (which govern the site) ban page-scraping/robots/reverse-engineering.
2. **No paywall circumvention** and **no reproduction** of subscription content (copyright + ToS §1).
3. **Only lawful data sources** for the engine — see the Green/Yellow/Red table in [docs/data-sources.html](docs/data-sources.html).
4. **Every factual claim has an openable source link.** No hallucinations: claims without a source are marked as local observations or inferences.

## Verification summary

| Pass | Focus | Result |
|------|-------|--------|
| 1 | Implement completely; verify | Research + engine + site built; first test run: **3 failures found** |
| 2 | Bugs / missing requirements / edge cases | 12 issues fixed (double-QB FLEX bug, return-type bug, percentile semantics, FD scoring provenance, docs drift…) → **79/79 green** |
| 3 | Re-check vs original request; quality pass | Requirements R1–R17 mapped, 15-claim hallucination audit 15/15, link check 0 failures |

Full audit trail: [`research/VERIFICATION.md`](research/VERIFICATION.md).

## Not affiliated

Independent research project. FantasyLabs, Action Network, Better Collective,
DraftKings, FanDuel, and all trademarks belong to their respective owners.
