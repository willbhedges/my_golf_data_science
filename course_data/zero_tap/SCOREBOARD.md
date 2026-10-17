# Zero-tap benchmark scoreboard

Benchmark: 313 courses ({'dev': 160, 'test': 153}; 152 new since v0), built 2026-10-17T20:28:22Z. Contract and rules: [BENCH.md](BENCH.md). Test = held-out states: report, never tune.

## test

| method | tier | courses | hole number | formed | par | fully right | certain: coverage | certain: precision | cov @ P>=99% | cov @ P>=95% | top course failures |
|---|---|---|---|---|---|---|---|---|---|---|---|
| formation_v2 | osm_card | 153 | 2.5% | 44.1% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | no_result 71, pairing 58, missed_tee 9, start_hole 7 |
| routing_v2 | osm_card | 153 | 67.3% | 73.4% | 98.6% | 16.3% | 2.0% (3) | 33.3% | 0.0% | 0.0% | pairing 94, missed_tee 25, count 9 |
| sequence | osm_card | 153 | 31.1% | 38.9% | 92.0% | 5.9% | 4.6% (7) | 42.9% | 0.0% | 0.0% | no_result 72, pairing 59, missed_tee 6, count 5 |
| sequence_v2 | osm_card | 153 | 38.6% | 44.2% | 94.1% | 7.8% | 0.0% (0) | - | 0.0% | 0.0% | no_result 71, pairing 44, missed_tee 18, count 5 |
| structure | osm_card | 153 | 56.4% | 71.6% | 87.3% | 0.7% | 0.0% (0) | - | 0.0% | 0.0% | pairing 103, par 21, missed_tee 13, count 11 |
| formation_v2 | unmapped_card | 17 | 4.6% | 86.3% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 10, start_hole 4, missed_tee 2, count 1 |
| routing_v2 | unmapped_card | 17 | 61.8% | 67.3% | 99.5% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 13, missed_tee 3, no_result 1 |
| sequence_v2 | unmapped_card | 17 | 73.9% | 87.3% | 94.4% | 17.6% | 0.0% (0) | - | 0.0% | 0.0% | pairing 7, missed_tee 6, count 1 |
| structure | unmapped_card | 17 | 48.0% | 65.7% | 92.5% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 16, count 1 |
| formation_v2 | nocard | 153 | 2.7% | 44.7% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | no_result 71, pairing 60, missed_tee 10, count 7 |
| routing_v2 | nocard | 153 | 14.6% | 60.3% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 128, count 14, missed_tee 6, par 2 |
| sequence | nocard | 153 | 9.3% | 37.2% | 87.6% | 0.0% | 1.3% (2) | 0.0% | 0.0% | 0.0% | no_result 72, pairing 65, missed_tee 5, count 4 |
| sequence_v2 | nocard | 153 | 14.6% | 44.1% | 87.1% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | no_result 71, pairing 50, missed_tee 15, nine_swap 6 |
| structure | nocard | 153 | 24.6% | 72.9% | 87.2% | 1.3% | 0.0% (0) | - | 0.0% | 0.0% | pairing 117, par 11, count 8, missed_tee 5 |
| formation_v2 | unmapped_nocard | 17 | 5.2% | 86.9% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 9, start_hole 3, order 2, missed_tee 2 |
| routing_v2 | unmapped_nocard | 17 | 18.3% | 52.0% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 16, no_result 1 |
| sequence_v2 | unmapped_nocard | 17 | 43.5% | 87.3% | 88.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 8, missed_tee 4, nine_swap 2, count 1 |
| structure | unmapped_nocard | 17 | 16.3% | 65.7% | 94.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 16, count 1 |

## dev

| method | tier | courses | hole number | formed | par | fully right | certain: coverage | certain: precision | cov @ P>=99% | cov @ P>=95% | top course failures |
|---|---|---|---|---|---|---|---|---|---|---|---|
| formation_v2 | osm_card | 160 | 2.3% | 44.3% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | no_result 84, pairing 46, start_hole 15, order 8 |
| routing_v2 | osm_card | 160 | 69.4% | 76.3% | 98.5% | 20.0% | 3.1% (5) | 80.0% | 0.0% | 0.0% | pairing 95, missed_tee 23, count 9, par 1 |
| sequence | osm_card | 160 | 29.1% | 36.1% | 89.3% | 6.9% | 2.5% (4) | 50.0% | 0.0% | 0.0% | no_result 86, pairing 55, missed_tee 4, par 2 |
| sequence_v2 | osm_card | 160 | 38.5% | 42.9% | 93.1% | 10.6% | 0.6% (1) | 100.0% | 0.6% | 0.6% | no_result 84, pairing 42, missed_tee 12, par 4 |
| structure | osm_card | 160 | 56.1% | 73.1% | 88.2% | 5.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 106, par 18, missed_tee 12, count 10 |
| formation_v2 | unmapped_card | 38 | 3.8% | 92.5% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 12, start_hole 9, order 9, missed_tee 4 |
| routing_v2 | unmapped_card | 38 | 69.3% | 73.7% | 98.8% | 5.3% | 0.0% (0) | - | 0.0% | 0.0% | pairing 28, missed_tee 7, count 1 |
| sequence_v2 | unmapped_card | 38 | 79.7% | 89.3% | 94.4% | 31.6% | 0.0% (0) | - | 0.0% | 0.0% | pairing 16, missed_tee 6, order 3, count 1 |
| structure | unmapped_card | 38 | 49.4% | 67.7% | 89.9% | 2.6% | 0.0% (0) | - | 0.0% | 0.0% | pairing 35, count 1, missed_tee 1 |
| formation_v2 | nocard | 160 | 2.1% | 44.7% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | no_result 84, pairing 49, start_hole 12, order 9 |
| routing_v2 | nocard | 160 | 12.5% | 59.6% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 136, count 14, missed_tee 5, start_hole 2 |
| sequence | nocard | 160 | 15.0% | 36.0% | 87.4% | 1.3% | 0.0% (0) | - | 0.0% | 0.0% | no_result 86, pairing 59, par 3, count 3 |
| sequence_v2 | nocard | 160 | 17.6% | 42.8% | 86.0% | 1.9% | 0.0% (0) | - | 0.0% | 0.0% | no_result 84, pairing 39, missed_tee 11, par 7 |
| structure | nocard | 160 | 20.2% | 73.6% | 87.9% | 2.5% | 0.0% (0) | - | 0.0% | 0.0% | pairing 116, missed_tee 11, count 11, start_hole 7 |
| formation_v2 | unmapped_nocard | 38 | 3.9% | 94.3% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 17, start_hole 10, order 7, count 2 |
| routing_v2 | unmapped_nocard | 38 | 7.6% | 56.0% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 37, count 1 |
| sequence_v2 | unmapped_nocard | 38 | 25.9% | 90.5% | 86.0% | 7.9% | 0.0% (0) | - | 0.0% | 0.0% | pairing 18, missed_tee 6, start_hole 5, count 2 |
| structure | unmapped_nocard | 38 | 17.5% | 70.3% | 90.1% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 35, count 3 |

## test, v0 courses only (comparable with the 161-course board)

| method | tier | courses | hole number | formed | par | fully right | certain: coverage | certain: precision | cov @ P>=99% | cov @ P>=95% | top course failures |
|---|---|---|---|---|---|---|---|---|---|---|---|
| formation_v2 | osm_card | 84 | 4.6% | 82.1% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 58, missed_tee 9, start_hole 7, count 6 |
| routing_v2 | osm_card | 84 | 68.1% | 74.1% | 99.2% | 11.9% | 2.4% (2) | 50.0% | 0.0% | 0.0% | pairing 53, missed_tee 18, count 3 |
| sequence | osm_card | 84 | 58.0% | 72.4% | 92.0% | 10.7% | 8.3% (7) | 42.9% | 0.0% | 0.0% | pairing 59, missed_tee 6, count 5, no_result 3 |
| sequence_v2 | osm_card | 84 | 71.8% | 82.3% | 94.1% | 14.3% | 0.0% (0) | - | 0.0% | 0.0% | pairing 44, missed_tee 18, count 5, no_result 2 |
| structure | osm_card | 84 | 57.5% | 70.8% | 87.7% | 1.2% | 0.0% (0) | - | 0.0% | 0.0% | pairing 59, par 9, missed_tee 7, count 5 |
| formation_v2 | nocard | 84 | 5.0% | 83.2% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 60, missed_tee 10, count 7, start_hole 3 |
| routing_v2 | nocard | 84 | 13.5% | 59.6% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 71, count 5, missed_tee 3, par 2 |
| sequence | nocard | 84 | 17.3% | 69.2% | 87.6% | 0.0% | 2.4% (2) | 0.0% | 0.0% | 0.0% | pairing 65, missed_tee 5, count 4, no_result 3 |
| sequence_v2 | nocard | 84 | 27.2% | 82.1% | 87.1% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 50, missed_tee 15, nine_swap 6, count 6 |
| structure | nocard | 84 | 21.4% | 69.3% | 88.2% | 2.4% | 0.0% (0) | - | 0.0% | 0.0% | pairing 66, count 4, no_result 3, par 3 |

## dev, v0 courses only

| method | tier | courses | hole number | formed | par | fully right | certain: coverage | certain: precision | cov @ P>=99% | cov @ P>=95% | top course failures |
|---|---|---|---|---|---|---|---|---|---|---|---|
| formation_v2 | osm_card | 77 | 4.8% | 91.3% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 46, start_hole 15, order 8, count 3 |
| routing_v2 | osm_card | 77 | 73.6% | 78.7% | 98.3% | 16.9% | 2.6% (2) | 50.0% | 0.0% | 0.0% | pairing 51, missed_tee 11, count 1, par 1 |
| sequence | osm_card | 77 | 59.8% | 74.4% | 89.3% | 14.3% | 5.2% (4) | 50.0% | 0.0% | 0.0% | pairing 55, missed_tee 4, no_result 3, par 2 |
| sequence_v2 | osm_card | 77 | 79.3% | 88.2% | 93.1% | 22.1% | 1.3% (1) | 100.0% | 1.3% | 1.3% | pairing 42, missed_tee 12, par 4, no_result 1 |
| structure | osm_card | 77 | 59.8% | 74.2% | 87.6% | 5.2% | 0.0% (0) | - | 0.0% | 0.0% | pairing 55, par 9, missed_tee 4, no_result 3 |
| formation_v2 | nocard | 77 | 4.3% | 91.9% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 49, start_hole 12, order 9, count 3 |
| routing_v2 | nocard | 77 | 9.2% | 59.1% | 0.0% | 0.0% | 0.0% (0) | - | 0.0% | 0.0% | pairing 73, missed_tee 3, count 1 |
| sequence | nocard | 77 | 31.0% | 74.2% | 87.4% | 2.6% | 0.0% (0) | - | 0.0% | 0.0% | pairing 59, no_result 3, par 3, count 3 |
| sequence_v2 | nocard | 77 | 36.2% | 88.2% | 86.0% | 3.9% | 0.0% (0) | - | 0.0% | 0.0% | pairing 39, missed_tee 11, par 7, count 5 |
| structure | nocard | 77 | 24.8% | 74.4% | 88.0% | 3.9% | 0.0% (0) | - | 1.3% | 1.3% | pairing 59, no_result 3, missed_tee 3, count 3 |

## Coverage vs precision (test)

Courses sorted by the method's course confidence; precision of the top-k (fully right incl. par).

- **formation_v2 / osm_card**: cov 5.2% -> 0.0%; cov 9.8% -> 0.0%; cov 20.3% -> 0.0%; cov 30.1% -> 0.0%; cov 49.7% -> 0.0%; cov 69.9% -> 0.0%; cov 100.0% -> 0.0%
- **routing_v2 / osm_card**: cov 5.2% -> 37.5%; cov 9.8% -> 26.7%; cov 20.3% -> 32.3%; cov 30.1% -> 30.4%; cov 49.7% -> 26.3%; cov 69.9% -> 22.4%; cov 100.0% -> 16.3%
- **sequence / osm_card**: cov 5.2% -> 50.0%; cov 9.8% -> 40.0%; cov 20.3% -> 29.0%; cov 30.1% -> 19.6%; cov 49.7% -> 11.8%; cov 69.9% -> 8.4%; cov 100.0% -> 5.9%
- **sequence_v2 / osm_card**: cov 5.2% -> 50.0%; cov 9.8% -> 33.3%; cov 20.3% -> 29.0%; cov 30.1% -> 23.9%; cov 49.7% -> 15.8%; cov 69.9% -> 11.2%; cov 100.0% -> 7.8%
- **structure / osm_card**: cov 5.2% -> 0.0%; cov 9.8% -> 0.0%; cov 20.3% -> 0.0%; cov 30.1% -> 0.0%; cov 49.7% -> 1.3%; cov 69.9% -> 0.9%; cov 100.0% -> 0.7%
- **formation_v2 / unmapped_card**: cov 5.9% -> 0.0%; cov 11.8% -> 0.0%; cov 17.6% -> 0.0%; cov 29.4% -> 0.0%; cov 47.1% -> 0.0%; cov 70.6% -> 0.0%; cov 100.0% -> 0.0%
- **routing_v2 / unmapped_card**: cov 5.9% -> 0.0%; cov 11.8% -> 0.0%; cov 17.6% -> 0.0%; cov 29.4% -> 0.0%; cov 47.1% -> 0.0%; cov 70.6% -> 0.0%; cov 100.0% -> 0.0%
- **sequence_v2 / unmapped_card**: cov 5.9% -> 0.0%; cov 11.8% -> 50.0%; cov 17.6% -> 66.7%; cov 29.4% -> 60.0%; cov 47.1% -> 37.5%; cov 70.6% -> 25.0%; cov 100.0% -> 17.6%
- **structure / unmapped_card**: cov 5.9% -> 0.0%; cov 11.8% -> 0.0%; cov 17.6% -> 0.0%; cov 29.4% -> 0.0%; cov 47.1% -> 0.0%; cov 70.6% -> 0.0%; cov 100.0% -> 0.0%
- **formation_v2 / nocard**: cov 5.2% -> 0.0%; cov 9.8% -> 0.0%; cov 20.3% -> 0.0%; cov 30.1% -> 0.0%; cov 49.7% -> 0.0%; cov 69.9% -> 0.0%; cov 100.0% -> 0.0%
- **routing_v2 / nocard**: cov 5.2% -> 0.0%; cov 9.8% -> 0.0%; cov 20.3% -> 0.0%; cov 30.1% -> 0.0%; cov 49.7% -> 0.0%; cov 69.9% -> 0.0%; cov 100.0% -> 0.0%
- **sequence / nocard**: cov 5.2% -> 0.0%; cov 9.8% -> 0.0%; cov 20.3% -> 0.0%; cov 30.1% -> 0.0%; cov 49.7% -> 0.0%; cov 69.9% -> 0.0%; cov 100.0% -> 0.0%
- **sequence_v2 / nocard**: cov 5.2% -> 0.0%; cov 9.8% -> 0.0%; cov 20.3% -> 0.0%; cov 30.1% -> 0.0%; cov 49.7% -> 0.0%; cov 69.9% -> 0.0%; cov 100.0% -> 0.0%
- **structure / nocard**: cov 5.2% -> 0.0%; cov 9.8% -> 0.0%; cov 20.3% -> 3.2%; cov 30.1% -> 2.2%; cov 49.7% -> 2.6%; cov 69.9% -> 1.9%; cov 100.0% -> 1.3%
- **formation_v2 / unmapped_nocard**: cov 5.9% -> 0.0%; cov 11.8% -> 0.0%; cov 17.6% -> 0.0%; cov 29.4% -> 0.0%; cov 47.1% -> 0.0%; cov 70.6% -> 0.0%; cov 100.0% -> 0.0%
- **routing_v2 / unmapped_nocard**: cov 5.9% -> 0.0%; cov 11.8% -> 0.0%; cov 17.6% -> 0.0%; cov 29.4% -> 0.0%; cov 47.1% -> 0.0%; cov 70.6% -> 0.0%; cov 100.0% -> 0.0%
- **sequence_v2 / unmapped_nocard**: cov 5.9% -> 0.0%; cov 11.8% -> 0.0%; cov 17.6% -> 0.0%; cov 29.4% -> 0.0%; cov 47.1% -> 0.0%; cov 70.6% -> 0.0%; cov 100.0% -> 0.0%
- **structure / unmapped_nocard**: cov 5.9% -> 0.0%; cov 11.8% -> 0.0%; cov 17.6% -> 0.0%; cov 29.4% -> 0.0%; cov 47.1% -> 0.0%; cov 70.6% -> 0.0%; cov 100.0% -> 0.0%

## Hole failure types (test, holes)

| method | tier | pairing | missed_tee | nine_swap | start_hole | order | par | missing |
|---|---|---|---|---|---|---|---|---|
| formation_v2 | osm_card | 115 | 67 | 16 | 636 | 520 | 1219 | 1575 |
| routing_v2 | osm_card | 340 | 247 | 0 | 8 | 164 | 28 | 749 |
| sequence | osm_card | 249 | 66 | 23 | 30 | 165 | 86 | 1722 |
| sequence_v2 | osm_card | 112 | 71 | 0 | 31 | 128 | 72 | 1572 |
| structure | osm_card | 439 | 133 | 19 | 62 | 346 | 254 | 800 |
| formation_v2 | unmapped_card | 23 | 15 | 0 | 181 | 69 | 264 | 42 |
| routing_v2 | unmapped_card | 40 | 42 | 0 | 10 | 7 | 1 | 100 |
| sequence_v2 | unmapped_card | 17 | 18 | 0 | 22 | 19 | 15 | 39 |
| structure | unmapped_card | 76 | 25 | 0 | 22 | 32 | 15 | 105 |
| formation_v2 | nocard | 180 | 82 | 33 | 495 | 654 | 1233 | 1559 |
| routing_v2 | nocard | 676 | 243 | 238 | 770 | 280 | 1680 | 1117 |
| sequence | nocard | 305 | 78 | 326 | 291 | 168 | 128 | 1770 |
| sequence_v2 | nocard | 194 | 92 | 396 | 245 | 190 | 158 | 1575 |
| structure | nocard | 555 | 143 | 370 | 505 | 488 | 260 | 762 |
| formation_v2 | unmapped_nocard | 22 | 14 | 0 | 179 | 71 | 266 | 40 |
| routing_v2 | unmapped_nocard | 75 | 54 | 15 | 53 | 35 | 159 | 147 |
| sequence_v2 | unmapped_nocard | 21 | 14 | 34 | 80 | 20 | 32 | 39 |
| structure | unmapped_nocard | 73 | 23 | 41 | 95 | 15 | 12 | 105 |

## By facility size (test: hole number / fully right)

- formation_v2 / osm_card: 9-hole n=15 5.2% / 0.0%; 18-hole n=124 2.7% / 0.0%; 27-hole n=6 0.6% / 0.0%; 36-hole n=8 0.7% / 0.0%
- routing_v2 / osm_card: 9-hole n=15 80.0% / 40.0%; 18-hole n=124 77.0% / 15.3%; 27-hole n=6 1.9% / 0.0%; 36-hole n=8 22.9% / 0.0%
- sequence / osm_card: 9-hole n=15 34.1% / 13.3%; 18-hole n=124 37.2% / 5.6%; 27-hole n=6 0.0% / 0.0%; 36-hole n=8 0.3% / 0.0%
- sequence_v2 / osm_card: 9-hole n=15 40.0% / 13.3%; 18-hole n=124 46.0% / 8.1%; 27-hole n=6 3.1% / 0.0%; 36-hole n=8 0.3% / 0.0%
- structure / osm_card: 9-hole n=15 76.3% / 0.0%; 18-hole n=124 65.8% / 0.8%; 27-hole n=6 5.6% / 0.0%; 36-hole n=8 3.1% / 0.0%
- formation_v2 / unmapped_card: 18-hole n=17 4.6% / 0.0%
- routing_v2 / unmapped_card: 18-hole n=17 61.8% / 0.0%
- sequence_v2 / unmapped_card: 18-hole n=17 73.9% / 17.6%
- structure / unmapped_card: 18-hole n=17 48.0% / 0.0%
- formation_v2 / nocard: 9-hole n=15 5.2% / 0.0%; 18-hole n=124 2.9% / 0.0%; 27-hole n=6 0.0% / 0.0%; 36-hole n=8 1.4% / 0.0%
- routing_v2 / nocard: 9-hole n=15 24.4% / 0.0%; 18-hole n=124 15.9% / 0.0%; 27-hole n=6 9.3% / 0.0%; 36-hole n=8 3.5% / 0.0%
- sequence / nocard: 9-hole n=15 10.4% / 0.0%; 18-hole n=124 11.0% / 0.0%; 27-hole n=6 0.0% / 0.0%; 36-hole n=8 1.0% / 0.0%
- sequence_v2 / nocard: 9-hole n=15 19.3% / 0.0%; 18-hole n=124 16.8% / 0.0%; 27-hole n=6 2.5% / 0.0%; 36-hole n=8 1.7% / 0.0%
- structure / nocard: 9-hole n=15 31.9% / 0.0%; 18-hole n=124 28.3% / 1.6%; 27-hole n=6 4.3% / 0.0%; 36-hole n=8 3.8% / 0.0%
- formation_v2 / unmapped_nocard: 18-hole n=17 5.2% / 0.0%
- routing_v2 / unmapped_nocard: 18-hole n=17 18.3% / 0.0%
- sequence_v2 / unmapped_nocard: 18-hole n=17 43.5% / 0.0%
- structure / unmapped_nocard: 18-hole n=17 16.3% / 0.0%
