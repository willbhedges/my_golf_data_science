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
taps) and keeps part of the re-solve gains (all pairs right 53 -> 63 %, numbering 86.5 -> 88.7 %). Shipped as the
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
