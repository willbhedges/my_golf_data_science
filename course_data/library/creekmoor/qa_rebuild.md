# Creekmoor GC: rebuild QA, NAIP fairway fill (2026-11-03)

**Verdict: PUBLISH.** The fairway-fill stage (S4f, ec1e61124) fixes the course-level gap. All 14 par-4/5 holes now
have a fairway that sits on the mown fairway in the photo, and every tee-shot landing reads fairway 39-84%. The aim
CHECKs are gone: only the 3 Black lidar-pad tee CHECK is left, down from 14. No pick aims into a bunker, and the one
native card is sensible.

Page checked: `course_data/library/creekmoor/page.html`, GitHub Actions run 41574368966 (built 2026-11-03T04:35Z).
I ran both solved sets (Black 7,406 and Green 6,806, par 72) through `qa_page.js`, phone and desktop: 18 holes each, 0
page problems, no console errors. I looked at every Black and Green hole picture. I also drew the package fairway
(`zones`, src `fairway_fill:naip`), sand, trees, water, OB and native outlines on the page's own hole images for all 18
holes (scratch `creekmoor_zones.png`).

## Fairway fill

`sources.fairway_fill`: d' 2.01; all 14 holes pass the gate (line cover 0.57-0.84, width 24-42 yds, corridor share
0.29-0.47).

| hole | fill on the photo |
|---|---|
| 1, 2, 3, 6, 9, 11, 13, 15, 16, 18 | follows the mown fairway edge closely, around the fairway bunkers (sand stays sand) |
| 5 | main fairway right; two small scraps (≈ 10 yds) in the rough short of the landing, 70-160 yds. Harmless |
| 8 | right; a thin spur by the creek crossing ~100 yds and one near the forward tees. Harmless |
| 10 | right; a narrow tail runs ~40 yds into the native/sandy area right of the fairway's start. No landing reaches it |
| 14 | right; a small lobe by the tree clump at the fairway's start. Harmless |

No fill on greens, tees, water or houses. The OSM fairway scraps (cyan) by tees and greens are unchanged.

## Picks (were bunker-blind)

| hole | before (fairway 0%) | now |
|---|---|---|
| 14 Black | Driver 28.5 left into the left bunker cluster, sand 15% | Driver 10.5 left between the bunkers, fairway 64%, sand 11% |
| 3 / 13 / 18 Black | among the bunkers, sand 12-13% | aim point on fairway beside the bunkers: fairway 51 / 65 / 62%, sand 12 / 13 / 10%. The oval edge takes in a bunker; the aim is not at one |
| 1 Black / Green | Driver +35 / +39 to the right edge | Driver +31.5 / +40 to the far right of the dogleg-right fairway, fairway 72 / 60%. Green +40 is on the bound and gets no CHECK; the oval clips the right picture edge a little |

## Native cards

One asked (14 Black, prior L 0.40 / R 0.75), kept. Every answer re-plans inside the corridor: L / both → 4-wood +2;
R / current → Driver -10; none → Driver -8. The old ±95-120 yd re-plans are gone.

## Holes

| hole | Black | Green | note |
|---|---|---|---|
| 4, 7, 12, 17 | OK | OK | par 3s; 12 / 17 review tees inside the OSM boxes; yardage = card ±2 |
| 1 | OK | OK (on the ±40 bound) | above |
| 2, 5, 6, 9, 15 | OK | OK | fairway 41-84% |
| 3 | OK (tee CHECK) | OK | Black lidar pad 25 yds from a box, 441 / 440 |
| 8 | OK | OK (tie) | 22.5 / 27 left into the dogleg, fairway 63-75% |
| 10 | OK | OK | 481 / 482; fairway 39-55%, sand 8% |
| 11 | OK (tie) | OK | Driver 28 / 36.5 left around the left bunkers, fairway 57-58%, sand 7-9%, trees 7-9% |
| 13, 14, 16, 18 | OK | OK | fairway 47-76% |

## Next fix

None blocking. Optional: drop fill parts shorter than ~15 yds (holes 5, 8, 14), and clip the hole-10 tail at the
native edge.
