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
