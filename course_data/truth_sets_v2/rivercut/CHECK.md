# Rivercut (Springfield, MO): truth v2 check

Card: from the package (golfify / AllSquare / OpenGolfAPI; Black 7,066 / Blue 6,536 / White 6,019 / Red 5,483, par 72;
16 Black 316 = AllSquare / OpenGolfAPI, golfify 345). Corridor set **Black** (14 tee shots). Lidar: MO_FEMANRCS_1_2020.

**Confidence: high for routing / greens / tees (OSM maps a box per set) / trees / fairway; medium for OB (house lots)
and water edges on 8 / 9.**

How it was checked: routing = the OSM golf=hole ways (draft_spec), greens = OSM outlines, all 18 greens agree with the reviewed library package (within 15 yds) and the library review checked routing on the page screenshots; pars = card; whole-course routing map viewed; tee areas zoomed (3 px/yd) on every hole where the corridor-set tee is estimated by more than ~20 yds. Corridors: every par-4/5 tee shot viewed as photo + zones | photo | lidar HAG at ~1.6 px/yd; OB candidates (OSM course outline / house-lot rule) kept only where the photo shows houses, a road or a fence line, otherwise dropped (woods stay trees). "est" = tee moved along the line to the card length because no OSM box measures within 8 yds (no box visible there in NAIP at 0.6 m unless said).

Hand corrections: 9 the OSM water right of the fairway was 10-15 yds left of the channel / pond (CIR, no lidar
returns): redrawn; 18 the house-lot rule closed across the fairway: right side drawn by hand (houses beyond the
trees, 290-420 yds), left = OSM outline.

## Uncertain items

| hole | item | what |
|---|---|---|
| 2 10 11 13 15 18 | Black tee | estimated 9-14 yds behind the Blue box (OSM boxes shared by Black / Blue: the back end of the box). |
| 16 | card | Black 316 used (golfify 345); OSM way 309-312. |
| 3 10 11 12 13 14 16 | OB | house lots (building footprints + 25 yds), not stake lines: +/-10 yds. |
| 4 5 | OB (not drawn) | outline runs along the creek / trees left: water + trees drawn instead. |
| 8 | water | OSM strip right (x +15..+25, 140-260) is a narrow dry-looking channel in NAIP: kept as water at OSM width. |
| 9 | water | redrawn channel / pond edge from CIR + lidar: +/-5 yds. |
| all | long grass | none seen in landing zones. |
