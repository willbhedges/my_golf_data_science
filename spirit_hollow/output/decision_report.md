# Spirit Hollow — Bayesian tee-shot decisions

4 quasi-Monte Carlo prior draws x 3000 swings (common random numbers within each draw). Driver dispersion prior centred on 70 yds (90% ~62-80). Margin is posterior expected strokes saved per round vs the next club, ± Monte Carlo standard error. P(best) is the share of plausible worlds where the pick is the right club. EVPI is what perfect knowledge of your game would save on that hole: small EVPI means the decision is robust.

| Hole | Pick | Aim | Margin ± SE | P(best) | EVPI | Driver-width break-even |
|---|---|---|---|---|---|---|
| 1 | **4-wood** | +2.5 | 0.004 ± 0.013 vs Driver | 25% | 0.011 | Driver→4-wood at 70 yds |
| 2 back tee | **Driver** | -7.5 | 0.033 ± 0.009 vs 2-wood | 75% | 0.006 | Driver→2-wood at 79 yds |
| 2 forward tee | **Driver** | -10.0 | 0.076 ± 0.015 vs 2-wood | 100% | 0.001 | Driver→2-wood at 84 yds |
| 4 | **Driver** | -5.0 | 0.022 ± 0.021 vs 4-wood | 75% | 0.011 | Driver→4-wood at 73 yds |
| 5 | **Driver** | -7.5 | 0.011 ± 0.004 vs 2-wood | 50% | 0.012 | Driver→2-wood at 73 yds |
| 6 | **Driver** | -2.5 | 0.005 ± 0.018 vs 4-wood | 50% | 0.015 | Driver→4-wood at 72 yds |
| 8 | **4-wood** | +2.5 | 0.076 ± 0.023 vs 2-wood | 100% | 0.007 | none (55-90 yds) |
| 9 back tee | **Driver** | -15.0 | 0.013 ± 0.007 vs 2-wood | 50% | 0.013 | Driver→2-wood at 73 yds |
| 9 forward tee | **2-wood** | -12.5 | 0.003 ± 0.006 vs 4-wood | 50% | 0.004 | none (55-90 yds) |
| 10 | **Driver** | -7.5 | 0.053 ± 0.015 vs 2-wood | 75% | 0.004 | Driver→2-wood at 82 yds |
| 11 | **4-wood** | -7.5 | 0.008 ± 0.119 vs Long iron | 75% | 0.088 | none (55-90 yds) |
| 13 | **4-wood** | -17.5 | 0.017 ± 0.008 vs 2-wood | 100% | 0.001 | none (55-90 yds) |
| 14 | **Driver** | -10.0 | 0.021 ± 0.006 vs 2-wood | 75% | 0.006 | Driver→2-wood at 78 yds |
| 16 | **4-wood** | -5.0 | 0.010 ± 0.021 vs Driver | 25% | 0.010 | Driver→4-wood at 71 yds |
| 17 | **Driver** | -2.5 | 0.072 ± 0.013 vs 2-wood | 100% | 0.000 | none (55-90 yds) |
| 18 | **Driver** | -5.0 | 0.037 ± 0.031 vs 4-wood | 50% | 0.022 | Driver→2-wood at 77 yds |

Total EVPI over these tee shots: 0.21 strokes per round.

