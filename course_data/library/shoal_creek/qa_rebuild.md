# Shoal Creek GC (Kansas City MO): rebuild QA, tee-snap fix (2026-11-03)

**Verdict: PUBLISH.** The tee-snap fix (1d77bfeb2) restores the off-page sets: Black 5 is 128 against the 130 card
(it was 139), and White 6 is 308 against 306 (it was 320). Both are kept as review points. Gold 4 is still on the
right box: 422 against the 418 card, "review (inside OSM tee 897736290)", with 4-wood -2 straight up the fairway. Nothing
else moved. This rebuild is the same course as the published page ME9qwJtZ3Kp9M8Payhtgft, and it is fine to replace it.

Page checked: `course_data/library/shoal_creek/page.html`, GitHub Actions run 41574368966 (built 2026-11-03T04:31Z).
I ran both solved sets (Gold 6,983 and Blue 6,363, par 71) through `qa_page.js`, phone and desktop: 18 holes each, 0
page problems, no console errors. I looked at every Gold and Blue hole picture (montage).

## Tee-snap holes (package `tees`)

| hole | set | measured / card | method |
|---|---|---|---|
| 4 | Gold | 422 / 418 | review, inside OSM tee 897736290 |
| 5 | Gold / Blue / White / Black | 233/234, 178/179, 146/147, **128/130** | review; Black kept (snap would give 139) |
| 6 | Gold / Blue / White / Black | 366/364, 335/333, **308/306**, 283/281 | review; White kept (snap would give 320) |

## Holes

| hole | Gold | Blue | note |
|---|---|---|---|
| 1, 3, 5, 7-11, 13-18 | OK | OK | yardage = card ±3 |
| 2 | OK (tee CHECK) | OK (tee CHECK) | Gold walk-back 32 yds, Blue tee_axis 3 yds; yardage = card ±4. The only CHECK hole |
| 4 | OK | OK | Gold 4-wood -2 (fairway 80%); Blue 4-wood +8.5 |
| 6 | OK | OK (marginal) | Blue Driver 33.5 left into the dogleg-left corner, fairway 31%, 52 yds in |
| 12 | OK | OK (marginal) | Blue 4-wood short of the pond, fairway 24%, trees 15% (as before) |

No aim is past ±40. Every landing oval is inside the picture.

## Next fix

None.
