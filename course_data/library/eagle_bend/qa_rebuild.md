# Eagle Bend GC (Lawrence KS): rebuild QA, final pass (2026-11-02)

**Verdict: PUBLISH.** The rebuild on current code keeps the card fix. The mapper layers (native grass left of 2,
tree adds/erases on 3-15) are in, and the four native-grass check cards are consistent with the page.

Page checked: `course_data/library/eagle_bend/page.html`, GitHub Actions run 41479479995 (committed 18:55Z). Both
solved sets (Gold 7,052, Blue 6,542, par 72) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page
problems, no console errors. I looked at every phone hole picture (montage in the QA scratch folder).

## Checks

| check | result |
|---|---|
| Card / pars (`card_fix.json`) | Pars 4 4 5 3 4 4 5 3 4 / 4 4 3 5 4 4 4 3 5 = 72. Page yardage = card on all 36 hole-sets; measured within 5 yds everywhere (Blue 12: 144 / 139) |
| Mapper layers (`course_data/mapper/eagle_bend/`) | in. Hole 2 native left (6,055 yd2): the Gold pick aims 11 right, away from it. The tree adds/erases on 7, 9, 10, 14, 15 show in the landing stats; every tee shot lands on fairway with 0-4% trees/water/OB |
| Native check cards (`native.json`, Gold) | 4 cards: 2, 13, 15, 11. Priors follow the layers (2 L 0.75, 13 R 0.75). The "current" plans match the page picks to 1-2 yds (2 Driver +12 / page +11; 13 -8 / -9; 15 -20 / -20.5; 11 -5 / -4). Re-plans are sensible: away from the answered side, or 4-wood when both sides are long grass |
| Water filter | ran; 364 m2 of vision water dropped (small cells). The only water near play is the real ponds (8, 17, 18 greens) |
| Aims past ±40 | none |

## Holes

| hole | Gold | Blue | note |
|---|---|---|---|
| 1-5, 8, 9, 11-13, 15-17 | OK | OK | tees on OSM boxes; yardage = card |
| 6 | OK (CHECK) | OK | Gold tee 3 yds off the box line (tee_axis), 456 / 460 |
| 7 | OK (CHECK) | OK (CHECK) | Gold walked back 28 yds, Blue tee_axis; yardage = card ±4 |
| 10 | OK (CHECK) | OK | Gold on a lidar pad 13 yds from the box, 418 / 417 |
| 14 | OK (CHECK) | OK | Gold walked back 56 yds (no mapped back box), 430 / 429 |
| 18 | OK (CHECK) | OK | Gold walked back 41 yds, 547 / 547; the line runs up the fairway left of the pond |

The CHECKs are all tee-position CHECKs where OSM has no back box; the yardages match the card. Same as the previous
pass.

## Next fix

None.
