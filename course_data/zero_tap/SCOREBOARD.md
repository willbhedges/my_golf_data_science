# Zero-tap benchmark scoreboard

Benchmark: 161 courses ({'dev': 77, 'test': 84}), built 2026-10-17T17:19:41Z. Contract and rules: [BENCH.md](BENCH.md). Test = held-out states: report, never tune.

## test

| method | tier | courses | hole number | formed | par | fully right | certain: coverage | certain: precision | cov @ P>=99% | cov @ P>=95% | top course failures |
|---|---|---|---|---|---|---|---|---|---|---|---|
| formation_v2 | osm_card | 84 | 4.6% | 82.1% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 58, missed_tee 9, start_hole 7, count 6 |
| routing_v2 | osm_card | 84 | 69.4% | 75.3% | 98.0% | 14.3% | 6.0% (5) | 80.0% | 1.2% | 1.2% | pairing 55, missed_tee 12, count 3, par 1 |
| sequence | osm_card | 84 | 58.0% | 72.4% | 92.6% | 11.9% | 8.3% (7) | 42.9% | 0.0% | 0.0% | pairing 59, missed_tee 6, count 5, no_result 3 |
| structure | osm_card | 84 | 57.7% | 71.8% | 88.3% | 1.2% | 0.0% (0) | - | 0.0% | 0.0% | pairing 60, par 9, missed_tee 6, count 5 |
| formation_v2 | unmapped_card | 17 | 4.6% | 86.3% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 10, start_hole 4, missed_tee 2, count 1 |
| routing_v2 | unmapped_card | 17 | 61.8% | 67.3% | 98.1% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 13, missed_tee 3, no_result 1 |
| structure | unmapped_card | 17 | 48.0% | 65.7% | 91.5% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 16, count 1 |
| formation_v2 | nocard | 84 | 5.0% | 83.2% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 60, missed_tee 10, count 7, start_hole 3 |
| routing_v2 | nocard | 84 | 13.5% | 59.5% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 71, count 5, missed_tee 3, par 2 |
| sequence | nocard | 84 | 17.3% | 69.2% | 87.9% | 0.0% | 2.4% (2) | 0.0% | 0.0% | 0.0% | pairing 65, missed_tee 5, count 4, no_result 3 |
| structure | nocard | 84 | 21.4% | 69.3% | 88.3% | 2.4% | 0.0% (0) | - | 0.0% | 0.0% | pairing 66, count 4, no_result 3, par 3 |
| formation_v2 | unmapped_nocard | 17 | 5.2% | 86.9% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 9, start_hole 3, order 2, missed_tee 2 |
| routing_v2 | unmapped_nocard | 17 | 18.0% | 52.6% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 16, no_result 1 |
| structure | unmapped_nocard | 17 | 16.3% | 65.7% | 93.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 16, count 1 |

## dev

| method | tier | courses | hole number | formed | par | fully right | certain: coverage | certain: precision | cov @ P>=99% | cov @ P>=95% | top course failures |
|---|---|---|---|---|---|---|---|---|---|---|---|
| formation_v2 | osm_card | 77 | 4.8% | 91.3% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 46, start_hole 15, order 8, count 3 |
| routing_v2 | osm_card | 77 | 77.8% | 80.3% | 96.8% | 15.6% | 2.6% (2) | 50.0% | 1.3% | 1.3% | pairing 50, missed_tee 10, par 4, count 1 |
| sequence | osm_card | 77 | 59.8% | 74.4% | 91.4% | 15.6% | 5.2% (4) | 100.0% | 5.2% | 5.2% | pairing 55, missed_tee 4, no_result 3, count 1 |
| structure | osm_card | 77 | 63.7% | 74.7% | 89.4% | 5.2% | 0.0% (0) | - | 0.0% | 0.0% | pairing 55, par 9, missed_tee 4, no_result 3 |
| formation_v2 | unmapped_card | 38 | 3.8% | 92.5% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 12, start_hole 9, order 9, missed_tee 4 |
| routing_v2 | unmapped_card | 38 | 69.3% | 73.7% | 97.3% | 2.6% | 0.0% (0) | - | 0.0% | 0.0% | pairing 28, missed_tee 7, count 1, par 1 |
| structure | unmapped_card | 38 | 49.4% | 67.7% | 89.5% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 35, count 1, par 1, missed_tee 1 |
| formation_v2 | nocard | 77 | 4.3% | 91.9% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 49, start_hole 12, order 9, count 3 |
| routing_v2 | nocard | 77 | 10.0% | 58.8% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 73, missed_tee 3, count 1 |
| sequence | nocard | 77 | 31.0% | 74.2% | 89.2% | 3.9% | 0.0% (0) | - | 0.0% | 0.0% | pairing 59, no_result 3, count 3, order 3 |
| structure | nocard | 77 | 24.8% | 74.4% | 89.6% | 3.9% | 0.0% (0) | - | 1.3% | 1.3% | pairing 59, no_result 3, missed_tee 3, count 3 |
| formation_v2 | unmapped_nocard | 38 | 3.9% | 94.3% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 17, start_hole 10, order 7, count 2 |
| routing_v2 | unmapped_nocard | 38 | 10.1% | 55.1% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 37, count 1 |
| structure | unmapped_nocard | 38 | 17.5% | 70.3% | 89.7% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 35, count 3 |

## Coverage vs precision (test)

Courses sorted by the method's course confidence; precision of the top-k (fully right incl. par).

- **formation_v2 / osm_card**: cov 4.8% -> 0.0%; cov 9.5% -> 0.0%; cov 20.2% -> 0.0%; cov 29.8% -> 0.0%; cov 50.0% -> 0.0%; cov 70.2% -> 0.0%; cov 100.0% -> 0.0%
- **routing_v2 / osm_card**: cov 4.8% -> 75.0%; cov 9.5% -> 62.5%; cov 20.2% -> 41.2%; cov 29.8% -> 28.0%; cov 50.0% -> 28.6%; cov 70.2% -> 20.3%; cov 100.0% -> 14.3%
- **sequence / osm_card**: cov 4.8% -> 50.0%; cov 9.5% -> 50.0%; cov 20.2% -> 41.2%; cov 29.8% -> 40.0%; cov 50.0% -> 23.8%; cov 70.2% -> 16.9%; cov 100.0% -> 11.9%
- **structure / osm_card**: cov 4.8% -> 0.0%; cov 9.5% -> 0.0%; cov 20.2% -> 0.0%; cov 29.8% -> 0.0%; cov 50.0% -> 2.4%; cov 70.2% -> 1.7%; cov 100.0% -> 1.2%
- **formation_v2 / unmapped_card**: cov 5.9% -> 0.0%; cov 11.8% -> 0.0%; cov 17.6% -> 0.0%; cov 29.4% -> 0.0%; cov 47.1% -> 0.0%; cov 70.6% -> 0.0%; cov 100.0% -> 0.0%
- **routing_v2 / unmapped_card**: cov 5.9% -> 0.0%; cov 11.8% -> 0.0%; cov 17.6% -> 0.0%; cov 29.4% -> 0.0%; cov 47.1% -> 0.0%; cov 70.6% -> 0.0%; cov 100.0% -> 0.0%
- **structure / unmapped_card**: cov 5.9% -> 0.0%; cov 11.8% -> 0.0%; cov 17.6% -> 0.0%; cov 29.4% -> 0.0%; cov 47.1% -> 0.0%; cov 70.6% -> 0.0%; cov 100.0% -> 0.0%
- **formation_v2 / nocard**: cov 4.8% -> 0.0%; cov 9.5% -> 0.0%; cov 20.2% -> 0.0%; cov 29.8% -> 0.0%; cov 50.0% -> 0.0%; cov 70.2% -> 0.0%; cov 100.0% -> 0.0%
- **routing_v2 / nocard**: cov 4.8% -> 0.0%; cov 9.5% -> 0.0%; cov 20.2% -> 0.0%; cov 29.8% -> 0.0%; cov 50.0% -> 0.0%; cov 70.2% -> 0.0%; cov 100.0% -> 0.0%
- **sequence / nocard**: cov 4.8% -> 0.0%; cov 9.5% -> 0.0%; cov 20.2% -> 0.0%; cov 29.8% -> 0.0%; cov 50.0% -> 0.0%; cov 70.2% -> 0.0%; cov 100.0% -> 0.0%
- **structure / nocard**: cov 4.8% -> 0.0%; cov 9.5% -> 0.0%; cov 20.2% -> 5.9%; cov 29.8% -> 4.0%; cov 50.0% -> 4.8%; cov 70.2% -> 3.4%; cov 100.0% -> 2.4%
- **formation_v2 / unmapped_nocard**: cov 5.9% -> 0.0%; cov 11.8% -> 0.0%; cov 17.6% -> 0.0%; cov 29.4% -> 0.0%; cov 47.1% -> 0.0%; cov 70.6% -> 0.0%; cov 100.0% -> 0.0%
- **routing_v2 / unmapped_nocard**: cov 5.9% -> 0.0%; cov 11.8% -> 0.0%; cov 17.6% -> 0.0%; cov 29.4% -> 0.0%; cov 47.1% -> 0.0%; cov 70.6% -> 0.0%; cov 100.0% -> 0.0%
- **structure / unmapped_nocard**: cov 5.9% -> 0.0%; cov 11.8% -> 0.0%; cov 17.6% -> 0.0%; cov 29.4% -> 0.0%; cov 47.1% -> 0.0%; cov 70.6% -> 0.0%; cov 100.0% -> 0.0%

## Hole failure types (test, holes)

| method | tier | pairing | missed_tee | nine_swap | start_hole | order | par | missing |
|---|---|---|---|---|---|---|---|---|
| formation_v2 | osm_card | 115 | 67 | 16 | 636 | 520 | 1170 | 270 |
| routing_v2 | osm_card | 184 | 136 | 0 | 1 | 88 | 22 | 374 |
| sequence | osm_card | 249 | 66 | 23 | 30 | 165 | 77 | 417 |
| structure | osm_card | 256 | 68 | 22 | 46 | 145 | 121 | 426 |
| formation_v2 | unmapped_card | 23 | 15 | 0 | 181 | 69 | 264 | 42 |
| routing_v2 | unmapped_card | 40 | 42 | 0 | 10 | 7 | 4 | 100 |
| structure | unmapped_card | 76 | 25 | 0 | 22 | 32 | 17 | 105 |
| formation_v2 | nocard | 180 | 82 | 33 | 495 | 654 | 1184 | 254 |
| routing_v2 | nocard | 382 | 159 | 162 | 407 | 126 | 865 | 613 |
| sequence | nocard | 305 | 78 | 326 | 291 | 168 | 120 | 465 |
| structure | nocard | 307 | 75 | 233 | 304 | 187 | 116 | 464 |
| formation_v2 | unmapped_nocard | 22 | 14 | 0 | 179 | 71 | 266 | 40 |
| routing_v2 | unmapped_nocard | 72 | 55 | 15 | 63 | 28 | 161 | 145 |
| structure | unmapped_nocard | 73 | 23 | 41 | 95 | 15 | 14 | 105 |

## By facility size (test: hole number / fully right)

- formation_v2 / osm_card: 9-hole n=8 9.7% / 0.0%; 18-hole n=71 4.7% / 0.0%; 27-hole n=2 1.9% / 0.0%; 36-hole n=3 1.9% / 0.0%
- routing_v2 / osm_card: 9-hole n=8 73.6% / 25.0%; 18-hole n=71 77.8% / 14.1%; 27-hole n=2 1.9% / 0.0%; 36-hole n=3 0.9% / 0.0%
- sequence / osm_card: 9-hole n=8 63.9% / 37.5%; 18-hole n=71 64.9% / 9.9%; 27-hole n=2 0.0% / 0.0%; 36-hole n=3 0.9% / 0.0%
- structure / osm_card: 9-hole n=8 63.9% / 0.0%; 18-hole n=71 64.6% / 1.4%; 27-hole n=2 0.0% / 0.0%; 36-hole n=3 0.9% / 0.0%
- formation_v2 / unmapped_card: 18-hole n=17 4.6% / 0.0%
- routing_v2 / unmapped_card: 18-hole n=17 61.8% / 0.0%
- structure / unmapped_card: 18-hole n=17 48.0% / 0.0%
- formation_v2 / nocard: 9-hole n=8 9.7% / 0.0%; 18-hole n=71 5.1% / 0.0%; 27-hole n=2 0.0% / 0.0%; 36-hole n=3 3.7% / 0.0%
- routing_v2 / nocard: 9-hole n=8 26.4% / 0.0%; 18-hole n=71 14.1% / 0.0%; 27-hole n=2 9.3% / 0.0%; 36-hole n=3 0.0% / 0.0%
- sequence / nocard: 9-hole n=8 19.4% / 0.0%; 18-hole n=71 19.2% / 0.0%; 27-hole n=2 0.0% / 0.0%; 36-hole n=3 2.8% / 0.0%
- structure / nocard: 9-hole n=8 19.4% / 0.0%; 18-hole n=71 24.0% / 2.8%; 27-hole n=2 0.0% / 0.0%; 36-hole n=3 2.8% / 0.0%
- formation_v2 / unmapped_nocard: 18-hole n=17 5.2% / 0.0%
- routing_v2 / unmapped_nocard: 18-hole n=17 18.0% / 0.0%
- structure / unmapped_nocard: 18-hole n=17 16.3% / 0.0%
