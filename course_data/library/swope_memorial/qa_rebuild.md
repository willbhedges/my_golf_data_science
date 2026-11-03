# Swope Memorial Golf Course: rebuild QA, hole-1 Green tee fix (2026-11-03)

**Verdict: PUBLISH.** The hole 1 Green tee is now on hole 1's own line. It sits 14 yds behind the Bronze box, 19 yds
from the OSM line start, and measures 389 against the 390 card. The snap-fix rule kept the review point ("snap 14 yds
along OSM tee 284464464 would measure 374, another set's box"). Hole 6 Green is unchanged: 406 = card, on its own line
start (1 yd). The pick is Driver +1.5 straight up hole 1's fairway (fairway 56%, trees 5%).

Page checked: `course_data/library/swope_memorial/page.html`, GitHub Actions run 41579618212 (built
2026-11-03T05:12Z), with the review fix 7a98a046a. I ran both solved sets (Green 6,324 and Bronze 6,079, par 71) through
`qa_page.js`, phone and desktop: 18 holes each, 0 page problems, no console errors. I looked at every Green and Bronze
hole picture (montage).

## Holes 1 and 6

| | hole 1 Green | hole 6 Green |
|---|---|---|
| before | hole 6's box, 88 yds off hole 1's line | 406 / 406 |
| now | (39.001355, -94.516316), 14 yds behind Bronze; **389 / 390** | 406 / 406, unchanged |
| CHECK | tee (14 yds from an OSM box: the review point, by design) | none |

## Holes

| hole | Green | Bronze | note |
|---|---|---|---|
| 1 | **fixed** (tee CHECK) | OK | Green Driver +1.5; Bronze Driver -3 |
| 2 | OK (aim CHECK) | OK | 321 / 307 par 4, Driver short of the green, fairway 11-14% (as before) |
| 3, 4, 7, 10, 11, 16, 17 | OK | OK | yardage = card ±5 |
| 5 | OK (tee CHECK) | OK | 470 / 475; trees 21-23% (pre-restoration tree line) |
| 6 | OK (tie) | OK (tie) | Driver ≈ long iron, 8.5-12 right |
| 8 | OK | OK | 2-wood / 4-wood toward the greenside bunkers, sand 25-27% (as before) |
| 9 | OK (tie) | OK (tie) | 19.5 / 23.5 right |
| 12 | OK (tee CHECK) | OK | Green on a lidar pad, 527 / 533 |
| 13 | OK | OK (tee CHECK) | Bronze tee_axis 5 yds, 220 / 215 card. New CHECK, minor |
| 14, 15, 18 | OK (marginal) | OK (marginal) | aims 1.5-23.5 off the line; trees 11-24%. Model choice |

No aim is past ±40. Page yardage = the 2026 card ±6 on every hole-set.

## Next fix

None. The imagery caveat still stands (NAIP 2020/2022 predates the restoration).
