# eagle_knoll: auto vs hand truth (gate)

Auto package: `course_data/library/gate/gate_eagle_knoll/package.json`; tee set Back; quick decision n=8000.

* routing ok 18/18, par ok 18/18, green within 10 yds 18/18
* tees within 10 yds 69/72 (median 0.0 yds; 0 set-holes with no auto tee)
* par 3s planned as par 3 4/4, with a green outline 4/4
* tee-shot picks: same club 13/14, same or tie 14/14, total regret 0.012 strokes
* corridor IoU (mean): trees 0.692, long grass 0.0, water 0.75, ob 0.617

| hole | par | routing | green err | tee err by set | par 3 | auto pick | truth pick | regret | IoU |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver -32 | Driver -30 | 0.0 | trees 0.811, fw 1.0 |
| 2 | 3 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 | planned |   |   |  |  |
| 3 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver +10 | Driver +10 | 0.0 | trees 0.865, fw 1.0 |
| 4 | 4 | ok | 0.0 | Ea 0.0, Ba 9.0, Mi 0.0, Fo 0.0 |  | Driver -10 | Driver -15 | 0.0 | trees 0.75, fw 1.0 |
| 5 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver +8 | Driver +5 | 0.0 | trees 0.693, fw 1.0 |
| 6 | 3 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 | planned |   |   |  |  |
| 7 | 5 | ok | 0.0 | Ea 11.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver -2 | Driver -5 | 0.0 | trees 0.735, fw 0.995 |
| 8 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver +8 | Driver +8 | 0.0 | trees 0.333, fw 0.993 |
| 9 | 5 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver +0 | Driver -2 | 0.0 | trees 0.615, long  0.0, fw 1.0 |
| 10 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | 4-wood +2 | 4-wood +2 | 0.0 | trees 0.791, fw 1.0 |
| 11 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | 4-wood +0 | 4-wood +0 | 0.0 | trees 0.385, long  0.0, fw 1.0 |
| 12 | 3 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 | planned |   |   |  |  |
| 13 | 5 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Driver +18 | Driver +15 | 0.0 | , fw 1.0 |
| 14 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | Mid iron +12 | Mid iron +10 | 0.0 | trees 0.739, water 1.0, fw 1.0 |
| 15 | 4 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 |  | 4-wood -15 | 4-wood -15 | 0.0 | trees 0.895, fw 0.989 |
| 16 | 3 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 0.0 | planned |   |   |  |  |
| 17 | 5 | ok | 0.0 | Ea 0.0, Ba 0.0, Mi 0.0, Fo 9.0 |  | Driver -28 | 4-wood +8 | 0.0118 | trees 0.752, water 0.5, fw 1.0 |
| 18 | 4 | ok | 0.0 | Ea 12.0, Ba 0.0, Mi 0.0, Fo 14.0 |  | Driver +2 | Driver +2 | 0.0 | trees 0.63, ob 0.617, fw 0.988 |
