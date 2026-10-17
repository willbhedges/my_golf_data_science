# Hole formation v2 (zero-tap workstream A)

Pairs every green with its own tee complex, with calibrated probabilities, from OSM features (hole ways hidden) or a
blind perception scene, with or without a scorecard. Output contract: **`hole_pairs/1`** (below), consumed by
workstream C's sequence solver. Results: [RESULTS.md](RESULTS.md).

## Method

1. **Candidates.** The structure solver's tee complexes (`structure/solver.complexes`; perception scenes already
   give complexes, including its fairway-end virtual ones) plus **fairway-end virtual tees**: for each green, the far
   end of every fairway touching it, 15 yds beyond the end, when no candidate lies within 40 yds (`data.add_virtual_tees`).
   On dev they are the right tee for ~12 % of holes (OSM often maps no tee box) and lift the candidate ceiling to
   98-99 %.
2. **Pair features** (`data.pair_features`, every (green, candidate) 70-700 yds apart): the structure solver's 13
   formation features (length vs par mixture, tee-axis alignment, least-cost corridor over fairway / rough / bunker /
   water / woods, green -> fairway -> tee chain, fairway coverage / crossings / ends, crossing another green,
   forward tees, start-of-hole context); the pair's rank and gap within its green and within its candidate;
   candidate confidence / box count / axis weight / virtual flag (and whether the virtual tee was made from this
   green's own fairway); green elongation along the line of approach; distance to the nearest other green.
   **Imagery / lidar** (`aux_build.py`, 5 m layers from the perception stack: U-Net fairway / tee / green, 3DEP
   DTM and canopy, NAIP mowing-stripe orientation): fairway probability along the line (mean, weakest stretch, near the
   green), canopy crossed, a least-cost line of play on the U-Net fairway raster, stripe alignment with the line,
   tee-green elevation change, ridges and valleys crossed, U-Net tee probability at the boxes.
   **Scorecard**: each tee set's yardage vs the distances of the pair's boxes (its complex and the forward
   complexes on its corridor), per card hole (`formation.card_match`), through a soft green <-> card-hole assignment.
3. **Model.** Gradient-boosted trees (`sklearn` HistGradientBoosting) on the pair features (stage 1), then a stage-2
   model on the same features plus the pair's context from the stage-1 logits: its competition in its row and
   column, whether the competing green has an alternative, the stage-1 Sinkhorn marginals, and the card evidence.
   Both are fitted on dev-state training courses only; stage 2 on out-of-fold stage-1 logits.
4. **Global assignment** (`assign.py`): each candidate starts at most one hole, each green ends at most one;
   capacity-constrained Sinkhorn gives the pair marginals (rows sum to 1 with a per-green "no tee" slack), Hungarian
   gives the MAP pairing. Temperature and slack are fitted on out-of-fold dev predictions.
5. **Confidence** of a green's hole: the marginal of its MAP candidate plus that of the candidates on the same line
   of play (its forward / back tees: `formation.corridor_mass`); that is what is calibrated.

## Data and protocol

* Courses: `structure/sets.json` + `generalize/courses` (OSM truth from the hidden `golf=hole` ways, 9 / 18 holes
  with refs 1..N). Splits follow the zero-tap benchmark (`zero_tap/state_split.json`): **train** = dev-state courses
  (CA GA IL KY MA ME MN MS NH UT WI WY), excluding generalize's validation test courses; **held-out** = the 12
  structure held-out states (AR CT DE IA ID MO NC NE NJ NV PA WA); **gtest** = generalize's 31 test courses (dev
  states, never trained on). Model choices were made by 6-fold cross-validation grouped by state on train only;
  held-out and gtest were scored once.
* Inputs: `osm` (OSM scene, hole hints hidden), `perc` (blind perception scene: `perception/scenes`, plus scenes
  built here for courses without one); cards: `none`, `web` (golfify / club site / opengolfapi, chosen without OSM
  lengths for the courses fetched here) and `truth` (a stand-in from the hidden ways: one tee set = line lengths,
  pars where tagged).
* Metrics (`formation.evaluate`): **formed** = the MAP pair for the true hole's green is acceptable by
  `structure/eval.py`'s tee criterion (a box within 35 yds of the true line start, or the back tee within 25 yds of
  its first 60 % extended 90 yds back); **top-1** = the same for the highest marginal; **ceiling** = some candidate
  is acceptable; **ECE / reliability** of the corridor confidence vs formed; **Brier** of the mass on acceptable
  candidates. True greens with no matching scene green count as not formed.

## Files

| file | what |
|---|---|
| `data.py` | course lists / splits, inputs (OSM, perception scene, card, aux), virtual tees, pair features, instances |
| `assign.py` | capacity-constrained Sinkhorn marginals + Hungarian MAP |
| `formation.py` | feature cache (`build`), grouped CV (`cv`), fit + one-time test scoring (`final` -> `model.pkl`, `results.json`, `RESULTS.md`) |
| `hole_pairs.py` | `hole_pairs/1` for one course (API + CLI) |
| `bench_run.py` | `zero_tap_result/1` files for the zero-tap benchmark (formation only, numbers arbitrary) |
| `route_check.py` | the pair marginals inside the structure route CRF (a stand-in for C's solver) |
| `aux_build.py`, `fetch_inputs.py`, `.github/workflows/zt_formation.yml` | Actions: aux layers (artifact `zt-formation-aux`, not committed), blind scenes and web cards (`inputs/<slug>/`) |

## Contract: `hole_pairs/1`

```json
{"schema": "hole_pairs/1", "slug": "dwan_mn", "input": "osm" | "perception", "card_used": true, "aux_used": true,
 "model": "formation-v2@2026-10-17T18:00:00Z", "built_utc": "...",
 "greens": [{"id": "g3", "ll": [lon, lat], "p_hole_input": 1.0,
             "p_no_tee": 0.01,          // P(this green ends no hole of the candidates: practice green / tee missed)
             "p_paired": 0.99,          // 1 - p_no_tee
             "map_tee": "c4", "p_map": 0.81, "p_map_corridor": 0.93}],
 "tees":   [{"id": "c4", "ll": [lon, lat], "boxes_ll": [[lon, lat], ...], "virtual": false, "p_input": 1.0,
             "p_starts_hole": 0.95}],   // sum of its marginals over greens (<= 1)
 "pairs":  [{"green": "g3", "tee": "c4", "p": 0.81, "logit": 2.4, "length_yd": 402.1, "bearing_deg": 81.2,
             "green_ll": [lon, lat], "tee_ll": [lon, lat],   // tee_ll: the complex's back box
             "tee_boxes_ll": [[lon, lat], ...],
             "p_corridor": 0.93,        // per-hole pair confidence: P(this green's hole starts on this line of play)
             "covers": ["c5"]}],        // forward complexes on this pair's corridor (same hole if this pair is right)
 "map":    [{"green": "g3", "tee": "c4", "p": 0.81, "p_corridor": 0.93, "green_ll": [...], "tee_ll": [...],
             "tee_boxes_ll": [...], "length_yd": 402.1}],
 "summary": {"n_greens": 21, "n_tees": 24, "n_virtual": 3, "expected_holes": 18.2, "map_holes": 19}}
```

* `pairs[].p` are **marginals** of the global assignment: per green, `sum(p) + p_no_tee = 1`; per tee,
  `sum(p) <= 1`. Pairs with p < 0.005 are omitted. Use `log(p)` as the formation term of a sequence model; the tee
  exclusivity is already in the marginals, so a solver that enforces it again only double-counts mildly.
* `p_map_corridor` / `map[].p_corridor` is the calibrated confidence that the green's hole starts on that line of
  play (any of its tees). Calibration tables are in `RESULTS.md`.
* Precomputed for every benchmark course and tier by the eval stage: `hole_pairs/<tier>/<slug>.json` (inputs exactly
  as `zero_tap/bench.inputs(row, tier)`); workstream C's `sequence/solve.py --hole-pairs` reads `pairs[]`
  (`green_ll`, `tee_ll`, `p`). For a per-hole certainty gate, use `p_corridor` of the chosen pair.
* `tees[].virtual`: no tee box seen, a point at a fairway end. `tee_ll` of a virtual tee is that point.
* Coordinates `[lon, lat]` WGS84. Ids are the scene's (`g*` / `t*` / `c*` OSM complexes; perception ids for scenes;
  `v*` virtual).

```python
import sys; sys.path.insert(0, "course_data/zero_tap/formation")
from hole_pairs import hole_pairs
from scene import scene_from_osm          # course_data/structure/scene.py (on the path via data.py)
hp = hole_pairs(scene_from_osm(fc, boundary), card=card, aux_path="aux.npz")
```
CLI: `python course_data/zero_tap/formation/hole_pairs.py --osm osm.geojson.gz --course course.json [--card scorecard.json] [--aux aux.npz] --out hp.json`.
