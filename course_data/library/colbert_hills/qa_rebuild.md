# Colbert Hills: rebuild QA, wide-aim pass (2026-11-03)

**Verdict: PUBLISH.** The agent mapper layers are in, as `course_data/mapper/colbert_hills/review.md` describes. Hole
13's drive-the-green line (Driver 51.5 right, both sets) now carries the wide-aim CHECK, and its oval is inside the
picture.

Page checked: `course_data/library/colbert_hills/page.html`, GitHub Actions run 41537321619 (committed 2026-11-03
01:22Z). I ran both solved sets (Black/Blue, Silver) through `qa_page.js`, phone and desktop: 18 holes each, 0 page
problems, no console errors. I looked at every Black/Blue phone hole picture, and checked every landing oval against
the picture edge on both sets (0 outside, picks or club rows).

## Checks

| check | result |
|---|---|
| Mapper layers | applied 2026-11-02T23:00Z, 21 ops, 5 tee moves. Agent native zones on 1, 3, 4, 6, 7, 10, 12, 14, 16 and 18; landings read "long grass 1-5%" on 1, 3, 4, 6, 14 and 16. Water added on 9 (2 zones; the 9 landing reads water 1-3%). OB erased on 13 and 16: no OB in either landing. The 7 recovery erase is in |
| Agent tees | 1 Black/Blue moved 33 yds onto the rearmost raised box. This agrees with the review point (5 m apart): 559 measured / 590 card, the card following the dogleg. 1 Silver moved 31 yds to the next box (544 / 578, same dogleg gap; low confidence). 17 Black/Blue moved 30 yds: 237 = card |
| Native check cards (Black/Blue) | 16 (Driver -21) and 9 (Driver -5) = page. Priors follow the layers (16 L 0.75 / R 0.9). 3 and 14 dropped (the planner's plan is not the page's) |
| Wide-aim CHECK | 13 on both sets |
| Card / pars | page yardage = card on all 36 hole-sets. Measured within 5 yds except 1 (dogleg; yardage CHECK on both sets) |

## Holes

| hole | Black/Blue | Silver | note |
|---|---|---|---|
| 2, 4-6, 8-12, 14-18 | OK | OK | |
| 1 | OK (yardage CHECK) | OK (yardage CHECK) | 559 / 590 and 544 / 578 measured straight; the card follows the dogleg. Tees on the visible boxes |
| 3 | OK | OK (aim CHECK) | Silver 4-wood -3 lands 10 yds short of the fairway |
| 7 | OK (aim CHECK) | OK | Driver +15.5 lands just past the mapped fairway, as before |
| 13 | OK (CHECK) | OK (CHECK) | Driver 51.5 / 50.5 right to the greenside bunker complex, sand 21-26%. A judgement call, now flagged |

## Next fix

None.
