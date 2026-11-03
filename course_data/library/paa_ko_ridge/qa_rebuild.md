# Paa-Ko Ridge Golf Club (Sandia Park NM): multi-course rebuild QA (2026-11-03)

**Verdict: the nines are right; NEEDS FIX (card only) — rebuild pushed.** The standard 18 is **nines 1 & 2 = OSM holes
1-9 + 10-18**, which is exactly what the rebuilt page uses (the old page's 1-9 + 19-27 was wrong). No nine fix or
request note is needed. Every hole is sensible as a no-card page, but the course has a full card on golfify, so I added
it (`card_golfify.json`, nines 1 & 2, Black 7,562) and pushed a rebuild so the page gets card tees, pars and sets.
Publish after that build is QA'd (the current page would also pass as a no-card page).

Page checked: `page.html` from GitHub Actions run 41583713847 (built 2026-11-03T05:58Z). `qa_page.js` phone + desktop:
18 holes, 0 problems, 0 console errors. Montage of all 18 hole pictures and a routing plot (scratch).

## Which two nines

- Package warning: "3 nine-hole groups (by sub-course outline: Paa-ko Ridge 10-18, 1-9, 19-27); kept the 'Paa-ko Ridge
  1-9' nine as holes 1-9 + the 'Paa-ko Ridge 10-18' nine as holes 10-18 … CHECK the nines against the card".
- Cards (web_fetch `qa_mcb_cards`, golfify): nine 1 = 4 4 5 3 5 4 4 3 4 (Black 429 394 604 183 562 327 496 265 477),
  nine 2 = 4 4 5 4 3 5 3 4 4 (416 449 541 386 272 640 228 419 474), nine 3 = 5 4 4 3 5 3 5 3 4. golfify lists the
  combinations "1 & 2" (7,562, 75.2/138), "1 & 3" and "2 & 3".
- Top 100 Golf Courses ranks "Paa-Ko Ridge (1st & 2nd)" and says "The original 18-hole course opened in 2000 with the
  additional nine added five years later" (`research/web/qa_mcb_cards/09.txt`). 1 & 2 is the standard 18.
- The page's holes 1-9 are nine 1 (pars equal; lengths 428 397 603 186 539 326 492 271 474) and 10-18 are nine 2 (pars
  equal; 417 446 536 380 266 611 224 417 462). OSM "10-18" outline = golfify nine 2.

## Routing

Green → next tee 48-145 yds on 15 links; 15→16 203, 17→18 143, 18→1 169. 9 green comes back to the 10 tee (84 yds).
No hole of the 19-27 nine is on the page.

## Holes (Back tee = OSM box nearest the line start; card Black for comparison)

| hole | par | yds (page / Black) | pick | note |
|---|---|---|---|---|
| 1 | 4 | 428 / 429 | Driver +2 | sand 12% |
| 2 | 4 | 397 / 394 | 4-wood -8 | fairway 80% |
| 3 | 5 | 603 / 604 | Driver -9 | fairway 62% |
| 4 | 3 | 186 / 183 | 210 to the box | long green (Dye-abolical) |
| 5 | 5 | 539 / **562** | Driver -10 | tee 23 yds short of the tips; trees 12% |
| 6 | 4 | 326 / 327 | Driver +6 (tie) | drivable-length par 4, sand 14% |
| 7 | 4 | 492 / 496 | Driver -10 | fairway 62% |
| 8 | 3 | 271 / 265 | 258 to the box | |
| 9 | 4 | 474 / 477 | Driver +8 | sand 8% |
| 10 | 4 | 417 / 416 | Driver -11 (tie) | water 2% |
| 11 | 4 | 446 / 449 | Driver -2 | fairway 63% |
| 12 | 5 | 536 / 541 | Driver -6 | sand 8% |
| 13 | 4 | 380 / 386 | 4-wood -14 | fairway 72% |
| 14 | 3 | 266 / 272 | 260 to the box | |
| 15 | 5 | 611 / **640** | Driver +0 | tee 29 yds short of the tips |
| 16 | 3 | 224 / 228 | 217 to the box | water left of the green |
| 17 | 4 | 417 / 419 | Driver +6 | water 2% |
| 18 | 4 | 462 / 474 | Driver -14 (tie) | trees 16% (trees on the left of the oval) |

Page total 7,475 vs Black 7,562; pars 72 = card. No aim past ±40; nothing off the course; all 18 holes carry only the
no-card CHECK.

## Fix pushed

`course_data/library/paa_ko_ridge/card_golfify.json` (golfify "1 & 2": Black / Blue / Green / Brown / Grey; the
Green/Blue combo set left out); `course_page_paa_ko_ridge.json` rev 3; batch `course_batch_qa_mcb_cards.json`. The
split already keeps 1-9 + 10-18 by default (no request names a nine), so no nine note is needed. Expect Black + Blue
solved, card matched; check 5 and 15 reach the tips boxes.
