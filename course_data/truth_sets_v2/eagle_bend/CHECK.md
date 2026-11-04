# Eagle Bend Golf Course (Lawrence, KS): truth v2 check (native-grass set)

Card: package card (`course_data/packages/eagle_bend/package.json` tee_sets). Corridor set **Gold** (the package's set).

**Confidence: medium (routing, greens, trees, fairway, water); golfer truth for native on 2, 3, 5, 6; medium-low native elsewhere (NAIP 2021 only, summer).**

How it was checked: routing = `draft_spec.py --package-lines` from the OSM golf=hole ways (package hole lines where OSM has none), greens = OSM outlines, tees = OSM tee boxes measured against the card (`build_holes_truth.py`; `*` = a box within 8 yds of the card length, else estimated along the line). The routing was viewed on the whole-course map only (no per-hole tee sheets). Corridors: every par-4/5 tee shot's 130-420 yd footprint; trees = 3DEP lidar canopy > 2.5 m when the raw stack is present (NAIP crowns otherwise), fairway / water / sand = OSM. **Native / long grass is the point of this course** (s2_longgrass.md 'Enlarged native set'): traced by eye on the corridor photos (NAIP 2023 0.3 m unless said), as the unmown ground beyond the mown-rough band around every OSM fairway, per hole side, with trees, water, sand and fairway drawn over it. Sentinel-2 was NOT used to draw it (it is what the native model is scored against). OB not traced (none drawn).

Numbering: the OSM / OpenGolfAPI order (library review rv06; the golfify card is scrambled). The golfer's notes match the OSM numbering: his hole 3 'native left before the pond' is the par-5 3 that ends beside the pond; in the golfify order 3 would be the real 12, a par 3 with no pond. Golfer (hard truth): 2 native left and right, 3 left before the pond, 5 left, 6 left. Imagery (NAIP 2021 / CIR, mottled unmown grass) agrees on 2 left, 2 right (beyond the cart path), 5 left and 6 left; on 3 left the 2021 photo alone was ambiguous, but NAIP 2017, 2019 and 2023 (tourn_truth evidence render) show tan / textured unmown grass left of the fairway, so the imagery agrees on all four of his holes. No disagreement found. Added from imagery only: 11, 13 (both sides), 15, 16, 18 (left).

## Uncertain items

| hole | item |
|---|---|
| 2 | right native starts beyond the cart path (~20 yds right of the fairway edge); golfer said 'right' without an edge |
| 3 | golfer: native left before the pond; agrees with NAIP 2017/2019/2023; drawn to the end of the footprint (the pond is beyond it) |
| 11 13 15 16 18 | native from the 2021 photo only (mottled vs smooth turf): medium-low |
| 1 7 9 10 14 | no native traced (mown / trees / water) |
| 14 | Gold tee (re-checked 2026-11-03) | **moved by hand to the back edge of the back-most mapped box: 374 yds vs card 429.** The +62 estimate is open rough beside a tree line: no box in NAIP 2021 / 2023, flat DEM, no lidar pad. |
| 14 | Gold tee: **LOW CONFIDENCE** (blind re-check 2026-11-03, `../TEE_RECHECK.md`: unsure, lean disagree) | the re-check measures a raised, flat DEM pad (+0.47 m, std 0.03 m, like the mapped round box) on the 429 contour beside the tree line (~425 yds; faint mown patch in NAIP 2021 / 2023, no OSM box, no detected lidar pad). Neither check found a visible tee. Kept at 374, flagged `tee_confidence` low in `holes_spec.json`; `platform/error_budget.py` reports scores with and without it. |
| 18 | Gold tee (re-checked 2026-11-03) | moved by hand 23 yds right onto the small mown pad at the end of the cart path (raised in the DEM): 547 yds = the card. |
| all | mown-rough width 10 yds: +/-5 |
