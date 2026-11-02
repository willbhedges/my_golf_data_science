# Drumm Farm GC: rebuild QA (2026-11-02)

**Verdict: PUBLISH.** The reviewer's main fix (attach the card) is applied. The page now has Tour and Championship sets
with the AllSquare card yardages and pars, and the hole 7 Tour tee is on the review spot. The Tour tees on 8 and 13 are
still estimates, as the reviewer expected.

Page checked: `course_data/library/drumm_farm/page.html`, built 2026-11-01T21:47Z. Both solved sets (Tour 7121,
Championship 6564) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems. I looked at every
phone hole picture. Pars 4 4 3 4 4 3 5 4 5 / 4 4 4 4 3 5 4 3 5 = 72, as in the review. Championship differs from the
review card by 1 yd on 4 and 18 (metre rounding).

## Review fixes

| fix in review.md | applied? |
|---|---|
| Rebuild with the card (Tour + Championship) | **yes.** The card source is AllSquare. The Tour per-hole overrides equal the card. The Championship values come from the card; the `"*"` overrides did not leak onto them. |
| 7 Tour tee about 53 yds behind the 538 box (39.0632948, -94.3985147) | **yes.** Tee source `review`, 0 yds from the point. Page 598 / measured 591. Driver on the line, fairway 67%. |
| 8, 13 Tour boxes not mapped | still estimates: 8 Tour is a lidar pad 27 yds from any OSM box (384 measured / 390), and 13 Tour is a walk-back (414). Neither changes the club. |

## Holes

| hole | Tour | Championship | note |
|---|---|---|---|
| 1-6, 9-12, 14, 15, 17, 18 | OK | OK | yardage within 8 of the card (box centre gap); par-3 boxes on the green |
| 7 | **fixed** | OK | |
| 8 | OK (tee uncertain) | OK | forecast Driver / calm 2-wood, aim 24 left; Champ 4-wood aim 32 left, fairway 56% |
| 13 | OK (tee uncertain) | OK | Driver lands by the right fairway bunker, fairway 52% |
| 16 | OK | OK (marginal) | Champ Driver to 42 yds short of a 320-yd green along the tree line (fairway 2%, trees 8%); 2-wood is 0.035 behind. Model choice |

## Next fix

None blocking. Optional: map the Tour boxes on 8 and 13 if imagery shows them.
