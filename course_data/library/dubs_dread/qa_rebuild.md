# Dub's Dread Golf Club: rebuild QA (2026-11-02)

**Verdict: PUBLISH.** The card, the hole 4 routing, the hole 12 par and the tee / yardage fixes are all applied. One
uncertain tee is left (9 Championship, as reviewed).

Page checked: `course_data/library/dubs_dread/page.html`, built 2026-11-02T03:27Z (GitHub Actions run 41378665063).
Both solved sets (Championship, Back, par 72) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page
problems. I looked at every phone hole picture. Card: `card_golfify.json`, Championship 7,230 / Back 6,687. Page
yardage = card on all 36 hole-sets. The review's bare `yards` applied to Championship only, as intended; Back reads its
own card on every hole.

## Review fixes

| fix in review.md | applied? |
|---|---|
| 4: real par 3 (way 1029130675, tee way/505295054 to green way/505295060), 216 | **yes.** Tee snapped 1 yd to OSM tee 505295054, 217 measured. No two holes share a green any more |
| 12: par 5, 547 | **yes.** Par 5, 547 measured; 2-wood off the tee |
| 5: tee to the hole-way start, 382 | **yes.** 377 measured (Back 351 = card) |
| 9: tee to the hole-way start, 418 (uncertain) | **applied, still short.** 397 measured vs 418, build warning "no OSM tee box at that yardage". As the reviewer expected |
| 3, 6, 7, 13 yardages 446 / 467 / 550 / 420 | **yes.** Measured 441 / 468 / 550 / 421 (13 on a lidar pad) |

## Holes

| hole | Championship | Back | note |
|---|---|---|---|
| 1 | OK (marginal) | OK | Driver into the dogleg-right corner, trees 28% (judgement call, as reviewed) |
| 2, 3, 6-8, 10-14, 16, 18 | OK | OK | |
| 4, 5, 12 | **fixed** | OK | |
| 9 | OK (uncertain, 21 short) | OK | see above |
| 15 | OK | OK (marginal) | Back 4-wood into the dogleg-left corner, trees 16% |
| 17 | OK | OK (marginal) | Driver near the right-hand trees (15-18%) |

## Remaining (optional)

9 Championship: the back tee is unmapped. Add a tee point about 20 yds behind the hole-way start if a mapper confirms
it on imagery.
