# A. L. Gustin GC: rebuild QA (2026-11-02)

**Verdict: NEEDS FIX** (one regression on hole 15 Gold; the reviewer's must-fix, hole 15 Black, is fixed)

Page checked: `course_data/library/gustin/page.html`, built 2026-11-01T20:38Z (GitHub Actions run 41346747941). Both
solved sets (Black, Gold) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems. I looked at
every phone hole picture and compared the page's per-hole yardage with the card in review.md. Note that the weather is
new (forecast for 11/7-11/8, wind 9 mph from 60°), so some club and aim picks moved for that reason alone.

## Review fixes

| fix in review.md | applied? |
|---|---|
| 15 Black: tee to the OSM back box (38.93061, -92.34709), about 399 yds | **yes.** The tee is snapped 4 yds to OSM tee 591649550, beside green 14. Page 399 / measured 396. The pick is 2-wood, aim 30 left (tie with 4-wood), and it lands in fairway. |

## New problem: hole 15 Gold

The Gold tee on 15 moved from its own box at the foot of the fairway (old build: 345 measured vs card 350, 4-wood,
fairway) back onto the Black box. The page now says **Gold 401 yds, 2 yds behind Black (399)**, and Gold total is
5,890 instead of 5,839.

Cause: `raw/scorecard_web.json` `consensus.changes` replaced Gold hole 15 = 350 (golfify **and** AllSquare agree) with
opengolfapi's 401. opengolfapi is flagged `consistent: false` and is the worst-fitting source. With hole 15 Black now
at 399, the 401 "fits the ground" and wins. The card consensus should not let one inconsistent source overrule two
agreeing ones.

## Holes

| hole | Black | Gold | note |
|---|---|---|---|
| 1 | OK | OK | 492 / 470; Driver to the fairway on both |
| 2 | OK | OK | par 3; box on the green |
| 3 | OK | OK | Black on the shared hole-6 box, 440; Gold lidar pad, 351, 4-wood +40 to the edge of the fairway (plausible) |
| 4 | OK | OK | Black tee in the chute, 5 yds off the OSM box (review: OK) |
| 5 | OK | OK | par 3, 201 / 170 |
| 6 | OK | uncertain | Gold changed from Long iron -3 (fairway) to 4-wood -40 over the dogleg corner. The calm landing centre sits on the tree clump at the corner ("recovery, 10 yds from fairway"). Weather-driven. Plausible as an aggressive line but not a clear improvement; not blocking. |
| 7 | OK (uncertain, as reviewed) | OK | Black chute tee, 364 vs 369 |
| 8 | OK | OK | |
| 9 | OK | OK | Gold Driver -14 runs to the greenside sand/path at 304 on a 323 hole; same as before, plausible |
| 10 | OK | OK | par 3 |
| 11 | OK (minor, as reviewed) | OK | Black lidar pad, moved 7 yds off a road, 416 vs 424 |
| 12 | OK | OK | |
| 13 | OK | OK | par 3 |
| 14 | OK | OK | lidar pads (OSM maps no tee boxes on 14) |
| **15** | **fixed** | **still wrong (new)** | Black: see above. Gold sits on the Black box at 401 instead of its own box at about 345 (card 350). |
| 16 | OK | OK | |
| 17 | OK | OK | |
| 18 | OK | OK | |

## Next fix

1. `course_data/library/gustin/review.json`, hole 15 `fix`: add `"tee_ll": {"Gold": [38.9303307, -92.3459911]}`. This
   is the OSM tee box at the foot of the fairway, 341 yds along the dogleg (332 straight). Also add `"yards": {"Gold":
   350}` next to the existing Black entries. Then rebuild (coordinator: course_page_gustin request).
2. (Pipeline, optional but better) the card consensus in `course_data/platform/package.py` (card_consensus) should
   not replace a yardage on which two consistent sources agree with the value from a source flagged
   `consistent: false`.

After that rebuild: PUBLISH, provided Gold 15 reads about 350 from the forward box.
