# Plan with the mapper's layers: Annbriar Golf Course (Black tees)

Quick decision (n = 2000, seed 31) on the base package and on base + agent layers (ok: course_data/mapper/annbriar (29 zone edits on 10 holes, 0 tee(s) moved, 90 checked)). Changed = other club, or aim points > 10 yds apart.

| hole | AUTO | AUTO + AGENT | aim apart (yds) | changed | agent edits on the hole |
|---|---|---|---|---|---|
| 1 | Driver -8 | Driver -8 | 0.0 |  | erase native 442 yd2; add recovery 151 yd2; add recovery 151 yd2 |
| 2 | Driver +2 | Driver +2 | 0.0 |  | checked, no change |
| 3 | Driver -5 | Driver -5 | 0.0 |  | erase native 581 yd2 |
| 5 | Driver +32 | Driver +30 | 2.5 |  | erase native 570 yd2; erase native 559 yd2; add recovery 49 yd2; add recovery 49 yd2; add recovery 49 yd2; add recovery 49 yd2; add recovery 49 yd2 |
| 6 | Driver -25 | Driver -25 | 0.0 |  | checked, no change |
| 8 | 4-wood -5 (tie) | 4-wood -5 (tie) | 0.0 |  | erase native 238 yd2 |
| 9 | Driver +28 | Driver +28 | 0.0 |  | erase native 929 yd2; erase native 532 yd2; add recovery 77 yd2; add recovery 77 yd2; add recovery 77 yd2 |
| 10 | 4-wood +10 (tie) | 4-wood +10 (tie) | 0.0 |  | add recovery 28 yd2; add recovery 49 yd2 |
| 11 | 4-wood -25 | 4-wood -25 | 0.0 |  | erase native 789 yd2 |
| 12 | Driver +28 | Driver +28 | 0.0 |  | erase native 1691 yd2; add recovery 151 yd2 |
| 13 | Driver +8 | Driver +8 | 0.0 |  | erase native 2015 yd2; add recovery 77 yd2; add recovery 77 yd2; add recovery 77 yd2; add recovery 77 yd2 |
| 14 | 2-wood -30 | 2-wood -30 | 0.0 |  | checked, no change |
| 16 | Driver -22 | Driver -22 | 0.0 |  | checked, no change |
| 18 | Driver +15 (tie) | Driver +15 (tie) | 0.0 |  | add recovery 111 yd2; add recovery 77 yd2 |

0 of 14 tee shots change. Page: add `"agent_layers": "course_data/mapper/annbriar/"` to `course_data/requests/course_page_annbriar.json` (coordinator).
