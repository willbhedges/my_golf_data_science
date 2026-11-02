# Plan with the mapper's layers: A. L. Gustin Golf Course (Black tees)

Quick decision (n = 2000, seed 31) on the base package and on base + agent layers (ok: course_data/mapper/gustin (103 zone edits on 14 holes, 0 tee(s) moved, 54 checked)). Changed = other club, or aim points > 10 yds apart.

| hole | AUTO | AUTO + AGENT | aim apart (yds) | changed | agent edits on the hole |
|---|---|---|---|---|---|
| 1 | Driver +8 | Driver +8 | 0.0 |  | add recovery 105 yd2; add recovery 402 yd2; add recovery 699 yd2; add recovery 135 yd2; add recovery 569 yd2; add recovery 168 yd2; add recovery 45 yd2; add recovery 119 yd2; add recovery 214 yd2 |
| 3 | Driver +20 | Driver +20 | 0.0 |  | add recovery 316 yd2; add recovery 2010 yd2; add recovery 49 yd2; add recovery 33 yd2 |
| 4 | Driver +0 | 4-wood +5 | 20.6 | **yes** | add recovery 2367 yd2; add recovery 309 yd2; add recovery 50 yd2; add recovery 33 yd2; add recovery 36 yd2; add recovery 37 yd2; add recovery 247 yd2; add recovery 101 yd2; add recovery 366 yd2 |
| 6 | 4-wood -38 | 4-wood -38 | 0.0 |  | add recovery 52 yd2; add recovery 195 yd2; add recovery 71 yd2; add recovery 105 yd2; add recovery 45 yd2; add recovery 109 yd2; add recovery 111 yd2; add recovery 87 yd2 |
| 7 | 4-wood -8 | 4-wood -8 | 0.0 |  | add recovery 43 yd2; add recovery 136 yd2; add recovery 52 yd2; add recovery 194 yd2; add recovery 16 yd2; add recovery 107 yd2; add recovery 112 yd2; add recovery 250 yd2 |
| 8 | 4-wood -2 | 4-wood +0 | 2.5 |  | add recovery 342 yd2; add recovery 116 yd2; add recovery 167 yd2; add recovery 94 yd2; add recovery 91 yd2; add recovery 56 yd2; add recovery 436 yd2 |
| 9 | Driver -2 | 4-wood +10 (tie) | 23.5 | **yes** | add recovery 141 yd2; add recovery 146 yd2; add recovery 554 yd2; add recovery 45 yd2; add recovery 116 yd2 |
| 11 | Driver -2 (tie) | 4-wood -2 (tie) | 19.9 | **yes** | add recovery 36 yd2; add recovery 324 yd2; add recovery 25 yd2; add recovery 298 yd2; add recovery 69 yd2; add recovery 76 yd2; add recovery 33 yd2; add recovery 164 yd2; add recovery 280 yd2; add recovery 29 yd2; add recovery 144 yd2; add recovery 112 yd2; add recovery 161 yd2 |
| 12 | Driver +8 | Driver +5 | 2.5 |  | add recovery 90 yd2; add recovery 236 yd2; erase ob 4015 yd2 |
| 14 | 4-wood +0 | 4-wood +2 | 2.5 |  | add recovery 69 yd2; add recovery 520 yd2; add recovery 536 yd2; add recovery 16 yd2; erase water 449 yd2 |
| 15 | Driver +8 | Driver +8 | 0.0 |  | add recovery 112 yd2; add recovery 42 yd2; add recovery 352 yd2; add recovery 86 yd2 |
| 16 | 2-wood +58 (tie) | 2-wood +52 | 5.0 |  | add recovery 158 yd2; add recovery 259 yd2; add recovery 184 yd2; add recovery 217 yd2; add recovery 181 yd2 |
| 17 | Driver +22 | Driver +22 | 0.0 |  | add recovery 246 yd2; add recovery 2410 yd2; add recovery 168 yd2; add recovery 163 yd2; add recovery 138 yd2; add recovery 33 yd2; add recovery 151 yd2; add recovery 316 yd2; add recovery 28 yd2; add recovery 59 yd2 |
| 18 | 4-wood +0 | 4-wood -2 | 2.5 |  | add recovery 69 yd2; add recovery 108 yd2; add recovery 268 yd2; add recovery 196 yd2; add recovery 27 yd2; add recovery 30 yd2; add recovery 420 yd2; add recovery 73 yd2; add recovery 27 yd2; add recovery 247 yd2; add recovery 935 yd2; add recovery 129 yd2; add recovery 17 yd2 |

3 of 14 tee shots change. Page: add `"agent_layers": "course_data/mapper/gustin/"` to `course_data/requests/course_page_gustin.json` (coordinator).
