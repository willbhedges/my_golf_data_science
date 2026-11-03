# Sand Hollow Championship (UT): card rebuild QA (2026-11-03)

**Verdict: PUBLISH.** The page is the Championship 18 with the GolfPass card (Black 7,315 / Blue 6,893 solved; also
White, Combo, Red). **Hole 4 is now 463** from the Black tee (was 345 from a forward OSM box). Page yardage equals the
card on all 18 for both solved sets, the pars equal the card, and routing chains 1→18.

Page checked: `course_data/library/sand_hollow/page.html`, GitHub Actions run 41604633702 (built 2026-11-03T09:04Z).
`qa_page.js` phone + desktop, Black: 18 holes, 0 problems. The Blue run had the same result (page = card 6,893). I
looked at all 18 hole pictures (montage in the QA scratch folder).

## Checks

- Split warning: "champion 18, #2 9; kept the largest group". The 9-hole Links course is dropped. The kept 18's pars
  (4 5 3 4 4 4 5 3 4 / 5 3 4 4 4 3 4 5 4) equal the card.
- Hole 4: a 463 tee walked back along the hole line (tee CHECK: 113 yds from the nearest OSM box; Blue 439 is also a
  walkback). In the photo the tee is on the grass just past the 3rd green. The measured length is 462 and the line is
  472. Driver 3.5 L, fairway 58%.
- Chains run 47-214 yds. Status "needs confirm" is for CHECKs on 4 and 18 (tee, Black) and 13 and 17 on Blue (lidar-pad
  tee 12 yds off a box; Driver -8 lands 8 yds into the rough). All are minor.

## Holes (Black; page yds = card on all 18)

| hole | par | page yds | measured | chain | pick | lie | note |
|---|---|---|---|---|---|---|---|
| 1 | 4 | 447 | 444 | - | Driver 13 R | fairway 87% |  |
| 2 | 5 | 577 | 577 | 109 | Driver 17 R | fairway 76%, sand 6% |  |
| 3 | 3 | 208 | 208 | 73 | plays 206 |  |  |
| 4 | 4 | 463 | 462 | 66 | Driver 3.5 L | fairway 58% | tee CHECK (walkback; 113 yds from the nearest OSM tee box) |
| 5 | 4 | 355 | 354 | 62 | Driver 2.5 L | fairway 79%, sand 5% |  |
| 6 | 4 | 493 | 493 | 47 | Driver 4.5 L | fairway 85%, OB 1% |  |
| 7 | 5 | 577 | 578 | 62 | Driver 10.5 R | fairway 79%, OB 1% |  |
| 8 | 3 | 162 | 162 | 97 | plays 165 |  |  |
| 9 | 4 | 433 | 434 | 214 | Driver 7.5 L | fairway 75%, sand 8% |  |
| 10 | 5 | 565 | 566 | 133 | Driver 5 R | fairway 69%, sand 7% |  |
| 11 | 3 | 190 | 190 | 96 | plays 192 |  |  |
| 12 | 4 | 443 | 442 | 160 | Driver 1.5 L | fairway 57% |  |
| 13 | 4 | 320 | 320 | 75 | Driver 5.5 L | fairway 40%, sand 4% |  |
| 14 | 4 | 525 | 525 | 65 | Driver 1 R | fairway 74% |  |
| 15 | 3 | 230 | 230 | 100 | plays 219 |  |  |
| 16 | 4 | 369 | 367 | 91 | 4-wood 6 R | fairway 58%, sand 11% |  |
| 17 | 5 | 523 | 522 | 157 | Driver 2.5 R | fairway 74%, sand 6% |  |
| 18 | 4 | 435 | 435 | 97 | Driver 13.5 R | fairway 61%, sand 10% | tee CHECK (lidar_pad; 8 yds from the nearest OSM tee box) |

No aim is past 17 yds and nothing is off the course. Nit: the title is "Sand Hollow Resort Caddie" (no
"Championship").
