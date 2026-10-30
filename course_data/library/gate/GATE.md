# Confidence gate vs the hand-checked courses

Built 2026-10-30 16:35Z by `course_data/library/gate_eval.py`. Each course was built blind by the course-page workflow (`course_data/requests/course_page_gate_<slug>.json`: name, town, state, the hand-checked tee set; the same disambiguation the earlier blind requests used) and scored against its hand truth. **match** = every scored tee shot is the same club or a tie, and every hole routed to the right green with the right par where the truth scores routing.

| course | gate status | CHECK holes | reasons | tees | same / same-or-tie | regret | routing / par | match |
|---|---|---|---|---|---|---|---|---|
| blue_hills | needs confirm | 2, 11 | 2 hole(s) with a CHECK | Black | 13/14, 14/14 | 0.001 | 18/18, 18/18 | yes |
| eagle_knoll | needs confirm | 1, 7, 9, 18 | 4 hole(s) with a CHECK | Back | 13/14, 14/14 | 0.012 | 18/18, 18/18 | yes |
| gateway_national | needs confirm | 8, 10, 13 | 3 hole(s) with a CHECK | Back | 11/13, 11/13 | 0.128 | 18/18, 18/18 | no |
| national_kc | needs confirm | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27 | holes not all mapped in OSM (hole method: structure); OSM greens 21 of 27 holes; scorecard not matched (source None, flags []); 27 holes built vs the card's 0; pars sum to 103, card None; 27 hole(s) with a CHECK | Black | 6/9, 6/9 | 0.431 | 2/18, 5/18 | no |
| pine_dunes | failed | - | package: resolve: not_found None None [] gate_pine_dunes: not_found; see packages/gate_pine_dunes/raw/course.json for the candidates  |  | - | None | n/a | error: no package |
| hot_springs_arlington | needs confirm | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18 | scorecard not matched (source None, flags []); 18 holes built vs the card's 0; pars sum to 72, card None; 18 hole(s) with a CHECK | Gold | 12/14, 14/14 | 0.013 | 18/18, 18/18 | yes |
| spirit_hollow | needs confirm | 1, 2, 7, 9, 11, 13, 14, 15, 17, 18 | 10 hole(s) with a CHECK | Black | 12/16, 14/16 | 0.203 | n/a | no |
| mozingo_lake | needs confirm | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18 | scorecard not matched (source None, flags []); 18 holes built vs the card's 0; pars sum to 72, card None; 18 hole(s) with a CHECK | osm_back | 6/12, 7/12 | 0.37 | n/a | no |
| veenker | needs confirm | 3, 5, 7, 8, 10, 12, 15, 16, 18 | 9 hole(s) with a CHECK | Blue | 12/13, 12/13 | 0.011 | n/a | no |
| coldwater | needs confirm | 2, 7, 8, 12, 17 | 5 hole(s) with a CHECK | Blue | 12/14, 13/14 | 0.155 | n/a | no |
| ellis | needs confirm | 2, 6, 10, 13, 17 | 5 hole(s) with a CHECK | Blue | 12/14, 12/14 | 0.124 | n/a | no |

* auto-OK courses: 0; of them match truth: 0
* needs-confirm courses: 10; of them match truth anyway: 3
* tee shots on PASS holes: 77, wrong club (not same or tie) 4; on CHECK holes: 56, wrong 12

* courses with a web card only: PASS holes 77 tee shots, 4 wrong club; CHECK holes 21, 4 wrong. Pine Dunes: no build (Overpass timed out in all three runs).

Wrong tee-shot club (not the same club, not a tie) by failed check, on the scored set:

| check failed | tee shots | wrong club |
|---|---|---|
| (none: PASS) | 77 | 4 (5%) |
| aim | 27 | 3 (11%) |
| oval | 1 | 1 (100%) |
| par | 35 | 8 (23%) |
| tee | 15 | 1 (7%) |
| yardage | 38 | 9 (24%) |

Looser course thresholds (sensitivity, same courses): OSM holes + card matched + page clean, and at most K holes with a CHECK (the CHECK holes are then the golfer's confirm list):

| K | courses passing | of them match truth |
|---|---|---|
| 0 | 0 (-) | 0 |
| 2 | 1 (blue_hills) | 1 |
| 3 | 2 (blue_hills, gateway_national) | 1 |
| 5 | 5 (blue_hills, eagle_knoll, gateway_national, coldwater, ellis) | 2 |

