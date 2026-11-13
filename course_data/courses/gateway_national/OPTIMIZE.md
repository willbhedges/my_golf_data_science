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

## 5. Nov 12-13 second pass (integrator)

One integrator (this section) with four specialists writing proposals only (`second_pass/`: PHYSICS.md, MODEL.md,
FEATURES_1_9.md, FEATURES_10_18.md, WILL_REVIEW.md). Golfer's rules for this pass: his stated carries as given, one
normal shot pattern per club, one club and one aim per hole; only real external conditions vary (forecast wind and
temperature, firm or frozen ground, tee position). No "if you are hitting it well / badly" cases on the page.

### 5a. The audit's 13 findings on the built page

Status per finding: AUDIT.md, last section. In short: 1, 4, 5, 6, 9, 10, 11, 12 fixed; 7 and 8 fixed as designed with
a residual (the par-3 number is still the card's by default; 20 / 40 up on a Back tee shows the card-tee solve with a
pill); 2 right; 3 over-corrected (re-fixed here); 13 mostly.

### 5b. New evidence for the map

* **Sentinel-2 NDVI, Nov 8 + 10 2026 (10 m, cloud-free)**, `second_pass/s2/`: fairway 0.87, mown rough ~0.80, dormant
  prairie / fescue 0.50-0.65. It shows what is dormant warm-season grass today. It cannot tell standing from cut, and
  unmown cool-season grass stays green, so it is used to confirm or reject a mapped band, not to trace one alone.
* **USGS 3DEP lidar point clouds of Dec 2020 and Dec 2023** (F2 / F1): grass height on a 0.5 m grid (mown 0.02-0.04 m,
  standing fescue / prairie 0.10-0.35 m). The direct measure of long grass, late in the season.
* **The summer photo misleads on unirrigated rough:** tan and "textured" in August (NAIP), short and green in
  November. That is how the right side of 9 and the inside of 8's dogleg were mapped as fescue on Nov 9.
* Every applied edit was looked at by me on a render (NAIP 2023 RGB + CIR at 4-9 px / yd, NDVI, lidar height) before
  and after (`opt/lie_render.py`, the engine's own lie raster).

### 5c. Map edits (rule from Fri 03:00Z: apply only if a Back or Middle aim moves >= 3 yds or a club changes)

Aim in yds right (+) / left (-) of the tee line; central world, 16,000 swings (SE 0.001-0.004), Nov 13 forecast
temperatures, second-pass physics. "v5" = the published page's calm book.

| hole | edge, old -> new | evidence | Back pick / aim, v5 -> now |
|---|---|---|---|
| 8 | ground left of the fairway at 240-345 (x -65..-128): "unverified" (priced as half trees) -> rough | outside the +/-65-yd hand corridor; looked at on NAIP + NDVI: mown rough, then the cart path (`engine.checked_extra_ll`) | 2-wood -41 -> **Driver -44.5** (0.057 over 2-wood). This artefact alone was worth 0.05 to the Driver |
| 8 | unmown square inside the bend (299-336, x -88..-48): unmapped -> native | NAIP 2023 tufted block ringed by a mown bank; F1 confirms the position (6-9 yds larger east); standing now: not settled | part of the above (the Driver finishes 285, short of it; from Middle it stops the Driver: Middle 8 4-wood -35.5) |
| 8 | right side at 220-312: native from the fairway edge (two bands) -> native from the lidar brush line (x 47 / 45 / 34 / 28 / 21 / 9 / -7 at 220 / 250 / 260 / 270 / 280 / 290 / 300) | F1: no standing grass in the Dec 2020 lidar, NDVI Nov 2024-26 0.76-0.84; mown collar visible on NAIP | part of the above |
| 9 | right "fescue" band x +30..+45, 140-340 -> removed (rough) | mowing stripes on NAIP 2023; NDVI 0.87 (= fairway); F1: no lidar height out to the trees | 4-wood +3 -> **Driver +13** (0.025 over 2-wood, 0.039 over 4-wood): close call |
| 9 | left inner edge at 250-340: x -24 / -19 / -14 / -16 / -22 -> -34 / -29 / -19 / -22 / -27 / -28 (250 / 265 / 280 / 300 / 320 / 340) | worn line on NAIP; NDVI edge; F1 lidar within 1-4 yds at 270-340 | part of the above |
| 10 | long grass: hand bands (left x < -45, right x > 30-52) -> lidar polygons (left from x -55..-60 beyond the bunkers, a band across 300-315 behind the green, right strip between the two cart paths) | F2, Dec 2020 lidar; checked on the lidar render | 4-wood -16 -> **2-wood -20.5** (0.060 over 4-wood): the aim is the green centre; the club is the colder, shorter ball (5d) |
| 16 | left native inner edge at 235-300: x -30..-34 -> -26 at 235 to -18 at 295 (lidar polygons, whole hole) | F2, Dec 2023 lidar (0.22 m in the block); my NAIP read was -27..-22 | 4-wood -3 -> 4-wood **+6.5** (0.108 over 2-wood, 0.111 over long iron) |
| 16 | mound right at 264-298 (x +6..+43): native (lost-ball) -> a penal lie priced as "sand" | tufted in every summer photo, 0.036 m in the Dec 2020 and Dec 2023 lidar (the block across the fairway reads 0.22 m), stone wall on its fairway face. Deliberate: found but awkward, between rough and native; the engine has no heavy-rough lie | part of the above. As native: aim +4; as plain rough: +7.5, 2-wood only 0.038 behind |

Tested and NOT applied (under the rule): lidar long grass on 11, 13, 15, 18 (aims moved 0.5-2 yds: the Nov 9 hand
bands stay); 18 Back tee 17 yds forward onto pad B (F2, confidence 0.7: Driver aim 14.5 -> 12.5, same club; the hole
may play ~17 shorter than the card from that pad); fairway right edges 2-5 yds narrower on 10 / 15 / 18; 8 fairway
left edge 3-7 yds inside the OSM line at 240-290; tree lines 3-15 yds further from play on 8, 9, 14, 17, 18 (the map
is conservative); OSM greens and bunkers 1.5-3 yds off on 10-18; par-3 surrounds on 12, 14, 17 (no par-3 target
re-solve). My own notes that fell under the rule: 1 right native 5-8 yds further right at 290-340, 2 native right of
the cart path from x +48.

Process errors of this pass, so they are not repeated: (1) `opt/map_edits.py` splices by the OLD trace's zone
counts; run twice on already-edited zones it dropped hole 9's right tree zone (request rev 4 was solved on that).
It is now always applied from the v5 zones. (2) trace.py first read the specialists' working JSON and applied only
"add" edits, which silently deleted 16's mound (rev 5). It now reads a frozen copy
(`truth/gateway_national/features_applied.json`) and raises on any other action.

### 5d. Physics (PHYSICS.md), adopted behind `config.engine.physics` (Gateway only)

| change | old -> new | check | effect this weekend |
|---|---|---|---|
| carry lost per F below 70 | 0.00075 (air only) -> 0.00135 | air 0.00075 (0.39 % of carry per 1 % of density: Titleist altitude rule 0.40) + a ball at air temperature ~0.0004 (about 1 % of ball speed at 45 F) + the 1027-1031 hPa high ~0.0002 | Driver about 4 yds shorter at 45 F; par 3s +2 to +4 yds |
| crosswind drift | 1.14 yds / mph for the driver, 0.8 mid iron -> 1.5 for every full shot | lag formula W (T - x / v0): driver 6.8 s, 250 m, 75 m/s -> 17 yds at 10 mph; 6-iron 6.3 s -> 16 | aims 1-2.5 yds further up wind |
| head / tail multipliers | 1.0-1.3 -> 2-wood 1.2, 4-wood 1.3, long iron 1.5, mid iron 1.65, 8-iron 2.0 | mid iron -9 % into 10 mph (rule of thumb 1 % per mph) | par 3s +/-1 yd |

Golfer's answers (Nov 13): he will rotate balls from a pocket as best he can (gives back ~1.5-2 yds of Driver carry
against a fully cold ball), and his carries were measured in Lawrence KS at ~850-900 ft (Gateway is ~410 ft: costs
~1.5 yds). The two cancel within a yard, so 0.00135 stays.

Not changed: roll. The fairways are dry (0.43 in of rain in three weeks, none since Nov 3) and Saturday starts
frozen (24 F overnight, 35 F at 9:00): the stated totals are a fair centre, firm is the likely side (5e).

Also fixed: from a moved tee (The Tips / Champions / Forward grids) the putting-green polygon stayed in card-tee
yards, so on the drivable 10th the "green" sat 20-60 yds off. Back and Middle were not affected.

### 5e. Frozen or firm ground (roll x1.25 / x1.5), a condition like wind

| hole | normal | x1.25 | x1.5 |
|---|---|---|---|
| 8 | Driver -46 (0.056) | Driver -46.5 (0.042) | Driver -48.5 (0.028) |
| 9 | Driver +15 (0.030) | Driver +15.5 (0.020) | Driver +16 (0.007: a tie with 2-wood) |
| 10 | 2-wood -20.5 (0.060) | 2-wood -20.5 (0.019) | **4-wood -21.5 (0.015)** |
| 16 | 4-wood (0.108) | 4-wood (0.087) | 4-wood (0.057) |

(Run before the last 8 / 9 edge edits; those moved the aims 1.5-2 yds.) The page carries one condition pill, on 10:
"Frozen or very firm ground (drives running 35+ yds): 4-wood, same line".

### 5f. Page

* Par 3s: the number uses the new temperature rule; a crosswind line ("The wind moves the ball about 6 yds right:
  start it that far left of the box", 1.4 yds per mph); the club still follows the live number.
* One aim number per hole, the one at the top; the calm note keeps club, margin and shares. "what-if worlds" ->
  "N% sure". Pattern break-even sentences dropped. The hybrid he does not own sorts last.
* Footer: temperature rule and tee-slider wording corrected.

### 5g. Honest list of what is still uncertain

* Whether the long grass is standing on Nov 14. The lidar is Dec 2020 / Dec 2023, the photo Aug 2023; the Nov 2026
  satellite shows dormancy, not height. 8's square and 16's mound are the two that matter.
* 9 (Driver vs 2-wood vs 4-wood within 0.04) and 10 (2-wood vs 4-wood, decided by 4 yds of carry and the turf) are
  coin flips in strokes. 8's Driver rests on the left side being open rough (F1 confirms).
* Tee positions: 18 Back may be 17 yds forward of the mapped point; par 3 on 4 is 176 from the pad centre (card 180).
* Tee time (9:00 assumed; a frost delay is likely on Saturday) and the tee set.
