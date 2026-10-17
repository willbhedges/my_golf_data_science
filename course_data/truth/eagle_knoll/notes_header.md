# Eagle Knoll Golf Club (Hartsburg, MO): hand-checked truth

NCCGA Regional 2 (Nov 7-8 2026). Wooded, hilly parkland in the Missouri River bluffs. Card (golfify = OpenGolfAPI):
Eagle/gold 6920 (73.8/141), **Back/blue 6667 (72.8/134, the likely NCCGA set: the NCCGA played the blue tees here
in 2015 and 2025)**, Middle/white 6186, Forward/red 5174; par 72 (4 3 4 4 4 3 5 4 5 / 4 4 3 5 4 4 3 5 4).

Files: `holes_truth.json` (from `holes_truth.py`: hole number, par, card per set, tee per set, green; per-hole notes),
`trace.py` -> `hand_zones_ll.json` (landing corridors of the 14 par 4/5 tee shots from the Back tee, 145-345 yds x
+/-65), `render/` (NAIP 2022 photo, CIR, NAIP 2012-2022, lidar canopy), `review/` (trace over every layer).

## Method

* Hole numbers: the OSM hole ways give a continuous routing on the ground and every Back length matches the card
  within 2% -> numbering correct on all 18. Greens: every OSM outline sits on the visible green (18/18).
* Tees: the package's pad per set kept when it sits on an OSM / visible pad and measures within 8 yds of the card;
  otherwise moved along the line to the card ('estimated': Eagle 7, 18; Forward 17, 18).
* Corridors: start layers OSM fairway / bunker / water + 3DEP lidar canopy > 2.5 m (`course_data/truth/assist.py`),
  each checked against the 2022 photo, CIR and NAIP 2012-2020; added by hand: long grass on 9 and 11, OB on 18
  (house lots), the grown right tree line on 10; checked and left as rough: the mounds left of 1, the tan areas of
  NAIP 2020 on 4 / 8 (2020 is a dry year everywhere, mown in every other year).
* No OB in the corridor on 3 although the OSM course outline crosses the ravine woods (no lots / fence there).
* Second pass: every hazard edge within 10 yds of the fairway (list below per hole) was re-checked on 5-6 px/yd zooms
  (photo + lidar edge, CIR, NAIP 2020): edges agree within 2-3 yds except 10 right (crowns 3-8 yds past the 2015
  lidar edge: corrected).

## Elevation (3DEP 1 m DEM)

Driver landing area vs tee (ft, + = below): 1 +61, 3 -6, 4 +23, 5 +29, 7 -30, 8 -19, 9 +14, 10 +26, 11 -12, 13 +28,
14 +24, 15 +25, 17 -5, 18 -12. Par-3 greens vs tee: 2 60 ft below (plays ~17 yds shorter), 6 47 ft below (~13
shorter), 12 12 ft below (~3), 16 39 ft below (~11).
