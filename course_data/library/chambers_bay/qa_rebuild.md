# Chambers Bay (University Place WA): rebuild QA after the card-order fix (2026-11-03, run 41607398168)

**Verdict: PUBLISH (after the normal confirm of the 9 CHECK holes).** The card-order fix (eb20d7bef) did what it
should. The OSM holes 1-18 walk as a round, with the longest green-to-next-tee at 234 yds (3→4; Chambers Bay is a long
walk), so the order was kept and not renumbered to the card's "best" 1↔13 swap. The card (golfify, cross-checked
against AllSquare and OpenGolfAPI) was kept, and the par disagreements on 1 and 13 became CHECKs. `regate` blocks
nothing.

Page checked: `course_data/library/chambers_bay/page.html`, built 2026-11-03T09:38Z. `qa_page.js` ran on phone and
desktop, for Navy (the opening set) and Sand: 18 holes each, 0 problems. I looked at all 36 hole pictures. The 2023
NAIP is pale, which is the fescue, not an imagery fault. Black is not on the card, so the build used Navy. Navy 7,100
and Sand 6,605 equal the card hole by hole.

## The 9 CHECK holes

- **1, 13: par, Sand set only.** Chambers Bay swaps par 4 and par 5 between 1 and 13 by tee set. golfify's Navy row is
  1 = par 5, 13 = par 4, and its Sand row (and "White #2") flips that. The page uses one par row for both sets, the
  Navy one. OSM tags the Sand way round (1 = 4, 13 = 5), hence the "OSM says" notes. So on the Sand set the page shows 1 as par 5
  (487) and 13 as par 4 (468) against a card saying 4 and 5. AllSquare's Sand row agrees with the page (1 = 5,
  13 = 4), so the sources disagree, and a CHECK is the right outcome. Navy passes.
- **3, 8, 11, 12, 14: tee not on an OSM box.** The tee was placed on a lidar or texture pad 7-39 yds from the nearest
  box (11 Sand is a 66-yd walkback). On 11, OSM maps only the 496 and 531 boxes, so Navy 457 and Sand 425 are unmapped
  forward tees. The others sit between mapped boxes.
- **7: wide aim, Sand.** Driver 40 R, past the 40-yd bound at +51 on a dogleg-right corner (Humpback). The landing is
  on fairway (91%), and Navy aims 27 R. The CHECK is right.
- **17: yardage.** The card says 172 on both sets, and the tee-axis marker measures 159 (-13). OSM has a 171 box, so
  the 172 tee exists. The picker placed the marker 4 yds off a nearer box. The CHECK is right, with a small effect
  (the par-3 play number is 170).

## Holes (page as built)

| hole | par page (card Navy/Sand) | Navy page / card | Sand page / card | OSM tee boxes (yds to green) | chain | Navy pick, lie | Sand pick, lie | CHECKs |
|---|---|---|---|---|---|---|---|---|
| 1 | 5 (5/4) | 494 / 494 | 487 / 487 | 450, 465, 488 | - | Driver 5.5R (fairway 67%, sand 3%, trees 22%) | Driver 5R (fairway 68%, sand 1%, trees 21%) | Sand: par: par 5 vs card 4 |
| 2 | 4 (4/4) | 395 / 395 | 365 / 365 | 336, 378, 401 | 76 | 4-wood 3L (fairway 71%, sand 4%, trees 20%) | 4-wood 28L (fairway 60%, sand 15%, trees 10%) |  |
| 3 | 3 (3/3) | 167 / 167 | 145 / 145 | 126, 197 | 96 | plays 159 | plays 139 | Navy: tee CHECK (lidar_pad; 29 yds from the nearest OSM tee box); Sand: tee CHECK (lidar_pad; 17 yds from the nearest OSM tee box) |
| 4 | 5 (5/5) | 530 / 530 | 480 / 480 | 455, 480, 505, 513, 632, 670 | 234 | Driver 15.5R (fairway 88%, sand 2%) | Driver 19.5R (fairway 87%, sand 5%) |  |
| 5 | 4 (4/4) | 465 / 465 | 441 / 441 | 391, 418, 434, 462, 483 | 68 | Driver 6.5R (fairway 60%, sand 28%) | Driver 1.5L (fairway 61%, sand 31%) |  |
| 6 | 4 (4/4) | 418 / 418 | 418 / 418 | 351, 375, 401, 492, 622 | 49 | 2-wood 14.5R (fairway 89%, trees 7%) | 2-wood 14.5R (fairway 89%, trees 7%) |  |
| 7 | 4 (4/4) | 482 / 482 | 435 / 435 | 375, 393, 429, 476 | 44 | Driver 27R (fairway 79%, sand 18%) | Driver 40R (fairway 91%, sand 3%, trees 2%) | Sand: wide_aim: Driver aim +51 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 8 | 5 (5/5) | 557 / 557 | 523 / 523 | 523, 550, 595, 707, 729 | 71 | Driver 8.5L (fairway 66%, about 270 yds in) | Driver 5L (fairway 61%, about 236 yds in) | Navy: tee CHECK (texture_pad; 7 yds from the nearest OSM tee box) |
| 9 | 3 (3/3) | 227 / 227 | 168 / 168 | 171, 196, 223 | 101 | plays 200 | plays 148 |  |
| 10 | 4 (4/4) | 398 / 398 | 381 / 381 | 365, 386, 387, 406, 430 | 221 | 4-wood 8L (fairway 82%, sand 10%, trees 3%) | 4-wood 12L (fairway 84%, sand 5%, trees 7%) |  |
| 11 | 4 (4/4) | 457 / 457 | 425 / 425 | 496, 531 | 66 | Driver 22.5L (fairway 69%, sand 5%, trees 21%) | 4-wood 10.5L (fairway 84%, sand 2%, trees 9%) | Navy: tee CHECK (lidar_pad; 39 yds from the nearest OSM tee box); Sand: tee CHECK (walkback; 66 yds from the nearest OSM tee box) |
| 12 | 4 (4/4) | 281 / 281 | 262 / 262 | 182, 294, 302 | 71 | Driver 7.5R (fairway 53%, sand 7%, trees 28%) | 4-wood 0.5R (fairway 78%, sand 2%, trees 16%) | Sand: tee CHECK (lidar_pad; 28 yds from the nearest OSM tee box) |
| 13 | 4 (4/5) | 485 / 485 | 468 / 468 | 395, 442, 510 | 98 | Driver 21R (fairway 74%, sand 2%) | Driver 18.5R (fairway 74%, sand 12%) | Sand: par: par 4 vs card 5 |
| 14 | 4 (4/4) | 496 / 496 | 423 / 423 | 447, 487, 512, 537 | 90 | Driver 23.5L (fairway 79%, sand 19%) | Driver 24.5L (fairway 69%, sand 8%) | Sand: tee CHECK (lidar_pad; 17 yds from the nearest OSM tee box) |
| 15 | 3 (3/3) | 139 / 139 | 139 / 139 | 99, 114, 139, 238 | 199 | plays 129 | plays 129 |  |
| 16 | 4 (4/4) | 396 / 396 | 359 / 359 | 280, 340, 392, 417 | 89 | 4-wood 5R (fairway 86%, sand 8%, trees 2%) | Driver 25R (fairway 72%, sand 15%, trees 8%) |  |
| 17 | 3 (3/3) | 172 / 172 | 172 / 172 | 119, 132, 149, 171, 217 | 107 | plays 170 | plays 170 | Navy: tee CHECK (tee_axis; 4 yds from the nearest OSM tee box); yardage: measured 159 vs card 172 (-13); Sand: tee CHECK (tee_axis; 4 yds from the nearest OSM tee box); yardage: measured 159 vs card 172 (-13) |
| 18 | 5 (5/5) | 541 / 541 | 514 / 514 | 506, 535, 592 | 63 | 4-wood 6.5R (fairway 85%, sand 10%, trees 1%) | Driver 12R (fairway 58%, sand 22%, trees 12%) |  |
| total | | 7,100 / 7,100 | 6,605 / 6,605 | | | | | |

Hole 1 Navy is 494 because of the card consensus. golfify and AllSquare both list Navy 1 at **559**, and OpenGolfAPI
lists 494. The consensus took 494 because it matches the OSM hole line (493), and the mapped boxes stop at 488. If the
real Navy tee is the unmapped 559 one, the page's Navy 1 is 65 yds short. Navy 1 passes the per-hole check, so a
reviewer confirming the page should look at it. Not verified on the ground.

Other notes: 12 Navy drives the 281-yd par 4 (Driver 7.5 R, 28% trees in the pattern; the forest is left). That is
aggressive but on the course. Sand plays 4-wood. No other aim is past 27.5 yds, and nothing is off the course.

## Fix

None pushed. The CHECKs are real disagreements between sources, not build faults.
