# Veenker Memorial (Ames, IA): hand-checked landing corridors

Independent truth for the any-course scoreboard. 13 tee shots (every par 4 / 5) from the **Blue** tees (the back
set on the card, 6680 yds; the scoreboard's set). Corridor 150-340 yds along the package's Blue tee line, +/-60 yds
(mapped footprint 145-345 x +/-65). Files: `trace.py` (the hand trace, in each hole's corridor yards),
`hand_zones_ll.json` (WGS84, schema of `course_data/spirit_hollow/hand_zones_ll.json`), `render/` (evidence:
NAIP 2023 0.3 m photo, CIR, NAIP 2023 / 2021 / 2019 / 2017 / 2015 / 2014 at 1 m, 3DEP lidar canopy height),
`review/` (trace over photo | photo + lidar canopy edge | NAIP 2021 | lidar | CIR).

## Method

* Each hole gets one planar corridor frame (UTM, tee and aim of the Blue set from the package): x = yds right of
  the tee line, along = yds out. Every render of a hole is in that frame with a 5- or 10-yd grid; I read the edges
  off the grid by eye and wrote them as polygons (`trace.py`), converted to WGS84 by the same frame.
* Fairway = the mown, striped turf (bright pink in CIR); a separate first cut only where a collar is visible
  (holes 1, 4, 9). Rough = everything mown and unzoned.
* Trees = the crown edge (the golfer's tree line), from the bright sunlit crowns in CIR and the lidar canopy edge
  (HAG > 2.5 m; 2020 leaf-off survey). NAIP 2023 was flown 2 Sep in the morning: crowns cast long shadows toward
  the north-west; shadows are never traced as trees. Where 2020 lidar and 2023 crowns differ (open-grown
  deciduous trees: lidar crowns are smaller), the 2023 crown wins.
* Long grass = unmown: tan / tufted in NAIP across several years and pale grey (not irrigated) in CIR. Veenker is
  a parkland course: only two such areas are in the corridors (hole 15 top-left, hole 16 carry strip).
* Water = dark in CIR / no lidar returns. OB = the US-30 highway left of hole 12 (the only property line in a
  corridor). Buildings / service roads inside the property are not OB.
* Second pass: every place a hazard starts within 10 yds of the fairway edge was re-checked on 6-8 px/yd zooms
  (photo, CIR, lidar, photo + lidar canopy edge). That pass moved the right tree line of 2 (cart path side), 5, 12
  and 16 by 2-5 yds outward (lidar crown edge vs RGB shadow) and the creek on 15 by ~4 yds.
* Registration: NAIP 2023 / 2021 and the lidar agree to < 3 m (cross-correlation of tree masks: lidar -2 / -3 m
  vs NAIP), i.e. ~2-3 yds; the frame itself is exact (no screenshot registration involved).

## Ambiguities (overall)

* Tree shadows on 2, 3, 4, 18 (RGB) - resolved with CIR + lidar; residual +/-3 yds on the left edge of 2.
* Tee positions: 7, 12, 16 use the package's Blue tee on a lidar pad (no OSM box). The overviews
  (`render/hNN_overview.png`) show a tee pad there on every hole; card and measured yardage agree within 8 yds
  except 3 (card 333, measured 318) - the corridor is measured from the package tee as the product plays it.
* Weedy, mottled rough left of 12 (290-345) is mown in 2021 and 2019: rough, not long grass.
* Dead trees (1: 308; 18: 175) are kept as trees (they still block).

## Per tee shot

### 1 (par 4, Blue 435 yds; tee: tee_axis)

Confidence: high. Zones: first_cut 1, fairway 1, recovery 17.

Straight par 4. Mown fairway ~35 yds, a lighter first-cut collar (wider on the left, 8-11 yds) inside the irrigated band; tan rough beyond is mown (cart paths run through it, no texture), not long grass. Trees = lidar crowns, scattered both sides from 30 yds out.

Zone notes: recovery: dead / leafless tree (lidar 2.5-8 m, grey in NAIP 2023).

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150L recovery 5 yds out; 160L recovery 7 yds out; 210R recovery 6 yds out; 220R recovery 7 yds out; 250L recovery 6 yds out; 260L recovery 6 yds out; 310R recovery 7 yds out.

Review: `review/h01.png`; evidence: `render/h01_evidence.png`.

### 2 (par 4, Blue 334 yds; tee: tee_centroid)

Confidence: medium (left fairway edge under shadow, +/-3 yds). Zones: fairway 2, recovery 3.

Tree-lined chute, cart path down the right edge of the fairway. NAIP 2023 (2 Sep) has long tree SHADOWS across the left half of the fairway (dark purple in CIR, no crowns): the left tree line is the lidar crown edge (-20 to -31), fairway edges from NAIP 2021 (less shadow). Fairway ends ~288; rough approach to the green (322-345, x -25..-3). No distinct first cut.

Zone notes: fairway: green (product LIE_MAP: green -> fairway); recovery: right tree line just right of the cart path (lidar crown edge, 2nd pass); incl. 0.5-2.5 m shrubs at 205-220.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 160L recovery 0 yds out; 160R recovery 6 yds out; 170L recovery 0 yds out; 170R recovery 6 yds out; 180L recovery 5 yds out; 180R recovery 5 yds out; 190L recovery 8 yds out; 190R recovery 2 yds out; 200L recovery 3 yds out; 200R recovery 2 yds out; 210L recovery 5 yds out; 210R recovery 2 yds out; 220L recovery 1 yds out; 220R recovery 3 yds out; 230L recovery 4 yds out; 230R recovery 2 yds out; 240L recovery 1 yds out; 240R recovery 2 yds out; 250L recovery 3 yds out; 260L recovery 8 yds out; 260R recovery 8 yds out; 270L recovery 8 yds out; 280L recovery 1 yds out; 290L recovery 8 yds out.

Review: `review/h02.png`; evidence: `render/h02_evidence.png`.

### 3 (par 4, Blue 333 yds; tee: tee_centroid)

Confidence: medium-high. Zones: fairway 4, sand 1, recovery 8.

Dogleg right to a green at (57, 289) behind a bunker; cart path crosses at 280-300. RGB shadows put the right tree line ~15 yds too far in: crowns from lidar + CIR (the right trees start 5-20 yds outside the fairway). Trees straight ahead from 312 (hole is 318 measured).

Zone notes: fairway: approach above the cart path; fairway: green; fairway: green of another hole (left); recovery: small trees at the cart-path junction: 2023 CIR crowns vs 2020 lidar differ by ~5 yds.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 170L recovery 7 yds out; 180L recovery 8 yds out; 190L recovery 10 yds out; 230L recovery 0 yds out; 230R recovery 4 yds out; 240R recovery 8 yds out; 250R recovery 8 yds out; 260R recovery 2 yds out; 270L recovery 0 yds out; 270R recovery 2 yds out; 280L recovery 0 yds out.

Review: `review/h03.png`; evidence: `render/h03_evidence.png`.

### 4 (par 4, Blue 349 yds; tee: tee_axis)

Confidence: medium-high. Zones: first_cut 1, fairway 2, sand 2, recovery 8.

Slight dogleg right along a wooded right side; a single big tree guards the left of the landing area at 277-312 (x -28..0). RGB shadows overstate the right trees at 190-210; crowns from lidar + CIR. Fairway right edge has a tan rough strip (5-20 yds) to the trees from 200 on.

Zone notes: first_cut: left collar (lighter in CIR) between the fairway and the cart path; fairway: green; recovery: big tree on the left edge of the fairway, 277-312.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150R recovery 0 yds out; 160R recovery 0 yds out; 170R recovery 0 yds out; 180R recovery 0 yds out; 190L recovery 6 yds out; 190R recovery 0 yds out; 200L recovery 6 yds out; 200R recovery 6 yds out; 240L recovery 4 yds out; 250L recovery 8 yds out; 270R recovery 6 yds out; 280L recovery 6 yds out; 280R recovery 4 yds out; 290L recovery 0 yds out; 290R recovery 4 yds out; 300L recovery 4 yds out; 300R recovery 0 yds out; 310R recovery 8 yds out.

Review: `review/h04.png`; evidence: `render/h04_evidence.png`.

### 5 (par 4, Blue 402 yds; tee: tee_centroid)

Confidence: medium. Zones: fairway 1, recovery 9, water 2.

Oval fairway ends at 253; beyond is mown rough among scattered trees, a pond at 284-316 right of the line (x +18..+56) and a second pond / tree band from 285 left. Card 402: the drive lands in the oval or the rough short of the ponds. A building and service road at the bottom right (x > +55, 150-185) are not marked OB (no property line visible in the corridor).

Zone notes: recovery: right tree line = lidar crown edge over the cart path (2nd pass); recovery: right tree line; 0.5-2.5 m shrubs at the pond's south bank; water: pond (algae: pale in RGB, no lidar returns); water: pond (2023 CIR; the 2020 lidar no-return area sits ~10 yds right).

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150R recovery 8 yds out; 160R recovery 6 yds out; 170R recovery 6 yds out; 180R recovery 6 yds out; 190R recovery 4 yds out; 200R recovery 4 yds out; 210R recovery 1 yds out; 220L recovery 8 yds out; 220R recovery 3 yds out; 230R recovery 4 yds out.

Review: `review/h05.png`; evidence: `render/h05_evidence.png`.

### 7 (par 5, Blue 590 yds; tee: lidar_pad)

Confidence: medium (fairway start / rough tone). Zones: fairway 2, sand 1, recovery 12.

The Blue tee (590) sits far back: 150-262 is an open band of mown, sun-bleached rough between tree clumps (left) and woods (right); the fairway starts at ~268 (x -15..+26) and runs to the creek beyond 345. A 0.5-2.5 m lidar strip along the cart path at 330-350 right is not marked (no canopy, hedge or tall grass not visible in 2023). Highway OB right is beyond +60 here.

Zone notes: fairway: green of another hole.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 270R recovery 4 yds out; 290R recovery 6 yds out; 300L recovery 1 yds out; 300R recovery 10 yds out; 310L recovery 0 yds out; 310R recovery 6 yds out; 320L recovery 4 yds out; 320R recovery 6 yds out.

Review: `review/h07.png`; evidence: `render/h07_evidence.png`.

### 9 (par 5, Blue 537 yds; tee: tee_centroid)

Confidence: medium. Zones: first_cut 1, fairway 1, recovery 19.

Fairway bends right after 250 between two tree groups. The 2020 lidar (leaf-off) shows these open-grown deciduous trees as small 2.5-8 m crowns, much smaller than NAIP 2021 / 2023: crowns traced on the CIR (bright, textured) with the shadow (dark, up-left of each crown) excluded.

Zone notes: first_cut: collar visible in CIR on both sides of the lower fairway.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 190R recovery 8 yds out; 200R recovery 8 yds out; 240R recovery 4 yds out; 250R recovery 7 yds out; 260R recovery 4 yds out; 270R recovery 4 yds out; 290L recovery 0 yds out; 290R recovery 5 yds out; 300L recovery 0 yds out; 300R recovery 4 yds out; 310L recovery 1 yds out; 320L recovery 4 yds out; 330L recovery 7 yds out; 330R recovery 0 yds out; 340L recovery 9 yds out; 340R recovery 2 yds out.

Review: `review/h09.png`; evidence: `render/h09_evidence.png`.

### 10 (par 5, Blue 560 yds; tee: tee_axis)

Confidence: medium-high. Zones: fairway 1, recovery 13.

The fairway runs up the right, past a tree group that blocks the tee line from 250 (x -15..+17) and a second tree band straight on at 290-350; the play is right of the trees toward the cart path. Left of the trees (x -35..-15) is rough, beyond the left cart path another hole's fairway. Crowns from CIR (2020 lidar under-sizes these leaf-off crowns).

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150R recovery 4 yds out; 160R recovery 0 yds out; 170R recovery 0 yds out; 180L recovery 10 yds out; 240R recovery 9 yds out; 250L recovery 0 yds out; 250R recovery 5 yds out; 260L recovery 0 yds out; 260R recovery 2 yds out; 270L recovery 0 yds out; 270R recovery 2 yds out; 280L recovery 0 yds out; 290L recovery 0 yds out; 310L recovery 0 yds out; 320L recovery 0 yds out; 330L recovery 0 yds out; 340L recovery 0 yds out.

Review: `review/h10.png`; evidence: `render/h10_evidence.png`.

### 12 (par 4, Blue 330 yds; tee: lidar_pad)

Confidence: medium. Zones: fairway 2, sand 1, recovery 16, ob 1.

Dogleg right; big woods on the right to 240, then the fairway swings right to the green (50, 318). Left of the cart path at 290-345 the rough is mottled / weedy in 2023 (pale texture in CIR) but not tan or tall in 2021: kept as rough (ambiguous, see NOTES). Highway OB on the left from ~200 out.

Zone notes: fairway: green; recovery: right woods: lidar crown edge (2nd pass, was 2 yds further in); ob: the highway (US 30 frontage) left: line at the grass edge of the shoulder; no fence visible.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150L recovery 1 yds out; 150R recovery 6 yds out; 160R recovery 6 yds out; 170L recovery 2 yds out; 170R recovery 6 yds out; 180L recovery 4 yds out; 180R recovery 6 yds out; 190R recovery 6 yds out; 200R recovery 6 yds out; 210L recovery 5 yds out; 210R recovery 5 yds out; 220L recovery 8 yds out; 220R recovery 6 yds out; 230R recovery 8 yds out; 240L recovery 0 yds out; 250L recovery 2 yds out; 270L recovery 0 yds out; 270R recovery 10 yds out; 280L recovery 4 yds out; 280R recovery 9 yds out; 290R recovery 8 yds out; 300R recovery 4 yds out; 310L sand 4 yds out; 310R recovery 0 yds out; 320L recovery 9 yds out; 320R recovery 0 yds out; 330R recovery 0 yds out.

Review: `review/h12.png`; evidence: `render/h12_evidence.png`.

### 14 (par 4, Blue 416 yds; tee: tee_axis)

Confidence: medium-high. Zones: fairway 1, recovery 15.

Fairway straight to ~230 then a diagonal band right (dogleg right) toward a green at ~(+75, 405). A crown at (+10..+28, 225-262) pinches the bend from the right; woods left beyond -30 from 245. Crowns from CIR 2023; the 2020 lidar has the big left woods but fewer crowns in the middle groups.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 180R recovery 10 yds out; 190R recovery 6 yds out; 210R recovery 4 yds out; 220R recovery 2 yds out; 230R recovery 0 yds out; 240R recovery 2 yds out; 250R recovery 0 yds out; 260R recovery 0 yds out; 270R recovery 4 yds out; 280R recovery 4 yds out; 290L recovery 4 yds out; 300L recovery 6 yds out; 300R recovery 10 yds out; 310L recovery 9 yds out; 330L recovery 0 yds out; 340L recovery 5 yds out.

Review: `review/h14.png`; evidence: `render/h14_evidence.png`.

### 15 (par 4, Blue 420 yds; tee: tee_axis)

Confidence: medium (native extent; creek under canopy +/-5 yds). Zones: native 1, fairway 1, recovery 8, water 1.

Sharp dogleg right (green at +151, 308 across the creek): the drive lands on the wide fairway left of a tree mass that covers the tee line from 150 to 200 (x > -18). Creek diagonally from (+50, 210) to (-12, 350). Top-left (-75..-5, 280-328): the only clearly unmown long grass at Veenker in these corridors (pale grey in CIR, tan in 2021 and 2023).

Zone notes: native: unmown: pale grey in CIR (dry, no irrigation), tan and tufted in NAIP 2023 and 2021; water: creek (dark in CIR, no lidar returns).

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150R recovery 9 yds out; 160R recovery 8 yds out; 170R recovery 8 yds out; 180R recovery 8 yds out; 190R recovery 8 yds out; 240R water 4 yds out; 250R water 7 yds out.

Review: `review/h15.png`; evidence: `render/h15_evidence.png`.

### 16 (par 5, Blue 544 yds; tee: lidar_pad)

Confidence: medium-high. Zones: native 1, fairway 1, recovery 2, water 1.

Straight par 5 down a chute: woods both sides (crown edges from CIR 2023 + lidar), a creek inside the right woods from 300. The first ~30 yds of the corridor (145-175) is an unmown carry area (native, medium confidence: tan and tufted in both years, but it could be a dry, rarely-mown forward-tee strip).

Zone notes: native: unmown carry area in front of the fairway: tan / tufted in 2021 and 2023, pale-grey speckled in CIR; recovery: right woods: lidar crown edge (2nd pass: a 5-8 yd rough strip between fairway and trees from 250); water: creek inside the right woods.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 180L recovery 6 yds out; 180R recovery 3 yds out; 190L recovery 6 yds out; 190R recovery 3 yds out; 200L recovery 2 yds out; 200R recovery 2 yds out; 210L recovery 1 yds out; 210R recovery 3 yds out; 220L recovery 2 yds out; 220R recovery 4 yds out; 230L recovery 4 yds out; 230R recovery 4 yds out; 240L recovery 6 yds out; 240R recovery 4 yds out; 250L recovery 5 yds out; 260L recovery 6 yds out; 260R recovery 10 yds out; 270L recovery 8 yds out; 270R recovery 10 yds out; 280R recovery 10 yds out; 290R recovery 10 yds out; 310R recovery 10 yds out; 320R recovery 10 yds out.

Review: `review/h16.png`; evidence: `render/h16_evidence.png`.

### 18 (par 5, Blue 534 yds; tee: tee_axis)

Confidence: medium-high. Zones: fairway 1, recovery 13.

Parkland: open-grown trees both sides, fairway 35 yds. NAIP 2023 shadows fall to the left (-x) of every crown in this frame: crowns traced on the bright CIR part, which the 2020 lidar confirms (crowns sit 5-10 yds right of the dark blobs).

Zone notes: recovery: dead / leafless tree (grey in CIR and RGB, small lidar returns): still blocks.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 170R recovery 8 yds out; 180R recovery 6 yds out; 190R recovery 8 yds out; 200R recovery 5 yds out; 210R recovery 4 yds out; 220R recovery 3 yds out; 230R recovery 3 yds out; 240R recovery 2 yds out; 250R recovery 0 yds out; 260R recovery 0 yds out; 270R recovery 0 yds out; 290L recovery 0 yds out; 290R recovery 8 yds out; 300L recovery 0 yds out; 300R recovery 2 yds out; 310L recovery 0 yds out; 310R recovery 1 yds out; 320L recovery 0 yds out; 320R recovery 3 yds out; 330L recovery 2 yds out; 340L recovery 8 yds out.

Review: `review/h18.png`; evidence: `render/h18_evidence.png`.

