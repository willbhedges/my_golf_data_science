# Shoal Creek GC (Kansas City MO): rebuild QA, wide-aim pass (2026-11-03)

**Verdict: PUBLISH.** The hole-4 Gold tee is fixed. Gold 4 is now on the OSM box at the top of the hole line, at
422 measured against the 418 card ("review, inside OSM tee"). The line runs straight up the fairway, not through the
woods, and the pick is 4-wood 2 left (fairway 80%). The routing of 5 and 6 still holds.

Page checked: `course_data/library/shoal_creek/page.html`, GitHub Actions run 41537321619 (committed 2026-11-03
01:25Z). I ran both solved sets (Gold, Blue) through `qa_page.js`, phone and desktop: 18 holes each, 0 page problems,
no console errors. I looked at every Gold phone hole picture, and checked every landing oval against the picture edge
on both sets.

## Checks

| check | result |
|---|---|
| Card / pars | page yardage = card on all 36 hole-sets; measured within 4 yds |
| Wide-aim CHECK | none needed: no aim past ±40 |
| Ovals | 0 outside, picks or club rows |
| Native check cards | none asked (no agent layers) |

## Holes

| hole | Gold | Blue | note |
|---|---|---|---|
| 1, 3, 5-11, 13-18 | OK | OK | |
| 2 | OK (tee CHECK) | OK (tee CHECK) | Gold walked back 23 yds, Blue tee_axis 3 yds; yardage = card ±4 |
| 4 | **fixed** | OK | Gold 422 / 418 from the OSM box at the line's start; 4-wood -2 |
| 12 | OK | OK (marginal) | Blue 4-wood to short of the pond, fairway 24%, trees 15%. Model choice, as before |

## Next fix

None. Off-page, the same review-snap bug as la_nickell 5 Blue (see that file) moved Black 5 by 11 yds (139 / 130) and
White 6 by 12 yds (320 / 306). Neither set is on the page.
