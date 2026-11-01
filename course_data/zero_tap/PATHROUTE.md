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
