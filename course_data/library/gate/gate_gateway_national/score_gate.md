# gateway_national: auto vs hand truth (gate)

Auto package: `course_data/library/gate/gate_gateway_national/package.json`; tee set Back; quick decision n=8000.

* routing ok 18/18, par ok 18/18, green within 10 yds 18/18
* tees within 10 yds 88/90 (median 0.0 yds; 0 set-holes with no auto tee)
* par 3s planned as par 3 5/5, with a green outline 5/5
* tee-shot picks: same club 11/13, same or tie 11/13, total regret 0.128 strokes
* corridor IoU (mean): long grass 0.0, water 1.0, trees 0.165, ob 0.0

| hole | par | routing | green err | tee err by set | par 3 | auto pick | truth pick | regret | IoU |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | ok | 0.0 | Ba 0.0, Ch 0.0, Fo 17.6, Mi 0.0, Th 0.0 |  | Driver -5 | Driver -8 | 0.0 | long  0.0, fw 0.992 |
| 2 | 4 | ok | 0.0 | Ba 0.0, Ch 0.0, Fo 0.0, Mi 0.0, Th 0.0 |  | Driver -5 | Driver +0 | 0.0 | long  0.0, water 1.0, fw 1.0 |
| 3 | 5 | ok | 0.0 | Ba 0.0, Ch 0.0, Fo 0.0, Mi 0.0, Th 0.0 |  | Driver -8 | Driver -8 | 0.0 | trees 0.0, long  0.0, ob 0.0, fw 1.0 |
| 4 | 3 | ok | 0.0 | Ba 0.0, Ch 0.0, Fo 0.0, Mi 0.0, Th 0.0 | planned |   |   |  |  |
| 5 | 4 | ok | 0.0 | Ba 0.0, Ch 0.0, Fo 0.0, Mi 0.0, Th 0.0 |  | Driver -2 | Driver -2 | 0.0 | long  0.0, fw 1.0 |
| 6 | 5 | ok | 0.0 | Ba 0.0, Ch 0.0, Fo 0.0, Mi 0.0, Th 0.0 |  | Driver +2 | Driver +5 | 0.0 | trees 0.722, long  0.0, fw 1.0 |
| 7 | 3 | ok | 0.0 | Ba 0.0, Ch 0.0, Fo 0.0, Mi 15.0, Th 0.0 | planned |   |   |  |  |
| 8 | 4 | ok | 0.0 | Ba 0.0, Ch 0.0, Fo 0.0, Mi 0.0, Th 0.0 |  | 2-wood -40 | 2-wood -40 | 0.0 | trees 0.103, long  0.0, fw 1.0 |
| 9 | 4 | ok | 0.0 | Ba 0.0, Ch 0.0, Fo 0.0, Mi 0.0, Th 0.0 |  | 2-wood +8 | 4-wood +2 | 0.0357 | trees 0.0, long  0.0, water 1.0, fw 1.0 |
| 10 | 4 | ok | 0.0 | Ba 0.0, Ch 0.0, Fo 0.0, Mi 0.0, Th 0.0 |  | 4-wood -25 | 4-wood -15 | 0.0 | long  0.0, water 1.0, fw 1.0 |
| 11 | 4 | ok | 0.0 | Ba 0.0, Ch 0.0, Fo 0.0, Mi 0.0, Th 0.0 |  | Driver +22 | 4-wood +8 | 0.0923 | long  0.0, fw 1.0 |
| 12 | 3 | ok | 0.0 | Ba 0.0, Ch 0.0, Fo 0.0, Mi 10.0, Th 0.0 | planned |   |   |  |  |
| 13 | 5 | ok | 0.0 | Ba 0.0, Ch 0.0, Fo 0.0, Mi 0.0, Th 0.0 |  | Driver +10 | Driver +2 | 0.0 | long  0.0, water 1.0, fw 1.0 |
| 14 | 3 | ok | 0.0 | Ba 0.0, Ch 0.0, Fo 0.0, Mi 0.0, Th 0.0 | planned |   |   |  |  |
| 15 | 4 | ok | 0.0 | Ba 0.0, Ch 0.0, Fo 0.0, Mi 0.0, Th 0.0 |  | Driver +10 | Driver +12 | 0.0 | long  0.0, fw 0.996 |
| 16 | 4 | ok | 0.0 | Ba 0.0, Ch 0.0, Fo 0.0, Mi 0.0, Th 0.0 |  | 4-wood +0 | 4-wood -2 | 0.0 | long  0.0, water 1.0, fw 0.994 |
| 17 | 3 | ok | 0.0 | Ba 0.0, Ch 0.0, Fo 0.0, Mi 0.0, Th 0.0 | planned |   |   |  |  |
| 18 | 5 | ok | 0.0 | Ba 0.0, Ch 0.0, Fo 0.0, Mi 0.0, Th 0.0 |  | Driver +15 | Driver +18 | 0.0 | trees 0.0, long  0.0, fw 1.0 |
