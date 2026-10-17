# pine_dunes: auto vs hand truth (before)

Auto package: `course_data/courses/pine_dunes/auto/package.json`; tee set Gold; quick decision n=4000.

* routing ok 18/18, par ok 18/18, green within 10 yds 18/18
* tees within 10 yds 63/72 (median 3.0 yds; 0 set-holes with no auto tee)
* par 3s planned as par 3 4/4, with a green outline 4/4
* tee-shot picks: same club 11/14, same or tie 12/14, total regret 0.136 strokes
* corridor IoU (mean): trees 0.0, water 1.0

| hole | par | routing | green err | tee err by set | par 3 | auto pick | truth pick | regret | IoU |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | ok | 1.1 | Go 1.5, Bl 2.3, Wh 1.8, Re 1.5 |  | 2-wood -2 | 4-wood +5 | 0.0449 | trees 0.0, fw 0.992 |
| 2 | 4 | ok | 1.3 | Go 6.8, Bl 0.4, Wh 7.3, Re 1.3 |  | Driver +8 | Driver +5 | 0.0 | trees 0.0, fw 1.0 |
| 3 | 3 | ok | 1.1 | Go 2.4, Bl 5.1, Wh 4.9, Re 7.9 | planned |   |   |  |  |
| 4 | 4 | ok | 2.5 | Go 20.0, Bl 2.9, Wh 29.2, Re 3.6 |  | Driver -20 | Driver +2 | 0.0 | trees 0.0, fw 1.0 |
| 5 | 5 | ok | 1.2 | Go 7.6, Bl 1.3, Wh 11.7, Re 1.9 |  | Driver -25 | Driver -12 | 0.0 | trees 0.0, fw 1.0 |
| 6 | 3 | ok | 2.3 | Go 1.1, Bl 3.2, Wh 14.7, Re 123.7 | planned |   |   |  |  |
| 7 | 4 | ok | 3.4 | Go 1.9, Bl 4.2, Wh 3.0, Re 2.9 |  | Driver +8 | Driver +8 | 0.0 | trees 0.0, fw 1.0 |
| 8 | 4 | ok | 1.0 | Go 1.5, Bl 5.9, Wh 3.6, Re 2.7 |  | 4-wood +2 | 4-wood +0 | 0.0 | trees 0.0, fw 0.99 |
| 9 | 5 | ok | 3.3 | Go 1.2, Bl 0.3, Wh 114.6, Re 92.0 |  | Driver -12 | Driver -10 | 0.0 | trees 0.0, fw 0.994 |
| 10 | 4 | ok | 1.9 | Go 7.8, Bl 2.4, Wh 2.2, Re 1.1 |  | 4-wood +5 | 4-wood +5 | 0.0 | trees 0.0, fw 1.0 |
| 11 | 5 | ok | 1.4 | Go 1.8, Bl 4.4, Wh 1.5, Re 9.0 |  | 2-wood +10 | 2-wood +8 | 0.0 | trees 0.0, fw 1.0 |
| 12 | 3 | ok | 1.5 | Go 3.1, Bl 1.5, Wh 8.5, Re 6.3 | planned |   |   |  |  |
| 13 | 4 | ok | 1.7 | Go 2.1, Bl 7.1, Wh 5.1, Re 4.4 |  | Driver -15 | 4-wood -5 | 0.0248 | trees 0.0, water 1.0, fw 1.0 |
| 14 | 4 | ok | 2.0 | Go 2.1, Bl 3.0, Wh 2.7, Re 2.4 |  | Driver -5 | Driver +2 | 0.0 | trees 0.0, water 1.0, fw 1.0 |
| 15 | 4 | ok | 1.0 | Go 10.1, Bl 1.3, Wh 2.0, Re 9.3 |  | Driver -28 | Long iron -5 | 0.066 | trees 0.0, fw 1.0 |
| 16 | 3 | ok | 1.6 | Go 2.0, Bl 6.5, Wh 2.0, Re 1.8 | planned |   |   |  |  |
| 17 | 4 | ok | 2.9 | Go 2.6, Bl 0.8, Wh 0.7, Re 6.7 |  | Driver +12 | Driver +5 | 0.0 | trees 0.0, fw 1.0 |
| 18 | 5 | ok | 0.8 | Go 10.9, Bl 3.3, Wh 4.5, Re 3.9 |  | 4-wood +28 | 4-wood +22 | 0.0 | trees 0.0, water 1.0, fw 1.0 |
