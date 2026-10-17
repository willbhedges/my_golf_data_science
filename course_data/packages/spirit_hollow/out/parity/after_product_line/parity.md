# Decision parity: product vs hand pipeline on the hand map (Black tees)

Both through product/decide.quick_hole (n=8000, seed 31, prior-mean settings): every difference is an input difference. Product tee line: product rule (250 yds along the hole line). Aims are yds right of the hand (app) tee line at the club's carry.

**Same club 13/14; same or tie 14/14; aims within 2.5 yds on 11/13 same-club holes.**

| hole | hand | product | same | tee err | bearing diff | ground/app yd | green err | lies agree (given order) | causes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4-wood -2.5 | 4-wood -1.7 | yes | 0.2 | +2.4 | 1.004 | 1.5 | 100% (100%) | - |
| 2F | Driver -20.0 | Driver -17.3 | yes | 0.0 | +3.7 | 1.002 | 2.5 | 100% (100%) | - |
| 4 | Driver -2.5 | Driver -3.1 | yes | 0.0 | +2.0 | 0.992 | 3.4 | 100% (100%) | - |
| 5 | 4-wood -5.0 | 4-wood -6.0 | yes | 0.1 | +0.3 | 0.985 | 5.1 | 100% (100%) | - |
| 6 | 4-wood (tie) -7.5 | 2-wood (tie) -7.6 | tie | 0.4 | +3.3 | 0.969 | 14.4 | 100% (100%) | - |
| 8 | 4-wood +5.0 | 4-wood +4.3 | yes | 0.0 | +3.2 | 0.997 | 5.9 | 100% (100%) | - |
| 9F | 4-wood -10.0 | 4-wood -8.7 | yes | 0.0 | -2.0 | 1.001 | 2.9 | 100% (100%) | - |
| 10 | 4-wood -0.0 | 4-wood +1.0 | yes | 0.2 | -1.5 | 0.983 | 10.5 | 100% (100%) | - |
| 11 | Long iron -0.0 | Long iron -0.0 | yes | 0.0 | -0.7 | 1.001 | 3.9 | 100% (100%) | - |
| 13 | Driver (tie) -12.5 | Driver (tie) -9.2 | yes | 0.0 | -2.9 | 0.989 | 3.5 | 100% (100%) | - |
| 14 | 4-wood (tie) -17.5 | 4-wood (tie) -16.9 | yes | 0.0 | -0.4 | 0.994 | 5.4 | 100% (100%) | - |
| 16 | 4-wood -5.0 | 4-wood -5.0 | yes | 0.3 | -0.6 | 1.025 | 1.7 | 100% (100%) | - |
| 17 | Driver (tie) +2.5 | Driver (tie) +0.6 | yes | 0.1 | -2.5 | 0.988 | 2.6 | 100% (100%) | - |
| 18 | 4-wood (tie) -7.5 | 4-wood (tie) -8.0 | yes | 0.0 | +1.6 | 1.001 | 1.5 | 100% (100%) | - |

## EV per club (hand / product)

| hole | Driver | 2-wood | 4-wood | Long iron | Mid iron |
|---|---|---|---|---|---|
| 1 | 4.083 / 4.072 | 4.046 / 4.016 | 3.957 / 3.938 | nan / nan | nan / nan |
| 2F | 4.325 / 4.364 | 4.399 / 4.440 | 4.436 / 4.476 | nan / nan | nan / nan |
| 4 | 4.582 / 4.591 | 4.637 / 4.645 | 4.638 / 4.647 | nan / nan | nan / nan |
| 5 | 3.935 / 3.944 | 3.894 / 3.904 | 3.874 / 3.877 | nan / nan | nan / nan |
| 6 | 3.922 / 3.971 | 3.916 / 3.923 | 3.915 / 3.925 | nan / nan | nan / nan |
| 8 | 4.013 / 4.011 | 3.961 / 3.958 | 3.894 / 3.900 | nan / nan | nan / nan |
| 9F | 4.143 / 4.166 | 3.935 / 3.907 | 3.867 / 3.863 | nan / nan | nan / nan |
| 10 | 4.521 / 4.537 | 4.558 / 4.572 | 4.508 / 4.522 | nan / nan | nan / nan |
| 11 | 4.687 / 4.651 | 4.585 / 4.558 | 4.043 / 4.145 | 3.874 / 3.884 | 3.946 / 3.960 |
| 13 | 4.016 / 4.016 | 4.033 / 4.034 | 4.019 / 4.023 | 4.126 / nan | 4.272 / nan |
| 14 | 3.879 / 3.910 | 3.883 / 3.912 | 3.877 / 3.901 | nan / nan | nan / nan |
| 16 | 3.925 / 3.937 | 3.913 / 3.934 | 3.889 / 3.916 | nan / nan | nan / nan |
| 17 | 4.045 / 4.047 | 4.054 / 4.053 | 4.073 / 4.070 | nan / nan | nan / nan |
| 18 | 4.666 / 4.668 | 4.592 / 4.595 | 4.585 / 4.591 | nan / 4.780 | nan / 4.818 |

## Inputs per hole

| hole | IoU fairway / first cut / trees / long grass / water / sand / OB | zones hand / product | irons hand / product | aims hand / product | elev Driver hand / product (carry, roll x, kick) |
|---|---|---|---|---|---|
| 1 | 0.982 / 0.948 / 1.0 / 0.998 / - / - / - | 11 / 11 | False / False | [-40, 40] / [-60, 60] | (17.3, 1.3, 0.0) / (16.1, 1.3, -0.0) |
| 2F | 1.0 / 1.0 / 0.999 / 0.999 / 0.999 / 1.0 / 1.0 | 14 / 14 | False / False | [-40, 40] / [-60, 60] | (14.9, 0.73, 0.0) / (9.1, 0.7, -0.0) |
| 4 | 0.996 / 0.951 / 1.0 / 1.0 / - / - / 1.0 | 11 / 11 | False / False | [-40, 40] / [-60, 60] | (-6.1, 0.84, 0.0) / (-6.0, 0.85, -0.0) |
| 5 | 0.999 / 0.996 / 1.0 / 0.999 / - / 1.0 / 1.0 | 13 / 13 | False / False | [-40, 40] / [-60, 60] | (-2.5, 0.86, 0.0) / (-3.6, 0.86, -0.0) |
| 6 | 0.999 / 0.997 / 1.0 / 0.999 / - / - / - | 10 / 10 | False / False | [-40, 40] / [-60, 60] | (5.4, 1.17, 0.0) / (3.1, 1.08, -0.0) |
| 8 | 0.992 / 0.983 / 1.0 / 0.998 / - / 1.0 / 1.0 | 12 / 12 | False / False | [-40, 40] / [-60, 60] | (-5.6, 0.99, 0.0) / (-6.5, 0.77, -0.0) |
| 9F | 0.993 / 0.976 / 0.998 / 0.998 / 0.999 / - / - | 17 / 17 | False / False | [-40, 40] / [-60, 60] | (10.7, 0.7, 0.0) / (9.7, 0.7, 0.0) |
| 10 | 0.998 / 0.99 / 0.994 / 0.995 / 0.994 / 1.0 / - | 8 / 8 | False / False | [-40, 40] / [-60, 60] | (11.2, 0.98, 0.0) / (6.3, 0.96, -0.0) |
| 11 | 0.995 / 0.991 / 1.0 / 1.0 / 1.0 / - / - | 13 / 13 | True / True | [-40, 40] / [-60, 60] | (-0.9, 1.04, 0.0) / (-0.4, 0.7, -0.0) |
| 13 | 0.988 / 0.974 / 0.998 / - / 0.999 / 0.988 / - | 9 / 9 | True / False | [-40, 40] / [-60, 60] | (12.0, 0.7, 0.0) / (10.9, 0.7, 0.0) |
| 14 | 0.992 / 0.989 / 1.0 / 1.0 / 1.0 / - / - | 6 / 6 | False / False | [-40, 40] / [-60, 60] | (21.8, 1.26, 0.0) / (18.3, 1.12, 0.0) |
| 16 | 0.99 / 0.983 / 0.999 / 0.996 / 1.0 / 0.994 / - | 13 / 13 | False / False | [-40, 40] / [-60, 60] | (5.4, 0.77, 0.0) / (5.4, 0.72, 0.0) |
| 17 | 0.99 / 0.978 / 0.996 / 1.0 / - / 0.983 / - | 10 / 10 | False / False | [-40, 40] / [-60, 60] | (2.6, 0.89, 0.0) / (0.6, 0.77, 0.0) |
| 18 | 0.992 / 0.967 / 1.0 / 0.998 / 0.992 / 1.0 / - | 12 / 12 | False / True | [-40, 40] / [-60, 60] | (23.5, 0.7, 0.0) / (23.7, 0.7, 0.0) |

## Model settings

| setting | product quick (decide.py) | hand calm cell (wind_grid.py) | hand final (final_decision.py) |
|---|---|---|---|
| driver width (yds, 95%) | 70.0 (65 x 70/65) | 70 (wind_grid.set_prior_means) | Sobol prior, median 70, 90% to 80 |
| carry depth | 35.0 (x1.25) | x1.25 | prior depth / 1.5 x 1.25 |
| tree severity / long grass lost | 0.8 / 0.5 | 0.8 / 0.5 | prior draws |
| mishit rate | 0.15 | 0.15 | prior draws |
| baselines | tour | tour (default) | tour (hcp False) |
| LONG_SLOPE / FIRST_CUT_COST | 0.0035 / 0.35 | same module | same module |
| swings, seed | 8000, 31 (decide._z) | 4000, 31 (same draw layout) | 3000 per draw, 128 draws, seed 2027 |
| wood aims | +/-60 capped by the hole's aim_min/max, 2.5 step, widened past the edge | -30..+30, 2.5 step | decision.aims_for: hole aim_min/max capped to +/-25 |
| iron aims | -25..+45 | -30..+45 | -25..+45 |
| irons offered | package.irons_offered: water / OB across the tee line 180-310 yds (or the package flag) | course.HOLES[h]['irons'] (11, 13) | same |
| absurd-aim guard | yes (40 yds; aim point lie; play_line) | no | no |
