# Grand National Links (RTJ Trail, Opelika AL): card rebuild QA (2026-11-03)

**Verdict: PUBLISH (Purple), with the CHECKs below.** The Links card (golfingrecord, `card_review.json`) is matched:
Purple 7,311 / Orange 6,574 solved, plus White and Teal. Page yardage equals the card on all 18 for both solved sets,
and the pars equal the card. The tees on **hole 1 (423)** and **hole 13 (418)** are fixed: hole 1 has a walkback tee
42 yds behind the nearest OSM box (measured 423), and hole 13 has a tee on the hole line 52 yds up from the line start
(measured 423). **The gate passes**: status "needs confirm", not blocked. `course_page.py regate` blocks nothing, and
the longest green → next-tee walk is 305 yds (1→2; Links has long cart rides along the lake). No other walk is over
253.

Page checked: `course_data/library/grand_national_links/page.html`, GitHub Actions run 41605206913 (built
2026-11-03T09:19Z). `qa_page.js` phone + desktop, Purple: 18 holes, 0 problems. The Orange run had the same result
(page = card 6,574). I looked at all 18 Purple hole pictures, plus Orange 2, 4, 5, 10 and 13 close up (montage and
crops in the QA scratch folder).

## Hole 1 and hole 13

- **1** (Purple 423): Driver 10 L, fairway 46%, trees 9%. The pick is no longer the -51 aim into the tree corner. The
  tee is on grass at the edge of the trees (tee CHECK, walkback).
- **13** (Purple 418): 4-wood 40 L (a tie with 2-wood). It lands 270 out in what the map calls rough, 38 yds from the
  fairway, with fairway 1% (CHECKed). The hole is a dogleg (the OSM line bends at ~245 yds from this tee). OSM maps
  only a small fairway blob short of the corner. In the photo the landing spot is open light grass inside the corner,
  not trees, so the cut is plausible but rests on unmapped fairway. The aim sits at the 40-yd search bound. Orange 13
  does the same at -52 (long iron, fairway 0%, CHECKed). Left as a CHECK for the golfer, not a blocker.

## Orange set: wide aims (CHECKed on the page)

- Orange 2 (par 5, 509): Driver 60 L over the dogleg corner. Trees 22%, and the landing oval sits partly on a tree
  clump in the photo (CHECK wide_aim). This is the weakest plan on the page. Purple 2 plays Driver 6 L down the
  fairway.
- Orange 5 (375): 4-wood 49.5 R into the dogleg (CHECK wide_aim), fairway 62%, trees 13%. Plausible.
- Orange 10 (326): Driver 40 L to 31 yds in, trees 16%, at the bound, not flagged. Orange 4: 2-wood 40 L, fairway
  55%. Both cut a dogleg.

The Orange aims are flagged and do not affect the default (Purple) set. If someone wants them gone, the fix is a
planner or wide-aim change, not a card or tee fix, so nothing was pushed for them.

## Holes (Purple; page yds = card on all 18)

| hole | par | page yds | measured | chain | pick | lie | note |
|---|---|---|---|---|---|---|---|
| 1 | 4 | 423 | 423 | - | Driver 10 L | fairway 46%, trees 9% | tee CHECK (walkback; 42 yds from the nearest OSM tee box) |
| 2 | 5 | 556 | 555 | 305 | Driver 6 L | fairway 40%, trees 7% |  |
| 3 | 3 | 206 | 206 | 169 | plays 202 |  |  |
| 4 | 4 | 425 | 424 | 252 | Driver 32 L | fairway 55% |  |
| 5 | 4 | 456 | 455 | 132 | Driver 31 R | fairway 49%, sand 3%, trees 12% |  |
| 6 | 5 | 544 | 545 | 57 | Driver 2.5 R | fairway 64%, trees 9%, water 1% |  |
| 7 | 4 | 472 | 473 | 88 | Driver 10 L | fairway 43%, sand 17%, trees 5% |  |
| 8 | 4 | 345 | 345 | 115 | Long iron 3 L | fairway 86%, sand 2% |  |
| 9 | 3 | 204 | 204 | 226 | plays 196 |  |  |
| 10 | 4 | 363 | 362 | 76 | 2-wood 31 L | fairway 73%, trees 3% | tee CHECK (tee_axis; 8 yds from the nearest OSM tee box) |
| 11 | 3 | 260 | 260 | 71 | plays 273 |  |  |
| 12 | 5 | 575 | 574 | 253 | Driver 16 R | fairway 48%, sand 22%, trees 7% |  |
| 13 | 4 | 418 | 423 | 133 | 4-wood 40 L | fairway 1% | aim: 4-wood -40 lands 270 yds out in rough (38 yds from fairway) |
| 14 | 4 | 467 | 467 | 114 | Driver 7.5 L | fairway 65%, trees 5%, OB 1% |  |
| 15 | 5 | 516 | 515 | 209 | Driver 2.5 L | fairway 60%, trees 9% |  |
| 16 | 3 | 181 | 181 | 67 | plays 175 |  |  |
| 17 | 4 | 429 | 428 | 214 | 2-wood 6.5 L | fairway 54%, sand 5%, trees 6% |  |
| 18 | 4 | 471 | 472 | 119 | Driver 2.5 L | fairway 60%, sand 17%, trees 8%, water 2% |  |

Totals: page 7,311 = card. The aims on 4 (-32), 5 (+31) and 10 (-31) follow doglegs on the photo. Nothing is off the
course. No Lake or Short Course hole is on the page. Not verified: GolfPass lists Purple at 7,404 (another tee
version). Nit: the title is "RTJ Grand National Golf Caddie" (it does not name the Links).
