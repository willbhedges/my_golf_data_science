# pathroute: card-blind hole routing from course structure

Method `pathroute` (`course_data/zero_tap/pathroute/`), results `results/pathroute/{nocard,osm_card}/`
(zero_tap_result/1, `certain` always false; `confidence` = beam posterior mass of the best route).

## Method

1. **Scene** (`scene.py`): greens, tee boxes (+ major axis / elongation), fairways, buildings, water, clubhouse
   (golf=clubhouse, else the biggest building next to a car park, else a car park, else a building, else the green
   centroid) and a **walking graph** from golf=cartpath + highway=path/footway/service/track/cycleway/steps
   (densified to 15 yd, lines joined within 6 yd). Green -> tee walking distance = off-path legs + Dijkstra.
2. **Local models** (`features.py`, `model.py`, gradient-boosted trees fitted on dev labels from truth):
   - hole P(tee t -> green g is one hole): length, fairway cover of the line, fairway linking tee and green,
     tee-axis alignment, greens / far tees / buildings / water under the line, distance ranks;
   - walk P(green g -> tee t is the walk to the next hole): edge distance, path distance, path-connected,
     detour ratio, ranks, clubhouse distances;
   - start (tee of 1 / 10) and end (green of 9 / 18) from clubhouse distance (logistic).
   - **stage 2 (stacking)**: each candidate's stage-1 score against its competitors on the same tee / green
     (out-of-fold within the training courses), plus cross-evidence (a "next tee" that is really the green's own tee,
     walk direction vs the green's approach direction from its best tee).
3. **Joint decode** (`decode.py`): the round is clubhouse -> T1 -> G1 -> walk -> T2 -> ... -> G_n -> clubhouse;
   cost = sum of -log P. The tee of each hole is chosen inside each green -> green step, so pairing and order are
   solved together; beam (4 000 states over (greens used, last green), deduplicated = Held-Karp in the limit)
   picks which greens to use (practice greens drop out). 18-hole loops add end(G9) + start(T10) at the turn.
   27 / 36: greedy loops of 9 / 18 on the remaining greens. Par from the hole length (cuts 225 / 450 yd fitted on
   dev). osm_card adds a per-position card-length term (straight-line length vs back-tee yardage) and card pars.

Diagnostic (dev, 9/18-hole courses): the true route always scores no better than the decoded one, i.e. **0 search
errors / 104 model errors** — all remaining failures are in the local hole / walk probabilities. Stage-1 top-1:
76 % of true greens get a true tee as their best hole tee, 73 % of greens get the true next tee as best walk.

## Numbers (bench.py scorer; dev = 5-fold out-of-fold over courses, test = one run, models fit on all dev)

formed = pairing accuracy (green + tee of one true hole), number = holes numbered right,
holes right / fully right = courses with every hole numbered right (/ and every known par right).

| tier | split | method | formed | number | holes right | fully right |
|---|---|---|---|---|---|---|
| nocard | dev | **pathroute** | 80.4 % | 32.2 % | 9.4 % | 5.6 % |
| nocard | dev | routing_v2 | 59.6 % | 12.5 % | - | 0.0 % |
| nocard | dev | sequence_v3 | 80.1 % | 27.0 % | - | 2.5 % |
| nocard | test | **pathroute** | 78.8 % | 25.9 % | 6.5 % | 2.0 % |
| nocard | test | routing_v2 | 60.3 % | 14.6 % | - | 0.0 % |
| nocard | test | sequence_v3 | 79.9 % | 23.6 % | - | 0.0 % |
| osm_card | dev | **pathroute** | 81.7 % | 70.8 % | 27.5 % | 27.5 % |
| osm_card | dev | routing_v2 | 76.3 % | 69.4 % | - | 20.0 % |
| osm_card | dev | sequence_v3 | 80.7 % | 67.9 % | - | 23.1 % |
| osm_card | test | **pathroute** | 82.1 % | 72.0 % | 23.5 % | 23.5 % |
| osm_card | test | routing_v2 | 73.4 % | 67.3 % | - | 16.3 % |
| osm_card | test | sequence_v3 | 78.3 % | 66.3 % | - | 22.2 % |

Other methods' numbers are from SCOREBOARD.md (same scorer, same splits). Test course failures, nocard: pairing 109,
missed_tee 19, par 7, no_result 5 (no OSM tees), nine_swap 5, start_hole 3; osm_card: pairing 103, missed_tee 8,
no_result 5. By size (test nocard formed / number / holes right): 9: 75 / 30 / 20 %, 18: 80 / 26 / 5 %,
27: 81 / 35 / 0 %, 36: 71 / 22 / 13 %.

Dev ablations (nocard, out-of-fold): stage 1 only, walk weight 1.0: 73.6 / 25.3 / 6.2 / 3.1 %; walk weight 0.5:
75.4 / 25.6 / 5.6 / 2.5 %; walk 2.0: 71.5 / 22.9 / 3.7 / 1.3 %. + stage 2: 80.4 / 32.2 / 9.4 / 2.5 % (par cuts
245/470) -> 5.6 % with par cuts 225/450. Clubhouse weight 2.0 hurts (78.9 / 29.1).

## Honest assessment

- Pairing is still the failure on ~70 % of courses: one wrong hole shifts the numbering of everything after it, so
  holes numbered right (26-32 % nocard) is far below formed (79-80 %). Walk evidence helps (and is what moves
  numbering), but the local walk model alone ranks the true next tee first only 73 % of the time.
- The walking graph is only as good as OSM paths: many courses have no cartpaths mapped, and path distance then
  carries no information beyond straight-line distance.
- The decoder is exact enough (0 search errors on dev), so gains must come from better local evidence (e.g. tee
  complex grouping, dogleg-aware fairway corridors, path continuity along the hole, lidar / imagery).
- No certainty gate: `certain` is false everywhere; confidence is not calibrated.
- Par cuts (2 numbers) and the walk weight were chosen on dev in-sample; the models themselves are out-of-fold.

## Reproduce

```bash
python course_data/zero_tap/pathroute/prep.py --cache C --split all                  # ~15 s, 4 procs
python course_data/zero_tap/pathroute/run.py dev  --cache C --tiers nocard,osm_card --out course_data/zero_tap/results/pathroute
python course_data/zero_tap/pathroute/run.py test --cache C --tiers nocard,osm_card --out course_data/zero_tap/results/pathroute
python -m pytest course_data/zero_tap/pathroute/test_pathroute.py -q
```
OMP_NUM_THREADS=1 is forced in model.py: on a shared box OpenMP oversubscription made the tree fits ~50x slower.

## v2 (`pathroute_v2/`, results `results/pathroute_v2/nocard/` + `summary.json`) — pairing first

Product target: a tee-shot plan needs the right **pairing** (tee complex <-> green) + tee boxes; numbering can come
from one "this is hole 1" tap or a card. v2 optimises pairing and adds a calibrated per-hole pair confidence.

1. **Pair features** (`features2.py`, 24 added to the v1 hole model; same 2-stage GBM): fairway *components*
   (touching fairways unioned) linking tee and green, how many greens / tees that component touches (shared
   fairways), fraction of the component inside the tee-green ellipse, dogleg-aware tee-axis alignment to the
   landing zone (fairway 140-290 yd out), approach direction (fairway 30-140 yd short of the green vs the hole
   line), other greens / tees inside the corridor ellipse, practice cues (driving-range distance, clubhouse
   distance, fairway reach, tees around a green, `inside_course` tag).
2. **Tee complexes** (`complexes.py`): GBM P(two boxes are one hole) on box-pair geometry (dev AUC 0.85), average
   linkage at 0.5. The hole's box set = complex members (+ v1 geometric box rule).
3. **Global constraints in the beam** (`decode2.py`): each green keeps its K=6 best tees; every state carries, per
   candidate pair, the count of already-chosen corridors it **crosses** (1.5 nats each) and whether it **reuses** a
   complex / box set (2 nats; the same box twice is forbidden). Practice greens still drop out of the tour.
4. **Per-hole confidence** (`confidence.py`): logistic calibration (out-of-fold on dev) of hole probability, tee /
   green margins, walk in / out, route confidence and the **min-marginal** (route cost increase when the pair is
   forbidden, beam 800 re-decode). Written as each hole's `confidence`.

Dev ablation (local truth labels, OOF; pairing / courses with all pairs right):
v1 81.9 / 21.0 -> + features 87.9 / 30.6 -> + crossing 88.6 / 32.5 -> + complexes & reuse 90.1 / 41.4.
(Box-set honesty check: complex-only boxes 89.8 vs v1+complex boxes 89.9; primary tee alone in the table below.)
Not helpful: hard crossing (3 nats = 1.5), reuse 4 nats, K=10. Not tried: par-count / total-length priors.

| split | method | paired | paired (primary tee only) | all pairs right | numbered | holes right | fully right | taps to 98 % pair precision |
|---|---|---|---|---|---|---|---|---|
| dev (OOF) | pathroute v1 | 80.4 % | 79.4 % | 20.6 % | 32.2 % | 9.4 % | 5.6 % | 15.3 / course |
| dev (OOF) | **pathroute v2** | **88.4 %** | 86.3 % | **39.4 %** | 28.9 % | 13.1 % | 8.1 % | **4.8 / course** |
| test | pathroute v1 | 78.8 % | 77.8 % | 12.4 % | 25.9 % | 6.5 % | 2.0 % | 14.6 / course |
| test | **pathroute v2** | **86.9 %** | 84.5 % | **35.3 %** | 26.3 % | 9.2 % | 2.6 % | **5.3 / course** (dev threshold 0.912 -> 98.2 %) |

Taps: the app asks the golfer to confirm every hole with confidence < threshold (a confirmed hole is right); true
holes with no predicted hole cost one tap each; v1's only confidence is the route posterior. Test, dev threshold:
98.2 % pair precision at 5.3 taps / 18-ish holes; 16 % of test courses need no tap. Reliability (test): conf
0.98-1.0 -> 99.2 % right (1 092 holes), 0.95-0.98 -> 96.8 %, 0.90-0.95 -> 93.1 %, < 0.5 -> 24 %.

Honest notes: numbering did not improve (dev 32.2 -> 28.9 %; more start_hole / nine_swap failures) — v2 only fixed
pairing; one "hole 1" tap is the intended fix. cross / reuse / complex threshold were picked on dev OOF predictions
(in-sample for those 3 numbers); test was run once. Taps assume no re-decode after a confirmation (re-decoding
with the confirmed pair fixed would likely repair neighbours too — not measured).

```bash
python course_data/zero_tap/pathroute/prep.py --cache C1 --split all
python course_data/zero_tap/pathroute_v2/prep2.py --cache C1 --out C2              # ~40 s
python course_data/zero_tap/pathroute_v2/run2.py --c1 C1 --c2 C2 --out course_data/zero_tap/results/pathroute_v2 --test   # ~13 min
python -m pytest course_data/zero_tap/pathroute_v2/test_pathroute_v2.py -q
```

## v2 confirm-and-resolve + production routing (2026-11-01)

**API** (`pathroute_v2/decode2.py` `decode2(fix=...)` / `apply_fix`, session wrapper `resolve2.Session`): golfer facts
are fixed and the whole route is re-solved: (a) `confirm_pair(N, tee, green)` - "hole N is this tee complex + green"
(pinned to position N on 9 / 18-hole courses, pair-only on 27 / 36; the complex serves only that green, +30 nats so the
tour includes it); `not_a_hole(green)` (practice green); (b) `hole_one(tee)` - step 1 must start at that tee's complex
(fixes start + direction). Facts are JSON-able by OSM id (`to_ids` / `from_ids`).

**Simulated golfer** (`sim2.py`, test split, 153 courses, one run; models fit on all dev, calibration dev OOF): ask
about the lowest-confidence unconfirmed hole, answer from truth, re-solve, repeat; a global stop threshold on the
remaining confidence. No-result courses (no OSM tees) cost one tap per hole. `summary_resolve.json`, `sim2_report.py`.

| policy (test) | pair precision | taps / course mean (median, p90) | no tap | courses with all pairs right |
|---|---|---|---|---|
| no resolve: confirm every hole < 0.899 (v2 estimate) | 98.0 % | **4.8** (3, 11) | 16 % | - |
| resolve, stop at remaining conf >= 0.954 | 98.0 % | 7.7 (5, 18) | 6 % | **69.9 %** |
| resolve, stop at 0.98 | 98.5 % | 10.2 (7, 22) | 2 % | 76.5 % |
| taps until all pairs right (oracle stop): resolve / no resolve | 100 % | 5.4 (2, 13) / 4.6 (2, 13) | 37 / 35 % | 100 % |

Numbering (9 / 18-hole test courses, 2 304 holes): no tap 25.3 % -> **one "hole 1" tap 63.9 %** (31 % of courses
all numbered); at the 98 % resolve stop (confirmations carry their hole number) 88.5 % -> **+ hole-1 tap 94.1 %**
(74 % of courses all numbered).

Honest: re-solving does **not** save pair taps - it costs more (7.7 vs 4.8 at 98 %). The calibrator was fit on free
decodes. After a fix, the route confidence / min-marginal features shift, so the remaining holes stay below threshold
and keep being asked. Fixing it needs a calibrator fit on constrained re-solves (simulate on dev OOF). Resolve does
pay for **numbering**: 25 % -> 94 % with the confirmations plus one hole-1 tap. Two sim bugs were fixed before this run
(double-green answers ping-ponging; two confirmed holes sharing a tee complex blanking each other in `apply_fix`).

**Production** (`pathroute_v2/live2.py`, `platform/stage_select.py` method `pathroute_v2`): features from the live OSM
(holes hidden), OSM golf=hole ways fixed as confirmed pairs (so only the missing holes are routed), calibrated
per-hole `confidence` (status `check` < 0.95), `confirm` = ask order + facts (`pathroute_confirm/1`, re-solve with
`live2.route(fc, course, n, fix=facts)`). Used by `package.py` for `"card": "none"` and as the `mapped_nocard`
default; fallbacks structure > routing v2 > geometry; request `"pathroute": false` restores the old choice. With a
real card the card tiers keep v2+structure (pathroute ignores the card; `"hole_method": "pathroute_v2"` forces it).
Model: `pathroute_v2/model_v2.pkl.gz` (1.9 MB, sklearn 1.9.1 pickle; refit: prep.py + prep2.py caches, then
`sim2.py --fit-out`, which also writes the calibration). Card-blind effect: CARDBLIND.md "Routing: pathroute_v2".

```bash
python course_data/zero_tap/pathroute_v2/sim2.py --c1 C1 --c2 C2 --fit-out M.pkl --json sim.json --jobs 4   # ~5 + 20 min
python course_data/zero_tap/pathroute_v2/sim2_report.py sim.json --out summary_resolve.json
```

## Confirm taps: fix-aware calibrator + re-solve in the browser (2026-11-01)

**Calibrator on constrained re-solves** (`pathroute_v2/calib_resolve.py`): dev, 5-fold OOF models; each dev course is
played by the sim2 golfer (old calibrator picks the question, up to 18 taps) and every state's unconfirmed holes give a
row: the old features of the constrained decode + `frac_fixed`, `nb_fixed` (confirmed route neighbours), `changed`
(pair not in the free decode), tee / green margins in the fixed cost matrix (`confidence.Calib2`, logistic). 160 dev
courses, 27 192 rows. Dev OOF log-loss after a fix 0.138 (old) -> **0.130**; on free decodes it is worse (0.230 vs
0.195, the old one in-sample), so production keeps `calib` for the free decode and uses `calib_fix` once any fact is
set (`model_v2.pkl.gz`, `resolve2.Session(calib_fix=...)`). Note: the old calibrator was already roughly calibrated
after fixes (0.95-0.98 bin: 96.6 % right), so calibration was not the main cause.

**Test, one run (sim2, 149 courses, Calib2 for every re-solve)** — `results/pathroute_v2/summary_resolve_calib2.json`:

| policy (test) | taps to 98 % pair precision, mean (median, p90) | courses all pairs right at that stop | taps to all pairs right (oracle stop) |
|---|---|---|---|
| no resolve (confirm every hole < thr) | 4.72 (3, 12) | - | 4.46 |
| resolve, old calibrator (sim_v3) | 7.72 (5, 18) | 69.9 % | 5.44 |
| **resolve, Calib2** | **7.08** (5, 17) | **76.5 %** | 5.27 |

Numbering (9 / 18 holes) at the 98 % stop + hole-1 tap: 94.1 % of holes, **80 % of courses** all numbered (74 % before).
The target (resolve needs fewer taps than no resolve) is **not met**. Diagnosis: re-solving after a fix makes a
previously right hole wrong in 170 of 2 630 sim steps (sim_v3; 58 of them on 27 / 36 courses with pair-only facts, so
it is not only the number pins), and even with an oracle stop resolve needs more taps (5.3 vs 4.5). Trying the
complex blanking of `apply_fix` softer halved those breakages on 27 dev courses but did not lower taps (3.15 vs 2.96,
noise level); not adopted. Next: a sticky re-solve (bonus for the previous decode's confident pairs) so an answer only
moves the holes it implicates. Resolve still pays for numbering and for "all pairs right".

**In the browser**: `course_data/app/pathroute_engine.js` ports decode2 (beam, pins, hole-1 tee, crossings / reuse,
reject facts), the min-marginals, the features and both calibrators; `export_js.py` writes the per-course inputs
(pathroute_decoder/1, app SCHEMA.md). Parity (`course_data/app/test_pathroute.js`): 24 test courses (3 x 27 / 36,
5 x 9, 16 x 18) x 4 fact sets (none; two confirmed pairs incl. a correction; reject + practice green; hole-1 tee) =
93 decodes, holes identical, confidences within 1e-13. ~0.9 s per full solve in node (one 4000 beam + one 800 beam
per hole); the page shows the new pairing after the first decode and fills the confidences in over the next frames.
The final route argsort is now stable (ties -> first state) so both sides agree.

## Sticky re-solve + confirm-tap policies (2026-11-02)

**Goal**: a re-solve after a golfer answer should save pair taps vs no re-solve (test 4.7 at 98 % pair precision).
**Not met.** The best re-solve policy ("local", below) is close to no re-solve on dev (4.94 vs 4.74 taps) but worse on
test (6.12 vs 5.22 simulated / 4.78 step-0 estimate). It is better than the old re-solve everywhere (test 7.71 -> 6.12
taps) and keeps part of the re-solve gains (all pairs right 53 -> 63 %, numbering 86.5 -> 88.7 %). Shipped as the (since superseded: "Every hole right" below)
re-solve default; for fewest pair taps, no re-solve is still best.

**What changed** (`pathroute_v2/resolve2.py`, `decode2.py`, `run2.py`; JS `course_data/app/pathroute_engine.js`):
- **Sticky re-solve** (`resolve2.STICKY`, default `pin=0, pin_w=30`): on each re-solve the previous solve's unconfirmed
  pairs get a bonus `w` nats (`fix["sticky"] = [(tee, green, w)]`, applied last in `apply_fix`; `w = pin_w` once the
  pair's confidence >= `pin`, else `alpha * conf`), so only the holes the new fact implicates move. A pair that
  survives keeps its previous confidence and its min-marginal is skipped (`decode_course(mm_skip=...)`, faster);
  moved pairs get the fix-aware calibrator (`calib_fix`). Options kept for experiments: `alpha`, `cap` (cap the
  confidence of a moved pair), `boxes` (a kept pair keeps its previous box set; no effect on dev).
- **Answer flow** (the shipped default): "yes" -> `Session.confirm_yes(i, number)` (confirmed, no re-solve);
  "not a hole" -> `Session.drop_hole(i)` (the hole leaves the route, no re-solve); only a **correction** (a different
  tee for the green) re-solves. Same API in JS: `confirmYes`, `dropHole`, `confirmPair` + `solve()` / `begin()`.
- **Decoder bug fix** (`decode2.decode2`, JS `decode2`): a golfer-confirmed tee is never handed out as another hole's
  box. Before, a confirmed tee swallowed into a neighbour's box set made its green (whose column is blanked for every
  other tee) undecodable, so on 27 / 36-hole courses the last loop failed and 9 holes vanished (10 of 157 dev courses
  under re-solve, +9 taps each).

**Dev** (157 courses, out-of-fold hole / tee-pair models; calibrators of model_v2 are in-sample on dev; `sim3.py`,
golfer = sim2's; "right->wrong" = steps where the count of wrong + missing holes went up):

| policy (dev) | taps to 98 % mean (median, p90) | all pairs right at stop | taps to all pairs right (oracle) | right->wrong steps |
|---|---|---|---|---|
| no re-solve (confirm in confidence order) | **4.74** (3, 12) | 55 % | 8.0 | 0 |
| re-solve after every answer (old) | 11.5 (10, 20) | 80 % | 4.9 | 160 / 2 596 |
| sticky (alpha 3 / 10), every answer | never reaches 98 % (97.4 % at 0.999) | - | 5.1 / 4.9 | 111 / 107 |
| sticky alpha 10, no re-solve after "yes" | 6.64 -> 6.45 with the box fix (4, 16) | 76 % | 4.7 | 62 |
| same, ask by (1 - conf)(1 + 0.5 unconfirmed neighbours) | 6.09 (4, 16) | 76 % | 4.9 | 65 |
| same, pinned pairs only (alpha 30) | 6.19 (4, 15) | 75 % | 4.9 | 66 |
| **local: pin every previous pair, re-solve only on a correction** | 4.94 (3, 14) | **65 %** | 5.6 | 58 |
| same, alpha 30 / alpha 10 | 4.93 / 5.07 | 64 / 63 % | 5.6 | 60 / 56 |
| local, confirmations without the hole number (no position pins) | 5.11 | 64 % | 5.5 | 58 |

Why re-solving costs taps: (1) after "not a hole" the re-solve has to fill the route again and usually picks another
wrong green (low confidence -> asked again), where no re-solve just drops the hole and the golfer adds the missing one
(one tap); (2) re-solves after a "yes" pin the number, re-order the tour and move right holes (the decoder hands box
sets out in tour order, so even an unchanged pair can lose its true tee box); (3) on courses with a bad route
(e.g. exmoor_il) one correction cascades. At the same stop threshold the old-style hybrid asked +84 questions to save
53 golfer-added holes and still had +17 wrong pairs. Calibration of moved pairs was fine (0.98-1.0 bin: 99.9 % right).

**Test, one run** (`sim3.py --split test`, 149 simulated + 4 no-result courses = 153, model_v2;
`results/pathroute_v2/summary_sticky.json`):

| policy (test) | taps to 98 % mean (median, p90) | stop threshold | all pairs right at stop | numbered at stop + hole-1 tap (holes / courses all numbered) | taps to all pairs right (oracle) | right->wrong steps |
|---|---|---|---|---|---|---|
| no re-solve, simulated (asks in confidence order) | **5.22** (3, 13) | 0.899 | 52.9 % | 86.5 % / 45.9 % | 8.22 | 0 / 2 679 |
| no re-solve, step-0 estimate (`taps_to_precision`) | 4.78 (3, 11) | 0.899 | - | - | - | - |
| re-solve after every answer (old, + box fix) | 7.71 (6, 18) | 0.954 | **77.1 %** | **95.0 % / 79.3 %** | **4.83** | 141 / 2 622 |
| **local sticky, re-solve only on a correction (default)** | 6.12 (4, 14) | 0.910 | 63.4 % | 88.7 % / 57.0 % | 6.25 | 58 / 2 660 |

The simulated no-resolve number (5.22) is above the step-0 estimate (4.78) because the simulated golfer's answers are
counted step by step (a "not a hole" drops the hole and adds a miss tap; hand-placed tees); the brief's 4.7 is that
estimate. Earlier Calib2 run of the old re-solve: 7.08 (same policy without the box fix; run-to-run difference from the
sim changes, not re-run). Per-policy p90s are high (13-18) on all policies: the long tail is 27 / 36-hole courses and
bad routes.

**Parity** (`course_data/app/test_pathroute.js`, fixtures regenerated by `export_js.py`): 24 test courses, 93 decodes
(with the box fix) + 140 sticky session solves (free -> `confirm_yes` -> correction -> `drop_hole` -> correction ->
"not a hole" + re-solve): 0 failing, holes / boxes identical, confidences within 1.1e-13. `test_route_ui.js` OK.

**Not done / caveats**: the app (`lib_play.js`) rebuilds a fresh `Session` from the answer log and solves once, so it
gets the stateless (non-sticky) re-solve; to use the sticky flow it must keep the `Session` across answers and call
`confirmYes` / `dropHole` / `confirmPair` + `begin()` (an app change, not made here). `live2.route(fix=...)` (server)
is stateless too. The calibrators were not refit for the sticky flow. Dev numbers use in-sample calibrators.

```bash
python course_data/zero_tap/pathroute_v2/sim3.py --c1 C1 --c2 C2 --split dev --folds FOLDS.pkl --no-h1 \
    --policy local:resolve=fix --policy never:resolve=never --json dev.json --jobs 3   # FOLDS = calib_resolve fold models
python course_data/zero_tap/pathroute_v2/sim3.py --c1 C1 --c2 C2 --split test --policy local:resolve=fix --json t.json
```

## Every hole right: P(all pairs right) stop + re-solve on corrections only (2026-11-02; superseded: "Fully right" below)

**Goal** (coordinator): every hole right (all pairs right + numbered) in the fewest taps, not 98 % pair precision.
**Shipped until "Fully right"** (`resolve2.POLICY` = `PathRoute.POLICY`, superseded the sticky "local" default above; the stop and ask order still ship):
- **stop**: P(every decoded pair right) = **product of the unconfirmed holes' calibrated confidences** >= **0.9**
  (`Session.p_all`). It is calibrated on dev states (plain re-solve: P 0.90-0.95 -> 96.7 % all right, 0.95-0.98 ->
  97.5 %, 0.98-1 -> 99.6 %). A learned course-level calibrator (`stop4.py` "learn": logistic on sum / min log conf,
  holes < 0.9 / 0.99, confirmed fraction, missing holes; dev 5-fold OOF) only moved along the same taps-vs-all-right
  curve (e.g. 8.3 taps / 87.5 % vs product 9.4 / 91.2 %), so the product ships (no fit, nothing to export).
- **ask**: the lowest-confidence unconfirmed hole (< 0.999) - under the product this is the largest gain in P(all right)
  per tap ((1 - c) / c); `Session.need()` = the holes still to ask, in order, until P >= target (the app's "N holes
  still need a look"). The neighbour-weighted order (`ask=voi`) was not better in the sticky runs; not re-run.
- **answers** (`Session.answer`): a correction (other tee / green, "no") re-solves the whole route **plain** (no sticky
  bonus); a "yes" confirms without a re-solve (its number pins at the next re-solve); **"not a hole" drops the hole
  without a re-solve** (the next correction's re-solve refills the route; a still-missing hole = one golfer tap).

**Metric note**: "all pairs right" here counts golfer-added missing holes as right (the golfer places them; one tap
each, counted in the taps, as in every taps number above). The earlier tables required `miss == 0`, which penalises
no re-solve (it never refills a dropped hole): under the fair count the no-re-solve oracle is as good as re-solve
(dev 4.49 vs 4.59 taps, test 5.05 vs 4.67), so the 8.22 "no re-solve oracle" above is that artefact. Re-solving
after every answer also breaks right routes: once all pairs are right, only 60 % (dev) / 62 % (test) of courses stay
all right to the end of the trajectory; plain re-solve tops out at 88-90 % courses all right, whatever the stop.

**Dev** (157 courses + 3 no-result, OOF hole / pair models, `sim3.py --no-h1`, `stop4.py`; taps = answers + golfer-added
holes; "taps at X %" = fewest mean taps of any P threshold with >= X % of courses all pairs right; plain / never from the
sticky agent's dev1 run (before the box fix), local from dev4):

| policy (dev) | taps at 75 / 80 / 85 / 90 / 95 % all right | P >= 0.9: taps mean (median, p90) / all right | P >= 0.95 | oracle |
|---|---|---|---|---|
| no re-solve (confirm in confidence order) | 4.94 / 5.86 / 7.24 / 9.21 / 12.53 | 10.7 (10, 18) / 91.9 % | 13.4 / 95.6 % | 4.49 |
| re-solve after every answer (plain) | 6.06 / 7.39 / 8.78 / 15.26 / - | 9.41 (8, 18) / 87.5 % | 11.6 / 88.1 % | 4.59 |
| local sticky (previous default) | 5.12 / 5.76 / 7.59 / 9.56 / 12.84 | 11.0 (10, 19) / 92.5 % | 13.5 / 95.6 % | 4.77 |
| plain re-solve, yes without re-solve, not-a-hole re-solves | 4.79 / 6.80 / 7.47 / 9.73 / - | 8.99 (8, 18) / 88.1 % | 11.3 / 90.0 % | 4.16 |
| **plain re-solve on corrections only, not-a-hole dropped (shipped)** | **4.66 / 5.47** / 7.42 / **8.81** / 13.49 | **9.38 (8, 18) / 91.2 %** | 11.6 / 93.1 % | 4.43 |

The shipped policy has the lowest curve from 75 to 90 % all right (no re-solve is a close second and the best above
93 %); it keeps the re-solve's numbering (confirmations + re-solve) that no re-solve lacks (test below).

**Test, one run** (153 courses = 149 simulated + 4 no-result; shipped policy simulated once with the hole-1 decode,
`sim3.py --split test --policy plain:resolve=fix`; the other three are the sticky agent's test trajectories re-scored
with the same stop; `results/pathroute_v2/summary_allright.json`). "fully right" = all pairs right and, on 9 / 18-hole
courses, every hole numbered right after one more "this tee is hole 1" tap (not counted in taps):

| policy (test), stop P >= 0.9 | taps mean (median, p90) | all pairs right | fully right (+ hole-1 tap) | holes numbered | P >= 0.95: taps / pairs / fully | oracle taps |
|---|---|---|---|---|---|---|
| no re-solve | 11.58 (10, 19) | **93.5 %** | 61.4 % | 91.4 % | 14.14 / 96.1 / 70.6 % | 5.05 |
| re-solve after every answer (plain) | **9.66** (8, 18) | 85.0 % | **84.3 %** | **96.4 %** | 11.84 / 86.9 / **86.3 %** | **4.67** |
| local sticky (previous default) | 11.85 (10, 20) | 91.5 % | 79.1 % | 94.6 % | 14.17 / 94.1 / 83.0 % | 5.07 |
| **shipped: re-solve on corrections only** | 9.93 (8, 18) | 89.5 % | 77.1 % | 95.2 % | 12.19 / 90.8 / 79.7 % | 4.70 |

Taps at a given % of courses with all pairs right (test): shipped 6.03 / 6.75 / 8.03 / 10.22 at 75 / 80 / 85 / 90 %,
no re-solve 6.33 / 7.44 / 8.52 / 10.13, plain 6.73 / 7.75 / 9.66 / - (never reaches 90 %), local 6.24 / 7.55 / 8.92 / 11.85. The
old 98 %-precision stop of the shipped policy would stop at 5.05 taps.

**Honest assessment**: on pairs the shipped policy holds its dev advantage up to 85 % all right (test) and ties no
re-solve at 90 %. But on the product metric (pairs **and** numbers after the hole-1 tap) re-solving after every
answer is better on test (84.3 vs 77.1 % fully right at fewer taps): the hole-1 tap re-solves the route, and a route
whose "yes" answers were never re-solved breaks or mis-numbers more often then. **Dev numbering was not measured**
(the dev runs with the hole-1 decode were cut for time on the shared box), so this was not a dev decision; the test
result is one run and the default was not changed after seeing it. Next: dev run with the hole-1 decode for
`plain` vs `plain:resolve=fix` (and re-solving after a "yes" only once the hole-1 tee is set); switching is
`POLICY yes="solve", not_hole="solve"` (Python and JS read the same keys; an exported `policy` overrides). The gap
between any stop (~10 taps at P 0.9) and the oracle (~4.7) is the confidence: at the first all-right state the median
P(all right) is only 0.59 (dev), so certifying "every hole right" costs ~5 extra taps whatever the order.

**App** (`course_data/app/lib_play.js`): one `PathRoute.Session` per course is kept across answers (`LPR`); a new
answer applies only itself (`lpRouteApply` -> `Session.answer`: a "yes" / "not a hole" is instant, a correction /
"no" / hole-1 tee re-solves, confidences fill in over the next frames); a different log (another golfer's answers
merged in) replays from scratch (one decode per re-solving answer, confidences for the last only). The holes asked
are `Session.need()`; "Routing is X % sure every hole is right" shows P(all right). Engine: `POLICY`, `pAll`, `need`,
`askAll`, `answer`; `step()` maps the confidences onto the holes by pair (answers between `begin` and the last step
keep their effect). An exported record's `sticky` is ignored (plain re-solve) unless `policy.sticky` is set.

**Tests**: `test_pathroute.js` 24 courses, 233 cases (69 decodes with facts + 140 policy session steps: holes, boxes,
conf, P(all right), the ask list and whether each answer re-solved), 0 failing, max diff 1.1e-13 (fixtures regenerated
by `export_js.py`); `test_route_ui.js` OK (asks every hole via `policy.target` 0.99999; B's strip now waits for the
render after the last step); `test_lib_play.js` OK (10 courses x 2 widths, 684 screens); `pytest pathroute_v2` 11
passed, 1 skipped. `out/index.html` / `aim_caddie.html` relinked (`build_app.py --relink`). Not done: `live2.route`
(server) stays stateless (= plain re-solve with all facts); the calibrators were not refit.

```bash
python course_data/zero_tap/pathroute_v2/sim3.py --c1 C1 --c2 C2 --split dev --folds FOLDS.pkl --no-h1 \
    --policy plain:resolve=fix --policy plain:resolve=no --json dev.json --jobs 3
python course_data/zero_tap/pathroute_v2/stop4.py eval dev.json --targets 0.9,0.95          # dev: learned stop OOF
python course_data/zero_tap/pathroute_v2/sim3.py --c1 C1 --c2 C2 --split test --policy plain:resolve=fix --json t.json
python course_data/zero_tap/pathroute_v2/stop4.py eval t.json --split test
```

## Fully right: re-solve after every answer + hole-1 tee first (2026-11-02, shipped default)

**Metric** (product): "fully right" = every decoded pair right (golfer-added missing holes count, one tap each) **and**,
on 9 / 18-hole courses, every hole numbered right after one "this tee is hole 1" tap (not counted in taps, in every
row). The policy above was chosen on pairs only and dev numbering was never measured; this is the dev decision.

**Dev** (157 courses out-of-fold + 3 no-result, `sim3.py --h1-at 0.8,0.85,0.9,0.95,0.98`: the hole-1 decode at the
first state reaching each P(all) target and at the last state, which is all `stop4.stop_eval` reads at those
targets; `results/pathroute_v2/summary_fullyright.json`). `plain` = re-solve after every answer (yes / correction /
not a hole); `resolve=fix` = the policy above (yes / not a hole without a re-solve); `h1=first` = the true hole-1 tee
is fixed and the route re-solved before the first hole question, `h1=last` = the hole-1 tap after the stop:

| policy (dev) | stop | taps mean (median, p90) | all pairs right | **fully right** | holes numbered | oracle taps |
|---|---|---|---|---|---|---|
| re-solve on corrections only, h1 last (was shipped) | P >= 0.9 | 9.38 (8, 18) | **91.2 %** | 77.5 % | 93.7 % | 4.43 |
| | P >= 0.95 | 11.64 (11, 18.1) | 93.1 % | 83.8 % | 94.8 % | |
| re-solve after every answer, h1 last | P >= 0.9 | 8.79 (8, 18) | 86.9 % | 84.4 % | 92.2 % | 4.38 |
| | P >= 0.95 | 11.13 (10, 19.1) | 88.1 % | 88.1 % | 93.2 % | |
| **re-solve after every answer, hole-1 tee first (shipped)** | **P >= 0.9** | **8.57 (7, 18)** | 86.9 % | **85.0 %** | 92.5 % | **4.20** |
| | P >= 0.95 | 10.95 (10, 19.1) | 88.7 % | 88.1 % | 93.0 % | |
| re-solve on corrections only, hole-1 tee first | P >= 0.9 | 9.17 (8, 18) | 91.2 % | 78.1 % | 92.3 % | 4.34 |
| | P >= 0.95 | 11.49 (11, 19.1) | 93.1 % | 82.5 % | 93.3 % | |

(Other stops, dev fully right / taps: every answer + h1 first 71.9 % / 6.48 at P 0.8, 78.1 % / 7.29 at 0.85, 89.4 % /
13.68 at 0.98; corrections only + h1 last 66.9 / 7.07, 72.5 / 8.07, 89.4 / 14.31. No policy passes 89.4 % fully
right on dev: the re-solve tops out there.)

**Decision (dev only)**: re-solving after every answer is better on fully right at every stop (84.4 vs 77.5 % at
P 0.9 with 0.6 fewer taps; 88.1 vs 83.8 % at 0.95), as test hinted: a route whose "yes" answers were never re-solved
breaks or mis-numbers when the hole-1 tap finally re-solves it, while "corrections only" keeps more pairs right
before that tap (91 vs 87 %). Asking the hole-1 tee **first** is a small further gain (0.2 fewer taps at the same or
+0.6 pt fully right, oracle 4.20 vs 4.38) - one course in 160, within noise, but never worse and free (the app
already had the question). Stop P >= 0.9 is kept: 0.85 -> 0.9 buys +6.9 pt fully right for 1.3 taps, 0.9 -> 0.95
only +3.1 pt for 2.4 taps. Shipped: `POLICY = {target: 0.9, cap: 0.999, yes: "solve", not_hole: "solve",
sticky: None, h1: "first"}` (Python `resolve2.POLICY` = JS `PathRoute.POLICY`; `Session.need_hole1()` /
`needHole1()` = 9 / 18-hole course with no hole-1 tee yet).

**Test** (153 = 149 simulated + 4 no-result; not used to choose). The shipped policy was simulated once after the dev
decision (`sim3.py --split test --policy plain:h1=first`); the other rows are the runs of "Every hole right":

| policy (test), stop P >= 0.9 | taps mean (median, p90) | all pairs right | fully right | holes numbered | P >= 0.95: taps / pairs / fully |
|---|---|---|---|---|---|
| **re-solve after every answer, hole-1 tee first (shipped)** | **9.41 (8, 18)** | 85.0 % | **84.3 %** | **96.5 %** | 11.64 / 87.6 / **86.9 %** |
| re-solve after every answer, h1 last | 9.66 (8, 18) | 85.0 % | 84.3 % | 96.4 % | 11.84 / 86.9 / 86.3 % |
| re-solve on corrections only, h1 last (was shipped) | 9.93 (8, 18) | 89.5 % | 77.1 % | 95.2 % | 12.19 / 90.8 / 79.7 % |

Test agrees with dev: the same fully right as h1 last at 0.25 fewer taps, +7 pt fully right over the previous
default. Honest limits: the h1-first gain is small on both splits; the simulated golfer always knows the hole-1 tee
(the app lets the golfer skip it, "Not now"), and on 27 / 36-hole courses fully right = all pairs right (no hole-1
tap is simulated).

**App** (`lib_play.js`): every answer re-solves (`Session.answer` returns true for a "yes" / "not a hole" too, so the
log replay runs one decode per answer); "First: which tee is hole 1?" is shown above the hole question on every 9 /
18-hole course until answered or skipped (`needHole1()`; before, only while some hole still needed a look, so a route
already at P >= 0.9 never asked it), not blocking the hole question. `out/index.html` / `aim_caddie.html` relinked
(JS only; the course-index blob kept as committed).

**Tests**: `test_pathroute.js` 24 courses, 246 cases (69 decodes with facts + 153 policy session steps, now ending
with the hole-1 tee on 9 / 18-hole courses and checking `needHole1`), 0 failing, max diff 1.1e-13 (fixtures
re-exported by `export_js.py`); `test_route_ui.js` OK (hole-1 tee first, then "Yes"); `test_lib_play.js` OK (10
courses x 2 widths, 572 screens); `pytest pathroute_v2` 12 passed, 1 skipped.

```bash
python course_data/zero_tap/pathroute_v2/sim3.py --c1 C1 --c2 C2 --split dev --folds FOLDS.pkl \
    --policy plain:resolve=fix --policy plain --policy plain:h1=first --policy plain:resolve=fix,h1=first \
    --h1-at 0.8,0.85,0.9,0.95,0.98 --json dev.json --jsonl --jobs 4      # ~17 + 18 min on 4 shared cores
python course_data/zero_tap/pathroute_v2/sim3.py --c1 C1 --c2 C2 --split test --policy plain:h1=first --json t.json
python course_data/zero_tap/pathroute_v2/stop4.py eval t.json --split test          # pp rows = the table
```
