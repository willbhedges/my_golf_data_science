# national_kc: auto vs hand truth (after)

Auto package: `course_data/courses/national_kc/auto/package_v3_card.json`; tee set Black; quick decision n=4000.

* routing ok 18/18, par ok 18/18, green within 10 yds 18/18
* tees within 10 yds 82/90 (median 2.9 yds; 0 set-holes with no auto tee)
* par 3s planned as par 3 4/4, with a green outline 4/4
* tee-shot picks: same club 12/14, same or tie 13/14, total regret 0.007 strokes
* corridor IoU (mean): trees 0.45, water 0.685, ob 0.074

| hole | par | routing | green err | tee err by set | par 3 | auto pick | truth pick | regret | IoU |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | ok | 2.9 | Bl 26.2, Bl 0.0, Go 0.9, Gr 1.5, Wh 3.1 |  | Long iron -40 | 4-wood +2 |  | trees 0.886, water 1.0, fw 1.0 |
| 2 | 5 | ok | 1.7 | Bl 1.2, Bl 2.4, Go 2.3, Gr 3.0, Wh 2.1 |  | Driver -10 | Driver -10 | 0.0 | trees 0.542, water 1.0, ob 0.0, fw 1.0 |
| 3 | 4 | ok | 1.6 | Bl 13.3, Bl 12.0, Go 2.3, Gr 13.5, Wh 2.0 |  | 4-wood -40 | 4-wood -40 | 0.0 | trees 0.671, water 0.0, ob 0.0, fw 1.0 |
| 4 | 3 | ok | 0.5 | Bl 2.1, Bl 4.0, Go 3.3, Gr 1.1, Wh 1.9 | planned |   |   |  |  |
| 5 | 5 | ok | 1.1 | Bl 2.7, Bl 1.9, Go 22.2, Gr 6.2, Wh 5.3 |  | Driver -15 | Driver -22 | 0.0 | trees 0.453, ob 0.189, fw 1.0 |
| 6 | 3 | ok | 2.2 | Bl 1.5, Bl 2.9, Go 3.0, Gr 3.1, Wh 1.1 | planned |   |   |  |  |
| 7 | 4 | ok | 0.9 | Bl 10.3, Bl 6.2, Go 5.3, Gr 4.4, Wh 4.9 |  | 4-wood -40 | 4-wood -40 | 0.0 | trees 0.397, water 1.0, ob 0.111, fw 1.0 |
| 8 | 4 | ok | 1.5 | Bl 4.4, Bl 4.8, Go 0.3, Gr 5.2, Wh 1.3 |  | Driver -18 | 4-wood -10 | 0.0071 | trees 0.219, ob 0.241, fw 1.0 |
| 9 | 4 | ok | 1.1 | Bl 5.6, Bl 5.1, Go 4.9, Gr 4.0, Wh 1.1 |  | 4-wood -10 | 4-wood -2 | 0.0 | trees 0.0, water 0.992, ob 0.0, fw 1.0 |
| 10 | 4 | ok | 1.0 | Bl 1.7, Bl 1.7, Go 1.6, Gr 5.8, Wh 2.2 |  | Driver +8 | Driver +8 | 0.0 | trees 0.0, water 0.0, fw 1.0 |
| 11 | 4 | ok | 1.3 | Bl 6.0, Bl 2.0, Go 1.9, Gr 6.1, Wh 1.8 |  | Driver -8 | Driver -8 | 0.0 | trees 0.333, fw 1.0 |
| 12 | 4 | ok | 1.0 | Bl 2.3, Bl 1.3, Go 1.2, Gr 6.8, Wh 1.2 |  | 4-wood +2 | 4-wood +10 | 0.0 | trees 0.542, fw 1.0 |
| 13 | 4 | ok | 0.7 | Bl 7.0, Bl 0.3, Go 1.7, Gr 6.0, Wh 0.8 |  | Driver -2 | Driver -2 | 0.0 | trees 0.632, water 0.486, fw 1.0 |
| 14 | 3 | ok | 0.9 | Bl 3.5, Bl 1.1, Go 3.4, Gr 1.2, Wh 1.2 | planned |   |   |  |  |
| 15 | 5 | ok | 3.2 | Bl 1.7, Bl 3.2, Go 20.7, Gr 6.0, Wh 1.7 |  | Driver +38 | Driver +38 | 0.0 | trees 0.88, fw 1.0 |
| 16 | 3 | ok | 2.1 | Bl 4.7, Bl 2.4, Go 2.0, Gr 4.0, Wh 1.7 | planned |   |   |  |  |
| 17 | 4 | ok | 3.4 | Bl 2.1, Bl 2.9, Go 3.2, Gr 2.7, Wh 3.2 |  | 4-wood +8 | 4-wood +8 | 0.0 | trees 0.658, ob 0.0, fw 1.0 |
| 18 | 5 | ok | 0.4 | Bl 15.1, Bl 5.0, Go 5.2, Gr 5.2, Wh 1.1 |  | Driver -32 | Driver -20 | 0.0 | trees 0.088, water 1.0, ob 0.053, fw 1.0 |
