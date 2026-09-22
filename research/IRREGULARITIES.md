# Irregularities & Flags for Human Review

Severity: 🔴 blocking/illegal-as-requested · 🟠 needs decisions · 🟡 informational.

| ID | Sev | Finding | Evidence | Action taken |
|----|-----|---------|----------|--------------|
| **I1** | 🔴 | Request "rebuild anything behind a paywall" = paywall circumvention + copying subscription content. Blocked by copyright and ToS §2 (no reproduction/republishing without consent). | S27 | Declined literally. Rebuilt only publicly documented functionality as original code. Documented in `research/PAYWALL_POLICY.md`. |
| **I2** | 🔴 | Request "reverse engineer the site" collides with ToS ban on page-scraping, robots, and reverse engineering of source code — ToS governs fantasylabs.com explicitly. | S27 | No bulk scraping, no code RE, no robots.txt probing. Research = a handful of direct public page reads + search results, analogous to manual browsing. |
| **I3** | 🔴 | Subscription articles/projections/ownership numbers are copyrighted "Content" per ToS §1 (which even claims *fantasy salaries, trends, systems*). | S27 | Zero subscription content reproduced. |
| **I4** | 🟠 | **Official docs disagree on "Duds":** NFL glossary = "fewer than half his salary-based expectation"; NBA **and MLB** glossaries = "≥ ½ standard deviation below" expectation. NFL is the outlier (2:1 against it). | S11 vs S12 vs S13 | Engine implements **both** (`dud_rate_half_expectation`, `dud_rate_half_sd`); house default = half-SD (majority official wording); documented. |
| **I5** | 🟠 | **Official docs disagree on Upside/Breakout:** NBA **and MLB** glossaries = "≥ ½ SD above" expectation; NFL glossary words it as "highest Plus/Minus scores" (vague). NFL is again the outlier. | S11 vs S12 vs S13 | Engine default = ½-SD definition (2:1 official majority); NFL PM-rank variant kept as `upside_rate_highest_pm`. |
| **I6** | 🟠 | Ceiling/Floor methodology *differs by sport* (NFL: PECOTA-style 30-comps sim score; NBA: volatility model from usage/on-off/shot charts). Both are paywalled features in practice. | S11 vs S12 | Engine ships a generic percentile-band method + a comps-based method; neither claims to be their exact production model. |
| **I7** | 🟡 | Third-party review says FantasyLabs "was acquired by The Action Network in 2017" — imprecise: TCG *formed* Action Network by acquiring FantasyLabs (+2 others). | S31 vs S24 | Findings use primary framing; S31 marked Class C. |
| **I8** | 🟡 | Date mismatch on Action Network formation: press release 2017-10-02; CBINSights 2017-10-03; PitchBook buyout date 2017-09-30. | S24 vs S43 vs S30 | All three dates recorded; press release treated as authoritative announcement date. |
| **I9** | 🟠 | **Current pricing not statically verifiable** — `/pricing/` renders client-side; only aged A/B pages (`pricing-curry`, `pricing-bain`) and a 2025 promo article show numbers, all different ($24.95–$59.95/mo band). | S22, S23, S32 | Pricing section presents ranges as *dated snapshots*, not "the" price. |
| **I10** | 🟡 | `https://www.fantasylabs.com/articles-new/` is publicly reachable and labeled "(Test)" in search index — test surface exposed on production host. | S44 | Reported only. Not accessed beyond existence check; recommend vendor fix. |
| **I11** | 🟡 | A search index surfaced a raw JSON API path (`/api/players/news/1/`) returning player-news records without apparent auth. Unprotected endpoint on a ToS-protected site. | *(observed in search results 2026-09-22; endpoint intentionally not interrogated further per I2)* | Flagged for vendor/user review. We do not consume it. |
| **I12** | 🟠 | **Scoring-source conflict:** secondary DFS guides (2019–2026) claim FanDuel has *no* yardage bonuses; FanDuel's official rules page (fetched today) lists 3-pt bonuses at 100+ rush, 100+ rec, 300+ pass. Either FD changed scoring or the guides are wrong. | S34 vs guides cited in S42-adjacent tables | Engine trusts **official pages only** (S33/S34/S46). Secondary tables excluded from config. |
| **I13** | 🟡 | Support docs live on two domains (`support.fantasylabs.com` and `fantasylabs.zendesk.com`) serving overlapping Zendesk content — link-rot/duplication risk. | S11 vs S17 | Ledger cites both where used. |
| **I14** | 🟡 | `nfl_data_py` (commonly recommended) was **archived 2025-09-25**; pipelines built on it need a successor (nflreadr/nfl-data-py alternatives or direct release URLs). | S50 | Noted in data-sources doc; engine reads raw CSVs/parquet from nflverse release URLs instead. |
| **I15** | 🟡 | Ownership projection methodology, Pro Trend definitions, position projection formulas, and salary-expectation regression parameters are **not public** — parity with "same data quality" is bounded by that absence. | §10 findings | Listed as residual gaps in roadmap; marked *unknown*, not guessed (no-hallucination rule). |
| **I16** | 🟠 | NBA/`stats.nba.com` and unofficial DK endpoints sit in a ToS gray zone (undocumented APIs, personal-use clauses). Using them at scale for a public product is risky. | S38, S39, S40, S41 | Data-sources page labels each source Green/Yellow/Red; engine defaults to Green sources; no DK scraping code shipped. |

## What is NOT flagged

- No broken links among Class A sources in the final ledger (link-check pass recorded in `VERIFICATION.md`).
- No numeric metric definition in `engine/` lacks a glossary source ID.
