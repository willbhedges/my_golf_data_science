# Hodge Park GC: rebuild QA (2026-11-02)

**Verdict: PUBLISH.** The reviewer's must-fix (17 White on a box behind Blue) and 1 White are fixed. Every Blue hole
now measures within 6 yds of the card. One cosmetic tee issue is left on hole 3 (both sets share one box). It does
not change the play, because par 3s play from the card yardage.

Page checked: `course_data/library/hodge_park/page.html`, built 2026-11-02T04:47Z (GitHub Actions run 41388450661).
Both solved sets (Blue, White, par 71) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page
problems. I looked at every phone hole picture. Card: golfify, Blue 6,181 / White 5,707; page yardage = card on all
36 hole-sets. The request still asks for "Black" and substitutes Blue (harmless).

## Review fixes

| fix in review.md | applied? |
|---|---|
| 17 White: the 489 box, not the 598 box behind Blue | **yes.** Snapped 6 yds to OSM box 279487481, 489 measured / 485 card |
| 1 White: the 373 box | **yes.** 372 measured / 380 card |
| 3 Blue on the 167 box, White on the 144 box | **no (cosmetic).** Both review points (166.5 and 143.6 yds from the green) were snapped 11-12 yds to the same OSM box 279486929 at 155. Blue shows 168 and White 148 from one spot; Blue carries a "measured 155 vs card 168" CHECK. The play-it-like numbers use the card yardage (Blue 181, White 160), so the advice is right |
| 6, 8, 10, 12, 13 Blue "16-30 yds short" (uncertain) | resolved: this build measures 304 / 407 / 400 / 188 / 383 against card 304 / 409 / 405 / 193 / 388 |

## Holes

| hole | Blue | White | note |
|---|---|---|---|
| 1 | OK | **fixed** | |
| 2, 4, 5, 7, 9, 11-14, 16, 18 | OK | OK | |
| 3 | tee shared (cosmetic) | tee shared (cosmetic) | see above |
| 6 | OK (marginal) | OK | Blue Driver on the 304 par 4 to the green complex, trees 19% |
| 8 | OK (marginal) | OK | Blue Driver aim 30 left over the dogleg corner, trees 15% |
| 10 | OK | pick on the bound | White 4-wood aim 40.0 left, fairway 15%, trees 15% (as reviewed) |
| 15 | OK (forecast mid iron; calm Driver +40) | pick on the bound | White 2-wood aim 40.0 right, trees 14% (as reviewed) |
| 17 | OK | **fixed** | |

## Remaining (optional)

1. **Pipeline** (`review` tee snap): a review `tee_ll` that already lies on a long OSM teeing ground should stay
   where it is (or snap along the box's axis), not jump 11-12 yds to the box centroid. On hole 3 two different sets
   ended on the same point.
2. Aim-bound picks on 10 / 15 (decide step clamp), as on other courses.
