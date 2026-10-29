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

## Per tee shot

### 1 (par 4, Back 366 yds; tee: tee_axis)

Confidence: high. Zones: recovery 6, fairway 3, sand 1.

Fairway (OSM) 140-270 then the hole turns left between tree lines: trees right from 220 (lidar edge = 2022 photo), trees left 240-300 (x < -45), one tree left at 150. Bunker left 225. The mounded rough left of the fairway (150-240) is mown in every year: rough.

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150L recovery 7 yds out; 160L recovery 8 yds out; 230L sand 8 yds out; 280R recovery 0 yds out; 290R recovery 0 yds out; 300L recovery 6 yds out; 300R recovery 6 yds out; 310L recovery 4 yds out.

Review: `review/h01.png`; evidence: `render/h01_evidence.png`.

### 3 (par 4, Back 397 yds; tee: tee_centroid)

Confidence: high. Zones: recovery 3, fairway 1, water 1, sand 4.

Forced carry over the ravine woods / pond to a fairway that starts ~185, is widest left at 200-270 and turns right to the green; woods left all the way (rough strip 7-15 yds). The OSM course outline crosses the ravine: not OB on the ground (no fence, no houses; woods continue), so no OB in the corridor.

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; water: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 200L recovery 10 yds out; 210L recovery 8 yds out; 220L recovery 0 yds out; 220R sand 2 yds out.

Review: `review/h03.png`; evidence: `render/h03_evidence.png`.

### 4 (par 4, Back 399 yds; tee: tee_axis)

Confidence: high. Zones: recovery 4, fairway 2, sand 4.

Fairway (OSM) 180-345 x -15..+15; woods left 20-30 yds off; hole 8's fairway right (fairway lie). The tan band right of the cart path in NAIP 2020 is dry mown rough (2020 is a dry year everywhere).

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo.

No hazard within 10 yds of the fairway edge.

Review: `review/h04.png`; evidence: `render/h04_evidence.png`.

### 5 (par 4, Back 465 yds; tee: tee_centroid)

Confidence: high. Zones: recovery 8, fairway 1, sand 1.

Tree-lined: woods right 0-10 yds off the fairway edge the whole corridor (lidar edge matches 2022), open rough + cart path left to the trees at x -35..-45. Bunker right 245.

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; recovery: left woods beyond the cart path at 145-262: continuous canopy from x -38 in NAIP 2020 / 2022 and CIR (the 2015 lidar has only scattered crowns > 2.5 m there: grown since).

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 160R recovery 6 yds out; 170R recovery 6 yds out; 180R recovery 6 yds out; 190R recovery 6 yds out; 200R recovery 5 yds out; 210R recovery 8 yds out; 220R recovery 8 yds out; 240R sand 10 yds out; 250R sand 5 yds out; 260R sand 8 yds out; 290R recovery 8 yds out; 300R recovery 6 yds out; 320R recovery 10 yds out; 330R recovery 6 yds out; 340R recovery 8 yds out.

Review: `review/h05.png`; evidence: `render/h05_evidence.png`.

### 7 (par 5, Back 475 yds; tee: tee_axis)

Confidence: high. Zones: recovery 3, fairway 2, water 1.

Woods right at the fairway edge (x +12..+25); hole 13's parallel fairway left beyond the cart path (fairway lie).

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; water: OSM polygon, checked on the photo.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150R recovery 6 yds out; 160R recovery 8 yds out; 180R recovery 0 yds out; 190R recovery 3 yds out; 200R recovery 6 yds out; 210R recovery 8 yds out; 230R recovery 4 yds out; 240R recovery 6 yds out; 250R recovery 10 yds out; 260R recovery 2 yds out; 270R recovery 6 yds out; 280R recovery 3 yds out; 290R recovery 10 yds out; 320R recovery 0 yds out; 330R recovery 2 yds out.

Review: `review/h07.png`; evidence: `render/h07_evidence.png`.

### 8 (par 4, Back 407 yds; tee: tee_axis)

Confidence: high. Zones: recovery 4, fairway 2, sand 4.

Bunkers left 255 / right 205 (OSM = photo); trees left 140-220; hole 4's fairway right. The tan upper-left area in NAIP 2020 is dry rough (mown in 2012-2018 and 2022).

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 160L recovery 6 yds out; 160R recovery 8 yds out; 170L recovery 0 yds out; 170R recovery 2 yds out; 180L recovery 4 yds out; 190L recovery 0 yds out; 200L recovery 4 yds out; 200R sand 0 yds out; 210L recovery 4 yds out; 210R sand 0 yds out; 220R sand 0 yds out; 250L sand 0 yds out; 260L sand 0 yds out; 270L sand 2 yds out.

Review: `review/h08.png`; evidence: `render/h08_evidence.png`.

### 9 (par 5, Back 510 yds; tee: tee_axis)

Confidence: medium (long-grass extent right). Zones: native 1, recovery 8, fairway 2, sand 5.

Two overlapping OSM fairway polygons (= the mown fairway). Right beyond the cart path at 280+: unmown grass (dark green 2022, tan 2020, bright CIR, no lidar height) = long grass. Trees right 150-280.

Zone notes: native: unmown grass right of the cart path; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; recovery: crown over the cart path right at 250-275 (NAIP 2020 / 2022, CIR; past the 2015 lidar edge); recovery: right woods at 148-200 filled in since 2015 (continuous canopy from x +28 in NAIP 2020 / 2022).

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 180R recovery 4 yds out; 260L sand 4 yds out; 260R recovery 0 yds out; 270L sand 5 yds out; 270R recovery 0 yds out; 290L sand 6 yds out.

Review: `review/h09.png`; evidence: `render/h09_evidence.png`.

### 10 (par 4, Back 405 yds; tee: tee_centroid)

Confidence: high. Zones: recovery 6, fairway 2, sand 3.

Chute: trees right at the fairway edge (x +8..+15) the whole corridor; trees left from 260, open rough with trees beyond left before that.

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; recovery: right tree line: 2020 / 2022 crowns reach x +20..+24 (2015 lidar edge +22..+37 at 170-180).

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150R recovery 4 yds out; 160R recovery 4 yds out; 170L recovery 6 yds out; 170R recovery 4 yds out; 180L recovery 9 yds out; 180R recovery 4 yds out; 190R recovery 4 yds out; 200R recovery 2 yds out; 210R recovery 2 yds out; 220R recovery 0 yds out; 230R recovery 0 yds out; 240R recovery 0 yds out; 250L recovery 9 yds out; 250R recovery 2 yds out; 260R recovery 4 yds out; 270R recovery 9 yds out; 280L recovery 4 yds out; 280R recovery 2 yds out; 290L recovery 9 yds out; 290R recovery 0 yds out; 300L recovery 3 yds out; 300R recovery 0 yds out; 310L recovery 4 yds out; 310R recovery 0 yds out; 320L recovery 6 yds out; 320R recovery 0 yds out; 330L recovery 5 yds out; 330R recovery 2 yds out; 340R recovery 1 yds out.

Review: `review/h10.png`; evidence: `render/h10_evidence.png`.

### 11 (par 4, Back 441 yds; tee: tee_axis)

Confidence: medium (long-grass strip edges +/-5). Zones: native 1, recovery 5, fairway 2, sand 2.

Doglegs right. Left: a strip of unmown grass (x -70..-42, 175-305; dark in 2012-2022 NAIP, bright CIR, no lidar height) beyond mown rough; trees right 230-280 beyond the cart path.

Zone notes: native: unmown grass strip left; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo.

No hazard within 10 yds of the fairway edge.

Review: `review/h11.png`; evidence: `render/h11_evidence.png`.

### 13 (par 5, Back 546 yds; tee: tee_axis)

Confidence: high. Zones: recovery 5, fairway 2.

Fairway drifts right of the tee line (x -15..+5 at 150 to +5..+45 at 340); hole 7's fairway left (fairway lie); trees right beyond the cart path.

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150L recovery 2 yds out; 330L recovery 4 yds out; 340L recovery 5 yds out.

Review: `review/h13.png`; evidence: `render/h13_evidence.png`.

### 14 (par 4, Back 265 yds; tee: tee_axis)

Confidence: high. Zones: recovery 6, fairway 3, water 1.

Short par 4: fairway to ~210, pond 200-260 across the line (OSM = CIR water), green surround beyond; woods both sides. Lay up or carry ~265.

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; water: OSM polygon, checked on the photo.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 180R recovery 2 yds out; 250L recovery 7 yds out; 250R water 8 yds out; 260L recovery 6 yds out; 260R water 8 yds out; 270L recovery 10 yds out; 290R recovery 8 yds out.

Review: `review/h14.png`; evidence: `render/h14_evidence.png`.

### 15 (par 4, Back 447 yds; tee: tee_axis)

Confidence: high. Zones: recovery 2, fairway 2, water 1.

Chute bending left: woods both sides, the right tree line 5-12 yds off the fairway.

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; water: OSM polygon, checked on the photo.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150L recovery 3 yds out; 160L recovery 3 yds out; 170L recovery 10 yds out; 180L recovery 6 yds out; 190L recovery 10 yds out; 190R recovery 10 yds out; 200L recovery 9 yds out; 200R recovery 10 yds out; 210R recovery 5 yds out; 220L recovery 9 yds out; 220R recovery 8 yds out; 230R recovery 4 yds out; 240L recovery 9 yds out; 240R recovery 2 yds out; 250L recovery 4 yds out; 250R recovery 0 yds out; 260L recovery 7 yds out; 260R recovery 4 yds out; 270L recovery 2 yds out; 270R recovery 5 yds out; 280R recovery 0 yds out; 290L recovery 6 yds out; 290R recovery 0 yds out; 300L recovery 10 yds out; 300R recovery 2 yds out; 310L recovery 4 yds out; 310R recovery 0 yds out; 320L recovery 7 yds out; 320R recovery 4 yds out; 330L recovery 2 yds out; 330R recovery 0 yds out; 340R recovery 0 yds out.

Review: `review/h15.png`; evidence: `render/h15_evidence.png`.

### 17 (par 5, Back 489 yds; tee: tee_axis)

Confidence: medium (creek width where it is grassed). Zones: recovery 2, fairway 3, water 4.

Creek (OSM water hazard, a wooded / grassed drainage) left 140-240 then crossing diagonally 250-345 between the first fairway and the second; woods right beyond the cart path.

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; water: OSM polygon, checked on the photo; water: OSM polygon, checked on the photo; water: OSM polygon, checked on the photo; water: OSM polygon, checked on the photo.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150L recovery 6 yds out; 160L recovery 8 yds out; 160R recovery 10 yds out; 170R recovery 8 yds out; 180L recovery 8 yds out; 180R recovery 6 yds out; 190L recovery 6 yds out; 190R recovery 9 yds out; 200L recovery 6 yds out; 200R recovery 3 yds out; 210L recovery 6 yds out; 210R recovery 7 yds out; 250L water 4 yds out; 250R recovery 8 yds out; 260L recovery 0 yds out; 260R water 0 yds out; 270L recovery 0 yds out; 270R water 2 yds out; 280L recovery 0 yds out; 280R water 2 yds out; 290L recovery 1 yds out; 290R water 3 yds out; 300L recovery 0 yds out; 300R water 3 yds out; 310L recovery 0 yds out; 310R water 2 yds out; 320L recovery 0 yds out; 320R water 2 yds out; 330L recovery 0 yds out; 330R water 0 yds out; 340L recovery 0 yds out; 340R water 4 yds out.

Review: `review/h17.png`; evidence: `render/h17_evidence.png`.

### 18 (par 4, Back 428 yds; tee: tee_axis)

Confidence: medium (OB line +/-8: no stakes visible). Zones: ob 2, recovery 10, fairway 2.

Trees right 240-340 beyond the cart path, trees left 140-220; a row of houses left: their back yards (houses ~65-100 yds left, yards ~25 yds) end ~45-70 yds left of the line: OB there (the OSM course outline runs 10-20 yds inside the yards).

Zone notes: ob: house lots left: footprints + 25 yds of back yard (no fence / stakes visible; the OSM outline runs 10-20 yds inside the yards); ob: house lots left: footprints + 25 yds of back yard (no fence / stakes visible; the OSM outline runs 10-20 yds inside the yards); recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150L recovery 8 yds out; 180L recovery 8 yds out; 190R recovery 6 yds out; 210L recovery 6 yds out; 220L recovery 3 yds out; 260R recovery 2 yds out; 300R recovery 4 yds out; 310R recovery 6 yds out; 320R recovery 3 yds out.

Review: `review/h18.png`; evidence: `render/h18_evidence.png`.

