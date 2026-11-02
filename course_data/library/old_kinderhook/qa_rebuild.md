# Old Kinderhook: rebuild QA (2026-11-02)

**Verdict: PUBLISH.** Both fixes are applied: the club's Championship column replaces the OpenGolfAPI "Web" card, and
the tees on 9 and 15 are moved. Hole 15 is now a 402-yd par 4 instead of a 273-yd one. Its Championship tee is the
reviewer's estimate, which nobody has seen on imagery.

Page checked: `course_data/library/old_kinderhook/page.html`, built 2026-11-02T03:14Z. One solved set (Championship
6,855, par 71). This is a single-set page with no set picker, so `qa_page.js` was run without the set argument (with the
argument it times out on the hidden picker). 18 holes, phone and desktop, 0 page problems. I looked at every phone hole
picture.

## Review fixes

| fix in review.md | applied? |
|---|---|
| Card = club Championship column (`rebuild_hint.yardages`, 6,855, par 71) | **yes.** Source `request`; the set is named "Championship"; all 18 yardages and pars equal the column. |
| 15: Championship tee about 70 yds behind the Member tee (38.00318, -92.80561), 402-404 | **yes.** Supplement tee, 0 yds from the point, 405 measured / 402. The play is 2-wood (calm 4-wood, a tie), aim on the line, fairway 88%, past the pond. |
| 9: tee off the lidar pad in the woods onto the hole-line start, about 505 | **yes.** Supplement tee, 506 measured / 514 card. Driver aim 7 right, fairway 55%. |

## Holes

| hole | Championship | note |
|---|---|---|
| 1-8, 10-14, 16-18 | OK | OSM boxes, measured within 5 of the column; par-3 boxes on the green |
| 9 | **fixed** | |
| 15 | **fixed** (tee uncertain) | the tee is on open grass by the buildings at the bottom of the picture. This is the reviewer's line-extension estimate |

## Next fix

None blocking. Optional: confirm the hole 15 Championship box on newer imagery or the club's hole guide.
Tooling note: `qa_page.js` with a set argument fails on single-set pages (the `#set` buttons are hidden).
