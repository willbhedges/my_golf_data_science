# TPC Sawgrass Stadium (FL): card rebuild QA (2026-11-03)

**Verdict: PUBLISH.** The Stadium card fixed the page. The holes play in OSM order 1→18 with no renumbering, and the
17th is the island green at 141 (plays 142). The card is the Stadium card (The Players 7,352, par 72), and page
yardage equals the card on all 18. The routing gate passes, with no walk from a green to the next tee over 350 yds.

Page checked: `course_data/library/tpc_sawgrass/page.html`, GitHub Actions run 41604633702 (built 2026-11-03T09:28Z).
I ran `qa_page.js` on phone + desktop for The Players (18 holes, 0 problems) and on phone + desktop for Blue (18 holes,
0 problems; page = card 6,670 on all 18). I looked at all 18 hole pictures (montage in the QA scratch folder).

## What changed since the last pass

- Card source: `card_review.json` (GolfPass Stadium). The tee sets are The Players 7,352 / Blue 6,670 (both solved)
  plus Blue/White, White, White/Green and Green. The OpenGolfAPI Valley card is gone.
- No "OSM hole numbering differs" warning. The only package warning is the multi-course split ("stadium 18, valley
  18; kept 'stadium'").
- 17 is the island green at 141. 18 is a par 4 of 462 with water left: 4-wood 12 R, water 6%. Hole 1 is a par 4 of
  424 and 9 is a par 5 of 601.
- Chains (green n → tee n+1) run 56-203 yds, except 9→10 at 350 (back past the clubhouse). `course_page.py regate`
  blocks nothing.
- Status is "needs confirm" for 4 tee CHECKs (2, 6, 9, 12). On each, the tee is a lidar pad or walkback 20-29 yds
  from the nearest OSM box, put there to reach the card yardage. All four sit on tee ground in the photo.

## Holes (The Players; page yds = card on all 18)

| hole | par | page yds | measured | chain | pick | lie | note |
|---|---|---|---|---|---|---|---|
| 1 | 4 | 424 | 423 | - | Driver 13 R | fairway 43%, sand 11%, trees 10% |  |
| 2 | 5 | 555 | 553 | 100 | Driver 2 L | fairway 40%, trees 22% | tee CHECK (lidar_pad; 29 yds from the nearest OSM tee box) |
| 3 | 3 | 182 | 182 | 67 | plays 185 |  |  |
| 4 | 4 | 387 | 386 | 108 | Driver 7 R | fairway 36%, sand 11% |  |
| 5 | 4 | 469 | 469 | 140 | Driver 13 L | fairway 43%, sand 12%, trees 2%, water 3% |  |
| 6 | 4 | 413 | 413 | 70 | 4-wood 1 L | fairway 61%, sand 19%, trees 12%, water 1% | tee CHECK (walkback; 20 yds from the nearest OSM tee box) |
| 7 | 4 | 450 | 450 | 95 | Driver 10 R | fairway 51%, sand 14%, trees 3%, water 5% |  |
| 8 | 3 | 236 | 236 | 108 | plays 235 |  |  |
| 9 | 5 | 601 | 595 | 69 | Driver 11 R | fairway 73%, sand 2%, trees 4%, water 4% | tee CHECK (lidar_pad; 24 yds from the nearest OSM tee box) |
| 10 | 4 | 419 | 419 | 350 | 4-wood 0.5 L | fairway 73%, sand 9%, trees 5% |  |
| 11 | 5 | 573 | 571 | 176 | Driver 4 L | fairway 66%, sand 1%, trees 10% |  |
| 12 | 4 | 365 | 364 | 120 | 4-wood 8 L | fairway 45%, sand 19%, trees 11%, water 3% | tee CHECK (lidar_pad; 21 yds from the nearest OSM tee box) |
| 13 | 3 | 183 | 182 | 203 | plays 181 |  |  |
| 14 | 4 | 485 | 483 | 56 | Driver 6.5 R | fairway 57%, sand 4%, water 3% |  |
| 15 | 4 | 470 | 469 | 113 | Driver 0.5 L | fairway 53%, sand 19%, trees 10% |  |
| 16 | 5 | 537 | 531 | 147 | Driver 0.5 L | fairway 57%, sand 2%, trees 12% |  |
| 17 | 3 | 141 | 141 | 104 | plays 142 |  |  |
| 18 | 4 | 462 | 461 | 94 | 4-wood 12 R | fairway 66%, water 6% |  |

No aim is wider than 13 yds and nothing is off the course. The picks follow the photos: 18 aims away from the lake
and 5 avoids the water right. Nit: the title is still "TPC Sawgrass Caddie" (it does not name the Stadium).
