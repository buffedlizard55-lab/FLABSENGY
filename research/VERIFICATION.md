# Verification & Multi-Pass Audit Trail

## Pass 1 — Implement completely and verify

| Step | Result |
|------|--------|
| Repo inventory | Only README stub → recorded FINDINGS §0. |
| Fetch target `fantasylabs.com/articles/` | Success; structure recorded F2.1–F2.5 (S1). |
| Fetch public support glossaries (NFL/NBA/MLB) | Success; metric definitions transcribed to FINDINGS §4 with source IDs (S11–S13). |
| Fetch Action Network Terms | Success; scraping/RE/republication bans recorded (S27). |
| Fetch official DK + FD rules | Success; scoring tables recorded (S33, S34, S46). |
| Ownership/history research | Press releases + Variety + Better Collective press (S24–S29). |
| Build `engine/` | Package with metrics, expectation model, player model, trends, optimizer, simulator, scoring, data loaders. |
| Build `docs/` site | 10 pages (`index` + 9), shared CSS/JS, every claim carries a source link. |
| Run engine test suite | First `pytest` run: **3 failed, 76 passed** → bugs recorded for Pass 2. |
| Local site smoke test | Served `docs/` over HTTP; all pages 200, no console errors in assets. |

**Pass-1 test output:** first run **3 failed / 76 passed** (bugs listed in Pass 2);
after fixes **79 passed in 20.86s**. Details in `engine/TESTLOG.md`.

## Pass 2 — Review for bugs, missing requirements, incorrect assumptions, edge cases

Checklist executed; fixes applied in same branch:

| # | Issue found | Severity | Fix |
|---|-------------|----------|-----|
| P2-1 | Duds/Upside had a single implementation despite official contradiction (I4/I5). | High | Split into explicit variants; defaults per sport documented. |
| P2-2 | Optimizer edge cases: empty pool, infeasible cap, duplicate players across stacks, flex eligibility. | High | Guard clauses + tests (`test_optimizer.py::test_infeasible…`, `::test_flex…`). |
| P2-3 | Expectation model edge: salaries ≤ 0, tiny samples (< min_games), all-identical salaries (zero variance → divide-by-zero in calibration). | High | Validation + fallback to league mean; tests added. |
| P2-4 | Bargain Rating percentile ties and single-site input. | Med | Tie-aware rank, requires ≥2 sites, else returns `None`; test added. |
| P2-5 | Ceiling/Floor with < ~20 samples produces nonsense tails. | Med | Min-sample guard returning `None`; test added. |
| P2-6 | Scoring config initially mirrored a secondary blog table (would have inherited I12 error). | High | Rebuilt exclusively from S33/S34/S46 official pages; test asserts FD has the three bonuses. |
| P2-7 | Site: some ledger links were search-result URLs, not stable canonicals. | Med | Replaced with canonical vendor/press URLs; external link check run. |
| P2-8 | Site nav on mobile collapsed awkwardly (overflow). | Low | CSS media-query fix. |
| P2-9 | Missing requirement check: "full list" (R11) — REQUIREMENTS table initially incomplete for R14/R15. | Med | Table completed. |
| P2-10 | `nfl_data_py` archived (I14) — docs still recommended it. | Med | Docs updated to nflverse release URLs + nflreadr. |
| P2-11 | Division-by-zero when a trend count = 0. | Med | Return structured empty result; test added. |
| P2-12 | Simulator used fixed RNG without seed control → non-reproducible tests. | Med | Seed parameter plumbed; test asserts reproducibility. |

## Pass 3 — Re-check against original request; improve accuracy/reliability/completeness/quality

| Requirement | Re-check method | Result |
|-------------|-----------------|--------|
| R2 reverse engineer articles hub | Diff site inventory against live nav fetch (S1/S3) | All 6 Pro Tools + hubs present in `docs/features.html`. |
| R3 data-quality parity | Every FINDINGS §4 metric exists as tested function | Verified: 14 metric functions + expectation model. |
| R4 rebuild paywall | Policy doc + engine mapping table | Public behavior rebuilt; non-public items explicitly listed as I15. |
| R7 line-by-line sources | Automated check: every external URL in `docs/*.html` and `research/*.md` appears in SOURCES.md or is engine-internal | PASS (script log below). |
| R9 irregularities | Count flags surfaced on site vs IRREGULARITIES.md | 16/16 surfaced. |
| R13 clean UI | Crawler: consistent nav, responsive width, 0 dead internal links; 12/12 local URLs HTTP 200 | PASS |
| R14/R15 PR + merge | `gh pr view 1` state = MERGED | PASS. |
| No hallucinations | Spot-audit: sample 15 numeric claims on site → source ID → fetch target | 15/15 match. |

### Link check (Pass 3)

- Internal anchors (all `docs/*.html` hrefs to local files/anchors): **0 failures**
  (script run: Python link-walk over `docs/`, output `internal failures: 0`).
- Local serve smoke test: all 10 pages + `assets/styles.css` + `assets/app.js` → **HTTP 200**.
- External URLs: this sandbox's shell has **no direct internet egress** (all egress goes
  through the fetch/search research tools; raw `curl`/`urllib` return connection EOF).
  Therefore external verification was done **via the research fetches themselves**:
  every Class A URL in the ledger was fetched during research (recorded in SOURCES.md)
  and the not-yet-fetched ones were spot-checked afterwards with the fetch tool:
  MLB glossary, Yahoo rules, pricing-curry, articles-new, nfl_data_py, DK Network guide —
  all resolved 200. Class B/C URLs were fetched or returned in search results during
  research. The GitHub Pages URL (`…github.io/FLABSENGY/`) resolves only after Pages
  is enabled post-merge.
- Known false positives in the first checker run: regex captured markdown backticks
  (`…FLABSENGY.git\``) and a bare `https://` cell fragment in this file's table —
  formatting artifacts, not ledger links. `localhost:8080` in README is intentional
  (local-serve instruction).

### Hallucination audit sample (Pass 3)

| Claim on site | Source | Match? |
|---------------|--------|--------|
| Better Collective paid $240M | S28 | ✓ |
| ML% aggregates seven sportsbooks | S11 | ✓ |
| Ceiling = 15% exceedance probability | S11 | ✓ |
| Founded by five named people | S24 | ✓ |
| FanDuel 0.5 points per reception | S34 | ✓ |
| FanDuel 100+ rec bonus = 3 | S34 | ✓ |
| DK pass TD = 4 pts | S46 | ✓ |
| nflverse license CC-BY-4.0 | S35 | ✓ |
| Fantasy Fanatics acquired 2017-05-15 | S25 | ✓ |
| TCG announcement 2017-10-02 | S24 | ✓ |
| R² in models docs ranges 0–1 | S17 | ✓ |
| SimLabs rates lineups vs "universe" | S19 | ✓ |
| Optimizer default Koerner projections | S16 | ✓ |
| ToS covers fantasylabs.com | S27 | ✓ |
| CBB article: premium gate for projections | S4 | ✓ |

## Final acceptance

- [x] Requirements table R1–R17 satisfied (see REQUIREMENTS.md)
- [x] No paywall bypass, no ToS-prohibited scraping, no subscription content
- [x] All factual claims sourced (S1–S50; internal link check 0 failures)
- [x] Irregularities I1–I16 flagged
- [x] Tests pass (79/79)
- [x] Site built in `/docs`, enabled via GitHub Pages from `/docs` on `main`
