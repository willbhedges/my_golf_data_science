# eagle_knoll: auto vs hand truth (before)

Auto package: `course_data/courses/eagle_knoll/auto/package.json`; tee set Back; quick decision n=6000.

* routing ok 18/18, par ok 18/18, green within 10 yds 18/18
* tees within 10 yds 69/72 (median 0.0 yds; 0 set-holes with no auto tee)
* par 3s planned as par 3 4/4, with a green outline 4/4
* tee-shot picks: same club 13/14, same or tie 14/14, total regret 0.019 strokes
* corridor IoU (mean): trees 0.845, long grass 0.0, water 0.75, ob 0.617

| hole | par | routing | green err | tee err by set | par 3 | auto pick | truth pick | regret | IoU |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver -30 | Driver -30 | 0.0 | trees 0.805, fw 1.0 |
| 2 | 3 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 | planned |   |   |  |  |
| 3 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver +10 | Driver +10 | 0.0 | trees 0.902, fw 1.0 |
| 4 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver -8 | Driver -8 | 0.0 | trees 0.767, fw 1.0 |
| 5 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver +5 | Driver +5 | 0.0 | trees 0.927, fw 1.0 |
| 6 | 3 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 | planned |   |   |  |  |
| 7 | 5 | ok | 0.0 | Ea 11.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver -5 | Driver -5 | 0.0 | trees 0.87, fw 0.995 |
| 8 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver +8 | Driver +8 | 0.0 | trees 1.0, fw 0.993 |
| 9 | 5 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver +0 | Driver +0 | 0.0 | trees 0.889, long  0.0, fw 1.0 |
| 10 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | 4-wood +2 | 4-wood +2 | 0.0 | trees 0.839, fw 1.0 |
| 11 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | 4-wood +0 | 4-wood -2 | 0.0 | trees 0.7, long  0.0, fw 1.0 |
| 12 | 3 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 | planned |   |   |  |  |
| 13 | 5 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver +15 | Driver +15 | 0.0 | , fw 1.0 |
| 14 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Mid iron +12 | Mid iron +10 | 0.0 | trees 0.747, water 1.0, fw 1.0 |
| 15 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | 4-wood -15 | 4-wood -15 | 0.0 | trees 0.945, fw 0.989 |
| 16 | 3 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 | planned |   |   |  |  |
| 17 | 5 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 9.0 |  | Driver -30 | 4-wood +10 | 0.019 | trees 0.855, water 0.5, fw 1.0 |
| 18 | 4 | ok | 0.0 | Ea 12.0, Ba 0.0, Mi 0.0, Fo 14.0 |  | Driver +0 | Driver +2 | 0.0 | trees 0.74, ob 0.617, fw 0.988 |
