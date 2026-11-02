# Colbert Hills: rebuild QA (2026-11-02)

**Verdict: NEEDS FIX** (set name only). The hole 1 tee and the hole 18 aim line are fixed. The page still offers the
OpenGolfAPI artefact set **"Web"** instead of **Black/Blue**, which the review asked to change.

Page checked: `course_data/library/colbert_hills/page.html`, built 2026-11-01T21:23Z. Both solved sets (Web, Silver)
were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems. I looked at every phone hole picture
and the hole 18 desktop picture. Card: OpenGolfAPI. Page yardages equal the card on every hole of both sets.

## Review fixes

| fix in review.md | applied? |
|---|---|
| 1 Web/Black tee: off the clubhouse/parking walk-back onto the back OSM box, card 590 | **yes.** Tee snapped 6 yds to OSM tee 780368833. Page 590 (measured 559 straight; the card follows the dogleg). Driver aim 24 left, no longer on the +40 bound. |
| 18: aim on the hole line, not the straight tee-green line | **yes.** `aim_ll` is now 250 yds along the hole line. Web: Driver on the app line, tie with 2-wood. Silver: Driver 27 right. Neither carries the pond onto the 9th green. |
| 13: calm-day Driver +40 into the greenside bunkers | **partly.** The forecast play is now 2-wood (Web) / 4-wood (Silver) to the left fairway, as the reviewer wanted. The calm-day pick is still Driver aim 40.0 right (on the bound), sand 29-33%, shown in the "Calm-day pick: Driver" badge. Solver issue, not blocking. |
| Course: solved set "Web" (7,505) should be Black/Blue (7,525); request tees `["Black", "Silver"]` | **no.** The request still carries `"tees": "Black", "allow_substitute": true`, so the build again chose OpenGolfAPI's "Web" row. Hole 12 shows 414; Black/Blue is 434. |

## Holes

| hole | Web | Silver | note |
|---|---|---|---|
| 1 | **fixed** | OK | Silver 578 card, 564 measured (dogleg) |
| 2-11, 14-16 | OK | OK | 3, 4, 7, 14 aim CHECKs are judgement calls, as reviewed |
| 12 | wrong length (434 on the Black/Blue card) | OK | follows from the set name |
| 13 | OK (calm-day pick still +40 into sand) | OK (same) | see above |
| 17 | OK (uncertain, as reviewed) | OK | Web on a lidar pad 19 yds behind the back box, 237 = card |
| 18 | **fixed** | OK | Web Driver ends at the bunker at the top of the fairway with a 21 mph tailwind (fairway 36%); a tie with 2-wood. Plausible |

## Next fix

1. `course_data/library/colbert_hills/review.json`: add a `rebuild_hint` `{"tees": ["Black/Blue", "Silver"]}` (or
   `page_set_should_be: "Black/Blue, Silver"`). `review_fixes.py` does send the course note's `tees ['Black', 'Silver']`,
   but the OpenGolfAPI card has no set called "Black" (it is "Black/Blue"), so `allow_substitute` picked "Web" again.
   The hole 1 fix keys on "Web"; with the real set it should key on "Black/Blue" (or "*").
   Pipeline alternative: let the set matcher accept a requested name that is one part of a slash name ("Black" ->
   "Black/Blue") before it substitutes.
2. Optional: aim-bound clamp in the decide step (13 calm-day pick, also seen on St Andrews 15 and Gustin 6).

After that rebuild: PUBLISH, provided the set reads Black/Blue 7,525 and hole 12 shows 434.
