# Plan with the mapper's layers: Coldwater Golf Links (Blue tees)

Quick decision (n = 2000, seed 31) on the base package and on base + agent layers (ok: course_data/mapper/coldwater (35 zone edits on 14 holes, 5 tee(s) moved, 72 checked)). Changed = other club, or aim points > 10 yds apart.

| hole | AUTO | AUTO + AGENT | aim apart (yds) | changed | agent edits on the hole |
|---|---|---|---|---|---|
| 1 | Driver +2 | Driver +5 | 2.5 |  | add native 8183 yd2; add native 2273 yd2 |
| 2 | Driver +2 | 4-wood +2 (tie) | 16.7 | **yes** | add recovery 11977 yd2; tee Blue moved 28 yd |
| 3 | Driver -10 | Driver -38 | 27.4 | **yes** | add native 5807 yd2; add native 688 yd2; erase fairway 96 yd2 |
| 4 | Driver -18 | 4-wood -5 | 23.5 | **yes** | add native 7473 yd2; add native 519 yd2; add native 1077 yd2; add ob 3765 yd2 |
| 6 | Driver +5 | Driver -2 | 7.5 |  | add native 3038 yd2; add native 1553 yd2 |
| 7 | Driver +2 | 4-wood -8 | 22.3 | **yes** | add recovery 9653 yd2; add native 8487 yd2; add native 5011 yd2; add native 680 yd2; add ob 1552 yd2; tee Black moved 16 yd |
| 9 | 4-wood -40 | 4-wood -40 (tie) | 0.0 |  | add native 6959 yd2; add native 9630 yd2 |
| 10 | Driver -10 (tie) | 4-wood -2 | 21.3 | **yes** | add native 11157 yd2; add native 5984 yd2; add recovery 108 yd2 |
| 12 | Driver +0 | Driver +8 | 7.5 |  | add native 7590 yd2; add native 2648 yd2 |
| 13 | Driver +5 | Driver +2 (tie) | 9.0 |  | add native 6778 yd2; add native 4008 yd2; tee Blue moved 11 yd |
| 14 | Driver +0 | 4-wood +0 | 20.0 | **yes** | add recovery 8500 yd2; add native 14717 yd2; add native 5966 yd2 |
| 15 | Driver -2 | 4-wood -8 | 20.5 | **yes** | add recovery 10300 yd2; add native 11293 yd2 |
| 17 | 4-wood +10 (tie) | 4-wood +2 | 7.5 |  | add native 9787 yd2; add native 7633 yd2 |
| 18 | Driver -10 | 4-wood -8 | 20.1 | **yes** | add native 8515 yd2; add native 11448 yd2 |

8 of 14 tee shots change. Page: add `"agent_layers": "course_data/mapper/coldwater/"` to `course_data/requests/course_page_coldwater.json` (coordinator).
