# Recovery study: how much of the golfer's own data pins the pattern down

Medians over simulated golfers (24 drawn from the prior + 5 scenarios x 4 replicates; the scenarios are off-prior on purpose). W = driver on-course width95. **W sd** = posterior sd / median; **±yds** = half the 90% interval at W = 76; **|err|** = |posterior median / truth - 1|; **cover** = share of 90% intervals holding the truth, for golfers drawn from the prior (the calibration check; scenario golfers excluded). **Break-even**: over (golfer, v2 break-even) pairs at least 5 yds apart (62.9, 67.4, 77.7, 79.1, 81.7, 86), the share with the posterior median on the right side, and with P(right side) > 90%.

## Launch monitor (range factor f uncertain), v2 prior

| shots/club | W sd | ±yds | W \|err\| | cover W (prior golfers) | bias sd (yds) | carry sd (yds) | mishit sd | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|
| 10 | 7.4% | 9.3 | 4.5% | 88% | 1.7 | 3.3 | 0.022 | 90% | 70% | 44 |
| 25 | 7.0% | 8.8 | 4.2% | 96% | 1.5 | 3.0 | 0.022 | 93% | 75% | 44 |
| 50 | 6.6% | 8.3 | 4.1% | 92% | 1.3 | 2.8 | 0.021 | 91% | 78% | 44 |
| 100 | 6.3% | 7.9 | 3.4% | 88% | 1.1 | 2.7 | 0.019 | 92% | 84% | 44 |
| 200 | 6.1% | 7.6 | 3.3% | 100% | 0.9 | 2.7 | 0.017 | 94% | 84% | 44 |

Scenarios at the largest n (200): book70: W 69 (truth 70, 90% 63-76), bias +0.6; published82: W 75 (truth 82, 90% 68-83), bias -0.2; wide95_t4: W 80 (truth 95, 90% 72-88), bias -1.0; fader+8: W 71 (truth 70, 90% 64-78), bias +5.5; mishit25: W 70 (truth 70, 90% 64-77), bias +0.2

## Launch monitor (range factor f uncertain), generic prior

| shots/club | W sd | ±yds | W \|err\| | cover W (prior golfers) | bias sd (yds) | carry sd (yds) | mishit sd | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|
| 10 | 10.4% | 13.0 | 5.5% | 92% | 3.6 | 3.9 | 0.057 | 86% | 51% | 44 |
| 25 | 9.3% | 11.6 | 4.4% | 88% | 2.6 | 3.3 | 0.050 | 88% | 57% | 44 |
| 50 | 8.6% | 10.7 | 6.5% | 79% | 2.1 | 3.1 | 0.041 | 86% | 56% | 44 |
| 100 | 7.9% | 9.9 | 4.4% | 79% | 1.7 | 3.0 | 0.032 | 89% | 64% | 44 |
| 200 | 7.4% | 9.3 | 4.4% | 79% | 1.3 | 3.0 | 0.024 | 92% | 68% | 44 |

Scenarios at the largest n (200): book70: W 73 (truth 70, 90% 65-83), bias +0.6; published82: W 82 (truth 82, 90% 73-93), bias +0.3; wide95_t4: W 88 (truth 95, 90% 77-100), bias -0.6; fader+8: W 80 (truth 82, 90% 71-91), bias +8.0; mishit25: W 84 (truth 82, 90% 74-95), bias -0.1

## Launch monitor (range = course, f = 1), v2 prior

| shots/club | W sd | ±yds | W \|err\| | cover W (prior golfers) | bias sd (yds) | carry sd (yds) | mishit sd | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|
| 10 | 7.3% | 9.2 | 4.2% | 88% | 1.8 | 3.4 | 0.023 | 91% | 74% | 44 |
| 25 | 6.5% | 8.2 | 4.2% | 83% | 1.6 | 3.0 | 0.022 | 90% | 76% | 44 |
| 50 | 5.7% | 7.2 | 4.7% | 92% | 1.4 | 2.8 | 0.022 | 92% | 82% | 44 |
| 100 | 4.9% | 6.1 | 3.9% | 92% | 1.1 | 2.7 | 0.019 | 96% | 84% | 44 |
| 200 | 4.0% | 4.9 | 3.0% | 92% | 0.9 | 2.7 | 0.017 | 98% | 92% | 44 |

Scenarios at the largest n (200): book70: W 69 (truth 70, 90% 65-74), bias +0.3; published82: W 79 (truth 82, 90% 74-84), bias +0.2; wide95_t4: W 84 (truth 95, 90% 78-91), bias -0.1; fader+8: W 71 (truth 70, 90% 67-76), bias +5.5; mishit25: W 71 (truth 70, 90% 67-76), bias -0.0

## Launch monitor (range = course, f = 1), generic prior

| shots/club | W sd | ±yds | W \|err\| | cover W (prior golfers) | bias sd (yds) | carry sd (yds) | mishit sd | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|
| 10 | 10.1% | 12.6 | 5.5% | 92% | 3.6 | 3.9 | 0.056 | 89% | 57% | 44 |
| 25 | 8.6% | 10.7 | 3.9% | 92% | 2.7 | 3.3 | 0.050 | 96% | 64% | 44 |
| 50 | 7.2% | 9.0 | 6.0% | 83% | 2.2 | 3.1 | 0.039 | 91% | 65% | 44 |
| 100 | 5.8% | 7.2 | 3.6% | 92% | 1.7 | 3.0 | 0.033 | 94% | 76% | 44 |
| 200 | 4.5% | 5.7 | 3.1% | 83% | 1.3 | 2.9 | 0.024 | 98% | 87% | 44 |

Scenarios at the largest n (200): book70: W 73 (truth 70, 90% 68-78), bias +0.4; published82: W 80 (truth 82, 90% 75-86), bias +0.5; wide95_t4: W 85 (truth 95, 90% 78-93), bias +0.7; fader+8: W 81 (truth 82, 90% 75-87), bias +7.5; mishit25: W 81 (truth 82, 90% 75-88), bias -0.4

## On-course GPS tee shots, aim logged (sd 3), v2 prior

| rounds | W sd | ±yds | W \|err\| | cover W (prior golfers) | bias sd (yds) | carry sd (yds) | mishit sd | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 7.7% | 9.6 | 4.5% | 92% | 1.9 | 3.9 | 0.023 | 92% | 68% | 44 |
| 3 | 6.9% | 8.7 | 4.6% | 92% | 1.7 | 3.3 | 0.023 | 91% | 74% | 44 |
| 5 | 6.5% | 8.1 | 3.3% | 92% | 1.5 | 3.1 | 0.023 | 91% | 80% | 44 |
| 10 | 5.6% | 7.0 | 4.5% | 88% | 1.3 | 2.8 | 0.023 | 92% | 82% | 44 |
| 20 | 4.6% | 5.7 | 4.4% | 92% | 1.0 | 2.7 | 0.023 | 93% | 87% | 44 |
| 40 | 3.6% | 4.5 | 1.7% | 92% | 0.8 | 2.7 | 0.022 | 96% | 92% | 44 |

Scenarios at the largest n (40): book70: W 70 (truth 70, 90% 67-75), bias -0.0; published82: W 82 (truth 82, 90% 77-86), bias +0.4; wide95_t4: W 81 (truth 95, 90% 77-87), bias +0.4; fader+8: W 70 (truth 70, 90% 66-75), bias +6.0; mishit25: W 71 (truth 70, 90% 67-75), bias +0.1

## On-course GPS tee shots, aim logged (sd 3), generic prior

| rounds | W sd | ±yds | W \|err\| | cover W (prior golfers) | bias sd (yds) | carry sd (yds) | mishit sd | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 11.0% | 13.8 | 4.7% | 96% | 4.2 | 5.8 | 0.062 | 89% | 50% | 43 |
| 3 | 9.3% | 11.7 | 6.3% | 83% | 3.0 | 5.1 | 0.060 | 86% | 57% | 43 |
| 5 | 8.2% | 10.3 | 6.1% | 92% | 2.4 | 5.0 | 0.060 | 88% | 61% | 44 |
| 10 | 6.7% | 8.4 | 3.5% | 92% | 1.8 | 4.8 | 0.059 | 93% | 73% | 44 |
| 20 | 5.3% | 6.7 | 3.2% | 96% | 1.4 | 4.6 | 0.058 | 98% | 85% | 44 |
| 40 | 4.1% | 5.2 | 3.7% | 83% | 1.0 | 4.6 | 0.056 | 98% | 89% | 44 |

Scenarios at the largest n (40): book70: W 71 (truth 70, 90% 67-77), bias -0.6; published82: W 81 (truth 82, 90% 75-87), bias -0.1; wide95_t4: W 85 (truth 95, 90% 79-93), bias +0.2; fader+8: W 81 (truth 82, 90% 75-86), bias +7.8; mishit25: W 81 (truth 82, 90% 76-86), bias -0.0

## On-course GPS tee shots, tee->pin line (aim sd 10), v2 prior

| rounds | W sd | ±yds | W \|err\| | cover W (prior golfers) | bias sd (yds) | carry sd (yds) | mishit sd | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 7.8% | 9.7 | 3.4% | 92% | 1.9 | 3.9 | 0.023 | 91% | 69% | 44 |
| 3 | 7.2% | 8.9 | 4.5% | 88% | 1.7 | 3.3 | 0.023 | 91% | 72% | 44 |
| 5 | 6.7% | 8.4 | 5.6% | 88% | 1.6 | 3.0 | 0.023 | 92% | 75% | 44 |
| 10 | 5.9% | 7.4 | 4.2% | 96% | 1.3 | 2.8 | 0.023 | 94% | 82% | 44 |
| 20 | 4.9% | 6.1 | 4.2% | 83% | 1.1 | 2.7 | 0.023 | 95% | 86% | 44 |
| 40 | 3.8% | 4.8 | 2.9% | 83% | 0.9 | 2.7 | 0.022 | 97% | 90% | 44 |

Scenarios at the largest n (40): book70: W 70 (truth 70, 90% 66-74), bias +0.6; published82: W 78 (truth 82, 90% 73-83), bias +0.7; wide95_t4: W 85 (truth 95, 90% 80-90), bias -0.4; fader+8: W 69 (truth 70, 90% 65-74), bias +6.8; mishit25: W 73 (truth 70, 90% 69-78), bias -0.1

## On-course GPS tee shots, tee->pin line (aim sd 10), generic prior

| rounds | W sd | ±yds | W \|err\| | cover W (prior golfers) | bias sd (yds) | carry sd (yds) | mishit sd | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 11.2% | 14.0 | 6.3% | 96% | 4.3 | 5.9 | 0.062 | 83% | 46% | 44 |
| 3 | 9.5% | 11.9 | 7.6% | 92% | 3.2 | 5.1 | 0.061 | 86% | 52% | 44 |
| 5 | 8.6% | 10.7 | 3.8% | 96% | 2.6 | 4.9 | 0.060 | 95% | 65% | 44 |
| 10 | 6.9% | 8.7 | 5.0% | 88% | 2.0 | 4.8 | 0.062 | 98% | 76% | 44 |
| 20 | 5.6% | 7.0 | 2.9% | 92% | 1.5 | 4.8 | 0.061 | 98% | 85% | 44 |
| 40 | 4.3% | 5.4 | 2.6% | 96% | 1.1 | 4.6 | 0.056 | 98% | 89% | 44 |

Scenarios at the largest n (40): book70: W 71 (truth 70, 90% 66-76), bias +0.5; published82: W 82 (truth 82, 90% 77-89), bias +0.5; wide95_t4: W 85 (truth 95, 90% 79-92), bias -0.2; fader+8: W 81 (truth 82, 90% 75-87), bias +8.1; mishit25: W 82 (truth 82, 90% 77-88), bias -0.1

## 50 LM shots/club + on-course rounds, v2 prior

| rounds + 50 LM | W sd | ±yds | W \|err\| | cover W (prior golfers) | bias sd (yds) | carry sd (yds) | mishit sd | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6.4% | 8.0 | 3.7% | 92% | 1.3 | 2.5 | 0.021 | 92% | 80% | 44 |
| 3 | 6.0% | 7.5 | 2.9% | 96% | 1.2 | 2.3 | 0.021 | 92% | 85% | 44 |
| 5 | 5.7% | 7.1 | 3.3% | 100% | 1.2 | 2.2 | 0.021 | 96% | 85% | 44 |
| 10 | 5.1% | 6.3 | 3.2% | 92% | 1.1 | 2.1 | 0.021 | 93% | 86% | 44 |

Scenarios at the largest n (10): book70: W 70 (truth 70, 90% 65-77), bias -0.1; published82: W 78 (truth 82, 90% 73-85), bias +0.5; wide95_t4: W 76 (truth 95, 90% 71-84), bias -0.4; fader+8: W 72 (truth 70, 90% 66-77), bias +6.5; mishit25: W 69 (truth 70, 90% 63-75), bias -0.3

## 50 LM shots/club + on-course rounds, generic prior

| rounds + 50 LM | W sd | ±yds | W \|err\| | cover W (prior golfers) | bias sd (yds) | carry sd (yds) | mishit sd | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 8.2% | 10.2 | 3.8% | 79% | 2.0 | 2.8 | 0.039 | 90% | 66% | 44 |
| 3 | 7.4% | 9.3 | 4.1% | 83% | 1.8 | 2.7 | 0.039 | 90% | 65% | 44 |
| 5 | 6.9% | 8.6 | 4.0% | 92% | 1.7 | 2.7 | 0.041 | 97% | 70% | 44 |
| 10 | 6.0% | 7.5 | 4.1% | 88% | 1.5 | 2.6 | 0.039 | 95% | 80% | 44 |

Scenarios at the largest n (10): book70: W 73 (truth 70, 90% 66-80), bias -0.5; published82: W 82 (truth 82, 90% 75-90), bias -0.1; wide95_t4: W 87 (truth 95, 90% 77-99), bias +0.4; fader+8: W 83 (truth 82, 90% 76-92), bias +7.0; mishit25: W 83 (truth 82, 90% 76-92), bias +0.1

## Summary stats only (Spirit Hollow emulator), v2 prior

| rounds | W sd | ±yds | W \|err\| | cover W (prior golfers) | bias sd (yds) | carry sd (yds) | mishit sd | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 7.6% | 9.5 | 2.4% | 83% | 1.6 | 4.3 | 0.023 | 90% | 71% | 44 |
| 10 | 7.3% | 9.1 | 4.5% | 83% | 1.4 | 4.2 | 0.023 | 90% | 68% | 44 |
| 20 | 6.7% | 8.4 | 5.0% | 88% | 1.1 | 4.1 | 0.023 | 90% | 68% | 44 |
| 40 | 6.1% | 7.7 | 4.6% | 83% | 0.9 | 3.9 | 0.023 | 92% | 72% | 44 |
| 80 | 5.6% | 7.0 | 4.3% | 75% | 0.7 | 3.7 | 0.023 | 92% | 75% | 44 |

Scenarios at the largest n (80): book70: W 72 (truth 70, 90% 65-79), bias +0.4; published82: W 82 (truth 82, 90% 74-89), bias -0.6; wide95_t4: W 81 (truth 95, 90% 74-89), bias +0.0; fader+8: W 72 (truth 70, 90% 66-79), bias +7.0; mishit25: W 72 (truth 70, 90% 66-80), bias +0.1

## Summary stats only (Spirit Hollow emulator), generic prior

| rounds | W sd | ±yds | W \|err\| | cover W (prior golfers) | bias sd (yds) | carry sd (yds) | mishit sd | right side of break-even | confident (>90%) | fits |
|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 10.6% | 13.2 | 8.1% | 92% | 2.8 | 6.0 | 0.063 | 88% | 50% | 44 |
| 10 | 9.6% | 12.0 | 6.6% | 92% | 2.1 | 5.8 | 0.064 | 88% | 52% | 44 |
| 20 | 8.6% | 10.8 | 5.7% | 92% | 1.6 | 5.6 | 0.064 | 88% | 62% | 44 |
| 40 | 7.9% | 9.8 | 6.6% | 92% | 1.2 | 5.3 | 0.065 | 92% | 62% | 44 |
| 80 | 7.3% | 9.1 | 7.1% | 83% | 0.8 | 5.0 | 0.067 | 89% | 65% | 44 |

Scenarios at the largest n (80): book70: W 77 (truth 70, 90% 67-88), bias +0.4; published82: W 88 (truth 82, 90% 78-100), bias +0.2; wide95_t4: W 84 (truth 95, 90% 74-94), bias +0.5; fader+8: W 85 (truth 82, 90% 76-95), bias +8.6; mishit25: W 83 (truth 82, 90% 74-94), bias +0.2

