# Blind loop: random US courses, one at a time, through the fully automatic pipeline

Started 2026-11-09. Owner: the blind-loop agent. Code: `course_data/platform/blind20/blind20.py`; the fixed list:
`course_data/platform/blind20/blind20.json`. This file was written (list + protocol) before any course was run.

**Headline (updated at every course): after 13 courses - 3 usable as is, 3 usable with 1-3 flagged confirms, 1 usable without a card, 6 not shown (4 unmapped tier D, 2 tier C), 0 shown wrong. Tier A 6 / 6 usable; tier C 1 / 3 (Royal Scot, by joint routing); tier D 0 / 4.**

**Change of method, 2026-11-09 evening (manager / Will):** the 1-hour Actions course-page path is no longer used.
Courses are built by the local fast path, one command, about 30 s cold: `python3 course_data/platform/fastpath/fast.py
"Name, City, ST"` (resolve from the national index + OSM API, card, NAIP + 3DEP, Meta canopy trees, the unchanged
`platform/package.py` build, quick solve). Raw fetches are cached in `fastpath/cache/` (not committed), so a re-run
after an algorithm change takes ~15 s. Grading is from ONE contact sheet per course
(`blind20_sheets.py --contact`, 0.6 s), zooming (`--out`, full sheets) only into holes that look wrong. Strictly one
course at a time: build, grade, fix generally + test, re-run this and every earlier course, next course.

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
| 1 | Crow Canyon CC, San Ramon CA | A | **wrong**: map right on 18 / 18 holes (card vs measured within 5 yds on 17), but Mid iron on 9 of 13 tee shots and hole 16's back tee on a house roof | (a) geometry: a `landuse=residential` area drawn round the whole subdivision made every yard of rough OB (S3 build_holes); (b) tees: 68 of 104 lidar "pads" were roofs / house lots outside the course (S2 lidar pads) | this commit | **usable as is**: 4-wood / 2-wood / Driver / Long iron picks that fit the corridors, 16 on its box (175 vs card 180), OB = the real property lines, trees from Meta canopy |
| 2 | Sunset GC, Mount Morris IL | D | **failed: blocked, routing** (105 s, 3 s cached; the Actions run failed the same way after 26 min) | package: OSM maps 0 holes / 0 greens / 0 tees and the fast path builds no perception scene (greens / tees from imagery), so there is nothing to route. Side fix: NAIP year scoring took 88 s with no OSM turf to score on -> newest covering year, newest 4 years only | open (the unmapped-course cause; revisit after 5 courses) | blocked |
| 3 | Pheasant Ridge GC, Cedar Falls IA | A | **usable, no card** (47 s cold, 8 s cached): 18 / 18 holes on the real holes, pars 72, tees on the mapped back boxes, Driver / 4-wood picks that follow the doglegs; but ONE tee set ("back, from the map") and no card yardage | card: OpenGolfAPI lists only the facility's par-27 nine (rightly rejected), golfify has no page, AllSquare / BlueGolf / GolfPass / the club site are not reachable from this container (proxy), and their retries held the build 36 s -> the card search now gets a 15 s budget and never holds the build | this commit (budget); hosts asked | usable, no card |
| 4 | Glenwild GC & Spa, Park City UT | D | **failed: blocked, routing** (29 s) | same as 2: OSM has only the outline | open | blocked |
| 5 | Candler Park GC, Decatur GA (9 holes) | C | **wrong** (20 s): 7 of 9 holes built (1 and 8 missing); 4 plays across a road and houses, 6 across another fairway; the card yardages "match" because the tees were slid to fit | routing: OSM maps 8 greens + 8 tees and no hole lines; routing v2 + structure paired them wrongly. Not fixed here (bigger than 10 min). Guard added: the course-page publish gate now runs in the fast path -> "7 holes built, the card has 9" | this commit (gate) | **blocked (not shown)** |
| 6 | Chevy Chase GC, Wheeling IL | A | **usable as is** (32 s incl. a late card; 11 s cached): 18 / 18 holes right, OpenGolfAPI card, every measured yardage within 6 of the card, 4 sets, water / OB / trees on the map, Driver / 4-wood / Long iron picks land on fairway (15: Driver +40 round the dog-leg; 9's back tee is a lidar pad at the card yardage) | - | - | usable as is |
| 7 | Cedar Glen GC, Saugus MA (9 holes) | A | **usable with 1 confirm** (31 s; 6 s cached): 9 / 9 holes right, OpenGolfAPI card, 8 yardages within 1 yd; hole 5 measures 265 against a card 350 (the hole on the ground is the 265; the sheet flags it in orange); 4-wood / Driver picks fit the tree-lined corridors | card: one hole's card yardage does not fit the map (OpenGolfAPI) | not fixed (flagged) | usable with 1 confirm |
| 8 | The Kittansett Club, Marion MA | A | **usable with 1 confirm** (64 s cold: year scoring 37 s; 17 s cached): 18 / 18 holes right, golfify card, yardages within 4; hole 10's back tee was a lidar pad 62 yds to the side of the mapped boxes that happened to give the card 352; marsh / beach / OB mapped; picks sensible (4: Driver +40 across the corner of a dog-leg: confirm the line) | tees: a lidar pad far from every mapped box taken for the card yardage; time: year scoring at 1.2 m | this commit: pads must be within 40 yds of a mapped box or behind the hole's first leg (when OSM maps >= 9 boxes); year scoring reads at 2.4 m | **usable as is** apart from the wide aim on 4 (10: tee_axis 347 vs card 352) |
| 9 | Makena North, Wailea HI | D | **failed: blocked, routing** (25 s) | same as 2 and 4: outline only (and no NAIP in Hawaii) | open | blocked |
| 10 | Down River GC, Everett PA | C | **wrong** (58 s; build 36 s, the router): 17 OSM hole lines + 1 routed hole; hole 12 was routed onto hole 1's green; the golfify card is 50-125 yds longer than the map on 9 / 10 / 11 and the tee stage "fitted" it by putting those tees on other holes' boxes (4, 12, 3) | tees: another hole's box borrowed to fit the card; routing: the missing hole put on a used green; card: does not fit the map | this commit: (a) sanity.guard_tees - a tee > 60 yds from its hole's start and nearer another hole's start goes back to the line start, flagged (test); (b) fast-path gate - two holes sharing a green, or the card off by > 25 yds on >= 3 holes -> blocked (test) | **blocked (not shown)**: "holes 1 and 12 share a green; the card does not fit the map on 3 holes" |
| 11 | Royal Scot GC, New Franken WI | C | **blocked (not shown)** (64 s; router 39 s): OSM has 19 greens + 48 tees and no hole lines; the old router built 17 of 18 holes, pars 67 vs 72 | routing (half-mapped, no lines) | joint routing wired into the fast path (`fastpath/route_joint.py`: zero_tap/joint on the OSM polygons with tee_reuse, dog-leg hole lines through the fairway centreline, gate min margin >= 4) | **usable with 2 flagged confirms** (15 s cached; routing 2 s): 18 / 18 holes run tee -> fairway -> green by eye, every card yardage within 5 yds, min margin 4.3; wide dog-leg aims on 3 and 10 carry the confirm flag |
| 12 | Zintel Creek GC, Kennewick WA | A | **usable with 3 confirms, all flagged** (25 s; 11 s cached): 18 / 18 holes right; the OpenGolfAPI card arrived after the 15 s budget and the first answer was built without it (bug: the late-card flag was overwritten, so no second-phase rebuild); with the card: 3 sets, yardages within 10 on 17 holes (18: card 455 vs 417), two dog-leg picks more than 40 yds off the line (5, 12) carry the "confirm the line" flag | fast path: late card not picked up | 9a2 (this commit): late card always triggers the rebuild | usable with 3 confirms |
| 13 | Hawk's Point GC, Vidalia GA | D | **failed: blocked, routing** (8 s) | outline only | open | blocked |

## Time per course by stage (Actions, runner-minutes)

Crow Canyon CC (tier A, 18 holes, 1,363 OSM features), the same course both ways:

| stage | Actions course-page (run 42698761601) | local fast path, cold | what changed |
|---|---|---|---|
| runner set-up (disk, 5 GB checkout, pip) | 4.5 min | 0 | one process, no runner |
| resolve + OSM | 18.8 min (every Overpass mirror failed for 8.6 min, then a 1.3 GB Geofabrik California download 7.7 min + cut 1.2 min) | 0.8 s + 1.8 s | national index + OSM API (`<type>/<id>/full`, `map?bbox=`) |
| scorecard | 18 s | 4.6 s (in parallel with imagery) | same code |
| NAIP + 3DEP DEM | 24 s | 16.7 s (list 2.4, year scoring 8.5, read 3.8, write 1.9; DEM 1.5) | years scored in parallel, strip reads by threads; same year, same grid |
| package build (tees, geometry, elevation) | 9 s + 72 s rebuild | 9.5 s (lidar tee pads 5, elevation 3) | same code, built once |
| trees | 6.0 min (lidar point clouds, PDAL, multi-year NAIP, LightGBM) | 1.9 s fetch + 1.1 s (Meta 1 m canopy height, one COG window) | accuracy cost: see the time-vs-accuracy table |
| S2 native stack / native questions | 49 s / 86 s | not run | |
| strategy solve | 4 compute jobs (wind grids + 48-draw decide), still running after 60 min | 3.2 s (decide quick, n 2000, 4 processes, lie raster) | calm-day pick only; no wind grids |
| **total** | **32.8 min package job + compute + finish (> 1 h wall)** | **about 31 s cold, 15 s with the fetch cache** | |

First local end-to-end was 58.6 s (imagery fetched by the stock script: 42.7 s); 34.7 s after the parallel imagery
fetch; the lie raster cut the solve from 12.7 s to 3.2 s with trees on the map (EVs within 0.001 strokes).

Held-out accuracy check (`fastpath/evalfast.py`: error_budget.score_course, auto vs truth, 24 card truth courses, 331
tee shots, n 4000): committed packages with the shipped native band stripped = 234 / 331 match (70.7 %), regret 8.51 =
0.36 strokes / 14-shot round. Wall: 10.2 min cold with polygon lie tests; the lie raster and the decision cache make
a re-score a few minutes (number below when measured).

| # | course | package | wind x2 | decide x2 | finish | total | wall |
|---|---|---|---|---|---|---|---|
| 2 | Sunset, Mount Morris IL (Actions, queued before the method change; not graded) | 16.2 min | 2.6 + 4.9 min | 2.8 + 2.9 min | 3.3 min | 32.7 runner-min | 26 min |

## For the routing agent (unmapped courses: pairing, numbering)

(none yet)

### Half-mapped courses, second pass (same evening): the tee-complex constraint was the wall

The joint solver let each linked tee complex serve one hole; 95 of 106 dev courses have a complex that serves two
(adjacent tees). With `tee_reuse` (zero_tap/joint/solve.py, params.json osm_card), OSM polygons + web card, 18-hole
courses, K 18, beam 4000:

| split | courses | holes fully right | greens numbered right | courses: every green numbered right | gate min margin >= 4: shown / right |
|---|---|---|---|---|---|
| dev, before | 106 | 76.0 % | 81.2 % | 45 (42 %) | about half right |
| dev, tee_reuse | 106 | 81.7 % | 86.4 % | 59 (56 %) | 19 / 16 |
| test, tee_reuse (read once) | 104 | 86.5 % | 90.4 % | 62 (60 %) | 28 / 27 (>= 3: 35 / 34; >= 6: 11 / 11) |

Not helped (17-course dev sample): hard exclusion of pairs crossing an OSM road / building (+0.3 pt of holes), a
fairway-ends rule (-1.3 pt): the hole model already reads the fairway polygons; pairs were 85.6 % right before any of
this. What is left is order / numbering.

Vision check by eye, blind, 5 dev courses, one contact sheet each of the solver's proposal (11-20 s to render incl.
the NAIP fetch, about 40 s of looking): per-hole "is this a real tee -> green corridor" against the true pairs:
precision 84 % (53 / 63), recall 90 %, 68 % of the wrong pairs caught (21 / 31). It separates hopeless routings (5 and
11 of 18 judged ok; truth 1 and 8 pairs) from near-right ones (17 / 14 / 16 judged ok; truth 17 / 17 / 16) but does not
see numbering and missed the one wrong hole of a 17 / 18 course: a coarse gate, not a zero-wrong gate.

In the fast path a joint-routed course is shown only with min margin >= 4, no virtual hole, and the existing gates
(hole count, shared green, card misfit on >= 3 holes); Royal Scot (blind 11) is the first such course shown: all 18
card yardages within 5 yds of the routed dog-leg lengths. Candler Park (8 greens for 9 holes, margin 0) stays blocked.

### Half-mapped courses (OSM greens + tees, no hole lines): first pass, before the tee-complex fix

`zero_tap/joint` (card-aware joint solve) on the OSM green / tee polygons with the hole lines hidden (`prep.py
--source osm`, first run of that source), web card, K 18, beam 4000, 4 CPUs: 0.5 s / course.

| split | courses | holes numbered right | courses with every hole right |
|---|---|---|---|
| dev | 130 | 69.8 % | 21.5 % |
| test (read once) | 125 | 75.3 % | 25.6 % |

No gate found that shows only right courses: the solver's own margin (min / p10 / mean, any threshold) tops out at
about 50 % of shown courses fully right; requiring the joint solve and pathroute to agree on every green and number
shows 41 dev courses, 22 right (test 47 / 20). So half-mapped courses stay **not shown** (the hole-count / shared-green
/ card-misfit gate catches the build); the honest unlock is the golfer confirm (the app's tap flow) with the solver's
per-hole margin choosing the holes to ask, not an automatic "shown correct".

Tier C by what OSM has (share of all 13,090 US courses): every hole line but greens / tees short 5.8 % (routing is
given: the detector fills greens, the line start gives the tee - Brookhaven, blind course 16, is the test); >= 80 %
of the hole lines 3.2 %; no lines but greens + tees complete 5.7 % (the case above); no lines, greens + tees >= 80 %
1.2 %; greens only 2.8 %; sparse 7.9 %. Tier D (outline only) 25.4 %.

Regression guard after the shared-code fixes (land-use OB, pad rules): 13 truth courses rebuilt from their raw data
with today's code, re-scored with the cached truth decisions: 138 / 180 match, regret 3.317 -> 138 / 180, 3.303
(Hot Springs -2, Pine Dunes +2). Neutral. (11 more courses did not finish inside the 15-minute limit: the rebuild of a
truth course with its lidar layers takes about a minute and some hang; `rebuild_truth.py`.)

## For the accuracy agent (mapped courses: tees, long grass, ensemble)

(none yet)

## Fix log

1. **Land-use OB inside the course** (`geometry/build_holes.py`, test `geometry/test_landuse_ob.py`). A
   `landuse=residential / commercial / industrial / retail` polygon is now clipped by the `leisure=golf_course`
   outline before it becomes OB; buildings, roads and `golf=out_of_bounds` are untouched. Crow Canyon: Mid iron on 9
   of 13 tee shots -> none. Open: a course with no outline (tier D) inside a residential land-use area still gets it.
2. **Lidar tee pads on roofs** (`platform/package.py pads_on_course`, test `platform/test_pads_on_course.py`). A lidar
   pad on an OSM building, or more than 20 yds outside every course outline, is not a tee candidate. Crow Canyon: 68
   of 104 pads dropped; hole 16's back tee moved from a house onto its box.
3. **OSM transport** (`fastpath/osm_api.py`): the OSM API instead of Overpass / Geofabrik (seconds instead of 19 min on
   Actions for this course; the Overpass mirrors and Geofabrik do not answer from the session container at all).
5. **Publish gate in the fast path** (`fastpath/fast.py`): `library/course_page.publish_gate` (hole count vs card,
   pars, routing walks) -> status blocked, never shown. Candler Park: 7 of 9 holes.
6. **Lidar pads far from the mapped boxes** (`package.py pads_on_course`, test added): Kittansett 10.
7. **Card search budget** (15 s; a late card is cached and the course rebuilt: two-phase) and **year scoring** (newest
   4 covering years, 2.4 m reads; newest year when OSM has no turf).
4. **Lie raster** (`fastpath/solve.py raster_lie_at`): the solve's lie lookup from a label raster of the hole's zone
   stack; 4x faster on a tree-heavy map, same picks except exact ties.
