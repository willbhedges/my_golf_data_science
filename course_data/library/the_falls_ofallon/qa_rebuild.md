# The Falls Golf Club (O'Fallon MO): rebuild QA (2026-11-02)

**Verdict: NEEDS FIX.** The rebuild did what the review asked: it uses `card_review.json`, and its solved sets are
**Blue and White**, so the made-up Gold tees are off the page. But the review's per-hole Gold yardages leaked onto
**Blue** on 6 holes. On those holes the Blue tee now sits on the back (Gold) box and the page shows the Gold-box
yardage. White is clean.

Page checked: `course_data/library/the_falls_ofallon/page.html`, built 2026-11-01T21:34Z. Both solved sets (Blue,
White, par 71) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems. I looked at every phone
hole picture. Pars 36-35 = 71, routing and greens as reviewed.

## What went wrong on Blue

`review.json` gives each Gold-tee hole `fix: {"tee_ll": {"Gold": [...]}, "yards": 390}`. The `yards` value is a bare
number meant for Gold's back box. `review_fixes.py` turns a bare number into `yardage_overrides {ref: {"*": yds}}`,
and `"*"` means **the solved set**, which is now Blue. So Blue gets the Gold-box yardage, and the tee localizer then
puts the Blue marker on the back box (2-4 yds from the Gold fix point):

| hole | Blue card | page Blue | Blue tee |
|---|---|---|---|
| 2 | 379 | **390** | back box (2 yds from the Gold fix) |
| 3 | 341 | **368** | back box (3 yds) |
| 9 | 449 | **476** | back box (4 yds) |
| 10 | 360 | **374** | back box (3 yds) |
| 13 | 345 | 344 | back box (1 yd), harmless |
| 15 | 510 | **506** | back box (0 yds), harmless |
| 18 | 499 | 482 | the review moved Blue here on purpose (walk-back at the road), OK |

11 (365) and 16 (330) equal the Blue card anyway. The page's Blue total is **6,068** instead of the card's 6,011.

## Holes

| hole | Blue | White | note |
|---|---|---|---|
| 1, 4-8, 11, 12, 14, 16, 17 | OK | OK | OSM boxes, card yardage |
| 2, 3, 9, 10 | **wrong tee/yardage** (Gold box) | OK | see table |
| 13, 15 | on the back box, yardage within 4 | OK | |
| 18 | OK (review tee) | OK | |
| 16 | OK | OK | Blue Driver to the left of the line, fairway 29% (the review's uncertain pick); not blocking |

## Next fix

1. **Course:** in `course_data/library/the_falls_ofallon/review.json`, make each Gold fix's yards per-set:
   `"yards": {"Gold": 390}` (likewise 3, 9, 10, 11, 13, 15, 16) and `"yards": {"Gold": 482, "Blue": 482}` on 18. Then
   rebuild (coordinator: course_page_the_falls_ofallon).
2. **Pipeline** (`course_data/library/review_fixes.py`): when a hole's `fix` has `tee_ll` for named sets and a bare
   `yards`, key the yardage to those sets, not to `"*"`. `"*"` should only be used when the fix names no set. The same
   pattern is in Swope, Drumm Farm, Weaver Ridge, La Nickell, Creekmoor and Colbert. It is harmless there only because
   the reviewed set happens to be the solved set.

After that rebuild: PUBLISH, provided Blue reads 379 / 341 / 449 / 360 on 2 / 3 / 9 / 10 from the Blue boxes and totals
6,011.
