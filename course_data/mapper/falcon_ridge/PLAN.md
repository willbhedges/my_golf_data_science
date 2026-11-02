# Plan with the mapper's layers: Falcon Ridge Golf Course (Black tees)

Quick decision (n = 2000, seed 31) on the base package and on base + agent layers (ok: course_data/mapper/falcon_ridge (11 zone edits on 9 holes, 0 tee(s) moved, 72 checked)). Changed = other club, or aim points > 10 yds apart.

| hole | AUTO | AUTO + AGENT | aim apart (yds) | changed | agent edits on the hole |
|---|---|---|---|---|---|
| 1 | Driver +5 (tie) | 4-wood +0 (tie) | 20.6 | **yes** | add recovery 223 yd2 |
| 2 | 4-wood -5 (tie) | 4-wood -5 (tie) | 0.0 |  | checked, no change |
| 3 | 4-wood +0 | 4-wood +0 | 0.0 |  | checked, no change |
| 4 | Driver -2 | Driver -2 | 0.0 |  | checked, no change |
| 6 | Driver +5 | Driver +5 | 0.0 |  | add fairway 5965 yd2; grow recovery +3 yd (+492 yd2) |
| 8 | Driver +18 | Driver +5 | 12.5 | **yes** | add fairway 7964 yd2 |
| 9 | Driver +0 | Driver +0 | 0.0 |  | add fairway 8078 yd2 |
| 10 | 4-wood +2 (tie) | 4-wood +2 (tie) | 0.0 |  | add water 251 yd2 |
| 11 | 4-wood +5 | 4-wood +5 | 0.0 |  | add water 414 yd2; add recovery 151 yd2 |
| 13 | Driver -15 | Driver -12 | 2.5 |  | add fairway 6499 yd2 |
| 15 | Driver +15 | Driver -2 | 17.4 | **yes** | add fairway 8118 yd2 |
| 17 | Driver -22 | Driver -22 | 0.0 |  | checked, no change |
| 18 | 4-wood +5 | 4-wood +5 | 0.0 |  | erase recovery 199 yd2 |

3 of 13 tee shots change. Page: add `"agent_layers": "course_data/mapper/falcon_ridge/"` to `course_data/requests/course_page_falcon_ridge.json` (coordinator).
