# Zero-tap benchmark: status (workstream D)

*Updated 2026-10-17.* Contract and how to run: [BENCH.md](BENCH.md). Numbers: [SCOREBOARD.md](SCOREBOARD.md).
OSM truth quality: [OSM_CHECK.md](OSM_CHECK.md).

**Benchmark v1** (`benchmark.json`, 2026-10-17): 313 courses, dev 160 / test 153, 48 states, all four Census
regions; 262 with a fitting web card. It is v0 (161 courses, frozen in `bench_v0.json`, every row flagged `v0`) plus
152 courses from 24 new states. Every v0 course kept its split, so `bench.courses("dev", version="v0")` is exactly
the dev set earlier work fitted on. v0 truth geometry is unchanged; 198 hole pars in 26 v0 courses changed because
new web cards were found (card par is the truth). The unmapped tiers still cover only the 55 v0 courses with
segment-model / perception inputs (NAIP + lidar for the new courses has not been fetched).

**Scoreboard (test, osm_card; Actions run 39062442720):**

| method | v1 test (153): holes numbered right / courses fully right | v0 test subset (84) |
|---|---|---|
| routing_v2 | 67.3 % / 16.3 % | 68.1 % / 11.9 % |
| structure | 56.4 % / 0.7 % | 57.5 % / 1.2 % |
| sequence_v2 (C) | 38.6 % / 7.8 % * | 71.8 % / 14.3 % |
| sequence (C) | 31.1 % / 5.9 % * | 58.0 % / 10.7 % |
| formation_v2 (A) | 2.5 % / 0 % * | 4.6 % / 0 % |

\* results exist only for v0 courses (the new ones count as no_result); compare on the v0 rows until re-run on v1.
No method reaches 99 % precision at any useful coverage; pairing is the dominant failure everywhere.

**For A / B / C:** write `zero_tap_result/1` files to `results/<method>/<tier>/<slug>.json`, tune on
`bench.courses("dev")` only, then commit a `course_data/requests/ztbench_run_<name>.json` with `{"stage": "score"}`.
