# Coldwater Golf Links (Ames, IA): hand-checked landing corridors

Independent truth for the any-course scoreboard: the **open / links-style** course of the three (Veenker is
parkland, Wakonda wooded). 14 tee shots (every par 4 / 5) from the **Blue** tees (6406 yds; middle-back of the
card's Black / Blue / White / Red; the package's set). Corridor 150-340 yds along the package's Blue tee line,
+/-60 yds (mapped footprint 145-345 x +/-65). Files as for Veenker: `trace.py`, `hand_zones_ll.json`, `render/`
(NAIP 2023 0.3 m photo, CIR, every other NAIP year at 1 m, lidar canopy, lidar low-vegetation share), `review/`.

## Method (as Veenker; differences)

* Long grass is the main hazard here. Unmown fescue / prairie = tufted, coarse texture in the 0.3 m photo, tan
  in NAIP 2021 (dry year) and pale grey-blue speckled in CIR (no irrigation), and unmown in several NAIP years.
  Mown rough that is merely dry (tan but smooth, mower stripes) is rough - this is the main judgement call
  (holes 6, 15, 18: wide tan mown rough beside the fairway).
* Fairway = the striped mown turf; fairway edges against same-colour mown rough are soft in 2023 (+/-3-4 yds on
  4, 13). No separate first cut is visible on this course.
* Trees only on 2, 7, 14, 15 (woods / belts, lidar crown edge) and a few in the prairie of 10.
* Water: ponds / lakes (1, 9), and three drainage ditches / creeks with shrubs (12, 17, 18) mapped as water
  (penalty areas) along the dark linear channels that every NAIP year shows.
* OB: the condominiums left of 1 and the mobile-home park left of 4, 6, 7 (property line at the shrub row /
  park road).
* Second pass on every hazard edge within 10 yds of the fairway on 6-7 px/yd zooms: moved the native edge on 10
  (4 yds out: a mown strip between fairway and prairie), on 3 (+2 yds) and the left prairie strip on 2 (to the
  cart paths that bound it).

## Ambiguities (overall)

* Dry mown rough vs fescue (6, 15, 18 right): rough where mower stripes / smooth texture are visible.
* Hole 1 left fescue: green in NAIP 2014-2017, tan and tufted 2019-2023 (let grow in the last years): native.
* Hole 12 creek: the inner rock line is the edge (+/-3 yds); the lidar no-return patch right of it is wet tall
  grass, not open water.
* Ditch widths on 17, 18 (+/-3 yds); the shrubs along them are mapped as part of the water / native.
