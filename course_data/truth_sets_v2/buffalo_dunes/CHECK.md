# Buffalo Dunes Golf Course (Garden City, KS): truth v2 check (native-grass set)

Card: package card (`course_data/packages/buffalo_dunes/package.json` tee_sets). Corridor set **Blue** (the package's set).

**Confidence: medium (routing, greens, trees, fairway, water); medium long-grass edges (+/-5 yds); OB not traced.**

How it was checked: routing = `draft_spec.py --package-lines` from the OSM golf=hole ways (package hole lines where OSM has none), greens = OSM outlines, tees = OSM tee boxes measured against the card (`build_holes_truth.py`; `*` = a box within 8 yds of the card length, else estimated along the line). The routing was viewed on the whole-course map only (no per-hole tee sheets). Corridors: every par-4/5 tee shot's 130-420 yd footprint; trees = 3DEP lidar canopy > 2.5 m when the raw stack is present (NAIP crowns otherwise), fairway / water / sand = OSM. **Native / long grass is the point of this course** (s2_longgrass.md 'Enlarged native set'): traced by eye on the corridor photos (NAIP 2023 0.3 m unless said), as the unmown ground beyond the mown-rough band around every OSM fairway, per hole side, with trees, water, sand and fairway drawn over it. Sentinel-2 was NOT used to draw it (it is what the native model is scored against). OB not traced (none drawn).

Sandhill prairie (tan textured native) between all fairways, beyond a mown rough ~10 yds wide. Trees drawn over it.

## Uncertain items

| hole | item |
|---|---|
| 10 | maintenance yard right short of 240: excluded |
| 14 | dirt lot right short of 250: excluded |
| 18 | left: hayed native with windrows (2023), kept as native |
| 6 | Blue tee (re-checked 2026-11-03) | moved by hand to the back end of the long mapped box (389 yds vs card 400); the estimate was 9 yds behind it in native grass. |
| 11 | Blue tee (re-checked 2026-11-03) | **moved by hand to the back end of the mapped box: 380 yds vs card 423** (medium confidence). The +55 estimate is rough beside a cart path and trees next to the previous green: no box in NAIP 2021 / 2023, no lidar pad. |
