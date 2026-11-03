# Buffalo Ridge Springs: rebuild QA, wide-aim pass (2026-11-03)

**Verdict: PUBLISH.** Hole 15 is present, on its own OSM line. Earlier builds dropped that way with the neighbouring
course's ways (10 ignored then, 9 now) and drew a 2-point straight guess. This build uses the 3-point OSM way: tee
boxes, carry over the pond, fairway, then a bend right to the green. Buffalo 365 / 366, Gold 347 / 348. The imagery
agrees.

Page checked: `course_data/library/buffalo_ridge/page.html`, GitHub Actions run 41537321619 (committed 2026-11-03
01:33Z). I ran both solved sets (Buffalo, Gold) through `qa_page.js`, phone and desktop: 18 holes each, 0 page
problems, no console errors. I looked at the Buffalo 1-9 and Gold 10-18 phone pictures and the Buffalo 15 desktop
picture, and checked every landing oval against the picture edge on both sets.

## Checks

| check | result |
|---|---|
| Hole 15 | own line (`hole_line_ll` 3 points, `tees:tee_centroid`). 4-wood +11 / +20 over the pond to the fairway, fairway 60-80%, water 3% |
| Card / pars | page yardage = card on all 36 hole-sets; measured within 6 yds |
| Wide-aim CHECK | Gold 10 (2-wood 54.5 left at the dogleg; oval inside the picture) |
| Ovals | all picks inside. The Driver row on 10 (both sets) goes 1-6 px off |
| Native check cards (Buffalo) | 18 (Driver -8) and 13 (Driver -19) = page |
| Mapper layers | applied; on 15 the water / native / OB erases are small and the landing still reads the real pond |

## Holes

| hole | Buffalo | Gold | note |
|---|---|---|---|
| 2-9, 11-14, 17, 18 | OK | OK | 3 Gold review fix still in (agent, 381 / 385) |
| 1 | OK (tee CHECK) | OK | tee_axis 4 yds |
| 10 | OK | OK (CHECK) | Gold 2-wood -54.5, fairway 53% |
| 15 | **fixed** | **fixed** | own line, as above |
| 16 | OK | OK (tee CHECK) | Gold walked back 31 yds, 379 = card (as reviewed) |

## Next fix

None.
