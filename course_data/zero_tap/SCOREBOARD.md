# Zero-tap benchmark scoreboard

Benchmark: 161 courses ({'dev': 77, 'test': 84}), built 2026-10-17T16:07:18Z. Contract and rules: [BENCH.md](BENCH.md). Test = held-out states: report, never tune.

## test

| method | tier | courses | hole number | formed | par | fully right | certain: coverage | certain: precision | cov @ P>=99% | cov @ P>=95% | top course failures |
|---|---|---|---|---|---|---|---|---|---|---|---|
| routing_v2 | osm_card | 84 | 69.4% | 75.3% | 98.0% | 14.3% | 6.0% (5) | 80.0% | 1.2% | 1.2% | pairing 55, missed_tee 12, count 3, par 1 |
| structure | osm_card | 84 | 0.7% | 1.2% | 87.5% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | no_result 82, pairing 2 |
| routing_v2 | unmapped_card | 17 | 61.8% | 67.3% | 98.1% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 13, missed_tee 3, no_result 1 |
| structure | unmapped_card | 17 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | no_result 17 |
| routing_v2 | nocard | 84 | 13.5% | 59.5% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 71, count 5, missed_tee 3, par 2 |
| structure | nocard | 84 | 0.0% | 1.1% | 83.3% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | no_result 82, pairing 2 |
| routing_v2 | unmapped_nocard | 17 | 18.0% | 52.6% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 16, no_result 1 |
| structure | unmapped_nocard | 17 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | no_result 17 |

## dev

| method | tier | courses | hole number | formed | par | fully right | certain: coverage | certain: precision | cov @ P>=99% | cov @ P>=95% | top course failures |
|---|---|---|---|---|---|---|---|---|---|---|---|
| routing_v2 | osm_card | 77 | 77.8% | 80.3% | 96.8% | 15.6% | 2.6% (2) | 50.0% | 1.3% | 1.3% | pairing 50, missed_tee 10, par 4, count 1 |
| structure | osm_card | 77 | 0.2% | 0.4% | 100.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | no_result 76, pairing 1 |
| routing_v2 | unmapped_card | 38 | 69.3% | 73.7% | 97.3% | 2.6% | 0.0% (0) | - | 0.0% | 0.0% | pairing 28, missed_tee 7, count 1, par 1 |
| structure | unmapped_card | 38 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | no_result 38 |
| routing_v2 | nocard | 77 | 10.0% | 58.8% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 73, missed_tee 3, count 1 |
| structure | nocard | 77 | 0.0% | 0.2% | 100.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | no_result 76, pairing 1 |
| routing_v2 | unmapped_nocard | 38 | 10.1% | 55.1% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 37, count 1 |
| structure | unmapped_nocard | 38 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | no_result 38 |

## Coverage vs precision (test)

Courses sorted by the method's course confidence; precision of the top-k (fully right incl. par).

- **routing_v2 / osm_card**: cov 4.8% -> 75.0%; cov 9.5% -> 62.5%; cov 20.2% -> 41.2%; cov 29.8% -> 28.0%; cov 50.0% -> 28.6%; cov 70.2% -> 20.3%; cov 100.0% -> 14.3%
- **structure / osm_card**: cov 4.8% -> 0.0%; cov 9.5% -> 0.0%; cov 20.2% -> 0.0%; cov 29.8% -> 0.0%; cov 50.0% -> 0.0%; cov 70.2% -> 0.0%; cov 100.0% -> 0.0%
- **routing_v2 / unmapped_card**: cov 5.9% -> 0.0%; cov 11.8% -> 0.0%; cov 17.6% -> 0.0%; cov 29.4% -> 0.0%; cov 47.1% -> 0.0%; cov 70.6% -> 0.0%; cov 100.0% -> 0.0%
- **structure / unmapped_card**: cov 5.9% -> 0.0%; cov 11.8% -> 0.0%; cov 17.6% -> 0.0%; cov 29.4% -> 0.0%; cov 47.1% -> 0.0%; cov 70.6% -> 0.0%; cov 100.0% -> 0.0%
- **routing_v2 / nocard**: cov 4.8% -> 0.0%; cov 9.5% -> 0.0%; cov 20.2% -> 0.0%; cov 29.8% -> 0.0%; cov 50.0% -> 0.0%; cov 70.2% -> 0.0%; cov 100.0% -> 0.0%
- **structure / nocard**: cov 4.8% -> 0.0%; cov 9.5% -> 0.0%; cov 20.2% -> 0.0%; cov 29.8% -> 0.0%; cov 50.0% -> 0.0%; cov 70.2% -> 0.0%; cov 100.0% -> 0.0%
- **routing_v2 / unmapped_nocard**: cov 5.9% -> 0.0%; cov 11.8% -> 0.0%; cov 17.6% -> 0.0%; cov 29.4% -> 0.0%; cov 47.1% -> 0.0%; cov 70.6% -> 0.0%; cov 100.0% -> 0.0%
- **structure / unmapped_nocard**: cov 5.9% -> 0.0%; cov 11.8% -> 0.0%; cov 17.6% -> 0.0%; cov 29.4% -> 0.0%; cov 47.1% -> 0.0%; cov 70.6% -> 0.0%; cov 100.0% -> 0.0%

## Hole failure types (test, holes)

| method | tier | pairing | missed_tee | nine_swap | start_hole | order | par | missing |
|---|---|---|---|---|---|---|---|---|
| routing_v2 | osm_card | 184 | 136 | 0 | 1 | 88 | 22 | 374 |
| structure | osm_card | 9 | 0 | 0 | 7 | 0 | 1 | 1494 |
| routing_v2 | unmapped_card | 40 | 42 | 0 | 10 | 7 | 4 | 100 |
| structure | unmapped_card | 0 | 0 | 0 | 0 | 0 | 0 | 306 |
| routing_v2 | nocard | 382 | 159 | 162 | 407 | 126 | 865 | 613 |
| structure | nocard | 9 | 1 | 0 | 11 | 6 | 1 | 1495 |
| routing_v2 | unmapped_nocard | 72 | 55 | 15 | 63 | 28 | 161 | 145 |
| structure | unmapped_nocard | 0 | 0 | 0 | 0 | 0 | 0 | 306 |

## By facility size (test: hole number / fully right)

- routing_v2 / osm_card: 9-hole n=8 73.6% / 25.0%; 18-hole n=71 77.8% / 14.1%; 27-hole n=2 1.9% / 0.0%; 36-hole n=3 0.9% / 0.0%
- structure / osm_card: 9-hole n=8 11.1% / 0.0%; 18-hole n=71 0.2% / 0.0%; 27-hole n=2 0.0% / 0.0%; 36-hole n=3 0.0% / 0.0%
- routing_v2 / unmapped_card: 18-hole n=17 61.8% / 0.0%
- structure / unmapped_card: 18-hole n=17 0.0% / 0.0%
- routing_v2 / nocard: 9-hole n=8 26.4% / 0.0%; 18-hole n=71 14.1% / 0.0%; 27-hole n=2 9.3% / 0.0%; 36-hole n=3 0.0% / 0.0%
- structure / nocard: 9-hole n=8 0.0% / 0.0%; 18-hole n=71 0.0% / 0.0%; 27-hole n=2 0.0% / 0.0%; 36-hole n=3 0.0% / 0.0%
- routing_v2 / unmapped_nocard: 18-hole n=17 18.0% / 0.0%
- structure / unmapped_nocard: 18-hole n=17 0.0% / 0.0%
