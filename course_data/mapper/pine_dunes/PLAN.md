# Plan with the mapper's layers: Pine Dunes Resort & Golf Club (Gold tees)

Quick decision (n = 2000, seed 31) on the base package and on base + agent layers (ok: course_data/mapper/pine_dunes (29 zone edits on 13 holes, 0 tee(s) moved, 72 checked)). Changed = other club, or aim points > 10 yds apart.

| hole | AUTO | AUTO + AGENT | aim apart (yds) | changed | agent edits on the hole |
|---|---|---|---|---|---|
| 1 | 4-wood +5 (tie) | 4-wood +8 | 2.5 |  | add sand 550 yd2; add recovery 223 yd2; add recovery 77 yd2 |
| 2 | Driver +5 | Driver +2 | 2.5 |  | add sand 1586 yd2 |
| 4 | Driver -2 | Driver -2 | 0.0 |  | checked, no change |
| 5 | Driver -22 | Driver -22 | 0.0 |  | add sand 952 yd2 |
| 7 | Driver +5 | Driver +5 | 0.0 |  | erase sand 1712 yd2; add recovery 3500 yd2 |
| 8 | 4-wood +2 | 4-wood +2 | 0.0 |  | add sand 789 yd2 |
| 9 | Driver -10 | Driver -10 | 0.0 |  | add sand 278 yd2; add sand 284 yd2; add sand 334 yd2; add sand 93 yd2 |
| 10 | 4-wood +2 | 4-wood +2 | 0.0 |  | add sand 3636 yd2; add sand 1515 yd2 |
| 11 | 2-wood +8 | 2-wood +8 | 0.0 |  | add sand 1253 yd2; add sand 996 yd2; add sand 550 yd2 |
| 13 | 4-wood -5 (tie) | 4-wood -5 (tie) | 0.0 |  | add sand 497 yd2; add sand 899 yd2; add sand 249 yd2 |
| 14 | Driver +2 | Driver +2 | 0.0 |  | add sand 108 yd2; add sand 74 yd2; add sand 99 yd2 |
| 15 | Driver -22 | Driver -22 | 0.0 |  | add sand 377 yd2; add sand 239 yd2; add sand 274 yd2 |
| 17 | Driver +8 | Driver +8 | 0.0 |  | add sand 884 yd2 |
| 18 | 4-wood +28 | 4-wood +28 | 0.0 |  | erase water 806 yd2; add sand 453 yd2 |

0 of 14 tee shots change. Page: add `"agent_layers": "course_data/mapper/pine_dunes/"` to `course_data/requests/course_page_pine_dunes.json` (coordinator).
