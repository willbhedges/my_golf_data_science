# The Harvester GC (Rhodes IA): rebuild QA, wide-aim pass (2026-11-03)

**Verdict: PUBLISH.** Blue 2 (2-wood / Driver 60 yds right on the 345 dogleg) now carries the wide-aim CHECK. The
picture shows the line over the native grass and creek to the fairway end by the green, with the oval inside the
frame. Everything else is as in the last pass.

Page checked: `course_data/library/harvester/page.html`, GitHub Actions run 41537321619 (committed 2026-11-03 01:21Z).
I ran both solved sets (Black, Blue) through `qa_page.js`, phone and desktop: 18 holes each, 0 page problems, no
console errors. I looked at every phone hole picture and checked every landing oval against the picture edge.

## Checks

| check | result |
|---|---|
| Card / pars | page yardage = card on all 36 hole-sets; measured within 6 yds |
| Wide-aim CHECK | Blue 2 (2-wood +60, Driver row +60) and Black 2 (pick Driver +2 forecast / 4-wood calm; the CHECK is for the Driver row +53) |
| Ovals | every pick inside the picture. Only the Driver row on 9 (both sets) goes outside, by 2-13 px |
| Native check cards | none asked |

## Holes

| hole | Black | Blue | note |
|---|---|---|---|
| 1, 3-5, 9-11, 14-17 | OK | OK | |
| 2 | OK (CHECK) | **fixed** (CHECK) | Blue 60 right over the creek / native to the fairway by the green, 48 yds in, sand 13% |
| 6 | OK (tee CHECK) | OK (tee CHECK) | tee_axis 5-11 yds off the boxes |
| 7, 8 | OK | OK (tee CHECK) | texture / lidar pads at card length |
| 12 | pick (aim CHECK) | OK (tee CHECK) | Black Driver +17.5 at the fairway bunker (sand 16%), flagged. Model choice |
| 13 | OK | OK (tee CHECK) | Blue walked back 16 yds |
| 18 | OK (tee CHECK) | OK (tee CHECK) | Black walked back 35 yds; 4-wood / long iron left of the lake |

## Next fix

None.
