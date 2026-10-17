# Decision parity: product vs hand pipeline on the hand map (Black tees)

Both through product/decide.quick_hole (n=8000, seed 31, prior-mean settings): every difference is an input difference. Product tee line: product rule (250 yds along the hole line). Aims are yds right of the hand (app) tee line at the club's carry.

**Same club 13/14; same or tie 14/14; aims within 2.5 yds on 9/13 same-club holes.**

| hole | hand | product | same | tee err | bearing diff | ground/app yd | green err | lies agree (given order) | causes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4-wood -2.5 | 4-wood +5.6 | yes | 0.2 | +2.4 | 1.004 | 1.5 | 100% (100%) | - |
| 2F | Driver -17.5 | Driver -14.8 | yes | 0.0 | +3.7 | 1.002 | 2.5 | 100% (100%) | - |
| 4 | Driver -5.0 | Driver -3.1 | yes | 0.0 | +2.0 | 0.992 | 3.4 | 100% (100%) | - |
| 5 | 4-wood -5.0 | 4-wood -6.0 | yes | 0.1 | +0.3 | 0.985 | 5.1 | 100% (100%) | - |
| 6 | 2-wood (tie) -2.5 | 2-wood (tie) -5.1 | yes | 0.4 | +3.3 | 0.969 | 14.4 | 100% (100%) | - |
| 8 | 4-wood +7.5 | 4-wood +9.4 | yes | 0.0 | +3.2 | 0.997 | 5.9 | 100% (100%) | - |
| 9F | 4-wood -17.5 | 4-wood -13.7 | yes | 0.0 | -2.0 | 1.001 | 2.9 | 100% (100%) | - |
| 10 | 4-wood (tie) +2.5 | 4-wood (tie) +1.0 | yes | 0.2 | -1.5 | 0.983 | 10.5 | 100% (100%) | - |
| 11 | Long iron +2.5 | Long iron -0.0 | yes | 0.0 | -0.7 | 1.001 | 3.9 | 100% (100%) | - |
| 13 | Driver (tie) -10.0 | Driver (tie) -9.2 | yes | 0.0 | -2.9 | 0.989 | 3.5 | 100% (100%) | - |
| 14 | 4-wood -17.5 | 4-wood -16.9 | yes | 0.0 | -0.4 | 0.994 | 5.4 | 100% (100%) | - |
| 16 | 2-wood (tie) -12.5 | Driver (tie) -10.1 | tie | 0.3 | -0.6 | 1.025 | 1.7 | 100% (100%) | - |
| 17 | 2-wood (tie) -5.0 | 2-wood (tie) -4.0 | yes | 0.1 | -2.5 | 0.988 | 2.6 | 100% (100%) | - |
| 18 | 4-wood -7.5 | 4-wood (tie) -8.0 | yes | 0.0 | +1.6 | 1.001 | 1.5 | 100% (100%) | - |

## EV per club (hand / product)

| hole | Driver | 2-wood | 4-wood | Long iron | Mid iron |
|---|---|---|---|---|---|
| 1 | 4.033 / 3.992 | 4.016 / 3.965 | 3.951 / 3.917 | nan / 4.038 | nan / 4.167 |
| 2F | 4.321 / 4.369 | 4.392 / 4.443 | 4.430 / 4.474 | nan / 4.719 | nan / 4.834 |
| 4 | 4.580 / 4.591 | 4.635 / 4.645 | 4.636 / 4.647 | nan / 4.825 | nan / 4.911 |
| 5 | 3.936 / 3.942 | 3.894 / 3.903 | 3.874 / 3.876 | nan / 4.033 | nan / 4.186 |
| 6 | 3.915 / 3.966 | 3.911 / 3.919 | 3.912 / 3.924 | nan / 4.126 | nan / 4.279 |
| 8 | 4.007 / 4.009 | 3.962 / 3.956 | 3.895 / 3.901 | nan / 4.032 | nan / 4.152 |
| 9F | 4.152 / 4.135 | 3.935 / 3.904 | 3.881 / 3.856 | nan / 3.959 | nan / 4.041 |
| 10 | 4.514 / 4.534 | 4.566 / 4.577 | 4.513 / 4.525 | nan / 4.671 | nan / 4.770 |
| 11 | 4.683 / 4.647 | 4.616 / 4.551 | 4.040 / 4.271 | 3.874 / 3.884 | 3.945 / 3.959 |
| 13 | 4.007 / 4.001 | 4.025 / 4.024 | 4.008 / 4.010 | 4.121 / 4.136 | 4.270 / 4.281 |
| 14 | 3.992 / 3.962 | 3.905 / 3.937 | 3.887 / 3.913 | nan / 4.080 | nan / 4.244 |
| 16 | 3.954 / 3.956 | 3.950 / 3.957 | 3.966 / 3.958 | nan / 4.051 | nan / 4.251 |
| 17 | 4.065 / 4.066 | 4.061 / 4.061 | 4.073 / 4.072 | nan / 4.353 | nan / 4.531 |
| 18 | 4.595 / 4.604 | 4.579 / 4.575 | 4.569 / 4.568 | nan / 4.780 | nan / 4.830 |

## Inputs per hole

| hole | IoU fairway / first cut / trees / long grass / water / sand / OB | zones hand / product | irons hand / product | aims hand / product | elev Driver hand / product (carry, roll x, kick) |
|---|---|---|---|---|---|
| 1 | 0.982 / 0.948 / 1.0 / 0.998 / - / - / - | 11 / 11 | False / True | [-40, 40] / [-60, 60] | (17.3, 1.48, -7.1) / (16.1, 2.0, -15.0) |
| 2F | 1.0 / 1.0 / 0.999 / 0.999 / 0.999 / 1.0 / 1.0 | 14 / 14 | False / True | [-40, 40] / [-60, 60] | (14.9, 0.73, -5.2) / (9.1, 0.58, -5.2) |
| 4 | 0.996 / 0.951 / 1.0 / 1.0 / - / - / 1.0 | 11 / 11 | False / True | [-40, 40] / [-60, 60] | (-6.1, 0.84, 2.1) / (-6.0, 0.85, -0.2) |
| 5 | 0.999 / 0.996 / 1.0 / 0.999 / - / 1.0 / 1.0 | 13 / 13 | False / True | [-40, 40] / [-60, 60] | (-2.5, 0.86, 0.4) / (-3.6, 0.86, -1.3) |
| 6 | 0.999 / 0.997 / 1.0 / 0.999 / - / - / - | 10 / 10 | False / True | [-40, 40] / [-60, 60] | (5.4, 1.17, -6.6) / (3.1, 1.08, -11.1) |
| 8 | 0.992 / 0.983 / 1.0 / 0.998 / - / 1.0 / 1.0 | 12 / 12 | False / True | [-40, 40] / [-60, 60] | (-5.6, 0.99, -6.5) / (-6.5, 0.77, -5.8) |
| 9F | 0.993 / 0.976 / 0.998 / 0.998 / 0.999 / - / - | 17 / 17 | False / True | [-40, 40] / [-60, 60] | (10.7, 0.62, 5.0) / (9.7, 0.64, 4.6) |
| 10 | 0.998 / 0.99 / 0.994 / 0.995 / 0.994 / 1.0 / - | 8 / 8 | False / True | [-40, 40] / [-60, 60] | (11.2, 0.98, -4.0) / (6.3, 0.96, -2.1) |
| 11 | 0.995 / 0.991 / 1.0 / 1.0 / 1.0 / - / - | 13 / 13 | True / True | [-40, 40] / [-60, 60] | (-0.9, 1.04, -4.8) / (-0.4, 0.69, -2.0) |
| 13 | 0.988 / 0.974 / 0.998 / - / 0.999 / 0.988 / - | 9 / 9 | True / True | [-40, 40] / [-60, 60] | (12.0, 0.69, 9.0) / (10.9, 0.52, 5.2) |
| 14 | 0.992 / 0.989 / 1.0 / 1.0 / 1.0 / - / - | 6 / 6 | False / True | [-40, 40] / [-60, 60] | (21.8, 1.26, 9.2) / (18.3, 1.12, 5.6) |
| 16 | 0.99 / 0.983 / 0.999 / 0.996 / 1.0 / 0.994 / - | 13 / 13 | False / True | [-40, 40] / [-60, 60] | (5.4, 0.77, 7.9) / (5.4, 0.72, 5.8) |
| 17 | 0.99 / 0.978 / 0.996 / 1.0 / - / 0.983 / - | 10 / 10 | False / True | [-40, 40] / [-60, 60] | (2.6, 0.89, 9.1) / (0.6, 0.77, 9.1) |
| 18 | 0.992 / 0.967 / 1.0 / 0.998 / 0.992 / 1.0 / - | 12 / 12 | False / True | [-40, 40] / [-60, 60] | (23.5, 0.5, 1.5) / (23.7, 0.56, 2.4) |

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
| irons offered | hole['irons'] (product: package irons rule) | course.HOLES[h]['irons'] (11, 13) | same |
| absurd-aim guard | yes (40 yds; aim point lie; play_line) | no | no |
