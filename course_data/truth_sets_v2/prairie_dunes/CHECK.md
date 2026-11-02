# Prairie Dunes Country Club (Hutchinson, KS): truth v2 check (native-grass set)

Card: package card (`course_data/packages/prairie_dunes/package.json` tee_sets). Corridor set **Blue** (the package's set).

**Confidence: medium (routing, greens, trees, fairway); medium long-grass edges (+/-4 yds); OB not traced.**

How it was checked: routing = `draft_spec.py --package-lines` from the OSM golf=hole ways (package hole lines where OSM has none), greens = OSM outlines, tees = OSM tee boxes measured against the card (`build_holes_truth.py`; `*` = a box within 8 yds of the card length, else estimated along the line). The routing was viewed on the whole-course map only (no per-hole tee sheets). Corridors: every par-4/5 tee shot's 130-420 yd footprint; trees = 3DEP lidar canopy > 2.5 m when the raw stack is present (NAIP crowns otherwise), fairway / water / sand = OSM. **Native / long grass is the point of this course** (s2_longgrass.md 'Enlarged native set'): traced by eye on the corridor photos (NAIP 2023 0.3 m unless said), as the unmown ground beyond the mown-rough band around every OSM fairway, per hole side, with trees, water, sand and fairway drawn over it. Sentinel-2 was NOT used to draw it (it is what the native model is scored against). OB not traced (none drawn).

Links / dune course: grey-green textured native prairie with plum thickets on both sides of every par-4/5 fairway, 4-8 yds off the mown edge (taken as 6). Trees (cottonwoods, thickets) drawn over it.

## Uncertain items

| hole | item |
|---|---|
| 1 | clubhouse / practice ground left short of 300: no native there |
| all | native edge = fairway + 6 yds: +/-4 yds; mown paths through the native not cut out |
