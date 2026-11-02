# Long grass from Sentinel-2 seasonality (2026-11-02)

The idea: native / fescue is not irrigated, so its greenness follows the season and droughts. Irrigated rough and
fairway stay green. Sentinel-2 L2A gives a 10 m NDVI / red-edge time series. Each feature is taken relative to the
course's own OSM fairway pixels.

**Update (second pass, see 'Enlarged native set' at the end):** with 23 courses (5 Kansas native courses traced, 5 extra negatives) the layer cuts regret over 22 scored courses from 9.12 to 5.88. But it still breaks 4 holes on parkland / partly native courses, and no drought gate separates Amana. It is still not adopted.

**Decision: not integrated into the product. It passes the error-budget bar narrowly on the 7 card courses, and the
bar should be confirmed before integration.** `model_v2` `native_thr: null` is unchanged, and no package or vision
layer was written. Results:

* **Pixels.** Sentinel-2 (S2) at 10 m is the best long-grass classifier so far. Leave one course out (LOCO) over
  13 courses at P >= 0.5: pooled corridor precision 0.54, recall 0.29, IoU 0.23. The v3 1 m model, re-run on the
  same 13 folds, gets 0.25 / 0.10 / 0.08.
* **Plans.** On the 7 card courses, `P >= 0.5` gets 75 matches and 1.203 strokes of regret. The control (today's
  packages rebuilt with no long grass) gets 74 / 1.465. All of the gain is Gateway and Coldwater.
* **Hard cases.** On the 4 other scored courses, the layer loses 2 holes (Spirit Hollow 17; Amana 14, the drought
  case) and changes none for the better. Over all 11 courses: 113 vs 114 matches, regret 2.94 vs 3.18.

## Data (`.github/workflows/s2_stack.yml`, `vision_any/s2/fetch_s2_stack.py`)

* **Run.** One Actions job (run 41377000510) covered 13 courses: Gateway, Spirit Hollow, Coldwater, Ellis, Mozingo,
  Pine Dunes, Hot Springs, Blue Hills, Eagle Knoll, Veenker, National KC, Annbriar and Amana Colonies.
  Collection: Planetary Computer `sentinel-2-l2a`, 2023-03 to 2025-11, March to November only, scene cloud < 60 %.
* **Grid.** Each scene is warped onto the course's `vision_any/<slug>/raw` UTM grid, coarsened to 10 m.
* **Masking.** SCL clear = classes 4/5/6. Cloud, shadow and cirrus are dilated by 2 px. A scene is kept only when
  >= 40 % of the grid is clear. One tile is kept per date. The BOA offset is applied for baseline >= 04.00.
* **Scenes kept.** 82-172 clear scenes per course; median 156.
* **Stored per course** (`vision_any/s2/<slug>/s2_stack.npz` + `s2_meta.json`):
  * monthly median NDVI, NDRE (B8A/B05), NDMI (B8A/B11), PSRI and NBR2, as int8;
  * every clear scene's NDVI;
  * the Jun-Aug median reflectance of the 10 bands.
* **Size.** 4-19 MB per course, 96 MB in total: more than the "small" I intended. The per-scene NDVI is most of it.
  Drop `ndvi_obs` (only `nd_std` / `nd_q10_sum` use it) if the repo size matters.
* **Speed.** The fetch is fast (30-75 s per course); the Actions queue is the wait.

## Features and model

* **Seasonal features, per year then averaged over years.** NDVI in spring, June, the Jul-Sep minimum, Jul-Sep
  median, fall and March. The Jun -> Jul-Sep drop and the fall rebound. Red-edge and NDMI: summer value, minimum and
  drop. PSRI: summer and fall maximum. NBR2. The worst year of the minimum and drop features.
* **Scene-level features.** NDVI std over Apr-Oct scenes, and the 10th percentile over Jun-Sep. Summer band ratios
  (B07/B05, B11/B8A).
* **Two references per course, both label-free.**
  * `fw_`: the feature minus its median over 10 m cells that are >= 70 % OSM fairway.
  * `rf_`: the same against unmown, canopy-free cells 5-25 m from the fairway.
* **Context.** OSM fairway / mown share, lidar canopy share and its 50 m neighbourhood, and the min / mean distance
  to the OSM fairway. These come from `prep_grid10.py`, which aggregates `v2_model.prepare` masks to 10 m.
* **Labels.** Hand native vs rough / first cut in the 145-440 yd corridors, at 1 m (`build_ds_13.py` is v3's
  `build_ds.py` with the truth_sets_v2 hand maps added). A 10 m cell is native when >= 50 % of its >= 30 labelled
  1 m cells are native.
* **Model.** LightGBM (15 leaves, 300 trees), balanced per course and per class, leave one course out over the 13
  courses. Scoring is per 1 m labelled cell (the cell gets its 10 m P). The scoring is the same as
  `v3_longgrass_loco.md`: landing corridors 180-320 yds, +/-50 yds.

**Which signal works.** The NDVI std over the season (AUC 0.60-0.79 native vs rough, same direction on all 8 native
courses) and the March NDVI relative to the fairway are the most informative. March NDVI is lower on native (AUC
0.60-0.96 inverted on all 8). Native is still dormant when irrigated cool-season turf has greened up. Top gain:
`fw_nd_march, fw_nd_std, c_canopy_nb, fw_re_sum, fw_mi_drop`.

The July-September drop itself is weak (AUC 0.53-0.66, 0.24 on Ellis). Eagle Knoll's native is *greener* in summer
than its rough (summer min AUC 0.82), the same flip v3 saw.

## LOCO (13 courses, pixel level at 1 m, landing corridors)

| model | thr | precision | recall | IoU | FP m2 on no-native courses | corridor sides: truth / pred / TP / FP / FN | start error med / p75 (yd), bias |
|---|---|---|---|---|---|---|---|
| v3 1 m (`norm`, re-run on 13 folds) | 0.5 | 0.25 | 0.10 | 0.08 | 24,419 | 85 / 47 / 19 / 28 / 66 | 6.6 / 8.4, +4.4 |
| context only (no S2) | 0.5 | 0.27 | 0.36 | 0.18 | 67,489 | 85 / 152 / 61 / 91 / 24 | 6.3 / 10.3 |
| **S2 relative + context** | 0.3 | 0.45 | 0.43 | **0.28** | 16,988 | 85 / 90 / 50 / 40 / 35 | 4.5 / 7.8, +1.2 |
| **S2 relative + context** | **0.5** | **0.54** | 0.29 | 0.23 | 7,937 | 85 / 56 / **37 / 19** / 48 | **5.6 / 9.1, +2.6** |
| S2 relative + context | 0.6 | 0.58 | 0.22 | 0.19 | 4,981 | 85 / 45 / 32 / 13 / 53 | 5.1 / 9.7 |
| S2 + raw S2 | 0.5 | 0.52 | 0.20 | 0.17 | 7,518 | | |
| S2 "side extent" fill | 0.5 | 0.60 | 0.27 | 0.23 | 5,006 | 85 / 42 / 31 / 11 / 54 | 9.9 / 14.7, +9.9 |
| late fusion mean(v3, S2) | 0.4 | 0.53 | 0.26 | 0.21 | 8,780 | 85 / 55 / 33 / 22 / 52 | 6.5 / 8.4 |
| late fusion geo-mean(v3, S2) | 0.5 | 0.65 | 0.13 | 0.12 | 1,661 | | |

**Corridor sides.** Each side is one hole's landing corridor on the left or right of the tee line (152 sides with
>= 500 m2 labelled). A side counts as having native when it has >= 250 m2 of it. "Start" is the 10th percentile of
the native cells' distance to the OSM fairway. It is reported only for sides where both truth and prediction have
native.

**Side-extent fill.** Per side, every cell >= N yds off the fairway, with N = argmax of sum_{cells >= N}(P - thr).
This is the "native starts N yds off, this side" layer. It is more precise but starts native 10 yds too far out, so
it covers less.

**S2 at P >= 0.5, per course.**

| course | precision | recall | IoU | predicted / hand m2 | sides TP / FP / FN |
|---|---|---|---|---|---|
| Gateway | 0.69 | 0.55 | 0.44 | 24,837 / 31,110 | 16 / 1 / 6 |
| Spirit Hollow | 0.66 | 0.14 | 0.13 | 3,856 / 18,587 | 5 / 1 / 13 |
| Coldwater | 0.76 | 0.27 | 0.25 | 7,590 / 20,975 | 8 / 1 / 7 |
| Ellis | 0.18 | 0.08 | 0.06 | 1,419 / 3,064 | 1 / 1 / 4 |
| Mozingo | 0.47 | 0.61 | 0.36 | 11,608 / 8,951 | 7 / 7 / 0 |
| Eagle Knoll / Veenker | 0 | 0 | 0 | 100 / 656; 53 / 1,066 | 0 / 0 / 1 each |
| Pine Dunes / Blue Hills / National KC (no native) | | | | 641 / 154 / 842 false | 1 / 0 / 0 FP |
| Hot Springs (no native) | | | | 0 | |
| **Annbriar (native prairie)** | 0 | 0 | 0 | 0 / 22,024 | 0 / 0 / 16 |
| **Amana (drought rough, no native)** | | | | 6,147 false | 7 FP sides |

* **Wins.** Eagle Knoll, the v3 canary, is clean: 100 m2 here against 11,577 for v3. Gateway reaches an IoU of
  0.44.
* **Hard cases.**
  * Annbriar's native is missed completely. It is tall prairie that stays green and is not dormant in March like
    the fescue on the training courses. Its native NDVI summer minimum is lower than its rough, but its March NDVI
    is not.
  * Amana's 2023 drought rough is called native on 7 corridor sides. Unirrigated mown rough browns exactly like
    fescue.
* **Hot Springs has no OSM fairway.** Its relative features are all NaN, so it predicts nothing. That is correct
  here by luck, and a product version needs a fallback reference.
* **Fusion.** The v3 1 m features + S2, trained jointly, was started and stopped: it ran too slowly on the shared
  box. The late fusions raise precision but not IoU. S2 alone is the best layer.

## Error budget (n = 4000, seed 31, `vision_any/s2/s2_eb.py` = `platform/error_budget_variant.py` + the truth_sets_v2 courses)

**The baseline moved.** The packages were rebuilt after ERROR_BUDGET.md's "none" row was measured (tees rule,
commit 51306d07). The no-long-grass control therefore had to be re-measured: today's packages through the same
`v2_calibrate.rebuild_package` with no native. It is 74 / 1.465 on the 7 card courses, not the old 71 / 1.357.
Veenker's regret went from 0.103 to 0.201, and Eagle Knoll's matches from 12 to 14.

**Annbriar and Amana.** They have no `vision_any.geojson`, so their base layers are rebuilt from the package's own
vision zones. Their control therefore differs from the committed package: Annbriar 10 / 0.418 vs committed
8 / 0.293; Amana 12 / 0.031 vs 10 / 0.085. Compare variants against the control only.

**Variant rasters.** The 10 m LOCO P (held-out course) is upsampled to 1 m. It goes through
`v2_model.native_mask` (strict eligibility, committed trees excluded) and `v2_calibrate.rebuild_package`
(`s2_variant.py`).

| auto long grass | 7 card courses: match / regret | Ellis | Spirit Hollow | Annbriar | Amana | all 11: match / regret |
|---|---|---|---|---|---|---|
| none (old committed table) | 71 / 1.357 | 11 / 0.375 | 7 / 0.893 | | | |
| **none (control, today's packages)** | **74 / 1.465** | 11 / 0.375 | 7 / 0.893 | 10 / 0.418 | 12 / 0.031 | 114 / 3.182 |
| **S2 P >= 0.5** | **75 / 1.203** | 11 / 0.377 | 6 / 0.867 | 10 / 0.419 | 11 / 0.071 | 113 / 2.937 |
| S2 side-extent fill, thr 0.5 | 74 / 1.445 | 11 / 0.375 | 7 / 0.893 | 10 / 0.418 | 11 / 0.084 | 113 / 3.215 |
| S2 P >= 0.6 (first 4 courses only) | Gateway 10 / 0.297, others = control | | | | | |
| hand long grass (old table) | 77 / 0.51 | | | | | |

* **Gateway.** `P >= 0.5` fixes holes 9, 11 and 13 and breaks 1 and 16. Regret 0.424 -> 0.224.
* **Coldwater.** Regret 0.472 -> 0.392, same matches.
* **Unchanged.** Blue Hills, Eagle Knoll, Hot Springs, Veenker and Ellis: the same picks and regret within 0.002.
  Pine Dunes: the same picks, regret +0.018.
* **Broken.** Spirit Hollow 17 and Amana 14 (the drought false positive).
* **Area outside the corridors.** The layer marks a lot of native course-wide, outside the hand corridors: Pine
  Dunes 58,000 m2, Amana 197,000, Spirit Hollow 166,000. The plans of the scored tee shots barely see it.
  Approach shots and the app's map would.
* **Side-extent fill.** It is precise per pixel but too far from the fairway (+10 yds bias). It gives back
  Gateway's gain (9 / 0.471), so "where the native begins" from this fill is not good enough.

**Why it is not integrated here:**

1. **The margin is one hole** on the 7 courses (75 vs 74). The threshold was picked among 3 variants scored on the
   same courses. Over all 11 scored courses it loses a match (113 vs 114) while cutting regret by 0.25.
2. **It fails both hard cases.** The drought rough (Amana) is called native and the prairie (Annbriar) is missed.
   These are exactly the course types where "native" matters for an arbitrary US course.
3. **The product needs more than the classifier.** An S2 fetch stage in the package build, and a fallback reference
   when the course has no OSM fairway (Hot Springs).

**Suggested next steps:**

* Add the S2 stage as an *opt-in* layer behind a gate. One candidate gate: a course-level "fairway vs rough NDVI
  contrast" in the drought months, to catch an Amana-type course.
* Re-score after adding more prairie-style native truth.
* Clip the native to the hole windows rather than marking it course-wide.

## Reproduce

Scripts are in `vision_any/s2/`, plus v3's `vision_any/longgrass_v3/{common,model_lib}.py`. Copy both to one
scratch directory and link `s2 -> <repo>/course_data/vision_any/s2`. Data lands next to the scripts.

1. `build_ds_13.py <repo> . <slugs>` and `prep_grid10.py <repo> . <slugs>`.
2. `s2_loco.py s2` (also `ctx`, `s2raw`, `v3`); then `s2_eval.py pred_s2.npz 0.3,0.5 -v [--json ...]`.
3. `s2_variant.py <repo> pred_s2.npz var s2_pix_0.5 pix 0.5 <slugs>` (`none` builds the control). Run one
   variant at a time on Pine Dunes: 4 builds in parallel ran out of memory.
4. `s2_eb.py <repo> var/<variant> eb/eb_<variant>.json <slugs>`, then
   `s2_summ.py eb/eb_ctl.json eb/eb_<variant>.json`.

Results: `vision_any/s2/s2_results.json`. It holds the LOCO tables, per-side rows for S2 at 0.5, and the error
budget per course and hole for the control and each variant.

## Not verified

* **The fused model.** The 1 m v3 features + S2, trained jointly, was not finished; only late fusion was scored. The
  fused layer was not scored in the error budget either: that needs a full-grid v3 P.
* **Incomplete runs.** S2 P >= 0.6 in the error budget was scored only on Blue Hills, Eagle Knoll, Gateway and Hot
  Springs. Its builds for the other courses ran out of memory.
* **Not scored in the error budget.** Mozingo and National KC; their pixel LOCO is above.
* **Other S2 options.** Winter (Dec-Feb) scenes, other cloud thresholds, and S2 years before 2023.

## Enlarged native set (23 courses), drought gate, error budget (2026-11-02, second pass)

**Decision: still not adopted (`native_thr: null` unchanged).** With 5 Kansas native courses added, the S2 layer
makes far better plans where native is everywhere: Prairie Dunes goes from 1 to 12 matches of 14, and Buffalo Dunes
from 7 to 12. It also beats "none" on regret on every course group. But it breaks 4 holes on courses with little or
no native: Ellis 2 and 9, Spirit Hollow 17, Rivercut 9. That fails the bar of no hard-case failure. P >= 0.6:
the same 4 holes break. Recommendation: offer it as an opt-in layer on courses the golfer says have native, or gate it with a golfer tap. Do not ship it as a default.

### New truth (`truth_sets_v2/<slug>/`, each with CHECK.md)

The courses were named by the golfer. They were traced by eye on NAIP, never from S2 (S2 is what the model is scored
on). Trees come from 3DEP lidar; fairway, water and sand from OSM. Routing is the `draft_spec` OSM draft, checked on
the routing map only. OB is not traced.

| course | set | how the native lies | hand native in the scored landing corridors (m2) |
|---|---|---|---|
| Sand Creek Station (Newton) | Championship | both sides of most holes, beyond ~12 yds of mown rough | 25,633 |
| Eagle Bend (Lawrence) | Gold | golfer's truth (see below) + 5 holes from imagery | 25,435 |
| Prairie Dunes (Hutchinson) | Blue | both sides of every hole, 6 yds off the fairway | 88,674 |
| Mariah Hills (Dodge City) | Blue | discrete islands between holes (+/-10 yds) | 27,872 |
| Buffalo Dunes (Garden City) | Blue | sandhill prairie between all fairways, beyond ~10 yds | 67,338 |
| Southwind CC (Garden City) | - | **not in OSM** (package request: "not_found: no candidates"); not traced | - |

* **Eagle Bend numbering.** The golfer's notes fit the OSM / OpenGolfAPI numbering, not the scrambled golfify
  card. His "3: native left before the pond" is OSM hole 3, the par 5 that ends beside the pond. On the golfify
  card, hole 3 is the real 12, a par 3 with no pond.
* **Golfer vs imagery: all four of his holes agree.** 2 has native left and right, 3 left, 5 left and 6 left. On 3,
  the 2021 photo alone was ambiguous; NAIP 2017, 2019 and 2023 show tan, textured grass left of the fairway.
* **Extra negatives.** S2 stacks were added for 5 truth_sets_v2 courses with no long grass in the landing zones:
  Tomahawk Hills, L.A. Nickell, Gustin, Rivercut and Osage National. Blue Hills is confirmed by the golfer as
  having no native anywhere; it was already a negative.
* **Fetch change.** `fetch_s2_stack.py` can read `s2/<slug>/grid.json`, the same `fetch_any.Grid` that
  raw/meta.json gets, so the S2 fetch can run alongside the raw/ fetch. It was checked identical on 4 courses.
  `tourn_truth.yml`'s commit retry now uses `--autostash`: run 41397494956 lost all of its output without it.

### LOCO, pixel level (landing corridors 180-320 yds +/-50; `s2_eval.py`)

"Before" is the 13-course model: LOCO on its own 13 courses, and on the 10 added courses trained on all 13. "After"
is the same model and features, LOCO over 23 courses.

| model, P >= 0.5 | original 13: prec / rec / IoU | KS native 5 | all 23 | FP m2 on no-native courses | sides truth / pred / TP / FP / FN | start err med / p75 (yd) |
|---|---|---|---|---|---|---|
| before (13 courses) | 0.54 / 0.29 / 0.23 | 0.68 / 0.25 / 0.23 | 0.61 / 0.27 / 0.23 | 12,639 | 193 / 135 / 101 / 34 / 92 | 4.6 / 8.6 |
| **after (23 courses)** | **0.51 / 0.38 / 0.28** | **0.81 / 0.62 / 0.54** | **0.72 / 0.55 / 0.45** | 6,208 | 193 / 177 / 139 / 38 / 54 | 3.5 / 6.8 |
| after, P >= 0.6 | 0.55 / 0.31 / 0.25 | 0.86 / 0.55 / 0.51 | 0.77 / 0.47 / 0.42 | 3,987 | 193 / 150 / 123 / 27 / 70 | 3.8 / 7.0 |
| after, per-season P, min over years (0.5) | 0.53 / 0.35 / 0.27 | 0.91 / 0.52 / 0.50 | 0.77 / 0.47 / 0.41 | 6,764 | 193 / 144 / 116 / 28 / 77 | 4.2 / 7.4 |
| v3 1 m alone (`norm`, 23 folds, 0.5) | 0.29 / 0.18 / 0.13 | 0.70 / 0.37 / 0.32 | 0.55 / 0.31 / 0.25 | 39,627 | 193 / 144 / 92 / 52 / 101 | 4.3 / 7.7 |
| late fusion mean(v3, S2), 0.4 | 0.55 / 0.39 / **0.30** | 0.76 / 0.61 / 0.51 | 0.70 / 0.54 / 0.44 | 5,140 | 193 / 187 / 150 / 37 / 43 | 4.5 / 7.7 |
| late fusion mean(v3, S2), 0.5 | 0.63 / 0.27 / 0.23 | 0.79 / 0.41 / 0.37 | 0.74 / 0.37 / 0.33 | 1,917 | 193 / 126 / 108 / 18 / 85 | 6.2 / 8.8 |

The late fusion at 0.4 is the best pixel layer on the original 13 courses. It was not put through the error budget: v3's P exists only on the labelled corridor cells, not on the full grid that the variant build needs.

**Per course, at P >= 0.5, before -> after (IoU).**

* Big gains: Prairie Dunes 0.36 -> 0.78, Buffalo Dunes 0.05 -> 0.67, Mariah Hills 0.25 -> 0.34, Spirit Hollow
  0.13 -> 0.23, Coldwater 0.25 -> 0.30, Gateway 0.44 -> 0.47.
* Still failing:
  * Eagle Bend 0.08 -> 0.03. Its native is mottled tall grass that is green in summer and close to the rough.
  * Annbriar 0.00 -> 0.01, still missed.
  * Ellis gets worse: 9,838 m2 predicted against 3,064 m2 of hand native, precision 0.19.
* **Blue Hills (the golfer's confirmed no-native course).** The new model predicts 0 m2 in every landing
  corridor and 0 m2 course-wide; the 13-course model predicted 154 m2. Gustin, L.A. Nickell, Rivercut and
  Tomahawk Hills are also 0. Osage National has 794 m2 in its corridors (2 and 5), Pine Dunes 115 and National KC
  117.

### Drought gate (Amana): tried, does not work

* **Per-season gate** (`s2year.py`, `s2y_loco.py`). Features are computed for each season separately and P is
  aggregated over the seasons, so native must look native every year. A season counts as a drought season when the
  course's own rough band browns >= 0.05 NDVI more, against its fairway, than in its best season. Drought seasons
  are left out ("gated"). The idea: drought rough browns only in the drought year.
* **Result on Amana's corridor false positive**, all at P >= 0.5:

  | model (P >= 0.5) | Amana false native (m2) |
  |---|---|
  | 23-course, multi-year features | 5,095 |
  | per-season, mean | 6,917 |
  | per-season, gated | 6,835 |
  | per-season, min over seasons | 4,472 |
  | 13-course model, for reference | 6,147 |

  The "drought" index flags 2023 at Amana, but also on Ellis, Pine Dunes, Prairie Dunes, Annbriar and others. 2023
  was a regional drought.
* **Why it fails.** Amana's false-native cells look like true native on every S2 feature, in every season (March
  dormancy, NDVI std, fall NDVI): `fpdiag.py` medians match Gateway, Coldwater and Mozingo native.
* **Other gates, also no separation.**
  * A course-level gate on "share of far rough called native": Amana 48 % vs Mozingo 67 % (real native).
  * Dropping the worst-year features: Amana 4,051 -> 3,813 m2.
* **What it needs.** At 10 m this is a signal limit. A gate needs information S2 does not have, such as a
  maintenance record, lidar height or the golfer.
* **Amana in the error budget.** Unlike the 13-course model, the 23-course layer does not break Amana 14 (12 / 14,
  regret 0.032). Its false native is still there: 14,593 m2 in the corridors at 1 m and 21.6 ha course-wide.

### Error budget (n = 4000, seed 31; `ng_variant.py` + `ng_eb.py`; configs auto / truth)

* **Base, for both sides.** The committed package, re-teed with the 3f1a201d rule and with vision_any/2 trees
  re-made from the lidar (`platform/rebuild_tees_trees.py`, "what a build with the lidar stack gives").
* **The variant** adds the held-out course's LOCO S2 native (`v2_model.native_mask`, strict eligibility, lidar
  trees excluded) through the same gapfill.
* **Truth.** The `error_budget.py` v1 harness for the original courses and the v2 harness for the
  truth_sets_v2 courses (the 5 new ones included).
* **Reproduction check.** The 13-course model through this harness reproduces the earlier table: Gateway 9 -> 10,
  regret 0.424 -> 0.224; Spirit Hollow 17 and Amana 14 broken.

| auto long grass | 7 card courses | Ellis / Spirit Hollow / National KC | 7 truth_sets_v2 held-out | 5 KS native | all 22: match / regret |
|---|---|---|---|---|---|
| none (control, this base) | 75 / 1.400 | 19 / 1.268 | 74 / 1.556 | 32 / 4.899 | 200 / 304, 9.122 |
| 13-course S2, P >= 0.5 (old 12 only) | 76 / 1.125 | 18 / 1.244 | Amana 11 / 0.071, Annbriar same | - | - |
| **23-course S2, P >= 0.5** | **76 / 1.164** | **16** / 1.265 | **73** / 1.583 | **48 / 1.867** | **213, 5.879** |
| 23-course S2, P >= 0.6 | 76 / 1.157 | 16 / 1.273 | 73 / 1.581 | 48 / 1.787 | 213, 5.799 |

At P >= 0.5, holes fixed (+) and broken (-) against the control:

| course | holes (+ fixed / - broken) | matches | regret |
|---|---|---|---|
| Prairie Dunes | 1+ 5+ 6+ 7+ 8+ 9+ 12+ 13+ 16+ 17+ 18+ | 1 -> 12 | 1.649 -> 0.164 |
| Buffalo Dunes | 7+ 10+ 11- 13+ 14+ 15+ 16+ | 7 -> 12 | 1.623 -> 0.256 |
| Mariah Hills | 6- 13- 17+ 18+ | | 0.852 -> 0.703 |
| Sand Creek Station | (same picks) | | 0.259 -> 0.228 |
| Gateway | 1- 11+ 13+ | | 0.424 -> 0.274 |
| Coldwater | (same picks) | | 0.472 -> 0.386 |
| **Ellis** | **2- 9-** | | 0.375 -> 0.390 |
| **Spirit Hollow** | **17-** | | |
| **Rivercut** | **9-** | | 0.045 -> 0.071 |
| Eagle Bend | (same picks: 7 / 14, 0.515) | | |
| Amana | (not broken) | 12 | 0.031 -> 0.032 |

Annbriar, Osage National, Gustin, L.A. Nickell, Tomahawk Hills, Blue Hills, Eagle Knoll, Hot Springs, Pine Dunes,
Veenker and National KC are unchanged.

* **Regret.** It beats "none" in every group: all 22 courses, 5.88 vs 9.12 strokes; the 7 card courses, 1.164 vs
  1.400.
* **Matches.** It does not match across the full held-out set. Away from the 5 new courses it loses 4 holes
  (Ellis 2 and 9, Spirit Hollow 17, Rivercut 9) and gains 2 (Gateway), so the original 10 + 7 v2 courses go
  168 -> 165. The breaks are false native on parkland or partly native courses.
* **Not adopted.** That is exactly the hard-case failure the bar excludes.

### Files

* Scripts in `vision_any/s2/`:
  * `s2year.py`, `s2y_loco.py`: per-season model and drought gate;
  * `s2_apply.py`: the "before" model on new courses;
  * `ng_variant.py`, `ng_eb.py`, `run_var.sh`, `ng_final.sh`, `ng_before.sh`: error budget;
  * `fp_report.py`: false-native area per corridor and course-wide;
  * `drought_diag.py`, `gate_diag.py`, `s2_loco_drop.py`: diagnostics.
* Results: `s2/s2_results_ng.json`.
* S2 stacks for the 10 new courses: `s2/<slug>/`.

**Not verified.**

* Routing and tees of the 5 new courses were checked on the routing map only; there are no per-hole tee sheets.
* The new courses have no OB.
* Mariah Hills' native islands are +/-10 yds; Eagle Bend's native beyond the golfer's 4 holes is from imagery
  only.
* The fused v3 + S2 model was scored at pixel level only (late fusion), not in the error budget.
