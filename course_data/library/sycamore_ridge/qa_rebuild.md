# Sycamore Ridge GC (Spring Hill KS): rebuild QA, wide-aim pass (2026-11-03)

**Verdict: PUBLISH.** Hole 18 (Driver 58 yds right on both sets) now carries the wide-aim CHECK. The wider hole
picture shows the whole landing area: the oval sits on the right side of the dogleg fairway, inside the frame. The
hole 1 tee fix still holds.

Page checked: `course_data/library/sycamore_ridge/page.html`, GitHub Actions run 41537321619 (committed 2026-11-03
01:29Z). I ran both solved sets (Black, Blue) through `qa_page.js`, phone and desktop: 18 holes each, 0 page
problems, no console errors. I looked at every phone hole picture and checked every landing oval against the picture
edge.

## Checks

| check | result |
|---|---|
| Card / pars | page yardage = card on all 36 hole-sets; measured within 8 yds (Blue 9: 408 / 416, tagged box) |
| Wide-aim CHECK | 18 Black and Blue (Driver +58; the CHECK text quotes the Driver row at +70 / +72). Blue 5 also gets one: pick Driver -32.5, Driver row -44 |
| Ovals | all picks inside, except Blue 2 calm Driver 40 left, which clips the left edge by 9 px (about 3 yds). That aim is on the ±40 bound, so the picture was not widened |
| Native check cards | none asked (no agent layers) |

## Holes

| hole | Black | Blue | note |
|---|---|---|---|
| 1 | OK | OK | 468 / 467 and 444 / 445, OSM boxes at the top of the line |
| 2-4, 6-8, 10-12, 14-17 | OK | OK | |
| 5 | OK | OK (CHECK) | Blue Driver 32.5 left; CHECK for the -44 row |
| 9, 13 | OK | OK (tee CHECK) | tagged box 3 yds / tee_axis 7 yds |
| 18 | **fixed** (CHECK) | **fixed** (CHECK) | Driver 58 right cuts the dogleg onto the fairway beyond the trees, fairway 58-59%, water 1% |

## Next fix

None. Optional, pipeline: widen the picture for aims on the ±40 bound too (Blue 2, 3 yds clipped).
