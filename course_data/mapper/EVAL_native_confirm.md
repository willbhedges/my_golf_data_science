# Native-side confirm tap: offline value (answers simulated from the truth, 'near', islands 'never')

Made 2026-11-02 12:36Z by `course_data/mapper/eval_native_confirm.py` (n = 4000, seed 31; DECIDE_ADAPTIVE_AIM=0 V2_ADAPTIVE_AIM=0 for comparison with EVAL_BLIND rounds 3-4). **Truth-bearing: never show to a mapper.**

match / regret (strokes) over the corridor tee shots; questions asked in brackets.

| course | holes | AUTO | AGENT | ASK 2 | ASK 4 | ASK 6 | ASK all |
|---|---|---|---|---|---|---|---|
| ellis | 14 | 11 / 0.375 | 11 / 0.334 | 11 / 0.334 (2) | 11 / 0.334 (4) | 11 / 0.334 (6) | 11 / 0.334 (14) |
| spirit_hollow | 14 | 7 / 0.892 | 8 / 0.729 | 9 / 0.670 (2) | 9 / 0.670 (4) | 10 / 0.343 (6) | 10 / 0.337 (14) |
| sand_creek_station | 14 | 12 / 0.259 | 12 / 0.258 | 13 / 0.257 (2) | 13 / 0.257 (2) | 13 / 0.257 (2) | 14 / 0.146 (14) |
| eagle_bend | 14 | 7 / 0.515 | 8 / 0.586 | 9 / 0.280 (2) | 9 / 0.297 (4) | 10 / 0.194 (6) | 10 / 0.190 (14) |
| prairie_dunes | 14 | 1 / 1.649 | 7 / 0.720 | 8 / 0.641 (2) | 9 / 0.438 (4) | 9 / 0.435 (6) | 10 / 0.361 (14) |
| buffalo_dunes | 14 | 7 / 1.623 | 13 / 0.208 | 13 / 0.185 (2) | 13 / 0.148 (4) | 13 / 0.133 (6) | 13 / 0.105 (14) |
| mariah_hills | 14 | 5 / 0.852 | 8 / -0.323 | 8 / -0.459 (2) | 8 / -0.509 (4) | 6 / -0.426 (6) | 6 / -0.458 (14) |
| **pooled** | | **50 / 6.165** | **67 / 2.512** | **71 / 1.908** (14) | **72 / 1.635** (26) | **72 / 1.270** (38) | **74 / 1.015** (98) |

## Asked holes (simulated answer; plan AGENT -> after; truth)

- **ellis** (ASK 6): 2 [L; out L; p L 0.75 R 0.40; value 0.067]: Driver +40 -> Driver +40 (truth Driver +40; regret 0.0006 -> 0.0006); 1 [none; p L 0.25 R 0.25; value 0.042]: Driver +2 -> Driver +2 (truth Driver -2; regret 0.0105 -> 0.0105); 12 [none; p L 0.25 R 0.10; value 0.042]: Driver -5 -> Driver -5 (truth Driver -5; regret -0.0 -> -0.0); 5 [none; p L 0.25 R 0.25; value 0.037]: Driver +0 -> Driver +0 (truth Driver -2; regret 0.003 -> 0.003); 10 [none; p L 0.25 R 0.25; value 0.020]: Driver +5 -> Driver +5 (truth Driver +2; regret 0.0009 -> 0.0009); 6 [none; p L 0.25 R 0.25; value 0.020]: Driver +2 -> Driver +2 (truth Driver -5; regret 0.0175 -> 0.0175)
- **spirit_hollow** (ASK 6): 18 [both; p L 0.75 R 0.90; value 0.200]: Driver -12 -> 4-wood -12 (truth 4-wood -15; regret 0.1484 -> 0.0094); 4 [both; out L; p L 0.40 R 0.75; value 0.091]: Driver -18 -> 4-wood -5 (truth Driver -12; regret 0.0183 -> 0.0982); 13 [none; p L 0.75 R 0.40; value 0.091]: Driver +15 -> Driver +15 (truth Driver +5; regret 0.0256 -> 0.0256); 17 [L; out L; p L 0.75 R 0.40; value 0.049]: Driver +2 -> Driver +2 (truth Driver +12; regret 0.0051 -> 0.0051); 1 [L; p L 0.30 R 0.30; value 0.039]: Driver -40 -> 4-wood -15 (truth 4-wood -15; regret 0.4591 -> 0.0119); 14 [both; out L; p L 0.40 R 0.75; value 0.027]: 2-wood -40 -> 4-wood -40 (truth 4-wood -12; regret 0.0285 -> 0.1486)
- **sand_creek_station** (ASK 2): 10 [R; out R; p L 0.30 R 0.30; value 0.028]: Driver +12 -> 4-wood +0 (truth 4-wood +5; regret 0.0392 -> 0.0303); 8 [none; p L 0.30 R 0.30; value 0.019]: Driver -32 -> Driver -30 (truth Driver -5; regret 0.0003 -> 0.008)
- **eagle_bend** (ASK 6): 2 [both; p L 0.75 R 0.40; value 0.106]: Driver +12 -> 4-wood -5 (truth 4-wood +0; regret 0.2 -> 0.0333); 15 [L; p L 0.40 R 0.25; value 0.070]: Driver -20 -> 4-wood -5 (truth Driver -5; regret 0.1571 -> 0.0168); 13 [both; out L; p L 0.40 R 0.75; value 0.049]: Driver -2 -> 4-wood +8 (truth Driver -2; regret -0.0008 -> 0.0729); 11 [both; p L 0.25 R 0.40; value 0.039]: Driver -5 -> 4-wood +0 (truth 4-wood -2; regret 0.0646 -> 0.0082); 5 [L; p L 0.25 R 0.10; value 0.027]: Driver +0 -> 4-wood +2 (truth 4-wood +2; regret 0.1025 -> -0.0008); 1 [none; p L 0.25 R 0.25; value 0.026]: Driver -2 -> Driver -2 (truth Driver -5; regret 0.0008 -> 0.0008)
- **prairie_dunes** (ASK 6): 5 [both; p L 0.90 R 0.90; value 0.048]: Driver -10 -> 4-wood -12 (truth 4-wood -12; regret 0.0809 -> 0.0014); 3 [both; p L 0.75 R 0.75; value 0.033]: 4-wood +8 -> 4-wood +8 (truth Driver -2; regret 0.0591 -> 0.0591); 1 [both; p L 0.75 R 0.75; value 0.023]: Driver +20 -> 4-wood +38 (truth 4-wood +30; regret 0.2064 -> 0.0033); 13 [both; p L 0.75 R 0.75; value 0.017]: 4-wood +20 -> 4-wood +20 (truth 4-wood +22; regret 0.013 -> 0.013); 7 [both; p L 0.90 R 0.90; value 0.012]: 4-wood -2 -> 4-wood -2 (truth 4-wood -5; regret 0.0037 -> 0.0037); 8 [both; p L 0.75 R 0.75; value 0.010]: 4-wood -32 -> 4-wood -35 (truth 4-wood -32; regret 0.0035 -> 0.0009)
- **buffalo_dunes** (ASK 6): 13 [both; p L 0.75 R 0.75; value 0.050]: 4-wood -10 -> 4-wood -10 (truth 4-wood -10; regret 0.0025 -> 0.0025); 10 [both; p L 0.75 R 0.75; value 0.038]: 4-wood -15 -> 4-wood -18 (truth 4-wood -20; regret 0.0252 -> 0.0022); 16 [both; p L 0.75 R 0.75; value 0.024]: 4-wood -10 -> 4-wood -10 (truth 4-wood -10; regret -0.001 -> -0.001); 5 [both; p L 0.75 R 0.75; value 0.021]: Driver +38 -> 4-wood +38 (truth 4-wood +40; regret 0.0477 -> 0.0113); 14 [both; p L 0.75 R 0.75; value 0.018]: 4-wood -8 -> 4-wood -8 (truth 4-wood -10; regret -0.0003 -> -0.0003); 1 [both; p L 0.75 R 0.75; value 0.014]: Driver -8 -> Driver -5 (truth Driver -2; regret 0.0176 -> 0.0026)
- **mariah_hills** (ASK 6): 1 [L; p L 0.90 R 0.75; value 0.476]: Driver +18 -> Driver +28 (truth Driver +20; regret -0.0008 -> 0.0301); 9 [both; out R; p L 0.90 R 0.90; value 0.120]: Driver -40 -> 4-wood +30 (truth Driver -38; regret 0.1671 -> None); 14 [both; out both; p L 0.90 R 0.90; value 0.090]: Driver +5 -> 4-wood -5 (truth 4-wood -5; regret 0.0274 -> 0.0032); 10 [R; out R; p L 0.40 R 0.75; value 0.042]: Driver +5 -> 4-wood -2 (truth Driver -2; regret 0.0382 -> 0.0119); 18 [both; p L 0.90 R 0.75; value 0.035]: Driver +15 -> 4-wood +10 (truth Driver +15; regret 0.001 -> 0.061); 12 [L; out L; p L 0.90 R 0.40; value 0.034]: Driver +5 -> Driver +10 (truth Driver +0; regret 0.0094 -> 0.0326)

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
