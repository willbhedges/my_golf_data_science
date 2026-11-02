# Heritage Park GC (Olathe KS): rebuild QA (2026-11-02)

**Verdict: PUBLISH, with 7 / 9 / 18 left as CHECKs.** The build now completes with the 18 supplement hole ways. The
routing errors from rv07 are fixed: holes 1, 2, 10, 11 and 12 are the real holes, and every hole matches the card.
Hole 7 is the weakest; see below.

Page checked: `course_data/library/heritage_park/page.html`, GitHub Actions run 41479479995 (committed 19:03Z). Both
solved sets (Blue 6,876, White 6,327, par 71) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page
problems. I looked at every phone hole picture, and at the desktop pictures of 7.

## Review fixes

| fix (review.md rv07) | applied? |
|---|---|
| 1 (was missing): tees 930838113-115 -> green 930838116 | **yes.** 371 / 368 Blue, 336 / 337 White |
| 2: tees 930838117-120 -> green 930838121 | **yes.** Par 3 over water, 192 / 193 |
| 10: north tees -> green 930838168 | **yes.** 394 / 396 |
| 11 (was missing): tees 170-173 -> green 930838176 | **yes.** Par 3, 224 / 227 |
| 12: tees 177-179 -> green 930838182 | **yes.** 392 / 395 |
| 5: Blue onto box 930838135 | **yes.** On a box, 622 / 629 |

## Checks

| check | result |
|---|---|
| Card | golfify; page yardage = card on all 36 hole-sets; measured within 7 yds (Blue 5 -7, White 10 +7) |
| Mapper / native cards | not used; `native.json` empty, as expected |
| Water filter | ran; 2,296 of 2,643 m2 of vision water was on roads and was dropped. Water in the stats is only the ponds on 2 / 3 / 16 |
| Aims past ±40 | none (largest Blue 7 -37.5) |

## Holes

| hole | Blue | White | note |
|---|---|---|---|
| 1-4, 6, 8, 10-17 | OK | OK | tees on OSM boxes |
| 5 | OK | OK (CHECK) | White on a lidar pad 19 yds from the box, 597 / 598 |
| 7 | **uncertain** (CHECK) | OK (marginal) | Blue is still on a lidar pad beside the cart path (no OSM box for 433). Its Driver -37.5 lands on the wide fairway **left of the cart path**. The White pick (from its OSM box, 393) lands 44 yds right, across the path. The Blue landing is inside an OSM fairway polygon that holes 7 and 8 share, so it may be hole 8's side. The page shows a CHECK (tee) on Blue |
| 8, 10, 15 | OK | OK | lone fairway trees in the landing ovals are not mapped as trees (trees 0-6%). Minor |
| 9 | uncertain (CHECK) | uncertain (CHECK) | back tees not in OSM; Blue lidar pad / White walkback match the card |
| 18 | uncertain (CHECK) | OK (CHECK) | Blue walked back 38 yds; card ~45 longer than every box (as reviewed) |

## Next fix

None blocking; 7 / 9 / 18 show as CHECKs. To clear 7: confirm the Blue tee on the ground, or put it on the line
behind box 930838147 (`fix tee_ll`), and check which side of the cart path is hole 7's fairway.
