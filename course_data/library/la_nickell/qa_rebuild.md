# L.A. Nickell GC: rebuild QA, wide-aim pass (2026-11-03)

**Verdict: NEEDS FIX (5 Blue tee, pipeline regression; minor).** The 12 CHECKs are mostly old tee CHECKs. Two are new
wide-aim CHECKs (16, 17), which are justified. But the 5 Blue review fix that the 2026-11-01 pass confirmed (325
measured) is undone. Since the review-snap change, the Blue point is pulled onto the White box, so Blue 5 plays from
313 while the card says 325.

Page checked: `course_data/library/la_nickell/page.html`, GitHub Actions run 41537321619 (committed 2026-11-03 01:17Z).
I ran both solved sets (Blue, White) through `qa_page.js`, phone and desktop: 18 holes each, 0 page problems, no
console errors. I looked at the Blue 1-18 and White 10-18 phone pictures, and checked every landing oval against the
picture edge on both sets.

## Why 12 CHECKs (Blue: 2, 4, 5, 7, 9, 10, 12, 13, 16, 17, 18; White adds 1)

| cause | holes | justified? |
|---|---|---|
| tee off an OSM box: tee_axis 4-12 yds (Blue 2, 7, 17; White 7, 9), walk-back 24-46 yds (Blue 9, 10, 12, 18), texture / lidar pad (Blue 4, 13) | 2, 4, 7, 9, 10, 12, 13, 17, 18 | yes, the same set the last pass accepted. Yardage = card on each |
| yardage: Blue 5 measured 313 / card 325 | 5 | **yes: a real regression**, see below |
| wide aim | 16 (Blue 2-wood +40 pick, Driver row +63; White 2-wood +48), 17 (Blue 2-wood -40, 4-wood row -57; White 4-wood -60) | yes: dogleg corners over trees. 16 / 17 sat on the ±40 clamp before; now they are free and flagged |
| aim: lands in rough 7-15 yds from fairway | White 1, White 10 | marginal, edge-of-fairway landings |

The wide-aim rule is not over-firing on the pick. It does fire on non-picked club rows (Blue 16 / 17), which the
CHECK text names.

## The 5 Blue regression

`review.json` hole 5: `fix.tee_ll.Blue = [38.9746675, -92.370716]`, about 12 yds behind White ("not visible in the
page imagery"). The package now has `method: "review (snapped 12 yds along OSM tee 552026435)"` at (38.9745739,
-92.3706457). That is 3 m from the White tee (38.9745716, -92.3706834), so both measure 313. `snap_to_tee_box` in
`course_data/platform/package.py` (commit d5eff82c8, 2026-11-02 10:08Z) moves any review point within
OVERRIDE_SNAP_YD of a box onto that box. It does this even when the reviewer put the point off the box on purpose to
match the card. Every build since 14:36Z on 11-02 has 313. The same snap hits shoal_creek Black 5 (139 / 130) and
White 6 (320 / 306); those sets are not on that page.

## Ovals

White 15 Driver 40 left clips the left edge by 1-7 px (forecast and calm; the aim is on the ±40 bound, so the picture
was not widened). Taps on non-picked rows go further off: Blue 17 Driver row 35-44 px, White 5 / 17 Driver row 7-14
px, Blue 5 calm Driver 7 px. The wide-aim picks themselves (16, 17 both sets) are inside.

## Holes

| hole | Blue | White | note |
|---|---|---|---|
| 3, 6, 8, 11, 14 | OK | OK | |
| 1 | OK | OK (aim CHECK) | White 4-wood -6, 15 yds short of the fairway edge |
| 2, 4, 7, 9, 12, 13, 18 | OK (tee CHECK) | OK / tee CHECK | as reviewed; yardage = card |
| 5 | **tee regressed** (313 / 325) | OK | 2-wood -36 from White's spot |
| 10 | OK (tee CHECK) | OK (aim CHECK) | White Driver -17, 7 yds off the fairway |
| 15 | OK | OK (oval clips 2 yds) | Driver 33-40 left toward the left trees |
| 16 | OK (CHECK) | OK (CHECK) | 2-wood +40 / +48 over the tree clump at the corner |
| 17 | OK (CHECK) | OK (CHECK) | 2-wood -40 / 4-wood -60 into the dogleg, flagged |

## Next fix

1. **Pipeline:** `snap_to_tee_box` should keep a review point when snapping takes the measured length further from
   the card yardage the same review gives (here `yards: 325`). Or it should not snap a point that is behind every box
   on the line. Then rebuild. The page is otherwise publishable; accepting 12 yds on Blue 5 is the coordinator's call.
2. Optional: widen the picture for aims on the ±40 bound (White 15).
