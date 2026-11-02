# Agent mapper evaluation (all)

Made 2026-11-02 09:54Z by `course_data/mapper/eval_mapper.py` (n = 4000, seed 31, aim tolerance 10 yds). AUTO = the package the mapper reviewed; AUTO + AGENT = the same package with the agent's layers; both scored against the all-truth plan by `platform/error_budget.score_course`. **Do not show this file to a mapper.**

## Pooled

| | tee shots | match | same club | same club or tie | regret (strokes) |
|---|---|---|---|---|---|
| AUTO | 98 | 50/98 (51%) | 63 | 68 | 6.165 |
| AUTO + AGENT | 98 | 66/98 (67%) | 73 | 82 | 2.253 |

Holes fixed by the agent: 18; broken: 2. Reference ties among all holes: 12.

Landing-corridor area vs truth (sq yds, 180-320 yds along the truth tee line, +/-50; summed over holes):

| layer | truth | AUTO missing / extra | AUTO + AGENT missing / extra |
|---|---|---|---|
| bunkers | 13206 | 1739 / 1424 | 1739 / 1649 |
| fairway | 475627 | 72368 / 8582 | 72368 / 8582 |
| long_grass | 305799 | 296477 / 13084 | 150926 / 33230 |
| ob | 5380 | 2397 / 10283 | 2397 / 8657 |
| trees | 129294 | 56115 / 13642 | 48998 / 17344 |
| water | 28177 | 2139 / 10494 | 2565 / 8433 |

## Per course

| course | set | mapper | tee shots | match AUTO -> AGENT | same club | regret | fixed | broken | tee err median (measured truth tees) |
|---|---|---|---|---|---|---|---|---|---|
| ellis | Blue | mapper-ellis (blind) | 14 | 11 -> 11 | 12 -> 12 | 0.375 -> 0.293 | - | - | 0.8 (14, 0 > 10) -> 0.8 (14, 0 > 10) |
| spirit_hollow | Black | mapper-spirit_hollow-3 | 14 | 7 -> 8 | 10 -> 11 | 0.892 -> 0.729 | 6 | - | 10.5 (14, 7 > 10) -> 10.5 (14, 7 > 10) |
| sand_creek_station | Championship | mapper-agent sand_creek_station (map3) | 14 | 12 -> 12 | 13 -> 13 | 0.259 -> 0.258 | - | - | 2.7 (3, 0 > 10) -> 2.7 (3, 0 > 10) |
| eagle_bend | Gold | mapper-eagle_bend | 14 | 7 -> 8 | 9 -> 9 | 0.515 -> 0.565 | 7 | - | 4.1 (7, 1 > 10) -> 4.1 (7, 1 > 10) |
| prairie_dunes | Blue | mapper-prairie_dunes-3 | 14 | 1 -> 7 | 2 -> 7 | 1.649 -> 0.720 | 7, 8, 12, 13, 16, 18 | - | 5.8 (4, 0 > 10) -> 5.8 (4, 0 > 10) |
| buffalo_dunes | Blue | mapper-buffalo_dunes-blue | 14 | 7 -> 13 | 7 -> 13 | 1.623 -> 0.208 | 7, 10, 13, 14, 15, 16 | - | 12.1 (2, 1 > 10) -> 12.1 (2, 1 > 10) |
| mariah_hills | Blue | mapper-mariah_hills-blue | 14 | 5 -> 7 | 10 -> 8 | 0.852 -> -0.520 | 1, 3, 14, 18 | 6, 10 | 2.3 (9, 0 > 10) -> 2.3 (9, 0 > 10) |

## Holes whose plan the agent changed

| course | hole | truth | AUTO | AUTO + AGENT | match | regret |
|---|---|---|---|---|---|---|
| ellis | 5 | Driver -2 | Driver +5 | Driver +2 | True -> True | 0.018 -> 0.0086 |
| ellis | 9 | Driver -2 | Driver +5 | Driver +0 | True -> True | 0.029 -> 0.0066 |
| ellis | 10 | Driver +2 | Driver +2 | Driver +5 | True -> True | 0.0 -> 0.0009 |
| ellis | 12 | Driver -5 | Driver -8 | Driver -5 | True -> True | 0.0044 -> -0.0 |
| ellis | 15 | 4-wood +12 | Driver +2 | Driver +10 | False -> False | 0.1044 -> 0.0575 |
| spirit_hollow | 4 | Driver -12 | Driver -5 | Driver -18 | False -> False | 0.0579 -> 0.0183 |
| spirit_hollow | 5 | 4-wood -8 | 4-wood -5 | 4-wood -2 | True -> True | 0.0001 -> 0.0013 |
| spirit_hollow | 6 | 4-wood -22 (tie) | Driver -40 | 4-wood -20 | False -> True | 0.1289 -> -0.0002 |
| spirit_hollow | 17 | Driver +12 (tie) | Driver +0 | Driver +2 | True -> True | 0.0007 -> 0.0051 |
| sand_creek_station | 1 | Driver -2 | Driver +10 | Driver -5 | True -> True | 0.0004 -> -0.0016 |
| sand_creek_station | 5 | Driver -8 | Driver -5 | Driver -8 | True -> True | -0.0002 -> -0.0 |
| sand_creek_station | 12 | Driver -2 | Driver -5 | Driver +0 | True -> True | 0.0018 -> 0.011 |
| sand_creek_station | 18 | 4-wood -2 | 4-wood -22 | 4-wood -20 | True -> True | 0.0257 -> 0.0135 |
| eagle_bend | 2 | 4-wood +0 | Driver +5 | Driver +10 | False -> False | 0.0973 -> 0.1549 |
| eagle_bend | 7 | Driver +5 | Driver -40 | Driver +5 | False -> True | 0.0072 -> 0.0 |
| eagle_bend | 9 | 4-wood +0 (tie) | Driver +0 | Driver -2 | False -> False | 0.0245 -> 0.0233 |
| prairie_dunes | 1 | 4-wood +32 | Driver +22 | Driver +20 | False -> False | 0.1643 -> 0.2064 |
| prairie_dunes | 3 | Driver -2 | Driver -12 | 4-wood +8 | False -> False | -0.0064 -> 0.0591 |
| prairie_dunes | 6 | 4-wood +15 | Driver +15 | Driver +10 | False -> False | 0.1183 -> 0.1333 |
| prairie_dunes | 7 | 4-wood -2 | Driver +5 | 4-wood -2 | False -> True | 0.0989 -> 0.0037 |
| prairie_dunes | 8 | 4-wood -32 | Driver -22 | 4-wood -32 | False -> True | 0.2014 -> 0.0035 |
| prairie_dunes | 11 | Driver +32 | Driver +28 | Driver +32 | True -> True | 0.0433 -> 0.0045 |
| prairie_dunes | 12 | 4-wood -2 | Driver +0 | 4-wood +0 | False -> True | 0.2271 -> 0.0162 |
| prairie_dunes | 13 | 4-wood +22 | Driver +2 | 4-wood +20 | False -> True | 0.1891 -> 0.013 |
| prairie_dunes | 14 | 4-wood +22 | Driver +0 | 2-wood +12 | False -> False | 0.1034 -> 0.0423 |
| prairie_dunes | 16 | 4-wood -28 | Driver -20 | 4-wood -28 | False -> True | 0.0934 -> -0.0005 |
| prairie_dunes | 17 | 4-wood +12 (tie) | Driver +10 | Driver +8 | False -> False | 0.004 -> 0.0171 |
| prairie_dunes | 18 | 4-wood -8 | Driver +2 | 4-wood -10 | False -> True | 0.2403 -> 0.0476 |
| buffalo_dunes | 1 | Driver -2 (tie) | Driver -5 | Driver -8 | True -> True | 0.0026 -> 0.0176 |
| buffalo_dunes | 2 | 4-wood +10 | 4-wood +10 | 4-wood +12 | True -> True | -0.0022 -> 0.0194 |
| buffalo_dunes | 3 | 4-wood +5 | 4-wood +5 | 4-wood +8 | True -> True | -0.005 -> 0.0024 |
| buffalo_dunes | 7 | 4-wood +18 (tie) | 2-wood +10 | 4-wood +18 | False -> True | 0.005 -> 0.0013 |
| buffalo_dunes | 10 | 4-wood -20 | Driver +8 | 4-wood -15 | False -> True | 0.5084 -> 0.0252 |
| buffalo_dunes | 13 | 4-wood -10 | Driver -5 | 4-wood -10 | False -> True | 0.1404 -> 0.0025 |
| buffalo_dunes | 14 | 4-wood -10 | Driver +12 | 4-wood -8 | False -> True | 0.4031 -> -0.0003 |
| buffalo_dunes | 15 | 4-wood +0 | Driver -8 | 4-wood +0 | False -> True | 0.2428 -> 0.0012 |
| buffalo_dunes | 16 | 4-wood -10 | Driver +5 | 4-wood -10 | False -> True | 0.1882 -> -0.001 |
| mariah_hills | 1 | Driver +20 | Driver +8 | Driver +12 | False -> True | 0.0197 -> 0.002 |
| mariah_hills | 2 | 4-wood +18 (tie) | Driver +12 | Driver +20 | False -> False | 0.0183 -> 0.0889 |
| mariah_hills | 3 | Driver +0 | Driver +10 | Driver +2 | False -> True | 0.0297 -> 0.0 |
| mariah_hills | 4 | 4-wood +2 | Driver +2 | Driver -2 | False -> False | 0.0313 -> 0.054 |
| mariah_hills | 6 | Driver -18 | Driver -18 | Driver -28 | True -> False | -0.0008 -> 0.0287 |
| mariah_hills | 7 | Driver +40 (tie) | Driver +0 | 4-wood +80 | False -> False | 0.6083 -> -0.7362 |
| mariah_hills | 9 | Driver -38 | Driver +28 | 4-wood +30 | False -> False | None -> None |
| mariah_hills | 10 | Driver -2 (tie) | Driver +5 | 4-wood +0 | True -> False | 0.0382 -> 0.0041 |
| mariah_hills | 12 | Driver +0 | Driver +0 | Driver +5 | True -> True | 0.0005 -> 0.0094 |
| mariah_hills | 13 | Driver +15 | Driver +0 | Driver -5 | True -> True | 0.0257 -> 0.0 |
| mariah_hills | 14 | 4-wood -5 | Driver -10 | 4-wood -5 | False -> True | 0.0301 -> 0.0032 |
| mariah_hills | 15 | 4-wood +20 | 4-wood +15 | 4-wood +18 | True -> True | 0.0046 -> -0.0002 |
| mariah_hills | 18 | Driver +15 | Driver +8 | Driver +10 | False -> True | 0.0435 -> 0.0224 |
