# Pevely Farms: rebuild QA, mapper wave 2b (2026-11-03)

**Verdict: PUBLISH.** Holes 1, 9, 10 and 18 are Pevely's own holes, and their tees measure at the card. The
neighbouring course's ways are still dropped (`ignored 5 golf=hole way(s) of a neighbouring course: OSM 881746238,
884242539, 884242547, 884242548, 884242556`). The mapper layers are in: native on 2 and 3, recovery adds on 4 and 15,
and the OB / water erases on 9 and 12. Hole 16 still has the pick on the +40 bound, as before.

Page checked: `course_data/library/pevely_farms/page.html`, GitHub Actions run 41539963949 (built 2026-11-02T23:42Z),
mapper layers `course_data/mapper/pevely_farms/` (11 zone edits on 7 holes, 0 tees moved). Both solved sets (Black
7,032, Blue 6,704, par 72) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems, no
console errors. I looked at every phone hole picture and drew the package zones, tees and lines on 1, 3, 9, 10, 16
and 18.

## Tees on 1, 9, 10, 18 (the old neighbouring-course bug)

| hole | OSM hcp (card) | Black measured / card | Blue measured / card | tee |
|---|---|---|---|---|
| 1 | 16 | 445 / 446 | 424 / 425 | OSM box (tee_centroid) at the start of Pevely's way 848080943 |
| 9 | 4 | 526 / 527 | 505 / 506 | OSM box |
| 10 | 13 | 404 / 403 | 385 / 384 | OSM box |
| 18 | 3 | 468 / 468 | 448 / 453 | Black walk-back 24 yds behind the box (CHECK); Blue tee_axis 4 yds off the box (CHECK) |

All four holes have their own OSM green, fairway and hole line inside the Pevely boundary. The overlay shows the tee
dots on the hole's own boxes, and the line runs up its own fairway.

## Holes

| hole | Black | Blue | note |
|---|---|---|---|
| 1, 2, 4-10, 12, 14, 15, 17 | OK | OK | yardage = card ±5; 2 native left (Driver -14.5, 1% long grass) |
| 3 | OK (CHECK) | OK (CHECK) | 277 / 250 par 4. Black on a lidar pad 28 yds behind the box; Blue 4-wood +8 just off the fairway. Native right is drawn |
| 11 | OK (CHECK) | OK | Black walk-back 24 yds under the canopy (as reviewed), 400 / 401 |
| 13 | OK | OK (CHECK) | Blue 4-wood -13 lands 10 yds off the fairway, 18% trees |
| 16 | pick on the bound | pick on the bound | 2-wood +40.0, fairway 3-4%, lands 23 yds right of the fairway at the dogleg. CHECK printed. Same as the previous pass |
| 18 | OK (CHECK) | OK (CHECK) | tee CHECKs only, see above |

## Next fix

None blocking. Solver: 16 is still clamped at the ±40 aim bound.
