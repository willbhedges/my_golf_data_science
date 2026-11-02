# Colbert Hills: rebuild QA, second pass (2026-11-02)

**Verdict: PUBLISH.** The solved sets are now **Black/Blue** (7,525) and **Silver** (7,049); "Web" is gone. Hole 12
reads 434, the hole 1 tee and the hole 18 aim fix still hold. One open solver caveat on 13 (below).

Page checked: `course_data/library/colbert_hills/page.html`, built 2026-11-02T06:23Z (GitHub Actions run 41392580512).
Both solved sets were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems. I looked at every
phone hole picture. Card: OpenGolfAPI; page yardage = card on all 36 hole-sets, measured within 5 yds except 1 (dogleg,
below).

## First-pass fixes

| fix | applied? |
|---|---|
| Sets Black/Blue + Silver, no "Web" | **yes.** Request `tees "Black/Blue"`; hole 12 Black/Blue 434 (435 measured) |
| 1: Black/Blue tee off the parking walk-back | **yes.** Review tee snapped 6 yds to OSM box 780368833. 590 on the card, 559 straight (the card follows the dogleg). Driver aim 24 left, fairway 29% |
| 18: aim on the hole line | **yes.** `aim_ll` 250 yds along the hole line. Black/Blue Driver on the app line, tie with 2-wood, water 3%; Silver Driver aim 27 right, fairway 36%. Neither carries the pond |

## Holes

| hole | Black/Blue | Silver | note |
|---|---|---|---|
| 1 | **fixed** | OK | Silver 578, 573 measured |
| 2-12, 14-16 | OK | OK | 3, 4, 7, 14 aim CHECKs are judgement calls, as reviewed |
| 13 | OK (calm-day pick on the bound) | **pick on the bound** | Silver's forecast pick is now Driver aim 40.0 right into the greenside bunker cluster (sand 33%, fairway 20%, 44 yds in), the reviewer's "bad pick". Black/Blue plays 4-wood (calm-day Driver +40, sand 29%) |
| 17 | OK (uncertain, as reviewed) | OK | Black/Blue on a lidar pad 19 yds behind the back box, 237 = card |
| 18 | **fixed** | **fixed** | |

## Remaining (optional)

13 is the shared aim-bound issue: every bad 13 pick sits at exactly +40.0 yds. A review file cannot fix it. The fix is
in the decide step (aim grid clamp at ±40; the same as St Andrews 15, Gustin 6/16, Weaver 10). It is not a geometry
fault, and the page shows the bunkers, so I don't block on it. If the coordinator wants 13 clean first, fix the clamp
and rebuild.
