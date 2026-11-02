# Eagle Bend GC (Lawrence KS): rebuild QA (2026-11-02)

**Verdict: PUBLISH.** The scrambled-card fix is applied: the page now uses `card_fix.json` (golfify reordered, Gold 13
= 610), and every hole on both sets has the right par and yardage on the right OSM hole.

Page checked: `course_data/library/eagle_bend/page.html`, built 2026-11-01T21:12Z. Both solved sets (Gold 7,052,
Blue 6,542, par 72) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems. I looked at every
phone hole picture.

## Review fixes

| fix in review.md | applied? |
|---|---|
| Rebuild with `card_fix.json` (holes 2-9 and 11-18 swapped back, 18 par 5, Gold 13 = 610) | **yes.** Scorecard source is the file. Pars 4 4 5 3 4 4 5 3 4 / 4 4 3 5 4 4 4 3 5 = 72. All 36 page yardages equal the card, and the measured length is within 7 yds of it on every hole-set. |
| Holes 3/12 no longer par 3s on par-5 corridors; hole 4 tee back on the course | **yes.** 3 is a 574/545 par 5, 12 is a 165/139 par 3 with the box on the green, and 4 is a 163/140 par 3 from OSM boxes. |

## Holes

| hole | Gold | Blue | note |
|---|---|---|---|
| 1-6, 8, 9, 11-13, 16, 17 | OK | OK | tees on OSM boxes; Driver landings on fairway; par-3 boxes on the green |
| 7 | OK | OK | Gold walk-back (561 measured / 560) |
| 10 | OK | OK | Gold on a lidar pad, 418 / 417 |
| 14 | OK | OK | Gold walk-back (430 / 429). Driver aim 13 left, water 8%, fairway 55% |
| 15 | OK | OK | 340/320-yd par 4: Driver to about 50 yds short, beside the greenside bunkers (fairway 32%). Plausible |
| 18 | OK | OK | Gold walk-back (547 / 547) |

Note: the build log says `requested tee set 'Black' is not on the card; using 'Gold' instead`. That is harmless here,
because Gold is the back set.

## Next fix

None. Publish.
