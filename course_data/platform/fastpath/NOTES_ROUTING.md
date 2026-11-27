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

## State 2026-11-19: scenes from the national U-Net (golfseg_own_v2), routing models refitted, v2 default

Detector: `FASTSCENE_UNET_MODEL=v2` (default, detector.py; NOTES_PERCEPTION.md 2026-11-19). The routing models read
U-Net maps, so they were refitted on the v2 scenes with the same recipe and hyperparameters (no new choices):
route_learn h / w / s / e (out-of-fold by state, peaks + x3), re-ranker (start / end re-solves, absolute loss, 15
leaves, threshold 0.75), tee refinement (course-set tie-break, eps 0.15, delta 0), per-hole gate. The fits live in
`route_models/v2/` (detector.routing_file); the top-level route_learn_model.pkl / route_rerank_model.pkl /
route_tee_model.pkl / route_gate.json stay the v1 fits (rollback: FASTSCENE_UNET_MODEL=v1). Env overrides
ROUTE_LEARN_MODEL / ROUTE_RERANK_MODEL / ROUTE_TEE_MODEL / ROUTE_GATE_PARAMS win over both.

Scenes: every validation course from its heldout package with v2 probabilities (val years refetched as before), and
all 600 TRAIN-BIG courses rebuilt (scratch rebuild_big.py: package refetched, NAIP pinned to the years the v1 build
used: NAIP 2025 appeared for some states since, 88 package years pinned; 598 of 600 with identical U-Net year sets).
A rebuild with v1 weights reproduced the cached v1 scenes bit for bit. Everything under cache/v2root
(FASTPATH_CACHE), so the v1 caches are untouched. Pair AUC (x3) 0.984 -> 0.988.

Holes right / courses all-right (out-of-fold for train+big; test read once at the end on the production path):

| split | v1 (2026-11-18) | **v2** |
|---|---|---|
| train+big 643 | 78.68 % / 170 | **80.15 % / 183** |
| choice 443 | 78.99 % / 119 | **80.01 % / 130** |
| never-used 200 | 77.99 % / 51 | **80.46 % / 53** |
| test 28 | 83.23 % / 9 | **81.78 % / 9** (402 -> 395 holes) |
| never-used 200 + test 28 pooled (3804 holes) | 78.65 % | **80.63 %** |

Card error median / p90 yd: train+big 6.3 / 39.2 -> 6.2 / 37.0; test 5.6 / 31.5 -> 5.3 / 39.4. Out-of-fold per course:
215 better (+673 holes), 196 worse (-516). Test: 9 better, 8 worse; two courses carry the loss. (The pipeline's
intermediate stages print test numbers, as v1's did; nothing was chosen on them.)

Next lever, from the two test losses (diagnosed, not tuned on): both lost tee complexes, matching the tee-complex
recall drop on TEST-40 (0.834 -> 0.765).
* woods_hole_ma 14 -> 7: v2 scene 23 tee complexes vs 26; the hole 9 start has no complex within 30 m (v1 missed 14
  and 18 instead), and the router renumbered a stretch: wrong 1, 5, 8-15, 18 (v1: 5, 14, 15, 18). Same greens
  (22; truth green 5 missed by both).
* visalia_ca 16 -> 11: 19 complexes vs 23; truth starts 7, 9, 12, 14 uncovered (v1: 7, 10, 12); wrong 1, 7, 10, 16,
  17 (v1 none).
So: give routing the complexes the v2 tee-complex model drops (below its F1 threshold 0.40) as low-p candidates, or
choose that threshold for routing recall on train+big out-of-fold.

Gate refitted on the v2 out-of-fold results (route_models/v2/route_gate.json; threshold still 1.1 under the auto
policy). Blind loop with v2 (cache/val/struct/loop/segv2.txt vs rt1.txt): tier A / B / C blocks identical (statuses,
picks, flagged picks, gates). D, all still shown: Sunset approximate holes 1, 2, 6 -> 2 (P(all) 0.009 -> 0.102);
Glenwild none approximate, card misfit warning 5 -> 3 holes; Hawk's Point approximate 11 -> 14 of 18; Remsen P(all)
0.409 -> 0.432; Makena North no build. Nothing goes from shown to blocked.

Reproduce: scratch pipe.sh (prep, table, x3, cv / fit, gen + learn re-ranker, tgen + tlearn3, out-of-fold eval with
picks, test, gate) with FASTPATH_CACHE=cache/v2root, ROUTE_LEARN_VER=v2seg_d0+yall, FASTSCENE_UNET_MODEL=v2.

## State 2026-11-19 (later): low-p tee complexes as routing candidates (opt-in ROUTE_TEE_ALL=1, not the default)

Lever named above: the v2 tee-complex object model's lower recall. The complexes it rejects are not dropped: every
complex stays in the scene with its calibrated p (the F1 threshold 0.40 maps to p 0.5), and routing's own cutoff
(route_scene, p * (1 - p_range_tee) >= 0.3) is what keeps them out. So the cutoff, not the object model, is the knob.
Coverage of truth tee starts by a scene complex (any box / centroid within 30 m), choice courses (451 with a v2 scene,
never-used and test not read): v2 79.7 % at >= 0.3, 81.8 % at 0.2, 83.1 % at 0.1, 83.4 % at 0.05 and at 0 (complexes
a course 19.6 -> 21.9); v1 84.2 % at 0.3, 85.3 % at 0. The rest of v2's gap is upstream (tee boxes below the complex
builder's min box p 0.3), not tried: it needs a scene rebuild.

Every routing fit was redone per cutoff with the v2 recipe unchanged (route_learn h / w / s / e + x3, re-ranker,
tee refinement, gate; scratch teerec/pipe2.sh = pipe.sh without test stages, ROUTE_P_TEE=<cutoff>). Candidates are still
capped at 3 a hole (54) by p, and complex p is already a route_learn feature (t_p). Out-of-fold, holes right / courses
all-right; card error median / p90 yd on train+big:

| cutoff | train+big 643 | choice 443 | never-used 200 | card err |
|---|---|---|---|---|
| 0.3 (v2 default) | 80.15 % / 183 | 80.01 % / 130 | 80.46 % / 53 | 6.2 / 37.0 |
| 0.2 | 81.52 % / 198 | 81.57 % / 141 | 81.42 % / 57 | 6.1 / 37.3 |
| 0.1 | 82.42 % / 212 | 82.06 % / 153 | 83.23 % / 59 | 5.9 / 36.4 |
| 0.05 | 82.68 % / 203 | 82.64 % / 146 | 82.78 % / 57 | 6.0 / 35.5 |
| **0 (every complex)** | **82.96 % / 209** | **83.01 % / 151** | **82.87 % / 58** | 5.9 / 35.6 |

Chosen on choice 443 holes right: 0 (all-right peaks at 0.1, 153 vs 151; holes is the target). Per course vs 0.3:
choice 120 better (+340 holes) / 58 worse (-119); never-used 50 better (+144) / 35 worse (-64). Cost about +0.1 s a
course (2.06 vs 1.94 s). Re-ranker at 0: 22 picks (54 at 0.3) since the base routing is stronger. Gate refitted on
the cutoff-0 out-of-fold results (640 courses, threshold still 1.1 under the auto policy).

Test 28 (read once, after the choice, bench production path: final fits, sc overrides from the final route_learn
model): 81.78 % / 9 -> **86.54 % / 10** (395 -> 418 of 483 holes; v1 was 83.23 %), card error 5.3 / 39.4 -> 5.0 / 34.8 yd.
9 courses better, none worse: towne_lake_hills 12 -> 17, visalia 11 -> 16, green_harbor 11 -> 15, skokie 12 -> 15,
ozaukee 14 -> 16, elmcrest, kingwood, smoke_rise, woods_hole 7 -> 8 (+1 each). Never-used 200 + test 28 pooled (3804
holes): 80.63 -> 83.33 %.

Blind loop (cache/val/struct/loop/teep0.txt vs segv2.txt, same NAIP years): tier A / B / C identical (statuses, picks,
flagged picks, gates). D: Sunset and Remsen identical; Glenwild shown, P(all) 0.191 -> 0.210, one pick moves (15:
Driver +8 -> +12); Makena North no build; **Hawk's Point goes from shown (P(all) 0.000, 14 of 18 approximate) to
blocked**: hard block "holes 1 and 14 share a green". That fails the ship rule (no tier D course from shown to blocked),
so this is NOT the default: the default stays cutoff 0.3 with route_models/v2/ (re-run of the loop on 2, 4, 13, 18
without the flag reproduces segv2.txt). Not tuned on the loop: 0.05 / 0.1 / 0.2 were not tried there.

Opt-in: `ROUTE_TEE_ALL=1` (v2 only; detector.tee_all / route_p_tee) sets the cutoff to 0 and reads the fits in
`route_models/v2_teeall/` (route_learn / re-ranker / tee / gate at cutoff 0; checked: the loop with only the flag set
gives teep0.txt's Hawk's Point). `ROUTE_P_TEE=<x>` alone overrides the cutoff (fits must match: ROUTE_*_MODEL).
To ship it, the Hawk's Point shared-green block has to be resolved (or accepted) first.

Reproduce: scratch teerec/pipe2.sh FASTPATH_CACHE P_TEE WORKDIR (then route_bench gate --train oof.json --write with
ROUTE_GATE_PARAMS), teerec/testeval.sh (one test read), teerec/cover.py (coverage), teerec/loopcmp.py (loop diff).

## State 2026-11-19 (later): tee cutoff 0 is the default, with a shared-green fallback

The cutoff-0 routing (section above) failed the ship rule only on Hawk's Point (tier D): its chosen routing put holes
1 and 14 on two green candidates 3 m apart, a hard block (fast.extra_gate "share a green"). Policy: deliver every
course, mark unsure holes approximate; hard blocks stay hard. So the routing now avoids a hard block it causes itself.

Fallback (route_scene._shared_fallback, after the re-ranker, before the tee refinement; `ROUTE_SHARED_FALLBACK=0`
turns it off). Shared green = two holes whose package greens are within 15 yd (fast.GATE_SHARED_GREEN_YD). The check
reproduces the package build: a virtual green end snaps to the nearest green the package holds (OSM greens + the
scene greens the routing uses) within 40 yd of its edge, as geometry/build_holes.find_green does (the first version
checked line ends only and picked an alternative that the package then blocked on holes 13 / 16). Only when the
routing has a shared green: alternatives = the routing before the re-ranker, the re-ranker's candidate list (beams,
renumberings, start / end re-solves; reused, not rebuilt), the same list built around the blocked routing, and
re-solves with one green of each offending pair forbidden at that hole / at every hole. Kept: complete (no more
missing holes than before), valid, no shared green. Chosen: fewest holes changed, then lowest solver cost
(`ROUTE_SHARED_ORDER=cost` for cost only). Its changed holes and the blocked pair's holes get P(right) capped at 0.45
(route_gate.FALLBACK_P), so they are marked approximate. The bench's out-of-fold tee picks are not applied to the
changed holes (they were made for the other routing). Cost: about +9 s on a course that needs it, 0 otherwise.
The other routing-side hard blocks are not routing-caused (card-order conflict reads the web cards only; a missing
hole is one no alternative fills), so the fallback handles shared greens only.

Out-of-fold, cutoff-0 fits (route_models/v2_teeall, now v2), train+big 643: 25 courses have a shared green under
the package rule (the bench's line-end rule gate_v0 counted 12); the fallback rescues 21 of them (4 have no complete
alternative without one; gate_v0 shared green 12 -> 3). No other course changes (per-course lines and holes identical
on the other 618 + 3 errors: verified). The rescued courses' holes: order choice on choice 443 only:

| fallback order | choice 443 holes | never-used 200 holes |
|---|---|---|
| lowest cost | -10 | 0 |
| **fewest changed holes, then cost** | **-5** | +1 |

Holes right / all-right out-of-fold with the fallback: train+big 643 82.96 % / 209 -> **82.93 % / 209**, choice 443
83.01 % / 151 -> **82.94 % / 151**, never-used 200 82.87 % / 58 -> **82.90 % / 58** (the cost of no longer counting
holes on courses that were blocked; vs the old default 0.3: +2.78 / +2.93 / +2.44 points). Test not re-read here
(see the tee detection section below for the one test read).

Default switched: detector.ROUTE_P_TEE["v2"] = 0.0 and the cutoff-0 fits are route_models/v2/; the previous v2 fits
(cutoff 0.3) are route_models/v2_p03/, selected with `ROUTE_TEE_ALL=0` (cutoff 0.3 + those fits; rollback).
ROUTE_TEE_ALL=1 is now the default and a no-op.

Blind loop with the new defaults and no env (cache/val/struct/loop/teep0fb.txt vs teep0.txt / segv2.txt): tier A / B
/ C identical (statuses, picks, flagged picks, approximate). D: Sunset, Remsen identical; Glenwild as in teep0 (one
pick 15: Driver +8 -> +12, P(all) 0.210); Makena North no build; **Hawk's Point shown again** (fallback switched hole 1
only, "start" re-solve; approximate 1-8, 13-18 = 14 of 18 as with the 0.3 default; P(all) 0.000). No tier D course
goes from shown to blocked.

## State 2026-11-19 (later): tee detection, P(tee) peak complexes from the U-Net map (v2 default)

Ceiling analysis (choice 443, cutoff 0.05): 351 wrong holes have no tee complex at any p near their start, 69 % of
them with U-Net P(tee) >= 0.1 within 30 m; the misses cluster in courses (worst 20 courses = 47 %;
tb_woodlyn_hills_ia: 4 complexes for 18 holes). Tee boxes need P(tee) >= 0.4 (detect.TEE_P) and box p >= 0.3 to
form a complex, so a weak tee never becomes a candidate. Cheapest fix first (no scene rebuild): candidates straight
from the cached probability maps, the same way augment_scene already adds map / peak greens.

`route_learn._peak_tees` (called from augment_scene, so production route_v2 and every bench / table path get the
same candidates): local maxima of P(tee) (Gaussian sigma 2 m, 15 m window) >= threshold, >= 25 m from every scene
complex box and from an earlier peak, not on a green (centre distance >= radius + 6 m); added strongest first as
one-box complexes kind 'peak' (p = the smoothed peak, outline = pixels >= half the peak, length_m unset, so the
learned models can tell them apart) **until the course holds fill x n_holes complexes** (course-adaptive: a course
with 4 complexes for 18 holes gets 32 peaks; one with 36 gets none). Settings: detector.route_tee_peaks (v2 0.1, v1
off; env ROUTE_TEE_PEAKS, 0 = off) and ROUTE_TEE_PEAK_FILL (default 2).

Coverage of truth tee starts (any complex box within 30 m), choice 451 courses with a scene, 7496 starts: scene
complexes 84.9 %. Peaks with no budget: 95.5 % at p >= 0.15 but 77 added a course (too many for the 60-candidate
solver). With a budget: fixed 6 / 12 / 24 a course 89.2 / 91.0 / 92.9 %; fill to 1.5 / 2 / 2.5 / 3 x holes
89.1 / **91.6** / 92.8 / 93.7 % (4.5 / 11.8 / 19.8 / 28.0 added a course; threshold 0.1 vs 0.2 the same within 0.1).

Routing refitted per variant with the cutoff-0 recipe unchanged (scratch tdet/run3.sh = teerec/pipe2.sh + env, route_learn
h / w / s / e + x3, re-ranker, tee refinement; the shared-green fallback on). Out-of-fold, holes right / all-right:

| variant | train+big 643 | choice 443 | never-used 200 | card err med / p90 yd |
|---|---|---|---|---|
| cutoff 0 + fallback (previous default) | 82.93 % / 209 | 82.94 % / 151 | 82.90 % / 58 | 5.9 / 35.7 |
| **peaks >= 0.1, fill 2 x holes** | **85.63 % / 220** | **85.29 % / 155** | **86.39 % / 65** | 5.6 / 32.0 |
| peaks >= 0.1, fill 2.5 x holes | 85.57 % / 212 | 85.28 % / 149 | 86.21 % / 63 | 5.6 / 31.4 |

Chosen on choice 443: fill 2 (85.29 vs 85.28 %, all-right 155 vs 149; fewer candidates). Per course vs the previous
default, choice 107 better (+340 holes) / 71 worse (-167), never-used 60 better (+179) / 35 worse (-63). Truth pairs
among route_learn's candidates 1838 -> 1971; prep stage (stale models) 71.67 -> 75.43 %. Shared green: 20 courses,
16 rescued by the fallback (4 not). The worst courses barely move (woodlyn_hills 2 -> 0 of 18, great_southern 0 -> 1,
holly_ridge 0 -> 4, edgebrook 0 -> 2, shagbark 0 -> 2, merriland_farm 0 -> 0; brent_bruehl_memorial 0 -> 15): there
the U-Net sees no tee or the card / course data are off. Not tried yet: (b) beyond the fill rule, (c) lidar / DEM pad
or canopy-gap cues, a scene rebuild with a lower box threshold.

Gate refitted on the fill-2 out-of-fold results (route_models/v2/route_gate.json, 643 courses, threshold still 1.1
under the auto policy). Cost: route about the same (bench 2.6 s a course; loop route 1.6-15.8 s vs 1.9-19.2 s).

Test 28 (read once, after the choice, testeval.sh production path): 86.54 % / 10 -> **89.65 % / 12** (418 -> 433 of
483 holes), card error 4.5 / 30.0 yd (was 5.0 / 34.8). 6 better (woods_hole 8 -> 16, elmcrest 13 -> 18, ozaukee,
riverwood_national, green_harbor, crossings +1), 2 worse (lake_tahoe, empire_ranch -1). No shared green on test.

Blind loop (cache/val/struct/loop/teepk.txt vs teep0fb.txt): tier A / B / C identical (statuses, picks, flagged
picks, approximate). D all still shown: Sunset approximate 2 -> none (P(all) 0.103 -> 0.315), Glenwild one pick moves
(P(all) 0.210 -> 0.270), Hawk's Point approximate 14 -> 6 of 18 (6, 10, 13-16; no shared green now, the fallback is
not needed), Remsen P(all) 0.476 -> 0.508; Makena North no build. Nothing goes from shown to blocked.

Shipped as the default (OOF 643 and never-used 200 both better, loop rule met): detector.TEE_PEAKS["v2"] = 0.1, fits
in route_models/v2/. Rollbacks: ROUTE_TEE_PEAKS=0 (no peaks, the cutoff-0 fits in route_models/v2_nopk/),
ROUTE_TEE_ALL=0 (cutoff 0.3, no peaks, route_models/v2_p03/).

## State 2026-11-20: routing selection, ranker re-ranker + hybrid tee choice (v2 default)

Fresh error buckets on the previous default (choice 443 out-of-fold, ceiling/holes.py + analyse.py, cutoff 0 + peaks):
85.29 % right, 1119 wrong holes: a1 (no candidate) 174, b (cut: 20 tee cap, 8 green cap) 28, a2 99, d (card / data)
224, failed 36, **c (routing selection among existing candidates) 558** = green right but tee not a hole start 162,
renumbered other 133, scrambled 66, green that is no hole's green 62, nine swap 53, another hole's tee 38, shift by one
27, virtual green wrong 15. Oracle "perfect routing on the router's candidates" 97.35 % (was 94.2 % before peaks).
Re-ranker candidates (gen rows, route_struct labels, choice): base 86.79 %, oracle over all kinds +383 holes
(start / end only +240); the shipped regressor took +9. Tee refinement rows: oracle +4.8 points, shipped rule +32-36.

Re-ranker (route_rerank, model file key rank=True): LightGBM lambdarank over each course's start / end alternatives
plus seq0 (seq0 = the row of seq0 against itself; graded by right holes, gain truncated at 30; 300 trees, 15 leaves,
lr 0.05, min 40 / leaf, truncation level 3); an alternative replaces seq0 when its score minus seq0's > thr. Out-of-fold
by state on the gen rows, choice / never-used holes gained:

| re-ranker | thr | choice | never-used |
|---|---|---|---|
| regressor start,end (previous) | 0.75 | +9 | +19 |
| regressor all kinds | 0.75 / 1.5 | -1 / +3 | -8 / -2 |
| classifier P(better) - P(worse), all kinds | 0.5 / 0.75 | +30 / +25 | +11 / +12 |
| ranker all kinds | 0.25-1.0 | -7 to -14 | -4 to -8 |
| **ranker start,end** | **0.5** (fixed grid 0-2; max) | **+48** (33 switched, 16 / 9) | +16 |

Tee choice (route_tee): rows regenerated (scratch rsel/tgen2.py: + distance to the true start) under the ranker's picks.
Tried, out-of-fold choice holes gained (card proxy = |straight tee-green - course set| median / p90 yd; incumbent
8.6 / 42.2, previous rule course-set eps 0.15 +32 at 6.5 / 34.9):
* stricter label (tee within 30 yd of the true start): -120 holes at any eps: dropped (the OSM start is often no box).
* extra columns (card residual rank / vs incumbent, boxes behind within 30 yd, P(tee) vs the hole's best): classifier
  argmax +112 vs +118, no gain; a lambdarank ranker on them: argmax +144 (vs +118) but card proxy 36 / 92 yd.
* penalised classifier P - lam x min(residual, 0.3): lam 0.25 / 0.35 / 0.5 -> +68 / +56 / +35 at 7.7 / 6.9 / 6.3 yd
  median (a smooth holes-vs-card trade).
* hybrid: when the classifier's P(incumbent) < tau, the ranker's best (score - lam_r x min(residual, 0.3)) if it beats
  the incumbent's; otherwise the penalised classifier (lam_c). Grid tau {0, 0.9, 0.93, 0.95}, lam_r {8..14}, lam_c
  {0.35, 0.4, 0.5}; cap on the ranker's residual tried, no better.

Guardrail (card error is a product metric: tee spots set the yardages shown): on choice, bench card error at most
+1 yd median and +5 yd p90 over the previous default (5.7 / 32.0). The proxy under-reads the bench p90 (about +2-4 yd),
so the top variants were benched out-of-fold (route_bench eval with the re-ranker / tee picks, same route_learn fits):

| variant (re-ranker / tee) | choice 443 holes / all-right, card | never-used 200 | train+big 643 |
|---|---|---|---|
| previous default (regressor / course-set eps 0.15) | 85.29 % / 155, 5.7 / 32.0 | 86.39 % / 65, 5.6 / 31.9 | 85.63 % / 220, 5.6 / 32.0 |
| w1c ranker / previous tee rule | 85.66 % / 154, 5.7 / 32.1 | **86.21 %** / 65, 5.5 / 30.7 | 85.83 % / 219 |
| w1 ranker / tau 0.93, lam_r 10, lam_c 0.4 | 86.34 % / 168, 6.5 / **39.7** | 87.02 % / 65, 6.5 / 43.1 | 86.55 % / 233, 6.5 / 40.4 |
| w1b ranker / tau 0.93, lam_r 10, lam_c 0.5 | 86.23 % / 165, 6.3 / **38.9** | 86.99 % / 65, 6.3 / 41.6 | 86.46 % / 230 |
| **w1e ranker / tau 0.93, lam_r 12, lam_c 0.5** | **86.08 % / 161, 6.2 / 36.8** | **86.72 % / 66**, 6.2 / 38.1 | **86.28 % / 227**, 6.2 / 37.5 |
| w1d ranker / tau 0.9, lam_r 14, lam_c 0.5 | 85.89 % / 157, 6.0 / 34.4 | 86.57 % / 65, 6.1 / 35.7 | 86.10 % / 222 |

Chosen on choice within the guardrail: w1e (+0.79 points choice, +0.33 never-used, +0.65 train+big). The re-ranker
alone (w1c) gains on choice but loses on never-used (-0.18), so it does not ship alone; the gain needs the tee step.
Regressions to note: card error median +0.5 yd and p90 +4.8 yd (choice), +6.2 yd p90 on never-used (above the choice
guardrail; not chosen on it). A correction I made mid-way and retracted: the out-of-fold tee picks behind the previous
85.63 % do use the production course-set rule (my first offline run had an empty FASTPATH_CACHE, so no cards for
TRAIN-BIG); the earlier numbers stand.

Gate refitted on w1e's out-of-fold results (route_models/v2/route_gate.json, 643 courses; threshold still 1.1 under the
auto policy).

Test 28 (read once, after the choice; teerec/testeval.sh production path, final fits): 89.65 % / 12 -> **89.44 % / 11**
(433 -> 432 of 483 holes), card error 4.5 / 30.0 -> 5.0 / 37.2 yd. 2 courses better (bartram_trail, arrowhead_pointe
+1), 3 worse (elmcrest, smoke_rise, wildwood -1). A small test regression (1 hole), reported, not tuned on. Never-used
200 + test 28 pooled (3804 holes): 86.80 -> 87.07 %.

Blind loop with the w1e fits (cache/val/struct/loop/rsel1.txt vs teepk.txt): tier A / B / C identical (statuses,
picks, flagged picks, approximate). D all still shown: Sunset picks move, P(all) 0.315 -> 0.398 (hole 6 0.73 -> 0.88);
Glenwild picks move, P(all) 0.270 -> 0.247 (holes 10 / 14 0.93 -> 0.86); Hawk's Point picks move, same approximate
holes 6, 10, 13-16, P(all) 0.000; Remsen P(all) 0.508 -> 0.527; Makena North no build. Nothing goes from shown to
blocked. Re-runs with the installed defaults and no env reproduce rsel1 (Sunset, Remsen); ROUTE_SELECT=0 reproduces
teepk (Sunset 0.315).

Shipped as the default (OOF 643 and never-used 200 both better, loop rule met, card guardrail met on choice): fits in
route_models/v2/ (route_learn unchanged; re-ranker = ranker with rank=True, thr 0.5; tee model = classifier +
ranker with lam 0.5, tau 0.93, lam_r 12; gate refitted). Rollback: `ROUTE_SELECT=0` (route_models/v2_pk/: the
previous re-ranker, tee and gate fits; the code reads model files without the new keys the old way). Env knobs:
ROUTE_TEE_TAU=0 (no ranker branch), ROUTE_TEE_LAM=0 (eps tie-break). Cost: the ranker branch adds one LightGBM
predict a hole (loop route times unchanged within noise).

Not done / next: richer re-ranker features (per-hole par fit, walk geometry) need a gen re-run (about 40 min); the
re-ranker oracle over all kinds is still +383 holes on choice and the ranker over all kinds lost holes. OSM footways /
paths survive the bench's hiding (strip_golf drops only golf-tagged features), but bench courses are better mapped
than unmapped ones, so they would be a biased walk signal: not used. Green cap (2 x holes) cuts only 8 wrong holes:
not tried.

Reproduce (scratch rsel/): run_gen.sh (prep, tgen2 tee rows, gen re-ranker rows on the tdet/pk10f2 fits), rr_exp.py /
rr_fit.py (re-ranker variants, picks, fit), run_w1.sh (tee rows under the new picks + out-of-fold bench), tl_exp.py /
tl_pen*.py / tl_hyb.py / tl_cap.py (tee variants), tl_fit.py (picks + fit), cerr.py (per-split holes + card error),
loop_w1e.sh, teerec/testeval.sh.

## State 2026-11-20 (later): re-ranker features + bagged ranker over all alternatives (v2 default); card selection (opt-in)

Re-ranker rows regenerated on the current fits (scratch rsel/gen3.py = gen.py + `route_rerank.features2`; prep rebuilt,
reproduces 75.43 %). New course-level features (FEATS2, model key feats2): par-band yd outside / par-4 misses; card
residual sum, counts over 8 % / 25 %, top-3 mean, best-of-any-set fit, length correlation to the course set; walk
geometry (rank of the next tee among all complexes by distance from the green, backtracking toward the tee just
played, median walk, walk-model cost sum / worst); loop closure (last green to first tee) and clubhouse at both ends;
front / back nine totals vs the card and the gain from swapping the nines; non-adjacent crossings; weakest hole-model
score / count below 0.5.

Clubhouse bias check (as for OSM footways): co["club"] on the bench (train+big 651) comes from OSM car parks 55, OSM
clubhouse tags 6, scene parking 20, none 570 (9.4 % OSM); on the blind loop's tier D courses 0 of 4 have one (tier C:
1 OSM tag of 7, 2 not routed). So the new re-ranker zeroes every clubhouse-derived feature (model key noclub:
club_start / club_end / club_rank_s / club_rank_e / club_both), in training and in production. (route_learn's loop
model reads OSM buildings, lp_bld_*: buildings are mapped independently of golf, left as is.)

Out-of-fold by state on the gen rows (route_struct labels), holes gained choice / never-used (re-ranker oracle over
all kinds +383 / +174):

| re-ranker | thr | choice | never-used |
|---|---|---|---|
| ranker start,end, old features (w1e, shipped) | 0.5 | +48 | +16 |
| + all 44 FEATS2 columns (differences + levels) | 0.5 | +35 | +9 |
| + 6 or 3 FEATS2 differences | 0.5 | +18 / +17 | +8 / +21 |
| all kinds, FEATS2, single ranker | 0.25 | +34 | +33 |
| bagged ranker (5 seeds, 0.8 row / column subsample), start,end, old / FEATS2 | 0.0 | +30 / +36 | +10 / +10 |
| bagged, all kinds, old features | 0.5 | +49 | +26 |
| bagged, all kinds, FEATS2 | 0.0 / 0.5 | +58 / +58 | +30 / +30 |
| **bagged, all kinds, FEATS2, noclub** | 0.0 / 0.5 / 0.75 | +56 / +49 / +46 | +31 / +33 / +32 |

Switches at thr 0.0 / 0.5 / 0.75: choice 339 / 186 / 122 of 431, never-used 159 / 90 / 58. Bench out-of-fold (tee rows
regenerated under each variant's picks, tee rule of w1e unchanged: tau 0.93, lam_r 12, lam_c 0.5):

| variant | choice 443 holes / all-right, card | never-used 200 | train+big 643 |
|---|---|---|---|
| w1e (previous default) | 86.08 % / 161, 6.2 / 36.8 | 86.72 % / 66, 6.2 / 38.1 | 86.28 % / 227, 6.2 / 37.5 |
| bagged noclub thr 0.0 | 86.16 % / 162, 6.2 / 35.8 | 87.35 % / 70, 6.2 / 37.0 | 86.53 % / 232, 6.2 / 36.4 |
| **bagged noclub thr 0.5** | **86.09 % / 161, 6.1 / 36.2** | **87.38 % / 68**, 6.2 / 38.0 | **86.49 % / 229**, 6.1 / 36.8 |
| bagged noclub thr 0.75 | 86.01 % / 167, 6.1 / 35.8 | 87.47 % / 71, 6.2 / 37.8 | 86.46 % / 238 |

Chosen: thr 0.5 (within 0.1 point of the best on choice with half the switches of 0.0; 0.75 is 0.15 below). The choice
gain is flat (+0.01 points); never-used +0.66, train+big +0.21; card error within the guardrail (choice 6.1 / 36.2).
The features alone did not help; the gain came with bagging and all alternative kinds (renumberings, nine swaps and
beams back in).

Gate refitted on the chosen variant's out-of-fold results (threshold still 1.1). Test 28 (read once, production path):
89.44 % / 11 -> **89.23 % / 11** (432 -> 431 holes: elmcrest, arrowhead_pointe -1, smoke_rise +1), card error
5.0 / 37.2 -> 4.8 / 36.0 yd. Never-used 200 + test 28 pooled: 87.07 -> 87.62 %.

Blind loop: a first run with the new fits (rsel2.txt) showed pick / status differences on tier A / C courses (Candler
Park blocked -> ok), but it ran while the test evaluation loaded the machine; re-run idle on every course that
differed (rsel3.txt vs a same-day baseline with the installed defaults, rsel2b.txt; rsel2b vs rsel1 differs only in
Glenwild): tier A / B / C identical (Candler Park, Chevy Chase, Cedar Glen, Zintel Creek, Maplewood, Brookhaven). The
load-sensitive picks are worth knowing about when comparing loops. D all still shown: Sunset P(all) 0.398 -> 0.359;
Glenwild 0.268 -> 0.265; Hawk's Point approximate holes 6 -> 12 of 18 (P(all) 0.000 both; a regression on that
course); Remsen 0.527 -> 0.531 (same picks); Makena North no build. Nothing goes from shown to blocked.

Shipped as the default (OOF 643 and never-used 200 better, loop rule met, card guardrail met): route_models/v2/
(re-ranker: route_rerank.RankAvg of 5 lambdarank fits, feats2, noclub, kinds beam / renum / start / end, thr 0.5; tee
model refitted on the new picks' rows with the same rule; gate refitted). Rollbacks: `ROUTE_SELECT=w1e`
(route_models/v2_w1e/, the previous default) and `ROUTE_SELECT=0` (route_models/v2_pk/).

### Card selection (opt-in ROUTE_CARD_SELECT=1)

d bucket (card / data, 224 wrong holes on choice): card yd off > 15 % 107, multi-course / duplicate ways 74, card
order conflict 34, card count != truth 9; concentrated in 83 courses (canyon_lake 17, tb_valley_co 15,
tb_hermitage_va 14 ...). 439 of 643 courses have two or more web cards, 77 of them materially different (closest tee
sets > 1 % apart); on 6 choice courses another card fits the true holes much better (66 wrong holes; e.g.
tb_valley_co golfify 17 % vs opengolfapi 1.5 %, a card of the sister course on 36-hole sites such as tb_hermitage_va).

Experiment (scratch rsel/cardalt.py): route those 77 courses with every card, hole / walk / loop scores rescored per
card with route_learn fold models (rsel/foldfit.py, the same state folds: out-of-fold), base solver (no re-ranker /
tee step). Oracle (best card per course): choice +85 holes, never-used +35. Rules (switch to the card the routed holes
fit best when better by more than a margin), choice holes (switches, worse) | never-used:

| rule | choice | never-used |
|---|---|---|
| routed median card residual, margin 0 / 0.005 | +68 (23, 3) / +58 (16, 2) | +11 (16, 5) / +8 (12, 4) |
| **margin 0.01** | **+45 (11, 1)** | **+14 (6, 0)** |
| margin 0.015 / 0.02 / 0.03 | +23 / +29 / +10 | +12 / +11 / +9 |
| residual + 0.02 x virtual ends, margin 0 | +74 (23, 2) | +7 (16, 6) |
| solver cost / hole model / margins | +48 / +40 / +68 at best | -1 / +10 / 0 |

Chosen on choice with a penalty of 15 holes per worse switch: margin 0.01 (17 picks). Bench out-of-fold on top of the
new default (switched courses: alternative card rescored with the fold models, their re-ranker / tee picks dropped
since those were made for the other card): choice 86.09 -> **86.50 %** / 162, card 6.0 / 35.7; never-used 87.38 ->
**87.02 %**; train+big 86.49 -> 86.66 %. Never-used loses (tb_knoxville_municipal 16 -> 9, tb_stonetree 17 -> 13,
partly the dropped picks); like-for-like on the 17 switched courses: base solver +45 / +14, in-sample re-ranker / tee
+15 / +3. Fails the ship rule on the strict bench, so opt-in: route_scene._card_select (tier C / D perception path
only, route_scene.run; a request / file / typed card is never replaced; on a switch fast.py writes raw/scene_card.json
and the package uses it). Costs one more routing per differing web card (about 12 % of courses). Not tried: per-nine
card choice, 27 / 36-hole site detection.

Reproduce (scratch rsel/): run_gen3.sh (prep + gen3 rows), rr_exp.py / rr_fit.py (X2=1 NC=1 MODEL=rankbag
KS=beam,renum,start,end THRS=...), run_w2.sh (tee rows, tee fit, bench), clubsrc.py / clubloop.py (clubhouse source),
cardscan.py, run_card.sh (tables, foldfit.py, cardalt.py), cardpen.py, run_w1c.sh (bench with ROUTE_CARD_PICKS +
ROUTE_BENCH_FOLDS), run_card_rt.sh, loop_w2b.sh, teerec/testeval.sh.

## State 2026-11-20 (later): blind loop determinism under machine load

The rsel2 loop (picks / statuses moved on tier A / C / D courses while a test evaluation loaded the machine) was not a
load effect in any solver: no routing, re-ranker, tee or shot-pick search has a wall-clock limit (beams / Lagrange
iterations are counted; decide.py's draws are Sobol / numpy seeded; LightGBM predicts are deterministic). That run
had `FASTPATH_CACHE=cache/v2root` set (the bench env), a cold package cache: every card search ran live and finished
after the build's card budget (phase 2 at 34-93 s), six courses got no card or another source (Chevy Chase no card ->
the OSM-nearest-tee fallback; Glenwild / Hawk's Point 91 / 93 s, past loop.py's 90 s wait), so packages differed.
The one wall-clock path in the fast path is the card budget (fast.CARD_BUDGET_S 15 s / CARD_GRACE_S 1 s, then
loop.py's wait_card(90)); with cached cards it never fires.

Fix: loop.py waits for a late card search without a time limit (fast.wait_card(None)), so a slow search on a busy
machine is never rebuilt without its card. Production builds keep their budget (latency), unchanged.

Check (default cache, installed defaults, no env): idle loop (scratch t1/idle1.txt) = rsel3.txt on every course it
holds; the loop under artificial load (8 busy processes on 4 cores, load average ~11; t1/load1.txt) identical to
idle on all 20 courses (statuses, picks, flagged picks, approximate holes, p_holes, warnings; only timings differ);
after the change, an idle loop (t1/post1.txt) identical to idle1 line for line except timings. Hawk's Point
approximate holes 12 of 18 (4-10, 13, 15-18) in all three.

## State 2026-11-20 (later): DEM pad tee complexes (opt-in ROUTE_TEE_PADS=1, not the default)

Target: choice wrong holes with no tee candidate at all (a1, 174 before the tee-choice work), concentrated in whole
courses where the U-Net P(tee) is ~0 (woodlyn_hills, merriland_farm, shagbark, edgebrook, holly_ridge, paintsville,
hansen_park ...). Per the scorer's tee rule (a candidate within 40 m of the first 60 % of the true line) the current
scene complexes + P(tee) peaks leave 176 truth starts on choice 443 (83 on never-used) with no acceptable candidate
(631 / 282 without one within 30 m of the start).

(a) DEM pads. Data already fetched: fastscene builds its grid from the package DEM (3DEP exportImage, 1 m,
imagery/dem.tif), and perceive already turns lidar pads into tee boxes, but a lidar-only box gets p 0.25-0.5 and the
complex builder keeps boxes >= 0.3, so most never become complexes; TRAIN-BIG kept no DEM. The bench job (scratch
pads/padgen.py) fetched the 3DEP 1 m DEM on each bench scene grid (680 courses; 2 fetches failed: tb_tara_sc,
tb_robert_trent_jones_hampton_cove_al, no pads there; DEM deleted after use) and ran tees/lidar_pads.components
(slope < 5 %, top-hat > 0.05 m, mean >= 0.1 m, >= 30 % banked ring, 30-2000 m2): ~150 pads a course. Raw pads cover
96 of the 176 (54 %) but at 1 % precision; a pad classifier (route_pad_model.pkl: LightGBM on pad shape, U-Net class
means under the pad, distance to the nearest complex / green edge; label = within 30 m of a start no complex covers;
out-of-fold by state, AUC 0.909, 99 133 pads, 395 positive) ranks them. Coverage of the 176 / 83 (choice / never-used)
by pads >= 25 m from every complex and clear of greens, filling to 3 complexes a hole: score >= 0.01 53 / 29 (5.8 pads a
course), >= 0.02 40 / 22, >= 0.05 22 / 11 (1.3 a course); turf-score ranking instead: 43 / 27 at 8 a course.
Pads go in as one-box complexes kind 'pad' (p = score) with a source column t_src (0 scene, 1 peak, 2 pad) in the
route_learn tee attributes (only in fits made with pads: model key tsrc). They are added to the solver's candidate list
after the split halves of real complexes (the first run put them before and cut truth pairs 1971 -> 1888 through the
60-candidate cap; fixed, 1987).

Full refit per variant with the shipped recipe unchanged (scratch dpad/run.sh: route_learn h / w / s / e + x3, gen3 +
bagged ranker thr 0.5, tgen2 + hybrid tee rule 0.93 / 12 / 0.5, out-of-fold bench), out-of-fold holes / all-right, card
median / p90 yd:

| variant | train+big 643 | choice 443 | never-used 200 |
|---|---|---|---|
| default (bagged noclub thr 0.5) | 86.49 % / 229, 6.1 / 36.8 | 86.09 % / 161, 6.1 / 36.2 | 87.38 % / 68, 6.2 / 38.0 |
| A: pads score >= 0.01, fill 3 | 86.28 % / 231, 6.2 / 37.8 | 85.95 % / 161, 6.1 / 37.4 | 86.99 % / 70, 6.3 / 39.2 |
| **B: pads score >= 0.05, fill 3** | 86.43 % / 228, 6.1 / 37.6 | 86.12 % / 162, 6.1 / 37.8 | 87.11 % / 66, 6.2 / 36.9 |

Per course vs the default: A choice 73 better (+132) / 75 worse (-142), never-used 32 (+74) / 38 (-87); B choice
66 (+130) / 66 (-128), never-used 26 (+50) / 33 (-59). Re-ranker OOF gain on the new rows: A choice +61 / never-used
+68, B +69 / +23 (default +49 / +33). The collapse courses under A: paintsville 0 -> 8, woodlyn 0 -> 1, merriland
0 -> 0, black_desert / hunter 0 -> 0, but shagbark 6 -> 2, edgebrook 7 -> 3, holly_ridge 4 -> 1, great_southern 1 -> 0.
The per-course swings both ways are of the size of refit noise; the net is flat on choice (B +2 holes) and negative
on never-used (A -13, B -9). Fails the ship rule (OOF 643 and never-used 200 must both improve): NOT the default. Test
not read (nothing to ship).

Opt-in: `ROUTE_TEE_PADS=1` reads route_models/v2_pads/ (variant B: route_learn / re-ranker / tee / gate fits +
route_pad_model.pkl; ROUTE_TEE_PAD_MIN 0.05, ROUTE_TEE_PAD_FILL 3) and is ignored under every rollback (ROUTE_SELECT,
ROUTE_TEE_PEAKS=0, ROUTE_TEE_ALL=0). Production (route_scene.run) computes the pads from the package's imagery/dem.tif,
which is the scene grid: on 4 loop packages the package DEM equals a fresh 3DEP fetch on the scene grid (max |dz| 0)
and the pads are identical (102 / 37 / 41 / 256). Cost: no extra network (the DEM is fetched for the scene and
elevation stages anyway, cold 2-5 s / 4-10 MB, warm 0); +0.4-1.1 s CPU a course. No DEM, a DEM off the scene grid or
mostly NaN, no 1 m coverage (the seamless fallback yields few or no pads), a missing model or any pad error -> no pads,
the build goes on (checked: Remsen with the pad model path broken is shown, not blocked).

Blind loop with the opt-in on (ROUTE_TEE_PADS=1 only, pads computed from each package DEM; scratch dpad/loop_pads.txt
vs t1/post1.txt): tier A / B / C identical (statuses, picks, flagged picks, approximate). D all shown: Sunset P(all)
0.359 -> 0.412, Glenwild 0.265 -> 0.225 (one pick), Hawk's Point approximate 12 -> 6 of 18 (6, 10, 14-16, 18; P(all)
0.000 both), Remsen same picks, Makena North no build. Route stage +0.2-0.9 s a course. With the flag off, the loop
after these changes (t1/post2.txt) is identical to today's idle baseline (t1/idle1.txt) line for line except timings.

(b) geometry virtual tees, not tried as separate candidates: solve2 already places virtual tees on the card ring at
every bearing with corridor costs, and of the 103 a1 'tee' holes 87 were routed onto a wrong real tee rather than a
virtual one, so more candidates of that kind would face the same competition. (c) a scene rebuild with a lower
box threshold is not cheap: TRAIN-BIG kept only probabilities and scenes (needs the NAIP / DEM / canopy refetch).

Reproduce (scratch pads/, dpad/): padgen.py (DEM -> pads), cover.py / cover2.py / ana.py (coverage), padfit.py (pad
classifier OOF + bench pad files keyed by scene grid), dpad/run.sh WORKDIR MIN FILL (refit + bench; env ROUTE_TEE_PADS=1
ROUTE_PADS_DIR ROUTE_PAD_MODEL), parity.py (production vs bench pads), dpad/loop_optin.sh.

## State 2026-11-20 (later): why the router picks a wrong real tee (diagnosis; nothing shipped)

Current default, out-of-fold, choice 443 (scratch t2/tdiag.py, gdiag.py; scorer tolerances: green 20 m, tee within
40 m of the first 60 % of the true line). 1024 wrong holes: green wrong 696, green right + wrong real tee 309, virtual
tee wrong 19 (never-used 200: 419 = 229 / 177 / 13).

Green wrong (696; never-used 229): right green routed to another hole (numbering / sequence) 488 (174); right green a
candidate and unused 128 (37); no router-candidate green within 20 m 80 (18; 9 / 2 of them below the router threshold /
cap); 81 on virtual greens. 444 of the 696 are on 35 collapse courses (>= 60 % of holes wrong; never-used 78 on 7).
Outside the collapses: 154 / 82 / 16 (never-used 101 / 35 / 15).

Green right, wrong real tee (309): a right candidate complex exists and no other hole uses it 237, it is used by another
hole 30, no right candidate 42 (the a1 'tee' bucket of the old default, 103, shrank with the peaks). The chosen tee is
another hole's start in 44. On the route_tee rows (regenerated on the default, t2/tg_tb; the hybrid rule reproduces
86.15 % on choice): of 6646 green-right holes 6319 right, 293 wrong with a right candidate among the tee step's
candidates, 34 without one. Of the 293, ~200 have the right candidate with a much worse card residual (median 0.18 vs
the chosen 0.03; mostly a shorter box, i.e. a forward / middle box of the right hole), and in 92 the classifier
already ranks the right one higher: the card penalty overrides it. Where the chosen wrong tee fits the card better by
> 10 yd (113 holes), the true OSM hole length is itself off the card yardage by a median 18 % (81 over 10 %, 33 over
25 %): the card number (or set) does not describe the true tee, so card fit pulls the tee off the hole.

Tried (offline, out-of-fold on the tee rows; card proxy = |play length - course set| median / p90, the default rule
6.5 / 35.2 yd on choice; proxy p90 reads ~2-4 yd under the bench):
* rule grid tau {0, .9, .93, .95, .97} x lam_r {0..12} x lam_c {0..0.5}: holes-only rules gain up to +149 choice /
  +105 never-used holes (87.35 %) but at card 34 / 90 yd; within the guardrail the best is tau 0.9, lam_r 8, lam_c 0.5:
  +72 vs +61 choice, +39 vs +41 never-used (6.5 / 36.3 yd): flat, not benched.
* card-distance spots (each candidate moved along its line to the card distance as an extra candidate, src 'ext',
  classifier / ranker refit; t2/tg_ext): card proxy drops to ~2 / 34 yd but holes gain falls (+56 choice at best
  within the guardrail, never-used +29 vs +41).
* move the chosen spot to the card distance when it misses by > 10 / 15 / 25 %: loses 19-335 holes (the card
  distance lands behind the true start or on another line).
* 'virtual over a far real tee' (idea 2): 19 + 42 holes in reach, and on the tee rows the virtual spot is no better
  placed (the card ring has the same card-truth mismatch). Tee swaps between holes (idea 3): 30 holes in reach.
So the tee lever is capped by the card guardrail itself (the guardrail measures the same card fit that pulls the tee
off), not by missing features: route_tee already has card residuals, used_other, walk, angles, P(tee). The larger
lever is the green / numbering side (488 renumbered holes, 444 in collapse courses). Code unchanged (the ext spots were
an experiment in route_tee and are not kept).

Reproduce (scratch t2/): tdiag.py / gdiag.py OOF.json OUT.jsonl, tg.sh (tee rows on the default), tg_ext.sh
(+ ROUTE_TEE_EXT spots, experiment code not committed), tana.py, tgrid.py, tpost.py (with rsel/tl_exp.py).

## State 2026-11-20 (later): 9-hole courses with an 18-hole card routed as n = 9 (default; ROUTE_NINE_DUP=0 rollback)

Many 9-hole cards list the nine twice (holes 10-18 = 1-9 from other tees); the router then routes 18 distinct holes
on a 9-hole scene (tb_o_donnell_ca 0 of 9 right). Rule (route_scene.route_n / nine_dup / front_nine, applied in
route_scene.run on web cards only): an 18-hole card whose best complete set has back-nine yardages within 5 % of the
front nine (median per hole, NINE_DUP_TOL) on a scene with <= 12 candidate greens (p_hole >= 0.35, the raw scene,
NINE_MAX_GREENS) is routed as 9 holes on the front nine; fast.py then builds the package on the front-nine card
(raw/scene_card.json, as card selection does), so the course is delivered as the 9 holes it has. The card test alone
also fires on real 18-hole courses (royal_manchester, green_oaks, wuskowhan: 18-23 scene greens), hence the green cap.

Prevalence (train+big, 643): the rule switches 3 courses, all choice: tb_cedardell_il, tb_o_donnell_ca,
tb_nevada_mo (truth 9 holes each); none on never-used (tb_highland_ma, a truth 9-hole course at 8 / 9, has a 6 %
nine difference and stays at 18; tb_harry_mussatto_wiu_il 9 / 9 likewise); none on test 28 (so test stays 89.23 %, not
re-read). Bench (scratch t2/nine_run.py: route_bench.load_course monkeypatched with route_n, the route_learn fold
models for out-of-fold scores, re-ranker / tee steps off in both arms since the out-of-fold picks were made for 18):
cedardell 8 -> 9, o_donnell 0 -> 7, nevada 6 -> 8 of 9. With those three replaced in the default's out-of-fold
results: train+big 643 86.49 % / 229 -> **86.59 % / 230**, choice 443 86.09 % / 161 -> **86.23 % / 162** (card 6.1 /
36.2 -> 6.0 / 35.7 yd), never-used 200 87.38 % / 68 unchanged (no course affected). Blind loop (t2/loop_nine.txt) is
identical to today's idle baseline (t1/idle1.txt) line for line except timings: no blind-20 course triggers the rule.
Hawk's Point approximate 12 of 18 (unchanged). The bench's own n is set in route_bench.load_course; the one-line hook
(n = route_scene.route_n(card, raw scene, n)) waits for the other route_bench.py work to land.

### 27 / 36-hole sites: cluster routing on scenes with many greens (default; ROUTE_MULTI_SITE=0 rollback)

Truth sites (OSM hole ways with duplicate refs or >= 5 extra ways): choice 7 (62 / 126 right: hermitage 0,
rtj_hampton_cove 1, mississippi_national 7, spring_lake_ny 9, toscana 12, falmouth 16, wellesley 17), never-used 1
(revere 18 / 18). The course boundary (course.json) encloses every course of the site on all of them, and more than
one golf_course polygon over 15 ha flags 2 of the 7 plus 38 single courses, so neither separates the courses. Raw
scene greens >= 1.5 x n flags 7 of the 8 sites and 5 single courses (101 / 126 right on 1.4 x n: 7). The truth
itself takes one way per duplicated ref (routing.truth_from_fc: the par-tagged one), which mixes courses on hermitage
(3 truth walks > 400 yd, up to 1884 yd) and toscana (1066 yd).

## State 2026-11-20 (later): card sanity + source vote in the card choice (default; CARD_SANITY=0 rollback), bench card = production's pick

From the collapse diagnosis (courses with <= 40 % of holes right: choice 35 / 457 wrong holes, never-used 8 / 105),
two of the causes are card data, not routing: broken cards and cards that other sources contradict.

Changes:
* `scorecard.sanity`: a card none of whose tee sets lists yardage on 80 % of its holes is unusable. OpenGolfAPI
  sometimes returns per-hole rows empty but for the last hole (tb_rocky_ford_co Blue [None x 8, 369] under a stated
  2904 yd; the par row then comes out sorted 5, 5, 5, ..., 3, 4). `choose_card` drops such cards first; with none left
  it returns None (the course routes card-blind, which it already did: zero_tap.joint.solve.card_sets ignores a set
  with a missing hole, so has_card was False on such a card and route_gate's no-card block applied before and after;
  the no-card block is unchanged). `card_consensus.consensus` drops them too: its ground share over the holes that
  have yards scored such a card 1.0 (1 of 1), so it won the base on tb_hillcrest_sc / tb_rocky_ford_co.
* `scorecard.source_vote` (CARD_VOTE=agree, default): support(card) = 1 + the other sources whose card is the same
  (`nine_order` 'same': median per-hole relative gap <= 4 % on the closest pair of complete sets and, for 18 holes,
  the nine-swapped order 3 points worse). When some card has more support than the reliability pick, the most
  reliable card of that group (one passing `consistency` if any) is taken. A lone card that two others contradict
  loses, whether its nines are swapped (tb_reflection_bay_nv golfify) or it is another layout (tb_naperville_il
  golfify). A tie keeps the reliability order. CARD_VOTE=nine: only the nine-swap case (the first version);
  CARD_VOTE=off: no vote.
* Tie-break by a clubhouse / hole-1 prior: not used. It needs one routing per card, and on the two tied nine-order
  courses (tb_valley_co golfify vs opengolfapi, canyon_lake_ca) the scene clubhouse would pick the wrong card (valley:
  hole-1 tee 56 yd from the clubhouse on the wrong card vs 84 yd on the right one, clubhouse p 0.04) or is about
  1300 yd from both starts (canyon). No source preference either: the only one the bench would support
  (opengolfapi over golfify on the ties) is circular (next point).
* OpenGolfAPI / OSM circularity: OpenGolfAPI is ODbL and partly derived from OpenStreetMap. On the bench every course
  is OSM-mapped (the truth), so OpenGolfAPI agreeing with the truth's hole order is not independent evidence, and
  preferring it would flatter the bench on courses production meets unmapped. In the vote OpenGolfAPI counts as one
  source like any other. Every switch the vote makes on the bench has OpenGolfAPI as one of its two votes, but always
  with an independent source (allsquare or golfify) agreeing on the per-hole yardages, which OSM does not carry. Without
  OpenGolfAPI's vote all five switches would be ties (no switch). Read the gains with that caveat.
* Bench parity (route_bench.bench_card, ROUTE_BENCH_CARD=pick, now the default): the bench routed scorecard.json's
  `chosen` raw card. For TRAIN-BIG that was package.pick_scorecard on raw/summary.json, i.e. card_consensus on the OSM
  hole lengths the bench hides: an OSM-informed card choice production does not have on an unmapped course (there,
  pick_scorecard has no ground and falls back to choose_card). 45 of the 643 courses (31 choice, 14 never-used) differ
  from production's pick. The bench now uses production's pick; ROUTE_BENCH_CARD=chosen restores the old card. The
  fits in route_models/v2 were made with `chosen` (not refitted: 50 courses change card). Cached prep pickles keep the
  card they were made with.
* Secondary bench metric `hole_acc_fwd` (route_bench.hole_ok_fwd; primary unchanged): a hole also counts as right when
  its green is right and its routed tee sits behind the OSM way's start (within 40 yd of the first segment's line, up to
  200 yd back): the OSM way starts at a forward tee, and the router took the back box (tb_sand_creek_station_ks
  6 -> 17, tb_bear_ridge_tx).

Evaluation (current models, no refit). The 52 courses whose card changes under any variant were re-prepared with
each card and routed by the base solver with route_learn state-fold models (rsel/folds; out-of-fold; the re-ranker /
tee step off because their out-of-fold picks were made for the old card). Each course's like-for-like delta was then
added to the default's out-of-fold result; the other 591 courses keep the default's result. The default bench was
re-run on the current code first (cardfix/fwd_oof.json): 86.49 %, identical hole_ok on all 643 courses. Holes right
(primary) / hole_acc_fwd, card error median / p90 yd:

| variant | train+big 643 | choice 443 | never-used 200 |
|---|---|---|---|
| default (bench card = chosen) | 86.49 % / 87.87 %, 6.1 / 36.8 | 86.09 % / 87.27 %, 6.1 / 36.2 | 87.38 % / 89.19 %, 6.2 / 38.0 |
| parity (production's old pick, CARD_SANITY=0) | 86.27 % / 87.64 %, 6.1 / 36.2 | 86.15 % / 87.31 %, 6.0 / 35.0 | 86.54 % / 88.38 %, 6.2 / 38.1 |
| sanity + nine vote (CARD_VOTE=nine) | 86.41 % / 87.78 %, 6.1 / 35.9 | 86.15 % / 87.31 % | 86.99 % / 88.83 % |
| **sanity + source vote (shipped)** | **86.83 % / 88.21 %, 6.1 / 35.7** | **86.42 % / 87.58 %, 6.0 / 34.5** | **87.74 % / 89.58 %, 6.2 / 37.5** |

All-right courses (switched courses substituted): 643 227 / 228 / 228 / 230; choice 160 / 163 / 163 / 164; never-used
67 / 65 / 65 / 66.

Shipped vs parity (the production change): +60 holes (choice +20, never-used +40), no course worse.
* Choice: tb_belvedere_mi 0 -> 18 (golfify + opengolfapi agree; allsquare, the consistent-card pick, is another
  layout); tb_nevada_mo 6 -> 8.
* Never-used: tb_naperville_il 1 -> 18; tb_greenview_il 9 -> 17; tb_reflection_bay_nv 0 -> 15 (the nine-swap case).
* The 5 courses whose only card is broken (tb_hillcrest_sc, tb_lakeside_ut, tb_oshkosh_wi, tb_eagle_crest_ny,
  tb_northern_michigan_university_mi) now route with no card: 0 holes changed.

Parity vs the old bench card (a measurement correction, not a production change):
* Choice: 10 courses better (+41), 6 worse (-37; tb_belvedere_mi -18, which the vote recovers).
* Never-used: 1 better (+5), 4 worse (-33; naperville -17 and greenview -8, both recovered).
* Shipped vs the old bench card: choice 11 better (+43) / 5 worse (-19: indian_trace -6, blue_hill -6, coventry_pines
  -5, wollaston -1, goat_hill -1); never-used 2 better (+20) / 2 worse (-8: burlington -7, gallery -1). The worse ones
  are courses where production's pick was always this card and only the OSM-informed bench choice had hidden it.
* B1 / B3 of the diagnosis (tb_rocky_ford_co 0 -> 8, tb_targhee_village_wy 4 -> 7, tb_monona_wi 0 -> 9) were
  bench-only: production's choose_card already took the good card there.

Protocol note: the vote was generalised from nine-swap to agreement after seeing the parity losers, which include two
never-used courses (naperville, greenview). So never-used is not untouched for this choice. The choice split alone
supports the rule (+20, no course worse).

Ship rule: OOF 643 and never-used both better (vs parity and vs the old default). Blind loop with CARD_SANITY=0 vs the
default (cardfix/loop_off.txt / loop_on.txt, same code otherwise): all 20 courses identical line for line except
timings (statuses, cards, picks, gates, approximate holes); nothing goes from shown to blocked. Test 28 (read once,
production path, route_models/v2 fits, bench card = pick): **89.23 % / 11, card error 4.8 / 36.0**, identical routings
on all 28 courses (no test course changes card); hole_acc_fwd 89.44 % (432 / 483).

Rollbacks: CARD_SANITY=0 (no sanity filter, no vote: production's old choice); CARD_VOTE=nine / off;
ROUTE_BENCH_CARD=chosen (the bench's old card). Not done: the no-card block (route_gate "no scorecard yardages") is
unchanged; no refit on production's cards; a per-orientation routing for nine-order ties.
test_package.py::test_black_package_uses_the_joint_tee_stage fails with or without the change (CARD_SANITY=0 too).

Reproduce (scratch cardfix/): count2.py (picks per variant), run.sh MODE base|live (switched courses; modes chosen /
par0 / new / agree), run_def.sh (default OOF with hole_acc_fwd), cmp.py base (tables), loop.sh, testeval.sh.

Rule (route_scene._multi_site, from route_v2, so also inside card selection): when the raw scene holds >= 1.5 x n
candidate greens (MULTI_GREENS), the augmented candidates are split by k-means on the green centroids (k = 2 and 3,
sklearn, fixed seed; every green / tee complex to the nearest centre); each cluster holding >= 0.9 n candidate greens is
routed alone; the cluster routing with the lowest solver cost (re-ranker / tee steps off for the comparison) replaces
the whole-scene routing when its cost is lower than the whole scene's; the chosen scene is then routed with the normal
steps. route_scene.json records multi_site = dict(k, cluster, cost, cost_full). The 1.5 x n flag threshold was picked
looking at detection counts on both splits (choice and never-used: 1.4 / 1.5 / 1.7 / 2.0 / 2.5 x n catch 7 / 7 / 5 /
5 / 1 of the 8 truth sites with 7 / 5 / 3 / 2 / 0 single courses flagged); never-used outcomes are unchanged.

Bench (scratch t2/multi_run.py: route_bench.load_course monkeypatched to the cluster scene, route_learn fold models for
out-of-fold scores, re-ranker / tee steps off in every arm): 12 courses flagged on train+big (7 of the 8 truth sites +
whisper_rock, silver_lakes, buffalo_hill, rebsamen, trump_national); 2 switch: tb_robert_trent_jones_hampton_cove_al
1 -> 8 (k 2, cost -41.5 vs -36.3), tb_whisper_rock_az 14 -> 18 (k 2, -50.3 vs -44.9), both choice; the other 10 keep
the whole-scene routing (every cluster routing costlier), including both never-used courses (buffalo_hill 16, revere
18) and the single-course false positives. With the n = 9 rule and these two replaced in the default's out-of-fold
results: train+big 643 86.59 % / 230 -> **86.69 % / 231**, choice 443 86.23 % / 162 -> **86.38 % / 163** (card 6.0 /
35.8 yd), never-used 200 87.38 % / 68 unchanged. Not flagged: any test 28 course (test stays 89.23 %, not re-read),
any blind-20 course.

Under the bench's new card convention (ROUTE_BENCH_CARD=pick, commit 4ab2004b7; same runners, fresh prep): the same 2
courses switch with the same results (+11); hermitage's whole-scene routing is 11 / 18 under pick (0 under chosen) and
its clusters are costlier, so it is kept. n = 9 under pick: cedardell 8 -> 9, o_donnell 0 -> 7; nevada_mo's picked
card is already a 9-hole card (8 / 9 either way): +8.

Blind loop with both rules (t2/loop_multi.txt, default env, on top of 4ab2004b7) is identical to today's idle
baseline (t1/idle1.txt) line for line except timings; Hawk's Point approximate 12 of 18. Cost: the rule routes the
scene 1 + (number of clusters) + 1 times on a flagged course: route_v2 22-30 s -> 57-62 s on whisper_rock / RTJ
(+35-40 s), nothing elsewhere. The routing stage has no time limit or timeout path (the only wall-clock budget in the
fast path is the card search, fast.CARD_BUDGET_S), so a flagged course just takes longer.

End-to-end check of the n = 9 rule (scratch t2/e2e9.py: real fast.build with the OSM golf features dropped, the bench's
web cards seeded): tb_o_donnell_ca shown (P(all) 0.059, approximate 3, 8), 9 holes on raw/scene_card.json (nine_of
18), yardages / pars = the front nine (312 357 130 207 125 468 197 504 301; total 2601), measured within 1 yd except
hole 6 (400 vs 468, warned); qa/e2e.py ok (exit 0, no problems; book 10 pages, 9 aim sheets, wind page).
tb_cedardell_il shown (P(all) 0.502), 9 holes on the front nine. route_bench.load_course now applies route_n too
(fresh prepares; cached prep pickles keep n = 18).

## State 2026-11-20 (later): card-blind routing measured; no-card courses shown under auto (opt-in ROUTE_NOCARD_SHOW=1)

Question: Will's goal is to deliver every course, with the unsure holes marked approximate. What would delivering
the no-card courses look like? Today route_gate.decide hard-blocks a scene routing with no usable card yardages ("no
scorecard yardages"). That covers no web card at all, and since the card sanity change also a card dropped as broken.

Bench (ROUTE_BENCH_CARD=none: every card dropped on all 643 courses; base solver, route_learn state-fold models,
out-of-fold; re-ranker / tee step off because their picks were made with cards). Reference: the same pipeline with
cards (cardfix/all_agree.json; that run spanned 95d5c5500's route_n hook in load_course, so a few 9-hole-card courses
may mix):

| | choice 443 | never-used 200 | 643 |
|---|---|---|---|
| holes right, card-blind | **14.48 %** (all-right 16) | **15.00 %** (8) | **14.64 %** (24) |
| holes right, with cards (same pipeline) | 85.17 % (143) | 85.61 % (57) | 85.30 % (200) |
| card-blind: P(all) median / p90 / courses >= 0.5 | 0.000 / 0.008 / 0 | 0.000 / 0.009 / 0 | 0.000 / 0.008 / 0 |
| card-blind: per-hole P mean, share < 0.5 | 0.54, 57 % | 0.53, 57 % | 0.54, 57 % |
| shown under auto with ROUTE_NOCARD_SHOW=1 (complete routing) | 357 | 152 | 509 |

Card-blind, the router still finds the holes: 83.9 % of the true holes appear under some number (with cards 89.8 %).
It numbers only 14.6 % right (green under the right number 16.3 %). Without yardages the hole order is close to a
guess, and the 24 all-right courses are mostly 9-hole loops. The gate is not calibrated for this (fitted on carded
routings; card_rel is missing and defaults to 0.3). Its per-hole P reads 0.39 / 0.59 / 0.78 / 0.87 in the bins
< 0.5 / 0.5-0.7 / 0.7-0.85 / 0.85-0.95, where 14 / 14 / 16 / 23 % of holes are right. Hence the flag caps every hole
at 0.45, so all are approximate.

Real no-card courses: in the 651 train+big rows, 8 have no web card (outside the 643 card-only bench), plus the 5
whose only card is now dropped as broken (tb_hillcrest_sc, tb_lakeside_ut, tb_oshkosh_wi, tb_eagle_crest_ny,
tb_northern_michigan_university_mi). Blind loop: 3 of 20 have no card: Pheasant Ridge (tier A) and The Heights (tier C),
which route_gate.decide never sees, and Makena North (tier D), which fails before routing (no package). So the flag
changes nothing in the loop: tiers D 2, 4, 9, 13, 18 re-run with ROUTE_NOCARD_SHOW=1 are identical to the default
(cardfix/loop_nocard.txt).

Implemented as an opt-in only (default unchanged): `route_gate.nocard_show()` / ROUTE_NOCARD_SHOW=1. Under the auto
policy a routing with has_card False is no longer blocked for that reason. Every p_hole is capped at NOCARD_P 0.45
(all approximate), P(all) is the product, and the gate's warnings ("no scorecard yardages: shown with every hole
approximate") go into the package's auto warnings (fast.py). The other hard blocks stay: missing holes, a hole with
neither end, card-order conflict, shared green. The calibrated policy is unchanged. Test:
test_route_scene.test_gate_no_card_opt_in.

Reproduce (scratch cardfix/): run_blind.sh (all_none / all_agree), blind.py, loop_nocard.txt.

## State 2026-11-20 (later): per-vintage NAIP fallback for green-blind scenes (opt-in FASTSCENE_VINTAGE=1, not the default)

Cause E of the collapse diagnosis: scenes with almost no greens. Six courses on the bench have fewer scene greens
than 0.5 x n, or have less than half their true greens visible in the U-Net map: black_desert, hunter, woodlyn_hills,
great_southern, stoner_creek, and shady_hills (never-used). They hold 94 wrong holes.

Diagnosis:
* The fetcher (fast_imagery.list_years, Planetary Computer STAC) reaches every NAIP year with full coverage: 5 to 13
  vintages per course, 2010-2025. TRAIN-BIG scenes average the U-Net over the package year and the 2 newest other
  years.
* No opening or renovation year is available: OSM tags, golf_course boundaries and card sources carry none.
* What the imagery shows (2.4 m mosaics, scratch vint/sheet_<slug>.jpg):
  * black_desert: under construction on the newest Utah NAIP (2021; the course opened 2023). Not fixable with NAIP,
    and Sentinel-2 at 10 m cannot resolve greens.
  * hunter: no playable course on any of 2020-2023.
  * woodlyn and great_southern: greens on the 2017-2020 flights, brown or overgrown on 2021-2023.
  * stoner_creek: fairways bare in 2020 (a renovation flight).
  * shady_hills: a working course; the U-Net misses it on the 2022 flight.
* A 3-vintage mean can bury greens that one flight shows (0.9 / 0.1 / 0.1 averages to 0.37).

Rule (`fastscene.vintage_fallback`, called from `fastscene.build` when the U-Net probabilities are computed there,
i.e. in production):
* Trigger: scene hole greens < VINTAGE_MIN (0.5) x n, where n comes from `package_holes` (the request's card file,
  else the web card `scorecard.choose_card` picks, else 18).
* The U-Net runs on each NAIP vintage alone: the package's own plus up to 5 others, newest first (fetched into
  imagery/years/ and cached there). Each is perceived; the scene with the most hole greens wins, ties go to the newer
  flight, and the mean scene stays unless a vintage beats it.
* If no vintage less than 3 years older than the newest reaches 0.5 x n greens, the scene carries "possibly closed /
  imagery outdated: greens show only on NAIP <year> ...". fast.py adds it to the package's auto warnings. Nothing is
  blocked.
* Cost on a triggered course: about 20-50 s and 10-15 MB of NAIP (Hawk's Point 39 -> 89 s).

Bench evaluation:
* Packages for the triggered courses were rebuilt in scratch (OSM, card, NAIP latest + 2, 3DEP, Meta canopy) and
  deleted after. 19 bench courses trigger (scene hole greens < 0.5 x n, counted on the bench scenes). Black_desert is
  left out (unfixable); 4 of the other 18 do not trigger on the rebuilt mean scene.
* Each course was built twice from the same package: A = the mean, as production does by default; B = with the
  fallback. Each scene was routed with the base solver and route_learn state-fold models (out-of-fold), on
  production's card pick.
* Truth greens found by the scene, A -> B: stoner 3 -> 9 (of 9), woodlyn 3 -> 18, shady 4 -> 18,
  great_southern 2 -> 17, jones_creek 3 -> 18, grandote 6 -> 17, outdoor_resort 2 -> 10, hunter 0 -> 1.

Holes right, A -> B (default OOF in brackets):

| course | split | A -> B | vintage chosen | warning |
|---|---|---|---|---|
| great_southern_ms | ch | 5 -> 16 /17 (1) | 2020 | yes |
| tb_woodlyn_hills_ia | ch | 4 -> 12 /18 (0) | 2017 | yes |
| tb_blue_hill_me | ch | 2 -> 8 /9 (6) | 2023 | - |
| tb_jones_creek_ga | ch | 12 -> 16 /18 (18) | 2017 | - |
| tb_lakeview_springs_ky / tb_merriland_farm_me | ch | +1 / +1 | 2016 / 2021 | yes / - |
| tb_stoner_creek_ky / tb_hunter_il / tb_grandote_peaks_co (nu) | | 9 -> 9 / 0 -> 0 / 17 -> 17 | 2018 / 2021 / 2023 | - / yes / - |
| tb_outdoor_resort_palm_springs_ca | ch | 5 -> 0 /18 | 2016 | yes |
| tb_mount_kineo_me / tb_el_rio_fl / tb_riverbend_evunbreth_wv | ch | -2 / -2 / -1 | 2015 / 2023 / 2022 | yes / - / - |
| **tb_shady_hills_in** | **nu** | **4 -> 2 /18** | 2018 | - |

* Choice: +21 holes (6 courses better, 4 worse / -10).
* Never-used: -2 holes (shady_hills, the only never-used course where the scene changes). Its greens go from 4 to 18,
  but its card fits the true holes badly (16.9 %), and the numbering stays wrong either way (green under the right
  number 0.22 -> 0.11).
* The rebuilt mean scene (A) differs from the bench's stored scene (other package-year choice at TRAIN-BIG time), so
  the gains are measured A -> B on the same package, not against the bench's out-of-fold result.
* Fails the ship rule (never-used down), so it is opt-in. The rule was not tuned on these 18 courses further.

Warnings:
* Fired on hunter, woodlyn and great_southern (the three that look closed) but not on stoner or shady (open; a recent
  flight shows greens).
* Also fired on Hawk's Point, mount_kineo, lakeview_springs and outdoor_resort. I have not checked those against the
  imagery: on Hawk's Point the U-Net finds greens only on 2017, while the package's green_visibility check calls
  18/18 greens turf on NAIP 2023. So the warning can be a false alarm where the U-Net is weak on recent flights.

Blind loop:
* FASTSCENE_VINTAGE=0 (the default) is identical to the previous loop (cardfix/loop_on.txt) on all 20 courses.
* With FASTSCENE_VINTAGE=1 only Hawk's Point (tier D) changes: still shown, P(all) 0.000 -> 0.015, approximate holes
  12 -> 1, yardage misfits 3 -> 0, plus the outdated-imagery warning (2017 chosen; 2023 shows 8 of 18 greens).
* The extra years the fallback cached in the loop package do not change the default build (re-run of course 13 with
  the flag off: identical).
* Test 28 not read (nothing ships).

Does the 3-vintage mean hurt healthy courses?
* Only 19 validation choice courses still have per-vintage U-Net probabilities on disk (cache/heldout/probs: d0 + 2
  y<year>.npz). TRAIN-BIG kept only the mean. That is short of the 40 asked; nothing was refetched.
* On those 19 (322 true greens):

| U-Net probabilities | P-visible greens | scene greens found | false scene greens |
|---|---|---|---|
| mean (production) | 321 | 303 | 39 |
| per-pixel max | 322 | 303 | 50 |
| mean without the dormant vintage (lowest turf P) | 321 | 301 | 40 |

* The mean does not bury greens on healthy courses. Max adds false greens. Dropping the dormant vintage changes
  nothing.

Reproduce (scratch vint/): rebuild.py SLUG... (package -> vroot_A / vroot_B + vint_<slug>.json; deletes the package),
route.sh ROOT OUT SLUGS, widen.py, sheet_*.jpg, loop_voff.txt / loop_von.txt.

## State 2026-11-20 (later): per-vintage fallback ON by default (coordinator override); "possibly closed" warning tightened

Override of the ship rule, recorded at the coordinator's decision. FASTSCENE_VINTAGE now defaults to on (rollback
FASTSCENE_VINTAGE=0) although never-used loses 2 holes. The reasons given:
* Never-used has a single affected course (tb_shady_hills_in), and its scene clearly improves (truth greens found
  4 -> 18). The hole loss comes from its card, which fits the true holes badly (16.9 %), not from the fallback. This
  is the small-sample exception already applied to the other agent's work.
* Choice gains +21 holes.
* The blind loop's worst tier D course, Hawk's Point, goes from 12 approximate holes to 1.

Warning tightened. The "possibly closed / imagery outdated" warning now also needs the recent flights (less than 3
years older than the newest tried) to show no maintained turf at the chosen scene's hole greens (`fastscene.green_cues`).
Either of these is enough:
* the U-Net turf P(green + fairway + tee) within 8 m of the greens stays below CLOSED_TURF 0.75 on every recent
  flight;
* the NIR roughness of the green (std / mean within 6 m) over that of its 15-30 m ring stays above CLOSED_ROUGH 0.25
  on every recent flight (maintained greens are smooth).

The package's own green_visibility check was not used: it compares each green's NDVI with the course's other greens,
so a course that is overgrown everywhere still passes it.

Calibrated on 7 courses checked by eye on the NAIP mosaics (scratch vint/sheet_*.jpg; a small sample, read as such):

| course | looks | recent turf max | rough ratio min | warning |
|---|---|---|---|---|
| tb_hunter_il | closed | 0.677 | 0.05 | yes |
| tb_woodlyn_hills_ia | closed | 0.718 | 0.34 | yes |
| great_southern_ms | closed | 0.352 | 0.23 | yes |
| Hawk's Point (loop) | open | 0.801 | 0.09 | no (was yes) |
| tb_mount_kineo_me | open (mowing patterns in 2021) | 0.781 | 0.12 | no (was yes) |
| tb_lakeview_springs_ky | open (greens visible in 2022) | 0.908 | 0.08 | no (was yes) |
| tb_outdoor_resort_palm_springs_ca | open (lush in 2022) | 0.858 | 0.01 | no (was yes) |

Stoner and shady never reach the warning: a recent flight shows enough greens.

Blind loop with the default on (scratch vint/loop_def.txt vs vint/loop_voff.txt): 19 of 20 courses are identical. The
one change is Hawk's Point (tier D): still shown, P(all) 0.000 -> 0.015, approximate holes 12 -> 1, yardage misfits
3 -> 0, and no warning now.

Test 28 (read once):
* Only jato_highlands_me triggers: 0 hole greens. It was already a "prepare failed" error in the test bench.
* Rebuilt from its heldout package, no vintage shows any green (2023 / 2021 / 2018 / 2015: 0 each), so the mean
  scene stays.
* The other 27 test scenes do not trigger, so the test is unchanged: 89.23 % / 11 (431 / 483 holes).

Bench caveats:
* The cached bench scenes (validation and TRAIN-BIG) were built with precomputed U-Net probabilities. The fallback
  only runs when fastscene.build computes P itself (production), so the bench's stored scenes and numbers do not move.
  The effect was measured on scratch-rebuilt packages (previous section: choice +21, never-used -2 holes).
* Cache key: fastscene.py is one of route_bench.DET_PATHS, so commits to it change detector_version(). Bench runs
  that omit --ver look for scenes under cache/val/scenes/<new hash>_<probs>/ and rebuild them (perceive only, with
  cached probabilities, so no fallback). Runs that pass `--ver v2seg_d0+yall`, as every routing experiment in these
  notes does, read the same cached scenes as before and stay comparable.

Reproduce (scratch vint/): cues.py (per-vintage green cues; packages rebuilt and deleted), loop_def.txt,
rebuild_jato.log.

## State 2026-11-20 (later): routing fits refitted under the bench's card pick (default; ROUTE_SELECT=chosen rollback)

The bench now routes production's card pick (ROUTE_BENCH_CARD=pick, 4ab2004b7); the route_models/v2 fits were made with
scorecard.json's chosen card, which differs in content on 186 of the 643 courses (source on 52), so their out-of-fold
re-ranker / tee picks do not apply there.

Hybrid pick baseline (HEAD 95d5c5500 defaults, scratch t2/pickbase.sh): every course rescored with the route_learn
state-fold models (ROUTE_BENCH_FOLD_RESCORE), the old out-of-fold re-ranker / tee picks on the 457 courses whose card is
unchanged, none on the other 186 (so those run without the re-ranker and tee step: the baseline is pessimistic there).
Holes right / all-right, card median / p90 yd: train+big 643 86.43 % / 223, 6.0 / 33.9; choice 443 86.08 % / 158,
5.9 / 33.2; never-used 200 87.20 % / 65, 6.2 / 35.6. (Neither this bench path nor the refit's includes the
27 / 36-hole cluster routing, which runs in route_v2 only; its 2 switched courses are not in these numbers.)

Refit (scratch t4/run_pick.sh: the shipped recipe unchanged under ROUTE_BENCH_CARD=pick, --ver v2seg_d0+yall: route_learn
h / w / s / e + x3 cv / fit, gen3 rows + bagged ranker thr 0.5 (out-of-fold gain choice +67 / never-used +67, vs +49 /
+33 for the old fits), tgen2 rows + hybrid tee rule 0.93 / 12 / 0.5 (tl_exp reading the bench's card), gate refitted):

| | train+big 643 | choice 443 | never-used 200 |
|---|---|---|---|
| hybrid pick baseline | 86.43 % / 223, 6.0 / 33.9 | 86.08 % / 158, 5.9 / 33.2 | 87.20 % / 65, 6.2 / 35.6 |
| **refit under pick** | **87.04 % / 233**, 6.1 / 36.3 | **86.70 % / 166**, 6.1 / 36.3 | **87.80 % / 67**, 6.2 / 36.4 |

Per course: choice 80 better (+159) / 67 worse (-113), never-used 31 (+59) / 26 (-39). Card on choice +0.2 / +3.1 yd
(within the +1 / +5 guardrail; vs the old default's 6.1 / 36.2 flat). Part of the gain is the 186 courses getting the
re-ranker / tee step back (the baseline caveat above); the other agent's delta composite for the pick convention was
86.83 / 86.42 / 87.74 %, which the refit also beats.

Test 28 (read once, production path with the new fits, teerec/testeval.sh): 89.23 % -> **88.20 %** (431 -> 426 of 483),
a regression: smoke_rise_ga 16 -> 9 (the old re-ranker switched to a beam alternative changing holes 10 / 11, the new one
does not switch; 7 of the 9 holes lost), bartram_trail -1; arrowhead_pointe, elmcrest, towne_lake_hills +1
(jato_highlands_me has no x3 table on test, as before). Never-used + test pooled: +20 - 5 = +15 holes.

Blind loop with the new defaults (t4/loop_refit.txt vs t1/idle1.txt): tier A / B / C identical (statuses, picks,
flagged picks, approximate). Tier D all still shown; picks move with the new routing: Sunset P(all) 0.359 -> 0.449,
Glenwild 0.265 -> 0.261, Remsen 0.531 -> 0.569, **Hawk's Point approximate 12 -> 1 of 18 (hole 15; P(all) 0.000 ->
0.012)**; Makena North no build. Nothing goes from shown to blocked.

Shipped: route_models/v2 = the refit; the previous fits are route_models/v2_chosen (ROUTE_SELECT=chosen). The
ROUTE_SELECT=0 / w1e rollbacks (v2_pk, v2_w1e) now carry their own copy of the previous route_learn fit, so they load
exactly the fit sets they were made with.

## State 2026-11-20 (later): numbering / green-choice diagnosis, per-hole combination, re-ranker misses (nothing shipped)

Numbering on healthy courses (> 60 % of holes right, not all; old default out-of-fold, scratch t2/ndiag.py): choice 235
courses / 470 wrong holes, never-used 117 / 262. Oracles on the routed lines: best single swap of two lines +50 / +41,
best contiguous segment shift or reversal +27 / +19, optimal renumbering of all lines +67 / +55: only ~14 % of the
wrong holes are a routed line that matches another truth hole (offsets +2: 14, +-9 nine swaps: 17, -1: 8, +1: 5; 35
of 97 green-on-another-hole pairs touch hole 9 / 10). 'Right green present and unused' (choice 128, 82 on healthy
courses): the chosen green is a median 209 m from the true one, only 29 have the right tee, 11 the wrong green within
60 m (never-used 35 healthy / 13 right tee): whole-hole errors inside a disrupted stretch, not green swaps.

Per-hole combination across the re-ranker's alternatives (scratch t4/combo.py / combo2.py on the pick-refit gen rows,
out-of-fold bagged ranker scores, route_struct hole labels; choice 7164 holes): seq0 87.74 / never-used 88.03 %, shipped
whole-routing pick 88.68 / 90.08 %, oracle whole routing 92.36 / 92.67 %, oracle per hole (no consistency) 95.70 /
95.97 %. Vote per hole weighted by exp(score / T): T 0.5 without repair 88.87 / 90.20 % but adds duplicated greens
(6 / 2 routings; a hard 'share a green' block in production); a strict no-shared-end repair loses (87.7-87.9 %: the
solver itself shares tees, seq0 has 113 duplicate ends); a green-only repair (fall back to the whole pick's option where
the vote creates a duplicated green) 88.82 / 90.17 % (choice 11 better / 6 worse courses): about +10 / +3 holes. Not
shipped (too small for the plumbing).

Re-ranker misses (oracle whole routing > pick, choice, pick-refit rows): 103 of 431 courses, 264 holes; 63 courses miss
by 1 hole and 18 by 2 (near-ties among ~247 alternatives, the oracle's score rank median 7); oracle kind beam 40, start
28, seq0 13, renum 11, end 11; 54 of the missed courses stay on seq0. Never-used: 49 of 197, 85 holes. Courses with a
>= 4-hole gap (scratch t4/bigmiss.py): 7 are renumberings whose oracle fits the card worse (lincolnshire_fields, pb_dye,
valley_co 0 -> 18, belgrade_lakes 9 -> 18, woods_fort 8 -> 17, woodlyn_hills, outdoor_resort): the card disagrees with
OSM (nine swap / misnumbered card), unwinnable by routing features (card nine-order is the card side's work); the
other ~18 are start / beam / end alternatives the ranker scores ~15th, with mixed feature differences (start-loop
score, walk-back, reuse, ends, virtual counts) and no single separating signal. Most of the suggested per-routing
features (weakest hole score / count below 0.5, par-band misses, walk sums, crossings, clubhouse at the ends) are in
FEATS2 already.

Objective / label variants (single LightGBM ranker, out-of-fold, holes gained choice / never-used at thr 0.5; scratch
t4/rr_v.py): linear gain trunc 3 (shipped settings) +63 / +64; exponential gain +33 / +61; truncation 10 +63 / +55;
truncation 30 +68 / +62; rank_xendcg +46 / +34; label + 5 x all-right +69 / +51; exponential + trunc 10 +26 / +35. The
shipped bagged ranker gives +67 / +67. None is better on both splits: not pursued.

## State 2026-11-20 (later): re-ranker FEATS3 and walk features wx4 (both gated, not the default)

All on the pick-refit baseline (route_models/v2 since 3906f8c15; out-of-fold 643 87.04 % / 233, choice 86.70 % / 166,
never-used 87.80 % / 67, card 6.1 / 36.3 yd).

FEATS3 (route_rerank.FEATS3, model key feats3; per routing: mean hole-model score and holes under 0.7, holes whose tee
complex another hole also uses (whole or split half), greens used twice, virtual ends): gen rows + bagged ranker on the
pick refit's route_learn (scratch t4/run_f3.sh). Re-ranker out-of-fold gain at thr 0.5 +67 / +67 -> +75 / +71; bench
643 87.18 % / 228 (+14 holes), choice 86.91 % / 163 (36 better / 27 worse, +15), never-used 87.77 % / 65 (14 / 17,
-1), card 6.1 / 36.2. Never-used not better: not shipped.

Walk model diagnosis (scratch t4/walks.py, wcal.py; all 643 courses, OSM truth): true green -> next tee walks median
75 yd, p90 161, p99 302 (12.3 % > 150 yd, 2.3 % > 250); the next tee is the green's nearest tee in 73.5 %, second
19.4 %, third or later 7 %; the re-ranker's walk_back rule fires on 0.5 % of true walks. route_learn's walk and hole
models are calibrated (by length bin and by probability decile: walk 0-50 yd rate 0.40 / mean pw 0.41, 100-150 0.22 /
0.22, 200-300 0.028 / 0.029; hole deciles 0.94 -> 0.95); the walk model's weakness is discrimination at short range
(50-100 yd: true walks mean pw 0.54 vs false 0.34; out-of-fold AUC 0.9685, 0.8434 on pairs <= 200 yd). On the 13
choice courses where the oracle routing beats the pick by >= 4 holes (renumberings excluded) the oracle's solver cost is
higher mainly in the walk term (median +1.42, higher on 85 %; total walk +80 yd), not in the hole / card terms; on 1-2
hole near-ties the difference is spread over card / walk (noise); virtual-end counts barely differ. The suggested scene
walk cues are mostly in walk_features3 already (wx_cos_out: walk vs the tee's outgoing hole, wx_ahead_tr: trees in
the next corridor, wx_rk_t / wx_rk_g: distance ranks both ways); the U-Net has no path class and the fast-path scenes
carry no cart paths (0 of 200 checked); OSM paths were not used (biased; skipped).

wx4 (route_learn.walk_features3 extra columns, tables ROUTE_LEARN_WX4=1, model key wx4: tee-complex axis vs the walk
and vs its best outgoing hole, the pair's distance over the green's nearest tee / the tee's nearest green), full
refit under pick (scratch t4/run_wx4.sh): walk AUC 0.9685 -> 0.9700 (short pairs 0.8434 -> 0.8451); re-ranker gain
+58 / +18; bench 643 87.08 % / 231 (+4), choice 87.01 % / 162 (59 better / 50 worse, +23), never-used 87.23 % / 69
(29 / 26, -19), card 6.2 / 36.8. W1 + FEATS3 (t4/run_w1f3.sh): re-ranker +69 / +18; 643 87.14 % / 234 (+10), choice
87.11 % / 163 (+30), never-used 87.20 % / 71 (28 better / 29 worse, -20), card 6.1 / 36.7. Both fail never-used: not
shipped. Both stay in the code gated by their model keys (no effect on route_models/v2); blind loop with the gated code
(t4/loop_gated.txt) identical to the shipped default's (t4/loop_refit.txt).

## Design 2026-11-20: routing bench and refit on GitHub Actions (not built yet)

Why: the local machine (4 cores, about 1.9 GB of free disk, shared by several agents) limits every routing
experiment. A full refit needs about 1.5 GB of scratch and about 2 h wall.

### How the inputs were built (all local, none on Actions)

TRAIN-BIG (600 courses, route_big.py; rebuilt for the v2 U-Net by scratch segv2/rebuild_big.py), per course:
* `fetch_stage`: OSM via osm_api, then card search (fetch_package.fetch_scorecards), then NAIP (latest year + the 2
  newest others), 3DEP DEM and Meta canopy.
* `perceive_stage`: fastscene.build, then cache/big/{scenes/<slug>.json.gz, probs/<slug>/d0+yall.npz (P(green) and
  P(tee) only), maps/<slug>.npz (corridor maps from the full 6-class P + CHM)}.
* The package is deleted after; courses/<slug>/ keeps osm_golf.geojson.gz, course.json and scorecard.json.

Validation (82 courses = 51 train + 31 test):
* heldout.py fetch builds the packages in cache/heldout/<slug> (the NAIP / DEM imagery has since been deleted locally;
  raw/ and canopy/ remain).
* perc_bench.py probs gives cache/heldout/probs/<slug>/{d0, y<year>}.npz (6-class uint8).
* route_bench.py scenes builds cache/val/scenes/v2seg_d0+yall/<slug>.json, and route_learn.bench_maps writes
  cache/val/maps/....

No workflow builds these. golfseg_v2_train.yml builds U-Net training data (NAIP + OSM labels), not bench scenes;
routing_v2_eval.yml routes the old committed generalize cache.

### What a bench shard needs, and where it lives

| input | size | in git? |
|---|---|---|
| route code (route_*.py, fastscene.py, zero_tap/joint ...) | small | yes |
| route_models/<v>/ fits | about 40 MB | yes |
| U-Net weights (segment/models/golfseg_own_v2/model.safetensors) | - | yes |
| validation truth + cards (generalize/courses/<slug>/osm_golf.geojson, scorecard.json; 679 files) | 49 MB | yes |
| TRAIN-BIG truth + cards (cache/big/courses/<slug>/{osm_golf.geojson.gz, course.json, scorecard.json}) | 58 MB | **no** (local only) |
| TRAIN-BIG scenes / probs / maps (cache/v2root/big) | 49 + 201 + 808 MB | no |
| validation scenes / maps / probs (cache/v2root/val/scenes, val/maps, heldout/probs) | 33 + 108 + 156 MB | no |
| heldout raw/ + canopy/ (validation maps use the CHM) | about 15 MB | no |
| out-of-fold state folds, learn tables, the refit's own scripts (scratch rsel/gen3.py, gen.py, rr_fit.py, tgen2.py, tl_exp.py, tl_fit.py, foldfit.py, segv2/summ3.py) | - | **no** (scratch only) |

* **Refetchable:** NAIP / DEM / canopy (Planetary Computer, 3DEP, Meta: free, about 15 MB a course).
* **Not refetchable reproducibly:** OSM truth and the web cards. OSM has been edited since 2026-11-17, the card sites
  change, and TRAIN-BIG's `chosen` card was made on the OSM ground (see "card sanity"). So the 58 MB of
  cache/big/courses must be frozen: commit them, e.g. under course_data/platform/fastpath/bench_data/big_courses/,
  rather than refetch.
* Library versions must match the pickled fits: scikit-learn 1.9.1, lightgbm 4.7.0, numpy 2.4.x, scipy 1.17,
  opencv 5.0, rasterio 1.4.4, pyproj 3.7.2, shapely 2.2. The U-Net runs through fastc / numpy, with no torch locally.
  The workflow pins these.

### Workflow shape (one file, routing_bench.yml; request-file trigger as golfseg_v2_train.yml)

Request file: course_data/requests/routing_bench_<name>.json, e.g.
`{"schema": "request/1", "kind": "routing_bench", "stage": "inputs" | "bench" | "refit", "inputs_run_id": "",
"slugs": [] (empty = all 643 + test 31), "nshards": 20, "env": {...}, "models": "route_models/v2", "commit_models": ""}`.

Stage `inputs` (once per detector / U-Net change):
* A plan job writes the slug list, a matrix of 20 shards.
* Each shard job checks out the repo (sparse: code + models + bench_data), pip-installs the pinned versions, then per
  course:
  * TRAIN-BIG: route_big.fetch_stage minus the card search (truth and card from bench_data), then perceive_stage.
  * validation: heldout.py fetch, then perc_bench.py probs d0 + years, then route_bench scenes.
* It uploads artifact `bench-inputs-<k>`: the cache/v2root layout restricted to the shard's courses; packages are
  deleted per course.
* Size about 1.7 MB a course (scene 80 KB, probs 330 KB, maps 1.3 MB), so about 1.2 GB in total, about 60 MB a shard.
* Wall: about 2.5 min a course (3 NAIP years plus the U-Net on a 4-vCPU runner), about 34 courses a shard, about
  85 min a shard, 20 in parallel.
* Artifacts expire (90 days at most; golfseg uses 30). The request names `inputs_run_id`, as golfseg's `data_run_id`;
  re-run `inputs` when it expires. Alternative that does not expire: a merge job tars the shards into a GitHub
  release asset (under 2 GB; GITHUB_TOKEN with contents: write).

Stage `bench` (an out-of-fold bench of the current models, or of `models`):
* Each of 8 shards downloads `bench-inputs-*` (actions/download-artifact with run-id), merges them into
  FASTPATH_CACHE, and runs `route_bench.py eval --scene fast --router v2 --card-only --prep --ver v2seg_d0+yall
  --split train+big --slugs <shard>`. Out-of-fold picks / scores come from the request's `oof_run_id` (artifacts of a
  refit), or production models when absent.
* A merge job runs summ3 / cerr (holes right, all-right, card error and hole_acc_fwd per split: 643 / choice 443 /
  never-used 200) into the run summary and a results artifact.
* Wall: 643 courses x about 2.5 s with prep plus about 3 s prepare is about 1 h of CPU, so about 8 min per 8-way shard
  plus about 3 min of artifact download.

Stage `refit` (the shipped recipe, scratch dpad/run.sh mapped onto jobs):

| local step | job | parallel | wall (est.) | output artifact |
|---|---|---|---|---|
| prep: route_bench eval --prep, ROUTE_RERANK=0 ROUTE_TEE=0 | prep-k | 8 shards (--slugs) | 10 min | prep pickles (about 340 MB in all) |
| route_learn table / x3 | tables | 1 (or 8 if table gets --slugs; it reads the prep) | 25 min | learn tables |
| route_learn cv + fit (state folds), foldfit.py | learn | 1 | 15 min | sc/cv, route_learn_model.pkl, folds |
| gen3.py re-ranker rows (already takes a slug-file argument) | gen-k | 8 | 15 min | gen3 rows |
| rr_fit.py (bagged ranker, thr 0.5) | rerank | 1 | 10 min | route_rerank_model.pkl, picks_tb.json |
| tgen2.py tee rows | tgen-k | 8 (needs a slug-file argument like gen3) | 10 min | tee rows |
| tl_exp.py + tl_fit.py (hybrid rule 0.93 / 12 / 0.5) | tee | 1 | 10 min | route_tee_model.pkl, tee_picks.json |
| out-of-fold bench (ROUTE_RERANK=0 ROUTE_TEE=0 with picks, ROUTE_BENCH_SC) | oof-k | 8 | 10 min | per-shard oof json |
| merge + route_gate fit + summary | gate | 1 | 5 min | route_models/<name>/ (4 files), oof.json, summary |

* End to end about 1 h 50 min of jobs, about 1 h 15 min wall with the 8-way shards; nothing on the local disk.
* Optional `commit_models: "route_models/<name>"`: the gate job commits the 4 fits (contents: write).
* Test 28 stays a separate stage (`test`) that must be requested explicitly, never part of a refit, to keep its
  read-once rule.

### Work needed before the first run (not done in this session)
1. Commit cache/big/courses (58 MB) as frozen bench data.
2. Move the refit scripts from scratch into the repo (a new course_data/platform/fastpath/refit/ dir, one per step),
   with a --slugs file argument where missing (tgen2, the route_learn table step through a wrapper).
3. Write the workflow and test `inputs` on 5 courses, then `bench` on those 5 against local numbers. The pass
   criterion is identical hole_ok to the local OOF on the same courses: same inputs, same pins. A mismatch would most
   likely come from the U-Net or LightGBM threads; set num_threads and deterministic mode.
4. Run `inputs` on all courses. Then compare the Actions-built scenes with the local ones on a sample. The NAIP
   "latest" year can move when a newer flight is published, so the Actions scenes are a new detector version for the
   bench: record the year per course.

## State 2026-11-20 (later): review fixes to the card choice and the per-vintage fallback

A code review confirmed five bugs in the card-sanity and per-vintage commits. Repros are in scratch review/r1.py and
r3.py. Each fix has a regression test.

1. **scorecard.source_vote raised KeyError 'same'.** nine_order 'same' is not transitive (A lists Blue, B Blue + White,
   C White: A~B and B~C, but not A~C), so the top-supported card could be 'same' as the pick and miss the lookup. The
   whole package build would die, because choose_card is called unguarded from pick_scorecard.
   * Fix: the lookup handles every relation.
   * When the majority's best card is the pick itself, nothing changes and no note is written.
   * choose_card wraps source_vote and keeps the reliability pick when the vote fails.
   * Test: test_source_vote_non_transitive_same_does_not_crash (3 source orders).
2. **A failure in the vintage fallback or its cues took down the scene build.**
   * Fix: build() wraps vintage_fallback; on a failure the mean scene stays and seconds.vintage_err records why.
   * The cue / warning block (_outdated_warning) is guarded separately, so the chosen vintage survives a cue failure
     (fastscene_vintage.cue_err).
3. **The "possibly closed" warning could fire wrongly.** It could fire with the newest flight chosen. It treated a
   missing cue as dead turf (turf 0.0). It could print "NAIP 0" for an unknown year.
   * Fix: it now needs a known year, newest - chosen >= OUTDATED_YEARS, and the chosen vintage to reach
     VINTAGE_MIN x n greens.
   * A cue that could not be measured is no evidence of dead turf.
   * Effect: Hunter IL no longer warns. Its best vintage, 2021, shows 1 hole green and is 2 years from the newest; it
     no longer even replaces the mean scene (fix 5). Woodlyn (2017) and great_southern (2020) still warn; Hawk's Point
     still does not.
4. **scorecard.sanity divided by the longest row, par row included.** A complete 9-hole set under an 18-long par row
   scored 50 % and was dropped; 18-hole sets under a 27-long par row scored 67 %.
   * Fix: fill is computed per tee set against that set's own length. Non-dict sets, None yards and string yardages
     are also handled (string yardages count; `_rows` converts them).
   * Test: test_sanity_fill_per_set_length.
5. **package_holes ignored nine-repeating cards, and the winner was uncapped.** It returned 18 for a 9-hole course
   whose 18-hole card repeats its nine, so the fallback fired on one missed green. The winner was the vintage with the
   most "hole" greens, with no cap at n.
   * Fix: package_holes(pkg_dir, scene) applies route_scene.route_n on the mean scene (nine-dup test plus the
     <= 12-greens rule; route_scene.py not edited).
   * Vintages compare on min(greens, n), so a newer flight that reaches n wins over an older one with extra blobs.
   * The winner must beat the mean scene by `vintage_margin(n)` = max(2, round(0.15 n)): 2 greens on 9 holes, 3 on 18.
     The bench wins were +4 to +15 greens; Hunter's 0 -> 1 is the kind of flight-to-flight noise the margin keeps out.
   * On the 18 bench courses the margin changes only Hunter's choice (holes 0 either way). Every other course keeps
     its earlier vintage, so the bench numbers of the default section stand.
   * Tests: test_vintage_fallback_review_cases (newest wins without a warning, the margin, an old winner warns, a cue
     failure keeps the vintage, missing cues, an unknown year, the cap at n) and test_package_holes_nine_dup.

Reach of fixes 1 and 4 on real data: on the bench's web cards (train+big 651 rows; old vs fixed scorecard.py) no
choose_card call raised, no card's sanity verdict changed, and no course's pick changed. Both bugs are latent on
today's data and guard future cards.

Blind loop after the review fixes (defaults; scratch vint/loop_fix.txt):
* Hawk's Point still falls back to NAIP 2017 with no warning (recent turf 0.801, not dead): shown, approximate holes
  only 15, P(all) 0.012.
* Compared with the loop before the fixes (vint/loop_def.txt, 06:52), tier D courses 2, 4, 13 and 18 differ in
  p_holes / picks / pad counts. That comes from the routing refit committed since (3906f8c15: fits under the bench's
  production card pick; 99ebbee2f), not from these fixes.
* Courses 2, 4 and 18 re-run with FASTSCENE_VINTAGE=0 on the same code are identical to the default line for line
  (vint/loop_fix_off.txt), and only Hawk's Point changes with the fallback.

## State 2026-11-20 (later): review fixes to multi-site routing, the nine-hole rule and test isolation

A code review of the 27/36-hole cluster routing (95d5c5500) and the nine-hole rule (f16e7a026) found five problems.
Each fix has a regression test in test_route_scene.py or test_fastpath.py.

1. **_multi_site: the final routing on the chosen cluster ran outside the try.** A failure in the re-ranker / tee step
   on the cluster scene took down route_v2.
   * Fix: that call and the multi_site record are inside the try; on any failure the whole-scene routing stands.
   * Test: test_multi_site_final_routing_failure_keeps_the_whole_scene_routing (two synthetic 9-hole courses 2.5 km
     apart; the final cluster call raises).
2. **route_bench never ran _multi_site,** so the production default was not covered by the bench.
   * Fix: route_bench._bench_multi_site runs after RS.route on courses with >= MULTI_GREENS x n raw candidate greens
     (ROUTE_MULTI_SITE=0 turns it off). It calls route_v2 with the production fits, so a switched course is scored
     with those fits, not with out-of-fold picks.
   * Bench, defaults, pick card, re-ranked final routing (holes right / 18, multi_site off -> on):
     tb_robert_trent_jones_hampton_cove_al 0 -> 4 (k 2, cost -1.21 vs 0.74; card set White -> Teal),
     tb_whisper_rock_az 14 -> 17 (k 2, cost -0.05 vs 6.06). The earlier solver-only numbers were 1 -> 8 and 14 -> 18.
     Both are choice courses. Routing time on the two: 52 / 82 s -> 87 / 137 s on the bench (route + route_v2 again).
   * Test: test_bench_multi_site_off_and_without_a_card.
3. **cluster_scenes raised KeyError on a green or tee complex without "centroid".**
   * Fix: .get, and the object is left out of every cluster.
   * Not fixed, noted in the code: OSM greens and tees in fc stay in every cluster scene and are not counted by the
     trigger (it counts scene candidate greens only).
   * Test: test_cluster_scenes_skips_objects_without_a_centroid.
4. **Nine-hole rule.**
   * front_nine kept the 18-hole rating, slope and par_total. It now drops rating / slope / course_rating /
     slope_rating / bogey_rating per set (no nine-hole value can be derived) and recomputes par_total from the set's
     or the card's 9-hole par row. Test: test_front_nine_drops_the_18_hole_aggregates.
   * nine_dup raised on string yardages, a None set or NaN yardages; such sets are now skipped (no evidence).
     Test: test_nine_dup_ignores_malformed_sets.
   * fast.py wrote raw/scene_card.json even when the routing produced no holes. It now writes it only when holes were
     routed.
   * The comment said the caller repeats holes as 10-18; nothing does. It now says the course is delivered as a
     9-hole course on the front-nine card.
   * The bench applied route_n with the 18-hole card. It now routes front_nine(card), as production does for web
     cards (bench cards are web cards).
5. **Test isolation.** test_fastpath.py did `import solve`, which registered fastpath/solve.py as sys.modules["solve"]
   and shadowed zero_tap/joint/solve.py for test_route_scene.py in the same process. CI hit it (run 44803923250:
   AttributeError: module 'solve' has no attribute 'raster_lie_at').
   * Fix: test_fastpath.py and test_solve_c.py load fastpath/solve.py by path as "fastpath_solve" (solve_c looks it
     up by that name).
   * Test: test_fastpath_solve_does_not_shadow_the_joint_solver. The three files pass together in either order (25).
   * Full `pytest course_data/platform`: 319 passed, 1 failed. The failure is
     test_package.py::test_black_package_uses_the_joint_tee_stage, which CI already fails and which is outside these
     files.

Blind loop after the fixes (scratch t5/loop_rev.txt) vs the loop after the card / vintage review fixes
(vint/loop_fix.txt): identical line for line except timings, on all 20 courses. Hawk's Point: shown, 1 approximate
hole (hole 15).

## State 2026-11-20 (later): routing bench smoke on GitHub Actions (routing_bench.yml) passes

The workflow is .github/workflows/routing_bench.yml. It fires only on course_data/requests/routing_bench_*.json, and its
concurrency group is routing-bench-smoke-<ref> (golfseg_v2_train's is golfseg-v2-train-rev2). The smoke uses 5
TRAIN-BIG courses (benchdata/smoke/slugs.txt: abenakee, rattlewood, costa_del_sol, broad_run, valley), with
refit/requirements.txt on Python 3.11.18.

* Run 44808833923 (attempt 1): bench out-of-fold protocol PASS. Its informational bench on rebuilt scenes used the
  out-of-fold picks, which index the committed scenes' candidates, so 2 courses raised IndexError. Hence attempt 2,
  which adds a scene-independent protocol.
* **Run 44810603606 (attempt 2): PASS.** On the committed inputs (benchdata/smoke/big, copies of the local bench
  cache), the per-hole results and routed lines are identical to the local references on all 5 courses, under both
  protocols:
  * out-of-fold (picks + ROUTE_BENCH_SC; matches the local w2_0.5 OOF per hole);
  * fold-model (ROUTE_BENCH_FOLD_RESCORE with benchdata/smoke/folds, re-ranker + tee step live).

  The local references were made on a clean export of HEAD's code (other agents' uncommitted edits excluded).
* **Inputs rebuilt on Actions** (refit/build_inputs.py: NAIP + 3DEP + canopy + U-Net + fastscene, about 1 min a
  course):
  * Scenes: 4 of 5 match the committed ones green for green (hole greens matched 9/9, 19/19, 19/19, 22/22; tee
    complexes equal, one 25 vs 26).
  * costa_del_sol differs: the package year moved (U-Net years [2022, 2023] then, [2019, 2022] now), giving 9 hole
    greens vs 6.
  * Routing on the rebuilt inputs (fold protocol), holes vs local: 9 / 16 / 18 the same; costa 17 -> 16; valley
    13 -> 0. Valley is the nine-swapped-card course that flips on small score changes.
  * Routed lines differ on every course, even where the greens match: the probabilities differ slightly (local U-Net
    path vs the runner's C fp32 path), so tee spots move.
  * So a bench on Actions-rebuilt inputs is a new input version, not the local bench. For like-for-like numbers, either
    ship the local caches (as benchdata/smoke does for 5 courses) or rebuild all 643 courses on Actions and treat that
    as the new baseline.
* Wall: checkout about 2.5-3.5 min (full repo); pip about 25 s; bench of 5 courses 8-30 s; rebuild about 5 min for 5
  courses.

## State 2026-11-20 (later): conditional DEM pads measured fully out of fold (opt-in ROUTE_PADS_COND=1, not shipped)

Rule: DEM pad tee complexes are added only on a tee-blind scene, one with fewer than 0.75 x n raw scene tee complexes
(counted before P(tee) peaks, which fill every scene to 2 n). The production fits are kept (no refit). This fires on 57
train+big courses: 40 choice, 17 never-used. Code: route_learn.tee_pads_cond (augment_scene) and the DEM hook in
route_scene.run. Off by default. The pad classifier must be given with ROUTE_PAD_MODEL (route_models/v2_pads); without
it, pads degrade to none.

The ship rule for this run was relaxed by the coordinator: never-used net positive with more courses better than worse
(a one-hole loss on one course is inside the refit noise measured earlier), plus OOF 643 up, the blind loop explained
and the card guardrail.

**The sprint's gain was mostly leakage.** The sprint measured choice +46 / never-used +6 solver-only. Two things in it
were in-sample:
* Pad scores came from the production pad classifier, which was trained on these same courses. Out-of-fold pad scores
  were rebuilt from scratch pads/padfit_oof.pkl (state folds; course order = pads/slugs_tb.txt minus one of the last
  six slugs, checked by index bounds on all 57 courses and rank correlation 0.83 with the in-sample scores).
* The route_learn fold models were made with the chosen card. New pick-card fold models (refit/foldfit.py on pick
  tables): scratch t5/folds_pick.

**Protocol (fully out of fold, all on the 57 courses):**
* Identity check, which passes exactly: with t5/folds_pick plus the shipped out-of-fold re-ranker / tee picks
  (t4/P/picks_tb.json, tee_picks.json), the off arm reproduces t4/P/oof.json (choice 368, never-used 139 holes right).
* Re-ranker rows regenerated: refit/gen3.py over all 643 off courses (t4/P/sc/cv scores) and over the 57 pads courses
  (out-of-fold fold-model scores with pads, t5/sc_on.py).
* The shipped re-ranker recipe (rankbag, X2 NC, beam/renum/start/end, thr 0.5) was fitted per state fold on the off rows
  only, as production keeps its fits, and applied out of fold to the off rows and to the pads rows (t5/rr_on.py). The
  off picks equal picks_tb.json (240 of 240).
* Tee: refit/tgen2.py rows for off (picks_tb) and pads (picks_on); the shipped hybrid rule (0.93 / 12 / 0.5) per fold
  on the off rows only (t5/tl_on.py). The off picks equal tee_picks.json (638 of 638).
* Bench arm: pads on, ROUTE_RERANK=0 ROUTE_TEE=0 with those picks, fold rescoring (t5/arm_B2.json) vs t5/arm_A0.json.

| arm (holes right on the 57) | choice (40) | never-used (17) |
| --- | --- | --- |
| off, out-of-fold re-ranker / tee (= oof.json) | 368 | 139 |
| **pads, out-of-fold re-ranker / tee** | **362 (-6; 1 better / 5 worse)** | **144 (+5; 3 better / 1 worse)** |
| off, solver only | 346 | 123 |
| pads, solver only | 348 (+2; 3 / 2) | 131 (+8; 3 / 2) |
| off, live production re-ranker / tee (in-sample: these courses are in their training) | 397 | 149 |
| pads, live production re-ranker / tee | 377 | 144 |

* Per course, out-of-fold: choice creekside 7 -> 10; hansen_park 4 -> 0, indian_trace 10 -> 8, edgebrook 3 -> 2,
  hickory_knoll 5 -> 4, riverbend 2 -> 1. Never-used stone_creek_ny 6 -> 10, pine_crest_wa 0 -> 2, rockingham 6 -> 7;
  shady_hills 3 -> 1.
* OOF 643: 507 -> 506 holes on the 57 courses, the other 586 unchanged by construction: 87.04 % -> 87.03 %. Fails
  "OOF 643 up". Never-used passes the relaxed rule (+5, 3 / 1).
* Card residual on the 57 (median / p90 yd): 9.0 / 51.0 off, 9.4 / 48.7 pads.
* The live production re-ranker / tee are in-sample on every one of these courses: +39 holes over the out-of-fold
  picks on the off arm. Any comparison with live models on bench courses is unusable.
* No trigger fraction helps choice. Each course's out-of-fold result does not depend on which other courses trigger
  (fold models are fitted on off rows only), so subsets of the 57 can be scored directly:
  < 0.1 n choice +0 (2 courses), < 0.25 -1 (8), < 0.4 -1 (12), < 0.5 -6 (15), < 0.6 -7 (25), < 0.75 -6 (40).
* A re-ranker refit on rows with pads (off rows for 586 courses + pads rows for the 57; rr_fit.py out of fold) is worse
  at the row level: choice 6353 -> 6339 holes right, never-used 2951 -> 2952. So a refit does not rescue it either.

Blind loop: no loop course triggers. Hawk's Point's chosen 2017 vintage has 20 raw complexes (trigger < 13.5): pads
cannot touch its 1 approximate hole (hole 15). Sunset (9 complexes, 9 holes), Remsen (11, 9 holes) and Glenwild (32)
are above it too. With the rule opt-in, the default code path is unchanged, so the loop was not re-run.

Reproduce (scratch t5/): folds.sh (pick tables in /dev/shm, foldfit), padk_oof (pad files with out-of-fold scores),
arms.sh (A0 / A1 / B1 / As / Bs / B2), gen_off.sh, on_rows.sh (sc_on.py + gen3), rr_on.py, tg_off.sh, tl_on.py,
cmp.py.

## State 2026-11-20 (later): gate 2 for golfseg_own_v3, paired v2 / v3 on Actions: FAILS (v3 stays opt-in)

Stage `detector_pair` of .github/workflows/routing_bench.yml (refit/detector_pair.py + refit/pair_merge.py). Per course
the inputs are rebuilt twice on the same runner with the same code and the same NAIP years. The years are the package
year + the 2 extra years the v2 bench's scenes used (benchdata/big/pinned_years.json). If the pinned package year is no
longer served, the first served year above the extra years is used.

Only the U-Net weights and the object models differ between the arms. Both arms are routed the same way:
* state-fold route_learn scores (ROUTE_BENCH_FOLD_RESCORE=1, benchdata/folds = the rsel fold models, committed);
* the shipped re-ranker and tee step live;
* production card pick;
* FASTSCENE_UNET_MODEL=v2 and FASTSCENE_VINTAGE=0 in both arms.

So the routing fits and thresholds are v2's in both arms: this is v3 scenes under v2-tuned routing, not a v3 refit.

Pool: the 600 TRAIN-BIG courses, 20 shards. The 43 validation courses of choice are excluded (different imagery path).
Test 28 was not touched.

Runs:
* 44813097321, noise attempt 1: failed. 12 of 20 courses had an unserved pinned package year; fixed in 2a9775992.
* **44815560624, noise floor A vs A:** v2 twice, B's imagery refetched, 20 courses (14 choice + 6 never-used). All 20 are
  identical: holes, fwd, card error, recall, scene counts. Choice is 94.22 % in both arms, never-used 87.96 % in both.
  The paired delta within one run has zero noise.
* **44817755394 (run 5):** A = golfseg_own_v2 + objects_unet_v2, B = golfseg_own_v3 + objects_unet_v2.
* **44823590755 (run 6):** A = golfseg_own_v2 + objects_unet_v2, B = golfseg_own_v3 + objects_unet_v3.

Both 600-course runs: 596 complete pairs.

Run 5 (B = v3 + objects_unet_v2):

| | choice (397, 6570 holes) | never-used (199, 3303) | all (596, 9873) |
|---|---|---|---|
| holes right A / B | 87.06 / 86.96 % | 86.74 / 87.01 % | 86.95 / 86.97 % |
| net change | -7 | +9 | +2 |
| fwd metric A / B | 88.08 / 88.17 % | 88.37 / 88.47 % | 88.18 / 88.27 % |
| courses better / worse / same | 88 (+207) / 97 (-214) / 212 | 51 (+103) / 54 (-94) / 94 | 139 (+310) / 151 (-308) / 306 |
| flips of 5+ holes, up / down | 9 / 8 | 5 / 4 | 14 / 12 |
| all-right courses A / B | 161 / 147 | 70 / 72 | 231 / 219 |
| card error median A / B | 6.3 / 6.2 yd | 6.5 / 6.2 yd | 6.4 / 6.2 yd |
| green recall A / B | 96.21 / 96.83 % | 95.58 / 96.85 % | 96.00 / 96.84 % |
| tee recall A / B | 87.34 / 88.25 % | 85.92 / 88.01 % | 86.86 / 88.17 % |

Largest flips in run 5:
* up: soule_park_ca +16, holiday_valley_ny +15, holly_ridge_ma +13;
* down: pb_dye_md -17, valley_co -13, wilshire_ca -10, belgrade_lakes_me -10.

Run 6 (B = v3 + objects_unet_v3):

| | choice (397, 6570 holes) | never-used (199, 3303) | all (596, 9873) |
|---|---|---|---|
| holes right A / B | 87.03 / 86.77 % | 86.47 / 87.01 % | 86.84 / 86.85 % |
| net change | -17 | +18 | +1 |
| fwd metric A / B | 88.04 / 87.87 % | 88.13 / 88.59 % | 88.07 / 88.11 % |
| courses better / worse / same | 84 (+213) / 99 (-230) / 214 | 52 (+122) / 53 (-104) / 94 | 136 (+335) / 152 (-334) / 308 |
| flips of 5+ holes, up / down | 11 / 12 | 5 / 3 | 16 / 15 |
| all-right courses A / B | 166 / 162 | 68 / 63 | 234 / 225 |
| card error median A / B | 6.5 / 6.3 yd | 6.5 / 6.2 yd | 6.5 / 6.2 yd |
| green recall A / B | 96.24 / 96.85 % | 95.64 / 97.00 % | 96.04 / 96.90 % |
| tee recall A / B | 87.29 / 89.62 % | 85.92 / 89.10 % | 86.83 / 89.45 % |
| tee complexes A / B | 8500 / 8760 | 4440 / 4605 | 12940 / 13365 |

Largest flips in run 6:
* up: hillcrest_sc +18, eagle_crest_ny +17, soule_park_ca +15, holiday_valley_ny +12;
* down: pb_dye_md -17, texas_rangers_tx -12, creekside_wv -9, hermitage_va -9.

Reading:
* v3 reshuffles routing course by course (about 290 courses move, 5-18 hole swings both ways), but the net is flat.
* Recall rises (greens +0.9 pt, tees +1.3 pt, or +2.6 pt with objects_unet_v3) and card error falls 0.2 yd. Neither
  turns into holes: choice goes down (-7 / -17), never-used up (+9 / +18).
* objects_unet_v3 was loaded under FASTSCENE_UNET_MODEL=v2. Its models took effect (tee complex counts changed), but
  any other v3-only setting did not.

Caveats:
* **Arm A (v2) is not identical between the runs:** 8585 holes in run 5, 8574 in run 6. The code is the same; the only
  commit between them adds the objects_unet_v3 files, which arm A does not read. So rebuilding on Actions has about 10
  holes of run-to-run noise in aggregate. Imagery served differently and runner CPU / BLAS are the candidates; this is
  not yet checked. Compare runs only through their own paired deltas, which share imagery within the run.
* The same 4 courses failed in both arms of both runs:
  * woods_fort_mo, windy_acres_wi and rising_star_casino_resort_in: an extra year of 2024 is not served;
  * buffalo_hill_mt: no NAIP.
* The package-year pin held on only 146 of 597 courses; the rest used the fallback year. Both arms share this, but the
  absolute levels are not comparable with the v2 bench.

**Verdict (coordinator): v3 fails gate 2 and stays opt-in** (FASTSCENE_UNET_MODEL=v3). The fair test is a routing refit
on v3 scenes against a v2 refit on the same rebuilt inputs. The next step is the Actions `refit` stage, built from the
design above.

Reproduce: course_data/requests/routing_bench_pair_{noise,v3,v3obj}.json; the tables are in each run's pair-merge job
summary (artifact pair-merged: pair_all.jsonl + pair_tables.txt).

## State 2026-11-26: two routings per course, route_conf picks one and scores every hole (default; ROUTE_ENSEMBLE=0 rollback)

Problem (Ridges, 2026-11-20): wrong holes are not flagged. On the default out-of-fold bench (t2/x/P/oof.json, 643
courses) route_gate's P < 0.5 marks 4.6 % of holes and catches 24 % of the wrong ones.

Data: the per-course routings of the paired detector runs 44817755394 and 44823590755 (594 TRAIN-BIG courses, each
routed on the v2 scene (A), the v3 scene with objects_unet_v2 (B) and v3 with objects_unet_v3 (C)), copied into the repo
by .github/workflows/artifact_fetch.yml (course_data/research/artifacts/pair_v3).

Finding: A and B are equally accurate (87.1 %) but differ on half the courses. Where they put a hole's green in the
same place (within 20 yd: 92 % of holes) the hole is right 92.4 % of the time; where they do not, 29 %.

route_conf.py: LightGBM on route_gate's per-hole features, the neighbouring holes, course statistics and the distance
of the hole's green / tee to the other routing's. Out of fold by course (8 folds), second routing B:

| | all 594 | choice 396 | never-used 198 |
|---|---|---|---|
| holes right, routing A | 87.11 % | 87.18 % | 86.98 % |
| picked routing (B must lead by 0.5 predicted holes) | 88.24 % (+111 holes, 102 switch) | 88.31 % (+74) | 88.10 % (+37) |
| best of the two per course (oracle) | 90.26 % | 90.34 % | 90.10 % |

Flags on the picked routing: P < 0.65 marks 9.1 % of holes, 65.5 % of them wrong, and catches 50.8 % of the wrong
holes; unflagged holes are 93.6 % right. route_gate on routing A at its 0.5: 5.6 % marked, 30.6 % caught, unflagged
90.5 % right. (The paired runs' level is not the out-of-fold bench's: the re-ranker and tee step are live there.)

Not shipped, measured: a third routing (C) with the pick over three gives 88.74 %; taking each hole number from the
routing with the higher P (ignoring consistency) gives 88.87 % with two routings, 88.92 % with three, with 99 / 116
shared-green conflicts over the 594 courses. Per-hole oracle of three: 92.3 %.

Wired: route_scene.run -> _ensemble (second fastscene.build with FASTSCENE_UNET = golfseg_own_v3, route_v2 with the
same card, route_conf.pick). r["ensemble"] = use / p / sum_a / sum_b / agree / seconds. fast.py marks holes with
route_conf's P (approximate below route_conf.APPROX_P = 0.65; routing_confidence.source = route_conf); a hole
route_gate holds at or under FALLBACK_P keeps the lower of the two. The second scene failing leaves routing A with the
single-routing model (41 % of wrong holes caught at 0.5 on A). Cost: 10-105 s per course (the second U-Net pass).

Real builds (e2e/run1.py, 4 never-used courses): Ridges 10 -> 13 of 18 (routing B kept), Split Rock 9 / 9, Bailey
Creek 18 / 18, Revere 18 / 18 unchanged (A kept), no hole marked approximate on the three right courses. Ridges'
5 remaining wrong holes (3, 4, 6, 7, 12) are not flagged (P 0.94-0.96): both routings agree and fit the card within
3 yd, but the card's yardages are not the truth holes' (card 268 / 367 / 432 / 474 / 291 against 350 / 466 / 287 /
350 / 214): a wrong-card case, not a routing one.

Test 28 was not read (no paired routings exist for it).

Same day, tee placement on routed courses (platform/package.py, platform/sanity.py, 033421131): the far cap is off when
the tee boxes are detections, and a tee straight behind the line start is not sent back for standing beside another
hole's tee. Card misfits over 15 yd on the right holes of the 4 builds: 7 -> 0.

## State 2026-11-26 (later): verified holes (route_conf 'pair_id' model + card corroboration)

Goal: holes the page can show as right with no human check. Out of fold by course (8 folds) on the paired 594 TRAIN-BIG
courses, routing A scored against B.

Ceiling of the shipped P(hole right): at P >= 0.97 the holes are 97.0 % right and no threshold passes 98.6 %. What the
confident wrong holes are (P >= 0.97, forward-tee label, 110 of 4,714):

| | holes |
|---|---|
| green right, tee more than 40 yd off the mapped centre line | 61 |
| a real hole under another number (nine swap 20, other 13) | 33 |
| green matches no mapped hole end | 14 |
| another hole's green | 2 |

* The tee cases are mostly a forward box beside the mapped line, on the right hole, with the card fitting within 5 yd.
  Label `identity_ok` (route_conf.py): green within 20 yd and the tee within 90 yd of the first 60 % of the hole's line
  with no other hole's line nearer. Holes right 88.3 % -> 89.5 %.
* The number cases cluster in a few courses whose card sequence is not the map's (Lincolnshire Fields 16 holes, Spring
  Lake 8, Burlington 6, Jersey Meadow 5): one card source, no second source agreeing.
* A third routing (arm C) as extra features: no gain (98.3 -> 98.5 % at half the holes).

Rule (truth-free): VERIFIED = P_id >= 0.98 (model 'pair_id', fitted on identity_ok) and at least one scorecard from
another source agreeing with the card used on 80 % of the holes within 12 yd (route_conf.card_corroboration).

| | holes verified | tee and green right | green and number right |
|---|---|---|---|
| all 594 | 31.7 % | 99.14 % (27 wrong of 3,124) | 99.65 % |
| never-used 198 | 29.7 % | 99.18 % | 99.80 % |
| choice 396 | 32.7 % | 99.12 % | 99.58 % |

322 of 594 courses get at least one verified hole (median 9.5), 22 get all 18. Threshold 0.97: 39.1 % at 98.96 %.
The threshold and the rule were chosen on these same out-of-fold predictions; the never-used split is the check.

Wired: route_scene._ensemble -> r["ensemble"] p_id / verified / card_corroborated; library/route_unmapped.py ->
routing.json; library/course_page.py verified_holes: a routed hole must also pass every picture check on every solved
set and not be approximate. On a fully OSM-mapped course every hole that passes its checks with a matched card is
verified. status.json `verified_holes`, the page subtitle and each hole's `verified`. Library backfill from the stored
qa.json files (mapped pages only): 1,071 of 1,791 holes verified, 48 of 100 courses with 14 or more.

Refit: python3 route_conf.py fit_id ../../research/artifacts/pair_v3/44817755394 ../../research/artifacts/pair_v3/44823590755

## State 2026-11-26 (evening): verified holes, first real builds and fixes

* First builds with the rule: gaylord_springs 1 verified (9, 10 routed-verified; 9 has a CHECK), lake_shawnee and
  lake_of_the_woods_como 0. Lake Shawnee was a bug: `card_corroboration` dropped every web card whose tee sets equal
  the used card's, so three sites with the very same numbers gave 0. The measured rule (oof5.py) counts every other
  card, identical or not; only the used card itself is now excluded. Lake of the Woods is right to get none (no
  second card; the one card misfits the map on 3 holes).
* Uncorroborated holes cannot be verified at any threshold: P(id) >= 0.98 / 0.99 / 0.992 are 97.1 / 97.4 / 97.1 %
  right (only >= 0.995, 2 % of holes, reaches 99 %). The misses are card-order conflicts the features cannot see.
  40 % of benchmark holes sit on courses with no second card, so a new card source is the lever for coverage;
  bluegolf and golfpass never return a card (their lookup goes through a web search that answers runners with a
  bot page).
* Partly mapped courses (hole method v2 / structure / v2+structure): the holes OpenStreetMap draws itself (no
  `routing` on the package hole) now verify like a fully mapped course's. Holes the old routing stage numbered do
  not: its unflagged holes are 89 % right (pipeline_eval.json 31 test courses 0.893, pipeline_select.json 51
  train 0.897).
* Scorecard plausibility at multi-course sites: the OSM summary lists every hole in the area, so Pinehurst No. 2
  (57 holes, refs like "10 - #2"), Gamble Sands and Forest Dunes (a short course repeating 1-18) rejected the right
  card. `fetch_package.hole_lengths` now gives each number the list of its mapped lengths and no hole count when
  numbers repeat; `scorecard.plausible` compares with the nearest.
* picture_checks.TEE_TOL 3 -> 8 yds: 52 mapped library holes failed only by a marker 4-8 yds off the tee polygon.
  Of 507 failing mapped holes, 249 fail on the tee-box check alone; the rest of those are walkback / lidar-pad tees
  30-40 yds from any mapped box (the card yardage matches no mapped tee), which stay unverified.
* Tier C (route_joint) verified holes, `route_conf.verified_joint`: `route_bench.py joint --split train+big` rerun
  (631 courses per mode). Lines mode (OSM's hole lines without refs) 97.2 % numbered right; margin >= 4 and a
  corroborated card: 56 % of holes, 99.6 % right (23 wrong); margin >= 4 alone 98.7 %. Osm mode (greens and tees
  only) 81 % right and no margin / card-fit / corroboration rule passes 96 %: never verified (Brown Deer, Glen Mills).
* build_holes.build: a way with no ref took number len(out) + 1, which replaced Ironhorse's hole 17 (hole 4's green
  and par) once OSM lost a hole way; it now takes a number above every mapped one.

## State 2026-11-26 (night): greens and tees mapped, lines not -> the scene router

`pair_keeposm` (routing_bench run 45881895609, artifacts research/artifacts/pair_keeposm): the 600 TRAIN-BIG courses
routed by the scene router (detector v2, fold models, re-ranker and tee step live) with OSM golf features given back
(`ROUTE_BENCH_KEEP_OSM`, route_bench.strip_golf; `keep_osm_a` / `keep_osm_b` in the request). Holes right (tee and
green), 586 courses in every arm:

| input | all | never-used 197 | courses all right |
|---|---|---|---|
| photos only (pair_v3 arm A) | 87.3 % | 87.0 % | 39.4 % |
| + every OSM golf feature but the hole ways | 89.4 % | 89.7 % | 42.7 % |
| + OSM greens and tees only | 89.5 % | 89.6 % | |
| route_joint on the same OSM objects (osm mode) | 80.8 % | 80.9 % | 21.0 % |

Shipped: fast.py sends a course with < 3 hole lines to the scene router whatever OSM maps of its greens and tees
(route_scene.needs_perception), route_joint's osm mode only when that gives no holes (or no imagery). route_joint
still orders OSM's own unnumbered lines first. Mapped greens add only 2 points to photos alone: the misses are the
numbering, not the objects.

route_conf on those routings (shipped model, A against B of pair_keeposm, a same-detector pair): P(id) >= 0.98 and a
corroborated card is right on every hole it passes but passes 0.7 % of holes; the model was fitted on photo-only
candidates. `pair_keeposm2` (both detectors, OSM given) is the refit's input.

Ruled out: OpenGolfAPI's per-hole tee_coords / green centre / green_polygon fields are null on every course tried
(Lake Shawnee, Gaylord Springs, Pebble Beach, Glen Mills, Brown Deer).

route_conf refit on photos-only and OSM-given routings (`pair_keeposm2`, run 45897110413: both detectors, every OSM
golf feature but the hole ways given). `route_conf.py fit / fit_id <pair_v3 runs> -- <pair_keeposm2 run>` ("--"
separates experiments: arms pair only within one). Out-of-fold by course (scratch oof6.py), P(id) >= 0.98 and a
corroborated card:

| fitted on | photos: holes verified / right | OSM given: holes verified / right |
|---|---|---|
| pair_v3 only (shipped until now) | 32.4 % / 99.09 % (29 wrong) | 0.5 % / 100 % |
| pair_v3 + pair_keeposm2 | 31.9 % / 99.27 % (23 wrong) | 27.0 % / 99.22 % (20 wrong) |

Never-used courses: 29.1 % / 99.27 % and 26.7 % / 99.29 %. OSM-given routings are 91.9 % identity-right, 89.3 % tee
and green right (two-detector run). The threshold stays 0.98.

## State 2026-11-27: where the misses are; the course point as a clubhouse (not shipped)

Misses on pair_keeposm2 arm A (OSM greens / tees given; 999 wrong of 9,459 holes under hole_ok):
* 424 green right, tee wrong: 245 of them pass hole_ok_fwd or identity_ok (a forward box beside the line), 168 are
  another hole's tee (median 21 yd from that hole's line, 98 yd from the own start), 15 other.
* 429 a real hole green under another number: 88 nine swaps (8 courses), 72 two-hole swaps (36 courses), 32 shifts,
  237 other (48 courses).
* 146 a green that is no hole's (76 scene detections and 24 virtual greens although OSM maps every green; the rest
  OSM practice greens).
* 639 of the 999 are on the 69 + 84 courses whose hole 1 or last hole is wrong (photos only: 848 of 1,252).

Course point: OpenGolfAPI's lat / lng (benchdata/big/club_points.json, 518 of 600 TRAIN-BIG courses). Hole 1's tee
is the tee nearest it on 35 % of courses, among the nearest three on 68 %; the last green 37 % / 67 %; median 159 yd.
`ROUTE_CLUB_POINT=1` makes it co["club"] (src "point") when no clubhouse is tagged and it lies within 400 yd of a
green. Full refit with it and the re-ranker's clubhouse features live (NC=0), routing_bench run 45913165005, against
the v2 refit 44856349197, out of fold:

| split | v2 refit | with the point |
|---|---|---|
| all 643 | 85.51 % | 86.09 % (+62 holes; 111 courses better, 105 worse) |
| choice 443 | 85.09 % | 86.43 % (+99) |
| never-used 200 | 86.45 % | 85.34 % (-37; 23 better, 46 worse) |

Not shipped: the gain is on one split and a loss on the other, and as many courses get worse as better. The knob
stays off (default 0). A refit alone moves 234 courses' per-hole results, so a +0.6 point change is inside the noise
of this protocol.

## State 2026-11-27 (later): pairing is the bottleneck; a learned hole field (part affinity field)

Physical holes (a routed line whose green is a mapped hole's and whose tee stands on that hole): 94.1 % of holes with
OSM greens / tees given (pair_keeposm2 arm A), 91.7 % on photos (pair_v3 arm A). Courses with every physical hole
right: 288 of 570 / 270 of 594, and of those 271 / 259 are numbered right throughout (94 / 96 %). So the numbering is
not the bottleneck: the tee <-> green pairing is, and a wrong pair drags its neighbours' numbers (329 / 405 holes are
a right physical hole under a wrong number, 89 / 90 of them on courses with every pair right). Six failing courses
drawn (scratch viz.py): parallel holes sharing a tee area and swapping tees, the tee by the previous green taken for
the wrong hole, a par-3 course entered from the wrong side; no single pattern. Card: on the 183 right-green wrong-tee
holes the true tee fits the longest set better on 53 %, the routed one on 26 %; an all-sets yardage fingerprint is no
better (40 / 28 %).

Hole field (research/holefield_gate0.py, the routing_bench `research` stage): a 5-level U-Net (24 base channels,
5 m / pixel, 384 x 384) predicts the unit tee -> green direction within 22 m of each hole line (+ an on-a-hole
logit), as OpenPose's part affinity fields; a tee is scored for a green by the field's mean alignment along the
segment (or its best single bend). Gate 0, input = the mapped layout only (green / tee / fairway / bunker / water
rasters), 421 train / 95 test courses, 40 epochs (run 45936097627, 4.5 h on 4 cores):

| score | green's best tee is its own | Hungarian, hole starts x greens | courses all paired |
|---|---|---|---|
| hand (length + fairway under the segment) | 52.2 % | 46.3 % | 1 % |
| learned field | 90.2 % | 92.3 % | 70.5 % |
| true field (ceiling of the scoring) | 97.0 % | 97.8 % | 85.3 % |

Gate 0b (run 45976979983), per hole against the scene router on the same 91 test courses (1,453 holes whose routed
green is a mapped hole's): router's tee right 1,367 (94.1 %), field's best tee right 1,329 (91.5 %), both 1,268,
router wrong / field right 61, router right / field wrong 99, both wrong 25; on the router's 86 wrong tees the true
tee out-scores the routed one on 80 %. The two err on different holes (either right: 98.3 %): a feature for the hole
/ tee models, not a replacement. Gate 1 (holefield_gate1.py) = the same from the detector's maps, against the
photo-only router.

Gate 1 (run 45979467058, research/holefield_gate1.py, 3 h): the field learned from the detector's maps (U-Net
P(green) / P(tee) + corridor maps fair / bunker / water / tree / turf; 420 train / 95 test courses, fold 0): green's
best tee its own 89.0 %, Hungarian 92.3 %, courses all paired 69.5 % (true field 96.4 / 97.8 / 85.3 %): the same as
from the mapped layout. Against the photo-only router (pair_v3 arm A, 1,479 holes whose routed green is a mapped
hole's): router's tee right 1,356 (91.7 %), field's 1,334 (90.2 %), router wrong / field right 74, router right /
field wrong 96, both wrong 49 (either right 96.7 %); on the router's 123 wrong tees the true tee out-scores the
routed one on 76 %. Caveat: the tee candidates include the mapped hole starts. Go: folds 1-4 for out-of-fold fields
(`args_list` runs one job per entry), then the field's line integral as a hole / tee feature and a refit.

## State 2026-11-27 (night): hole-field features in the hole model: +1.2 points out of fold (not shipped yet)

Fields out of fold for every TRAIN-BIG course (holefield_gate1.py, fold 0 run 45979467058, folds 1-4 run 46020653509;
about 3 to 4.5 h a fold on 4 cores). `holefield.pair_x` -> hx4 per candidate (tee complex, green): the line integral
from the complex centroid and from its far box, the pair against the best of its green and of its tee, its rank among
the green's tees. `ROUTE_HOLEFIELD=<dir>` adds hx4 to route_learn's hole model (x3 tables; NaN where a course has no
field, e.g. the 43 validation train courses). The shipped refit with it (routing_bench run 46061583284,
`holefield_run_a` / `holefield_run_b` in the request), against the v2 refit 44856349197, out of fold:

| split | v2 refit | + hx4 | courses better / worse | all-right courses |
|---|---|---|---|---|
| all 643 | 85.51 % | 86.75 % (+133 holes) | 159 / 89 | 234 -> 261 |
| choice 443 | 85.09 % | 86.62 % (+113) | 106 / 60 | 170 -> 190 |
| never-used 200 | 86.45 % | 87.05 % (+20) | 53 / 29 | 64 -> 71 |

Forward-tee metric +130 holes (86.97 -> 88.19 %); card error median 6.4 -> 6.0 yd. Both splits up, better : worse
about 1.8 : 1 on each (the course-point refit was 111 : 105). Only the hole model reads the field so far: the tee
step and the re-ranker do not. Caveats: the field canvas is centred on the mapped hole lines (production must centre
on the scene), the fields come from 420-course fits, the test-28 split is unread.
To ship: a field model fitted on every course; field inference in the fast path (the network is 5 levels of 3x3
convolutions at 384 x 384, 5 m); the refit's fits into route_models/ with fold models and a route_conf refit on its
paired routings; one read of test 28.
