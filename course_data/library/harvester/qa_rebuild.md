# The Harvester Golf Club (Rhodes IA): rebuild QA (2026-11-02)

**Verdict: NEEDS FIX (wide aim on Blue 2, pipeline).** The build now completes, and all the review fixes are in
(9, 13, 14, 16). Routing, pars and tees are right. But Blue 2 prints Driver **60 yds right** with no CHECK.

Page checked: `course_data/library/harvester/page.html`, GitHub Actions run 41479479995 (committed 19:17Z). Both solved
sets (Black 7,306, Blue 6,760, par 72) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems.
I looked at every phone hole picture, and zoomed in on 1, 2 and 12.

## Review fixes

| fix (review.json / request) | applied? |
|---|---|
| 9 Black onto the line-start box, 437 | **yes.** On an OSM box, 439 measured. 4-wood +0 short of the left pond (fairway 81%) |
| 13 Black 414 | **yes.** 415 measured |
| 14 Black tee onto the back box, 180 (was walked into the rough; wrong club) | **yes.** On an OSM box, 176 measured; box on the green |
| 16 Black 500 | **yes.** 501 measured |
| 3 back tee (supplement box) | **yes.** On an OSM box, 195 / 195 |

Card: golfify plus the overrides (Black 7,306). The build still flags the golfify White 14 (195) as longer than Blue 14
(155). Blue 14 sits on an OSM box at 155 measured, so the White number is the bad one. It does not affect the solved sets.

## Checks

| check | result |
|---|---|
| Yardage | page = card on all 36 hole-sets; measured within 6 yds (Black 10: 464 / 470) |
| Mapper / native cards | not used (no `agent_layers`); `native.json` empty, as expected |
| Water filter | ran; only 29 m2 dropped. Water in the stats is the ponds (3, 9, 17, 18) and the creek through the native grass on 1 / 2 (2-5%), which the photo shows |
| Aims past ±40 | **Blue 2 Driver +60**, no CHECK |

## Holes

| hole | Black | Blue | note |
|---|---|---|---|
| 1, 3-5, 7-11, 13-17 | OK | OK | tees on OSM boxes / pads matching the card |
| 2 | OK | **wide aim, no CHECK** | 345 Blue, dog-leg right (green 96 yds right of the line). Driver +60 carries the native grass and the creek to the fairway end by the green (48 yds in, sand 13%). Plausible, but unflagged |
| 6 | OK (CHECK) | OK (CHECK) | tee_axis 5-11 yds off the boxes; 556 / 560 |
| 7, 8 | OK | OK (CHECK) | Blue texture / lidar pads matching the card (as reviewed) |
| 12 | **pick** (CHECK) | OK (CHECK) | Black Driver +17.5 lands in the fairway bunker (calm and forecast, sand 16%). The page flags it; the review called it a bad pick. Model choice |
| 13 | OK | OK (CHECK) | Blue walked back 16 yds |
| 18 | OK (CHECK) | OK (CHECK) | Black walked back 35 yds (both cards ~565); 4-wood left of the lake |

## Next fix

1. **Pipeline (blocks the publish):** wide-aim CHECK on library pages (see gustin/qa_rebuild.md). Then rebuild;
   PUBLISH if Blue 2 comes back as a CHECK.
2. Optional: hole 12 Black. The page already shows a CHECK.
