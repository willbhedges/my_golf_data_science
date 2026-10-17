# eagle_knoll: auto vs hand truth (v0_no_vision)

Auto package: `course_data/courses/eagle_knoll/auto/package_v0_no_vision.json`; tee set Back; quick decision n=6000.

* routing ok 18/18, par ok 18/18, green within 10 yds 18/18
* tees within 10 yds 69/72 (median 0.0 yds; 0 set-holes with no auto tee)
* par 3s planned as par 3 4/4, with a green outline 4/4
* tee-shot picks: same club 9/14, same or tie 9/14, total regret 0.261 strokes
* corridor IoU (mean): trees 0.144, ob 0.182, long grass 0.0, water 1.0

| hole | par | routing | green err | tee err by set | par 3 | auto pick | truth pick | regret | IoU |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver -38 | Driver -30 | 0.0 | trees 0.695, fw 1.0 |
| 2 | 3 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 | planned |   |   |  |  |
| 3 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver +10 | Driver +10 | 0.0 | trees 0.0, ob 0.0, fw 1.0 |
| 4 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver -15 | Driver -8 | 0.0 | trees 0.0, fw 1.0 |
| 5 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver +12 | Driver +5 | 0.0 | trees 0.0, fw 1.0 |
| 6 | 3 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 | planned |   |   |  |  |
| 7 | 5 | ok | 0.0 | Ea 11.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver +0 | Driver -5 | 0.0 | trees 0.0, fw 0.995 |
| 8 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver +8 | Driver +8 | 0.0 | trees 0.0, fw 0.993 |
| 9 | 5 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver +2 | Driver +0 | 0.0 | trees 0.0, long  0.0, fw 1.0 |
| 10 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver +0 | 4-wood +2 | 0.1007 | trees 0.093, fw 1.0 |
| 11 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver +15 | 4-wood -2 | 0.0318 | trees 0.0, long  0.0, fw 1.0 |
| 12 | 3 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 | planned |   |   |  |  |
| 13 | 5 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver +18 | Driver +15 | 0.0 | , fw 1.0 |
| 14 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | 4-wood -10 | Mid iron +10 | 0.0388 | trees 0.0, water 1.0, fw 1.0 |
| 15 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver -28 | 4-wood -15 | 0.0636 | trees 0.757, ob 0.0, fw 0.989 |
| 16 | 3 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 | planned |   |   |  |  |
| 17 | 5 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 9.0 |  | Driver -30 | 4-wood +10 | 0.0256 | trees 0.328, water 1.0, fw 1.0 |
| 18 | 4 | ok | 0.0 | Ea 12.0, Ba 0.0, Mi 0.0, Fo 14.0 |  | Driver +2 | Driver +2 | 0.0 | trees 0.0, ob 0.545, fw 0.988 |
