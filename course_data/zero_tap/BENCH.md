# Zero-tap benchmark (workstream D)

One scoreboard every zero-tap workstream reports against. Latest numbers: [SCOREBOARD.md](SCOREBOARD.md)
(machine-readable: `scoreboard.json`, per course: `scores/<method>__<tier>.json`). Short status: [STATUS.md](STATUS.md).

## The benchmark set

`benchmark.json` (`bench_set.py`, offline, deterministic) lists every candidate course; `in_bench: true` marks the
ones scored. Per course: state, Census region, split, facility size `kind` (9 / 18 / 27 / 36), OSM mapping
(`greens_mapped`, `tees_mapped`, `par_known`), the web scorecard (`card`: source, hole count, tee sets, whether it
fits the course), and file paths (OSM, resolve output, card, NAIP segment model, lidar pads, perception scene,
truth).

Sources (reused, not copied): `generalize/validation_set.json` (82), `structure/sets.json` (131), and this
benchmark's own seeded selection over 24 more states (`fetch.py`, `selection.json`, `data/<slug>/`).

**Split by state** (`state_split.json`, frozen): **dev** = the 12 generalize tuning states (CA GA IL KY MA ME MN MS
NH UT WI WY) + 11 seeded new states; **test** = the 12 structure held-out states (AR CT DE IA ID MO NC NE NJ NV PA
WA) + 13 seeded new states. Exception: the 31 `validation_set` test courses (dev states) stay in test.
**Never tune, fit, calibrate or look at per-course failures on test.** Report test once per method version.

**Versions.** v0 = the first 161 courses (dev 77 / test 84), frozen in `bench_v0.json`; every manifest row carries
`v0: true/false`. `bench.courses("dev", version="v0")` gives exactly the v0 dev split that earlier work fitted on.
Later versions only add courses (from new states, so a v0 course never changes split; `bench_set.py` refuses to
build otherwise). The scoreboard also reports the v0-only subset for comparison with earlier boards.

**Truth** (`truth/<slug>.json`, `truth/1`, built by `truth.py`): the OSM `golf=hole` ways. A course is in the
benchmark only when its refs are exactly 1..N (or 1..9 x 3/4, 1..18 x 2, 1..18 + 1..9), every line is 50-750 yds
and >= 90 % of lines end on a mapped OSM green. Per hole: line, tee (line start), green (OSM green centroid +
equal-area radius, else the line end), nearby OSM tee ids, par (OSM tag, else the card when its hole count fits).
Hand checks against NAIP (`osm_check.py`, `OSM_CHECK.md`) are stored in the truth file (`hand_check`); a course
whose OSM was found wrong is dropped.

## Tiers (what a method may see)

| tier | inputs |
|---|---|
| `osm_card` | OSM greens / tees / fairways / everything else, with every `golf=hole` / `golf=pin` way and every golf ref / name / par removed (`truth.hide`), + a scorecard |
| `unmapped_card` | no OSM `golf=*` feature at all (`truth.strip_golf`: boundary, buildings, car parks, paths, water, woods stay), NAIP segment model, lidar pads, perception scene, + a scorecard |
| `nocard` | as `osm_card`, no scorecard |
| `unmapped_nocard` | as `unmapped_card`, no scorecard |

The card is the course's web card (golfify / club site / opengolfapi) when its hole count fits, else one derived
from the hidden OSM ways (pars + line lengths as tee set `osm`); `card_kind` says which. Use `bench.inputs(row,
tier)` to get exactly these inputs. Unmapped tiers are scored on courses that have a segment model output or a
perception scene.

## Contract: `zero_tap_result/1`

One JSON per course, written to `course_data/zero_tap/results/<method>/<tier>/<slug>.json` (or a `.jsonl`):

```json
{"schema": "zero_tap_result/1", "method": "my_method", "version": "git sha or tag", "tier": "osm_card",
 "slug": "sky_mountain_ut", "card_kind": "web:golfify",
 "certain": false,            // the zero-tap promise: true = shown to the golfer with no confirm step
 "confidence": 0.43,          // course-level P(every hole right); used for the coverage-precision curve
 "holes": [
   {"number": 1, "par": 4,
    "green_ll": [-113.27, 37.11],              // required: a point on / in the green  [lon, lat]
    "tee_ll": [-113.27, 37.10],                // required: a point in the tee complex (back tee preferred)
    "tee_boxes_ll": [[...], ...],              // optional: more boxes of the same complex (any may match)
    "green_id": "way/123", "tee_id": "...",    // optional, informational
    "confidence": 0.9,                         // optional per-hole P(right), used for hole ECE
    "course": "North"},                        // optional, 27 / 36-hole facilities
   ...],
 "error": null}                // set (and holes empty) when the method failed: scored as a miss
```

Holes is a list, so 27 / 36-hole facilities may repeat numbers. Coordinates, not ids, are scored.

## Scoring (`bench.py`)

Per predicted hole: its green matches true hole *j* when the point is within 12 yds of the true green's edge
(centroid - equal-area radius) or 20 yds of the true line's end; its tee matches when any tee point is within 35
yds of the true line's start or 30 yds of the first 60 % of the true line extended 90 yds backwards (back tees
behind the mapped start). Green and tee of the same true hole = **formed**; each true hole can be formed once.
Formed + number = ref = **hole number right**.

Course: **fully right** = exactly N holes, every hole number right, and every par right where the truth knows it
(`courses_holes_right` is the same without par). **Zero-tap coverage** = share of courses with `certain: true`;
**zero-tap precision** = fully right among those (target >= 99 %). **Curve**: courses sorted by `confidence`,
precision of the top-k at several coverages, and the largest coverage with precision >= 99 / 95 / 90 %.

Failure types (per hole, and a primary one per wrong course in this order):
`no_result`, `count` (wrong hole count), `pairing` (green not a true green, or its tee belongs to another hole, or a
true hole used twice), `missed_tee` (right green, tee matches no true hole start), `nine_swap` / `start_hole` /
`order` (formed holes numbered wrongly; the numbering is explained by front/back swap, a cyclic shift, or neither
(incl. reversed)), `par`; `missing` counts true holes nobody formed.

## How to run

```bash
python course_data/zero_tap/bench_set.py                           # manifest + truth (offline, ~3 s)
python course_data/zero_tap/bench.py score my_results_dir --split dev   # your method, dev only while tuning
python course_data/zero_tap/baselines.py --method routing_v2 --tier osm_card --split dev --out /tmp/res
python -m pytest course_data/zero_tap/test_bench.py -q             # scorer self-checks (oracle = 100 %)
```

On GitHub Actions (`.github/workflows/zero_tap_bench.yml`): commit
`course_data/requests/ztbench_run_<name>.json` with `{"stage": "run", "methods": "routing_v2,structure"}` to
re-run the baselines (6 shards), or `{"stage": "score"}` after committing your own `results/<method>/<tier>/`
files: the workflow re-scores everything and commits `SCOREBOARD.md`, `scoreboard.json`, `scores/`.

Data (`.github/workflows/zero_tap_data.yml`, request `ztbench_data_<name>.json`): `stage` survey / fetch / all,
`what` osm,card / imagery (NAIP + segment model + lidar pads for the unmapped tier).
