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

## Per tee shot

### 1 (par 4, Back 366 yds; tee: tee_axis)

Confidence: high. Zones: recovery 3, fairway 2, sand 1.

Fairway (OSM) 140-270 then the hole turns left between tree lines: trees right from 220 (lidar edge = 2022 photo), trees left 240-300 (x < -45), one tree left at 150. Bunker left 225. The mounded rough left of the fairway (150-240) is mown in every year: rough.

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150L recovery 7 yds out; 160L recovery 8 yds out; 230L sand 8 yds out; 280R recovery 0 yds out; 290R recovery 0 yds out; 300L recovery 6 yds out; 300R recovery 5 yds out; 310L recovery 5 yds out.

Review: `review/h01.png`; evidence: `render/h01_evidence.png`.

### 3 (par 4, Back 397 yds; tee: tee_centroid)

Confidence: high. Zones: recovery 3, fairway 1, water 1, sand 1.

Forced carry over the ravine woods / pond to a fairway that starts ~185 and bends left; woods left all the way (rough strip 7-15 yds). The OSM course outline crosses the ravine: not OB on the ground (no fence, no houses; woods continue), so no OB in the corridor.

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; water: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 200L recovery 10 yds out; 210L recovery 7 yds out; 220L recovery 2 yds out; 220R sand 2 yds out.

Review: `review/h03.png`; evidence: `render/h03_evidence.png`.

### 4 (par 4, Back 399 yds; tee: tee_axis)

Confidence: high. Zones: recovery 1, fairway 2, sand 3.

Fairway (OSM) 180-345 x -15..+15; woods left 20-30 yds off; hole 8's fairway right (fairway lie). The tan band right of the cart path in NAIP 2020 is dry mown rough (2020 is a dry year everywhere).

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo.

No hazard within 10 yds of the fairway edge.

Review: `review/h04.png`; evidence: `render/h04_evidence.png`.

### 5 (par 4, Back 465 yds; tee: tee_centroid)

Confidence: high. Zones: recovery 6, fairway 1, sand 1.

Tree-lined: woods right 0-10 yds off the fairway edge the whole corridor (lidar edge matches 2022), open rough + cart path left to the trees at x -35..-45. Bunker right 245.

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 160R recovery 6 yds out; 170R recovery 6 yds out; 180R recovery 6 yds out; 190R recovery 6 yds out; 200R recovery 5 yds out; 210R recovery 8 yds out; 220R recovery 9 yds out; 240R sand 10 yds out; 250R sand 5 yds out; 260R sand 8 yds out; 290R recovery 9 yds out; 300R recovery 8 yds out; 320R recovery 9 yds out; 330R recovery 10 yds out; 340R recovery 10 yds out.

Review: `review/h05.png`; evidence: `render/h05_evidence.png`.

### 7 (par 5, Back 475 yds; tee: tee_axis)

Confidence: high. Zones: recovery 1, fairway 2, water 1.

Woods right at the fairway edge (x +12..+25); hole 13's parallel fairway left beyond the cart path (fairway lie).

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; water: OSM polygon, checked on the photo.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150R recovery 6 yds out; 160R recovery 8 yds out; 180R recovery 0 yds out; 190R recovery 3 yds out; 200R recovery 6 yds out; 210R recovery 8 yds out; 230R recovery 4 yds out; 240R recovery 6 yds out; 250R recovery 10 yds out; 260R recovery 2 yds out; 270R recovery 4 yds out; 280R recovery 2 yds out; 290R recovery 10 yds out; 320R recovery 0 yds out.

Review: `review/h07.png`; evidence: `render/h07_evidence.png`.

### 8 (par 4, Back 407 yds; tee: tee_axis)

Confidence: high. Zones: recovery 3, fairway 2, sand 2.

Bunkers left 255 / right 205 (OSM = photo); trees left 140-220; hole 4's fairway right. The tan upper-left area in NAIP 2020 is dry rough (mown in 2012-2018 and 2022).

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 160L recovery 6 yds out; 160R recovery 8 yds out; 170L recovery 0 yds out; 180L recovery 5 yds out; 190L recovery 0 yds out; 200L recovery 4 yds out; 200R sand 0 yds out; 210L recovery 4 yds out; 210R sand 0 yds out; 220R sand 0 yds out; 250L sand 0 yds out; 260L sand 0 yds out; 270L sand 2 yds out.

Review: `review/h08.png`; evidence: `render/h08_evidence.png`.

### 9 (par 5, Back 510 yds; tee: tee_axis)

Confidence: medium (long-grass extent right). Zones: native 1, recovery 5, fairway 2, sand 4.

Two overlapping OSM fairway polygons (= the mown fairway). Right beyond the cart path at 280+: unmown grass (dark green 2022, tan 2020, bright CIR, no lidar height) = long grass. Trees right 150-280.

Zone notes: native: unmown grass right of the cart path; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo; sand: OSM polygon, checked on the photo.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 180R recovery 4 yds out; 260L sand 4 yds out; 270L sand 5 yds out; 290L sand 6 yds out.

Review: `review/h09.png`; evidence: `render/h09_evidence.png`.

### 10 (par 4, Back 405 yds; tee: tee_centroid)

Confidence: high. Zones: recovery 4, fairway 2.

Chute: trees right at the fairway edge (x +8..+15) the whole corridor; trees left from 260, open rough with trees beyond left before that.

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; recovery: right tree line: 2020 / 2022 crowns reach x +20..+24 (2015 lidar edge +22..+37 at 170-180).

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150R recovery 4 yds out; 160R recovery 4 yds out; 170L recovery 6 yds out; 170R recovery 4 yds out; 180R recovery 4 yds out; 190R recovery 4 yds out; 200R recovery 2 yds out; 210R recovery 2 yds out; 220R recovery 0 yds out; 230R recovery 0 yds out; 240R recovery 0 yds out; 250L recovery 10 yds out; 250R recovery 2 yds out; 260R recovery 4 yds out; 270L recovery 8 yds out; 270R recovery 8 yds out; 280L recovery 4 yds out; 280R recovery 2 yds out; 290R recovery 0 yds out; 300L recovery 2 yds out; 300R recovery 0 yds out; 310L recovery 4 yds out; 310R recovery 0 yds out; 320L recovery 6 yds out; 320R recovery 0 yds out; 330L recovery 4 yds out; 330R recovery 0 yds out; 340R recovery 3 yds out.

Review: `review/h10.png`; evidence: `render/h10_evidence.png`.

### 11 (par 4, Back 441 yds; tee: tee_axis)

Confidence: medium (long-grass strip edges +/-5). Zones: native 1, recovery 5, fairway 2.

Doglegs right. Left: a strip of unmown grass (x -70..-42, 175-305; dark in 2012-2022 NAIP, bright CIR, no lidar height) beyond mown rough; trees right 230-280 beyond the cart path.

Zone notes: native: unmown grass strip left; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo.

No hazard within 10 yds of the fairway edge.

Review: `review/h11.png`; evidence: `render/h11_evidence.png`.

### 13 (par 5, Back 546 yds; tee: tee_axis)

Confidence: high. Zones: recovery 3, fairway 2.

Fairway drifts right of the tee line (x -15..+5 at 150 to +5..+45 at 340); hole 7's fairway left (fairway lie); trees right beyond the cart path.

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150L recovery 2 yds out; 330L recovery 3 yds out; 340L recovery 4 yds out.

Review: `review/h13.png`; evidence: `render/h13_evidence.png`.

### 14 (par 4, Back 265 yds; tee: tee_axis)

Confidence: high. Zones: recovery 4, fairway 3, water 1.

Short par 4: fairway to ~210, pond 200-260 across the line (OSM = CIR water), green surround beyond; woods both sides. Lay up or carry ~265.

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; water: OSM polygon, checked on the photo.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 180R recovery 2 yds out; 250L recovery 6 yds out; 250R water 8 yds out; 260L recovery 6 yds out; 260R water 8 yds out; 270L recovery 10 yds out; 290R recovery 10 yds out.

Review: `review/h14.png`; evidence: `render/h14_evidence.png`.

### 15 (par 4, Back 447 yds; tee: tee_axis)

Confidence: high. Zones: recovery 2, fairway 2, water 1.

Chute bending left: woods both sides, the right tree line 5-12 yds off the fairway.

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; water: OSM polygon, checked on the photo.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150L recovery 3 yds out; 160L recovery 2 yds out; 170L recovery 10 yds out; 180L recovery 6 yds out; 190L recovery 10 yds out; 190R recovery 10 yds out; 200L recovery 9 yds out; 200R recovery 10 yds out; 210R recovery 4 yds out; 220L recovery 8 yds out; 220R recovery 6 yds out; 230R recovery 4 yds out; 240L recovery 10 yds out; 240R recovery 1 yds out; 250L recovery 4 yds out; 250R recovery 0 yds out; 260L recovery 7 yds out; 260R recovery 3 yds out; 270L recovery 2 yds out; 270R recovery 6 yds out; 280R recovery 0 yds out; 290L recovery 6 yds out; 290R recovery 0 yds out; 300L recovery 10 yds out; 300R recovery 0 yds out; 310L recovery 6 yds out; 310R recovery 2 yds out; 320L recovery 6 yds out; 320R recovery 2 yds out; 330L recovery 4 yds out; 330R recovery 0 yds out; 340R recovery 0 yds out.

Review: `review/h15.png`; evidence: `render/h15_evidence.png`.

### 17 (par 5, Back 489 yds; tee: tee_axis)

Confidence: medium (creek width where it is grassed). Zones: recovery 2, fairway 2, water 3.

Creek (OSM water hazard, a wooded / grassed drainage) left 140-240 then crossing diagonally 250-345 between the first fairway and the second; woods right beyond the cart path.

Zone notes: recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo; water: OSM polygon, checked on the photo; water: OSM polygon, checked on the photo; water: OSM polygon, checked on the photo.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150L recovery 6 yds out; 160L recovery 8 yds out; 160R recovery 10 yds out; 170R recovery 8 yds out; 180L recovery 7 yds out; 180R recovery 6 yds out; 190L recovery 5 yds out; 190R recovery 8 yds out; 200L recovery 6 yds out; 200R recovery 2 yds out; 210L recovery 6 yds out; 210R recovery 7 yds out; 250L water 4 yds out; 250R recovery 8 yds out; 260L recovery 0 yds out; 260R water 0 yds out; 270L recovery 0 yds out; 270R water 2 yds out; 280L recovery 0 yds out; 280R water 2 yds out; 290L recovery 0 yds out; 290R water 3 yds out; 300L recovery 0 yds out; 300R water 3 yds out; 310L recovery 0 yds out; 310R water 2 yds out; 320L recovery 0 yds out; 320R water 2 yds out; 330L recovery 0 yds out; 330R water 0 yds out; 340L recovery 0 yds out; 340R water 4 yds out.

Review: `review/h17.png`; evidence: `render/h17_evidence.png`.

### 18 (par 4, Back 428 yds; tee: tee_axis)

Confidence: medium (OB line +/-8: no stakes visible). Zones: ob 1, recovery 9, fairway 2.

Trees right 240-340 beyond the cart path, trees left 140-220; a row of houses left: their back yards (houses ~65-100 yds left, yards ~25 yds) end ~45-70 yds left of the line: OB there (the OSM course outline runs 10-20 yds inside the yards).

Zone notes: ob: house lots left: footprints + 25 yds of back yard (no fence / stakes visible; the OSM outline runs 10-20 yds inside the yards); recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; recovery: lidar canopy > 2.5 m (2015 leaf-off), checked on the photo; fairway: OSM polygon, checked on the photo; fairway: OSM polygon, checked on the photo.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150L recovery 8 yds out; 180L recovery 8 yds out; 190R recovery 6 yds out; 210L recovery 5 yds out; 220L recovery 4 yds out; 260R recovery 2 yds out; 300R recovery 3 yds out; 310R recovery 5 yds out; 320R recovery 3 yds out; 330R recovery 10 yds out.

Review: `review/h18.png`; evidence: `render/h18_evidence.png`.


## Every hole (numbering, tees per set, green)

* **1** (par 4; Eagle 399, Back 366, Middle 346, Forward 327): Par 4 downhill from the clubhouse; fairway 140-270 then turns left between tree lines (left 240-300, right from 220); bunker left at 225. Tees: Eagle pad (tee_axis), measured 394 vs card 399; Back pad (tee_axis), measured 361 vs card 366; Middle pad (tee_axis), measured 348 vs card 346; Forward pad (tee_axis), measured 321 vs card 327.
* **2** (par 3; Eagle 167, Back 151, Middle 132, Forward 98): Par 3, open; green outline OSM. No water near the green. Tees: Eagle pad (tee_axis), measured 164 vs card 167; Back pad (tee_axis), measured 150 vs card 151; Middle pad (tee_axis), measured 132 vs card 132; Forward pad (tee_axis), measured 98 vs card 98.
* **3** (par 4; Eagle 409, Back 397, Middle 361, Forward 203): Par 4 over a wooded ravine and the pond (forced carry ~200 from Back): fairway starts at ~185 and bends left; woods left all the way; the OSM course outline crosses the ravine woods (not OB on the ground). Tees: Eagle pad (tee_centroid), measured 410 vs card 409; Back pad (tee_centroid), measured 398 vs card 397; Middle pad (tee_centroid), measured 362 vs card 361; Forward pad (tee_axis), measured 210 vs card 203.
* **4** (par 4; Eagle 416, Back 399, Middle 363, Forward 313): Par 4 uphill; woods left 20-30 yds off the fairway; hole 8's fairway right (playable). Tees: Eagle pad (tee_axis), measured 414 vs card 416; Back pad (tee_axis), measured 405 vs card 399; Middle pad (tee_axis), measured 362 vs card 363; Forward pad (tee_axis), measured 312 vs card 313.
* **5** (par 4; Eagle 473, Back 465, Middle 380, Forward 353): Par 4, tree-lined: woods right within 0-10 yds of the fairway edge the whole way; open rough + cart path left. Tees: Eagle pad (tee_axis), measured 474 vs card 473; Back pad (tee_centroid), measured 466 vs card 465; Middle pad (tee_axis), measured 380 vs card 380; Forward pad (tee_centroid), measured 353 vs card 353.
* **6** (par 3; Eagle 149, Back 138, Middle 120, Forward 84): Par 3 over the pond: water short, left and right of the green; bunkers long. Tees: Eagle pad (tee_axis), measured 148 vs card 149; Back pad (tee_centroid), measured 138 vs card 138; Middle pad (tee_centroid), measured 120 vs card 120; Forward pad (tee_axis), measured 85 vs card 84.
* **7** (par 5; Eagle 493, Back 475, Middle 451, Forward 390): Par 5: woods right hug the fairway; hole 13's fairway left (playable). Tees: Eagle estimated: pad tee moved +11 yds along the line to the card (482 measured); Back pad (tee_axis), measured 476 vs card 475; Middle pad (tee_axis), measured 449 vs card 451; Forward pad (walkback), measured 390 vs card 390.
* **8** (par 4; Eagle 424, Back 407, Middle 376, Forward 322): Par 4: bunkers left 255 and right 205; trees left 140-220; hole 4's fairway right (playable). Tees: Eagle pad (tee_axis), measured 423 vs card 424; Back pad (tee_axis), measured 406 vs card 407; Middle pad (tee_centroid), measured 375 vs card 376; Forward pad (tee_axis), measured 322 vs card 322.
* **9** (par 5; Eagle 526, Back 510, Middle 486, Forward 454): Par 5 up to the clubhouse; unmown grass right beyond the cart path at 280+ (NAIP 2020 tan, 2022 dark green / CIR bright, no lidar height); trees right 150-280. Tees: Eagle pad (walkback), measured 526 vs card 526; Back pad (tee_axis), measured 508 vs card 510; Middle pad (tee_centroid), measured 486 vs card 486; Forward pad (tee_axis), measured 454 vs card 454.
* **10** (par 4; Eagle 420, Back 405, Middle 380, Forward 264): Par 4 down a chute: trees right at the fairway edge (x +10..+15), trees left from 260. Tees: Eagle pad (tee_centroid), measured 420 vs card 420; Back pad (tee_centroid), measured 405 vs card 405; Middle pad (tee_centroid), measured 380 vs card 380; Forward pad (tee_centroid), measured 264 vs card 264.
* **11** (par 4; Eagle 448, Back 441, Middle 420, Forward 364): Par 4 doglegging right: a strip of unmown grass left (x -70..-42, 180-300: dark in every NAIP year, bright CIR, no lidar height); trees right 230-280. Tees: Eagle pad (tee_axis), measured 447 vs card 448; Back pad (tee_axis), measured 440 vs card 441; Middle pad (tee_centroid), measured 419 vs card 420; Forward pad (tee_axis), measured 363 vs card 364.
* **12** (par 3; Eagle 198, Back 180, Middle 162, Forward 120): Par 3, bunkers right and long. Tees: Eagle pad (tee_centroid), measured 198 vs card 198; Back pad (tee_centroid), measured 180 vs card 180; Middle pad (tee_centroid), measured 162 vs card 162; Forward pad (tee_centroid), measured 120 vs card 120.
* **13** (par 5; Eagle 556, Back 546, Middle 524, Forward 438): Par 5: hole 7's fairway left (playable), trees right beyond the cart path. Tees: Eagle pad (tee_axis), measured 557 vs card 556; Back pad (tee_axis), measured 546 vs card 546; Middle pad (lidar_pad), measured 525 vs card 524; Forward pad (tee_centroid), measured 439 vs card 438.
* **14** (par 4; Eagle 265, Back 265, Middle 246, Forward 215): Short par 4 (265) with the pond between ~200 and ~260 in front of the green: lay up short of 200 or carry ~265; woods both sides. Tees: Eagle pad (tee_axis), measured 261 vs card 265; Back pad (tee_axis), measured 261 vs card 265; Middle pad (tee_axis), measured 247 vs card 246; Forward pad (tee_axis), measured 214 vs card 215.
* **15** (par 4; Eagle 459, Back 447, Middle 427, Forward 345): Par 4 down a chute: woods both sides within ~10 yds of the fairway; fairway bends left. Tees: Eagle pad (tee_axis), measured 457 vs card 459; Back pad (tee_axis), measured 445 vs card 447; Middle pad (tee_axis), measured 426 vs card 427; Forward pad (tee_axis), measured 350 vs card 345.
* **16** (par 3; Eagle 177, Back 158, Middle 136, Forward 107): Par 3 through a chute of trees; drainage creek short-right of the green. Tees: Eagle pad (tee_centroid), measured 177 vs card 177; Back pad (tee_centroid), measured 158 vs card 158; Middle pad (tee_centroid), measured 136 vs card 136; Forward pad (tee_centroid), measured 107 vs card 107.
* **17** (par 5; Eagle 499, Back 489, Middle 471, Forward 424): Par 5: creek (OSM penalty area) left 140-240, then crossing diagonally 250-345 between the two fairways; woods right. Tees: Eagle pad (tee_axis), measured 493 vs card 499; Back pad (tee_axis), measured 489 vs card 489; Middle pad (tee_centroid), measured 471 vs card 471; Forward estimated: pad tee moved +9 yds along the line to the card (415 measured).
* **18** (par 4; Eagle 442, Back 428, Middle 405, Forward 353): Par 4 home: trees right 240-340 beyond the cart path, trees left 140-220; houses far left (x < -75). Tees: Eagle estimated: pad tee moved +12 yds along the line to the card (430 measured); Back pad (tee_axis), measured 428 vs card 428; Middle pad (tee_centroid), measured 405 vs card 405; Forward estimated: pad tee moved -14 yds along the line to the card (367 measured).
