# Ellis Golf Course (Cedar Rapids, IA): hand-checked landing corridors

Independent truth for the any-course scoreboard: the **wooded / hilly** course of the three (Veenker parkland,
Coldwater links). It replaces the first wooded pick, Wakonda Club (Des Moines): Wakonda's NAIP 2023 shows a
course in renovation (tree removal since 2021, dormant / reseeded turf, re-routed paths), so 2023 fairway lines
could not be traced reliably (its package and renders stay committed, unused). 14 tee shots (every par 4 / 5)
from the **Blue** tees (6502 yds, the back set of Blue / White / Gold / Red; the package's set). Corridor
150-340 yds along the package's Blue tee line, +/-60 (mapped footprint 145-345 x +/-65).

## Method (as Veenker; differences)

* **2020 derecho.** The 3DEP lidar here is the 2019 IA_Eastern survey; the August 2020 derecho felled many of
  Ellis's trees. NAIP 2021 and 2023 both show the losses. Trees are therefore the crowns standing in NAIP 2023
  (bright, textured in CIR), checked against the lidar where the two agree; lidar crowns missing in 2021 / 2023
  are not trees (holes 1, 2, 3, 5, 6, 7, 13, 15, 17 lose 20-80% of the 2019 canopy in the corridor). This is a
  real hazard for any lidar-based tree layer and is itself a useful test.
* **Drought image.** NAIP 2023 (summer) shows dormant, white-in-CIR rough and the irrigated fairway / collar as
  the only green. Fairway = the striped, irrigated turf; on 7 the irrigated collar outside the stripes is mapped
  as first cut. Dormant mown rough (tan, mower stripes) is rough, not long grass.
* Long grass only where unmown in several years: the replanted prairie on 2 (where the felled woods stood),
  shrubby tall-grass slopes / ridges on 15 and 17 (lidar 0.5-2.5 m returns + tufts in 2023).
* Linear lidar returns along straight lines (5, 6) are power lines, not trees.
* OB: streets / houses on 7 (right), 9 (left), 13 (straight on, beyond the tree belt).
* Second pass (6 px/yd zooms, photo + CIR + lidar edge): the right woods on 12 and 18 moved 2-5 yds outward
  (dark crown shadow in front of the crowns), the crowns right of 16 and left of 18 moved onto the lidar.

## Ambiguities (overall)

* Which 2019 crowns are gone: judged on NAIP 2023 + 2021 crowns (bright in CIR); small replanted trees and
  stumps (< 3 m crowns) are not mapped.
* Fairway edges in drought-dormant turf +/-3-4 yds where the collar and the fairway are both green (2, 5, 13).
* Hole 2 left: prairie vs dormant rough boundary +/-4 yds.

## Per tee shot

### 1 (par 4, Blue 395 yds; tee: tee_centroid)

Confidence: medium-high. Zones: fairway 1, recovery 12.

Straight par 4 with single trees both sides. 2023 is a drought image (dormant rough white in CIR, the fairway irrigated pink). Several 2019-lidar crowns right (+15..+60, 140-200) and left (-45..-30, 150-175, 260) are gone in 2023 (derecho; small replanted trees / stumps remain): not trees.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 190L recovery 6 yds out; 250L recovery 9 yds out; 310L recovery 8 yds out; 320L recovery 10 yds out.

Review: `review/h01.png`; evidence: `render/h01_evidence.png`.

### 2 (par 4, Blue 365 yds; tee: tee_centroid)

Confidence: medium (fairway edges in drought-dormant turf +/-4 yds). Zones: native 1, fairway 1, sand 2, recovery 6.

Dogleg right. In the 2019 lidar a wood fills the left (-70..-30, 140-260) and a tree line crosses the corner (-35..0, 250-310); both are gone in 2023 (2020 derecho): the left is now tufted, unmown prairie (native) and the corner a stump-dotted band of dormant rough. Trees right only at 205-250.

Zone notes: native: replanted prairie where the 2019-lidar woods stood (felled in the 2020 derecho): tufted, tan, unmown in 2023.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150L native 7 yds out; 160L native 6 yds out; 170L native 5 yds out; 180L native 6 yds out; 190L native 6 yds out; 200L native 6 yds out; 210L native 8 yds out; 210R sand 4 yds out; 220L native 10 yds out; 220R sand 4 yds out; 240R sand 2 yds out; 260R recovery 0 yds out.

Review: `review/h02.png`; evidence: `render/h02_evidence.png`.

### 3 (par 5, Blue 481 yds; tee: tee_axis)

Confidence: medium-high. Zones: fairway 1, recovery 6.

Straight par 5 along woods right; a row of three single trees right of the fairway at 255-310. The 2019 lidar's tree row left (-55..-35, 140-300) is gone in 2023 (derecho; stumps in dormant rough).

Zone notes: recovery: woods right (crowns in CIR 2023 and the 2019 lidar agree here).

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 260R recovery 4 yds out; 280R recovery 4 yds out; 300R recovery 9 yds out.

Review: `review/h03.png`; evidence: `render/h03_evidence.png`.

### 5 (par 4, Blue 385 yds; tee: tee_centroid)

Confidence: medium. Zones: fairway 1, sand 3, recovery 9.

Straight par 4 with single trees both sides. The 2019 lidar has two rows of big trees (left -60..-35 and right +30..+50) the whole length; about half survive in 2023 (derecho). The thin linear 'canopy' at +15..+30 in the lidar is a power line, not trees.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150L recovery 4 yds out; 160L recovery 8 yds out; 220R sand 0 yds out; 260L sand 0 yds out.

Review: `review/h05.png`; evidence: `render/h05_evidence.png`.

### 6 (par 4, Blue 420 yds; tee: lidar_pad)

Confidence: medium-high. Zones: fairway 1, sand 3, recovery 7.

Straight, open par 4 with single trees; the 2019 lidar's tree rows (left -70..-50 at 145-225, right +20..+45 the whole length) are mostly gone in 2023. Linear lidar returns at +45..+55: power line.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 200L sand 2 yds out; 210L sand 3 yds out; 230R sand 4 yds out; 240R sand 2 yds out.

Review: `review/h06.png`; evidence: `render/h06_evidence.png`.

### 7 (par 4, Blue 463 yds; tee: tee_axis)

Confidence: medium-high. Zones: first_cut 1, fairway 1, recovery 5, ob 1.

Long straight par 4, very open (2019-lidar tree groups right at 200-280 and left at 210-340 are gone in 2023). Drought image: the irrigated fairway + collar are the only green; the collar is mapped as first cut. A street runs along the right edge (+61): OB.

Zone notes: first_cut: irrigated collar (green in the drought image, pink in CIR) outside the striped fairway; ob: street right (fence line / curb at +61).

No hazard within 10 yds of the fairway edge.

Review: `review/h07.png`; evidence: `render/h07_evidence.png`.

### 9 (par 5, Blue 534 yds; tee: tee_centroid)

Confidence: medium-high. Zones: fairway 1, recovery 16, ob 1.

Par 5 along a residential street (left, OB at the curb); a row of small trees between the street and the fairway, single trees right. Fairway starts at ~170.

Zone notes: ob: street + houses left (line at the course-side curb).

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 200L recovery 6 yds out; 220L recovery 5 yds out; 240L recovery 8 yds out; 270R recovery 0 yds out; 290R recovery 4 yds out; 310R recovery 4 yds out.

Review: `review/h09.png`; evidence: `render/h09_evidence.png`.

### 10 (par 4, Blue 321 yds; tee: tee_centroid)

Confidence: medium-high. Zones: fairway 2, sand 3, recovery 11.

Short par 4 to a green at (+13, 318); trees right (big crowns at 150-220 and 260-340) and small ones left. The tan area left of -35 is drought-dormant mown rough (mowing stripes), not long grass.

Zone notes: fairway: green.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 160R recovery 1 yds out; 170L recovery 0 yds out; 210R recovery 5 yds out; 240L recovery 0 yds out; 260R sand 0 yds out; 270R recovery 8 yds out; 280L recovery 6 yds out; 300L sand 0 yds out; 310L sand 9 yds out; 320L sand 6 yds out.

Review: `review/h10.png`; evidence: `render/h10_evidence.png`.

### 12 (par 5, Blue 519 yds; tee: tee_centroid)

Confidence: high. Zones: fairway 1, recovery 6.

Par 5 in a wooded valley: woods right the whole way (crown edge +15..+35), a cart path and tree groups left. The 2019 lidar and 2023 crowns agree on this hole (no derecho loss in the landing area).

Zone notes: recovery: woods right (lidar edge; 2nd pass moved it 2-3 yds out: the dark band at +13..+19 is crown shadow).

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150R recovery 8 yds out; 160R recovery 8 yds out; 170L recovery 9 yds out; 170R recovery 8 yds out; 180L recovery 10 yds out; 180R recovery 8 yds out; 190L recovery 10 yds out; 190R recovery 8 yds out; 200R recovery 8 yds out; 210R recovery 8 yds out; 220R recovery 10 yds out; 250L recovery 2 yds out; 270R recovery 10 yds out; 280R recovery 8 yds out; 290R recovery 7 yds out; 300L recovery 4 yds out; 300R recovery 6 yds out; 310R recovery 4 yds out; 320R recovery 4 yds out; 330R recovery 4 yds out; 340R recovery 4 yds out.

Review: `review/h12.png`; evidence: `render/h12_evidence.png`.

### 13 (par 4, Blue 350 yds; tee: tee_axis)

Confidence: medium. Zones: fairway 1, recovery 4, ob 1.

Sharp dogleg left (green at -82, 340): the tee line points at a tree belt and the back yards of houses (OB) from ~250 straight on; the landing area is the wide fairway bending left at 230-300. Some 2019-lidar trees left (-70..-40, 145-185) are gone in 2023.

Zone notes: recovery: tree belt in front of the houses (crown edge: lidar + CIR); ob: houses and yards (residential lots ahead / right).

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 210R recovery 9 yds out; 240R recovery 0 yds out; 250R recovery 5 yds out; 260R recovery 4 yds out; 270R recovery 6 yds out; 280R recovery 8 yds out.

Review: `review/h13.png`; evidence: `render/h13_evidence.png`.

### 15 (par 4, Blue 306 yds; tee: tee_axis)

Confidence: medium. Zones: native 2, fairway 2, recovery 9.

Short par 4 (306) to a green at (+3, 305); fairway between two cart paths. Left slope 245-295 is shrubby tall grass (2019 lidar 0.5-2.5 m, dark tufts in 2023): native. Most 2019-lidar crowns left (-45..-20, 195-245) are gone in 2023.

Zone notes: native: shrubs / tall grass on the slope left (lidar 0.5-2.5 m returns, dark tufts in 2023); native: tall grass on the bank right of the right cart path; fairway: green.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 230L recovery 10 yds out; 250L native 0 yds out; 260L native 1 yds out; 270L native 3 yds out; 280L native 6 yds out.

Review: `review/h15.png`; evidence: `render/h15_evidence.png`.

### 16 (par 4, Blue 314 yds; tee: tee_axis)

Confidence: medium-high. Zones: fairway 2, sand 1, recovery 9.

Short par 4 (314) bending slightly left to a green at (-25, 315), between tree groups on both sides (crowns from lidar + CIR; NAIP shadows fall away from the tee here). Cart path right of the fairway.

Zone notes: fairway: green; recovery: crown right of the fairway (lidar crown edge; 2nd pass moved it 8 yds left onto the lidar).

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150L recovery 9 yds out; 160L recovery 10 yds out; 240R recovery 8 yds out; 250L recovery 9 yds out; 260L recovery 6 yds out; 260R recovery 2 yds out; 270L recovery 4 yds out; 270R recovery 2 yds out; 280L recovery 8 yds out; 280R recovery 7 yds out; 290L sand 0 yds out.

Review: `review/h16.png`; evidence: `render/h16_evidence.png`.

### 17 (par 5, Blue 569 yds; tee: tee_centroid)

Confidence: medium. Zones: fairway 1, native 2, sand 1, recovery 9.

Long par 5: the fairway runs right of a dormant-rough slope with single trees and a bunker (left), past two shrubby tall-grass ridges at 270-340 (native). The 2019-lidar crowns at (-45..-10, 140-235) are mostly gone in 2023 (one big tree at (-14, 218) remains).

Zone notes: native: shrubby tall-grass ridge (lidar 0.5-2.5 m, tufted in 2023); native: shrubby tall-grass ridge right; recovery: tree row along the right cart path.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 210L recovery 9 yds out; 220L recovery 4 yds out; 260R recovery 10 yds out; 280R native 0 yds out; 290L native 4 yds out; 290R native 0 yds out; 300L native 4 yds out; 310L native 9 yds out.

Review: `review/h17.png`; evidence: `render/h17_evidence.png`.

### 18 (par 4, Blue 418 yds; tee: tee_axis)

Confidence: high. Zones: fairway 1, sand 1, recovery 6.

Wide fairway with woods tight on the right (the cart path runs along the tree line), tree groups left. Crown edges from lidar + CIR agree to ~2 yds.

Zone notes: recovery: woods right of the cart path (lidar + CIR crown edge; 2nd pass: 3-5 yds out at 190-260, shadows excluded); recovery: 2nd pass: moved onto the lidar / CIR crown.

Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): 150R recovery 2 yds out; 160R recovery 3 yds out; 170R recovery 4 yds out; 180R recovery 5 yds out; 190R recovery 6 yds out; 200R recovery 7 yds out; 210R recovery 8 yds out; 220R recovery 7 yds out; 230R recovery 6 yds out; 240L recovery 0 yds out; 240R recovery 7 yds out; 250R recovery 6 yds out; 260R recovery 6 yds out; 270R recovery 2 yds out; 280L recovery 8 yds out; 280R recovery 7 yds out; 290L recovery 8 yds out; 290R recovery 8 yds out; 300L sand 0 yds out; 320L recovery 0 yds out; 330L recovery 0 yds out.

Review: `review/h18.png`; evidence: `render/h18_evidence.png`.

