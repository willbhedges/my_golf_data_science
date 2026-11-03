# L.A. Nickell GC: rebuild QA, tee-snap fix (2026-11-03)

**Verdict: PUBLISH.** The 5 Blue regression is fixed. The tee now measures 325, which matches the card (it was 313 on
the White box). The review point is kept on purpose: "kept: snap 12 yds along OSM tee 552026435 would measure 313,
another set's box, point 325, card 325". No other hole changed, and the CHECK set is the one the last pass accepted.
One caveat does not block: the 15 White pick is Driver 39.5 left with 42% trees and no CHECK (see below).

Page checked: `course_data/library/la_nickell/page.html`, GitHub Actions run 41574368966 (built 2026-11-03T04:26Z),
with the snap fix 1d77bfeb2. I ran both solved sets (Blue 6,335 and White 5,862, par 70) through `qa_page.js`, phone
and desktop: 18 holes each, 0 page problems, no console errors. I looked at the Blue and White hole pictures for all
18 holes (montage).

## 5 Blue

| | before (run 41537321619) | now |
|---|---|---|
| tee | snapped onto the White box (38.97457, -92.37065) | review point (38.9746675, -92.370716), 12 yds behind White on the line |
| measured / card | 313 / 325 | **325 / 325** |
| pick | 2-wood -36 | Driver -39.5: lands 304 out, 33 yds short of the green across the dogleg-left corner. Fairway 26%, trees 14%, water 2% |
| CHECK | tee + yardage | tee (12 yds off an OSM box, as reviewed) + aim (lands in rough 8 yds from the fairway) |

The Driver pick is the short-par-4 "drive at the green" line, the same corner White plays (2-wood -37.5). Both CHECKs
are printed on the page.

## Holes

| hole | Blue | White | note |
|---|---|---|---|
| 3, 6, 8, 11, 14 | OK | OK | yardage = card ±3; par-3 boxes on the green |
| 1 | OK | OK (aim CHECK) | White 4-wood -6.5, 15 yds short of the fairway edge |
| 2, 4, 7, 9, 10, 12, 13, 18 | OK (tee CHECK) | OK / tee CHECK | the same tee CHECKs as before (tee_axis, walk-back, lidar/texture pad); yardage = card ±7 |
| 5 | **fixed**, 325 = card (CHECK) | OK | above |
| 10 | OK (tee CHECK) | OK (aim CHECK) | White Driver -17, 7 yds off the fairway |
| 15 | OK | caveat | White Driver 39.5 left: oval on the left edge, trees 42%, fairway 34%. It is under the ±40 rule, so there is no CHECK. Blue plays 4-wood -5 |
| 16 | OK (CHECK) | OK (CHECK) | wide aim over the corner trees: Blue Driver +40 (CHECK names +53), White 2-wood +47.5 |
| 17 | OK (CHECK) | OK (CHECK) | Blue 2-wood -40, White 4-wood -60 into the dogleg; flagged |

## Next fix

None blocking. Optional, for the solver: 15 White Driver 39.5 left with 42% trees. It is a tree-heavy pick that sits
just inside the wide-aim bound.
