# Buffalo Ridge Springs: rebuild QA (2026-11-02)

**Verdict: PUBLISH.** The reviewer's one suggested fix (3 Gold tee) is applied, and every hole on both sets matches the
card.

Page checked: `course_data/library/buffalo_ridge/page.html`, built 2026-11-01T21:02Z. Both solved sets (Buffalo, Gold)
were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems. I looked at every phone hole picture.
Card: golfify, Buffalo 7036 / Gold 6616, par 71. Page yardage equals the card on all 36 hole-sets (measured within 5,
except 15 Buffalo 352 measured vs 366, OSM box, same as at review).

## Review fixes

| fix in review.md | applied? |
|---|---|
| 3 Gold: tee to the back of the long pad (36.584663, -93.1935109), about 378-385 | **yes.** Tee source `review`, 0 yds from the fix point. Page 385 / measured 386. Driver, aim 22 left, fairway 74%. |

## Holes

| hole | Buffalo | Gold | note |
|---|---|---|---|
| 1-2, 4-5, 7-12, 15, 17 | OK | OK | par-3 boxes on the green; Driver/4-wood landings on fairway |
| 3 | OK | **fixed** | see above |
| 6 | OK | OK (marginal) | Gold Driver aim 8 left: fairway 32%, sand 11%, trees 13%. 4-wood is 0.019 behind. Model choice |
| 8 | OK (tee not photo-verified, as reviewed) | OK | lidar pad 19 yds behind Gold box, 524 |
| 13 | OK | OK | Driver aim 20-28 left toward the left tree line, fairway 60-62% |
| 14 | OK | OK | Gold Driver lands among the fairway bunkers (sand 16%, fairway 47%). Model choice |
| 16 | OK | OK (walk-back, as reviewed) | 379 = card |
| 18 | OK | OK | |

## Next fix

None required. Publish.
