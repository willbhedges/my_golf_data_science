# The Falls Golf Club (O'Fallon MO): rebuild QA, mapper wave 2c (2026-11-03)

**Verdict: PUBLISH.** The mapper layers are in, and the tees and yardages are unchanged from the 2026-11-02 pass, which
was already a PUBLISH. The only aims wider than ±40 are 16 (both sets) and 2 White, and each one prints its wide-aim
CHECK.

Page checked: `course_data/library/the_falls_ofallon/page.html`, GitHub Actions run 41554623184 (package built
2026-11-03T01:40Z). Mapper layers: `course_data/mapper/the_falls_ofallon/` (35 zone edits on 11 holes, 0 tees moved,
72 checked). Both solved sets (Blue 5,994, White 5,594, par 71) were run through `qa_page.js`: 18 holes each, phone and
desktop, 0 page problems, no console errors. I looked at every phone hole picture.

## Tees

Blue and White measured = card ±5 on all 36 hole-sets, with no build warnings and no tee shared between two holes.
Two tee CHECKs are printed and are minor: 6 Blue (`tee_axis`, 4 yds off the OSM box) and 2 White (lidar pad, 9 yds
off the box).

## Mapper layers

| edit | on the page? |
|---|---|
| crown groups added as recovery on 1-3, 5-7, 11, 13, 15, 18 | yes. Landing-oval trees are 2-14% (Blue) and up to 29% on 6 White (the left tree line), on real crowns |
| 10: lake trimmed by 1,550 sq yds | yes. 10 Blue 4-wood: fairway 62%, trees 2%, no water in the pattern |
| 13: 2,034 sq yds of stale recovery erased | yes. 13 Blue 4-wood lands clean |
| 18: 3,276 sq yds of OB erased (in play, not houses) | yes. 18 Driver +7, fairway 38-45%, trees 14-17%, no OB |

## Holes

| hole | Blue | White | note |
|---|---|---|---|
| 1, 4, 5, 8, 10-12, 14, 17 | OK | OK | par-3 boxes on the green |
| 2 | OK | OK (CHECK) | White calm Driver +53 over the dogleg-right corner to the fairway (37%, trees 19%). Wide-aim CHECK printed. The forecast play is 4-wood, a tie |
| 3 | OK | OK | Driver 32.5 / 36 right (inside ±40), fairway 31-32% |
| 6 | OK | OK (marginal) | White Driver -22, trees 29% |
| 7, 13, 15, 18 | OK | OK | Driver/4-wood near the fairway, trees 7-17% |
| 9 | OK (tie) | OK (tie) | Pond short-left, out of reach |
| 16 | OK (CHECK) | OK (CHECK) | Driver -50 / -51 across the dogleg-left corner to the fairway (32-33%). Wide-aim CHECK printed on both sets |

## Next fix

None.
