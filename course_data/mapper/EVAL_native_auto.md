# Automatic native sides: held-out plan value (product/native_auto.py)

Made 2026-11-03 16:50Z by `course_data/mapper/eval_native_auto.py` (two `--score` halves of one training set, merged) (n = 4000, seed 31, env {'DECIDE_ADAPTIVE_AIM': '0', 'V2_ADAPTIVE_AIM': '0'}). Leave-one-course-out p (side AUC 0.93); per held-out course the threshold is chosen on the other courses only (pooled side precision >= 0.9). **Truth-bearing: never show to a mapper.**

match / regret (strokes) over the corridor tee shots; taps asked in brackets; sides TP / FP / FN at the held-out threshold.

GATED = CLS only on courses where >= 0.25 of the sides reach the threshold (share column).

| course | thr | share | sides TP / FP / FN (pos) | AUTO | CLS | GATED | PRI+TAP2 | CLS+TAP2 | GATED+TAP2 | ORACLE |
|---|---|---|---|---|---|---|---|---|---|---|
| sand_creek_station | 0.7 | 0.607 on | 15 / 2 / 3 (18) | 12 / 0.259 | 12 / 0.293 | 12 / 0.293 | 13 / 0.258 (2) | 13 / 0.187 (2) | 13 / 0.187 (2) | 14 / 0.095 |
| prairie_dunes | 0.75 | 1.0 on | 28 / 0 / 0 (28) | 1 / 1.649 | 12 / 0.116 | 12 / 0.116 | 2 / 1.492 (2) | 12 / 0.116 (0) | 12 / 0.116 (0) | 12 / 0.116 |
| mariah_hills | 0.725 | 0.964 on | 23 / 4 / 0 (23) | 5 / 0.852 | 7 / -0.380 | 7 / -0.380 | 6 / -0.478 (2) | 7 / -0.380 (2) | 7 / -0.380 (2) | 8 / -0.464 |
| buffalo_dunes | 0.75 | 0.964 on | 27 / 0 / 1 (28) | 7 / 1.623 | 13 / 0.088 | 13 / 0.088 | 9 / 0.714 (2) | 13 / 0.088 (2) | 13 / 0.088 (2) | 13 / 0.062 |
| eagle_bend | 0.65 | 0.0 | 0 / 0 / 12 (12) | 7 / 0.515 | 7 / 0.515 | 7 / 0.515 | 9 / 0.254 (2) | 9 / 0.254 (2) | 9 / 0.254 (2) | 10 / 0.136 |
| ellis (control) | 0.7 | 0.071 | 0 / 2 / 5 (5) | 11 / 0.375 | 9 / 0.562 | 11 / 0.375 | 11 / 0.375 (2) | 9 / 0.562 (2) | 11 / 0.375 (2) | 11 / 0.428 |
| spirit_hollow (control) | 0.675 | 0.536 on | 11 / 4 / 7 (18) | 7 / 0.892 | 7 / 0.886 | 7 / 0.886 | 8 / 0.744 (2) | 9 / 0.290 (2) | 9 / 0.290 (2) | 9 / 0.379 |
| blue_hills (control) | 0.675 | 0.0 | 0 / 0 / 0 (0) | 14 / 0.051 | 14 / 0.051 | 14 / 0.051 | 14 / 0.051 (0) | 14 / 0.051 (0) | 14 / 0.051 (0) | 14 / 0.051 |
| eagle_knoll | 0.65 | 0.0 | 0 / 0 / 1 (1) | 14 / 0.026 | 14 / 0.026 | 14 / 0.026 | 14 / 0.026 (0) | 14 / 0.026 (0) | 14 / 0.026 (0) | 14 / 0.030 |
| gateway_national | 0.75 | 0.923 on | 23 / 1 / 1 (24) | 9 / 0.424 | 9 / 0.303 | 9 / 0.303 | 9 / 0.271 (2) | 10 / 0.169 (1) | 10 / 0.169 (1) | 10 / 0.158 |
| pine_dunes | 0.7 | 0.0 | 0 / 0 / 0 (0) | 11 / 0.099 | 11 / 0.099 | 11 / 0.099 | 11 / 0.099 (0) | 11 / 0.099 (0) | 11 / 0.099 (0) | 11 / 0.099 |
| veenker | 0.675 | 0.0 | 0 / 0 / 0 (0) | 9 / 0.193 | 9 / 0.193 | 9 / 0.193 | 9 / 0.193 (0) | 9 / 0.193 (0) | 9 / 0.193 (0) | 9 / 0.193 |
| coldwater | 0.7 | 0.571 on | 16 / 0 / 4 (20) | 10 / 0.472 | 10 / 0.416 | 10 / 0.416 | 10 / 0.430 (2) | 10 / 0.416 (2) | 10 / 0.416 (2) | 9 / 0.383 |
| la_nickell | 0.65 | 0.0 | 0 / 0 / 0 (0) | 10 / 0.142 | 10 / 0.142 | 10 / 0.142 | 10 / 0.142 (0) | 10 / 0.142 (0) | 10 / 0.142 (0) | 10 / 0.142 |
| rivercut | 0.675 | 0.0 | 0 / 0 / 0 (0) | 12 / 0.071 | 12 / 0.071 | 12 / 0.071 | 12 / 0.071 (2) | 12 / 0.071 (2) | 12 / 0.071 (2) | 12 / 0.071 |
| gustin | 0.65 | 0.0 | 0 / 0 / 0 (0) | 9 / 0.622 | 9 / 0.622 | 9 / 0.622 | 9 / 0.622 (0) | 9 / 0.622 (0) | 9 / 0.622 (0) | 9 / 0.622 |
| osage_national | 0.675 | 0.0 | 0 / 0 / 0 (0) | 11 / 0.227 | 11 / 0.227 | 11 / 0.227 | 11 / 0.227 (2) | 11 / 0.227 (2) | 11 / 0.227 (2) | 11 / 0.227 |
| annbriar | 0.725 | 0.071 | 2 / 0 / 14 (16) | 8 / 0.293 | 8 / 0.320 | 8 / 0.293 | 9 / 0.286 (2) | 9 / 0.313 (2) | 9 / 0.286 (2) | 10 / 0.180 |
| **pooled** | | | 145 / 13 / 48 (193) | **167 / 8.785** | **184 / 4.550** | **186 / 4.336** | **176 / 5.777** (24) | **191 / 3.446** (21) | **193 / 3.232** (21) | **196 / 2.908** |

## Holes whose plan changed (AUTO -> CLS; truth)

- **sand_creek_station**: 5 Driver -5 -> Driver -8 (truth Driver -8; -0.0002 -> -0.0); 8 Driver -32 -> 4-wood -32 (truth Driver -5; 0.0003 -> 0.0507; BROKEN); 10 Driver +12 -> 4-wood +0 (truth 4-wood +5; 0.0392 -> 0.0303; fixed); 11 4-wood -8 -> 4-wood -2 (truth 4-wood -5; 0.0036 -> 0.01); 12 Driver -5 -> Driver -2 (truth Driver -2; 0.0018 -> 0.0007); 15 Driver -35 -> Driver -32 (truth Driver -28; 0.0396 -> 0.0214); 16 Driver +5 -> Driver +8 (truth Driver +0; 0.0116 -> 0.0291); 18 4-wood -22 -> 4-wood -20 (truth 4-wood -2; 0.0257 -> 0.0135)
- **prairie_dunes**: 1 Driver +22 -> 4-wood +40 (truth 4-wood +32; 0.1643 -> 0.0101; fixed); 3 Driver -12 -> 4-wood +10 (truth Driver -2; -0.0064 -> 0.0688); 5 Driver -10 -> 4-wood -10 (truth 4-wood -12; 0.0796 -> 0.0036; fixed); 6 Driver +15 -> 4-wood +15 (truth 4-wood +15; 0.1183 -> 0.0057; fixed); 7 Driver +5 -> 4-wood -2 (truth 4-wood -2; 0.0989 -> 0.0035; fixed); 8 Driver -22 -> 4-wood -35 (truth 4-wood -32; 0.2014 -> -0.0006; fixed); 9 Driver -5 -> 4-wood -8 (truth 4-wood -8; 0.0922 -> 0.0037; fixed); 11 Driver +28 -> Driver +32 (truth Driver +32; 0.0433 -> 0.0045); 12 Driver +0 -> 4-wood -2 (truth 4-wood -2; 0.2271 -> -0.0054; fixed); 13 Driver +2 -> 4-wood +22 (truth 4-wood +22; 0.1891 -> 0.0009; fixed); 14 Driver +0 -> 4-wood +20 (truth 4-wood +22; 0.1034 -> 0.0008; fixed); 16 Driver -20 -> 4-wood -28 (truth 4-wood -28; 0.0934 -> -0.0005; fixed); 18 Driver +2 -> 4-wood -8 (truth 4-wood -8; 0.2403 -> 0.0172; fixed)
- **mariah_hills**: 1 Driver +8 -> 4-wood +15 (truth Driver +20; 0.0197 -> 0.1292); 2 Driver +12 -> 4-wood +22 (truth 4-wood +18; 0.0183 -> 0.0375; fixed); 3 Driver +10 -> Driver +8 (truth Driver +0; 0.0297 -> 0.0168; fixed); 4 Driver +2 -> 4-wood +8 (truth 4-wood +2; 0.0313 -> 0.0159; fixed); 6 Driver -18 -> Driver -20 (truth Driver -18; -0.0008 -> 0.0014); 7 Driver +0 -> 4-wood +82 (truth Driver +40; 0.6083 -> -0.7328); 9 Driver +28 -> 4-wood +30 (truth Driver -38; None -> None); 10 Driver +5 -> 4-wood -2 (truth Driver -2; 0.0382 -> 0.0119; BROKEN); 12 Driver +0 -> Driver +12 (truth Driver +0; 0.0005 -> 0.0454; BROKEN); 13 Driver +0 -> 4-wood +0 (truth Driver +15; 0.0257 -> 0.0219; BROKEN); 14 Driver -10 -> 4-wood -10 (truth 4-wood -5; 0.0301 -> 0.0047; fixed); 17 Driver -35 -> 4-wood -40 (truth 4-wood -40; 0.0033 -> 0.0024; fixed); 18 Driver +8 -> 4-wood +10 (truth Driver +15; 0.0435 -> 0.061)
- **buffalo_dunes**: 1 Driver -5 -> Driver -2 (truth Driver -2; 0.0026 -> 0.0008); 3 4-wood +5 -> 4-wood +10 (truth 4-wood +5; -0.005 -> 0.0287); 5 Driver +38 -> 4-wood +38 (truth 4-wood +40; 0.0477 -> 0.0113); 6 4-wood -25 -> 4-wood -32 (truth 4-wood -18; 0.0747 -> -0.0001); 7 2-wood +10 -> 4-wood +15 (truth 4-wood +18; 0.005 -> 0.0127; fixed); 9 4-wood +12 -> 4-wood +10 (truth 4-wood +10; 0.0024 -> 0.0006); 10 Driver +8 -> 4-wood -18 (truth 4-wood -20; 0.5084 -> 0.0029; fixed); 13 Driver -5 -> 4-wood -10 (truth 4-wood -10; 0.1404 -> 0.0025; fixed); 14 Driver +12 -> 4-wood -8 (truth 4-wood -10; 0.4031 -> -0.0003; fixed); 15 Driver -8 -> 4-wood -2 (truth 4-wood +0; 0.2428 -> 0.0; fixed); 16 Driver +5 -> 4-wood -10 (truth 4-wood -10; 0.1882 -> -0.001; fixed); 18 4-wood +12 -> 4-wood +15 (truth 4-wood +8; 0.0145 -> 0.0313)
- **eagle_bend**: no change
- **ellis**: 2 Driver +40 -> 4-wood +2 (truth Driver +40; 0.0006 -> 0.1668; BROKEN); 7 Driver +0 -> Driver -10 (truth Driver +0; 0.0 -> 0.0213; BROKEN)
- **spirit_hollow**: 4 Driver -5 -> 4-wood -5 (truth Driver -12; 0.0579 -> 0.0982); 5 4-wood -5 -> 4-wood -2 (truth 4-wood -8; 0.0001 -> 0.0013); 6 Driver -40 -> 4-wood -20 (truth 4-wood -22; 0.1289 -> -0.0002; fixed); 8 4-wood -8 -> 4-wood -2 (truth 4-wood -10; 0.0031 -> 0.0173); 10 4-wood +5 -> 4-wood +2 (truth 4-wood +8; 0.0097 -> 0.0361); 13 Driver +15 -> 4-wood +5 (truth Driver +5; 0.0256 -> 0.0101); 16 4-wood -2 -> 4-wood +2 (truth 4-wood -2; 0.0064 -> 0.0402); 17 Driver +0 -> 4-wood +0 (truth Driver +12; 0.0007 -> 0.0225; BROKEN)
- **blue_hills**: no change
- **eagle_knoll**: no change
- **gateway_national**: 2 Driver -2 -> Driver -5 (truth Driver +0; 0.0028 -> 0.0113); 3 Driver -10 -> 4-wood -5 (truth Driver -8; 0.0044 -> 0.0473; BROKEN); 5 Driver +0 -> Driver -2 (truth Driver -2; 0.0029 -> 0.0); 6 Driver +5 -> Driver +0 (truth Driver +5; 0.0 -> 0.0179); 9 2-wood +10 -> 2-wood +12 (truth 4-wood +0; 0.0987 -> 0.1359); 10 4-wood -25 -> 4-wood -22 (truth 4-wood -18; 0.0598 -> 0.0276); 11 Driver +22 -> 4-wood +8 (truth 4-wood +8; 0.1961 -> 0.0; fixed); 15 Driver +10 -> Driver +15 (truth Driver +15; 0.0062 -> 0.0); 16 4-wood +0 -> 4-wood +2 (truth 4-wood -2; 0.0024 -> 0.017); 18 Driver +15 -> Driver +20 (truth Driver +18; 0.0044 -> -0.0001)
- **pine_dunes**: no change
- **veenker**: no change
- **coldwater**: 2 Driver +5 -> 4-wood +8 (truth 4-wood +10; 0.0473 -> 0.0004; fixed); 6 Driver +5 -> Driver -2 (truth Driver +2; 0.0021 -> 0.0026); 7 Driver +2 -> Driver -8 (truth Driver -5; 0.0357 -> -0.0004); 10 Driver -8 -> 4-wood +0 (truth 4-wood -15; 0.2347 -> 0.1924); 12 Driver +2 -> Driver +8 (truth Driver +0; 0.003 -> 0.0242); 13 Driver +2 -> Driver +0 (truth Driver +8; 0.0069 -> 0.0257); 14 Driver +2 -> Driver -8 (truth Driver -2; 0.0128 -> 0.0203); 15 Driver -2 -> Driver -8 (truth Driver -2; 0.0 -> 0.0057); 17 4-wood +12 -> 4-wood +5 (truth 4-wood +5; 0.0171 -> -0.0001); 18 Driver -8 -> 4-wood -8 (truth Driver -10; 0.0001 -> 0.0331; BROKEN)
- **la_nickell**: no change
- **rivercut**: no change
- **gustin**: no change
- **osage_national**: no change
- **annbriar**: 2 Driver +2 -> Driver +8 (truth 4-wood +5; -0.001 -> 0.0266)
