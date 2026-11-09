# Blind loop: random US courses, one at a time, through the fully automatic pipeline

Started 2026-11-09. Owner: the blind-loop agent. Code: `course_data/platform/blind20/blind20.py`; the fixed list:
`course_data/platform/blind20/blind20.json`. This file was written (list + protocol) before any course was run.

**Headline (updated at every course): 0 of the last 10 random courses usable as is (0 graded so far).**

## Protocol

1. **The draw.** Frame: every open row of the national index (`library/us_courses.json.gz`, the list behind
   `us_readiness.json`): 13,090 courses, tiers A 5,858 / B 413 / C 3,498 / D 3,321. 20 courses,
   allocated to the national tier mix by largest remainder: A 9, B 1, C 5, D 5 (11 of 20 have no
   complete OSM hole lines + greens + tees). Seed 20261109: within each tier the rows (sorted by state, name, OSM id)
   are shuffled with `random.Random(seed)` and taken in order; the 20 are then shuffled with `seed + 1` to give the loop
   order, so any window of the loop is near the national mix. Nothing is filtered by hand: disc-golf rows, driving
   ranges, Alaska / Hawaii stay in the frame (the app's search lists them too).
2. **Excluded** (drawn, then skipped, because the project has seen them): a row whose OSM id appears in the library,
   packages, request files, truth sets, zero_tap selection / benchmark / surveys, structure or osm_check files
   (9,238 ids), or that lies within 2 km of a known course centre (10,227 centres), or whose slug is a folder
   in any of those sets. Skipped this way: Hilton Head National Golf Club (SC, A); Spring Valley Golf Course (OH, A); Triggs Memorial Golf Course (RI, A); Shepherd's Hollow (MI, A); Rock Creek Golf Club (NC, A); Goodrich Country Club (MI, A); Salem Hills Golf Club (MI, A); Executive Golf Course (SD, A); Saddlebrook Golf Course (IN, A); The Captain's Club at Woodfield (MI, B); Malone Golf Club (East Course) (NY, B); Montclair Golf Club (NJ, C); Legends Golf and Resort (SC, C); Goodman Aggie Golf Complex (TX, C); Sycamore Hills Golf Club (MI, C); Woodlands Country Club - Palmer Course (TX, C); Woodlands (FL, C); Meadow Lake Golf Course (KS, D); Citrus Springs Golf & Country Club (FL, D); Polish Pines Country Club Golf Course (WV, D); Errol Estate Golf & Country Club (FL, D); Beverly Park Golf Course (TN, D); Swamp Fox Golf Club (SC, D).
3. **The run.** One course per request, exactly what the app's "Request this course" + `requests_to_batch.py` write:
   name, city, state, the index row's OSM id and centre (`near`). No tee sets, no card, no fixes. `group: "gate"` so
   the page goes to `course_data/library/gate/gate_b20_<slug>/` and never into `index.json` or the app (the only
   difference from a golfer's request). Workflow: `.github/workflows/course_page.yml` (package -> 4 compute cells ->
   finish). Every fetch stage (resolve, OSM, card, NAIP, 3DEP / lidar, Sentinel-2, weather) needs Actions: the session
   container reaches none of those hosts. Offline stages (package build from fetched raw files, tests) run locally.
4. **Grading** (the grader is an independent checker: it reads the built page, not the pipeline's own QA verdict).
   Per hole, on the page's own imagery with the tee, green, hole line, zones and the pick drawn
   (`blind20.py sheets`, looked at hole by hole), plus the scorecard where one exists:
   * right hole: the tee and the green are on the real hole N (a real tee box at the tee, a real putting surface at
     the green, a playable corridor between them, card par / yardage consistent, the green-to-next-tee walk sane);
   * tee: the default set's tee within ~10 yds of a real box and of the card length;
   * hazards that matter (water, trees, OB, sand in play of the tee shot) present on the map;
   * the club and aim are sensible for that picture.
   Per course: **usable as is** (every hole right; a golfer could play it without touching anything) /
   **usable with 1-3 confirms** (at most 3 holes need a tap, and the page flags those holes itself) /
   **wrong** (more than 3 holes wrong, or any wrong hole the page does not flag) / **failed** (no page; includes
   blocked / unsupported / "not ready"), with the stage that failed and the cause. A row that is not a golf course
   (disc golf, a range) is graded "not a course": correct behaviour is a clear refusal, a built page is wrong.
   Limits of the grading, stated once: hole *numbers* on courses with no OSM hole lines can only be checked against
   the card (length, par) and the walk order, not against a sign on the ground; the pick is judged for sense, not
   re-solved.
5. **After a failed / wrong course:** root cause, a general fix in the pipeline with a test (no per-course data),
   then that course and every earlier course of the loop are re-run. Routing / numbering of unmapped courses and tees /
   long grass / ensemble on mapped courses belong to two other agents: those cases are recorded below as regression
   examples, not fixed here.
6. **Re-scoring later:** `python3 course_data/platform/blind20/blind20.py rerun done` bumps `rev` in the request files
   of every course run so far; commit + push those files = one course-page run. The list never changes.

## The list (loop order)

| # | tier | course | town | OSM | index: holes / OSM hole lines / greens / tees | card | slug |
|---|---|---|---|---|---|---|---|
| 1 | A | Crow Canyon Country Club | San Ramon, CA | relation/3132092 | 18 / 18 / 19 / 46 | oga | `b20_crow_canyon` |
| 2 | D | Sunset Golf Course | Mount Morris, IL | way/295902652 | 0 / 0 / 0 / 0 | oga | `b20_sunset` |
| 3 | A | Pheasant Ridge Golf Course | Cedar Falls, IA | way/200218531 | 18 / 18 / 19 / 38 | oga | `b20_pheasant_ridge` |
| 4 | D | Glenwild Golf Club & Spa | Park City, UT | way/266954189 | 0 / 0 / 0 / 0 | oga | `b20_glenwild_spa` |
| 5 | C | Candler Park Golf Course | Decatur, GA | way/34772875 | 9 / 0 / 8 / 8 | oga | `b20_candler_park` |
| 6 | A | Chevy Chase Golf Club | Wheeling, IL | way/164468765 | 18 / 18 / 19 / 66 | oga | `b20_chevy_chase` |
| 7 | A | Cedar Glen Golf Course | Saugus, MA | way/29831267 | 9 / 9 / 10 / 18 | oga | `b20_cedar_glen` |
| 8 | A | The Kittansett Club | Marion, MA | way/29697009 | 18 / 18 / 23 / 64 | oga | `b20_kittansett` |
| 9 | D | Makena North Course | Wailea, HI | relation/4683724 | 0 / 0 / 0 / 0 | oga | `b20_makena_north` |
| 10 | C | Down River Golf Course | Everett, PA | way/469532052 | 18 / 17 / 17 / 41 | oga | `b20_down_river` |
| 11 | C | Royal Scot Golf Course | New Franken, WI | way/292010201 | 18 / 0 / 19 / 48 | oga | `b20_royal_scot` |
| 12 | A | Zintel Creek Golf Club | Kennewick, WA | way/27183423 | 18 / 18 / 21 / 36 | oga | `b20_zintel_creek` |
| 13 | D | Hawk's Point Golf Course | Vidalia, GA | way/549577968 | 0 / 0 / 0 / 0 | oga | `b20_hawks_point` |
| 14 | A | The Golf Club at Cedar Creek | Onalaska, WI | way/87493616 | 18 / 18 / 18 / 55 | oga | `b20_at_cedar_creek` |
| 15 | A | Falls Village Golf Club | Durham, NC | way/643124259 | 18 / 18 / 20 / 70 | oga | `b20_falls_village` |
| 16 | C | Brookhaven Country Club | Brookhaven, MS | way/1428337532 | 18 / 18 / 0 / 0 | oga | `b20_brookhaven` |
| 17 | C | The Heights Golf Club San Diego | San Diego, CA | way/44501324 | 9 / 5 / 3 / 12 | - | `b20_heights_san_diego` |
| 18 | D | Remsen Golf Course | Remsen, IA | way/296975110 | 0 / 0 / 0 / 0 | oga | `b20_remsen` |
| 19 | A | Maplewood Golf Course | Renton, WA | relation/420415 | 18 / 18 / 20 / 44 | oga | `b20_maplewood` |
| 20 | B | Twisted Pine Golf Course | Hazlehurst, GA | way/1188531225 | 9 / 9 / 10 / 21 | oga? | `b20_twisted_pine` |

## Scoreboard

| # | course | tier | verdict before | cause (stage) | fix commit | verdict after |
|---|---|---|---|---|---|---|

## Time per course by stage (Actions, runner-minutes)

| # | course | package | wind x2 | decide x2 | finish | total | wall |
|---|---|---|---|---|---|---|---|

## For the routing agent (unmapped courses: pairing, numbering)

(none yet)

## For the accuracy agent (mapped courses: tees, long grass, ensemble)

(none yet)

## Fix log

(none yet)
