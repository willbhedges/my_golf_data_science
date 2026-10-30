# national_kc: auto vs hand truth (gate)

Auto package: `course_data/library/gate/gate_national_kc/package.json`; tee set Black; quick decision n=8000.

* routing ok 2/18, par ok 5/18, green within 10 yds 2/18
* tees within 10 yds 0/0 (median None yds; 90 set-holes with no auto tee)
* par 3s planned as par 3 1/4, with a green outline 4/4
* tee-shot picks: same club 6/9, same or tie 6/9, total regret 0.431 strokes
* corridor IoU (mean): trees 0.077, water 0.263, ob 0.0

| hole | par | routing | green err | tee err by set | par 3 | auto pick | truth pick | regret | IoU |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 (auto 3) | ok | 2.9 | Bl -, Bl -, Go -, Gr -, Wh - |  |   |   |  |  |
| 2 | 5 | ok | 1.7 | Bl -, Bl -, Go -, Gr -, Wh - |  | Driver -10 | Driver -10 | 0.0 | trees 0.542, water 0.789, ob 0.0, fw 1.0 |
| 3 | 4 (auto 5) | green is truth hole 5's | 791.3 | Bl -, Bl -, Go -, Gr -, Wh - |  | Driver -18 | Driver -12 | 0.0 | trees 0.0, fw 0.0 |
| 4 | 3 | green is truth hole 6's | 448.0 | Bl -, Bl -, Go -, Gr -, Wh - | planned |   |   |  |  |
| 5 | 5 (auto 4) | green is truth hole 7's | 410.2 | Bl -, Bl -, Go -, Gr -, Wh - |  | 4-wood -40 | 4-wood +0 | 0.0 | trees 0.155, ob 0.0, fw 0.0 |
| 6 | 3 (auto 4) | green is truth hole 8's | 245.8 | Bl -, Bl -, Go -, Gr -, Wh - | NOT planned |   |   |  |  |
| 7 | 4 | green off (> 25 yds) | 432.5 | Bl -, Bl -, Go -, Gr -, Wh - |  | 4-wood -2 | Driver -5 | 0.0751 | trees 0.0, water 0.0, ob 0.0, fw 0.0 |
| 8 | 4 | green off (> 25 yds) | 414.0 | Bl -, Bl -, Go -, Gr -, Wh - |  | Long iron -40 | Driver +32 | 0.2769 | trees 0.0, ob 0.0, fw 0.0 |
| 9 | 4 (auto 3) | green off (> 25 yds) | 776.8 | Bl -, Bl -, Go -, Gr -, Wh - |  |   |   |  |  |
| 10 | 4 (auto 3) | green is truth hole 4's | 1479.2 | Bl -, Bl -, Go -, Gr -, Wh - |  |   |   |  |  |
| 11 | 4 (auto 3) | green off (> 25 yds) | 1208.6 | Bl -, Bl -, Go -, Gr -, Wh - |  |   |   |  |  |
| 12 | 4 | green is truth hole 10's | 225.7 | Bl -, Bl -, Go -, Gr -, Wh - |  | Driver +12 | Driver +40 | 0.0 | trees 0.0, fw 0.0 |
| 13 | 4 (auto 5) | green is truth hole 11's | 534.3 | Bl -, Bl -, Go -, Gr -, Wh - |  | Driver -8 | 4-wood +0 | 0.0789 | trees 0.0, water 0.0, fw 0.0 |
| 14 | 3 (auto 4) | green is truth hole 12's | 404.7 | Bl -, Bl -, Go -, Gr -, Wh - | NOT planned |   |   |  |  |
| 15 | 5 (auto 4) | green is truth hole 13's | 716.1 | Bl -, Bl -, Go -, Gr -, Wh - |  | Driver -2 | Driver +8 | 0.0 | trees 0.0, fw 0.0 |
| 16 | 3 (auto 4) | green is truth hole 18's | 1009.2 | Bl -, Bl -, Go -, Gr -, Wh - | NOT planned |   |   |  |  |
| 17 | 4 (auto 5) | green is truth hole 15's | 720.9 | Bl -, Bl -, Go -, Gr -, Wh - |  | Driver +40 | Driver +0 | 0.0 | trees 0.0, fw 0.0 |
| 18 | 5 (auto 3) | green is truth hole 16's | 1007.3 | Bl -, Bl -, Go -, Gr -, Wh - |  |   |   |  |  |
