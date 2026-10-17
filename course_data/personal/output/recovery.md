# Recovery study: how much of the golfer's own data pins the pattern down

Each row: median over simulated golfers (24 from the prior + 5 scenarios x 4). Driver width W: posterior sd and 90% CI width in yds at W ~ 70-82 (from the log-scale sd), median |error| of the posterior median (%), 90% CI coverage (all golfers). Break-even: share of (golfer, break-even) pairs at least 5 yds apart where the posterior median is on the right side / where P(right side) > 90%.

## Launch monitor (range factor f uncertain), v2 prior

| shots/club | W sd (log) | W 90% CI (yds at 76) | |err| W | cover W | bias sd | carry sd | mishit sd | nu |err| (log) | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10 | 5.262 | 436558.6 | 4.5% | 80% | 1.7 | 3.3 | 0.022 | 0.18 | 90% | 70% | 44 |
| 25 | nan | nan | nan% | 80% | nan | nan | nan | nan | 92% | 72% | 44 |
| 50 | 4.678 | 167033.2 | 4.1% | 80% | 1.3 | 2.8 | 0.021 | 0.25 | 91% | 78% | 44 |
| 100 | 4.440 | 112897.2 | 3.4% | 84% | 1.1 | 2.7 | 0.019 | 0.25 | 92% | 84% | 44 |
| 200 | 4.279 | 86695.2 | 3.3% | 89% | 0.9 | 2.7 | 0.017 | 0.31 | 94% | 84% | 44 |

Scenarios at the largest n (200): book70: W 69 (truth 70, 90% 63-76), bias +0.6; published82: W 75 (truth 82, 90% 68-83), bias -0.2; wide95_t4: W 80 (truth 95, 90% 72-88), bias -1.0; fader+8: W 71 (truth 70, 90% 64-78), bias +5.5; mishit25: W 70 (truth 70, 90% 64-77), bias +0.2

## Launch monitor (range factor f uncertain), generic prior

| shots/club | W sd (log) | W 90% CI (yds at 76) | |err| W | cover W | bias sd | carry sd | mishit sd | nu |err| (log) | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10 | 8.548 | 97168759.6 | 6.1% | 93% | 3.6 | 3.9 | 0.057 | 0.35 | 85% | 51% | 44 |
| 25 | 7.503 | 17429741.1 | 4.4% | 91% | 2.6 | 3.3 | 0.050 | 0.34 | 88% | 57% | 44 |
| 50 | 6.918 | 6651426.4 | 6.5% | 86% | 2.1 | 3.1 | 0.041 | 0.26 | 86% | 57% | 44 |
| 100 | nan | nan | nan% | 84% | nan | nan | nan | nan | 86% | 61% | 44 |
| 200 | nan | nan | nan% | 86% | nan | nan | nan | nan | 91% | 66% | 44 |

Scenarios at the largest n (200): book70: W 73 (truth 70, 90% 65-83), bias +0.6; published82: W 82 (truth 82, 90% 73-93), bias +0.3; wide95_t4: W 88 (truth 95, 90% 77-100), bias -0.6; fader+8: W 80 (truth 82, 90% 71-91), bias +8.0; mishit25: W 84 (truth 82, 90% 74-95), bias -0.1

## Launch monitor (range = course, f = 1), v2 prior

| shots/club | W sd (log) | W 90% CI (yds at 76) | |err| W | cover W | bias sd | carry sd | mishit sd | nu |err| (log) | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10 | 5.223 | 409594.0 | 4.2% | 80% | 1.8 | 3.4 | 0.023 | 0.21 | 91% | 74% | 44 |
| 25 | nan | nan | nan% | 80% | nan | nan | nan | nan | 90% | 75% | 44 |
| 50 | nan | nan | nan% | 75% | nan | nan | nan | nan | 92% | 80% | 44 |
| 100 | 3.441 | 21845.3 | 3.9% | 86% | 1.1 | 2.7 | 0.019 | 0.29 | 96% | 84% | 44 |
| 200 | 2.759 | 7105.2 | 3.0% | 86% | 0.9 | 2.7 | 0.017 | 0.30 | 98% | 92% | 44 |

Scenarios at the largest n (200): book70: W 69 (truth 70, 90% 65-74), bias +0.3; published82: W 79 (truth 82, 90% 74-84), bias +0.2; wide95_t4: W 84 (truth 95, 90% 78-91), bias -0.1; fader+8: W 71 (truth 70, 90% 67-76), bias +5.5; mishit25: W 71 (truth 70, 90% 67-76), bias -0.0

## Launch monitor (range = course, f = 1), generic prior

| shots/club | W sd (log) | W 90% CI (yds at 76) | |err| W | cover W | bias sd | carry sd | mishit sd | nu |err| (log) | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10 | nan | nan | nan% | 91% | nan | nan | nan | nan | 88% | 56% | 44 |
| 25 | nan | nan | nan% | 89% | nan | nan | nan | nan | 95% | 63% | 44 |
| 50 | nan | nan | nan% | 84% | nan | nan | nan | nan | 88% | 62% | 44 |
| 100 | nan | nan | nan% | 86% | nan | nan | nan | nan | 93% | 75% | 44 |
| 200 | nan | nan | nan% | 77% | nan | nan | nan | nan | 95% | 85% | 44 |

Scenarios at the largest n (200): book70: W 73 (truth 70, 90% 68-78), bias +0.4; published82: W 80 (truth 82, 90% 75-86), bias +0.5; wide95_t4: W 85 (truth 95, 90% 78-93), bias +0.7; fader+8: W 81 (truth 82, 90% 75-87), bias +7.5; mishit25: W 81 (truth 82, 90% 75-88), bias -0.4

## On-course GPS tee shots, aim logged (sd 3), v2 prior

| rounds | W sd (log) | W 90% CI (yds at 76) | |err| W | cover W | bias sd | carry sd | mishit sd | nu |err| (log) | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5.418 | 564379.7 | 4.6% | 82% | 1.9 | 3.9 | 0.023 | 0.12 | 92% | 68% | 44 |
| 3 | 4.981 | 275025.4 | 5.0% | 84% | 1.7 | 3.3 | 0.023 | 0.23 | 90% | 74% | 44 |
| 5 | 4.655 | 160783.5 | 3.6% | 82% | 1.5 | 3.1 | 0.023 | 0.22 | 92% | 78% | 44 |
| 10 | 3.982 | 53188.7 | 5.3% | 77% | 1.3 | 2.8 | 0.023 | 0.23 | 93% | 80% | 44 |
| 20 | 3.340 | 18490.0 | 4.1% | 84% | 1.0 | 2.7 | 0.023 | 0.25 | 94% | 84% | 44 |
| 40 | 2.681 | 6251.3 | 2.8% | 82% | 0.8 | 2.7 | 0.022 | 0.30 | 98% | 92% | 44 |

Scenarios at the largest n (40): book70: W 72 (truth 70, 90% 68-77), bias -0.0; published82: W 84 (truth 82, 90% 79-89), bias +0.4; wide95_t4: W 82 (truth 95, 90% 78-88), bias +0.4; fader+8: W 72 (truth 70, 90% 68-76), bias +6.0; mishit25: W 72 (truth 70, 90% 68-77), bias +0.0

## On-course GPS tee shots, aim logged (sd 3), generic prior

| rounds | W sd (log) | W 90% CI (yds at 76) | |err| W | cover W | bias sd | carry sd | mishit sd | nu |err| (log) | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 8.961 | 191750921.8 | 4.6% | 98% | 4.2 | 5.8 | 0.062 | 0.36 | 91% | 51% | 44 |
| 3 | 7.709 | 24437299.8 | 6.3% | 86% | 3.0 | 5.1 | 0.061 | 0.34 | 88% | 57% | 43 |
| 5 | 6.767 | 5194165.9 | 5.5% | 91% | 2.5 | 5.0 | 0.060 | 0.25 | 88% | 62% | 44 |
| 10 | 5.557 | 709670.7 | 5.1% | 91% | 1.9 | 4.8 | 0.059 | 0.32 | 93% | 74% | 44 |
| 20 | 4.419 | 109152.3 | 3.6% | 100% | 1.4 | 4.6 | 0.058 | 0.29 | 99% | 85% | 44 |
| 40 | 3.417 | 20983.3 | 3.6% | 84% | 1.0 | 4.6 | 0.056 | 0.26 | 98% | 88% | 44 |

Scenarios at the largest n (40): book70: W 73 (truth 70, 90% 68-79), bias -0.6; published82: W 83 (truth 82, 90% 78-90), bias -0.1; wide95_t4: W 88 (truth 95, 90% 81-96), bias +0.2; fader+8: W 83 (truth 82, 90% 78-89), bias +8.0; mishit25: W 83 (truth 82, 90% 78-89), bias +0.0

## On-course GPS tee shots, tee->pin line (aim sd 10), v2 prior

| rounds | W sd (log) | W 90% CI (yds at 76) | |err| W | cover W | bias sd | carry sd | mishit sd | nu |err| (log) | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5.525 | 673116.7 | 3.5% | 77% | 1.9 | 3.9 | 0.023 | 0.12 | 90% | 68% | 44 |
| 3 | 5.156 | 366943.3 | 5.2% | 80% | 1.7 | 3.3 | 0.023 | 0.21 | 90% | 68% | 44 |
| 5 | 4.928 | 251844.1 | 5.9% | 82% | 1.6 | 3.0 | 0.023 | 0.15 | 90% | 67% | 44 |
| 10 | 4.386 | 103416.2 | 4.3% | 77% | 1.4 | 2.8 | 0.023 | 0.26 | 95% | 76% | 44 |
| 20 | 3.699 | 33383.1 | 5.8% | 68% | 1.1 | 2.7 | 0.023 | 0.21 | 96% | 81% | 44 |
| 40 | 3.058 | 11627.8 | 6.2% | 52% | 0.9 | 2.7 | 0.023 | 0.29 | 94% | 76% | 44 |

Scenarios at the largest n (40): book70: W 74 (truth 70, 90% 69-80), bias +0.6; published82: W 84 (truth 82, 90% 79-89), bias +0.7; wide95_t4: W 90 (truth 95, 90% 85-96), bias -0.4; fader+8: W 75 (truth 70, 90% 70-80), bias +7.1; mishit25: W 78 (truth 70, 90% 73-83), bias -0.1

## On-course GPS tee shots, tee->pin line (aim sd 10), generic prior

| rounds | W sd (log) | W 90% CI (yds at 76) | |err| W | cover W | bias sd | carry sd | mishit sd | nu |err| (log) | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 9.221 | 293990275.0 | 6.9% | 93% | 4.4 | 5.9 | 0.062 | 0.33 | 84% | 47% | 44 |
| 3 | 8.256 | 60080248.4 | 9.7% | 82% | 3.3 | 5.1 | 0.062 | 0.29 | 83% | 57% | 44 |
| 5 | 7.316 | 12811553.0 | 6.2% | 89% | 2.7 | 5.0 | 0.061 | 0.32 | 96% | 68% | 44 |
| 10 | 6.142 | 1856539.4 | 6.4% | 89% | 2.1 | 4.8 | 0.063 | 0.27 | 96% | 79% | 44 |
| 20 | 4.942 | 257850.9 | 6.8% | 68% | 1.6 | 4.8 | 0.062 | 0.33 | 94% | 83% | 44 |
| 40 | 3.848 | 42635.9 | 7.8% | 48% | 1.2 | 4.6 | 0.056 | 0.32 | 95% | 85% | 44 |

Scenarios at the largest n (40): book70: W 76 (truth 70, 90% 71-82), bias +0.6; published82: W 90 (truth 82, 90% 84-96), bias +0.5; wide95_t4: W 91 (truth 95, 90% 85-98), bias -0.2; fader+8: W 88 (truth 82, 90% 82-94), bias +8.7; mishit25: W 89 (truth 82, 90% 83-95), bias -0.1

## 50 LM shots/club + on-course rounds, v2 prior

| rounds + 50 LM | W sd (log) | W 90% CI (yds at 76) | |err| W | cover W | bias sd | carry sd | mishit sd | nu |err| (log) | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4.486 | 121735.7 | 3.9% | 86% | 1.3 | 2.5 | 0.021 | 0.27 | 92% | 80% | 44 |
| 3 | nan | nan | nan% | 84% | nan | nan | nan | nan | 91% | 82% | 44 |
| 5 | 4.108 | 65373.6 | 3.5% | 89% | 1.2 | 2.2 | 0.021 | 0.27 | 96% | 85% | 44 |
| 10 | 3.638 | 30187.3 | 2.8% | 84% | 1.1 | 2.1 | 0.021 | 0.28 | 92% | 84% | 44 |

Scenarios at the largest n (10): book70: W 71 (truth 70, 90% 65-77), bias -0.1; published82: W 79 (truth 82, 90% 73-86), bias +0.5; wide95_t4: W 77 (truth 95, 90% 71-84), bias -0.4; fader+8: W 72 (truth 70, 90% 67-78), bias +6.5; mishit25: W 69 (truth 70, 90% 64-75), bias -0.4

## 50 LM shots/club + on-course rounds, generic prior

| rounds + 50 LM | W sd (log) | W 90% CI (yds at 76) | |err| W | cover W | bias sd | carry sd | mishit sd | nu |err| (log) | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | nan | nan | nan% | 80% | nan | nan | nan | nan | 83% | 60% | 44 |
| 3 | nan | nan | nan% | 86% | nan | nan | nan | nan | 90% | 61% | 44 |
| 5 | nan | nan | nan% | 89% | nan | nan | nan | nan | 96% | 69% | 44 |
| 10 | nan | nan | nan% | 89% | nan | nan | nan | nan | 95% | 77% | 44 |

Scenarios at the largest n (10): book70: W nan (truth 70, 90% nan-nan), bias +nan; published82: W 84 (truth 82, 90% 76-92), bias -0.1; wide95_t4: W 88 (truth 95, 90% 78-100), bias +0.5; fader+8: W 85 (truth 82, 90% 77-93), bias +7.1; mishit25: W 85 (truth 82, 90% 77-94), bias +0.1

## Summary stats only (Spirit Hollow emulator), v2 prior

| rounds | W sd (log) | W 90% CI (yds at 76) | |err| W | cover W | bias sd | carry sd | mishit sd | nu |err| (log) | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 5.345 | 500479.3 | 2.4% | 77% | 1.6 | 4.3 | 0.023 | 0.14 | 90% | 71% | 44 |
| 10 | 5.182 | 382814.9 | 4.5% | 75% | 1.4 | 4.2 | 0.023 | 0.21 | 90% | 68% | 44 |
| 20 | 4.876 | 231337.9 | 5.0% | 82% | 1.1 | 4.1 | 0.023 | 0.30 | 90% | 68% | 44 |
| 40 | 4.509 | 126565.9 | 4.6% | 82% | 0.9 | 3.9 | 0.023 | 0.25 | 92% | 72% | 44 |
| 80 | 4.214 | 77912.1 | 4.3% | 77% | 0.7 | 3.7 | 0.023 | 0.27 | 92% | 75% | 44 |

Scenarios at the largest n (80): book70: W 72 (truth 70, 90% 65-79), bias +0.4; published82: W 82 (truth 82, 90% 74-89), bias -0.6; wide95_t4: W 81 (truth 95, 90% 74-89), bias +0.0; fader+8: W 72 (truth 70, 90% 66-79), bias +7.0; mishit25: W 72 (truth 70, 90% 66-80), bias +0.1

## Summary stats only (Spirit Hollow emulator), generic prior

| rounds | W sd (log) | W 90% CI (yds at 76) | |err| W | cover W | bias sd | carry sd | mishit sd | nu |err| (log) | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 8.616 | 108757519.3 | 8.1% | 93% | 2.8 | 6.0 | 0.063 | 0.27 | 88% | 50% | 44 |
| 10 | 8.076 | 44689581.6 | 6.6% | 93% | 2.1 | 5.8 | 0.064 | 0.26 | 88% | 52% | 44 |
| 20 | 7.200 | 10586374.6 | 5.7% | 89% | 1.6 | 5.6 | 0.064 | 0.30 | 88% | 62% | 44 |
| 40 | 6.510 | 3400787.4 | 6.6% | 89% | 1.2 | 5.3 | 0.065 | 0.26 | 92% | 62% | 44 |
| 80 | 6.117 | 1782630.0 | 7.1% | 86% | 0.8 | 5.0 | 0.067 | 0.32 | 89% | 65% | 44 |

Scenarios at the largest n (80): book70: W 77 (truth 70, 90% 67-88), bias +0.4; published82: W 88 (truth 82, 90% 78-100), bias +0.2; wide95_t4: W 84 (truth 95, 90% 74-94), bias +0.5; fader+8: W 85 (truth 82, 90% 76-95), bias +8.6; mishit25: W 83 (truth 82, 90% 74-94), bias +0.2

