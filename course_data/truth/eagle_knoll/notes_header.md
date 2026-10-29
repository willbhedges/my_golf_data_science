# Eagle Knoll Golf Club (Hartsburg, MO): hand-checked truth

NCCGA Central Regional Tournament 2 (Sat-Sun Nov 7-8 2026, 9:00 am both days; tee sheet not posted yet). Wooded,
hilly parkland in the Missouri River bluffs. Card (golfify = OpenGolfAPI = the NCCGA 2015 tee sheet):
Eagle/gold 6920 (73.8/141), **Back/blue 6667 (72.8/134, the likely NCCGA set: the NCCGA tee sheets list "Tee Marker:
Blue" here in Fall 2015 (6682, shotgun) and Fall 2024 (6512 as set up that day, 72.7/131, tee times off 1))**,
Middle/white 6186 (70.8/130), Forward/red 5174; par 72 (4 3 4 4 4 3 5 4 5 / 4 4 3 5 4 4 3 5 4). Back, Eagle and
Middle are each solved as full base sets on the wind page.

Files: `holes_truth.json` (from `holes_truth.py`: hole number, par, card per set, tee per set, green, hole line,
reference frame; per-hole notes), `trace.py` -> `hand_zones_ll.json` (landing corridors of the 14 par 4/5 tee shots
from the Back tee, 145-440 yds x +/-65: extended past 345 so that the Middle tees, up to 85 yds ahead, stay on the
hand map), `render/` (NAIP 2022 photo, CIR, NAIP 2012-2022, lidar canopy), `review/` (trace over every layer),
`recheck/` (course_data/truth/recheck.py on NAIP 2020: tees per set vs the card, landing zones with the lidar edge,
whole holes with each set's tee line, par-3 greens).

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
* Third pass (Oct 29 2026, `recheck/`): the sharpest NAIP year over the course was scanned for (every year on
  Planetary Computer, sharpness on a common 0.3 m grid: `course_data/imagery/years/eagle_knoll_display.json`). No
  0.3 m year exists here (Planetary Computer stops at 2022, 0.6 m; the MSDIS and USDA APFO services are not reachable
  from the runners); NAIP 2020 (0.6 m, Jul 8) is about twice as sharp as 2022 (Jun 20, soft / hazy) and is the page
  photo. **Lidar date: 3DEP 2015 (leaf-off), 11 years old.** Every landing zone (Back 130-440) re-checked on NAIP 2020
  + CIR and 2022 with the lidar 2.5 m edge: trees grown in since 2015 added on 5 (left woods beyond the cart path at
  145-262: the lidar had only scattered crowns) and 9 (a crown over the cart path right at 250-275; right woods
  filled in at 148-200); no crowns gone. Other edges agree within ~3 yds.
* Tees, third pass: measured with the card convention (tees/place_tee.LineOfPlay: straight to the next turning point,
  then along the line). Back 4 was on the front edge of the Eagle pad (+7): moved to its own OSM pad 7-20 yds ahead
  (-0.5). Every Back, Eagle and Middle tee is now within 5.4 yds of the card on a mapped pad (Back 1 and Eagle 1 -4,
  Back / Eagle 14 -5 and Eagle 17 -5 at the back edge of their pads); Eagle 7 and 18 stay estimated (no separate
  box visible under the trees; the pad tee moved back along the line to the card).
* Doglegs: the OSM hole lines bend at the fairway (1 left at ~225, 3 right at ~270, 11 right, 15 left, 17 at the
  creek); the 250-yd tee-line point of Back and Eagle sits in the fairway on every hole and the quick-plan aims stay
  within +/-15 yds of the tee line for Eagle and +/-30 for Back (1: -30), well inside the engine's +/-40 search.

## Elevation (3DEP 1 m DEM)

Driver landing area vs tee (ft, + = below): 1 +61, 3 -6, 4 +23, 5 +29, 7 -30, 8 -19, 9 +14, 10 +26, 11 -12, 13 +28,
14 +24, 15 +25, 17 -5, 18 -12. Par-3 greens vs tee: 2 60 ft below (plays ~17 yds shorter), 6 47 ft below (~13
shorter), 12 12 ft below (~3), 16 39 ft below (~11).
