# St Andrews GC (Overland Park): rebuild QA (2026-11-02)

**Verdict: PUBLISH.** The reviewer's must-fix (hole 16 Black tee) is fixed and every other hole matches the review.
One caveat on 15 Black is noted below.

Page checked: `course_data/library/st_andrews_op/page.html`, built 2026-11-01T20:43Z (GitHub Actions run 41346747941).
Both solved sets (Black, Blue) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems. I looked
at every phone hole picture.

The card is now opengolfapi rather than golfify, but its Black and Blue yardages and pars are identical to the review's
card, apart from the 16 override. `consensus.changes` is empty, so the Gustin-style card swap does not apply here.

## Review fixes

| fix in review.md | applied? |
|---|---|
| 16 Black: tee off the 15th green, onto the back of the Blue box (about 393) | **yes.** The tee is on the OSM box in front of the pond. The page shows 393 (measured 386; Blue 391 on the same box). The pick is Driver +26, fairway, 0% trees. |

## Holes

| hole | Black | Blue | note |
|---|---|---|---|
| 1-4, 6-8, 11-14, 17 | OK | OK | page yardage = card ±1; par-3 boxes on the green |
| 5 | OK (marginal, as reviewed) | OK (marginal) | 4-wood -40 cuts the dogleg-left corner, 4-10 yds off the fairway, 20% / 31% trees |
| 9 | OK | OK | Black 378 measured vs 386 card, as reviewed |
| 10 | OK (uncertain, as reviewed) | OK | Black on the lidar pad behind the Blue box, 577 |
| 15 | uncertain (not blocking) | OK | The **calm-day** Black pick is still 4-wood -40 into the corner (51% trees / OB pattern, QA CHECK). The forecast-day play shown on the page is long iron, straight, and plausible. The reviewer flagged this as a model pick, not a geometry fix. The aim sits on the ±40 grid edge (Gustin 6 Gold does the same), which is worth a solver look. |
| **16** | **fixed** | OK | see above |
| 18 | OK | OK | 4-wood straight, fairway |

## Remaining (optional)

15 Black calm-day pick: this is a solver issue, not something a review file can fix. If you want it gone before
publishing, check the aim grid clamp at ±40 yds in the decide step. Otherwise publish as is.
