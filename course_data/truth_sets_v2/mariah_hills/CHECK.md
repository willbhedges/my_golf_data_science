# Mariah Hills Golf Course (Dodge City, KS): truth v2 check (native-grass set)

Card: package card (`course_data/packages/mariah_hills/package.json` tee_sets). Corridor set **Blue** (the package's set).

**Confidence: medium-low (routing from the package's hole lines: OSM has no golf=hole ways; greens OSM); native islands +/-10 yds.**

How it was checked: routing = `draft_spec.py --package-lines` from the OSM golf=hole ways (package hole lines where OSM has none), greens = OSM outlines, tees = OSM tee boxes measured against the card (`build_holes_truth.py`; `*` = a box within 8 yds of the card length, else estimated along the line). The routing was viewed on the whole-course map only (no per-hole tee sheets). Corridors: every par-4/5 tee shot's 130-420 yd footprint; trees = 3DEP lidar canopy > 2.5 m when the raw stack is present (NAIP crowns otherwise), fairway / water / sand = OSM. **Native / long grass is the point of this course** (s2_longgrass.md 'Enlarged native set'): traced by eye on the corridor photos (NAIP 2023 0.3 m unless said), as the unmown ground beyond the mown-rough band around every OSM fairway, per hole side, with trees, water, sand and fairway drawn over it. Sentinel-2 was NOT used to draw it (it is what the native model is scored against). OB not traced (none drawn).

Native comes as distinct textured islands between the holes (not continuous bands), each drawn as an ellipse or box read off the corridor photo grid (+/-10 yds). Everything else unzoned = mown rough.

## Uncertain items

| hole | item |
|---|---|
| all | routing = package hole lines (no OSM holes): checked only on the whole-course map |
| 7 | large island in the carry zone of the dogleg |
| all | island outlines +/-10 yds |
