# Native-side confirm tap: offline value (answers simulated from the truth, 'near')

Made 2026-11-02 11:41Z by `course_data/mapper/eval_native_confirm.py` (n = 4000, seed 31; DECIDE_ADAPTIVE_AIM=0 V2_ADAPTIVE_AIM=0 for comparison with EVAL_BLIND rounds 3-4). **Truth-bearing: never show to a mapper.**

match / regret (strokes) over the corridor tee shots; questions asked in brackets.

| course | holes | AUTO | AGENT | ASK 2 | ASK 4 | ASK 6 | ASK all |
|---|---|---|---|---|---|---|---|
| ellis | 14 | 11 / 0.377 | 11 / 0.335 | 11 / 0.335 (2) | 11 / 0.335 (4) | 11 / 0.335 (6) | 11 / 0.335 (14) |
| spirit_hollow | 14 | 6 / 0.841 | 7 / 0.682 | 8 / 0.617 (2) | 8 / 0.617 (4) | 8 / 0.305 (6) | 8 / 0.299 (14) |
| sand_creek_station | 14 | 12 / 0.237 | 12 / 0.232 | 13 / 0.233 (2) | 13 / 0.233 (2) | 13 / 0.233 (2) | 14 / 0.136 (14) |
| eagle_bend | 14 | 7 / 0.517 | 8 / 0.588 | 9 / 0.280 (2) | 9 / 0.299 (4) | 10 / 0.196 (6) | 10 / 0.190 (14) |
| prairie_dunes | 14 | 1 / 1.614 | 7 / 0.789 | 8 / 0.714 (2) | 9 / 0.514 (4) | 9 / 0.510 (6) | 10 / 0.440 (14) |
| buffalo_dunes | 14 | 7 / 1.622 | 13 / 0.205 | 13 / 0.182 (2) | 13 / 0.152 (4) | 13 / 0.138 (6) | 13 / 0.113 (14) |
| mariah_hills | 14 | 6 / 0.850 | 8 / -0.317 | 7 / -0.454 (2) | 7 / -0.505 (4) | 5 / -0.420 (6) | 5 / -0.454 (14) |
| **pooled** | | **50 / 6.058** | **66 / 2.514** | **69 / 1.907** (14) | **70 / 1.645** (26) | **69 / 1.297** (38) | **71 / 1.059** (98) |

## Asked holes (simulated answer; plan AGENT -> after; truth)

- **ellis** (ASK 6): 2 [L; p L 0.75 R 0.40; value 0.067]: Driver +40 -> Driver +40 (truth Driver +40; regret 0.0009 -> 0.0009); 1 [none; p L 0.25 R 0.25; value 0.042]: Driver +2 -> Driver +2 (truth Driver -2; regret 0.0107 -> 0.0107); 12 [none; p L 0.25 R 0.10; value 0.042]: Driver -5 -> Driver -5 (truth Driver -5; regret -0.0002 -> -0.0002); 5 [none; p L 0.25 R 0.25; value 0.037]: Driver +0 -> Driver +0 (truth Driver -2; regret 0.0031 -> 0.0031); 10 [none; p L 0.25 R 0.25; value 0.020]: Driver +5 -> Driver +5 (truth Driver +2; regret 0.0007 -> 0.0007); 6 [none; p L 0.25 R 0.25; value 0.020]: Driver +2 -> Driver +2 (truth Driver -5; regret 0.0177 -> 0.0177)
- **spirit_hollow** (ASK 6): 18 [both; p L 0.75 R 0.90; value 0.200]: Driver -12 -> 4-wood -12 (truth 4-wood -15; regret 0.1503 -> 0.009); 4 [both; p L 0.40 R 0.75; value 0.091]: Driver -18 -> 4-wood -5 (truth Driver -12; regret 0.0177 -> 0.0942); 13 [none; p L 0.75 R 0.40; value 0.091]: Driver +15 -> Driver +15 (truth 4-wood +2; regret 0.0278 -> 0.0278); 17 [L; p L 0.75 R 0.40; value 0.049]: Driver +2 -> Driver +2 (truth Driver +12; regret 0.0053 -> 0.0053); 1 [L; p L 0.30 R 0.30; value 0.039]: Driver -40 -> 4-wood -15 (truth 4-wood -12; regret 0.4223 -> 0.0101); 14 [both; p L 0.40 R 0.75; value 0.027]: 2-wood -40 -> 4-wood -40 (truth 4-wood -15; regret 0.0144 -> 0.1146)
- **sand_creek_station** (ASK 2): 10 [R; p L 0.30 R 0.30; value 0.028]: Driver +12 -> 4-wood +0 (truth 4-wood +5; regret 0.0357 -> 0.0299); 8 [none; p L 0.30 R 0.30; value 0.019]: Driver -32 -> Driver -30 (truth Driver -2; regret 0.001 -> 0.0074)
- **eagle_bend** (ASK 6): 2 [both; p L 0.75 R 0.40; value 0.106]: Driver +12 -> 4-wood -5 (truth 4-wood +0; regret 0.2015 -> 0.0337); 15 [L; p L 0.40 R 0.25; value 0.070]: Driver -20 -> 4-wood -5 (truth Driver -8; regret 0.1569 -> 0.0163); 13 [both; p L 0.40 R 0.75; value 0.049]: Driver -2 -> 4-wood +8 (truth Driver -2; regret -0.0008 -> 0.0752); 11 [both; p L 0.25 R 0.40; value 0.039]: Driver -5 -> 4-wood +0 (truth 4-wood -2; regret 0.0644 -> 0.0082); 5 [L; p L 0.25 R 0.10; value 0.027]: Driver +0 -> 4-wood +2 (truth 4-wood +2; regret 0.1034 -> 0.0003); 1 [none; p L 0.25 R 0.25; value 0.026]: Driver -2 -> Driver -2 (truth Driver -5; regret 0.0008 -> 0.0008)
- **prairie_dunes** (ASK 6): 5 [both; p L 0.90 R 0.90; value 0.048]: Driver -10 -> 4-wood -12 (truth 4-wood -12; regret 0.0752 -> 0.001); 3 [both; p L 0.75 R 0.75; value 0.033]: 4-wood +8 -> 4-wood +8 (truth Driver -2; regret 0.1173 -> 0.1173); 1 [both; p L 0.75 R 0.75; value 0.023]: Driver +20 -> 4-wood +38 (truth 4-wood +30; regret 0.2038 -> 0.0033); 13 [both; p L 0.75 R 0.75; value 0.017]: 4-wood +20 -> 4-wood +20 (truth 4-wood +22; regret 0.0094 -> 0.0094); 7 [both; p L 0.90 R 0.90; value 0.012]: 4-wood -2 -> 4-wood -2 (truth 4-wood -2; regret 0.0039 -> 0.0039); 8 [both; p L 0.75 R 0.75; value 0.010]: 4-wood -32 -> 4-wood -35 (truth 4-wood -32; regret 0.0037 -> -0.0001)
- **buffalo_dunes** (ASK 6): 13 [both; p L 0.75 R 0.75; value 0.050]: 4-wood -10 -> 4-wood -10 (truth 4-wood -10; regret 0.002 -> 0.002); 10 [both; p L 0.75 R 0.75; value 0.038]: 4-wood -15 -> 4-wood -18 (truth 4-wood -20; regret 0.0243 -> 0.0021); 16 [both; p L 0.75 R 0.75; value 0.024]: 4-wood -10 -> 4-wood -10 (truth 4-wood -10; regret -0.001 -> -0.001); 5 [both; p L 0.75 R 0.75; value 0.021]: Driver +38 -> 4-wood +38 (truth 4-wood +40; regret 0.0419 -> 0.012); 14 [both; p L 0.75 R 0.75; value 0.018]: 4-wood -8 -> 4-wood -8 (truth 4-wood -10; regret 0.0012 -> 0.0012); 1 [both; p L 0.75 R 0.75; value 0.014]: Driver -8 -> Driver -5 (truth Driver -2; regret 0.0179 -> 0.0029)
- **mariah_hills** (ASK 6): 1 [L; p L 0.90 R 0.75; value 0.476]: Driver +18 -> Driver +28 (truth Driver +18; regret -0.0008 -> 0.0304); 9 [both; p L 0.90 R 0.90; value 0.120]: Driver -40 -> 4-wood +30 (truth Driver -38; regret 0.1675 -> None); 14 [both; p L 0.90 R 0.90; value 0.090]: Driver +5 -> 4-wood -5 (truth 4-wood -5; regret 0.0277 -> 0.0032); 10 [R; p L 0.40 R 0.75; value 0.042]: Driver +5 -> 4-wood -2 (truth Driver -2; regret 0.0381 -> 0.0119); 18 [both; p L 0.90 R 0.75; value 0.035]: Driver +15 -> 4-wood +10 (truth Driver +15; regret 0.0009 -> 0.0616); 12 [L; p L 0.90 R 0.40; value 0.034]: Driver +5 -> Driver +10 (truth Driver +0; regret 0.0091 -> 0.0326)

## Simulated answers vs mapper (every corridor hole)

| course | hole | truth answer | sq yds L / R | prior L / R |
|---|---|---|---|---|
| ellis | 2 | L | 1466 / 0 | 0.75 / 0.4 |
| ellis | 7 | none | 0.0 / 0.0 | 0.75 / 0.4 |
| ellis | 15 | both | 1233 / 640 | 0.75 / 0.75 |
| ellis | 17 | both | 716 / 315 | 0.9 / 0.9 |
| spirit_hollow | 1 | L | 1844 / 0 | 0.3 / 0.3 |
| spirit_hollow | 2 | both | 336 / 1997 | 0.3 / 0.3 |
| spirit_hollow | 4 | both | 1612 / 3292 | 0.4 / 0.75 |
| spirit_hollow | 5 | L | 2250 / 0 | 0.75 / 0.75 |
| spirit_hollow | 6 | both | 1038 / 523 | 0.75 / 0.75 |
| spirit_hollow | 8 | both | 1432 / 327 | 0.3 / 0.3 |
| spirit_hollow | 10 | L | 730 / 0 | 0.4 / 0.9 |
| spirit_hollow | 11 | L | 819 / 22 | 0.3 / 0.3 |
| spirit_hollow | 13 | none | 0.0 / 0.0 | 0.75 / 0.4 |
| spirit_hollow | 14 | both | 551 / 3121 | 0.4 / 0.75 |
| spirit_hollow | 16 | L | 907 / 0 | 0.75 / 0.75 |
| spirit_hollow | 17 | L | 559 / 0 | 0.75 / 0.4 |
| spirit_hollow | 18 | both | 2612 / 2222 | 0.75 / 0.9 |
| sand_creek_station | 1 | R | 0 / 1549 | 0.3 / 0.3 |
| sand_creek_station | 4 | both | 2751 / 1595 | 0.3 / 0.3 |
| sand_creek_station | 5 | both | 3545 / 1607 | 0.4 / 0.75 |
| sand_creek_station | 10 | R | 161 / 1487 | 0.3 / 0.3 |
| sand_creek_station | 11 | both | 1456 / 3272 | 0.75 / 0.75 |
| sand_creek_station | 12 | both | 3310 / 2387 | 0.75 / 0.4 |
| sand_creek_station | 14 | both | 2393 / 3164 | 0.3 / 0.3 |
| sand_creek_station | 15 | both | 1419 / 1271 | 0.9 / 0.4 |
| sand_creek_station | 16 | both | 2813 / 1994 | 0.4 / 0.75 |
| sand_creek_station | 18 | both | 2410 / 1093 | 0.3 / 0.3 |
| eagle_bend | 2 | both | 3846 / 4920 | 0.75 / 0.4 |
| eagle_bend | 3 | L | 3725 / 0 | 0.4 / 0.1 |
| eagle_bend | 5 | L | 4050 / 0 | 0.25 / 0.1 |
| eagle_bend | 6 | L | 4033 / 0 | 0.25 / 0.1 |
| eagle_bend | 11 | both | 3357 / 5462 | 0.25 / 0.4 |
| eagle_bend | 13 | both | 595 / 3727 | 0.4 / 0.75 |
| eagle_bend | 14 | none | 0.0 / 0.0 | 0.75 / 0.4 |
| eagle_bend | 15 | L | 5074 / 0 | 0.4 / 0.25 |
| eagle_bend | 16 | L | 5029 / 0 | 0.25 / 0.1 |
| eagle_bend | 18 | L | 2246 / 0 | 0.25 / 0.1 |
| prairie_dunes | 1 | both | 2312 / 3596 | 0.75 / 0.75 |
| prairie_dunes | 3 | both | 5799 / 6551 | 0.75 / 0.75 |
| prairie_dunes | 5 | both | 4510 / 4692 | 0.9 / 0.9 |
| prairie_dunes | 6 | both | 4542 / 4354 | 0.75 / 0.75 |
| prairie_dunes | 7 | both | 6334 / 4790 | 0.9 / 0.9 |
| prairie_dunes | 8 | both | 4073 / 5655 | 0.75 / 0.75 |
| prairie_dunes | 9 | both | 4761 / 4805 | 0.75 / 0.75 |
| prairie_dunes | 11 | both | 3383 / 2964 | 0.75 / 0.75 |
| prairie_dunes | 12 | both | 4216 / 7213 | 0.75 / 0.75 |
| prairie_dunes | 13 | both | 3536 / 5080 | 0.75 / 0.75 |
| prairie_dunes | 14 | both | 3660 / 5052 | 0.9 / 0.4 |
| prairie_dunes | 16 | both | 3391 / 4621 | 0.4 / 0.75 |
| prairie_dunes | 17 | both | 4684 / 4458 | 0.75 / 0.75 |
| prairie_dunes | 18 | both | 6328 / 6236 | 0.75 / 0.9 |
| buffalo_dunes | 1 | both | 3668 / 3477 | 0.75 / 0.75 |
| buffalo_dunes | 2 | both | 7437 / 6892 | 0.75 / 0.75 |
| buffalo_dunes | 3 | both | 4624 / 3812 | 0.75 / 0.75 |
| buffalo_dunes | 5 | both | 2861 / 4777 | 0.75 / 0.75 |
| buffalo_dunes | 6 | both | 4576 / 5156 | 0.75 / 0.75 |
| buffalo_dunes | 7 | both | 3871 / 3876 | 0.75 / 0.75 |
| buffalo_dunes | 9 | both | 4654 / 3620 | 0.75 / 0.75 |
| buffalo_dunes | 10 | both | 3975 / 1949 | 0.75 / 0.75 |
| buffalo_dunes | 11 | both | 5089 / 4726 | 0.75 / 0.75 |
| buffalo_dunes | 13 | both | 3914 / 6262 | 0.75 / 0.75 |
| buffalo_dunes | 14 | both | 4170 / 1843 | 0.75 / 0.75 |
| buffalo_dunes | 15 | both | 3539 / 5161 | 0.75 / 0.75 |
| buffalo_dunes | 16 | both | 3994 / 6340 | 0.75 / 0.75 |
| buffalo_dunes | 18 | both | 5311 / 4900 | 0.75 / 0.75 |
| mariah_hills | 1 | L | 2154 / 0 | 0.9 / 0.75 |
| mariah_hills | 2 | both | 625 / 3635 | 0.9 / 0.75 |
| mariah_hills | 3 | both | 930 / 2489 | 0.9 / 0.9 |
| mariah_hills | 4 | both | 988 / 1527 | 0.9 / 0.9 |
| mariah_hills | 6 | R | 0 / 935 | 0.4 / 0.75 |
| mariah_hills | 7 | both | 1726 / 781 | 0.75 / 0.9 |
| mariah_hills | 9 | both | 2212 / 1841 | 0.9 / 0.9 |
| mariah_hills | 10 | R | 0 / 620 | 0.4 / 0.75 |
| mariah_hills | 12 | L | 586 / 0 | 0.9 / 0.4 |
| mariah_hills | 13 | both | 903 / 2105 | 0.75 / 0.9 |
| mariah_hills | 14 | both | 2837 / 1505 | 0.9 / 0.9 |
| mariah_hills | 15 | L | 1351 / 0 | 0.75 / 0.4 |
| mariah_hills | 17 | both | 466 / 504 | 0.9 / 0.75 |
| mariah_hills | 18 | both | 2177 / 1035 | 0.9 / 0.75 |
