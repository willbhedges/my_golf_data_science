# Shoal Creek Golf Course (Kansas City MO): rebuild QA (2026-11-02)

**Verdict: NEEDS FIX (hole 4 Gold tee).** The build now completes, and the rv16 routing fix is in: 5 and 6 are Shoal
Creek's own holes, with imagery. But the Gold tee on 4 moved to a lidar pad 77 yds beside the Blue box. From there the
hole is drawn through the woods, and the pick is a 4-wood aimed **58.5 yds left**.

Page checked: `course_data/library/shoal_creek/page.html`, GitHub Actions run 41479479995 (committed 19:25Z). Both
solved sets (Gold 6,983, Blue 6,363, par 71) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page
problems. I looked at every phone hole picture, and zoomed in on 4.

## Review fixes

| fix (review.md rv16) | applied? |
|---|---|
| 5 / 6 from Shoal Creek's ways (supplement + `ignore_osm_holes`), not Hodge Park's | **yes.** 5 is a par 3, 233 / 234 Gold, 178 / 179 Blue, on OSM boxes, box on the green. 6 is a par 4, 366 / 364 and 335 / 333. Pictures show imagery (no longer black) |
| 2 Gold (walkback, left as is) | unchanged: walked back 32 yds, 428 / 427 (CHECK) |

## Hole 4 Gold (new fault)

The previous build had Gold walked back 17 yds behind the OSM box, on the hole line (review: "418/384 = card, sensible").
Now the Gold tee is lidar pad `lidar:409` at (39.2490648, -94.4742379). That is 67 yds west and 37 yds south of the Blue
box 897736289, beside the hole, not behind it. The length still reads 418 = card, but the tee line crosses the tree
belt, and the 4-wood -58.5 lands at the left edge of the picture (trees 6%, sand 8%). Blue 4, from the box, plays
4-wood +9 down the fairway. Hole 4 is straight (green on the hole line), so an aim of 58 yds is a symptom of the wrong tee.

## Checks

| check | result |
|---|---|
| Card | golfify; page = card on all 36 hole-sets; measured within 4 yds |
| Mapper / native cards | not used; `native.json` empty, as expected |
| Water filter | ran; 459 of 1,938 m2 of vision water was on roads and was dropped. Water in the stats is the 15 / 16 ponds (Blue 12: 12%, from the pond left) |
| Aims past ±40 | **Gold 4 -58.5** (wrong tee, above) |

## Holes

| hole | Gold | Blue | note |
|---|---|---|---|
| 1, 3, 7-11, 13-17 | OK | OK | tees on OSM boxes |
| 2 | OK (CHECK) | OK (CHECK) | Gold walkback, Blue tee_axis 3 yds off; yardage = card ±4 |
| **4** | **wrong tee** (CHECK) | OK | see above |
| 5, 6 | **fixed** | **fixed** | real Shoal Creek holes |
| 12 | OK | OK (marginal) | Blue 4-wood to the rough short of the pond, trouble 25%. Model choice |
| 18 | OK | OK | trees 12-16% along the right; landings on fairway |

## Next fix

1. **Course** (`course_data/library/shoal_creek/review.json`, hole 4 `fix`): `"tee_ll": {"Gold": [39.249541,
   -94.4738726]}` (the OSM hole-line start, 411 yds to the green point, 32 yds behind the Blue box on the line), `"yards":
   {"Gold": 418}`. Or walk it back 34 yds behind Blue along the green line: [39.2495854, -94.4737528]. Then rebuild.
2. **Pipeline** (tee localizer): a lidar pad should not win when it is far off the hole line (here about 70 yds beside
   the set's own boxes) while an on-line walkback matches the card.
