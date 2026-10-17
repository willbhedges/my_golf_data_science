# Course structure from first principles: every hole and the playing order

Owner: course-structure inference (`course_data/structure/`). Input: "this is the golf course" (a boundary, or a
point resolved to one) and a scene of what can be seen on it: greens, tee boxes / complexes, fairways, bunkers,
water, trees, cart paths, buildings, car parks, ranges. Output: every hole (tee complex -> corridor -> green), its
number 1..N, par, direction of play and a calibrated confidence per hole, **with no scorecard and no OSM hole
markings**. A card is an optional prior.

## Results

### Held-out: 12 states never used for tuning, all OSM hole info and the scorecard hidden

59 fully mapped courses (52 x 18 holes, 7 x 9) in IA MO NE CT NJ PA AR DE NC ID NV WA (seeded, 3 states per
Census region). Solver commit `89d98c3`, one run (Actions `structure` eval, run 39021134300); `eval/results.json`.

| config | courses | holes | hole formed | **hole number** | number, nine-swap ok | **courses fully correct** | all holes formed | par | N (9/18) right | ECE | Brier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **no card, no OSM holes (full)** | 59 | 999 | 73.1% | **24.1%** | 35.4% | **5.1%** (3/59) | 11.9% | 87.8% | 98% | 0.080 | 0.162 |
| - without cart paths | 59 | 999 | 71.8% | 23.9% | 33.6% | 3.4% | 10.2% | 88.0% | 98% | 0.088 | 0.159 |
| - without clubhouse | 59 | 999 | 72.7% | 14.3% | 27.3% | 3.4% | 8.5% | 87.7% | 98% | 0.104 | 0.116 |
| + card prior (pars + yards) | 59 | 999 | 76.3% | 64.5% | 65.2% | 11.9% | 11.9% | 87.2% | 98% | 0.164 | 0.203 |
| perception stand-in (degraded OSM) | 59 | 999 | 52.5% | 13.4% | 22.6% | 1.7% | 1.7% | 87.5% | 81% | 0.092 | 0.127 |
| - without clubhouse | 59 | 999 | 51.5% | 8.2% | 15.4% | 0.0% | 0.0% | 86.9% | 81% | 0.135 | 0.096 |
| - with card prior | 59 | 999 | 54.7% | 32.0% | 32.7% | 1.7% | 1.7% | 85.8% | 95% | 0.088 | 0.163 |

27 / 36-hole facilities (10 held-out, formation only, any number): 35.5% of 330 true holes formed; the hole
count (27+) was guessed on 8/10. These use a greedy loop builder, not the exact DP.

Fully correct held-out courses (no card): heritage_shores_de, blair_nj, skytop_pa; spooky_brook_nj is right up to
the front / back nine. Per state, hole formation runs 62-91 % and hole number 0-50 %.

**Calibration (held-out, no card).** Per-hole confidence vs hole-number correctness:

| confidence | holes | mean confidence | accuracy |
|---|---|---|---|
| 0.0-0.2 | 334 | 0.16 | 0.07 |
| 0.2-0.4 | 526 | 0.28 | 0.29 |
| 0.4-0.6 | 116 | 0.47 | 0.50 |
| 0.6-0.8 | 14 | 0.62 | 0.21 |
| 0.8-1.0 | 8 | 0.90 | 1.00 |

With the card the confidences are under-confident (0.4-0.6 bin: 76 % right; 0.8-1.0: 92 %); the Platt map was fitted
on no-card dev runs only.

### Perception scenes (blind, `course_data/perception/scenes`, tuning-state courses)

The perception agent's blind `course_scene/1` output (NAIP + lidar, no OSM golf input) for 63 dev-state courses
with OSM truth: formation 64.6 %, hole number 21.5 % (30.6 % nine-swap ok), no course fully correct; with the
card prior 68.9 % / 53.8 %. The real perception output forms more holes than the degraded-OSM stand-in (65 vs
51 %), and its confidences are the best calibrated (ECE 0.035).

### Dev (tuning states; same solver; `eval_dev/`, Actions run 39022431554)

| config | courses | holes | formed | hole number | nine-swap ok | fully correct | par | ECE |
|---|---|---|---|---|---|---|---|---|
| full (no card) | 100 | 1782 | 75.2% | 26.4% | 41.6% | 5.0% | 90.0% | 0.055 |
| no cart paths | 100 | 1782 | 75.1% | 25.6% | 42.3% | 5.0% | 89.9% | 0.045 |
| no clubhouse | 100 | 1782 | 75.4% | 16.7% | 29.2% | 2.0% | 89.4% | 0.083 |
| card prior | 100 | 1782 | 77.9% | 68.2% | 68.9% | 15.0% | 90.1% | 0.196 |
| degraded | 100 | 1782 | 50.8% | 10.0% | 19.5% | 0.0% | 86.5% | 0.126 |
| degraded, no clubhouse | 100 | 1782 | 51.0% | 5.8% | 14.2% | 0.0% | 86.2% | 0.157 |
| degraded + card | 100 | 1782 | 53.1% | 30.2% | 32.0% | 0.0% | 87.0% | 0.069 |
| perception scenes (blind) | 63 | 1116 | 64.6% | 21.5% | 30.6% | 0.0% | 88.8% | 0.035 |
| perception scenes + card | 63 | 1116 | 68.9% | 53.8% | 54.0% | 0.0% | 89.4% | 0.083 |

Held-out matches dev (formation 73 vs 75 %, hole number 24 vs 26 %): the model did not overfit the tuning states.
Cart paths add little once the walk-direction terms are in (+0.2-1.8 points); the clubhouse is worth ~10 points of
hole-number accuracy.

## Why it is not ~100 % yet (error analysis on dev)

* **Hole formation (~73-75 %)** is the ceiling for everything else. Per green, the right tee complex is the top
  hypothesis 73 % of the time; 63 % of the misses take another hole's tee (exclusivity and the route fix some),
  28 % take a forward tee or a range / practice tee, 8 % are greens without a mapped tee. Dog-legs without a
  fairway touching the green and par 3s next to each other are the hard cases.
* **Given the right holes the loop is right.** With oracle hole formation the cyclic order is correct on 13 of the 15
  first dev courses; what is left is where the round starts:
* **Front / back nine.** Two returning nines are nearly symmetric. Cues fitted on dev: tee 1 nearer the
  clubhouse (66 % alone), green 18 nearer it (61 %), the DP score difference (68 %), tee 1 nearer a practice
  green, the range, the car park; the classifier gets ~70 %. Without a card about a third of otherwise-perfect
  routes come out with the nines swapped (one dev run: 8 courses correct only up to the swap). A card resolves it
  (64.5 % hole numbers held-out vs 24.1 %).
* **Clubhouse.** OSM rarely names it; 16 % of dev courses fall back to "hubs". Without any clubhouse the hole
  number accuracy drops from 24 to 14 %.
* **Truth noise.** OSM hole ways start at the mapped tee, sometimes 50-100 yds ahead of the back tee; some
  courses map the wrong course of a 36-hole facility (whistling_straits_wi) or a pitch-and-putt.

## 1. What the solver does

`scene.py` turns OSM features (every `golf=hole` way and `golf=pin` dropped, `ref` / `name` of golf features
hidden) or a perception scene (`course_scene/1`) into one local frame in yards. `solver.py`:

1. **Tee complexes.** Boxes within 22 yds, or up to 75 yds apart along a shared long axis (forward tees), are one
   complex. Perception scenes already give complexes.
2. **Hole hypotheses** for every (green, complex) 70-700 yds apart, scored by a conditional-logit formation model
   (`solver.FEATS`):
   * `length`: log-likelihood ratio of the straight length under a par 3/4/5 mixture (dev holes: par 3 172 +/- 32,
     par 4 370 +/- 55, par 5 498 +/- 55 yds back-tee straight line; USGA guide for men: par 3 <= 250, par 4
     251-470, par 5 471-690 yds);
   * `align`: the complex's long axis vs the line of play (boxes are built along it);
   * `corr`: least-cost "line of play" over a cost raster (fairway / green / tee 1, rough 1.8, bunker 1.5,
     water 3, woods 3.5) relative to the straight length. A dog-leg follows its fairway cheaply; a wrong pair
     crosses rough, woods or water;
   * `chain` / `chain_neg`: the green's own fairway (the one touching it) points back at this complex (green ->
     fairway -> far end -> tee cone). This is the strongest single cue (per-green top-1 72 -> 81 % on the first dev
     set);
   * `fw_x`: the line crosses another fairway at > 35 deg (holes rarely cross). `fw_cov` / `fw_end`: fairway
     share / ends along the line. `cross_green`: the line passes over another green. `far`: another complex on the
     far part of the line. `fwd`: forward tees on the corridor. `start`: another green (the previous hole) or the
     clubhouse is near the complex; forward tees sit mid-corridor;
   * the detector confidence of the complex (perception `p`) as a fixed log-prior.
3. **Sequence as a CRF over routes.** A round is a path through N of the M greens. The move from green *a* to hole
   (*b*, *h*) scores its formation plus the walk (`solver.TFEATS`): the walk log-normal (dev: median 64 yds, 90 %
   under 137, 99 % under 240), the distance, cos(previous hole's direction, walk) (players walk on, not back down the
   hole), cos(walk, next hole's direction) (tees are reached from behind), and cart paths that join them directly.
   The tee choice is summed out inside each move. Anchors: tee 1 and green 18 near the clubhouse H, and for 18
   holes green 9 and tee 10 (returning nines; the 9 -> 10 move has its own weights), each a log-normal plus a linear
   distance term. H is latent: tagged / detected clubhouses, buildings by car parks or next to the golf features,
   and "hubs" where greens and hole starts meet, each with a prior; the partition functions give the posterior.
   A hole-number par prior is a position term: on dev, hole 1 is a par 3 on 2 % of courses, hole 10 on 9 % and
   hole 18 on 13 %, against ~22 % overall. A card, when given, is another position term.
4. **Exact inference.** Held-Karp in log space over subsets (one BLAS matmul per layer; 2^19 x 19 states for 18
   holes + 1 spare green) gives log Z, the MAP route (Viterbi) and exact marginals P(green j is hole k). A complex
   (and its forward tees) can start only one hole: Lagrangian prices on complexes used twice, until the MAP route is
   consistent. Greens off the route are practice greens. The hole count N (9/18/27/36) comes from an exclusive
   green -> complex assignment (98 % right held-out).
5. **Front / back nine** by the antisymmetric classifier above; its probability enters the hole confidences.
6. **Par** from the length posterior with a prior on the number of par 3s / 5s (total ~70-72; 88 % of held-out
   holes right). **Hole numbers** come from the route, **direction of play** is tee -> green, and the hole
   **confidence** is P(number) x P(tee | route), Platt-calibrated on dev.

**Learning (dev courses only).** First the formation logit (`fit.py`), then the transition logit. Then every
formation, transition, turn and anchor weight is fitted jointly by maximum likelihood of the true routes, with
exact gradients: observed minus expected features, the pairwise marginals coming from the same forward-backward
(`crf.py`; checked against finite differences). Last come the hole-number par prior, the nine classifier and the
calibration (`fit.py --swap`, `--calibrate`). All weights are in `params.json`.

## 2. Data and protocol

* **Dev (tuning)**: courses from the 12 generalize states (CA GA IL KY MA ME MN MS NH UT WI WY): 48 drawn by
  `fetch.py select` from the committed surveys (outside generalize/sample.json), plus the generalize study's cached
  courses (routing v2's validation set). 100 of them have a clean 9 / 18-hole truth (refs 1..N once each) and >= N-2
  greens and tees.
* **Held-out**: 12 other states, seeded (`fetch.py states`) and surveyed on Actions. Per state: 5 random fully
  mapped 18-hole courses, one 9-hole course and one 27/36-hole facility; 59 of the 9/18-hole courses have clean
  truth. They were never looked at while tuning and were scored once.
* Hidden: every `golf=hole` way, `golf=pin`, every `ref` / `name` of golf features, and the scorecard. The truth
  is the hidden hole ways.
* Metrics (`eval.py`):
  * *formation*: the routed hole is a true hole (the green the true line ends on, plus a tee within 35 yds of the
    line start or on its first 60 %, extended 90 yds back for back tees);
  * *hole number*: formation and the same number;
  * *nine-swap ok*: number accuracy after swapping the nines, when that is better;
  * *fully correct*: all N numbers right;
  * *calibration*: ECE / Brier of the hole confidence vs hole-number correctness.
* Ablations:
  * `no_paths` and `no_clubhouse`;
  * `card`: pars and yards from the hidden ways, as a card prior;
  * `degraded`, a perception-quality stand-in: 25 % of tee boxes missed, merges, 4-yd jitter, 40 % of tee axes
    lost, 20 % of fairways and 3 % of greens missed, ~1 false green per course, cart paths cut and thinned, and the
    clubhouse only as an unnamed detection;
  * `perception`: the perception agent's blind scenes.

## 3. Contract (`course_structure/1`, `structure.py`)

`python course_data/structure/structure.py --osm osm.geojson[.gz] [--course course.json] [--card card.json]` or
`--scene scene.json` writes:

```json
{"schema": "course_structure/1", "n_holes": 18, "status": "ok", "card_used": false, "input": "osm",
 "clubhouse": {"ll": [lon, lat], "how": "named", "p": 0.8}, "total_par": 72, "p_route": 0.03, "p_front_nine": 0.71,
 "practice_greens": [{"id": "g19", "ll": [lon, lat]}],
 "holes": {"1": {"ref": "1", "par": 4, "p_par": [0.02, 0.9, 0.08], "tee_ll": [lon, lat], "green_ll": [lon, lat],
                 "tee_boxes_ll": [[lon, lat]], "length_yd": 402.5, "bearing_deg": 81.2,
                 "p_number": 0.43, "p_tee": 0.97, "confidence": 0.41, "p_green": 0.41,
                 "walk_in_yd": null, "status": "check", "flags": ["uncertain (41%) ..."],
                 "green_id": "g3", "tee_id": "t12", "tee_complex": "c4"}}}
```

`to_hole_features(res, fc)` adds `golf=hole` LineStrings (ref, par, `structure_conf`) the way
`routing.to_hole_features` does. `for_package(fc, course, card)` is a drop-in for `package.route_missing_holes`:
it fills only the refs OSM lacks, and holes with confidence < 0.8 get `status: check`. package.py is not changed
here; its owner can switch to it.

## 4. Files

| file | what |
|---|---|
| `scene.py` | Scene (yards frame); OSM -> scene with hole hints hidden; `truth_from_osm`; `degrade`; perception `course_scene/1` -> scene |
| `solver.py` | complexes, hypotheses + features, transition features, route DP (soft + Viterbi + marginals), Lagrangian tee exclusivity, nine classifier, pars, `solve()` |
| `crf.py` | the route CRF: potentials, forward-backward with pairwise marginals, exact-gradient maximum-likelihood fit |
| `fit.py` | formation / transition logits, par-by-hole-number prior, nine classifier, calibration -> `params.json` |
| `params.json` | every fitted weight (dev only) |
| `eval.py` | evaluation + ablations (`--split`, sharded on Actions) -> `eval/` (held-out), `eval_dev/` (dev) |
| `structure.py` | CLI + `course_structure/1` contract, `to_hole_features`, `for_package` |
| `fetch.py`, `.github/workflows/structure.yml` | held-out state survey, set selection, OSM fetch, sharded eval on Actions; `sets.json`, `surveys/`, `data/` |
| `plot.py` | per-course debug plot (truth vs route) |
| `test_structure.py` | DP vs brute force (log Z, MAP, marginals), CRF pairwise marginals, synthetic loop, contract |

## 5. Next steps (largest expected gains first)

1. Formation: learn the green -> fairway -> tee corridor from imagery or lidar (perception `fairways[].centerline`,
   mowing stripes) instead of OSM fairway polygons, and add tee-box elevation pads. Every point of formation
   accuracy compounds into the route.
2. Front / back nine: starter-hut / cart-barn detections, 10th-tee "halfway house" buildings, and the
   practice-area geometry as perception classes. A single web hint (the card's hole-1 length or par) settles it,
   as the card ablation shows.
3. 27 / 36 holes: run the exact DP per loop of 9 (3-4 loops through the clubhouse) instead of the greedy builder.
4. Train the CRF on perception scenes (not OSM) once there are enough labelled blind scenes; the weights now come
   from OSM-quality inputs.
