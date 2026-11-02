# Osage National: rebuild QA, final pass (2026-11-02)

**Verdict: NEEDS FIX (native check card 15 only).** The page itself is publishable, with the renovation caveat from
the previous pass. But the hole-15 native-grass card describes a plan the page does not show.

Page checked: `course_data/library/osage_national/page.html`, GitHub Actions run 41479479995 (committed 19:22Z). Both
solved sets (Palmer 7,120, Tournament 6,681, par 72) were run through `qa_page.js`: 18 holes each, phone and desktop,
0 page problems. I looked at every phone hole picture.

## Checks

| check | result |
|---|---|
| Card | page yardage = OpenGolfAPI card on all 36 hole-sets; measured within 7 yds (Palmer 1: 370 / 377, 3: 376 / 370) |
| Mapper layers (`course_data/mapper/osage_national/`) | in. The adds on 5, 6, 7, 9-12, 14, 17, 18 show in the landing stats (e.g. 7 long grass 5%, 12 long grass 3%, 6 water 6%). Tee shots land on fairway 38-83% |
| Native check cards (`native.json`, Palmer) | 3 cards: 5, 15, 11. 5 and 11 match the page (5 Driver -18 / -18.5; 11 -8 / -7). **15 does not:** the card's "current" plan is **Driver +60** and its Right / Both texts read "now Driver, 60 yds right ... would cost 0.27 strokes". The page plays **Long iron -1** (calm and forecast, fairway 83%). The card was solved with a different aim grid (±60) than the page, and +60 is a wide aim with no CHECK |
| Water filter | ran; 3,895 of 19,621 m2 of vision water dropped (3,485 on roads). The water left in the stats is the real ponds / lake (6, 10-12) |
| Aims past ±40 | none on the page (only in card 15, above) |

## Holes

| hole | Palmer | Tournament | note |
|---|---|---|---|
| 1, 4, 5, 8-18 | OK | OK | tees on OSM boxes |
| 2 | OK (CHECK) | OK | Palmer walked back 22 yds, 456 / 455 |
| 3 | OK (CHECK) | OK | Palmer on the lidar pad behind the pond by the parking lot, 376 / 370 (as reviewed) |
| 6, 7 | OK (CHECK) | OK | Palmer lidar pads 18-27 yds behind the boxes; yardage = card ±3 |
| 15 | OK | OK | page fine (Long iron to the fairway); **native card 15 wrong**, see above |

## Next fix

1. **Native card 15** (`course_data/library/osage_national/native.json`): drop or regenerate it from the page's own
   plan (Long iron -1). **Pipeline:** the native-confirm step should take "current" from the page's calm pick, or use the
   page's aim bound, so a card never names a plan the page does not show.
2. As before (not blocking): get a post-renovation card and newer imagery.
