# WeaverRidge Golf Club: rebuild QA (2026-11-02)

**Verdict: NEEDS FIX.** The main fix worked: the page uses `card_review.json`, and the set names are now right ("Black"
is the tips, "Gold" is the Gold set). But the review's per-hole yardages were sent as `"*"` (the solved set, which is
Black), so three Black holes are now wrong.

Page checked: `course_data/library/weaver_ridge/page.html`, built 2026-11-01T21:18Z. Both solved sets (Black, Gold, par
72) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems. I looked at every phone hole
picture and the Gold 5 desktop picture. Routing, greens and pars are right on all 18 holes.

## Review fixes

| fix in review.md | applied? |
|---|---|
| Rebuild with `card_review.json`, tees Black + Gold (set labels were swapped) | **yes.** Black: 1 540, 3 519, 7 435, 12 228, 15 458 (tips). Gold: 1 518, 7 401, 15 424. All match the golfify card. |
| Gold tees on 11, 13, 14, 16, 18 moved to the OSM boxes at card yardage | **yes for Gold.** 11 482, 13 401, 14 362, 16 401, 18 535; all on OSM boxes, measured = card. |
| Black 16 probably 401, not golfify's 439 | **yes.** 401, on the box |
| 5: tips tee unmapped, expect a CHECK | still a CHECK, and now worse, see below |

## New problems on Black (from the `"*"` yardage overrides)

`review.json` gives bare `"yards"` (meant for the Gold set on 11, 13, 18 and for the tips on 5, 14, 16).
`review_fixes.py` sends them as `yardage_overrides {ref: {"*": y}}`, and `"*"` is applied to the solved set, Black:

| hole | Black card | page Black | effect |
|---|---|---|---|
| 13 | 432 | **401** | Black sits on the **same tee as Gold** (403 measured). The previous page had the tips on a lidar pad at 427, which the reviewer accepted |
| 18 | 556 | **535** | Black on the same tee as Gold (535). The previous page had 554 = card |
| 11 | 489 | 482 | Black on Gold's box; 7 yds, minor |
| 5 | 387 | **387 shown, 326 measured** | Black is a capped walk-back ("ran onto a building 40 yds behind the line start, capped 62 yds short of the card"). The Black marker is **in front of** the Gold box (363). The page shows 387 from a spot that measures 326 |

The Black total reads 6,933 instead of 7,030.

## Holes

| hole | Black | Gold | note |
|---|---|---|---|
| 1-4, 6-9, 12, 15, 17 | OK | OK | |
| 5 | **wrong tee** | OK | Gold Driver aim 39.5 right across the corner of the lake to the fairway (83%), a legitimate cape line |
| 10 | pick on the bound (as reviewed) | pick on the bound | 4-wood aim 40.0 right toward the creek/tree band, 48% trees/water pattern on Gold (CHECK). The review asked for a recheck: unchanged, still a model issue |
| 11 | minor (482 vs 489) | OK | |
| 13 | **wrong (Gold tee)** | OK | |
| 14 | OK (406) | OK (362) | |
| 16 | OK (401) | OK | |
| 18 | **wrong (Gold tee)** | OK | |

## Next fix

1. **Course:** in `course_data/library/weaver_ridge/review.json`, make the yards per-set: 11 `{"Gold": 482}`, 13
   `{"Gold": 401}`, 14 `{"Black": 406}`, 16 `{"Black": 401, "Gold": 401}`, 18 `{"Gold": 535}`. On 5, pin Black to the
   Gold box until the tips are mapped: `"tee_ll": {"Black": [40.7493811, -89.6649398]}, "yards": {"Black": 387}`. That
   gives an honest 363 measured instead of a spot in front of Gold. Then rebuild.
2. **Pipeline:** the same `review_fixes.py` `"*"` issue as The Falls. A bare `yards` should apply to the set(s) the
   fix's notes or tee_ll name, or to the reviewed page set, never blindly to the solved set after the sets were renamed.
3. (Pipeline) A capped walk-back that ends **in front of** a shorter set's tee should fall back to that box.

After that rebuild: PUBLISH, provided Black reads 432 / 556 on 13 / 18 from the back tees (lidar pads behind Gold are
fine) and Black 5 is no longer forward of Gold.
