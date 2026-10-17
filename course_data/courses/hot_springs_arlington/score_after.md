# hot_springs_arlington: auto vs hand truth (after)

Auto package: `course_data/courses/hot_springs_arlington/auto/package_v3_vision.json`; tee set Gold; quick decision n=4000.

* routing ok 18/18, par ok 18/18, green within 10 yds 18/18
* tees within 10 yds 51/72 (median 2.5 yds; 0 set-holes with no auto tee)
* par 3s planned as par 3 4/4, with a green outline 2/4
* tee-shot picks: same club 12/14, same or tie 14/14, total regret 0.038 strokes
* corridor IoU (mean): trees 0.677, ob 0.0

| hole | par | routing | green err | tee err by set | par 3 | auto pick | truth pick | regret | IoU |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | ok | 1.7 | Go 1.2, Bl 13.5, Gr 0.6, Wh 0.5 |  | Driver -25 | 4-wood -22 | 0.0089 | trees 0.836, ob 0.0 |
| 2 | 3 | ok | 1.4 | Go 1.3, Bl 1.0, Gr 2.4, Wh 1.0 | planned |   |   |  |  |
| 3 | 4 | ok | 0.0 | Go 0.2, Bl 65.8, Gr 65.9, Wh 65.9 |  | 2-wood -40 | 2-wood -40 | 0.0 | trees 0.947 |
| 4 | 4 | ok | 1.8 | Go 17.6, Bl 17.4, Gr 2.0, Wh 62.3 |  | Driver +5 | 4-wood -5 | 0.0296 | trees 0.822 |
| 5 | 4 | ok | 0.0 | Go 2.8, Bl 2.0, Gr 2.0, Wh 2.0 |  | 4-wood +15 | 4-wood +15 | 0.0 | trees 0.789 |
| 6 | 5 | ok | 2.1 | Go 2.1, Bl 2.3, Gr 2.4, Wh 38.9 |  | Driver -40 | Driver -40 | 0.0 | trees 0.658 |
| 7 | 4 | ok | 1.3 | Go 1.6, Bl 1.4, Gr 1.6, Wh 2.2 |  | 2-wood -25 | 2-wood -25 | 0.0 | trees 0.715 |
| 8 | 3 | ok | 0.0 | Go 5.9, Bl 0.9, Gr 5.5, Wh 0.9 | planned, no outline |   |   |  |  |
| 9 | 5 | ok | 0.0 | Go 28.1, Bl 28.0, Gr 90.9, Wh 100.3 |  | Driver +10 | Driver +40 | 0.0 | trees 0.804 |
| 10 | 5 | ok | 2.3 | Go 8.6, Bl 1.0, Gr 12.9, Wh 12.5 |  | Driver +15 | Driver +0 | 0.0 | trees 0.368, ob 0.0 |
| 11 | 3 | ok | 0.0 | Go 5.5, Bl 2.1, Gr 39.5, Wh 39.5 | planned, no outline |   |   |  |  |
| 12 | 4 | ok | 2.0 | Go 8.2, Bl 1.5, Gr 4.4, Wh 8.6 |  | Driver +8 | Driver +5 | 0.0 | trees 0.445, ob 0.0 |
| 13 | 4 | ok | 0.2 | Go 1.0, Bl 1.0, Gr 10.6, Wh 28.0 |  | Driver +5 | Driver +15 | 0.0 | trees 0.515 |
| 14 | 4 | ok | 1.2 | Go 5.4, Bl 24.5, Gr 20.7, Wh 11.7 |  | Driver -2 | Driver -5 | 0.0 | trees 0.522 |
| 15 | 4 | ok | 1.0 | Go 2.8, Bl 1.0, Gr 1.0, Wh 1.0 |  | Driver -40 | Driver -38 | 0.0 | trees 0.832 |
| 16 | 4 | ok | 0.8 | Go 0.6, Bl 1.1, Gr 1.3, Wh 1.1 |  | Driver -22 | Driver -22 | 0.0 | trees 0.555 |
| 17 | 3 | ok | 1.7 | Go 6.4, Bl 2.6, Gr 2.8, Wh 4.0 | planned |   |   |  |  |
| 18 | 5 | ok | 0.0 | Go 0.7, Bl 1.1, Gr 6.3, Wh 1.0 |  | Driver +38 | Driver +8 | 0.0 | trees 0.664 |
