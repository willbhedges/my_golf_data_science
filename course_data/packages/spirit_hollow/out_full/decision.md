# Spirit Hollow Golf Course (Black tees): tee-shot decisions

Full Bayesian run: 32 Sobol prior draws x 3000 swings (spirit_hollow/final_decision.py settings). Margin = expected strokes saved vs the next club; cross-fitted = corrected for picking the best of a noisy grid; P(best) = noise-corrected share of plausible worlds where the pick wins.

| Hole | Par | Yds | Pick | Aim (yds, +R) | Zone | Runner-up | Margin | Cross-fitted | P(best) | Width break-even |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 391 | **Driver** | -47.5 | -60 to -38 | 2-wood | 0.058 | 0.058 | 100% | none 55-90 |
| 2 | 5 | 507 | **Driver** | +7.5 | +2 to +12 | 2-wood | 0.065 | 0.065 | 100% | none 55-90 |
| 4 | 5 | 532 | **Driver** | -7.5 | -18 to +0 | 2-wood | 0.073 | 0.073 | 100% | none 55-90 |
| 5 | 4 | 384 | **4-wood** (tie) | -5.0 | -12 to +2 | Driver | 0.000 | -0.001 | 44% | none 55-90 |
| 6 | 4 | 408 | **Driver** | -35.0 | -45 to -28 | 2-wood | 0.029 | 0.029 | 100% | none 55-90 |
| 8 | 4 | 383 | **Driver** | -20.0 | -32 to -10 | 2-wood | 0.012 | 0.012 | 62% | none 55-90 |
| 9 | 4 | 365 | **4-wood** | +2.5 | -8 to +15 | 2-wood | 0.029 | 0.031 | 72% | 4-wood->Driver at 82 |
| 10 | 5 | 502 | **Driver** | -2.5 | -5 to +2 | 2-wood | 0.058 | 0.058 | 100% | none 55-90 |
| 11 | 4 | 338 | **4-wood** | -2.5 | -20 to +8 | 2-wood | 0.089 | 0.091 | 91% | none 55-90 |
| 13 | 4 | 409 | **Driver** | +15.0 | +5 to +22 | 2-wood | 0.038 | 0.038 | 84% | none 55-90 |
| 14 | 4 | 393 | **2-wood** (tie) | -57.5 | -60 to -48 | Driver | 0.000 | -0.001 | 44% | 2-wood->Driver at 84 |
| 16 | 4 | 378 | **2-wood** (tie) | -5.0 | -12 to +2 | Driver | 0.009 | 0.009 | 69% | none 55-90 |
| 17 | 4 | 445 | **Driver** | -5.0 | -12 to +5 | 2-wood | 0.033 | 0.032 | 100% | none 55-90 |
| 18 | 5 | 521 | **Driver** | -2.5 | -8 to +5 | 2-wood | 0.036 | 0.036 | 100% | Driver->4-wood at 89 |
