# TPC Harding Park (CA): multi-course rebuild QA (2026-11-03)

**Verdict: PUBLISH.** The page is the Harding 18. No Fleming hole is left in it, the routing runs 1→18, and every
hole matches the card.

Page checked: `course_data/library/tpc_harding_park/page.html`, GitHub Actions run 41583713847 (built
2026-11-03T05:53Z, request batch `course_batch_multicourse_fix` on 269de3c1d). Set: Championship (7,169, par 72;
AllSquare card). I ran it through `qa_page.js`, phone and desktop: 18 holes, 0 page problems. I looked at every hole
picture.

## Harding, not Fleming

- Package warning: "by hole chains (green -> next tee): #1 18, fleming 9; kept the largest group (no name or near
  point decides: CHECK the course)". The 9 ignored ways are exactly the OSM "Fleming 1-9" ways (par 4-3-3-3-3-3-4-4-3).
- Chain green n → tee n+1: 24-153 yds on every link (the old mix had 1-9 on Fleming).
- Landmarks: the 606-yd par-5 4th, the par-5 10th and 12th, and the 468-yd 18th along Lake Merced.

## Card

The card is AllSquare's TPC Harding Park (Championship / Blue / White / Red). It is the Harding card: its par
4-4-3-5-4-4-4-3-5 / 5-3-5-4-4-4-4-3-4 matches the OSM Harding ways' pars on all 18. Measured vs card: within 1 yd on
17 holes. Hole 5 is the exception: the tee is a walkback (CHECK), 20 yds behind the nearest OSM box, giving 428 vs
the card's 429.

## Holes

| hole | par | yds | pick | note |
|---|---|---|---|---|
| 1 | 4 | 395 | Driver 4.5 R (tie 4-wood) | fairway 70% |
| 2 | 4 | 449 | Driver | fairway 44%, sand 14% |
| 3 | 3 | 183 | plays 185 | |
| 4 | 5 | 606 | Driver | fairway 40% |
| 5 | 4 | 429 | Driver 10 L | fairway 37%, trees 33% (a tree-lined hole). Tee CHECK (walkback) |
| 6 | 4 | 473 | Driver | fairway 59% |
| 7 | 4 | 344 | Driver (tie 4-wood) | fairway 41%, sand 12% |
| 8 | 3 | 230 | plays 221 | |
| 9 | 5 | 525 | Driver | fairway 52% |
| 10 | 5 | 562 | Driver | fairway 55% |
| 11 | 3 | 200 | plays 204 | |
| 12 | 5 | 494 | Driver | fairway 44%, trees 14% |
| 13 | 4 | 428 | Driver 5 L | fairway 48% |
| 14 | 4 | 467 | Driver | fairway 67% |
| 15 | 4 | 405 | Driver 7 L | fairway 49% |
| 16 | 4 | 336 | 4-wood 16 L | fairway 56% |
| 17 | 3 | 175 | plays 176 | |
| 18 | 4 | 468 | Driver 20 L | over the lake corner to the fairway; fairway 71% |

No aim is past ±20, and nothing is off the course.

## Nit

The coordinator should confirm the course choice once: the split kept "the largest group" with a CHECK note, which
is correct here (Fleming is a 9-hole executive course).
