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

## Per tee shot

### 1 (par 4, Blue 307 yds; tee: tee_axis)

Confidence: medium (fescue vs dormant mown rough). Zones: native 2, fairway 2, sand 4, water 1, ob 1.

Short par 4 along a lake (right). Fairway is wide and continuous; the left side between the cart path and the fairway has tan, tufted fescue in 2019-2023 (green in 2014-2017: it was let grow after ~2018). Condos left of the cart path to 220 = OB.

Zone notes: native: tufted fescue between the cart path and the fairway (tan 2019-2023); native: fescue halo around the left fairway bunker; fairway: green; water: lake (edge checked on NIR profiles); ob: condominium buildings and yards left (property line at the hedge / tree row).

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150L ob 8 yds out; 150R water 3 yds out; 160L ob 8 yds out; 160R water 2 yds out; 170L ob 8 yds out; 170R water 3 yds out; 180L ob 8 yds out; 180R water 3 yds out; 190L ob 9 yds out; 190R water 4 yds out; 200R water 4 yds out; 210L native 0 yds out; 210R water 4 yds out; 220L native 0 yds out; 220R water 4 yds out; 230L native 0 yds out; 230R water 4 yds out; 240L native 0 yds out; 240R water 4 yds out; 250R sand 0 yds out; 260L sand 0 yds out; 260R sand 0 yds out; 270L native 4 yds out; 270R water 4 yds out; 280L native 3 yds out; 280R water 4 yds out; 290L native 3 yds out; 290R water 4 yds out; 300L native 3 yds out; 300R sand 0 yds out; 310R sand 0 yds out.

Review: `review/h01.png`; evidence: `render/h01_evidence.png`.

### 2 (par 4, Blue 425 yds; tee: tee_axis)

Confidence: high. Zones: native 1, fairway 1, recovery 1, sand 1.

Straight par 4 with woods right. Left: a permanent prairie strip between two cart paths (x -50..-30 at 150, -34..-8 at 300); beyond it another hole's fairway.

Zone notes: native: prairie strip between the two cart paths: tan in 2014, 2015, 2021, 2023; recovery: woods right: lidar crown edge (RGB shadows reach +22).

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 220R recovery 8 yds out; 230R recovery 10 yds out; 240L native 10 yds out; 250R recovery 10 yds out; 260R recovery 10 yds out; 330R recovery 9 yds out; 340R recovery 6 yds out.

Review: `review/h02.png`; evidence: `render/h02_evidence.png`.

### 3 (par 5, Blue 510 yds; tee: tee_centroid)

Confidence: medium-high. Zones: fairway 1, native 3, sand 1.

Par 5 doglegging slightly left. A prairie / wetland area occupies the right of the corridor to 260 (x > +22): unmown in every NAIP year (standing water in 2015) - long grass. Fescue islands at 285-330. Two cart paths left; another hole beyond.

Zone notes: native: wetland / prairie: coarse texture in every year, standing water in 2015; native: fescue island in the fairway.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 160R native 5 yds out; 170R native 4 yds out; 180R native 4 yds out; 190R native 3 yds out; 200R native 3 yds out; 210R native 4 yds out; 220R native 4 yds out; 230R native 4 yds out; 240R native 4 yds out; 250L sand 0 yds out; 250R native 0 yds out; 260L sand 6 yds out; 260R native 0 yds out; 290L native 0 yds out; 300L native 0 yds out; 310L native 0 yds out; 320L native 0 yds out; 320R native 0 yds out; 330L native 0 yds out; 330R native 0 yds out; 340R native 0 yds out.

Review: `review/h03.png`; evidence: `render/h03_evidence.png`.

### 4 (par 4, Blue 371 yds; tee: tee_centroid)

Confidence: medium. Zones: fairway 1, native 4, recovery 1, ob 1.

Dogleg left around the cart path; mobile-home park left = OB (behind a shrub row). Fescue islands and a prairie in the elbow (right, 280-350): long grass. Fairway edges are soft (mown rough the same colour in 2023): +/-4 yds.

Zone notes: native: prairie in the elbow of the dogleg: unmown in every year; native: fescue mound; native: fescue island; recovery: shrub / small-tree row between the cart path and the mobile-home park (lidar 0.5-4 m); ob: mobile-home park left (property line at the shrub row).

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 160R native 4 yds out; 210R native 8 yds out; 220R native 6 yds out; 230L native 0 yds out; 230R native 6 yds out; 240L native 2 yds out; 240R native 8 yds out; 260L ob 3 yds out; 270L ob 10 yds out; 310R native 10 yds out; 320R native 9 yds out.

Review: `review/h04.png`; evidence: `render/h04_evidence.png`.

### 6 (par 4, Blue 418 yds; tee: tee_axis)

Confidence: medium. Zones: fairway 1, native 2, recovery 1, sand 1, ob 1.

Straight par 4 between two cart paths. Right of the tee line at 180-250 the turf is dry and tan but smooth (mown rough, also lighter in 2021); unmown patches at 145-178 and along the right cart path from 296. Mobile-home park left of its road from 250 = OB.

Zone notes: native: unmown patch right of the tee line (coarse texture, tan in 2021 and 2023); native: unmown strip along the right cart path; recovery: shrub thicket; ob: mobile-home park left (road edge).

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150R native 4 yds out; 160R native 2 yds out; 170R native 5 yds out; 260L sand 0 yds out; 300R native 10 yds out.

Review: `review/h06.png`; evidence: `render/h06_evidence.png`.

### 7 (par 5, Blue 505 yds; tee: tee_axis)

Confidence: medium-high. Zones: fairway 1, native 2, recovery 1, ob 1.

Long par 5; tree belt left with a mobile-home park behind it (OB), prairie / unmown patches right of the cart path. The grass hollow at 270-310 left (sand in 2021, grassed in 2023) is mapped as rough.

Zone notes: native: unmown patch right of the cart path; native: prairie right (coarse, tan in 2021, unmown every year); recovery: tree belt left (lidar crown edge); mobile-home park behind it; ob: mobile-home park behind the tree belt.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150R native 10 yds out; 160R native 8 yds out; 170R native 10 yds out; 290R native 10 yds out; 300R native 4 yds out; 310R native 5 yds out; 320R native 6 yds out.

Review: `review/h07.png`; evidence: `render/h07_evidence.png`.

### 9 (par 4, Blue 371 yds; tee: tee_axis)

Confidence: medium-high. Zones: fairway 1, native 2, recovery 1, sand 2, water 2.

The lake runs up the right and then crosses the line of play diagonally (from 245 at the right edge to 310 at the left), with an unmown lip along the bank. The far bank beyond the arm is another hole.

Zone notes: native: unmown bank between the fairway and the lake (pale, speckled in CIR; tan 2021); native: unmown lip along the lake bank (5-8 yds); recovery: shrub row along the left cart path (lidar 0.5-2.5 m); water: lake (right); water: lake arm crossing the line of play (lidar no-return area).

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150L recovery 0 yds out; 150R native 2 yds out; 160L recovery 0 yds out; 160R native 3 yds out; 170L recovery 0 yds out; 170R native 4 yds out; 180L recovery 0 yds out; 180R native 6 yds out; 190L recovery 0 yds out; 190R native 6 yds out; 200L recovery 0 yds out; 200R native 8 yds out; 210L recovery 2 yds out; 210R native 10 yds out; 220L recovery 5 yds out; 230L recovery 8 yds out; 240L sand 0 yds out; 270R native 7 yds out; 280L sand 0 yds out; 280R native 5 yds out; 290R native 6 yds out.

Review: `review/h09.png`; evidence: `render/h09_evidence.png`.

### 10 (par 4, Blue 396 yds; tee: tee_axis)

Confidence: medium-high. Zones: fairway 1, native 2, recovery 4, sand 1.

Prairie hole: the whole right side of the corridor is unmown long grass (a few trees in it at 310-335), behind a 4-6 yd strip of mown rough from 260 (2nd pass); left of the cart path an unmown strip with a shrub line. Fairway edge to the prairie +/-3 yds.

Zone notes: native: prairie right of the fairway (tan in 2021, coarse / pale in CIR 2023); native: unmown strip with a shrub line left of the cart path.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 260R native 7 yds out; 270L sand 0 yds out; 270R native 6 yds out; 280R native 6 yds out; 290R native 6 yds out; 300R native 6 yds out; 310R native 6 yds out; 320R native 6 yds out; 330R native 6 yds out; 340R native 6 yds out.

Review: `review/h10.png`; evidence: `render/h10_evidence.png`.

### 12 (par 4, Blue 328 yds; tee: tee_axis)

Confidence: medium. Zones: fairway 2, native 2, water 1, sand 2.

Short par 4; a stone-lined drainage creek with shrubs runs down the right (x +18..+55), unmown grass and shrubs beyond it, an unmown strip left of the left cart path. The creek is mapped as water (penalty area; the inner edge is the rock line, +/-3 yds). The lidar no-return patch right of the creek at 150-200 is tall wet grass in the photo, not open water.

Zone notes: fairway: green; native: unmown grass and shrubs beyond the creek; water: stone-lined drainage creek (grey rock in NAIP, shrubs along it); native: unmown strip left of the left cart path.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150R water 3 yds out; 160R water 4 yds out; 170R water 6 yds out; 180R water 8 yds out; 310R sand 0 yds out.

Review: `review/h12.png`; evidence: `render/h12_evidence.png`.

### 13 (par 4, Blue 413 yds; tee: tee_axis)

Confidence: medium. Zones: fairway 1, native 4, sand 2.

Fairway between a diagonal fescue band (left) and two cart paths (right) with unmown islands between them. Fairway edges are soft in 2023 (fairway and rough the same green): +/-4 yds.

Zone notes: native: fescue / prairie band left (tufted, tan in 2021, dark speckled in CIR); native: unmown oval between the two cart paths; native: unmown strip between the cart paths.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 200L native 10 yds out; 210L native 8 yds out; 220L native 6 yds out; 230L native 4 yds out; 240L native 2 yds out; 240R sand 6 yds out; 250L native 0 yds out; 250R sand 2 yds out; 260L native 2 yds out; 270L native 4 yds out; 280L sand 2 yds out; 290L sand 1 yds out; 300L native 8 yds out; 310L native 9 yds out; 320L native 8 yds out; 330L native 8 yds out; 340L native 7 yds out.

Review: `review/h13.png`; evidence: `render/h13_evidence.png`.

### 14 (par 5, Blue 476 yds; tee: tee_axis)

Confidence: medium-high. Zones: fairway 1, native 2, recovery 1, sand 1.

Par 5 along a wood (left). Mown fairway is a wide oval from 165; between it and the woods a narrow unmown strip; right of the first cart path an unmown strip with a bunker at 180-200.

Zone notes: native: unmown strip along the tree line (pale in CIR); native: unmown strip between the two cart paths; recovery: woods left: lidar crown edge (CIR + lidar agree to ~2 yds).

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 180R native 8 yds out; 190R native 8 yds out; 200R native 6 yds out; 210R native 6 yds out; 220L recovery 10 yds out; 220R native 6 yds out; 230L native 6 yds out; 230R native 7 yds out; 240L native 5 yds out; 240R native 8 yds out; 250L native 4 yds out; 250R native 8 yds out; 260L native 4 yds out; 260R native 8 yds out; 270L native 3 yds out; 270R native 8 yds out; 280L native 4 yds out; 280R native 8 yds out; 290L native 3 yds out; 290R native 9 yds out; 300L native 4 yds out; 300R native 10 yds out; 310L native 4 yds out; 310R native 10 yds out; 320L native 4 yds out; 320R native 10 yds out; 330L native 4 yds out; 330R native 10 yds out; 340L native 4 yds out.

Review: `review/h14.png`; evidence: `render/h14_evidence.png`.

### 15 (par 4, Blue 417 yds; tee: tee_axis)

Confidence: medium. Zones: fairway 1, native 2, recovery 1.

Woods left, wide dry rough right of the fairway (tan, but mower stripes visible: rough, not long grass - ambiguous, see NOTES). Fescue only as the tufted carry patch at 145-168 and beyond the right cart path at 300+.

Zone notes: native: tufted fescue carry patch; native: fescue beyond the right cart path; recovery: woods left: lidar crown edge.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 180L recovery 10 yds out; 190L recovery 6 yds out; 200L recovery 8 yds out; 210L recovery 6 yds out; 220L recovery 8 yds out.

Review: `review/h15.png`; evidence: `render/h15_evidence.png`.

### 17 (par 4, Blue 395 yds; tee: tee_axis)

Confidence: medium-high. Zones: native 2, fairway 1, water 1, sand 2.

Fairway ends at ~305 against a band of fescue that crosses the line of play (305-330); fescue left of a wet ditch and right of the cart path. Card 395: driver over the crossing fescue is a real carry decision.

Zone notes: native: fescue left of the ditch and the band crossing the line of play beyond the fairway end; native: fescue right of the cart path (tan, tufted); water: wet ditch (lidar no returns 150-190, standing water dark in CIR).

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 160L water 9 yds out; 170L water 8 yds out; 180L water 6 yds out; 190L water 6 yds out; 200L sand 0 yds out; 210L sand 0 yds out; 220L water 8 yds out; 230L water 10 yds out; 270L sand 0 yds out; 280L sand 0 yds out.

Review: `review/h17.png`; evidence: `render/h17_evidence.png`.

### 18 (par 4, Blue 433 yds; tee: tee_axis)

Confidence: medium. Zones: fairway 1, native 2, water 1, sand 2.

Finishing hole between a shrubby drainage ditch (left, mapped as water: penalty area) with fescue beyond, and a cart path with a second shrubby ditch and fescue right. Mown dry rough (tan, smooth) between the fairway and both ditches.

Zone notes: native: fescue left (tufted, tan) incl. the shrubby ditch; water: ditch / drainage channel with shrubs left (dark linear feature in every NAIP year); native: shrubby ditch and fescue right of the cart path.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 190L sand 2 yds out; 200L sand 0 yds out; 210L sand 2 yds out; 260R sand 2 yds out; 270R sand 2 yds out; 280R sand 3 yds out.

Review: `review/h18.png`; evidence: `render/h18_evidence.png`.

