# WeaverRidge Golf Club: rebuild QA, second pass (2026-11-02)

**Verdict: PUBLISH.** The per-set yardages now land on the right sets. Black 13 and 18 play from the back tees, and
Black 5 is no longer in front of Gold. One caveat on 5 Black (below).

Page checked: `course_data/library/weaver_ridge/page.html`, built 2026-11-02T06:24Z (GitHub Actions run 41392580512).
Both solved sets (Black, Gold, par 72) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page
problems. I looked at every phone hole picture. Card: `card_review.json` (golfify). Black total 6,992 = 7,030 with 16
at the reviewed 401; Gold 6,543 = card.

## First-pass fixes

| fix | applied? |
|---|---|
| 13 Black off the Gold tee | **yes.** 432, measured 427, on an OSM box 24 yds behind Gold (403) |
| 18 Black off the Gold tee | **yes.** 556, measured 554, 19 yds behind Gold (535) |
| 11 per set | **yes.** Black 489 (484 measured, on the Gold box: 5 yds, minor); Gold 482 |
| 14 / 16 per set | **yes.** Black 406 / 401, Gold 362 / 401 |
| 5 Black pinned to the Gold box | **yes.** The marker is 2 yds behind Gold (365 vs 363 measured), not in front. |

## Holes

| hole | Black | Gold | note |
|---|---|---|---|
| 1-4, 6-9, 12, 14-17 | OK | OK | |
| 5 | OK (caveat) | OK | Black shows the card 387 but plays from the Gold box (365; the note says "measured 365 vs card 387"). The tips are unmapped and not visible on NAIP, as reviewed. Driver aim 40 right across the lake corner to the fairway (83%) |
| 10 | pick on the bound (as reviewed) | same | 4-wood / Driver aim 40.0 right toward the creek/tree band. Solver aim-clamp issue, not a geometry fault |
| 11 | minor (on the Gold box, 484 vs 489) | OK | |
| 13, 18 | **fixed** | OK | |

## Remaining (optional)

1. Hole 10 aim on the ±40 bound (pipeline, decide step), as on Gustin 6/16, Colbert 13 and St Andrews 15.
2. When the hole 5 tips are mapped, drop the Black `tee_ll` pin.
