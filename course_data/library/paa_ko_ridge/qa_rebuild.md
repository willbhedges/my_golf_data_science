# Paa-Ko Ridge (NM): card rebuild QA (2026-11-03)

**Verdict: PUBLISH.** The page is nines 1-9 + 10-18 with the golfify "1 & 2" card (Black 7,562 / Blue 7,195 solved;
also Green, Brown, Grey). Page yardage equals the card on all 18 for both solved sets, and the pars equal the card.
**Holes 5 and 15 reach the back boxes**: 5 is 562 (measured 557) and 15 is 640 (measured 639; the box sits 24 yds
behind the OSM line start).

Page checked: `course_data/library/paa_ko_ridge/page.html`, GitHub Actions run 41605206913 (built 2026-11-03T09:10Z).
`qa_page.js` phone + desktop, Black: 18 holes, 0 problems. The Blue run had the same result (page = card 7,195). I
looked at all 18 hole pictures (montage in the QA scratch folder).

## Checks

- Split warning: "3 nine-hole groups ... kept 'Paa-ko Ridge 1-9' as 1-9 + 'Paa-ko Ridge 10-18' as 10-18; ignored 9"
  (the 19-27 nine). That matches the card's "1 & 2".
- Chains run 48-147 yds, except 15→16 at 208. Every measured length is within 5 yds of Black.
- The one CHECK is hole 18: the tee is 3 yds off an OSM box (trivial).

## Holes (Black; page yds = card on all 18)

| hole | par | page yds | measured | chain | pick | lie | note |
|---|---|---|---|---|---|---|---|
| 1 | 4 | 429 | 430 | - | Driver 3 R | fairway 43%, sand 12%, OB 1% |  |
| 2 | 4 | 394 | 395 | 147 | 4-wood 9 L | fairway 79%, sand 3% |  |
| 3 | 5 | 604 | 604 | 114 | Driver 9 L | fairway 63%, sand 4% |  |
| 4 | 3 | 183 | 183 | 89 | plays 207 |  |  |
| 5 | 5 | 562 | 557 | 125 | Driver 13.5 L | fairway 40%, trees 5% |  |
| 6 | 4 | 327 | 327 | 55 | Driver 6 R | fairway 31%, sand 13%, trees 4% |  |
| 7 | 4 | 496 | 496 | 145 | Driver 7 L | fairway 59%, trees 6% |  |
| 8 | 3 | 265 | 267 | 70 | plays 252 |  |  |
| 9 | 4 | 477 | 478 | 48 | Driver 7.5 R | fairway 63%, sand 6% |  |
| 10 | 4 | 416 | 417 | 85 | Driver 11 L | fairway 57%, trees 3%, water 2% |  |
| 11 | 4 | 449 | 449 | 59 | Driver 2 L | fairway 64%, sand 3%, trees 2% |  |
| 12 | 5 | 541 | 541 | 85 | Driver 6.5 L | fairway 55%, sand 6%, trees 5% |  |
| 13 | 4 | 386 | 385 | 114 | 4-wood 13 L | fairway 76% |  |
| 14 | 3 | 272 | 272 | 79 | plays 266 |  |  |
| 15 | 5 | 640 | 639 | 104 | Driver 9 L | fairway 61%, trees 3% |  |
| 16 | 3 | 228 | 228 | 208 | plays 220 |  |  |
| 17 | 4 | 419 | 420 | 121 | Driver 6.5 R | fairway 55%, sand 7%, trees 1%, water 3% |  |
| 18 | 4 | 474 | 470 | 136 | Driver 9.5 L | fairway 37%, sand 4%, trees 14%, water 2% | tee CHECK (tee_axis; 3 yds from the nearest OSM tee box) |

No aim is past 13.5 yds and nothing is off the course. Hole 4 plays 207 for 183. The elevation is 0 and there is a light wind, so this is not a yardage
error. The target box sits in the back half of a long, narrow green (the page reads "water short, safe miss is long").
