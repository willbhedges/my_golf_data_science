# Gateway National par 3s: aim box for an unknown pin, and the plays-like number (Nov 9 2026)

Holes 4, 7, 12, 14 and 17 (Back 180 / 180 / 131 / 200 / 195), every tee set. The page's par-3 box was the DECADE box
(`yardage_book.par3_plan`: cushions in from each edge, the worse side first). This page replaces it with the
**expected-strokes optimum for a pin anywhere on the green, on Will's own iron pattern**. It is the method of Eagle
Knoll (`eagle_knoll/OPTIMIZE.md` section 13). The model code is imported unchanged from
`eagle_knoll/opt/par3_target.py`. Only the course wiring, the two ends of the bag and the forecast are Gateway's.

* Script: `opt/par3_target.py` (`solve`, `robust`, `mapvar`, `numbers`, `page`).
* Results: `opt/results/par3_target_<set>.json` (surfaces (coarse grid for Back only), clubs, SEs), `opt/results/par3_robust.json` (sensitivity and
  map variants) and `opt/results/par3_numbers.json` (plays-like by temperature and wind).
* Page file: `par3_targets.json`. It is read by `course_data/courses/par3_targets.py` once the config has
  `"par3_targets": "course_data/courses/gateway_national/par3_targets.json"`. It is not wired yet, because the engine
  agent owns `config.json`.

## 1. Method

**Ball** (the engine's `model.shots` at the central world):
* Lateral sigma = 95 % width / 4 x 70/65. Carry sigma = depth window x 1.25 / 4. rho 0.1.
* Mishits: 12 % slight (92-95 % carry) and 2.5 % heavy (65-85 %).
* Temperature: carry x (1 - 0.00075 (70 - T)).
* Wind: `wind.adjust`, including gust scatter. The mean drift is aimed off.
* Clubs:
  * **Engine numbers:** Long iron 210, Mid iron 185 and 4-wood 255. These are Will's numbers (mid iron ~184).
  * **From the brief:** 8-iron 162, assumed.
  * **Assumed exactly as at Eagle Knoll:** 5-iron 198, 7-iron 174, 9-iron 150, PW 138 and GW 126. They come from the
    Spirit Hollow approach bag (~12-yd gaps), with width and depth window scaled with carry like the engine's 8-iron.
    This is where Eagle Knoll's PW 138 came from.
  * **Assumed for Forward / Middle 12:** SW 113 and LW 100.
  * Nothing sits between 210 and 255 (the engine's "Hybrid ~235" is marked not in the bag).
* The aim surface uses an ideal club for each depth: carry interpolated, with that carry's width, depth and roll. So
  the box does not depend on the gapping. The club table does.

**Terrain:**
* The truth package is loaded per tee set through the page's own loader, so each set has its own tee, line and frame.
* Each ball lands where its flight meets the 3DEP 1 m DEM (`packages/gateway_national/imagery/dem.tif`):
  x = flat carry + 0.839 x (tee height minus ground height). 0.839 = 1/tan 50 deg, the page's elevation factor.
* It then rolls the club's stated roll (+/-25 %): about 2.5 yds for a PW, 6 for a 7-iron, 8 for a 5-iron and 10 for a
  4-iron. Roll is x0.3 in rough, and the ball stops in sand, trees or water.
* **The box is the landing spot and the number is the carry.** The ball finishes about one roll past the box.

**Green and pins:**
* The green is the truth-map polygon.
* Pins are uniform over it, at least 4 yds inside the edge (222-288 pin spots per green on a 1-yd grid).
* Putting: Broadie by feet + 0.06, plus the slope term (an assumed size): 0.02 strokes per 1 % of downhill grade, from
  the DEM plane fit.

**After the shot:**
* Short game by lie + 0.15 within 40 yds; beyond that, the engine's table.
* Trees: Broadie recovery. Water: 1 + rough from the drop.

**Statistics:**
* Common random numbers throughout.
* Back: 6,000-swing 1-yd grid, then a 0.5-yd refine on 40,000 fresh swings. The other sets use 3,000 / 16,000.
* The centre and DECADE aims are scored on the refine swings. Margins are paired means +/- SE.
* Box = aims within 0.02 strokes of the best, at least 4 yds each way.
* One box per page wind class: calm, and 7 / 14 / 24 / 32 mph averaged over four directions. Back solves every class;
  the other sets copy classes 1-3 from class 0 (on Back they differ by 0.5 yd or less).

**Forecast** (`weather/forecast_gateway_national.json`, fetched Nov 7): conditions at each hole's time, with a 9:00
shotgun on 1 and 14 min a hole (4 at 9:42, 7 at 10:24, 12 at 11:34, 14 at 12:02, 17 at 12:44).
* Sat: NNW 8-9 mph, 41-49 F.
* Sun: SW 6.5-7.5 mph, 48-58 F.

## 2. Map and terrain check (imagery, lidar)

Each green and its surround was checked against these sources:
* NAIP 2023 RGB (0.6 m and the package's 0.3 m) and the 0.3 m NIR as CIR;
* NAIP 2022 CIR;
* the 2014 Madison Co. lidar HAG and DTM;
* the truth-map polygons overlaid, with 10-40 yd rings.

The renders were scratch only.

| hole | green outline | around it (in the tee frame) | verdict |
|---|---|---|---|
| 4 | matches the smooth putting surface; the green runs front-right to back-left | two bunkers short-left (match); mown rough left and long to the path at 195-200; trees and OB right from ~+40 | OK |
| 7 | matches (the surface may run ~1-2 yds further right than mapped; no effect) | bunker right, small bunker short-left; trees short-left (2014 canopy, thinner on NAIP 2023); native long-right from ~3 yds past the back-right edge (map fix of Nov 9), trees long-right; pond beyond | OK |
| 12 | matches | peninsula: water left (~3-5 yds off the edge), long (~22 yds past the centre at the line) and a creek 24-30 yds short; bunker long-right | OK, CIR water edges match the map |
| 14 | matches (NAIP 2023 is the reference; NAIP Plus is older and shadowed here) | bunker left; tree line 1-3 yds behind the back edge (canopy edge = map edge within ~2 yds); trees left beyond the bunker; native strip down the left of the corridor 0-185 yds (map fix of Nov 9), 30+ yds from the centre | OK |
| 17 | matches | three bunkers short-right, one left; trees right 5-8 yds off the edge; trees long beyond the cart path | OK; the "trees long" polygon takes in the path strip (3-5 yds, 25-30 yds past the centre), no effect |

No native or prairie lies within ~12 yds of any par-3 green. The par 3s were never hand-traced: their surrounds are
OSM bunker / water / fairway plus lidar canopy. Reviewer A (EYECHECK_A_1109.md) found the same for 4.

**Map revision.** Everything here is on the truth package as rebuilt on Nov 9 (commit 5403fb168). That revision added
native on 7 and 14. 4, 12 and 17 are unchanged in it (same zones, tees and green), so their results stand. 7 and 14
were re-solved for every set. Lies are painted in package order, as the page's `lie_at` does: later zones win, so where
the new native bands overlap the lidar trees, the trees stay. The Back boxes for 7 and 14 did not move; on the other
sets, the 14 boxes moved by 0.5-1 yd at most.

Three map questions were run as variants (`mapvar`). Each gives the regret of keeping the page aim:
* **4, if the smooth "fairway" lobe left of the green is putting surface** (reviewer A's note; pins there too): best
  (0, -5), regret 0.009 +/- 0.001.
* **4, reviewer A's C4** (native 24-54 yds past the centre): best (2, -5), regret 0.000.
* **7, if the 2014-lidar trees short-left are now rough:** best (-1, -4), regret 0.002 +/- 0.001.

**There is no map error near a par-3 green that changes a box, so no polygon edit is proposed.**

**Lidar.** The 3DEP DEM and the 2014 lidar DTM agree on the greens:
* plane-fit grades within 0.25 % and drops within 1 ft, with residual 0.1-0.2 ft;
* tee-to-green drops, Back: 4 -2.8 ft (uphill), 7 +0.8, 12 +2.3, 14 +2.5, 17 +2.5. That is under 1 yd of plays-like.

Green tilt (fall line, DEM):

| hole | tilt |
|---|---|
| 4 | 1.5 % up to the right, 1.0 % back-to-front |
| 7 | 1.6 % back-to-front, 0.8 % up to the right |
| **12** | **3.65 % right-to-left**, falling toward the water left |
| 14 | 0.45 % (flat) |
| 17 | 1.6 % back-to-front |

**Card vs map.** On 4 and 7 the map's tee-to-centre is 4-5 yds shorter than the card for every set:
* Back 176 / 176 against 180 / 180;
* Tips 192 / 199 against 197 / 204;
* Middle 7 155 against 160 (the Middle tees on 7 and 12 are estimated).

The page builds its number from the card, so on those two holes the page number is ~4 yds longer than the model's
carry to the same spot. **On the day, take the distance to the green centre from the tee plate or a laser, and add the
box depth.**

## 3. Result: Back

Depth is + long of the green centre, lateral is + right. Strokes are for the hole. The plays-like number is the carry
in 70 F, flat-ground yards.

| hole | best aim (lat, depth) | box lat / depth | EV | gain vs centre aim | gain vs old DECADE aim (its lat, depth) | plays like, 50 F calm: page (card) / model (map) [to centre] | 35 F / 65 F | 10 mph head / tail |
|---|---|---|---|---|---|---|---|---|
| 4 (180) | **+2.5, -5.5** | -1..5 / -8..-3 | 3.192 | **0.067 +/- 0.001** | 0.049 +/- 0.001 (1.8, -1.1) | **178** / 174 [180 / 179.5] | 180 / 176 | 191 / 170 |
| 7 (180) | **0, -3.5** | -3..2 / -6..-2 | 3.194 | **0.032 +/- 0.001** | 0.039 +/- 0.001 (-0.5, +0.4) | **179** / 175 [178.4] | 181 / 177 | 192 / 171 |
| 12 (131) | **+0.5, -1.5** | -2..2 / -3.5..0.5 | 3.069 | 0.007 +/- 0.001 | 0.007 +/- 0.001 (1.8, -1.6) | **131** / 131 [132] | 132 / 129 | 141 / 125 |
| 14 (200) | **+0.5, -6.5** | -3..3 / -10..-4 | 3.281 | **0.100 +/- 0.002** | 0.063 +/- 0.001 (1.0, -1.2) | **196** / 196 [202] | 198 / 194 | 210 / 187 |
| 17 (195) | **-1.5, -6.5** | -4..1 / -9..-4 | 3.244 | **0.090 +/- 0.001** | 0.049 +/- 0.001 (-1.8, -1.6) | **191** / 188.5 [195] | 193 / 188.5 | 205 / 182 |

How the numbers are built:
* Page = (card + aim depth + dz) / temperature factor. This is the template's formula and what the page will show.
* Model = the carry that lands a solid strike on the aim, at the map distance and the DEM height there.
* The wind column is the page's `wind_grid.plays_like` at 50 F. A crosswind does not change the number.

**Wind classes and the forecast days barely move the box:**
* 7-32 mph: within 1 yd of calm (14: -7..-7.5; 17: -7).
* Sat / Sun best aims:
  * 4: (2, -5.5) / (2.5, -6.5)
  * 7: (0.5, -3.5) / (0, -3)
  * 12: (0.5, -1.5) / (0.5, -2)
  * 14: (1, -6.5) / (1, -6.5)
  * 17: (-1.5, -7) / (-1, -6)
* Model carries to those aims, Sat / Sun:

  | hole | Sat | Sun |
  |---|---|---|
  | 4 | 169 (tail-ish, 41 F) | 179 (into, 48 F) |
  | 7 | 176 (across) | 170 (helping) |
  | 12 | 134 | 134 |
  | 14 | 194 | 189 |
  | 17 | 190.5 | 181.5 (helping) |

**Why the boxes sit short.** These are long par 3s, played with 5- to 7-irons that roll 6-8 yds. The model lands the
ball 3.5-6.5 yds short of the centre, so it **finishes at about the centre**. A centre landing finishes 6-8 yds long.
On 14 and 17 the trees are 1-8 yds behind the green, so that miss is expensive: 0.09-0.10 strokes a hole. Laterally:
* 4 aims 2.5 right, onto the wide front-right half of a diagonal green and away from the short-left bunkers.
* 17 aims 1.5 left, away from the trees right.
* 12 is the exception. It is a short club with little roll onto a peninsula, and the box is the centre (gain 0.007).
  Half a yard right, toward the high side and away from the water, is a wash.

**Club** (stock carries, lateral aim optimised; margin over the runner-up). This depends on the **assumed** 5- / 7- /
9-iron / wedge carries.

| hole | calm 50 F | Sat | Sun |
|---|---|---|---|
| 4 | 7-iron by 0.21 (lands -5.4) | 7-iron by 0.04 | 6-iron / 7-iron TIE |
| 7 | 7-iron by 0.29 | 7-iron by 0.21 | 7-iron by 0.07 |
| 12 | GW by 0.09 (lands -6) | PW by 0.15 | PW by 0.18 |
| 14 | 5-iron by 0.14 | 5-iron by 0.09 | 6-iron by 0.14 |
| 17 | 6-iron by 0.15 (lands -10) | 6-iron by 0.05 | 6-iron by 0.06 |

## 4. Sensitivity (Back; `robust`: 4,000-swing grid, 20,000 fresh swings)

Each cell gives the best aim under the variant, then the regret of keeping the page aim.

| variant | 4 | 7 | 12 | 14 | 17 |
|---|---|---|---|---|---|
| temp 35 F / 65 F | (3,-6) / (2,-5); 0.000 | (0,-4) / (0,-3); 0.000 | (0,-2) / (0,-1); 0.001 | (1,-7); 0.000 | (-1,-8) / (-1,-7); 0.000 |
| dispersion +/-15 % | (2..3,-6); <= 0.001 | (0..1,-4); 0.000 | (0..1,-1); 0.000 | (0..1,-6..-7); <= 0.002 | (-1..-2,-7); 0.001 |
| depth spread x2 | (3,-6); 0.001 | (1,-4); 0.006 | (0,-1); 0.000 | (3,-9); 0.010 | (-3,-8); 0.002 |
| 10 mph head / tail | (3,-7) / (2,-6); 0.005 / 0.000 | (0,-5) / (0,-3); 0.000 / 0.001 | (0,-2) / (0,-1); 0.001 | (1,-9) / (1,-6); 0.014 / 0.001 | (-2,-8) / (-1,-6); 0.006 / 0.001 |
| 10 mph from left / right | (2,-6); 0.000 | (0,-3); 0.000 | (0,-2); 0.000 | (1,-7); 0.000 | (-1,-7); 0.000 |
| 20 mph head | (3,-9); 0.023 | (2,-7); 0.022 | (2,-3); 0.010 | (2,-13); 0.055 | (-3,-12); 0.035 |
| **roll x0.5 (soft greens)** | (1,-3); **0.017** | (-1,-1); 0.011 | (0,0); 0.001 | (1,-3); 0.010 | (-1,-4); 0.014 |
| roll x1.5 (firm) | (3,-8); 0.020 | (-1,-5); 0.008 | (0,-2); 0.002 | (1,-9); 0.018 | (-2,-10); 0.020 |
| **carry +5 / -5** | (2,-10) / (2,-1); **0.064 / 0.048** | (0,-8) / (0,+1); 0.059 / 0.055 | (0,-6) / (0,+3); 0.074 / 0.080 | (1,-12) / (1,-2); 0.046 / 0.032 | (-1,-12) / (-1,-3); 0.044 / 0.031 |
| no slope / slope x2 | 0.000 | 0.000 | 0.001 | 0.000 | 0.000 |
| trees half the cost | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| no mishits | 0.003 | 0.005 | 0.004 | 0.001 | 0.003 |
| pins 3 / 6 yds in | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

* **The box is robust.** Temperature (35-65 F), dispersion (+/-15 %, depth x2), crosswind and wind to 10 mph, the
  slope term, tree cost, pin inset and mishits all leave the page aim within 0.015 strokes of the variant's best,
  usually within 0.005. The variant's best is within 1-1.5 yds (14 into 10 mph: 2.5 yds).
* **Into a strong wind, land it shorter.** At 20 mph into, 14 wants -13 (regret 0.055) and 17 wants -12 (0.035). The
  page's wind-class boxes average the four directions, so they do not know about this. Rule of thumb: into the wind,
  pick the short end of the box.
* **Green firmness is the main model uncertainty.** The box is a landing spot, so it moves with the roll: soft greens
  land 2-3 yds deeper, firm greens 2-3 yds shorter. The cost of not adjusting is 0.01-0.02. On soft November greens
  (dew, rain) take the long end of the box. If the ball is checking up, land it nearer the centre.
* **The number matters more than the box.** If Will's carry with the club is 5 yds off the model, he loses 0.03-0.08 a
  hole at the page aim. **Confirm the 5- / 7-iron and wedge carries with Will**; they are assumed.

## 5. Other tee sets (own tee, own frame; 3,000 / 16,000 swings)

Columns: best aim, box, gain vs centre, gain vs DECADE, plays like at 50 F calm (page from card / model from map).

| set | 4 | 7 | 12 | 14 | 17 |
|---|---|---|---|---|---|
| The Tips | (2,-6.5), -1..5 / -9..-5; 0.093; 0.083; 194 / 189 | (0.5,-5), -3..3 / -6.5..-2.5; 0.076; 0.113; 202 / 197 | (1,-2.5), -1..3 / -4.5..-0.5; 0.020; 0.006; 153 / 152.5 | (1.5,-11), -2..5 / -14..-8; 0.206; 0.125; 232 / 232 | (-2.5,-10), -6..0 / -13..-7; 0.161; 0.087; 224 / 219 |
| Champions | (2,-6.5), -1..5 / -9..-4; 0.092; 0.080; 191 / 187 | (0.5,-4.5), -3..3 / -7..-2; 0.059; 0.083; 198 / 193.5 | (0.5,-2), -1..3 / -4..0; 0.015; 0.006; 147 / 146 | (1.5,-10.5), -2..5 / -13..-8; 0.198; 0.120; 228 / 229 | (-3,-9.5), -6..0 / -12..-6; 0.152; 0.090; 218 / 215 |
| Middle | (2,-3.5), -1..4 / -6..-2; 0.031; 0.017; 153 / 150 | (0,-2.5), -3..1 / -5..0; 0.017; 0.021; 160 / 155 | (0,-1), -1.5..2.5 / -3..1; 0.005; 0.012; 115 / 114 | (0,-5.5), -3..3 / -8..-3; 0.067; 0.038; 181.5 / 182 | (-1,-5), -3..1 / -7..-3; 0.059; 0.033; 170 / 168 |
| Forward | (1.5,-2.5), -1..4 / -4..0; 0.011; 0.005; 130 / 129 | (-1,-2), -3..1 / -4..0; 0.014; 0.024; 145 / 142 | (-0.5,0), -2.5..1.5 / -2..2; 0.001; 0.035; 91 / 92 | (0.5,-3), -3..2 / -6..-1; 0.023; 0.010; 154 / 154 | (-0.5,-3.5), -3..1 / -6..-1; 0.035; 0.019; 154 / 153 |

The pattern is the same on every set: land short by about one roll. The longer the club, the shorter the landing,
because the roll and the long misses grow with it.

**Tips and Champions 14 (232 / 228 to play) and 17 (224 / 218).** These fall in Will's gap between the long iron
(210) and the 4-wood (255):
* The model's best real club is the long iron, landing 14-33 yds short. The 4-wood flies into the trees long.
* The page's number is the ideal carry, not one of his clubs.
* Back is the event set, so this is a note for the tee picker only.

**Forward 12 (90).** A partial lob wedge. The bag model has no partial shots, so the club margin there means nothing.

**Drawing.** The page draws every set's box in the Back frame, rotated by the tee-angle difference: 8.5 deg on Forward 4 and
12, and about 5 deg on Forward 14 and Tips 7. That moves a corner by at most ~1 yd. The depth used for the number is the
set's own.

## 6. Uncertainty / not verified

* The pins are uniform, not the day's sheet.
* The slope term's size is assumed (0 and x2 shown: no effect here).
* The DEM / lidar is 2014-15, so greens rebuilt since would not show.
* The roll is the club's fairway roll, applied to greens: see the roll rows.
* The short-iron and wedge carries are assumed. Card vs map is 4-5 yds on 4 and 7.
* Lateral wind drift is aimed off, not modelled as a miss. The wind classes are direction-averaged (see the 20 mph
  into row).
* Water banks are not modelled (12): a ball stopping on the rough bank stays dry.

## 7. To wire it (engine agent)

Add to `course_data/courses/gateway_national/config.json`:

```
"par3_targets": "course_data/courses/gateway_national/par3_targets.json"
```

The engine then calls `par3_targets.install(cfg, BW, meta["tee_set"])` (v2_course.py ~l.1193). No other key is needed.
The Middle alt-base page (`truth_middle`, tee_set Middle) takes the file's own Middle entries.
`par3_targets.json` covers all five sets. `d["p3club"]` names the club for the two forecast days. On Tips and
Champions 14 / 17 it reads "4-iron", which lands 14-33 yds short; a template showing p3club should not show it for
those sets.
