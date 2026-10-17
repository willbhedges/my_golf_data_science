# Decision parity: product vs hand pipeline on the hand map (Black tees)

Both through product/decide.quick_hole (n=8000, seed 31, prior-mean settings): every difference is an input difference. Product tee line: product rule (250 yds along the hole line). Aims are yds right of the hand (app) tee line at the club's carry.

**Same club 8/14; same or tie 10/14; aims within 2.5 yds on 5/8 same-club holes.**

| hole | hand | product | same | tee err | bearing diff | ground/app yd | green err | lies agree (given order) | causes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4-wood -2.5 | 4-wood +5.6 | yes | 0.2 | +2.4 | 1.004 | 1.5 | 91% (100%) | - |
| 2F | Driver -20.0 | Driver -17.3 | yes | 0.0 | +3.7 | 1.002 | 2.5 | 86% (100%) | - |
| 4 | Driver -2.5 | Driver -3.1 | yes | 0.0 | +2.0 | 0.992 | 3.4 | 98% (100%) | - |
| 5 | 4-wood -5.0 | 4-wood -6.0 | yes | 0.1 | +0.3 | 0.985 | 5.1 | 93% (100%) | - |
| 6 | 4-wood (tie) -7.5 | 2-wood (tie) -5.1 | tie | 0.4 | +3.3 | 0.969 | 14.4 | 93% (100%) | scale (alone fixes), elev (alone fixes) |
| 8 | 4-wood +5.0 | 4-wood +6.8 | yes | 0.0 | +3.2 | 0.997 | 5.9 | 89% (100%) | - |
| 9F | 4-wood -10.0 | 4-wood (tie) -11.2 | yes | 0.0 | -2.0 | 1.001 | 2.9 | 89% (100%) | - |
| 10 | 4-wood -0.0 | Driver -7.1 | **no** | 0.2 | -1.5 | 0.983 | 10.5 | 92% (100%) | tee (needed), line (needed), scale (needed), zones (alone fixes) (needed), order (alone fixes) (needed), elev (needed), green (needed), irons (needed), aims (needed), guard (needed) |
| 11 | Long iron -0.0 | 4-wood -5.6 | **no** | 0.0 | -0.7 | 1.001 | 3.9 | 85% (100%) | irons (alone fixes) (needed) |
| 13 | Driver (tie) -12.5 | 4-wood (tie) -13.1 | tie | 0.0 | -2.9 | 0.989 | 3.5 | 86% (100%) | scale (alone fixes), zones (alone fixes), order (alone fixes), elev (alone fixes) |
| 14 | 4-wood (tie) -17.5 | 2-wood -29.6 | **no** | 0.0 | -0.4 | 0.994 | 5.4 | 87% (100%) | elev (alone fixes) (needed) |
| 16 | 4-wood -5.0 | 4-wood (tie) -5.0 | yes | 0.3 | -0.6 | 1.025 | 1.7 | 90% (100%) | - |
| 17 | Driver (tie) +2.5 | Driver -1.9 | yes | 0.1 | -2.5 | 0.988 | 2.6 | 88% (100%) | - |
| 18 | 4-wood (tie) -7.5 | Driver -2.5 | **no** | 0.0 | +1.6 | 1.001 | 1.5 | 90% (100%) | zones (alone fixes), order (alone fixes) |

## Ladder (pick / aim on the hand line, one factor at a time)

| hole | all hand | only tee | only line | only scale | only zones | only order | only elev | only green | only irons | only aims | only guard | all but tee | all but line | all but scale | all but zones | all but order | all but elev | all but green | all but irons | all but aims | all but guard |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4-wood -0 | 4-wood +6 | 4-wood +7 | 4-wood +7 | 4-wood +6 | 4-wood +6 | 4-wood -2 | 4-wood +6 | 4-wood +6 | 4-wood +6 | 4-wood +6 | 4-wood -0 | 4-wood -2 | 4-wood -2 | 4-wood -0 | 4-wood -0 | 4-wood +7 | 4-wood -0 | 4-wood -0 | 4-wood -0 | 4-wood -0 |
| 2F | Driver -18 | Driver -17 | Driver -13 | Driver -13 | Driver -15 | Driver -15 | Driver -20 | Driver -17 | Driver -17 | Driver -17 | Driver -17 | Driver -18 | Driver -20 | Driver -18 | Driver -18 | Driver -18 | Driver -13 | Driver -18 | Driver -18 | Driver -18 | Driver -18 |
| 4 | Driver -2 | Driver -3 | Driver -2 | Driver -2 | Driver -3 | Driver -3 | Driver -3 | Driver -3 | Driver -3 | Driver -3 | Driver -3 | Driver -2 | Driver -3 | Driver -2 | Driver -2 | Driver -2 | Driver -2 | Driver -2 | Driver -2 | Driver -2 | Driver -2 |
| 5 | 4-wood -8 | 4-wood -6 | 4-wood -5 | 4-wood -5 | 4-wood -6 | 4-wood -6 | 4-wood -6 | 4-wood -6 | 4-wood -6 | 4-wood -6 | 4-wood -6 | 4-wood -8 | 4-wood -6 | 4-wood -5 | 4-wood -8 | 4-wood -8 | 4-wood -5 | 4-wood -8 | 4-wood -8 | 4-wood -8 | 4-wood -8 |
| 6 | 4-wood -8 | 2-wood -5 | 2-wood -5 | 4-wood -5 | 2-wood -5 | 2-wood -5 | 4-wood -11 | 2-wood -5 | 2-wood -5 | 2-wood -5 | 2-wood -5 | 4-wood -8 | 4-wood -8 | 4-wood -8 | 4-wood -8 | 4-wood -8 | 4-wood -5 | 4-wood -8 | 4-wood -8 | 4-wood -8 | 4-wood -8 |
| 8 | 4-wood +5 | 4-wood +7 | 4-wood +5 | 4-wood +5 | 4-wood +9 | 4-wood +9 | 4-wood +4 | 4-wood +7 | 4-wood +7 | 4-wood +7 | 4-wood +7 | 4-wood +5 | 4-wood +4 | 4-wood +5 | 4-wood +5 | 4-wood +5 | 4-wood +10 | 4-wood +5 | 4-wood +5 | 4-wood +5 | 4-wood +5 |
| 9F | 4-wood -10 | 4-wood -11 | 4-wood -12 | 4-wood -12 | 4-wood -14 | 4-wood -14 | 4-wood -9 | 4-wood -11 | 4-wood -11 | 4-wood -11 | 4-wood -11 | 4-wood -10 | 4-wood -9 | 4-wood -8 | 4-wood -10 | 4-wood -10 | 4-wood -15 | 4-wood -10 | 4-wood -10 | 4-wood -10 | 4-wood -10 |
| 10 | Driver -8 | Driver -7 | Driver -8 | Driver -10 | 4-wood +1 | 4-wood +1 | Driver -10 | Driver -7 | Driver -7 | Driver -7 | Driver -7 | Driver -8 | Driver -7 | Driver -8 | Driver -8 | Driver -8 | Driver -5 | Driver -8 | Driver -8 | Driver -8 | Driver -8 |
| 11 | Long iron -0 | 4-wood -6 | 4-wood -5 | 4-wood -5 | 4-wood -3 | 4-wood -3 | 4-wood -6 | 4-wood -6 | Long iron -0 | 4-wood -6 | 4-wood -6 | Long iron -0 | Long iron -0 | Long iron -0 | Long iron -0 | Long iron -0 | Long iron +2 | Long iron -0 | 4-wood -2 | Long iron -0 | Long iron -0 |
| 13 | Driver -10 | 4-wood -13 | 4-wood -12 | Driver -13 | Driver -9 | Driver -9 | Driver -9 | 4-wood -13 | 4-wood -13 | 4-wood -13 | 4-wood -13 | Driver -10 | Driver -9 | Driver -10 | Driver -10 | Driver -10 | Driver -10 | Driver -10 | Driver -10 | Driver -10 | Driver -10 |
| 14 | 4-wood -18 | 2-wood -30 | 2-wood -30 | 2-wood -30 | 2-wood -30 | 2-wood -30 | 4-wood -17 | 2-wood -30 | 2-wood -30 | 2-wood -30 | 2-wood -30 | 4-wood -18 | 4-wood -17 | 4-wood -18 | 4-wood -18 | 4-wood -18 | 2-wood -30 | 4-wood -18 | 4-wood -18 | 4-wood -18 | 4-wood -18 |
| 16 | 4-wood -5 | 4-wood -5 | 4-wood -5 | Driver -7 | 4-wood -5 | 4-wood -5 | 4-wood -3 | 4-wood -5 | 4-wood -5 | 4-wood -5 | 4-wood -5 | 4-wood -5 | 4-wood -5 | 4-wood -5 | 4-wood -5 | 4-wood -5 | 4-wood -5 | 4-wood -5 | 4-wood -5 | 4-wood -5 | 4-wood -5 |
| 17 | 2-wood +2 | Driver -2 | Driver -2 | Driver +0 | 2-wood -4 | 2-wood -4 | Driver +3 | Driver -2 | Driver -2 | Driver -2 | Driver -2 | 2-wood +2 | 2-wood +1 | Driver +2 | 2-wood +2 | 2-wood +2 | 4-wood -8 | 2-wood +2 | 2-wood +2 | 2-wood +2 | 2-wood +2 |
| 18 | 4-wood -7 | Driver -2 | Driver -0 | Driver -0 | 4-wood -8 | 4-wood -8 | Driver -0 | Driver -2 | Driver -2 | Driver -2 | Driver -2 | 4-wood -7 | 4-wood -8 | 4-wood -7 | 4-wood -7 | 4-wood -7 | 4-wood -10 | 4-wood -7 | 4-wood -7 | 4-wood -7 | 4-wood -7 |

## EV per club (hand / product)

| hole | Driver | 2-wood | 4-wood | Long iron | Mid iron |
|---|---|---|---|---|---|
| 1 | 4.083 / 3.954 | 4.046 / 3.899 | 3.957 / 3.882 | nan / nan | nan / nan |
| 2F | 4.325 / 4.347 | 4.399 / 4.418 | 4.436 / 4.446 | nan / nan | nan / nan |
| 4 | 4.582 / 4.585 | 4.637 / 4.635 | 4.638 / 4.634 | nan / nan | nan / nan |
| 5 | 3.935 / 3.927 | 3.894 / 3.890 | 3.874 / 3.866 | nan / nan | nan / nan |
| 6 | 3.922 / 3.964 | 3.916 / 3.911 | 3.915 / 3.914 | nan / nan | nan / nan |
| 8 | 4.013 / 3.992 | 3.961 / 3.938 | 3.894 / 3.878 | nan / nan | nan / nan |
| 9F | 4.143 / 3.875 | 3.935 / 3.833 | 3.867 / 3.826 | nan / nan | nan / nan |
| 10 | 4.521 / 4.413 | 4.558 / 4.449 | 4.508 / 4.442 | nan / nan | nan / nan |
| 11 | 4.687 / 4.637 | 4.585 / 4.448 | 4.043 / 4.167 | 3.874 / nan | 3.946 / nan |
| 13 | 4.016 / 3.991 | 4.033 / 4.014 | 4.019 / 3.990 | 4.126 / nan | 4.272 / nan |
| 14 | 3.879 / 3.992 | 3.883 / 3.921 | 3.877 / 3.944 | nan / nan | nan / nan |
| 16 | 3.925 / 3.912 | 3.913 / 3.916 | 3.889 / 3.909 | nan / nan | nan / nan |
| 17 | 4.045 / 4.006 | 4.054 / 4.026 | 4.073 / 4.040 | nan / nan | nan / nan |
| 18 | 4.666 / 4.481 | 4.592 / 4.551 | 4.585 / 4.550 | nan / nan | nan / nan |

## Inputs per hole

| hole | IoU fairway / first cut / trees / long grass / water / sand / OB | zones hand / product | irons hand / product | aims hand / product | elev Driver hand / product (carry, roll x, kick) |
|---|---|---|---|---|---|
| 1 | 0.679 / 0.0 / 0.963 / 0.816 / - / - / - | 11 / 11 | False / False | [-40, 40] / [-60, 60] | (17.3, 1.3, 0.0) / (18.2, 2.0, -15.0) |
| 2F | 0.677 / 0.0 / 0.971 / 0.864 / 0.999 / 1.0 / 1.0 | 14 / 14 | False / False | [-40, 40] / [-60, 60] | (14.9, 0.73, 0.0) / (9.1, 0.57, -5.1) |
| 4 | 0.903 / 0.0 / 1.0 / 1.0 / - / - / 1.0 | 11 / 11 | False / False | [-40, 40] / [-60, 60] | (-6.1, 0.84, 0.0) / (-5.7, 0.82, -0.1) |
| 5 | 0.841 / 0.0 / 1.0 / 0.999 / - / 0.986 / 1.0 | 13 / 13 | False / False | [-40, 40] / [-60, 60] | (-2.5, 0.86, 0.0) / (-2.9, 0.9, -1.2) |
| 6 | 0.85 / 0.0 / 0.777 / 0.719 / - / - / - | 10 / 10 | False / False | [-40, 40] / [-60, 60] | (5.4, 1.17, 0.0) / (4.0, 1.05, -10.6) |
| 8 | 0.69 / 0.0 / 1.0 / 0.99 / - / 1.0 / 0.991 | 12 / 12 | False / False | [-40, 40] / [-60, 60] | (-5.6, 0.99, 0.0) / (-6.3, 0.77, -5.5) |
| 9F | 0.667 / 0.002 / 0.591 / 0.973 / 0.911 / - / - | 17 / 17 | False / False | [-40, 40] / [-60, 60] | (10.7, 0.7, 0.0) / (9.2, 0.57, 3.9) |
| 10 | 0.778 / 0.0 / 0.99 / 0.238 / 0.994 / 1.0 / - | 8 / 8 | False / False | [-40, 40] / [-60, 60] | (11.2, 0.98, 0.0) / (5.7, 0.95, -2.1) |
| 11 | 0.601 / 0.0 / 0.966 / 0.24 / 1.0 / - / - | 13 / 13 | True / False | [-40, 40] / [-60, 60] | (-0.9, 1.04, 0.0) / (-0.6, 0.67, -2.0) |
| 13 | 0.693 / 0.003 / 0.968 / - / 0.979 / 0.988 / - | 9 / 9 | True / False | [-40, 40] / [-60, 60] | (12.0, 0.7, 0.0) / (10.6, 0.52, 5.4) |
| 14 | 0.573 / 0.0 / 0.999 / 0.997 / 1.0 / - / - | 6 / 6 | False / False | [-40, 40] / [-60, 60] | (21.8, 1.26, 0.0) / (22.3, 1.15, 10.0) |
| 16 | 0.639 / 0.0 / 0.998 / 0.996 / 1.0 / 0.994 / - | 13 / 13 | False / False | [-40, 40] / [-60, 60] | (5.4, 0.77, 0.0) / (5.4, 0.56, 1.8) |
| 17 | 0.697 / 0.0 / 0.893 / 1.0 / - / 0.983 / - | 10 / 10 | False / False | [-40, 40] / [-60, 60] | (2.6, 0.89, 0.0) / (2.6, 0.86, 8.4) |
| 18 | 0.763 / 0.0 / 1.0 / 0.91 / 0.782 / 1.0 / - | 12 / 12 | False / False | [-40, 40] / [-60, 60] | (23.5, 0.7, 0.0) / (23.8, 0.62, 2.6) |

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
