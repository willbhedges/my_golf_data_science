# Sand Creek Station (Newton, KS): truth v2 check (native-grass set)

Card: package card (`course_data/packages/sand_creek_station/package.json` tee_sets). Corridor set **Championship** (the package's set).

**Confidence: medium (routing, greens, trees, fairway, water); medium-low long-grass edges (+/-6 yds); OB not traced; tees: Championship by box/card.**

How it was checked: routing = `draft_spec.py --package-lines` from the OSM golf=hole ways (package hole lines where OSM has none), greens = OSM outlines, tees = OSM tee boxes measured against the card (`build_holes_truth.py`; `*` = a box within 8 yds of the card length, else estimated along the line). The routing was viewed on the whole-course map only (no per-hole tee sheets). Corridors: every par-4/5 tee shot's 130-420 yd footprint; trees = 3DEP lidar canopy > 2.5 m when the raw stack is present (NAIP crowns otherwise), fairway / water / sand = OSM. **Native / long grass is the point of this course** (s2_longgrass.md 'Enlarged native set'): traced by eye on the corridor photos (NAIP 2023 0.3 m unless said), as the unmown ground beyond the mown-rough band around every OSM fairway, per hole side, with trees, water, sand and fairway drawn over it. Sentinel-2 was NOT used to draw it (it is what the native model is scored against). OB not traced (none drawn).

Native on both sides of most holes (the golfer's description), beyond a mown rough 8-15 yds wide (taken as 12). Holes with no native traced: 2, 6, 9 (trees / mown both sides; 6 left is a hayfield off the course).

## Uncertain items

| hole | item |
|---|---|
| 1 | native right only (tall grass on the creek bank under trees) |
| 4 | left = hayed native with windrows (2023); right = tall grass round the pond to 270 yds |
| 8 10 | narrow bands before the wetlands; 10 left is the wetland fringe |
| 15 | houses right beyond ~290: native stopped at 290, OB not drawn |
| all | mown-rough width 12 yds everywhere (8 on 4 right, 8, 10 left): +/-6 yds |
