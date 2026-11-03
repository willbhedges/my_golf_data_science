# Grand National Links Course (RTJ Trail, Opelika AL): multi-course rebuild QA (2026-11-03)

**Verdict: NEEDS FIX (card) — rebuild pushed. The publish gate no longer blocks it.** The page is now a clean Links 18:
the Lake 18 and the 17 unnumbered Short Course ways are gone, the routing chains 1→18, and the pars equal the Links
card 18/18. The status is "needs confirm", not "blocked" (18 holes with no card passes the gate; `course_page.py
regate` lists nothing for it). What is still wrong is two tees with no card to place them: hole 1 is 367 on the page
vs 423 on the card, hole 13 is 476 vs 418, and on both the tee-shot pick is poor (1: aim -51 into the tree corner; 13:
Driver -37 into the rough left, fairway 5%). I found a Links card (golfingrecord, Purple 7,311, every set sums) and
added it as `card_review.json`; rebuild pushed. Publish after that build is QA'd.

Page checked: `page.html` from GitHub Actions run 41583713847 (built 2026-11-03T06:20Z). `qa_page.js` phone + desktop:
18 holes, 0 problems, 0 console errors. Montage of all 18 hole pictures and a routing plot (scratch).

## Links, not Lake, and no Short Course

- Package warning: "2 courses' hole ways in one outline (by hole chains: lake 18, #2 18); kept the course nearest the
  request's near point (1848 yds vs 3421), 18 ways; ignored 18 + 17 unnumbered golf=hole way(s)".
- The kept 18 is Links: its 15th is a par 5 (510) and 16th a par 3 (181). The dropped chain has the Lake's signature
  par-3 15th over water (OSM 1098809331, 203 yds). Kept pars 4 5 3 4 4 5 4 4 3 / 4 3 5 4 4 5 3 4 4 = the Links card on
  every hole; 12 = 575 and 16 = 181 equal the card exactly.
- The AllSquare "Grand National Golf Course" card fetched with it is the **Lake** (par 3 on 3, 8, 15, 17), so it was
  right that no card matched Links before.
- Routing: green → next tee 50-253 yds (longest 1→2 304, 11→12 253, 8→9 226, 16→17 214: Links has long cart rides
  between holes on the lake shore). 18 green → 1 tee 138. All 18 lines inside the Links area; none on Lake or Short.

## Holes (Back tee = OSM box nearest each line start; card Purple for comparison)

| hole | par | yds (page / Purple) | pick | note |
|---|---|---|---|---|
| 1 | 4 | **367 / 423** | Driver -40 (tie with 2-wood) | **wide-aim CHECK**: -51 calm, lands at the dogleg's tree corner (photo heavier than trees 7%). The card tee is ~56 yds farther back, which changes the play |
| 2 | 5 | 556 / 556 | Driver -6 | trees in the oval left/right (7%) |
| 3 | 3 | 201 / 206 | 191 to the box | |
| 4 | 4 | 444 / 425 | Driver -33 | lands left near the creek/native, fairway 45% |
| 5 | 4 | 451 / 456 | Driver +38 | aim right, trees 10%; plausible dogleg |
| 6 | 5 | 556 / 544 | Driver -3 | fairway 65% |
| 7 | 4 | 468 / 472 | Driver -10 | sand 21% (fairway bunkers left of the landing) |
| 8 | 4 | 347 / 345 | 4-wood -1 | fairway 31%, sand 8% |
| 9 | 3 | 206 / 204 | 198 to the box | |
| 10 | 4 | 338 / 363 | 4-wood -40 (Driver calm) | trees 14% left; 25 yds short of the card |
| 11 | 3 | 256 / 260 | 269 to the box (into the wind) | |
| 12 | 5 | 575 / 575 | Driver +16 | sand 23% |
| 13 | 4 | **476 / 418** | Driver -37 | **CHECK**: lands in the rough/native left, fairway 5%; the page tee is ~58 yds behind the card's |
| 14 | 4 | 473 / 467 | Driver -8 | fairway 63% |
| 15 | 5 | 510 / 516 | Driver -4 | fairway 61% |
| 16 | 3 | 181 / 181 | 175 to the box | |
| 17 | 4 | 426 / 429 | 2-wood (Driver -7 tie calm) | sand 6% |
| 18 | 4 | 472 / 471 | Driver -2 | lake left, water 2% |

Totals: page 7,303 (par 72) vs Purple 7,311; holes 1 and 13 cancel. All 18 carry the no-card yardage/par CHECK.

## Fix pushed

`course_data/library/grand_national_links/card_review.json` (Links: Purple 7,311 / Orange 6,574 / White 6,015 / Teal
4,843, men's ratings; from https://www.golfingrecord.com/golf-scorecard/64c8ad62-1d33-63a5-9a9e-da290ba768a4 via web_fetch
`qa_mcb_cards2`); `course_page_grand_national_links.json` rev 3; batch `course_batch_qa_mcb_cards.json`. Expect Purple
as the solved set with tees on 1 and 13 moved to the card lengths. Not verified: GolfPass lists Purple at 7,404 (a
different tee version); the golfingrecord card is the only per-hole Links card found.
