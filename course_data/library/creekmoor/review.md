# Creekmoor: course check (rv12)

**Verdict: NOT safe to publish.** The page has 15 of 18 holes (1, 12 and 17 are missing). Of those 15, holes 8, 9, 10 and 16 are routed across subdivisions, with tees on lidar pads among the houses.

Card: golfify, Black 7406 / Green 6806, par 72. The OSM tee rows confirm it on every hole I could test (OpenGolfAPI differs on Black 6, Black 9, Green 9 and Green 12; golfify fits the tees).

| verdict | holes |
|---|---|
| OK | 2, 4, 5, 6, 7, 11, 14, 15, 18 (the aim/oval CHECKs on these come from OSM mapping no fairways, not from a bad line) |
| fixed (osm_supplement) | 12 (tees way/1490361208-12 -> green 1490361213), 17 (tees 1490357722-26 -> green 1490357729); both are exact yardage fits |
| bad pick | 3: the straight tee-to-green line crosses houses. The hole doglegs left, so the line needs a bend point; Driver -40 lands in OB |
| wrong routing, unresolved | 1 (no tee), 8, 9, 10, 16 |
| wrong tee / uncertain | 13: Green/White/Red tees sit on lidar pads in the woods. The OSM row 1214-17 fits green way/1490361220 to the north instead |

Lead for 8: the E-W OSM tee row at lat 38.8333 fits green way/1490350625 (the green the page uses for 16) at 413/357/301 yds, vs card 409/365/305. If that holds, 9 and 16 need new greens and tees.

`osm_supplement.geojson` carries golf=hole ways for the 9 confirmed holes plus 12 and 17. A rebuild with it should get to 17 holes at best; 1, 3, 8, 9, 10, 13 and 16 need a mapper with full-course imagery.
