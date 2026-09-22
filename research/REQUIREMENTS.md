# Requirements — Full List

Derived line-by-line from the original request. Status reflects the final state of this repository after implementation.

| ID | Requirement | Status | Where satisfied |
|----|-------------|--------|-----------------|
| R1 | Review the repo | Done | Initial repo contained only `README.md` (stub `# FLABSENGY`). Logged in `research/FINDINGS.md` §0. |
| R2 | Reverse engineer https://www.fantasylabs.com/articles/ | Done (public-surface only) | Feature/product inventory in `research/FINDINGS.md` §2–§3, built from direct page fetches of public URLs. |
| R3 | Get same data quality used in the projection system | Done (methodology level) | Every publicly documented metric reimplemented from FantasyLabs' own public support-doc definitions in `engine/fantasylab_engine/metrics.py` + `expectation.py`; data-pipeline substitutes listed in `docs/data-sources.html`. |
| R4 | Rebuild anything behind a paywall/subscription | Partial — see policy | Paywalled *content* and *proprietary model weights* are NOT reproduced (copyright + ToS prohibition — `research/IRREGULARITIES.md` I1, I2). Publicly documented *functionality* (metric formulas, model architecture pattern, optimizer inputs, trends semantics) IS rebuilt as original code in `engine/`. Policy: `research/PAYWALL_POLICY.md`. |
| R5 | Examine strategies, data, and everything built into the website | Done (public surface) | `docs/features.html`, `docs/metrics.html`, `docs/methodology.html`. |
| R6 | Build own projection system for sports | Done | `engine/` — original Python package: expectation model, 14 metrics, weighted player model with R² backtest, lineup optimizer, Monte-Carlo slate simulator, official scoring rules. |
| R7 | Work line by line; official verified trusted sources; links for manual review | Done | `research/SOURCES.md` — every claim has an ID, exact source URL, source class (primary/secondary), and fetch date. Mirrored on the site at `docs/ledger.html`. |
| R8 | No manual input; work autonomously | Done | No clarification questions were asked; all work performed in-session. |
| R9 | Flag irregularities for review | Done | `research/IRREGULARITIES.md` (16 items) + surfaced on `docs/limitations.html`. |
| R10 | No hallucinations / verify | Done | Every factual statement in docs/site traces to a SOURCES.md ID. Pass-2 and Pass-3 audit described in `research/VERIFICATION.md`. |
| R11 | Full list following requirements | Done | This file. |
| R12 | GitHub Pages site: clean UI, user-friendly, simple, organized | Done | `docs/` static site, no build step, tested locally. |
| R13 | Site includes all relevant info, easy to read, official verified links | Done | 9 pages: Overview, Features, Metrics, Methodology, Data Sources, Source Ledger, Paywall & Legal, Limitations, Roadmap. |
| R14 | Create a pull request | Done | PR #1 `arena/01a0ca5d-flabsengy` → `main`. |
| R15 | Merge the PR onto main | Done | Merged; Pages enabled from `/docs` on `main`. |
| R16 | Suggestions for remaining work + limitations | Done | `docs/roadmap.html` + `docs/limitations.html` + `research/IRREGULARITIES.md`. |
| R17 | Multiple passes (1: implement+verify, 2: review bugs/assumptions/edge cases, 3: re-check vs original request, improve) | Done | Audit trail in `research/VERIFICATION.md`. |

## Explicit non-goals (enforced)

| ID | Non-goal | Reason |
|----|----------|--------|
| N1 | Scraping fantasylabs.com content programmatically | ToS prohibition (`research/SOURCES.md` S27) — page-fetch research used a small number of manual page reads only, no bulk crawling, no robots.txt violation, no login-walled area access. |
| N2 | Reproducing subscription-only articles, projections, ownership numbers, or model outputs | Copyright (ToS §1, S27) and subscription access was never obtained. |
| N3 | Reverse-engineering FantasyLabs client/server source code | Explicit ToS prohibition (S27). |
| N4 | Cloning TradeSecret/proprietary weighting schemes | Not publicly disclosed; would be misappropriation. Our model weights are our own, tunable by the user. |
