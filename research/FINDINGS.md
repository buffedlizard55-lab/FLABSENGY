# Verified Findings

Every numbered claim links to an ID in `SOURCES.md`. Claims without a source ID are either
(a) statements about this repository, or (b) explicitly marked *Inference*.

---

## §0 Repository state at start

- **F0.1** The repo contained exactly one file, `README.md`, content `# FLABSENGY` (11 bytes), single commit `062eb69 Initial commit`. *(Observation, 2026-09-22.)*
- **F0.2** Remote: `https://github.com/buffedlizard55-lab/FLABSENGY.git`; working branch `arena/01a0ca5d-flabsengy`. *(Observation.)*

---

## §1 Company / ownership history

- **F1.1** FantasyLabs was founded by Daniel Fabrizio, Jonathan Bales, Peter Jennings, Kevin Cassata, and Michael Bernhardt; Mark Cuban is an investor. [S24]
- **F1.2** On 2017-05-15 FantasyLabs announced acquisition of The Fantasy Fanatics LLC (founder Ryan Patsko joined the company); Jonathan Bales is quoted as President and CEO. [S25]
- **F1.3** On 2017-10-02 The Chernin Group (TCG) announced formation of **The Action Network**, acquiring Sports Insights, FantasyLabs, and SportsAction; Mike Kerns (TCG President of Digital) announced; Mark Cuban quoted re: his FantasyLabs investment. [S24]
- **F1.4** Variety independently reported the same roll-up on 2017-10-03 and notes FantasyLabs was "Mark Cuban-backed". [S26]
- **F1.5** Action Network's own About page: founded October 2017 from the three acquired companies; describes FantasyLabs as "a daily fantasy modeling platform". [S29]
- **F1.6** On 2021-05-03 Better Collective announced acquisition of 100% of Action Network, Inc. for **$240 million** (cash & debt-free basis); Action continues as a separate business unit; Fantasy Labs named among subscription products. [S28]
- **F1.7** FantasyLabs seed round recorded 2016-01-07 (investors incl. Mark Cuban per CBI profile). [S30][S31]
- **F1.8** CBI records the Action Network acquisition date as 2017-10-03 — one day after the press release. → **Irregularity I8.**

---

## §2 The target surface: fantasylabs.com/articles/

Direct fetch 2026-09-22. [S1]

- **F2.1** Page title "FantasyLabs: Daily Fantasy Sports Analysis"; H1 "Daily Fantasy Sports".
- **F2.2** Section "Popular Pro Tools" links: **SimLabs**, **Player Models**, **Lineup Optimizer**, **PickLabs**, **Trends Tool**, **Contests Dashboard**.
- **F2.3** Section "How To" links tutorials (e.g., "How to Use the NFL DFS Lineup Optimizer", MMA optimizer tutorial).
- **F2.4** Article feed with sport tags (NFL, CFB, NBA, MLB, GOLF, NASCAR, UFC) and per-sport landing hubs.
- **F2.5** Marketing CTAs link to `/subscribe` and `/pricing/` (subscription funnel).
- **F2.6** Example article (Week 2 NFL 2026) states Player Models "house our projections" and that decisions combine projection, salary, ceiling, projected ownership — plus fields Plus/Minus, Bargain Rating, Pro Trends, median/ceiling/floor. [S2]
- **F2.7** Preseason projections article (2021) publicly lists preseason model inputs: coach/teams' historical preseason usage, player skill, playing-time reporting updated in real time. [S6]

---

## §3 Product inventory (from public site navigation)

Direct fetch of `/subscribe` navigation, 2026-09-22. [S3]

| Sport/area | Publicly linked tools |
|------------|----------------------|
| NFL | SimLabs, Models, PickLabs, Weekly Projections, Trends, Ownership, Contest Dashboard, Vegas, News, Matchups, Correlations |
| NBA | SimLabs, Models, PickLabs, Trends, Ownership, Contest Dashboard, Vegas, News, Matchups, On/Off |
| MLB | SimLabs, Models, PickLabs, **PlateIQ**, Trends, Ownership, Contest Dashboard, Vegas, News, Lineups, Correlations |
| GOLF (PGA) | SimLabs, Models, PickLabs, Trends, Ownership, Contest Dashboard, Correlations |
| NHL | Models, PickLabs, Trends, Ownership, Contest Dashboard, Vegas, Team Lines, Team Ratings, Starting Goalies |
| CBB / CFB / MMA / NASCAR / WNBA | Multi-lineup (models), ownership, contests (varies) |
| Season-long | Best Ball Rankings, Season Projections, Snake/Auction Cheat Sheet Builders, Weekly Projections, Tiered Rankings, Survivor Analysis, Mock Drafts |
| PickLabs | Pages for Bet365, BetMGM, Caesars, DraftKings, Fanatics, FanDuel, HardRock, PrizePicks, Sleeper, Underdog |

- **F3.1** CBB projections product update (2023): projections include **median** and **points/salary**; premium-subscription gated; optimizer creates "300 lineups in seconds"; supports custom/blended projection upload. [S4]
- **F3.2** Conditional projections ("Scenarios", 2021): in/out toggles for key players create custom projection sets; base set assumes certain players out/in. [S7]
- **F3.3** Custom Projection Upload: template CSV or copy/paste; active-set checkbox management. [S8]
- **F3.4** NBA partnership with **ShotQuality** (2026): location data, shot quality, predicted scores feed NBA product. [S9]
- **F3.5** Marketplace third-party projection providers: Derek Carty's **THE BLITZ** (NFL, 2026), **THE BAT X** (MLB, 2026). [S5][S10]
- **F3.6** Optimizer article (2026): baseline NFL projections from Sean Koerner; inputs = projections (+ceiling/floor, custom uploads, aggregates), salary constraints, correlation/stack rules, player groups & exposures, ownership projections. [S16]

---

## §4 Publicly documented metric definitions (the data-quality core)

All from FantasyLabs public support glossaries (no login). [S11 NFL][S12 NBA][S13 MLB][S14 Trends how-to][S17 Models tutorial][S18 Trends article]

| Metric | Official definition (paraphrased; source) |
|--------|-------------------------------------------|
| **Plus/Minus** | actual fantasy points − expected fantasy points *based on salary* (historical salary→points database). [S11] |
| **Implied Points** | expected fantasy points (historically) based on cost. [S11] |
| **Projected Plus/Minus** | median projection − salary-based expectation. [S11] |
| **Pts/Sal** | projected points per $1,000 of salary. [S11] |
| **Consistency** | % of games produced *within one standard deviation* of salary-based expected points. [S11][S12] |
| Upside / Breakout | NBA glossary **and MLB glossary**: % of games ≥ ½ SD *above* salary-based expectation. NFL glossary words it differently ("most frequently posted the highest Plus/Minus scores"); NFL is the outlier. → **I5** [S11][S12][S13] |
| Duds | NBA + MLB: % of games ≥ ½ SD *below* expectation. NFL: % of games scoring *fewer than half* salary-based expectation. NFL is the outlier. → **I4** [S11][S12][S13] |
| **Bargain Rating** | historical percentile rank of cross-site salary bargain at a position (typical DK↔FD salary difference). [S11][S12] |
| **Opponent Plus/Minus (Allowed)** | opponent's fantasy production allowed to a position, salary-adjusted (naturally strength-of-schedule adjusted). [S11][S12] |
| **Salary Change** | player's salary change over a period. [S11] |
| **ML%** | % of moneyline bets on each team; Vegas data aggregated from **seven sportsbooks**. [S11] |
| **Ceiling (NFL)** | point total expected to be *surpassed with 15% probability*; PECOTA-style sim-score: 30 most comparable players' history. [S11] |
| **Floor (NFL)** | point total expected to be *failed to reach with 15% probability*; same 30-comps method. [S11] |
| **Ceiling/Floor (NBA)** | same 15%/15%/70% band, but from a **volatility rating** built on usage, on-off, shot charts (own and opponent). → methodology differs by sport, both officially documented. [S12] |
| **Pro Trends** | pro-created situational trends already surfaced in models/player cards; strongly linked to value. [S11] |
| **Trends outputs** | Count, Avg Expected Pts, Avg Actual Pts, Points +/-, Consistency; distribution charts by day/month. [S14][S18] |
| **Model R²** | correlation between user-weighted player ratings and historical Plus/Minus (0–1). [S17] |
| **Vegas Score** | percentile-style rating of opposing/implied team scoring context (example: 93 Vegas Score ⇒ implied run rank bottom 7% historically). [S17] |
| **Unique Players** | lineup must differ from previous at X roster spots. [S12] |

- **F4.1** Official NBA glossary also documents **PER** ( league-average 15.00) among player stats. [S12]

---

## §5 Simulation pipeline (publicly described behavior)

Sources: FantasyLabs-sim FAQs on RotoGrinders (publisher-hosted partner content) [S19][S20][S21].

- **F5.1** SimLabs "simulates every aspect of a DFS slate, from the plays in each game down to the results of a DFS contest." [S19]
- **F5.2** Pipeline steps published: (a) simulate games thousands of times; (b) generate massive lineup pool; (c) shape/filter pool to resemble projected real contest field across 3 common contest types; (d) simulate contest results thousands of times; (e) rate each lineup vs the "universe". [S19]
- **F5.3** User combines sim results with projections, correlation, upside, ownership via weight sliders ("Simulation Weight", "Ownership Weight", etc.). [S19]
- **F5.4** Per-lineup bars: Projection 0–99 relative rating; pOWN 0–99 ownership rating. [S19]

---

## §6 Pricing signals (volatile — see I9)

- **F6.1** Historical pricing page snapshot `/pricing-curry/` (aged 2022): NBA-only $29.95/mo; All-Access monthly $59.95; All-Access annual $29.95/mo billed annually. [S22]
- **F6.2** Historical `/pricing-bain/` (aged 2021): $4.95/5-day trial; All-Access annual $24.95/mo (was $34.95); NBA-only $30.00/mo (Justin Phan projections). [S23]
- **F6.3** Action Network's own 2025 article: FantasyLabs NFL annual $49.95 w/ promo; 2025-26 Season Bundle $299.95. [S32]
- **F6.4** Live `/pricing/` fetch returned nav only (prices render client-side) — current price **not statically verifiable**. → **I9**

---

## §7 Legal layer

- **F7.1** Action Network Terms govern fantasylabs.com explicitly. [S27]
- **F7.2** ToS §2 bans: deep-link/page-scrape/robot/spider access; reproducing/mirroring Content; reverse engineering/decompiling source code; unauthorized access; disproportionate load. [S27]
- **F7.3** ToS §1 claims ownership over "fantasy-related player salaries, player usage statistics, historical player performance, … lines, odds, betting percentages, … fantasy trends, fantasy systems … picks, articles …" — i.e., the data layer itself is claimed Content. [S27]
- **F7.4** Subscriptions: no refunds; cancel-anytime language in §4. [S27]
- **F7.5** DraftKings rules (official): salaries "determined based on historical statistics and aspects of a player's upcoming matchup"; stats from third-party providers (Stats Perform, Sportradar, FightMetric, GameScorekeeper, Champion Data, leagues). [S33]
- **F7.6** FanDuel official rules page provides full per-sport scoring tables (NFL: 0.5/rec, 0.1/rec-yd, **100+ rec-yd bonus 3**, **100+ rush-yd bonus 3**, **300+ pass-yd bonus 3**, pass TD 4, INT −1, fumble −2 …). [S34] → conflicts with secondary guides claiming FD has no yardage bonuses: **I12**.

---

## §8 Legitimate data sources for our own system

- **F8.1** **nflverse** (`nflverse-data`, `nflverse-pbp`): open NFL data, **CC-BY-4.0** license; nflfastR-based pbp since 1999; FTN charting subset CC-BY-SA-4.0 with attribution. [S35][S36]
- **F8.2** **MLB Stats API** (`statsapi.mlb.com`): official, free, no key for core endpoints (schedule, live game, box scores, play-by-play, players, stats); docs at docs.statsapi.mlb.com. [S37]
- **F8.3** **NBA stats endpoints** (`stats.nba.com`): rich but *undocumented*, no key, browser-header requirements, rate limits; unofficial wrappers (`nba_api`) exist; NBA.com ToS limits commercial reuse — treat as personal-research grade, not redistribution. [S38][S39]
- **F8.4** **DraftKings DFS**: no official public developer API for salaries; official contest CSV downloads exist; unofficial reverse-engineered clients (e.g., `draft-kings` PyPI, `draftkings_client`) are explicitly unsupported and ToS-risky at scale. [S40][S41]
- **F8.5** **FanDuel/DK scoring**: official rules pages are the canonical reference (S33, S34) — secondary blogs disagree on bonuses (I12).
- **F8.6** **Yahoo NFL official rules** (secondary-platform reference): 0.5 PPR etc. [S42]

---

## §9 Third-party context (secondary — corroborate before relying)

- **F9.1** Stokastic comparison (2026): FantasyLabs' reputation built on Player Models + Trends; surrounding tools: optimizer, ownership projections, correlations, contest dashboard, player props, PickLabs; SimLabs added simulations. [S32]
- **F9.2** PropsBot review (2026): claims launch 2015, Cuban backing 2016, acquired by "The Action Network" in 2017 — the acquisition framing is imprecise vs primary sources (TCG *formed* Action Network by acquiring FantasyLabs). → **I7** [S31]
- **F9.3** PitchBook: Buyout/LBO 2017-09-30 completed; Seed 2016-01-07. Date differs from press release (I8). [S30]

---

## §10 What is provably NOT public

Statements of absence, verified by attempting the public surfaces on 2026-09-22:

- **F10.1** Actual projection formulas per position (beyond metric definitions) — not published.
- **F10.2** Model factor library beyond documented examples (Vegas Score, Park Factor, Lineup Order Percentile named in tutorial) — full list not published. [S17]
- **F10.3** Ownership projection methodology — not published.
- **F10.4** Pro Trend boolean definitions — not published (only their outputs).
- **F10.5** Historical salary→expectation regression parameters — not published.
- **F10.6** SimLabs field-model calibration details (how contests/fields are shaped) — only steps, not parameters.
- **F10.7** Paywalled article bodies were not accessed (no login; no paywall bypass attempted).
