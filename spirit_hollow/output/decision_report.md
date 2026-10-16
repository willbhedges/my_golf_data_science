# Spirit Hollow — Bayesian tee-shot decisions

96 quasi-Monte Carlo prior draws x 3000 swings (common random numbers within each draw). Driver dispersion prior centred on 70 yds (90% ~62-80). Margin is posterior expected strokes saved per round vs the next club, ± Monte Carlo standard error. P(best) is the share of plausible worlds where the pick is the right club. EVPI is what perfect knowledge of your game would save on that hole: small EVPI means the decision is robust.

| Hole | Pick | Aim | Margin ± SE | P(best) | EVPI | Driver-width break-even |
|---|---|---|---|---|---|---|
| 1 | **4-wood** | +2.5 | 0.001 ± 0.002 vs Driver | 50% | 0.009 | Driver→4-wood at 70 yds |
| 2 back tee | **Driver** | -7.5 | 0.030 ± 0.002 vs 2-wood | 93% | 0.002 | Driver→2-wood at 79 yds |
| 2 forward tee | **Driver** | -12.5 | 0.070 ± 0.004 vs 2-wood | 99% | 0.002 | Driver→2-wood at 84 yds |
| 4 | **Driver** | -2.5 | 0.028 ± 0.004 vs 4-wood | 75% | 0.009 | Driver→4-wood at 73 yds |
| 5 | **Driver** | -5.0 | 0.009 ± 0.002 vs 2-wood | 69% | 0.006 | Driver→2-wood at 73 yds |
| 6 | **Driver** | -2.5 | 0.007 ± 0.003 vs 4-wood | 53% | 0.008 | Driver→4-wood at 72 yds |
| 8 | **4-wood** | +2.5 | 0.079 ± 0.003 vs 2-wood | 100% | 0.004 | none (55-90 yds) |
| 9 back tee | **Driver** | -15.0 | 0.010 ± 0.002 vs 2-wood | 56% | 0.005 | Driver→2-wood at 73 yds |
| 9 forward tee | **2-wood** | -10.0 | 0.000 ± 0.001 vs 4-wood | 46% | 0.005 | none (55-90 yds) |
| 10 | **Driver** | -7.5 | 0.047 ± 0.003 vs 2-wood | 96% | 0.002 | Driver→2-wood at 82 yds |
| 11 | **4-wood** | -5.0 | 0.114 ± 0.006 vs Long iron | 96% | 0.006 | none (55-90 yds) |
| 13 | **4-wood** | -20.0 | 0.028 ± 0.002 vs 2-wood | 98% | 0.001 | none (55-90 yds) |
| 14 | **Driver** | -10.0 | 0.023 ± 0.001 vs 2-wood | 92% | 0.001 | Driver→2-wood at 78 yds |
| 16 | **4-wood** | -2.5 | 0.002 ± 0.003 vs Driver | 44% | 0.013 | Driver→4-wood at 71 yds |
| 17 | **Driver** | -2.5 | 0.069 ± 0.003 vs 2-wood | 100% | 0.001 | none (55-90 yds) |
| 18 | **Driver** | -7.5 | 0.047 ± 0.005 vs 2-wood | 76% | 0.012 | Driver→2-wood at 77 yds |

Total EVPI over these tee shots: 0.09 strokes per round.

