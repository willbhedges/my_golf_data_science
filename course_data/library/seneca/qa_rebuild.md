# Seneca Golf Course (Louisville KY): multi-course rebuild QA (2026-11-03)

**Verdict: PUBLISH.** The page is Seneca's 18 and only the 18 (the extra nine that used to be holes 1-9 is gone). The
routing chains 1→18, the golfify card matches every hole (par 72, Blue 7,110, White 6,614), and every hole is
sensible. The 6 CHECK holes are two tee-marker notes and four aims that land just off the mapped fairway; none needs a
fix (reasons below). No rebuild.

Page checked: `page.html` from GitHub Actions run 41583713847 (built 2026-11-03T05:55Z). `qa_page.js` phone + desktop:
18 holes, 0 problems, 0 console errors. Montage of all 18 hole pictures and a routing plot (scratch).

## The right 18

- Package warning: "2 courses' hole ways in one outline (by hole chains: #1 18, #2 9); kept the largest group … 18
  ways; ignored 9". Kept pars 4 4 5 3 4 4 5 3 4 / 5 4 4 3 4 5 3 4 4 = the golfify card (re-fetched today,
  `research/web/qa_mcb_cards/23.html`, same numbers). Blue lengths are within 2 yds of the card on all 18 holes.
- Routing: front nine to the north-west, back nine to the south-east. Green → next tee 47-133 yds on 14 links; 1→2
  239, 9→10 211, 11→12 187 (longer walks between the two halves). 18 green → 1 tee 96 yds.

## The 6 CHECK holes, and why

| hole | set | CHECK | verdict |
|---|---|---|---|
| 4 | Blue | tee on a lidar pad, 19 yds from the nearest OSM tee box | OK: no OSM box at the card's 217; the pad is behind the mapped boxes on the hole line, length 217 = card |
| 17 | Blue | tee 5 yds from the nearest OSM box | OK: 5 yds is a marker on the box edge (399 vs card 399) |
| 7 | Blue | Driver -40 lands 305 out, 12 yds left of the OSM fairway | OK: the photo shows the mowed fairway widening left there; fairway 20% is the OSM polygon being narrow |
| 10 | Blue | Driver +28 lands 308 out, 32 yds from fairway (fairway 1%) | Acceptable: the OSM/photo fairway ends ~260 out and the driver flies past it into open rough (trees 4%), leaving 274 on a 577 par 5. 2-wood is only +0.031. Worth a golfer's glance, not a fix |
| 6 | White | Driver +31 (tie) lands 11 yds right of the fairway | OK: tie with 4-wood; the rough there is open |
| 9 | White | Driver -11 lands 7 yds off the fairway | OK: 320-yd par 4 with a bunker right; edge of the fairway |

## Holes (Blue)

| hole | par | yds (page / card) | pick | note |
|---|---|---|---|---|
| 1 | 4 | 426 / 426 | Driver +6 | fairway 55% |
| 2 | 4 | 412 / 412 | Driver +0 (tie) | trees 8% |
| 3 | 5 | 586 / 586 | Driver -12 | sand 7%, trees 7% |
| 4 | 3 | 217 / 217 | 218 to the box | CHECK tee (above) |
| 5 | 4 | 463 / 463 | Driver -6 | sand 7% |
| 6 | 4 | 397 / 397 | Driver +19 | fairway 48% |
| 7 | 5 | 564 / 564 | Driver -40 | CHECK aim (above) |
| 8 | 3 | 149 / 149 | 148 to the box | |
| 9 | 4 | 320 / 320 | Driver -14 | OB 1% (road left) |
| 10 | 5 | 577 / 577 | Driver +28 | CHECK aim (above) |
| 11 | 4 | 390 / 390 | Driver +14 | water 3% |
| 12 | 4 | 346 / 346 | Driver +28 | dogleg; fairway 51% |
| 13 | 3 | 213 / 213 | 218 to the box | into the wind |
| 14 | 4 | 438 / 438 | Driver +5 | fairway 47% |
| 15 | 5 | 565 / 565 | Driver +7 | fairway 54% |
| 16 | 3 | 206 / 206 | 194 to the box | |
| 17 | 4 | 399 / 399 | Driver -14 | CHECK tee (above) |
| 18 | 4 | 442 / 442 | Driver +8 | fairway 59% |

No aim past ±40; nothing off the course. Not verified: whether the hole-10 fairway really ends where OSM ends it.
