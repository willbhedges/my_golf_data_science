# Creekmoor: rebuild QA (2026-11-02)

**Verdict: NEEDS FIX** (hole 10 only). The addendum's 18 hole ways fixed the routing on 17 holes: 1, 3, 8, 9, 12, 16
and 17 are now the real holes, numbered to the card. Hole 10 was dropped from the supplement, and the router put it on
the driving range.

Page checked: `course_data/library/creekmoor/page.html`, built 2026-11-01T21:23Z. Both solved sets (Black, Green) were
run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems. I looked at every phone hole picture.
Card: golfify, Black 7406 / Green 6806, par 72. The page yardage equals the card on all 36 hole-sets, and the measured
length is within 7 yds everywhere except hole 10.

## Review fixes

| fix in review.md / review_addendum.md | applied? |
|---|---|
| Add 1 and 17 and 12 (page had 15 holes) | **yes.** 18 holes. 12 (240/187) and 17 (214/184) tees snapped 0-1 yds to the review tees, greens as given. |
| Routing from the 18 OSM hole ways in `osm_supplement.geojson` | **17 of 18.** Every hole except 10 starts on the way's tee and ends on its green. 3 is the bent N-of-subdivision hole and no longer crosses the houses. |
| 3 Black tee (way starts 34 yds short) | lidar pad at 441 = card (440). Plausible chute tee, not photo-verified. |
| 18 Black tee (line 526 vs 541) | OSM box, 534 measured / 541 card. OK. |
| **10** | **not applied.** Build warning: `ignored 2 golf=hole way(s) of a neighbouring course (outside this course's boundary): OSM 1553245446, 1553245446`. 1553245446 is the ref-10 way, and both the live OSM copy and the supplement copy were dropped. Hole 10 was then "placed by v2+structure inference" (`routing:check`). The tee is a capped walk-back among the houses (351 measured vs 482 card on both sets), and the Driver lands on the **driving range** next to the car park. |

## Holes

| hole | Black | Green | note |
|---|---|---|---|
| 1, 4-9, 11, 13, 15, 16 | OK | OK | OSM maps no fairways here, so every landing reads "fairway 0%"; the pictures show the landings on fairway |
| 2 | OK | OK | Black forecast 2-wood, calm Driver on the line |
| 3 | OK (tee uncertain) | OK | |
| **10** | **wrong hole** | **wrong hole** | driving range; see above |
| 12, 17 | **fixed** | **fixed** | par 3s, boxes on the green |
| 14 | OK (marginal) | OK | Black Driver aim 28 left into the fairway bunkers (sand 13%). Model choice |
| 18 | OK (marginal) | OK | Driver lands by the centre-line fairway bunker (sand 10%). Model choice |

## Next fix

1. **Pipeline** (`course_data/platform/sanity.py` `select_hole_ways`): the live OSM ways are now back, so OSM and the
   supplement both carry refs 1-18. The duplicate refs switch the neighbour filter on, and it drops way 1553245446
   (ref 10, `inside_course` False) in both copies. Fix: dedupe the supplement against OSM by ref (the supplement wins)
   **before** `select_hole_ways`, and never drop a supplement feature there. Alternatively, rebuild Creekmoor with
   `"ignore_osm_holes": true` (add it to `review.json` `rebuild_hint`), which takes the supplement's 18 ways as they are.
2. Rebuild, then check hole 10: tee at about (38.827625, -94.471104), green at (38.828278, -94.466313), 482 / 448.

After that rebuild: PUBLISH, provided hole 10 is the 482-yd par 4 off the supplement way.
