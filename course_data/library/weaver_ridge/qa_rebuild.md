# WeaverRidge Golf Club: rebuild QA, mapper wave 2c (2026-11-03)

**Verdict: PUBLISH.** About 170 crown groups and OB on the house rows are in, and they look right on the pictures. The
tees are unchanged from the 2026-11-02 pass. Same caveat as before: 5 Black uses the review pin on the Gold box, 363
measured against 387 on the card. The page shows the yardage CHECK. The wide aims on 5 and 10 now carry CHECKs.

Page checked: `course_data/library/weaver_ridge/page.html`, GitHub Actions run 41554623184 (package built
2026-11-03T01:40Z). Mapper layers: `course_data/mapper/weaver_ridge/` (184 zone edits on 14 holes, 0 tees moved, 90
checked). Both solved sets (Black 6,992, Gold 6,543, par 72) were run through `qa_page.js`: 18 holes each, phone and
desktop, 0 page problems, no console errors. I looked at every phone hole picture.

## Mapper layers

| edit | on the page? |
|---|---|
| OB along the house rows on 1, 2, 3, 5, 6, 15, 16 (875-4,035 sq yds each) | yes. The houses border these holes on the pictures, and no picked landing oval carries OB |
| 11: 2,099 sq yds of OB erased (in play) | yes. 11 Driver on the line, fairway 67-68%, no OB |
| crown groups as recovery (20-414 sq yds each) on 14 holes | yes. Landing-oval trees are 1-17% and sit on real crowns at the edges |

## Tees

Measured = card ±5 on every hole-set except 5 Black (below). Two tees are shared between holes. Both are plausible
shared back-tee complexes: the two holes leave in opposite directions, and each measures exactly the card.
- 2 Black and 6 Black: OSM 749271904, 391 / 388 = card.
- 14 Black and 18 Gold: OSM 749559594, 406 / 535 = card.

Tee CHECKs printed on 1 and 13 (4-7 yds off the OSM box) are minor.

## Holes

| hole | Black | Gold | note |
|---|---|---|---|
| 1-4, 7-9, 11, 13-18 | OK | OK | par-3 boxes on the green |
| 5 | OK (caveat, CHECK) | OK (CHECK) | Black: the review pin on the Gold box (363 vs card 387); the tips are unmapped. Yardage CHECK printed. Driver +40/+41 across the lake corner to the fairway (83%, water 5%); wide-aim CHECK printed on both sets |
| 6 | OK | OK (CHECK) | Gold 4-wood -5 lands in rough 12 yds off the fairway (fairway 12%); aim CHECK printed |
| 10 | OK (CHECK) | OK (CHECK) | 2-wood / 4-wood +55 / +56 over the right tree band, fairway 35-38%. Gold oval 40% trees/water/OB. Both CHECKs printed. As reviewed: the pick sits on the widened bound |
| 12 | OK | OK | 228 / 195 play 201 / 174: the green is 97 ft below the tee (lidar), the same as the published 2026-11-02 page |

## Next fix

None blocking. When the hole 5 tips are mapped, drop the Black `tee_ll` pin.
