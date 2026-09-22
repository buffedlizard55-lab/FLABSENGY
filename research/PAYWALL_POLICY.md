# Paywall & Rebuild Policy

## What the request asked

> "Rebuild anything that is behind a paywall, subscription."

## What was done instead (and why)

The literal reading — copying FantasyLabs subscription content or bypassing the paywall — is
blocked by two hard constraints found during verification:

1. **Terms of Use.** The Action Network Terms explicitly govern `www.fantasylabs.com`
   (`research/SOURCES.md` **S27**). They prohibit, verbatim:
   - "page-scrape", "robot", "spider" or other automatic devices to access or copy materials;
   - reproducing, republishing, mirroring or distributing Content without written consent;
   - "reverse engineer, decompile, disassemble … any of the source code".
   Violating these is a contract breach regardless of copyright.

2. **Copyright.** Subscription articles, projection tables, ownership projections, and model
   outputs are creative/compiled works owned by the Action Network Group (ToS §1). Rebuilding
   them = infringement.

## The compliant rebuild (what this repo delivers)

Reverse-engineering *ideas that the vendor published themselves in the open* is the legal
equivalent of a clean-room reimplementation. FantasyLabs documents its metric definitions in
public support docs (no login). This project therefore:

| Layer | Treatment |
|-------|-----------|
| Metric formulas (Plus/Minus, Consistency, Upside, Duds, Bargain Rating, Pts/Sal, Projected +/-, Opponent +/-, Implied Points, Ceiling/Floor semantics, Salary Change, ML%) | Reimplemented as **original code** from the public glossary definitions (S11–S14). No text copied beyond short attributed quotes of the definition itself. |
| Player-model architecture (user-weighted factors → ratings → backtest vs Plus/Minus → R²) | Rebuilt as an original implementation of the *described behavior* (S17). |
| Optimizer input set (projections, salary cap, correlations, groups/exposures, ownership) | Rebuilt as an original constrained optimizer (S16). |
| Trends semantics (count, avg expected, avg actual, points +/-, consistency) | Rebuilt as an original query/aggregation layer (S18). |
| Simulation pipeline description (simulate games → lineup pool → field model → contest sims → lineup rating) | Rebuilt as an original Monte-Carlo pipeline matching the *publicly described steps* (S19–S21). |
| Proprietary weights, actual projection numbers, ownership forecasts, Pro Trend definitions, article text | **NOT rebuilt.** Not public. Listed as limitations (I4, I6). |
| Data acquisition | Never from fantasylabs.com. From licensed/open sources only (`docs/data-sources.html`). |

## Decision record

- Paywall circumvention: **declined** → flagged as irregularity **I1**.
- ToS-prohibited scraping/reverse engineering of the site: **declined** → flag **I2**.
- Public-doc clean-room reimplementation: **accepted** → delivered in `engine/`.
- Subscription article republication: **declined** → flag **I3**.
