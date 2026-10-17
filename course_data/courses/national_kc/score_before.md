# national_kc: auto vs hand truth (before)

Auto package: `course_data/courses/national_kc/auto/package.json`; tee set Black; quick decision n=4000.

* routing ok 3/18, par ok 6/18, green within 10 yds 3/18
* tees within 10 yds 0/0 (median None yds; 80 set-holes with no auto tee)
* par 3s planned as par 3 0/4, with a green outline 4/4
* tee-shot picks: same club 9/10, same or tie 9/10, total regret 0.221 strokes
* corridor IoU (mean): trees 0.0, water 0.4, ob 0.012

| hole | par | routing | green err | tee err by set | par 3 | auto pick | truth pick | regret | IoU |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 (auto 3) | ok | 2.9 | Bl -, Bl -, Go -, Gr -, Wh - |  |   |   |  |  |
| 2 | 5 | ok | 1.7 | Bl -, Bl -, Go -, Gr -, Wh - |  | Driver -5 | Driver -8 | 0.0 | trees 0.0, water 1.0, ob 0.0, fw 1.0 |
| 3 | 4 | missing in auto | None |  |  |   |   |  |  |
| 4 | 3 (auto 4) | green is truth hole 17's | 1523.8 | Bl -, Bl -, Go -, Gr -, Wh - | NOT planned |   |   |  |  |
| 5 | 5 | green is truth hole 11's | 601.5 | Bl -, Bl -, Go -, Gr -, Wh - |  | Driver -25 | Driver +30 | 0.0 | trees 0.0, ob 0.0, fw 0.0 |
| 6 | 3 (auto 4) | green is truth hole 12's | 1105.5 | Bl -, Bl -, Go -, Gr -, Wh - | NOT planned |   |   |  |  |
| 7 | 4 | green is truth hole 13's | 1391.7 | Bl -, Bl -, Go -, Gr -, Wh - |  | Driver -5 | Driver +0 | 0.0 | trees 0.0, water 0.0, ob 0.0, fw 0.0 |
| 8 | 4 (auto 3) | green is truth hole 14's | 1222.1 | Bl -, Bl -, Go -, Gr -, Wh - |  |   |   |  |  |
| 9 | 4 (auto 5) | green is truth hole 15's | 1347.6 | Bl -, Bl -, Go -, Gr -, Wh - |  | Driver +35 | Driver +0 | 0.0 | trees 0.0, water 0.0, ob 0.0, fw 0.0 |
| 10 | 4 (auto 5) | green is truth hole 4's | 1479.2 | Bl -, Bl -, Go -, Gr -, Wh - |  | Driver +38 | Driver +0 | 0.0 | trees 0.0, fw 0.0 |
| 11 | 4 | green is truth hole 5's | 603.2 | Bl -, Bl -, Go -, Gr -, Wh - |  | Driver -2 | Driver -68 | 0.0 | trees 0.0, fw 0.0 |
| 12 | 4 | green is truth hole 7's | 1151.5 | Bl -, Bl -, Go -, Gr -, Wh - |  | Driver -18 | Driver +0 | 0.0 | trees 0.0, fw 0.0 |
| 13 | 4 | green is truth hole 8's | 1081.5 | Bl -, Bl -, Go -, Gr -, Wh - |  | Driver -15 | Driver +58 | 0.0 | trees 0.0, water 0.0, fw 0.0 |
| 14 | 3 (auto 4) | green is truth hole 9's | 775.2 | Bl -, Bl -, Go -, Gr -, Wh - | NOT planned |   |   |  |  |
| 15 | 5 | missing in auto | None |  |  |   |   |  |  |
| 16 | 3 (auto 4) | green off (> 25 yds) | 1261.3 | Bl -, Bl -, Go -, Gr -, Wh - | NOT planned |   |   |  |  |
| 17 | 4 (auto 5) | green is truth hole 10's | 157.9 | Bl -, Bl -, Go -, Gr -, Wh - |  | Driver +40 | 4-wood -18 | 0.2208 | trees 0.0, fw 0.0 |
| 18 | 5 (auto 4) | ok | 0.4 | Bl -, Bl -, Go -, Gr -, Wh - |  | 4-wood +20 | 4-wood +0 | 0.0 | trees 0.0, water 1.0, ob 0.062, fw 1.0 |
