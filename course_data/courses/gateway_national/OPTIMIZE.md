# Gateway National: page, engine, map fixes and re-solve (Nov 9-12 2026)

For Will (KU club golf), NCCGA Regional 3, Gateway National Golf Links (Madison IL), Sat-Sun Nov 14-15 2026, Back
tees (6,623). Same process as Eagle Knoll (`course_data/courses/eagle_knoll/OPTIMIZE.md`, Nov 3-8), which went well.
Scripts: `opt/` (copied from Eagle Knoll's `opt/` and made course-generic: `SLUG` env, default gateway_national).

## 1. Page display (Nov 9)

Golfer feedback from Eagle Knoll: the first photos were blurry (par 3s worst); no hazard outlines or hazard words on
the page; the current club above the hole number (the shared template already does that).

* **Photos:** config `display_imagery` = Eagle Knoll's (USGS NAIP Plus at 0.3 m, rendered directly at page size with
  Lanczos, 900 px, unsharp mask, par 3s show a 150-yd view, alt-base photo sharing), `fallback_year` 2023 (the year
  the truth map was checked on; the IL 2023 NAIP item is itself 0.30 m: `il_m_3809023_se_15_030_20230819`).
  Rebuilt through `display_imagery.yml` (request `course_data/requests/display_gateway_national.json` rev 1, run
  42647177803): NAIP Plus fetched (6,677 x 5,457 px at 0.3 m, 20 tiles, no fallback), 18 photos rendered directly.
* **Superseded the same day: the page photo is now NAIP 2023 (config `display_imagery.year` 2023).** Putting the
  NAIP Plus photo beside the 0.30 m NAIP 2023 photo of 14 (the package imagery, rendered the same way) shows NAIP Plus
  serves an *older, shadowed* image at Gateway: a different bunker left of the green, different green and collar
  shapes, long tree shadows over the green (the reason the 14 outline looked as if it ran into the trees). The truth
  map was traced on NAIP 2023, and on it the 14 outline sits on the green (RGB and CIR). NAIP 2023 is also sharper
  (page-photo Laplacian 1.60-2.23 against 1.25-1.59 for NAIP Plus, every hole). The nccga-v2 merge fetches it
  (Planetary Computer, 0.3 m).
* **Sharpness check** (mean absolute Laplacian of the page photos, the same measure at the same 900-px scale):
  Gateway par 3s 1.25-1.55, tee shots 1.29-1.59; Eagle Knoll's final page (accepted by the golfer) par 3s 1.40-1.53,
  tee shots 1.24-1.84. The same 0.3 m source detail; nothing sharper exists for this ground. I looked at the par-3
  photos (4, 7, 12, 14, 17) at full size: greens, bunkers, cart paths and the tee boxes are crisp at 2x the source;
  the green outline sits on the green in the photo on 4, 7, 12 and 17; on 14 the top-left of the outline runs into
  the tree shadow (August photo), left to the hole 13-18 map review (section 3).
* **No hazards:** config `page_text.hide_hazards` (no water / OB outlines, hazard words dropped from the notes).
  Gateway has no `hole_notes`, so `map_notes` is empty. qa_page.js text scan on every hole: no water, pond, creek,
  bunker, sand, tree, OB, fescue, prairie or "long grass" word appears (only "2-wood / 4-wood").
* **qa_page.js on the rebuilt page:** The Tips, Champions, Back, Middle, Forward: 18 / 18 holes, 0 problems each.

## 2. Engine options (Nov 9)

Eagle Knoll's engine options (`config.engine`, OPTIMIZE.md sections 7 and 12) checked one by one for Gateway.
Central-world two-stage solve (`opt/solve2.py`: 3,000 swings on -60..+60, then 16,000 fresh common swings on aim
+/-10), Back, every tee shot, three engines side by side (margin over the runner-up, strokes; paired SE 0.001-0.004):

| hole | engine as solved Oct 17 (`V2_ENGINE=0`) | + 8-iron + green putting | + lidar flight trees |
|---|---|---|---|
| 1 | Driver -7.5 (0.050) | same | same (0.050) |
| 2 | Driver +1.5 (0.078) | same | 0.077 |
| 3 | Driver -7.5 (0.062) | same | 0.062 |
| 5 | Driver -1 (0.088) | same | same |
| 6 | Driver +6.5 (0.116) | same | 0.116 |
| 8 | 2-wood -36 (0.021 vs Driver) | same | same |
| 9 | 4-wood 0 (0.016 vs 2-wood) | same | 0.016 |
| **10** | **4-wood -15 (0.004 vs 2-wood: a tie)** | **4-wood -16.5 (0.032 +/- 0.004)** | same |
| 11 | 4-wood +6 (0.068) | same | same |
| 13 | Driver -1 (0.137) | same | same |
| 15 | Driver +14.5 (0.102) | same | same |
| 16 | 4-wood -2 (0.052) | same | same |
| 18 | Driver +15 (0.133) | same | Driver +14.5 (0.133) |

### 2a. Green putting: ON (it matters on the drivable 10th)

The bug Eagle Knoll's panel found (OPTIMIZE.md 12d) is general: the tee-shot raster has no green lie, and the tables
stop at 20 yds, so a tee ball on the green scored as fairway-at-20 yds. On Gateway it decides 10 (271 yds from
Back): with putts on the green every club near the green gets cheaper (4-wood 3.837 -> 3.612, 2-wood 3.841 -> 3.643,
Driver 3.918 -> 3.865), and the 4-wood-vs-2-wood tie becomes 4-wood by 0.032. No other Back tee ball reaches 20 yds
of a hole; the other holes are unchanged.

### 2b. 8-iron: ON (no Back pick uses it)

Added as on Eagle Knoll (162 / 167 carry / total, width 30, depth 16; assumed gapping below the 210 long iron,
**confirm with Will**). It is never within 0.07 of the pick on a Back tee shot (10: 8-iron 4.14 vs 4-wood 3.61).
It is there for the forward sets and the moved tees.

### 2c. Lidar flight-path trees: NOT enabled (they do not matter here, and the canopy file has artefacts)

* **The file:** `vision_any/gateway_national/raw/hag.tif` is the USGS 3DEP Madison Co. IL lidar (2014-03-23..31,
  leaf-off), height above ground, uint8 in **0.25 m units, nodata 255** (file tags and meta.json; the same encoding
  as Eagle Knoll's), 1 m grid, EPSG:32615. 0.5 % nodata (the ponds: no returns from water).
* **Artefacts:** at the pond edges the HAG has interpolation spikes, e.g. hole 2 at 130 yds, 24-29 yds left: a block
  of value 215 (53.8 m) beside the nodata void, ramping 156 / 98 / 59 (39 / 25 / 15 m) toward the shore, class 0 in
  the classification raster. A flight check would read those as 55-m trees. If the option is ever enabled here,
  water must be in `exclude` and crowns over ~35 m dropped.
* **Where the trees are:** crown cells (lidar >= 2.5 m + 3 m growth, OB / water masked) in the descent corridor
  (150-320 yds, +/-45) of each Back tee shot (`opt/canopy_check.py`): none on 1, 2, 5, 11, 13, 15, 16; 10 cells
  on 10 (a single small tree, 6 yds high); 186-1,463 on 3, 6, 8, 9, 18, almost all on the mapped trees (the tree map
  came from this lidar), medians 8-17 yds high (p90 10-23).
* **Does it matter?** With the Eagle Knoll model (k = 0.10 / yd) the picks, aims and margins of every hole change by
  at most 0.0004 strokes and 0.5 yd (table above). Worst case (+6 m growth, k = 0.25 / yd, summer-like): 3, 6, 8, 9,
  18 keep club and aim, margins within 0.0003 (the share of balls stopped in crowns is 0-2 %). Gateway's trees stand
  back from the lines, below the descending ball: a ball that reaches them was already finishing in them.
* The Meta canopy fill Eagle Knoll used (for trees grown in since its lidar) would be wrong here: Gateway's tree map
  was traced FROM this lidar (> 2.5 m), so a mapped tree cell without a 4-m crown is a crown edge or a 2.5-4 m tree,
  not a missing tree, and the fill would put a 10-m default crown on it. Meta's heights also run 1-12 m under the
  lidar on the same cells (its known bias), so they give no growth estimate either.

### 2d. Monte Carlo precision (as Eagle Knoll ended up)

* Calm-day book: 256 prior draws per hole (was 64 here; config `draws` 256 for the page text).
* Card-tee wind grids: `refine_swings` 16,000 (second stage on aim +/-10, `v2_course.refined_solver`; Eagle Knoll
  section 2: median SE of a margin 0.0033 -> 0.0012, unresolved cells 13 -> 1 on Back). Moved-tee offsets stay
  coarse (2,500).
* `nccga_v2.yml` gains `wind_split` (a refined offset's holes dealt over several jobs) and `wind_holes` (wind jobs
  limited to some holes; the merge keeps the stored grid's other holes): 13 refined tee shots x 183 cells x ~25 s on
  4 cores is ~4 h, too close to the 300-min job limit for one job.

### 2e. General fixes from Eagle Knoll that Gateway already gets

* Hole temperature: the stored Gateway book (Oct 17) was decided at the 48 F fallback on every hole (`temp_f` 48.0
  in `v2_decisions.json`): the `hole_temp` default fix (Oct 24) came after it. The re-solve uses the forecast
  temperature per hole.
* Par-3 plays-like temperature term, the tee-frame landing oval, the 5-yd tee slider, close-call badges, moved-tee
  notes: template / page code, already on this page.

## 3. Map fixes from the Nov 9 eye check (EYECHECK_A/B/C_1109.md)

Three reviewers checked holes 1-6, 7-12 and 13-18 on NAIP 2023 0.3 m RGB + CIR, NAIP 2022 and the 2014 lidar. I
applied every must-fix and should-fix edit, plus 13's Tips tee, and checked each one on a render
(`opt/lie_render.py`: the course module's lie map painted over the NAIP 2023 photo in the page frame; `geo_crop`
panels RGB / CIR / 2022 / lidar for the tees and the par 3s).

* **Source of truth:** `truth/gateway_national/trace.py` (EXTRA / LATE bands, each edit commented) and
  `holes_truth.py` (`TEE_FIX`, par-3 `EXTRA_ZONES`). `opt/map_edits.py` puts the edited bands into
  `hand_zones_ll.json` and keeps every other stored zone. A full `corridor.py build` would also re-read the Nov 4
  package OSM, which moved a few fairway vertices on 13, 15 and 18 since Oct 17. It then rebuilds
  `courses/gateway_national/truth/package.json` with `score_auto.truth_package`. Before the edits that call reproduced
  the stored package exactly. Unedited holes 1, 2, 5, 6, 9, 10: zones byte-identical. The reviewers' WGS84 rings
  agree with the converted bands within 5e-8 deg.

| hole | edit | reviewer | checked on the render |
|---|---|---|---|
| 2 | **Back tee moved to its own pad (OSM way 719497753, [-90.1434917, 38.663402])**. The old tee was hole 18's rear pad, 54 yds left, behind an 8-20 m tree block | A (M1) | The new point is on the mown pad between Champions / Tips and Middle, on the line SW. The old point is on 18's pad chain heading SSE (RGB, CIR, lidar) |
| 3 | tree / shrub line right x +32..+44 (recovery), then the industrial yard x +44..+65 (**OB**), 145-345 | A (M2) | The OB band lies on the paved yard and buildings, the recovery band on the shrub line |
| 7 (par 3) | native long-right of the green | B | Tan, mottled in CIR, outside the mown collar |
| 8 | fescue inside the dogleg, from the fairway's right edge to the trees, 225-300 | B | The tan grass right of the fairway bend |
| 11 | left prairie inner edge 5-9 yds off the fairway at 160-280; right fescue from the cart path out (was 15-20 yds inside it) | B | Both bands now off the fairway, the right one beyond the path |
| 13 | right fescue inner edge 20 -> 50 up the hole (was a flat 32); left "fescue strip" removed (mown rough); native / wetland between the left path and the ditch; **The Tips** tee to the back of the Champions pad (card +5; was a lidar pad 50 yds right across the ditch) | C | Yes |
| 14 (par 3) | native strip down the left of the tee-to-green corridor, 0-185 | C | On the dark textured CIR band left of the approach |
| 15 | left prairie inner edge 5-10 yds out before the bunkers; "prairie right" removed (mown rough); fescue beyond the cart path at 230-345 | C | Yes |
| 16 | both right bands replaced by one from the cart path out | C | Yes |
| 18 | left fescue swings out with the cart path from 260 | C | Yes |

Not applied (cosmetic: out of reach, or no effect on any shot): 1 C1 (a vision water triangle 40-80 yds out), 2 C2
(native right beyond the path, 25-35 yds off the fairway), 3 C3 (Forward tee), 4 C4, 5 C5, 7 short-left
recovery -> native (both penal), 8 the native square at 303-337 L, 9 R fescue (kept: uncertain, p 0.46), 10
Tips / Champions walkback, 12 water short-left, 14 R native 25+ yds off line, 18 water basin by the tees, OB
outside 13-18 (nowhere near a corridor).

Manager's questions:
* **14 green outline:** correct. On NAIP 2023 RGB and CIR the OSM outline sits on the putting surface. The "tree
  shadow" was the NAIP Plus photo (section 1).
* **15 Back tee chute:** no nudge. With flight trees off, the engine prices only where the ball finishes. Every
  modelled swing finishes 150+ yds out (heavy mishits carry 65-85 %), so canopy 5-40 yds from the tee cannot
  change anything. On the course the chute is real and open on the 2023 photo.
* **2 Back tee:** the highest-impact fix. From the real pad the Driver aim moves from 1.5 yds right of the line to
  16 right (central world, section 4), and the line and yardages are now the right ones.

Middle as an alt base: the NCCGA's Nov 2025 setup (6,377) mixed Back and Middle boxes, so Middle
(`truth_middle`, config `alt_bases`) is solved from its own pads like Eagle Knoll's Middle. The hand footprint
starts 145 yds from Back. Middle 3 is 64 yds ahead, so its long drives land past the 345-yd footprint end, where
the auto layers apply (OSM, lidar, and the package OB along the yard).

## 4. Re-solve on the final map and engine

### 4a. Central world, Back (`opt/solve2.py`, two-stage, paired SE; forecast temperatures)

Pick and aim (yds, + = right of the page's tee line) and the margin over the runner-up. "Old map" is the same
engine (8-iron, green putting) on the Oct 17 map; "stored" is the page's book before this work (Oct 17, 64 draws,
48 F):

| hole | stored book | old map | **final map** |
|---|---|---|---|
| 1 | Driver -7 | Driver -7.5 (0.050) | Driver -7.5 (0.050 +/- 0.001 vs 2-wood) |
| 2 | Driver +2.5 | Driver +1.5 (0.077) | **Driver +16** (0.070 +/- 0.001 vs 2-wood): the real Back pad |
| 3 | Driver -7.5 | Driver -7.5 (0.062) | Driver -8.5 (0.056 +/- 0.001 vs 2-wood): OB right |
| 5 | Driver -1 | Driver -1 (0.088) | Driver -1 (0.088 +/- 0.001) |
| 6 | Driver +6 | Driver +6.5 (0.116) | Driver +6.5 (0.116 +/- 0.001) |
| 8 | 2-wood -37 | 2-wood -36 (0.021) | 2-wood -39.5 (0.022 +/- 0.001 vs 4-wood): fescue inside the dogleg |
| 9 | 4-wood +0.5 | 4-wood 0 (0.016) | 4-wood 0 (0.016 +/- 0.002 vs 2-wood) |
| 10 | 4-wood -14 (TIE) | 4-wood -16.5 (0.032) | 4-wood -16.5 (0.032 +/- 0.004 vs 2-wood): green putting |
| 11 | 4-wood +6.5 | 4-wood +6 (0.068) | **Driver +19** (0.034 +/- 0.002 vs 2-wood): the right fescue starts beyond the path |
| 13 | Driver +0.5 | Driver -1 (0.137) | Driver +4 (0.138 +/- 0.002) |
| 15 | Driver +14.5 | Driver +14.5 (0.102) | Driver +12.5 (0.096 +/- 0.001) |
| 16 | 4-wood -1.5 | 4-wood -2 (0.052) | 4-wood +4 (0.021 +/- 0.001 vs 2-wood): the right fescue moved out |
| 18 | Driver +15.5 | Driver +15 (0.133) | Driver +13.5 (0.139 +/- 0.001) |

### 4b. Sensitivity (central world, final map; carry +/-5 yds, 95 % width +/-10 %, roll x0.8 / x1.2, 5 mph head / tail / either cross)

| hole | central | flips under | closest variant |
|---|---|---|---|
| 1 | Driver -7.5 (0.050) | none | width +10 %: 0.042 |
| 2 | Driver +16 (0.070) | none | carry +5: 0.062 |
| 3 | Driver -8.5 (0.056) | none | width +10 %: 0.036 vs 4-wood |
| 5 | Driver -1 (0.088) | none | carry +5: 0.075 |
| 6 | Driver +6.5 (0.116) | none | 0.103 |
| 8 | 2-wood -39.5 (0.022) | none, but **ties**: 5 mph into 0.003 vs Driver, 5 mph helping 0.005 vs 4-wood, carry +5 0.009 | aim sits on the +/-40 bound with carry +5, helping or L>R wind; the curve is flat there (-42: +0.003) |
| 9 | 4-wood 0 (0.016) | **width -10 % -> Driver +1.5 (0.004)**; carry -5 and 5 mph into: 4-wood by only 0.002 over Driver | a three-way near tie (4-wood / 2-wood / Driver) |
| 10 | 4-wood -16.5 (0.032) | **carry -5 -> 2-wood (0.065); 5 mph into -> 2-wood (0.105); soft turf (roll x0.8) -> 2-wood by 0.006** | carry +5 or helping: 4-wood by 0.115-0.125 |
| 11 | Driver +19 (0.034) | none | width +10 %: 0.018 vs 4-wood |
| 13 | Driver +4 (0.138) | none | |
| 15 | Driver +12.5 (0.096) | none | |
| 16 | 4-wood +4 (0.021) | none | width -10 %: 0.016 |
| 18 | Driver +13.5 (0.139) | none | |

Crosswinds move the aims 5-7 yds (drift held off); they never change the club. The 10th is a real decision
between reaching the green and not: the 4-wood finishes on the green 35 % of the time (on the green 2.97 strokes
for the hole, fairway 3.22, the creek 8 %, sand 6 %). The 2-wood gets there 32 % of the time and goes through into
the rough 41 %. The Driver goes long (rough 77 %, 3.86). Into the wind or on a cold, soft morning, the 2-wood is the
better club; the page's wind grid makes that call by the hole.

### 4c. The Actions re-solve (run 42650772096, 6a3c37956; 16:03-17:49Z)

Back rev 2 + Middle rev 1. Every job finished in 15-45 min: without flight trees a refined card-tee cell is ~4 s,
against ~25 s on Eagle Knoll. 256 prior draws per hole, the card-tee grids refined on 16,000 swings (3 jobs each),
9 coarse offsets. The merge fetched NAIP 2023 0.3 m for the photos, wired the par-3 targets (`par3_targets.json`,
PAR3.md), and built Middle as a solved alt base. The calm-day book is decided at the forecast temperature per hole
(Sat: 39 F on 1 to 49 F on 18).

**Back, calm-day book** (aim yds right of the line, 0.005 window, margin over the runner +/- paired SE, share of the
256 what-if golfers the pick wins):

| hole | pick | window | runner | margin +/- SE | p | note |
|---|---|---|---|---|---|---|
| 1 | Driver -7 | -10..-4 | 2-wood | 0.049 +/- 0.002 | 0.98 | |
| 2 | Driver +17.5 | +14..+21 | 2-wood | 0.069 +/- 0.002 | 1.00 | from the real pad (was +2.5) |
| 3 | Driver -8.5 | -11..-6 | 4-wood | 0.057 +/- 0.002 | 0.97 | 4-wood if the driver 95 % width is over 89 yds |
| 5 | Driver -1 | -3.5..+1.5 | 2-wood | 0.088 +/- 0.003 | 0.99 | |
| 6 | Driver +6 | +3..+9 | 2-wood | 0.113 +/- 0.002 | 1.00 | |
| 8 | 2-wood -40 | -40..-37.5 | 4-wood | 0.017 +/- 0.002 | 0.71 | **close call**; aim on the +/-40 bound (below) |
| 9 | 4-wood 0 | -2.5..+2.5 | Driver | 0.019 +/- 0.002 | 0.71 | **close call**; Driver if the width is under 62 |
| 10 | 4-wood -16 | -18..-14 | 2-wood | 0.020 +/- 0.006 | 0.62 | **close call**; 2-wood when cold or into the wind (below) |
| 11 | Driver +19 | +16.5..+21.5 | 4-wood | 0.029 +/- 0.002 | 0.84 | **close call** (was 4-wood +6.5 on the old map) |
| 13 | Driver +4.5 | +1..+8 | 2-wood | 0.118 +/- 0.003 | 1.00 | |
| 15 | Driver +12 | +8.5..+15.5 | 2-wood | 0.095 +/- 0.003 | 1.00 | |
| 16 | 4-wood +4 | +1..+7.5 | 2-wood | 0.020 +/- 0.001 | 0.86 | **close call** (was 4-wood -1.5, 0.059) |
| 18 | Driver +13.5 | +10..+17 | 2-wood | 0.132 +/- 0.003 | 1.00 | |

Every margin is more than 3 SE (z 3.1-75). 10 is the least resolved (z 3.1).

**Middle, calm-day book:** 1 Driver -4.5 (0.027 vs 4-wood, p 0.81), 2 Driver +21.5 (0.040), 3 Driver -8 (0.081),
5 Driver -1.5 (0.042), 6 Driver +7.5 (0.037), 8 4-wood -40 (0.098), 9 4-wood +0.5 (0.053), 10 4-wood -13 (0.180),
11 **Driver +19.5, 0.012 +/- 0.002 over 4-wood (p 0.67)**, 13 Driver +10 (0.095), 15 Driver +6.5 (0.041),
16 **Driver +25, 0.017 +/- 0.004 over 4-wood (p 0.59: close; the Driver finishes on the green 7.5 % of the time,
in the pond 12 %)**, 18 Driver +6.5 (0.140).

### 4d. Wind grids: Monte Carlo check and wind / temperature sensitivity

* **Fresh swings** (`opt/grid_se.py`: 169 Back card-tee cells at 50 F, 0 and 10 mph; the top 3 clubs
  re-optimised +/-6 yds on 16,000 new swings). The pick differs in 2 cells: 8 at 10 mph from 120 and 240, 4-wood vs
  2-wood, |margin| <= 0.005, both labelled TIE on the page. 8 cells are within 2 SE on the fresh swings, all on 8, 9
  and 11 at 10 mph; their stored margins are 0.003-0.02.
* **The +/-40 aim bound on 8.** On 8 at 10 mph from 60 / 300 the stored margin is 0.020 and the fresh check gives
  0.002. The check has no bound, and the Driver's best aim on the dogleg is about -50 (calm central curve: Driver
  -50 4.337, 2-wood -40 4.273, 2-wood -42 4.276). So the bound does not change the calm pick (2-wood by 0.06 even
  against an unbounded Driver). In a 10-mph crosswind, Driver at -45..-50 is about level with the 2-wood. On the
  course: 2-wood over the left side is the play; Driver only if you can start it 45-50 left of the line.
* **Calm pick vs every 5-mph cell** (`opt/wind_sens.py`, refined grid):
  * Back at 50 F: every hole keeps its club except 10 (into the wind -> 2-wood by 0.02-0.09) and 8 (5 mph
    helping -> 4-wood by 0.004, a tie).
  * Back at 35 F: 10 calm is already 2-wood (by 0.007), and any helping wind gives 4-wood by 0.05-0.10. 8: into
    the wind -> Driver (0.003).
  * Middle: 16 with a helping wind -> Driver (0.03-0.06); 6, 8 and 9 change in 1-3 of the 12 10-mph directions.
  * Sunday's forecast and Saturday's NNW 8-9 mph are read off these grids by the page, hole by hole.
* **10 is temperature-sensitive.** The Back calm pick is 2-wood at 35 F, 4-wood at 50 F, and the book at the
  hole's 45 F is 4-wood by 0.020. The page interpolates between the grid temperatures, so it shows 2-wood on a cold
  calm morning and 4-wood once it warms up. The Saturday 11:06 forecast cell (45 F, NNW 8, slightly into) shows
  2-wood (screenshot checked).

### 4e. Page (final)

The merge built `wind_page/index.html` from the new grids, the Middle alt base, NAIP 2023 photos and the par-3
targets. qa_page.js on The Tips, Champions, Back, Middle and Forward: 18 / 18 holes each, 0 problems. I looked at the
phone screenshots of every Back par 3 (4, 7, 12, 14, 17: sharp; the box sits on the green, short of centre) and of
the tee shots that changed (2, 10, 11), and at Middle 16. Par-3 club line: each set shows its own club
(`by_set.p3club`). The Tips / Champions 14 and 17 and Forward 12 show only "Plays N" (config `par3_club_hide`).

### 4f. Still uncertain

* Will's dispersion and the 8-iron / short-iron carries are assumed, as on Eagle Knoll. 3, 8, 9 and 11 flip with the
  driver width (89 / 87 / 62 / 83 yds).
* The tee sheet is not posted: the NCCGA's 2025 setup mixed boxes. Middle is solved; The Tips / Champions /
  Forward are the Back line moved.
* Middle 3's long drives land past the hand-checked footprint (auto layers there).
* The map fixes were made on 2023 imagery. Fescue edges are good to +/-3-5 yds (reviewers' estimate).
* The forecast is from Nov 9; the weather workflow refresh (~Nov 12, 13) rebuilds the page but not the book.
