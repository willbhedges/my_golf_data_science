# Zero-tap benchmark: status (workstream D)

*Updated 2026-10-17.* Contract and how to run: [BENCH.md](BENCH.md). Numbers: [SCOREBOARD.md](SCOREBOARD.md).
OSM truth quality: [OSM_CHECK.md](OSM_CHECK.md).

**Benchmark v0** (`benchmark.json`): 161 courses with complete OSM truth (145 x 18, 10 x 9, 2 x 27, 4 x 36), 24
states, all four Census regions; dev 77 / test 84 (split by state, `state_split.json`). 50 with a fitting web card
(others get a card derived from the hidden OSM ways), 55 with segment-model + lidar inputs, 55 with a perception
scene. v1 (in progress on Actions): +24 states via `fetch.py` (5 x 18 + one 9 + one 27/36 per state), web cards for
every course, NAIP segment + lidar pads for the unmapped tier.

**Baselines (test, osm_card, 84 courses; Actions run 39048121736):** routing_v2 69.4 % hole numbers right, 14.3 %
courses fully right, certain 6.0 % coverage at 80 % precision; sequence (C) 58.0 % / 11.9 %, certain 8.3 % at 42.9 %;
structure 57.7 % / 1.2 %; formation_v2 (A) forms 82 % of holes but numbers 4.6 %. No method reaches 99 % precision at
any useful coverage yet. Dominant failure everywhere: **pairing** (green/tee of different holes). Without a card,
numbering collapses (routing_v2 13.5 %). Full table: SCOREBOARD.md.

**For A / B / C:** write `zero_tap_result/1` files to `results/<method>/<tier>/<slug>.json`, tune on
`bench.courses("dev")` only, then commit a `course_data/requests/ztbench_run_<name>.json` with `{"stage": "score"}`.
