# Long grass v3: a precision-first classifier, leave-one-course-out (2026-11-02)

**Decision: not adopted. Long grass stays off** (`model_v2/model.json` `native_thr: null`, `settings.native_off`
unchanged; no package or vision layer was written). Every classifier setting, and a simulated golfer tap, is
worse than no long grass in the error budget.

## What was tried

* **Data.** Every corridor cell (145-440 yds off the tee, |lat| <= 60 yds) on the 11 hand-mapped courses, from
  the cached `vision_any/<slug>/raw` rasters (2 NAIP years each, 0.6 m; 3DEP HAG at 0.25 m steps; Meta CHM; DTM),
  through `v2_model.prepare` (77 v2 features). Labels: hand `native` vs `rough` / `first_cut`. Native on
  Gateway (61k m2), Spirit Hollow (45k), Coldwater (41k), Mozingo (25k), Ellis (5k), Veenker (3k), Eagle Knoll (2k);
  none on Pine Dunes, Hot Springs, Blue Hills, National KC. Not available locally: `raw2` (lidar point
  statistics, 1 m multi-year NAIP). It lives only in the Actions cache, and the queue was ~1.5 h deep.
* **Lidar dates.** Lidar is leaf-off and old: Gateway 2014-03, Mozingo 2014-04, Eagle Knoll 2015-03, Blue Hills
  2006-04, Hot Springs 2018. Spirit Hollow, Pine Dunes and National KC have no PC HAG product (EPT fallback). The
  median HAG of hand native and mown rough is 0.00 m on Gateway, Spirit Hollow and Coldwater. Dormant fescue in
  March does not stand out at 0.25 m quantisation.
* **Features.** (a) the 77 v2 features (`base`); (b) plus a per-course mown-turf reference: robust z-scores of 28
  spectral / texture / HAG features against the course's own cells 3-12 m from the OSM fairway, label-free
  (`norm`); (c) the z-scores plus context only (`normonly`).
* **Model.** LightGBM (15 leaves, 300 trees). Training is balanced per course (≤ 15k native + 15k non-native), and
  each course carries the same total weight. Leave one course out: the held-out course is never seen.

## Separability (why it fails)

The best single feature reaches an AUC of 0.55-0.66 within one course (native vs rough in its corridors), and its
direction flips between courses. Example: z(NIR) is 0.13-0.48 on six courses and 0.77 on Eagle Knoll. Pooled, the
strongest features are context features: distance to canopy (AUC 0.75), then chroma (0.65). Native and parkland
rough look alike in summer NAIP and in leaf-off lidar.

## LOCO, per course (featset `norm`, P >= 0.5, landing corridors 180-320 yds +/- 50 yds, pixel level)

| course | precision | recall | IoU | predicted m2 | hand native m2 |
|---|---|---|---|---|---|
| Gateway | 0.70 | 0.11 | 0.10 | 4,736 | 31,110 |
| Spirit Hollow | 0.76 | 0.08 | 0.08 | 2,139 | 20,756 |
| Coldwater | 0.61 | 0.15 | 0.13 | 4,958 | 20,975 |
| Ellis | 0.15 | 0.02 | 0.02 | 499 | 3,064 |
| Mozingo | 0.64 | 0.08 | 0.08 | 1,183 | 8,951 |
| Eagle Knoll | 0.00 | 0.00 | 0.00 | 2,772 | 656 |
| Veenker | 0.00 | 0.00 | 0.00 | 26 | 1,066 |
| Pine Dunes / Hot Springs / Blue Hills / National KC (no native) | – | – | – | 0 / 198 / 1 / 1,094 | 0 |
| **pooled** | **0.50** | **0.10** | **0.09** | | |

The per-course reference (`norm`) is what moved precision. Pooled precision is 0.14-0.17 for the product model
and 0.35 for `base` here. Pine Dunes falls from 85 % of its eligible area marked native (product, P >= 0.5) to
0.3 %. The other thresholds, pooled precision / recall: 0.3: 0.34 / 0.25; 0.4: 0.41 / 0.17; 0.7: 0.66 / 0.03.
`normonly` at 0.5: 0.46 / 0.19, but it marks 11 % of Pine Dunes course-wide.

* **Corridor-level aggregation.** Ranking corridors by their share of P >= 0.5 gives an AUC of 0.81 for
  "hand native > 250 m2". Among the top 10, Eagle Knoll 9 and National KC 15 are false.
* **Context gate.** Local mean P over 20-40 m windows, LOCO-selected: no setting reaches precision 0.7 on the
  training courses. Pooled precision stays at about 0.55 or below at any recall above 0.05.

## Error budget (`platform/error_budget_variant.py`, n = 4000, seed 31)

LOCO full-grid P(native) feeds `v2_model.native_mask` (strict, committed trees and water excluded) and then
`v2_calibrate.rebuild_package`. The control (the rebuild with no long grass) reproduces the committed zones
(checked on Blue Hills). The 7 card courses and 96 tee shots are the same as in ERROR_BUDGET.md "Follow-up
2026-11-02".

| auto long grass | auto match (7 courses) | regret (strokes) | Ellis | Spirit Hollow |
|---|---|---|---|---|
| none (committed) | **71/96** | **1.357** | 11 / 0.377 | 7 / 0.893 (committed table) |
| v3 `norm` P >= 0.4 | 67 | 1.453 | 11 / 0.380 | 4 / 1.056 |
| v3 `norm` P >= 0.5 | 68 | 1.460 | 11 / 0.375 | 6 / 0.842 |
| v3 `norm` P >= 0.6 | 69 | 1.396 | 11 / 0.375 | 6 / 0.842 |
| simulated tap + fill (≥ 9 m off fairway) | 70 | 1.465 | 11 / 0.427 | 7 / 0.821 |
| simulated tap + fill & P >= 0.2 | 70 | 1.498 | 11 / 0.337 | 4 / 1.163 |
| hand long grass (+long_grass) | 77 | 0.51 | | |

* **Classifier.** The false native on Eagle Knoll breaks holes 3 and 9 at P >= 0.4 and 0.5, and hole 9 at 0.6. On Gateway, P >= 0.5
  places native at 0.67-0.70 precision, but regret rises from 0.425 to 0.502. With recall at about 0.1 the plan
  keeps its club and moves its aim off the found patches, into native the map does not show. Partial native is
  worse than none here.
* **Simulated tap** ("native grass along this hole?", answered from the hand map: > 250 m2 in the corridor).
  The tapped holes get native on every eligible non-tree cell ≥ 9 m from the OSM fairway in their 150-340 yd
  corridor. Gateway improves (9 → 10 matches, regret 0.425 → 0.358, hole 9 fixed). Coldwater breaks (9 → 7, 0.473
  → 0.653) because its native is in patches, and filling the whole rough band puts native in mown rough.

## What would be needed

1. **Extent from the golfer, not a yes/no.** A per-hole tap is not enough. The tap needs where the native starts:
   "native begins about N yds off the fairway, left / right / both", or a drag of the native line on the hole
   photo. A yes/no tap with a geometric fill helped Gateway (links-like, native close to the fairway) and broke
   Coldwater (patchy).
2. **Better signal before another classifier.** Candidate sources:
   * `raw2` lidar point statistics (share of returns at 0.3-1.5 m, multiple returns) on courses with leaf-on or
     autumn lidar.
   * A late-season NAIP year (Oct-Nov), when native has browned and irrigated rough has not. The cached years are
     June-September, except Hot Springs 2021-11 and Pine Dunes 2020-09.
   * Score with `longgrass_v3/run_eb.sh`. The adoption bar is "better than none" on the 7 courses, and Eagle
     Knoll 3 and 9 are the false-native canaries.
3. **More native truth.** 5 courses with substantial native, of which only Gateway, Coldwater and Spirit Hollow
   are links / prairie style. That is too few for a course-type gate to be learned and tested out of fold.

## Reproduce

Scripts are in `vision_any/longgrass_v3/`. Run them from a scratch copy: data files land next to the scripts.

1. `build_ds.py <repo> . <slugs>`: datasets, ~1 min per course (Pine Dunes 3 min).
2. `loco.py norm` writes `pred_norm.npz`; `evalp.py pred_norm.npz 0.3,0.5`, `corr.py` and `ctxgate.py` read it.
3. `build_variant.py <repo> norm var 0.4,0.5,0.6 0 <slugs>` and `tapfill.py <repo> var 9 0 <slugs>`: variant
   packages.
4. `WT=<repo> run_eb.sh <variant>...` scores the variants. `WT=<repo> summ.py eb2/eb_<variant>.json` summarises
   them.

Results: `longgrass_v3/eb_results.json`.

Not verified:
* the `raw2` features, which are Actions-only;
* National KC and Mozingo in the error budget (no card / not scored);
* Spirit Hollow's control row in this harness: its comparison uses the committed table's 7 / 0.893;
* tap fills at other distances, and side-specific fills.
