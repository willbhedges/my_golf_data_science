# Joint routing: one constrained optimisation per course (UNFINISHED, stopped early on request)

Status 2026-11-09: **work in progress, stopped after the first dev runs.** Code is new and self-contained in
`course_data/zero_tap/joint/`; nothing in the default pipeline calls it. **No test-split number was ever run**
and no weights were tuned (the first tuning job was killed before it wrote anything). Every number below is
**dev**, local models out-of-fold by state, default weights, from the quick label check in `run.py`
(bench tolerances via `bench.Matcher`, not yet the official `bench.score_course`).

## Formulation (implemented)

No agent / LLM in the per-course path: candidates -> three small tree models -> one beam / DP solve.

* **Candidates** (`cands.py`), one structure for every detection source: `from_scene` (blind perception scene,
  what an unmapped course has), `from_truth` (true hole endpoints, shuffled, numbers hidden: isolates routing from
  detection), `from_osm` (OSM green / tee polygons, holes hidden; written, **never run**).
* **Play length with doglegs** (`feats.play_length`): tee -> centreline of the fairway that leads to the green ->
  green. Against true hole-line length on dev (truth source): straight MAE 11.0 yd / p90 30 yd -> 7.0 / 14.5.
* **Local evidence** (`models.py`, LightGBM, dev only, OOF by state): P(hole t->g), P(walk g->next tee),
  P(loop start | clubhouse, car park), P(loop end). Dev OOF AUC: hole 0.950 / walk 0.962 (truth source),
  0.953 / 0.964 (scene).
* **Cost of a routing** (`solve.py`): sum over positions of hole cost + **card term per position** (negative
  log-likelihood ratio of play length - card yardage of hole i; best tee set first, then a second pass with the
  course's one best-fitting tee set) + walk to the next tee (at a loop turn: min(walk, end + start at the
  clubhouse), so single-loop and two-loop courses both fit) + start / end + crossing count; every green and tee
  complex used at most once; detection confidence as log-odds.
* **Missing detections**: a hole may take a *virtual tee* or be *missing* at a fixed cost, so the rest of the
  numbering survives; `propose.py` places the missing piece from the card yardage (marked `virtual`).
  Written, **not measured** (how often a proposal lands within tolerance is unknown).
* **Search**: beam over positions, state (greens used, tees used, last green) = Held-Karp in the limit.
* **Confidence**: `solve.margins` = per-hole min-marginal (cost gap to the best routing that puts another green
  at that position). Implemented; **the calibration (gap -> P(course right), dev threshold, coverage) is not done.**
* **One golfer answer**: `fix={0: tee}` pins the first tee and re-solves (implemented, measured below).

## Numbers measured so far (dev only, default weights, untuned)

| detections | card | answers | courses | holes numbered right | courses with every hole right |
|---|---|---|---|---|---|
| truth endpoints | web card | 0 | 133 | 84.5 % | 59.4 % |
| truth endpoints | web card | 0, K=18 beam=4000 | 133 | 86.8 % | 69.2 % |
| truth endpoints | web card | first tee | 133 | 86.8 % | 63.2 % (K=6) |
| truth endpoints | none | 0 | 160 | 24.6 % | 11.9 % |
| truth endpoints | none | first tee | 160 | 46.1 % | 25.0 % |
| perception scene | web card | 0 | 66 | 67.8 % | 13.6 % |
| perception scene | web card | first tee | 66 | 72.4 % | 16.7 % |
| perception scene | none | 0 | 77 | 11.9 % | 0 % |
| perception scene | none | first tee | 77 | 23.3 % | 2.6 % |

"Web card" = golfify / OpenGolfAPI / club site only. The bench's `osm-derived` card is the truth and is never
used here (earlier "card" rows in UNMAPPED.md include it for 11 dev / 14 test courses, so they are not like for
like). For reference, UNMAPPED.md's existing dev numbers on scenes: sequence_v3 card 78 % numbered / 35 % courses
(in-sample formation pairs, optimistic); test 65 % / 20 %. **So on real detections this solver is not yet better
than what exists; I have no evidence that it is.** No before / after headline table can be claimed.

What the dev diagnostics showed (truth source, 18-hole courses):

* With a card, 4 of the worst courses are cards that do not match OSM at all (median residual 25-55 yd; about 6 %
  of dev web cards correlate < 0.8 with the true lengths). Unfixable by routing; the confidence must catch them
  (card residual is already a feature in `run.py`).
* Candidate pruning was losing the true pair in 23 / 125 courses at K=6 (hole model too weak to prune on); K=18
  raised fully-right 59 -> 69 %. 7-14 search errors at beam 1500.
* Without a card, pairs are 90.6 % right but only 12 % of courses are numbered right: order errors (32), nine
  swaps (10), start shifts (7). A nine swap is not decidable without a card; the first-tee answer only gets to 25 %,
  so the walk model, not the start, is the weak part.
* Scene source: every hole has both a green and a tee candidate in 61 % of dev courses, which caps "all 18 right"
  with real detections near there unless virtual proposals work.

Runtime (4 shared CPUs, 1 process per course): solve incl. second pass about 0.5 s per course at beam 1500
(133 courses in 22 s on 3 processes); beam 4000 / K=18 roughly 2-3x that. Margins add up to 18 small re-solves
(not timed). Feature preparation about 0.4 s per course. Model fitting (offline, once) 1-2.5 min.

## Not done

Weight tuning (`tune.py` written, never completed a run); confidence calibration and coverage; official
`bench.score_course` scoring and result files; any test-split run; scene+card failure inspection and renders;
the OSM-polygon source; comparison against pathroute / sequence_v3 on identical web-card courses; 27 / 36-hole
facilities (handled as loops of 9, unchecked). `params.json` holds only the K / beam setting for the truth source.

## Resume

```bash
C=/tmp/joint_cache
python course_data/zero_tap/joint/prep.py --source truth --out $C      # ~45 s each
python course_data/zero_tap/joint/prep.py --source scene --out $C
python course_data/zero_tap/joint/run.py scores --cache $C --source scene        # fits + caches model scores
python course_data/zero_tap/joint/run.py eval --cache $C --source scene --split dev --card 1 --answer 0
python course_data/zero_tap/joint/tune.py --cache $C --source scene --card 1     # dev only; writes params.json
python -m pytest course_data/zero_tap/joint/test_joint.py -q
```

Next, in order: (1) tune on dev, raise K for the scene source and add card-fit to candidate selection;
(2) look at scene+card dev failures (render) to split detection vs routing; (3) calibrate confidence from
margins + card residual on dev OOF; (4) test once, scored with `bench.score_course`, web-card courses only.
