# blue_hills: auto vs hand truth (v0_no_vision)

Auto package: `course_data/courses/blue_hills/auto/package_v0_no_vision.json`; tee set Black; quick decision n=8000.

* routing ok 18/18, par ok 18/18, green within 10 yds 18/18
* tees within 10 yds 136/144 (median 1.1 yds; 0 set-holes with no auto tee)
* par 3s planned as par 3 4/4, with a green outline 4/4
* tee-shot picks: same club 9/14, same or tie 9/14, total regret 0.262 strokes
* corridor IoU (mean): trees 0.0, ob 0.99, water 0.0

| hole | par | routing | green err | tee err by set | par 3 | auto pick | truth pick | regret | IoU |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | ok | 0.3 | Bl 0.4, Bl 1.5, Wh 0.4, Go 0.4, Re 0.3, Bl 1.5, Wh 0.4, Go 0.4 |  | Driver -5 | Driver +0 | 0.0 | trees 0.0, ob 1.0, fw 0.994 |
| 2 | 4 | ok | 1.2 | Bl 22.1, Bl 0.8, Wh 0.5, Go 0.9, Re 2.1, Bl 0.8, Wh 0.5, Go 0.9 |  | 4-wood +8 | 4-wood +8 | 0.0 | trees 0.0, ob 1.0, fw 0.992 |
| 3 | 4 | ok | 0.8 | Bl 0.6, Bl 0.1, Wh 0.1, Go 0.1, Re 0.0, Bl 0.1, Wh 0.1, Go 0.1 |  | Driver +8 | 4-wood -2 | 0.1671 | trees 0.0, fw 1.0 |
| 4 | 4 | ok | 2.2 | Bl 2.1, Bl 0.7, Wh 13.8, Go 4.1, Re 0.8, Bl 13.8, Wh 4.1, Go 0.8 |  | Driver +8 | 2-wood +12 | 0.0366 | trees 0.0, ob 0.985, fw 1.0 |
| 5 | 3 | ok | 1.7 | Bl 2.1, Bl 0.8, Wh 2.6, Go 0.0, Re 0.0, Bl 2.6, Wh 2.6, Go 0.0 | planned |   |   |  |  |
| 6 | 5 | ok | 0.8 | Bl 2.6, Bl 1.8, Wh 0.4, Go 0.0, Re 0.2, Bl 0.4, Wh 0.0, Go 0.0 |  | Driver -5 | Driver -5 | 0.0 | trees 0.0, fw 1.0 |
| 7 | 4 | ok | 1.9 | Bl 0.5, Bl 0.5, Wh 0.7, Go 0.3, Re 0.6, Bl 0.5, Wh 0.7, Go 0.3 |  | 4-wood +2 | 4-wood +0 | 0.0 | trees 0.0, fw 0.993 |
| 8 | 3 | ok | 2.0 | Bl 2.1, Bl 2.1, Wh 2.1, Go 2.0, Re 2.0, Bl 2.1, Wh 2.0, Go 2.0 | planned |   |   |  |  |
| 9 | 4 | ok | 2.0 | Bl 2.3, Bl 2.2, Wh 2.1, Go 4.3, Re 0.0, Bl 2.1, Wh 4.3, Go 4.3 |  | 4-wood +10 | 4-wood +8 | 0.0 | trees 0.0, ob 1.0, fw 1.0 |
| 10 | 4 | ok | 1.5 | Bl 2.1, Bl 1.3, Wh 2.0, Go 2.1, Re 1.5, Bl 1.3, Wh 2.0, Go 2.1 |  | Driver -5 | 4-wood +2 | 0.0015 | trees 0.0, ob 0.944, fw 1.0 |
| 11 | 4 | ok | 1.7 | Bl 2.0, Bl 0.5, Wh 0.6, Go 0.6, Re 0.8, Bl 0.5, Wh 0.6, Go 0.6 |  | Driver +0 | 4-wood +2 | 0.025 | trees 0.0, ob 1.0, fw 1.0 |
| 12 | 3 | ok | 3.9 | Bl 4.4, Bl 4.4, Wh 2.4, Go 0.0, Re 0.0, Bl 2.4, Wh 0.0, Go 0.0 | planned |   |   |  |  |
| 13 | 5 | ok | 1.1 | Bl 2.1, Bl 2.2, Wh 2.2, Go 2.0, Re 1.9, Bl 2.2, Wh 2.2, Go 2.0 |  | Driver +2 | Driver +8 | 0.0 | trees 0.0, fw 1.0 |
| 14 | 3 | ok | 0.6 | Bl 0.7, Bl 0.7, Wh 1.6, Go 15.2, Re 12.2, Bl 0.7, Wh 1.6, Go 15.2 | planned |   |   |  |  |
| 15 | 4 | ok | 1.5 | Bl 0.6, Bl 1.1, Wh 10.5, Go 1.3, Re 1.4, Bl 10.5, Wh 1.3, Go 1.4 |  | Driver +0 | Driver +0 | 0.0 | trees 0.0, fw 0.993 |
| 16 | 4 | ok | 1.3 | Bl 0.7, Bl 1.4, Wh 0.7, Go 2.0, Re 1.1, Bl 0.7, Wh 2.0, Go 1.1 |  | Driver +0 | Driver +0 | 0.0 | trees 0.0, fw 1.0 |
| 17 | 4 | ok | 0.8 | Bl 2.0, Bl 0.9, Wh 1.2, Go 2.1, Re 0.0, Bl 0.9, Wh 2.1, Go 0.0 |  | Driver +35 | 4-wood +0 | 0.0316 | trees 0.0, water 0.0, fw 1.0 |
| 18 | 5 | ok | 0.5 | Bl 0.6, Bl 1.0, Wh 0.5, Go 0.0, Re 0.0, Bl 0.5, Wh 0.0, Go 0.0 |  | Driver +12 | Driver +12 | 0.0 | trees 0.0, ob 1.0, fw 1.0 |
