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

## State 2026-11-16 (latest): split tee complexes, virtual greens on image evidence, per-hole confidence in gate.json

Measured on the d0+yall bench (detector feae37f33), train out-of-fold, test read once at the end.

What changed (router v2, all defaults):
* `route_scene.split_complex` / `SPLIT_TEES` (env `ROUTE_SPLIT_TEES`, default 1): a scene tee complex spanning >= 25 yd
  whose boxes have a >= 6 yd gap along its long axis is also offered as its two halves (`<id>/a`, `<id>/b`). In
  solve2 the whole complex clashes with each half (tee bit = its own | both halves'), the halves not with each other,
  so two holes can start from one merged complex without the reuse cost. The learned models were refitted on the new
  candidates (route_learn tables `cache/val/learn/split`, prep `cache/val/prep_split`, sc overrides
  `cache/val/sc_split`; route_learn_model.pkl is this fit).
* `solve2.refine_virtual` (V2_PARAMS refine=1): a virtual green (VG: tee found, green not) is moved from the card
  ring onto the strongest U-Net P(green) spot (>= 0.3) at 0.70-1.08 x card yards from its tee (fairway along the line
  as a bonus, never within 18 yd of a green the routing uses), else onto a fairway centreline end at card distance
  (+15 yd). Virtual tees stay on the ring (moving them onto P(tee) / fairway starts: +1 / -4 holes on train).
  Maps carry optional `green` / `tee` channels (route_learn.corridor_maps; the bench takes them from the cached probs).
* V2_PARAMS w_s 0.75 (loop start / end weight; coordinate-descent on train, everything else flat).
* gate: route_gate.pick_threshold had a bug (it stopped at the first row below MIN_SHOWN, so it could never pick a
  threshold); fixed, plus MIN_RATIO = 1.25 (the threshold must sit 25 % above the best-scored wrong train course).
  gate.json gains `routing` = p_all, threshold, per-hole calibrated P(hole right) `p_holes` and `unsure` (p < 0.5),
  for a draft view; shown / not shown is unchanged (p_all + hard blocks). Per-hole calibration (train out-of-fold /
  test): AUC 0.77 / 0.82, log-loss 0.43 / 0.43; bins 0.85-0.95 -> 0.92 / 0.89 right, 0.7-0.85 -> 0.81 / 0.77.

Bench (web-card courses, holes right / all-right):

| split | before (v2, d0+yall) | now |
|---|---|---|
| train (43, out-of-fold) | 75.9 % / 6 | 76.2 % / 11 |
| test (28) | 73.7 % / 5 | 73.7 % / 7 |

Gate refit on the new train results: willowhill 0.32, metamora 0.195, hatherly 0.159 all right, then sun_hills 0.137
wrong. MIN_SHOWN alone would give 0.159 (train 3 / 3 right; test: no course clears it, the top test course somerby
0.142 is wrong). With MIN_RATIO the threshold stays 1.1: nothing is shown.

Tried, measured on train, not kept (code left off by default):
* practice-green model (`route_learn.prac_features` / `cmd_prac`, kind 'p' -> sc 'pp', solver `w_pr`): labels = OSM
  greens ending no hole way, minus those a detected tee plays into (other courses on 27 / 36-hole sites); out-of-fold
  AUC 0.92, but as a cost (w_pr 1-2) it moved 1-3 holes either way (net 0). The practice greens the router takes are
  mostly small U-Net map greens near the clubhouse where the true green is undetected, and penalising them only
  hands the hole to a virtual end.
* dropping card tee sets that do not follow the card's other sets (`solve2.consistent_sets`, set_corr): derryfield's
  odd set is in fact useful there (-12 holes); off.
* final local search: every pairwise swap of two positions, the nine swap and each nine reversed, scored by the full
  objective (fixed-assignment beam): none of the 42 train routings improves. The beam is at a local optimum of the
  objective; the remaining numbering errors are objective errors (the true routing costs more than the chosen one on
  every train course, `oracle` check), not search errors.
* tee box choice by the median card set / the middle box / blended: -0.3 to -0.4 pts.
* per-hole gate with neighbour-hole margin / card fit: train out-of-fold AUC 0.769 -> 0.764; not kept.

Reproduce: `ROUTE_BENCH_PROBS=d0+yall ROUTE_LEARN_VER=feae37f33_d0+yall ROUTE_LEARN_KINDS=h,w,s,e` and
`route_bench.py eval --scene fast --router v2 --card-only --prep --ver feae37f33_d0+yall` with
`ROUTE_BENCH_SC=cache/val/sc_split/cv` (train) / `cache/val/sc_split/test` (test); the overrides come from the same
env + `route_learn.py table|cv|fit --out cache/val/sc_split` after an eval with --prep. Renders (green right, red wrong):
cache/val/render/v3_{ozaukee_wi,south_hills_ca,green_harbor_ma,woods_hole_ma}.jpg.

Blind loop after the change (all 20): tier A / B / C statuses, picks and flagged picks identical to the previous run;
D: Sunset and Remsen drafts (Remsen P(all) 0.104, hole 9 the unsure one in gate.json routing), Glenwild and Hawk's
Point blocked, Makena North no build. Nothing shown.

## State 2026-11-17: TRAIN-BIG (256 more training courses), refit, structured weight learning tried

TRAIN-BIG (`route_big.py`, cache/big, 422 MB, not committed): 340 tier "full" survey courses drawn with a seed
(12 survey states, 18 or 9 OSM hole ways). Excluded: every validation-set course (train and test), the blind20 list
(this covers TEST-40's b20 courses), the perception stacks_meta pool, the U-Net training index, and anything within
1.5 km of one of them. Each course was simulated unmapped through the normal fast path: OSM API, web card search,
NAIP "latest" + 2 other years, canopy, fastscene U-Net (production stride / AMX). Kept per course (~1.6 MB): the
scene, P(green) / P(tee), the corridor maps, the OSM truth and the cards. Raw imagery was deleted. 256 courses were
built. Skipped: 32 without a card, 15 without complete numbered hole ways, 1 closed, 36 not reached (a container
restart). Caveat: the card search's plausibility check sees the OSM hole lengths, as the validation set's did.
route_bench / route_learn read these courses as split `big`; `ROUTE_LEARN_TRAIN=train+big` fits on both.

Refit (`route_learn.py cv|fit --out cache/val/sc_big`, h / w / s / e, same hyperparameters; out-of-fold by state over
train+big). route_learn_model.pkl is now this fit. Pair AUC on old train, out-of-fold: 0.970 -> 0.980.

| split | before (old-train fit) | after (train+big fit) |
|---|---|---|
| train (43, out-of-fold) | 76.2 % / 11 | 76.0 % / 9 |
| big (256: before = never trained on, after = out-of-fold) | 66.6 % / 39 | 72.6 % / 48 |
| test (28, read once) | 73.7 % / 7 | **79.3 % / 7** |

Larger trees (700 x 31 leaves): train 75.8 % / 9, big 73.5 % / 46. Not kept.

Structured learning (`route_struct.py`): the solve2 cost is linear in 15 group weights (hole, detector p, virtual /
miss costs, obstacles, card, walk, loop, virtual geometry, crossings, reuse), checked exactly against the solver's own
cost. solve2 also has optional extra per-(position, option) features weighted by params `xw` (map green, small green,
green near the clubhouse mid-loop, low tee p, relative card misfit, par / length mismatch, virtual end on a par 3, tee
or green not the hole model's best, low ph). They are off by default, so routing is identical. The learner is a
margin-rescaled structured SVM with cutting planes: the decoded routing, the loss-augmented beam's 8 best (hole
Hamming loss), and the truth (each position restricted to right options). Theta is refitted on all constraints with L2
to the current params, and the iterate with the fewest wrong training holes is kept. Result: no out-of-fold gain.
* Old train fold 0 (10 courses): 73.7 % / 1 -> 74.9 % / 2.
* Train+big fold 0 (113 courses): 69.8 % / 17 -> 69.2 % / 18.
* In-sample, wrong holes go 544 -> 495 at best, but the iterates oscillate: the virtual-geometry weight flips to 0
  and back.
Reweighting the existing terms does not make the true routing cheapest. The errors sit in the local scores, and the
refit with more data is what moved them. Not wired into production (V2_PARAMS unchanged).

Gate refit on train+big out-of-fold results (293 courses), route_gate.json. Per-hole calibration on test: AUC 0.814,
log-loss 0.379. Bins: < 0.5 -> 0.23 right, 0.5-0.7 -> 0.49, 0.7-0.85 -> 0.81, 0.85-0.95 -> 0.91, >= 0.95 -> 0.93.
No threshold reaches precision 1.0 with MIN_SHOWN 3. On train+big the top two courses are right, the third is wrong,
and the top 10 are 8 right. On test the two top-scored courses are wrong. So the threshold stays 1.1 and nothing is
shown. A product of per-hole p tops out near 0.39 and does not separate whole courses. A course-level gate needs a
different signal.

Blind loop (all 20), new model + gate vs the previous one: tier A / B / C statuses, picks and flagged picks identical.
D: Sunset draft, Remsen draft (P(all) 0.104 -> 0.234), Glenwild and Hawk's Point blocked (their routings changed),
Makena North no build. Nothing shown.

## State 2026-11-17 (later): auto show policy, TRAIN-BIG 600, P(green) peak greens, richer local features

Product decision (user): every unmapped course that builds is delivered; the golfer never confirms holes.

Show policy (`ROUTE_SHOW_POLICY`, default `auto`; `calibrated` restores the P(all) threshold), route_gate.policy:
* scene-routed courses (tier D, route_scene v1 / v2): shown when the routing is complete. Every hole has
  `p_right` (the per-hole gate's calibrated P(hole numbered right)) and `approximate` (p < 0.5) in package.json, plus
  `routing_confidence`. The card-misfit, long-walk and par-sum gates become `warnings` (fast.SOFT_GATE_PREFIXES).
* tier C (route_joint on OSM greens / tees, or unnumbered OSM hole lines): the same, with
  route_gate.p_joint (`route_gate_joint.json`: logistic on margin, card fit, course min margin, virtual share and
  mode). It was fitted with `route_bench.py joint` on train+big: mapped courses with their hole ways hidden (mode osm)
  or kept without refs (mode lines). Out-of-fold: 89.7 % right, mean P 89.7 %, AUC 0.84. Test: osm 78.2 % right
  against 83.2 % expected (somewhat over-confident); lines 98.5 % against 98.2 %. The min-margin rule is a warning.
* hard blocks are unchanged: no card, missing holes / no routing, card-order conflict, a shared green, a hole with
  neither end, no build (Makena North). Tier A / B are untouched (they never reach either router).

TRAIN-BIG extension (`route_big.py pick2`): 560 more courses drawn (seed 20261117) from the national index
(library/us_courses.json.gz, readiness A / B) in the 36 lower-48 states the 12 surveys do not cover. Same exclusions,
plus 1.5 km around courses already drawn. The build was stopped at 600 kept courses (344 new), 1.06 GB, free disk
1.8 GB, 179 not reached (`build` resumes). Learning curve on the first 256 (out-of-fold on the fixed 299 = 43 train
+ 256 big): 0 % of big in the training folds 71.3 %, 25 % 72.2 %, 50 % 71.7 %, 100 % 73.15 % holes right. Positive but
noisy: one routing flip moves 9-18 holes, and 57 % of wrong holes sit in courses that are more than half wrong.

Missing greens: 354 of 4860 truth greens (train+big 299) had no green candidate. Most are weak, not under trees:
195 have P(green) >= 0.3 within 12 yd but no 0.5 blob; 9 have canopy over them. `route_learn._peak_greens`
(augment_scene, `ROUTE_LEARN_PEAKS`, default 0.2) adds the local maxima of P(green) (smoothed, sigma 3 m, 25 m window,
>= 0.2) that are not within 24 m of a green already offered, as kind `peak` (g_map = 2 in the hole model). It adds
about 4 candidates a course, and truth greens with no candidate go 354 -> 178. Errors on the 299: virtual greens
wrong 266 -> 130, greens that are no hole's green 93 -> 126, holes right +114.

Richer local features (`route_learn` x3, `ROUTE_LEARN_X3`, default 1; tables `LEARN/x3/`):
* hole: fairway / turf / tree profile in 5 bins along the line, water in 3; tree-free / fairway corridor width across
  it; U-Net P(green) at / around the green and P(tee) at the tee; the pair in context (rank / ratio of the prior hole
  score among the tee's greens and the green's tees, card-fit rank, card ambiguity, par-3 length); bunkers at the end.
* walk: turf profile, longest tree run, distance ranks both ways, whether the next hole turns back, walk vs hole
  length, trees ahead of the tee, P(tee), prior outgoing rank.
* loop start / end: scene buildings (largest, >= 250 m2, count within 150 yd), tee + green hub counts, nearest
  other end, P(tee / green).
Pair AUC 0.979 -> 0.984 (log-loss 0.087 -> 0.076). The loop models stay weak (AUC 0.71 -> 0.72). Without peaks, x3 made
holes right worse or no better (72.5 %; blended 73.3 %). With peaks it helps, because P(green) at the green tells a
real peak green from a false one.

Out-of-fold holes right / courses all right (folds by state):

| recipe | fixed 299 | 200 new courses (draw 2, never used for a choice) |
|---|---|---|
| before (split tees, no peaks, no x3; 299 / 499 training courses) | 73.15 % / 57 | 67.78 % / 33 |
| + peaks 0.2 | 75.47 % / 57 | |
| + peaks + x3 | 76.33 % / 65 | 74.80 % / 39 |
| final: + peaks + x3, 643 training courses | 76.27 % / 66 | 73.62 % / 47 (all 643: 75.59 % / 148) |

Re-tuning the solver weights on the 299 (route_bench tune, now with `--slugs` and multi-split): w_h 1.3, w_s 1.0,
c_vg 3, w_x 4 gave 76.3 -> 77.4 % there but 74.8 -> 74.3 % on the 200 new courses: overfit, so V2_PARAMS are unchanged.

Course-level gate (route_scene now returns `alts`, the 8 best other routings as cost gap and holes that differ).
A logistic / GBM on min / 2nd-min / mean / log-product of the per-hole P, share < 0.5 / < 0.7, virtual ends,
card residuals, margins, loop-closure gaps and alternative gaps ranks courses a little better than the product
(out-of-fold AUC 0.817 vs 0.791 on 626 courses). Its top course is right, the next wrong one scores 0.813 against
0.879, so no threshold passes MIN_SHOWN 3 / MIN_RATIO 1.25. Test: AUC 0.86, and the top two test courses are one
right, one wrong. The alternatives are almost all one-hole variants (gaps of 0.03-0.1), so they add little. Not wired
in. The refitted per-hole gate (route_gate.json, 640 courses) now passes on train at P(all) >= 0.475 (4 / 4 right).
No test course clears it, and under auto it only reports.

Test (28 web-card courses, read once): before (ae0953b0f) 79.3 % / 7 all-right, now **80.5 % / 8**. Errors: virtual
green 25 -> 8, another hole's green 25 -> 36. Under auto: 27 of 28 shown (96.4 %). Holes on shown courses: 80.0 %
right, mean P 80.5 %. Approximate holes (P < 0.5) are 29 % right, the rest 86.7 %. Train+big out-of-fold: 626 of 643
shown (97.4 %), 76.2 % right, mean P 76.1 %.

Per-hole calibration (P(hole right) bins -> share right), out-of-fold train+big / test:
< 0.5: 25 % / 29 %; 0.5-0.7: 59 % / 53 %; 0.7-0.85: 80 % / 77 %; 0.85-0.95: 91 % / 93 %; >= 0.95: 96 % / 95 %.
AUC 0.843 / 0.844, log-loss 0.382 / 0.352.

Blind loop (all 20, cache/val/struct/loop/auto*.txt): tier A / B statuses, picks and flagged picks identical; tier C
picks identical, with status changes Brookhaven blocked -> shown (P 0.87-0.98) and Royal Scot ok -> shown
(P 0.83-0.94). Candler, Down River and Heights stay blocked (shared greens). D: Sunset shown (approximate 1, 2, 6;
P(all) 0.001), Glenwild shown (none approximate, 11 at 0.69 the lowest), Remsen shown (all >= 0.80), Hawk's Point shown
(the new routing has no shared green; 11 of 18 approximate, P(all) 0.000), Makena North no build.

Reproduce (defaults now point at the peaks recipe: prep `cache/val/prep_pk20`, tables `cache/val/learn/pk20`):
`ROUTE_BENCH_PROBS=d0+yall ROUTE_LEARN_VER=feae37f33_d0+yall ROUTE_LEARN_KINDS=h,w,s,e ROUTE_LEARN_TRAIN=train+big`;
`route_bench.py eval --scene fast --router v2 --card-only --prep --ver feae37f33_d0+yall --split train+big` (prep),
`route_learn.py table --split train+big`, `route_learn.py x3 --split train+big|test`, `route_learn.py cv|fit --out
cache/val/sc_final`, then eval with `ROUTE_BENCH_SC=cache/val/sc_final/cv` (train+big) / `.../test`.
`ROUTE_LEARN_PEAKS=0 ROUTE_LEARN_X3=0` gives the old recipe (prep_split, learn/split).
Renders (green right, red wrong): cache/val/render/v4_{kingwood_ga,los_amigos_ca,william_j_devine_ma,bonneville_ut}.jpg.

## State 2026-11-18: error taxonomy, routing re-ranker (route_rerank.py, ROUTE_RERANK default 1)

Error taxonomy (train+big out-of-fold, 640 scored courses, wrong holes; "renumbered" = the routed (tee, green) is a
true hole under another number). Before -> after the re-ranker:

| wrong hole | before | after | in courses > half wrong (before) |
|---|---|---|---|
| another hole's green + another hole's tee (scrambled stretch) | 408 | 359 | 321 |
| green right, tee not a hole tee (123 of them: tee 40+ yd behind the OSM line start) | 357 | 371 | 56 |
| green that is no hole's green | 338 | 300 | 165 |
| green right, tee of another hole (shared / merged tees) | 305 | 324 | 56 |
| renumbered: other permutation | 276 | 239 | 189 |
| renumbered: shifted run (loop started from the wrong tee) | 253 | 173 | 206 |
| renumbered: nine swap | 193 | 183 | 169 |
| virtual green wrong | 187 | 196 | 158 |
| another hole's green, tee not a hole tee | 148 | 126 | 114 |
| green right, virtual tee | 70 | 74 | 9 |
| renumbered: reversed segment | 22 | 21 | 9 |
| total wrong | 2564 | 2373 | courses > half wrong 118 -> 104 |

27 / 36-hole sites (OSM hole ways > n + 1): 40 courses, 184 wrong holes (7 %): small, not addressed. Card-order
conflicts: 10 courses, 70 wrong. Oracle over pure renumberings of the chosen routing: 75.9 -> 79.2 %.

Re-ranker (`route_rerank.py`, wired in `route_scene.route` for v2; env `ROUTE_RERANK=0` turns it off; params
`fix_seq` / `rerank`; the bench's `ROUTE_RERANK_PICKS` = json {slug: sequence} of out-of-fold picks):
* alternatives to the solver's routing: the beam's 10 best (plain and priced), all renumberings (rotate / reverse a
  nine, swap nines, both rotated, whole-card rotation), and re-solves with each loop start fixed to another tee
  complex (the next tees of that loop + the top loop-start P) and each loop end fixed to another green (6 each).
* features (relative to the chosen routing): solver cost split (hole, card, walk, loop ends, reuse, crossings), card
  yardage correlation / mean and max relative residual / holes > 15 % off, par 3 / par 5 misfits, loop starts / ends
  distance and rank to the clubhouse, walk sum / max / long walks, loop P sums, hole-model P sum, size of the change.
* model: gradient boosting (absolute loss, 15 leaves, 300 iterations) predicting the gain in right holes; the best
  alternative is taken when its predicted gain > 0.75. Trained only on loop start / end re-solves (beam alternatives
  and renumberings rarely helped and the model picked bad ones: renumberings -18 holes out-of-fold).
  `route_rerank_model.pkl` = fit on all 628 labelled train+big courses. Labels: route_struct.correct (hidden OSM ways).
* choice protocol: kinds / loss / leaves / threshold chosen on the 443 courses outside the 200 never-used ones
  (criterion gain - 2 x worse courses); 5 variants tried.
* cost: about 8-12 s more per 18-hole course (24 fixed re-solves).

| holes right / all-right | before | after |
|---|---|---|
| train+big out-of-fold (643) | 75.59 % / 148 | **77.38 % / 148** |
| 200 never used for a choice | 73.62 % / 47 | **76.48 % / 47** |
| test (28, read once) | 80.5 % / 8 | **82.8 % / 8** |

Out-of-fold the re-ranker switches 73 of 628 courses: 49 better (+222 holes), 13 worse (-31). Test: 4 switched
(william_j_devine 10 -> 17 of 18, visalia 12 -> 15, elmcrest 7 -> 10, kingwood 12 -> 10). Courses all-right do
not move: the switches fix stretches of courses that stay partly wrong. Test errors: another hole's green 36 -> 27.
(Caveat: an exploratory label-count summary of the fitted model on test was printed once before the bench test run;
nothing was chosen after it.)

Per-hole gate refitted on the re-ranked out-of-fold results (route_gate.json; margins of a re-ranked routing are taken
against the solver's own optimum, so changed holes get margin ~0). Calibration out-of-fold / test:
< 0.5: 25 % / 31 %; 0.5-0.7: 59 % / 61 %; 0.7-0.85: 80 % / 72 %; 0.85-0.95: 91 % / 93 %; >= 0.95: 95 % / 96 %.
AUC 0.837 / 0.820, log-loss 0.373 / 0.350. Auto policy: train+big 626 of 643 shown, holes 78.0 % right vs mean P
77.9 %; test 27 of 28 shown, holes 82.3 % right vs mean P 82.2 %.

Reproduce: scratch scripts gen.py (route_struct.decode + route_rerank.candidates / features + labels per course,
resumable), learn.py (out-of-fold by state, threshold grid), picks.py; then route_bench eval with
`ROUTE_RERANK=0 ROUTE_RERANK_PICKS=<picks.json>` (train+big) or plain (test, production path). Renders:
cache/val/render/v5_{william_j_devine_ma,visalia_ca,elmcrest_ma,kingwood_ga}.jpg.

Blind loop (all 20, cache/val/struct/loop/rr1.txt vs auto3.txt): tier A / B / C blocks identical (statuses, picks,
gates). D: the re-ranker keeps every routing (best predicted gains: Sunset -0.56, Glenwild 0.36, Hawk's Point 0.15,
Remsen -1.0; threshold 0.75); only the refitted per-hole P moves. Sunset shown, approximate 1, 2, 6 (P 0.10 / 0.24 /
0.27, the rest 0.64-0.93, P(all) 0.002). Hawk's Point shown, 11 of 18 approximate (P 0.12-0.42; 4, 8, 11, 12,
16-18 at 0.65-0.74). Glenwild (lowest 11 at 0.68) and Remsen (all >= 0.84) shown. Makena North no build.

## State 2026-11-18 (later): per-hole tee refinement (route_tee.py, ROUTE_TEE default 1)

After the routing is fixed (solver + re-ranker), `route_tee.refine` revisits each hole's tee with its green fixed.
Candidates: every box of every tee complex (other holes' complexes too), local maxima of P(tee) >= 0.25 and the
incumbent, within card reach of the green (0.4 x shortest to 1.5 x longest set + 20 yd), 4 yd dedupe; 45 features
(card residuals, offset from the incumbent, P(tee), complex p / size / box rank, other holes' tees / greens, walk from
the previous green, line profile, pair score). Gradient-boosted classifier (300 iterations, 31 leaves, lr 0.05) on
P(candidate counts as this hole's tee under routing.score), trained on holes whose green is right.
`route_tee_model.pkl` = fit on all 633 train+big courses with rows (643 minus 10 with no v2 routing / card).

Choice (`route_tee.choose`): among candidates within eps of the best P, the one whose straight play length is
closest to the course's card set (`course_set`: the set of solve2's card rows that best fits the incumbent tees,
median |residual|); switch when its P beats the incumbent's by more than delta. Why the tie-break: routing.score counts
any spot within 40 yd of the first 60 % of the true line as right, so the model rates forward / middle boxes and spots
down the line as high as the back box. The argmax alone (eps 0, delta 0) gained the most holes but moved 4543 tees
on the 436 choice courses and pushed the bench card error (|line length - best card set|) from 6.4 / 37.9 yd
(median / p90) to 20.8 / 83.1.

Grid on the 436 choice courses (out-of-fold by state; the 197 never-used courses are slugs_new1, untouched). Card
error here is |straight tee-green distance - course set| (a proxy for the bench's line-length error; incumbent 8.5 /
43.1 yd):

| choice | holes gained | switched | card error med / p90 yd |
|---|---|---|---|
| argmax, eps 0, delta 0 | +141 | 4543 | 30.4 / 91.1 |
| argmax, delta 0.05 / 0.1 | +103 / +80 | 901 / 452 | 9.7 / 60.9, 8.8 / 51.3 |
| tie-break by nearest card set of any (r_min), eps 0.05 | +99 | 2432 | 12.5 / 67.6 (491-course run) |
| tie-break by the course set, eps 0.05 / 0.1 | +92 / +85 | 1820 / 1506 | 7.2 / 45.2, 6.7 / 37.8 |
| **tie-break by the course set, eps 0.15, delta 0** | **+89** | 1409 | **6.5 / 35.5** |
| course set, eps 0.2 / 0.3 | +85 / +81 | | 6.5 / 34.4, 6.4 / 33.5 |
| penalty P - lambda x residual (lambda 0.5 / 1) | +81 / +65 | | 6.4 / 34.3, 5.8 / 26.3 |
| switch only if P(incumbent) < 0.85, argmax | +88 | 562 | 8.8 / 51.6 |
| geometric equivalence (pick the card fit within 15-40 yd of the argmax) | +131-139 | | 18-29 / 86-91 |

The nearest-of-any-set tie-break looks fine on relative residuals (each hole fits *some* set) but mixes sets across
holes, so against the one set a golfer plays it is worse than today. The remaining ~50 holes of the argmax's gain
come with ~3000 switches to spots off the card: not taken. Chosen: course-set tie-break, eps 0.15, delta 0 (in the
model file; env ROUTE_TEE_EPS / ROUTE_TEE_DELTA override). Never-used 197: +50 holes (77.29 -> 78.81 %), 60 better /
10 worse, card proxy 9.1 / 45.4 -> 7.0 / 37.9 yd.

Bench (route_bench eval, out-of-fold: `ROUTE_TEE=0 ROUTE_RERANK=0 ROUTE_RERANK_PICKS=<re-ranker picks>
ROUTE_TEE_PICKS=<tee picks>`; ROUTE_TEE=0 is needed with the picks, or courses without a pick get the in-sample
model). Holes right / all-right, card error median / p90 yd:

| | before (re-ranker) | argmax (not shipped) | **shipped** |
|---|---|---|---|
| choice 443 | 77.78 % / 101, 6.3 / 36.4 | 79.69 % / 135, 20.0 / 81.7 | **78.99 % / 119, 6.2 / 38.4** |
| never-used 200 | 76.48 % / 47, 6.6 / 39.8 | 79.52 % / 55, 23.2 / 87.0 | **77.99 % / 51, 6.5 / 42.3** |
| train+big 643 | 77.38 % / 148, 6.4 / 37.9 | 79.64 % / 190, 20.8 / 83.1 | **78.68 % / 170, 6.3 / 39.2** |
| test 28 (read once, production path) | 82.8 % / 8, 5.8 / 29.8 | | **83.2 % / 9, 5.6 / 31.5** |

Test: 6 courses move (elmcrest, kingwood, los_amigos, visalia +1; green_harbor, bonneville -1). Cost about 0.5-1 s a
course.

Per-hole gate refitted on the new out-of-fold results (`route_bench.py gate --train tee_oof15.json --write`, 640
courses). Calibration (P bins -> share right), out-of-fold train+big / test:
< 0.5: 28 % / 31 %; 0.5-0.7: 60 % / 64 %; 0.7-0.85: 80 % / 61 % (62 test holes); 0.85-0.95: 91 % / 93 %;
>= 0.95: 95 % / 96 %. AUC 0.825 / 0.816, log-loss 0.374 / 0.350. Auto policy: train+big 626 of 643 shown, holes
79.3 % right vs mean P 79.3 %; test 27 of 28 shown, holes 82.7 % right vs mean P 83.4 %.

Blind loop (cache/val/struct/loop/rt1.txt vs rr1.txt): tier A / B blocks identical (statuses, picks, gates); tier C
picks and statuses identical (Candler / Down River now log "v2+structure" instead of an AttributeError fallback in
the OSM hole inference, unrelated to routing; same picks, both still blocked on shared greens). D, tees switched
(positions 0-based in route_scene.json tee_refine): Sunset holes 2, 4, 7, 9 (holes 2 / 9 now 377 / 437 vs card
434 / 496); Hawk's Point 2, 5, 6, 11, 16, 18 (6 now 499 vs 596); Glenwild 9, 10, 18 (boxes of the same complex);
Remsen 5, 7. Per-hole P: Sunset 0.22 / 0.29 / 0.93 / 0.80 / 0.89 / 0.49 / 0.65 / 0.87 / 0.74 (approximate 1, 2, 6);
Hawk's Point 11 of 18 approximate (0.16-0.48; 4, 8, 11, 12, 16, 17 at 0.68-0.74, 18 0.52); Glenwild all >= 0.75
(lowest 11); Remsen all >= 0.82. Makena North no build.

Reproduce: scratch tgen.py (training rows per course via route_scene params tee_dump / tee=0, resumable),
tlearn3.py (out-of-fold by state, cached P, grid, picks, fit; uses route_tee.choose / course_set / set_resid).
