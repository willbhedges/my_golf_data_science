# Mozingo Lake — strokes-gained tee report

SG:OTT = tour expected strokes from the tee minus (1 + expected strokes after the drive). Higher is better. *Diff* is the extra strokes per round vs the best club on that hole (paired, same random draws), with a 95% confidence interval.

## Every hole

| Hole | Club | Aim | Fairway | Approach | SG:OTT | Diff vs best (95% CI) | Best in % of what-if worlds |
|---|---|---|---|---|---|---|---|
| 1 | Driver | +2.5 | 76% | 75 | +0.090 | +0.031 (+0.027 to +0.034) | 10% |
| 1 | 2-wood | +2.5 | 87% | 93 | +0.112 | +0.008 (+0.006 to +0.010) | 20% |
| 1 | **4-wood** | +2.5 | 94% | 103 | +0.120 | — | 70% |
| 2 | Driver | -10.0 | 73% | 59 | +0.077 | +0.030 (+0.027 to +0.033) | 19% |
| 2 | 2-wood | -10.0 | 83% | 74 | +0.070 | +0.038 (+0.035 to +0.040) | 2% |
| 2 | **4-wood** | -5.0 | 95% | 81 | +0.107 | — | 79% |
| 3 | **Driver** | -12.5 | 89% | 219 | +0.177 | — | 98% |
| 3 | 2-wood | -15.0 | 94% | 238 | +0.067 | +0.110 (+0.109 to +0.111) | 2% |
| 3 | 4-wood | -17.5 | 98% | 248 | +0.013 | +0.163 (+0.162 to +0.165) | 0% |
| 4 | **Driver** | +0.0 | 89% | 63 | +0.190 | — | 97% |
| 4 | 2-wood | +0.0 | 92% | 83 | +0.146 | +0.044 (+0.044 to +0.045) | 2% |
| 4 | 4-wood | +0.0 | 96% | 92 | +0.132 | +0.059 (+0.058 to +0.060) | 1% |
| 6 | **Driver** | -5.0 | 96% | 192 | +0.186 | — | 98% |
| 6 | 2-wood | -10.0 | 96% | 212 | +0.061 | +0.124 (+0.123 to +0.126) | 2% |
| 6 | 4-wood | -12.5 | 98% | 222 | +0.008 | +0.178 (+0.177 to +0.179) | 0% |
| 7 | Driver | +2.5 | 74% | 132 | -0.060 | +0.082 (+0.077 to +0.087) | 8% |
| 7 | 2-wood | +5.0 | 82% | 151 | -0.038 | +0.060 (+0.057 to +0.064) | 6% |
| 7 | **4-wood** | +7.5 | 94% | 159 | +0.022 | — | 86% |
| 9 | **Driver** | +2.5 | 92% | 52 | +0.184 | — | 78% |
| 9 | 2-wood | +5.0 | 96% | 71 | +0.140 | +0.044 (+0.042 to +0.046) | 5% |
| 9 | 4-wood | +5.0 | 99% | 80 | +0.130 | +0.054 (+0.051 to +0.057) | 17% |
| 10 | **Driver** | -5.0 | 93% | 91 | +0.152 | — | 77% |
| 10 | 2-wood | -7.5 | 96% | 111 | +0.120 | +0.032 (+0.031 to +0.033) | 8% |
| 10 | 4-wood | -7.5 | 98% | 120 | +0.114 | +0.037 (+0.035 to +0.040) | 15% |
| 12 | **Driver** | +0.0 | 82% | 228 | +0.098 | — | 98% |
| 12 | 2-wood | -10.0 | 88% | 246 | -0.019 | +0.117 (+0.115 to +0.118) | 2% |
| 12 | 4-wood | -12.5 | 93% | 255 | -0.054 | +0.151 (+0.150 to +0.153) | 0% |
| 13 | Driver | +2.5 | 74% | 103 | +0.085 | +0.004 (+0.001 to +0.006) | 41% |
| 13 | 2-wood | +2.5 | 88% | 119 | +0.082 | +0.006 (+0.004 to +0.008) | 15% |
| 13 | **4-wood** | +2.5 | 95% | 127 | +0.088 | — | 44% |

## Hole 13 deep dive

### Driver (aim +2.5 yds) — expected score 3.896, SG:OTT +0.085

| Ends in | Share | Avg yds to centre | Expected strokes from there | Cost vs this club's average |
|---|---|---|---|---|
| fairway | 74.4% | 100 | 2.80 | -0.072 |
| rough | 22.3% | 121 | 3.09 | +0.042 |
| trees | 3.4% | 111 | 3.79 | +0.030 |

### 2-wood (aim +2.5 yds) — expected score 3.899, SG:OTT +0.082

| Ends in | Share | Avg yds to centre | Expected strokes from there | Cost vs this club's average |
|---|---|---|---|---|
| fairway | 87.6% | 118 | 2.85 | -0.046 |
| rough | 9.8% | 133 | 3.13 | +0.022 |
| trees | 2.6% | 120 | 3.79 | +0.023 |

### 4-wood (aim +2.5 yds) — expected score 3.893, SG:OTT +0.088

| Ends in | Share | Avg yds to centre | Expected strokes from there | Cost vs this club's average |
|---|---|---|---|---|
| fairway | 95.1% | 127 | 2.87 | -0.020 |
| rough | 3.7% | 139 | 3.15 | +0.010 |
| trees | 1.1% | 129 | 3.79 | +0.010 |

### Aim curve (expected score by aim, yds right of the app line)

| Aim | Driver | 2-wood | 4-wood |
|---|---|---|---|
| -15 | 4.031 | 4.060 | 4.043 |
| -10 | 3.961 | 3.982 | 3.963 |
| -5 | 3.917 | 3.930 | 3.915 |
| +0 | 3.897 | 3.903 | 3.894 |
| +5 | 3.901 | 3.900 | 3.894 |
| +10 | 3.923 | 3.916 | 3.909 |
| +15 | 3.956 | 3.945 | 3.936 |

### What would have to be true for one club to pull clear

| Assumption | Driver | 2-wood | 4-wood |
|---|---|---|---|
| As measured | +0.004 | +0.006 | +0.000 |
| Driver 55 wide (a good driving day) | +0.000 | +0.038 | +0.032 |
| Everything 20% wider | +0.025 | +0.020 | +0.000 |
| Firm-ground roll off (soft day) | +0.000 | +0.004 | +0.008 |
| Rough lets the ball run (60% roll) | +0.000 | +0.006 | +0.000 |
| Trees left only half as penal | +0.000 | +0.010 | +0.009 |
