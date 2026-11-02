# A. L. Gustin GC: rebuild QA, final pass (2026-11-02)

**Verdict: NEEDS FIX (wide aims).** The card, the 15 Gold fix and the mapper trees all took. But the adaptive aim now
prints Gold 6 at **60 yds left** with no CHECK, and Gold 3 at 52 right. The library pages do not carry the wide-aim
CHECK (pipeline).

Page checked: `course_data/library/gustin/page.html`, GitHub Actions run 41479479995 (committed 18:59Z). Both solved
sets (Black 6,424, Gold 5,839, par 70) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems.
I looked at every phone hole picture, and zoomed in on 3, 6 and 16.

## Checks

| check | result |
|---|---|
| Card | page yardage = card on all 36 hole-sets. 15 Gold 350 from its own box (340 measured), 15 Black 399 (400) |
| Mapper layers (`course_data/mapper/gustin/`) | in. 103 tree adds/erases on 1, 3, 4, 6-9, 11, 12, 14-18. Tree readings rose where crowns were added (Black 9 trees 16%, 18 14%, Gold 18 25%, 1 10%); landings still on fairway |
| Native check cards (`native.json`, Black) | 4 cards: 9, 1, 3, 12 (priors 0.25; no mapper native). 3 and 12 match the page (Driver +20 / +19.5; +5 / +7). 9 (+8 / page +2.5) and 1 (+10 / +3.5) are 5-7 yds off; acceptable. Re-plans are 4-wood near the line, or Driver -40 on 9 if right is long grass |
| Water filter | ran; 853 m2 of small vision cells dropped. Water readings at most 4% (14) |
| Aims past ±40 | **Gold 6 4-wood -60** (no CHECK, trees 19%), **Gold 3 2-wood +52.5** (CHECK only for the tee), **Black 16** 2-wood / 4-wood +59 (CHECK: calm landing in sand) |

## Holes

| hole | Black | Gold | note |
|---|---|---|---|
| 1, 2, 5, 8-10, 12, 13, 15, 17, 18 | OK | OK | |
| 3 | OK | **wide aim** (CHECK) | Gold 2-wood +52.5 over the right-hand trees at the dogleg; trees 17-30%. The CHECK on the page is only about the tee (lidar pad 6 yds off) |
| 4 | OK (CHECK) | OK | Black tee_axis 5 yds off the box |
| 6 | OK (aim -40) | **wide aim, no CHECK** | Gold 4-wood -60 over the corner; the landing oval is half off the left edge of the hole picture; trees 19-35% |
| 7 | OK (CHECK) | OK (marginal) | Black chute tee (lidar pad); Gold 4-wood / 2-wood -40 into the corner, sand 11% |
| 11 | OK (CHECK) | OK | Black capped lidar pad, 416 / 424 |
| 14 | OK (CHECK) | OK (CHECK) | lidar pads 150-183 yds from any OSM box (none mapped), yardage = card |
| 16 | **wide aim** (CHECK) | OK | Black +59 toward the green on a 332 par 4 (fairway 7%, sand / trees). The page flags it |

## Next fix

1. **Pipeline (blocks the publish):** carry the wide-aim CHECK onto library pages. `product/decide.py
   wide_aim_flags` (commit 67fda313c) is only in the quick engine. `library/v2_adaptive.py` widens to ±60, but the
   auto-map QA does not add a CHECK, so Gold 6 prints -60 silently. Then rebuild. Gold 3 / 6 and Black 16 become CHECKs;
   the lines are plausible dog-leg lines, so PUBLISH after that.
2. Optional: frame the hole picture so a wide landing stays inside it (Gold 6).
