# Swope Memorial Golf Course: rebuild QA, second pass (2026-11-02)

**Verdict: PUBLISH** (with the imagery caveat below). The page now carries the club's 2026 card: Green 6,324 / Bronze
6,079, par 71. The front nine follows the restored routing.

Page checked: `course_data/library/swope_memorial/page.html`, built 2026-11-02T06:23Z (GitHub Actions run
41392580512). Both solved sets (Green, Bronze) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page
problems. I looked at every phone hole picture. No build warnings.

## First-pass fix

| fix | applied? |
|---|---|
| Type the 2026 card (Scorecard-2026.pdf) into `card_review.json`, tees Green + Bronze | **yes.** Sets Green / Bronze, totals 6,324 / 6,079, par 35-36 = 71 |
| Front nine on OSM's own refs 3-9 (restored Tillinghast order; 4 par 3 176, 5 par 5 475, 6 par 4 406, 7 par 3 177, 8 par 4 273, 9 par 4 371) | **yes.** Pars 4 4 4 3 5 4 3 4 4 / 4 4 5 3 4 4 3 5 4 = card. No two holes share a green. |

Page yardage = the 2026 card on all 36 hole-sets. Measured length within 6 yds everywhere (largest: 12 Green 527 /
533 on a lidar pad, 13 Bronze 220 / 215, 15 Bronze 339 / 333). The par-3 green polygons (4, 7, 13, 16) sit on the
visible greens.

## Imagery caveat

The pictures are NAIP 2020, before the 2025-26 restoration (new tees, greens, bunkers and a pond). The 2026 card fits
the OSM boxes to within 6 yds on every hole, and I saw no hole whose tee, fairway or green looks out of place. But
bunkers and the new pond may differ from the pictures. The page does not say this anywhere; I would add a one-line
course note ("aerial imagery predates the 2025-26 restoration") when the page template allows it. Not a blocker.

## Holes

| hole | Green | Bronze | note |
|---|---|---|---|
| 1, 3, 4, 6, 7, 9-14, 16, 17 | OK | OK | |
| 2 | OK (uncertain) | OK (uncertain) | Driver on the 307-321 par 4 to about 40 yds short among trees (fairway 11-14%), as reviewed |
| 5 | OK (marginal) | OK | Driver on the line, trees 20-23% (pre-restoration tree line) |
| 8 | OK | OK | 259-273 par 4; 2-wood / 4-wood to the greenside bunkers (sand 24%). Plausible |
| 15, 18 | OK (marginal) | OK (marginal) | Driver near the tree lines (trees 17-24%). Model choice |

## Remaining (optional)

Re-check the hazard zones once post-restoration imagery is available.
