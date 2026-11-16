# Notes from the routing / gate side (fast path, unmapped courses)

Owner of: route_scene.py, route_joint.py, the show / block gate in fast.py, zero_tap/joint/, structure/,
platform/stage_select.py, platform/fastc/routing/, route_bench.py (this side's bench).

## Scenes the routing bench reads (please keep these stable)

`route_bench.py scenes` builds one fastscene scene per validation-set course from YOUR simulated-unmapped packages
`cache/heldout/<slug>/` and YOUR cached U-Net probabilities `cache/heldout/probs/<slug>/d0.npz` (perc_bench.py),
calling `fastscene.build(dir, out=False, P=P)`. Nothing is written into `cache/heldout/`. Scenes are cached at
`cache/val/scenes/<detector version>_<probs variant>/<slug>.json`, the version being the last commit touching
fastscene.py / fastscene_model / fastc/perception / perception / segment/models (+ `-dirty<hash>` of local edits).

Requests:
* Please do not delete `cache/heldout/<slug>/` or `probs/<slug>/d0.npz` for the 82 validation-set courses
  (generalize/validation_set.json, train + test) without a note here.
* When a detector version is the one routing should be measured on, name it in NOTES_PERCEPTION.md (commit hash +
  probs variant, e.g. `d0` or `d0+d1+d2+d3`); the routing bench will rebuild its scenes for it (perceive only,
  a few seconds a course).
* Scene fields routing uses: greens (centroid, p_hole / p, area_m2, kind), tee_complexes (centroid, p, p_range_tee,
  boxes[].centroid, axis_deg, length_m, virtual), fairways (polygon, centerline), parking, clubhouse (ll, p),
  buildings, relations.green_to_tee (p_next).

## 2026-11-16: the 21 validation-train courses missing from cache/heldout

`heldout.py fetch val` had stopped after 30 of the 51 VAL courses; the routing side ran `heldout.py fetch val <the 21
slugs>` and `perc_bench.py probs val d0 <the 21 slugs>` (your tools, unchanged, same layout), so VAL is complete.

## State 2026-11-16 (routing v1 + calibrated gate, wired into fast.py)

What runs for an unmapped course (fast.py route_perception -> route_scene.run, `ROUTE_SCENE_VERSION`, default v1):
* `zero_tap/joint/solve2.py`: the card is the sequence. Options per position: detected (tee, green) pair, VT (green
  found, tee placed on the card ring around it, at the bearing whose line has fairway cover / no buildings and is a
  short walk from the previous green), VG (tee found, green placed likewise toward the next tee), MISS. Corridor
  raster (`corridor.py`): OSM buildings / car parks / public roads + scene buildings / car parks are obstacles for
  real lines and virtual spots. Search: beam over positions, plus a Lagrange-priced beam (green prices from a
  subgradient on the relaxed exact DP) so taking a green early pays for what it costs later holes; the better true
  cost wins. Beam in C (`platform/fastc/routing`, identical to numpy, `GOLF_FASTC=0` = numpy).
* evidence models `model_scene.pkl` (`fit_scene.py`): the joint hole / walk / start / end models refitted on
  detection-like candidates (oracle-noised OSM, bench dev courses outside the validation set).
* gate (`route_gate.py`, `route_gate.json`): per-hole logistic P(right) from margin, card fit, virtual end,
  obstacles, hole-model p, crossings; P(all) = product; threshold picked on train for precision 1.0. On the current
  scenes no threshold reaches precision 1.0 on train (the two highest-scored train courses are wrong), so the
  threshold is 1.1: every scene-routed course is a draft (status "draft", gate.json "draft" reasons). No golfer
  questions (confirm_scene.json is only written by the v0 path).

Bench (route_bench_results.json; validation set simulated unmapped; web-card courses; holes numbered right /
courses with every hole right):

| scene | split | v0 (before) | v1 (now) |
|---|---|---|---|
| fastscene 2ef0018e4 d0 | train (43) | 49.9 % / 0 | 61.6 % / 2 |
| fastscene 2ef0018e4 d0 | test (28) | 49.7 % / 1 | 52.8 % / 1 |
| oracle, spec noise | train (43) | 17.0 % / 0 | 22.4 % / 0 |
| oracle, spec noise | test (28) | 17.0 % / 0 | 22.9 % / 0 |
| oracle, no noise | test (28) | 75.2 % / 5 | 73.9 % / 5 |

Gate: shown 0 of 31 test courses (precision vacuous, coverage 0) for v0 and v1. Blind loop 2026-11-16: tier A / B
and C picks and gates identical; D courses Remsen / Sunset / Glenwild are drafts, Hawk's Point blocked (also by the
shared-green and card gates), Makena North has no build (as before); nothing is shown wrong.

Requests to the detection side: the routing errors that remain on real scenes are dominated by holes whose tee
complex or green is missing or merged with a neighbour's (one complex serving two holes), and practice greens
next to the clubhouse taken as hole 9 / 18 greens (kind "practice" is rarely set). Splitting tee complexes per
hole axis and flagging practice greens would help routing most.

## State 2026-11-16 (later): router v2 (learned scores on real candidates + map greens), ROUTE_SCENE_VERSION=v2

What v2 adds (route_scene.route_v2, used by route_scene.run when ROUTE_SCENE_VERSION=v2 and fastscene.build returns
the 6-class U-Net P; otherwise v1 as before):
* `route_learn.py`: the hole (tee complex -> green), walk (green -> next tee) and loop start / end models are
  refitted on the routing bench's REAL fastscene candidates of the validation-train courses (labels from the hidden
  OSM hole ways), out-of-fold by state for train. New features are read from per-pixel maps on the scene grid:
  U-Net P(fairway) / P(turf) / P(water) / P(bunker) and Meta canopy >= 3 m (trees), along each tee -> green line (fairway
  mean / gaps / tree runs / parallel corridors / one-bend dogleg corridor), around greens and tees, plus detector p /
  area / map flag. Pair AUC 0.933 -> 0.970; correct tee ranked first for 77 % -> 87 % of greens; loop start / end
  AUC 0.44 / 0.46 (the model_scene.pkl ones are worse than chance on real scenes) -> 0.75 / 0.78. Model file
  `route_learn_model.pkl` (all-train fit), applied with `route_learn.rescore`.
* `route_learn.augment_scene`: greens the U-Net P(green) map holds as a solid blob (P >= 0.5, 120-2500 m2) but the
  scene left out are added as candidates (kind "map"); 50 of the 72 train greens the scene missed have P(green) >
  0.8 within 15 m.
* V2_PARAMS (route_bench tune on train): c_vt 3, c_vg 4 (virtual ends cost more), w_x 3 (crossings), tee box by the
  median card set.
* gate: per-hole features + learned ph / pw logits, green / tee detector p, map-green flag; a hard block when the web
  cards disagree on the hole order (route_gate.card_order_conflict: canyon_lake_ca, whose card sources list the same
  holes in a different order). Refitted on v2 train (route_gate.json). Threshold still 1.1: no threshold reaches
  precision 1.0 on train (the top-scored course, billy_caldwell_il, is 8 / 9 right: its 9th green is undetected and the
  router takes a green 38 yd away). On test the ranking is better than v1 (3 of the 4 top courses are all-right) but the
  top one is wrong, so nothing is shown.

Bench (web-card courses, holes right / courses with every hole right; detector 2ef0018e4_d0):

| split | v1 | v2 |
|---|---|---|
| train (43, out-of-fold scores) | 61.2 % / 2 | 72.4 % / 7 |
| test (28, all-train fit) | 53.4 % / 1 | 64.6 % / 4 |

Tried and dropped (train): fairway map as the virtual-spot corridor raster and a linear fairway-cover term for
virtual spots (-0.8 to -2.5 pts); a fairway-scored tee box choice inside merged complexes (no change); walk features
from the learned ph (-3 pts); higher hole-model weight (w_h 1.5-3: virtual ends win, -2 to -6 pts).

Where the remaining train errors are (v2): about half are sequence errors (the true green is routed at another
number), then greens the detector and the map both miss, then tees placed 40-120 yd from the OSM line's start (merged
tee complexes, card back tees vs OSM lines drawn from a middle tee).

Reproduce: `route_bench.py eval --scene fast --router v2 --prep --card-only --ver 2ef0018e4_d0` with
`ROUTE_BENCH_SC=cache/val/sc3/cv` (train) / `cache/val/sc3/test` (test); the overrides come from
`ROUTE_LEARN_KINDS=h,w,s,e route_learn.py table|cv|fit --out cache/val/sc3` (tables need the v2 prep pickles that
an eval with --router v2 --prep writes first). Pixel maps cached at cache/val/maps (85 MB).

### Detector feae37f33, probs d0+yall (the detection side's routing version), same v2 recipe refitted on its scenes

route_learn_model.pkl and route_gate.json are now the d0+yall fit (production runs multi-year by default).
`ROUTE_BENCH_PROBS=d0+yall ROUTE_LEARN_VER=feae37f33_d0+yall ROUTE_LEARN_KINDS=h,w,s,e`, sc overrides in cache/val/sc5;
d0+yall on the bench = d0 averaged with every cached extra-year probability (20 of 51 train courses and all 31 test
courses have them; the others are d0 alone).

| split | v1 | v2 |
|---|---|---|
| train (43, out-of-fold) | 69.2 % / 3 | 75.9 % / 6 |
| test (28) | 73.3 % / 3 | 73.7 % / 5 |

Gate (v2, d0+yall): precision 1.0 on train is reached at P(all) >= 0.174, but by two courses only (willowhill 9 / 9 at
0.33, hatherly 18 / 18 at 0.17; next is billy_caldwell 8 / 9 at 0.10). No test course clears 0.174; the top two test
courses (empire_ranch, westhaven, about 0.10) are both all-right. In the blind loop, Remsen (D) scored 0.170 against
that 0.174. That margin is too thin, so route_gate.MIN_SHOWN = 3 train courses are required and the threshold stays
1.1: nothing is shown. Blind loop after the change: A / B / C picks and gates identical to the v1 run; D: Sunset, Glenwild
and Hawk's Point blocked, Remsen a draft, Makena North no build.

Not done (detection-side handoffs): splitting tee complexes that serve two hole starts by hole direction (29 of 963
on the detector's test 40), and practice greens taken as hole greens (15 of 77). Both are behind the sequence errors
that remain. A per-hole floor (every hole p >= 0.5) on top of P(all) is the next gate idea once more courses clear it.
