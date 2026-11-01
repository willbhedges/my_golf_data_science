# Card-blind scoreboard: no scorecard -> how close is the tee-shot plan?

The question: a golfer names a US course and nothing else. No card from the web, no typed card, no review fixes.
How close is the plan (club + aim on every tee shot, back set and 2nd set) to the plan built with the true card
or the hand truth?

## How `"card": "none"` works (`platform/package.py`, new, isolated)

* A package request with `"card": "none"` (also `"blind"` / `"cardless"`) goes through `strip_card_inputs`. That
  drops `yardages`, `pars`, `scorecard`, `typed_card`, `yardage_overrides`, `par_overrides`, `tee_set`, `tees`, and
  the local card lookup. `pick_scorecard` is never called, so `raw/scorecard_web.json` is never read.
* **Before routing**, `cardless_card` builds the fallback card, `cardless_fallback`: the OSM hole lines only. Back set =
  hole-line length. `Second` = back x `CARDLESS_SET2_RATIO` (0.94). Par = the OSM `par` tag (3-6), else from
  length (<250 par 3, <480 par 4, else 5). This card drives the routing stage, so routing is the same with and
  without `tees/cardless.py`. If a teammate module defines one of `synthetic_card` / `cardless_card` /
  `build_card` / `make_card` / `card`, that function is used here instead.
* **After routing, renumbering and green overrides**, `cardless_infer` calls `tees/cardless.infer_card(holes, tees,
  pads)` on every routed hole line. It replaces the fallback card with that card's sets (`Back`, `2nd`, ...) and
  pars, mapped back onto the hole numbers (None for unrouted holes), and re-picks the longest set. The inputs come
  from `cardless_inputs`, built the way `tees/eval_cardless.course_inputs` builds them:
  * holes `{ref, line (lat, lon) tee->green, green centre, green_r_yd}`. The green centre and equal-area radius come
    from the OSM green within 40 yds of the line end; otherwise the line end is used.
  * OSM tee boxes, via `package.osm_tee_inputs`.
  * lidar pads from the package DEM, via `package.lidar_pads`, the same call the tee stage makes.
  On any error the fallback card stays and a warning names the reason. Request `"cardless": "fallback"` forces the
  fallback card (the "before" arm).
* After that the build runs as normal: the tee localizer v2 on the synthetic yardages, then geometry and zones.
  `package.scorecard.kind == "cardless"`.
* Default behaviour, with no `card` key in the request, is unchanged. Tests: `platform/test_cardblind.py` (helpers),
  `geometry/test_build_holes_multipolygon.py` (the tomahawk crash). The platform, tees and geometry suites pass
  (168 passed, 6 skipped).

## The harness (`platform/cardblind_eval.py`)

```
python3 course_data/platform/cardblind_eval.py --out-dir /tmp/cb --n 1000            # all courses
python3 course_data/platform/cardblind_eval.py --out-dir /tmp/cb --courses blue_hills  # one course
# parallel: one shard per process, then merge (and rewrite the table below)
python3 course_data/platform/cardblind_eval.py --out-dir /tmp/cb --json /tmp/a.json --courses a,b &
python3 course_data/platform/cardblind_eval.py --merge /tmp/a.json /tmp/b.json --md
```

It works offline, from the committed raw OSM. Each course is built twice in a child process: **ref** with the true
card (the hand-truth package `courses/<slug>/truth/package.json` where one exists, else a normal build: web card +
the request's review overrides), and **blind** (`card: none`, minus `tee_overrides` / `hole_renumber` /
`green_overrides`). Both go through `product/package.load` -> `product/decide.run(mode="quick")` for the back set
(the longest on each package's card) and the 2nd set (the second longest). Per hole, using ref numbering:

| metric | definition |
|---|---|
| routing right | the blind hole with that number has its green within 20 yds and the set's tee within 40 yds of ref (as `routing.score`) |
| par right | blind par == ref par |
| tee err | yds between the two tees for that set rank |
| same club | blind tee club == ref tee club, on the par 4/5 holes the ref plans (a blind par 3 there = "no plan") |
| aim diff | the blind aim point (its carry on its own tee line + its aim), seen from the ref tee and re-expressed as an aim at that club's carry on the ref tee line, minus the ref aim |
| regret | EV on the ref geometry of (blind club, transferred aim) - EV of the ref plan, in strokes (common random numbers, quick-model prior means) |
| **headline** | **same club and aim diff <= 10 yds** |

Re-run it after improving `tees/cardless.py` or the routing. Nothing in the harness needs editing.

## Routing: pathroute_v2 for card:none (2026-11-01, n = 1000)

`"card": "none"` now routes the holes OSM has no way for with **zero_tap/pathroute_v2** (`stage_select` method
`pathroute_v2`, `zero_tap/pathroute_v2/live2.py`; PATHROUTE.md). OSM golf=hole ways are fixed as confirmed pairs,
so pathroute fills only the missing holes and numbers them around the mapped ones. It is also the default for the
`mapped_nocard` tier (no card at all). Fallbacks: structure > routing v2 > geometry. Per-hole pair confidence is
in each routed hole (`package.holes[].routing.confidence`, status `check` below 0.95) and the ask order + golfer
facts are in `routing.json["confirm"]` (`pathroute_confirm/1`; re-solve with `live2.route(..., fix=facts)`).
Request `"pathroute": false` restores the old routing. Re-run for the four courses where routing failed, same code
and same `tees/cardless.py` (v2, hybrid) in both arms. Before = `CARDBLIND_REQ='{"pathroute": false}'`:
`cardblind_eval_pathroute_before.json`, after: `cardblind_eval_pathroute_after.json`:

| course | set | same club + aim <=10 (before -> after) | tee err med yds | tee <=10 yds | par right | regret / tee shot |
|---|---|---|---|---|---|---|
| hot_springs_park | back | 0/7 -> **1/7** | 478.7 -> 367.6 | 0 -> 0 / 9 | 1 -> 5 / 11 | 0.5 -> 0.231 |
| hot_springs_park | second | 0/7 -> **1/7** | 463.1 -> 340.5 | 0 -> 0 / 9 | 1 -> 5 / 11 | 1.143 -> 0.294 |
| jayhawk_club | back | 1/6 -> **2/7** | 457.0 -> 143.1 | 0 -> 0 / 9 | 4 -> 3 / 10 | 0.269 -> 0.823 |
| jayhawk_club | second | 1/6 -> **2/7** | 452.9 -> 138.4 | 0 -> 0 / 9 | 4 -> 3 / 10 | 0.156 -> 0.46 |
| national_kc | back | 1/7 -> **4/7** | 798.7 -> 3.0 | 1 -> 5 / 9 | 3 -> 9 / 18 | 0.91 -> 0.337 |
| national_kc | second | 1/7 -> **4/7** | 762.1 -> 5.0 | 1 -> 6 / 9 | 3 -> 9 / 18 | 1.004 -> 0.034 |
| tomahawk_hills | back | 0/12 -> **10/12** | 906.4 -> 5.0 | 0 -> 13 / 18 | 7 -> 18 / 18 | 2.356 -> 0.024 |
| tomahawk_hills | second | 1/12 -> **10/12** | 905.2 -> 5.5 | 0 -> 13 / 18 | 7 -> 18 / 18 | 1.64 -> 0.01 |
| **OSM maps few / no holes** (4 courses, both scored) | **back** | 2/32 -> **17/33** | 603.4 -> 28.8 | 1 -> 18 / 45 | 15 -> 35 / 57 | 1.264 -> 0.289 |
| **OSM maps few / no holes** (4 courses, both scored) | **second** | 3/32 -> **17/33** | 602.4 -> 22.1 | 1 -> 19 / 45 | 15 -> 35 / 57 | 1.112 -> 0.158 |

After, failure causes, back set: routing (wrong green) 9; routing / tee >40 yds off 4; tee position >15 yds 2; club flip on a ref tie 1

After, failure causes, second set: routing (wrong green) 9; routing / tee >40 yds off 4; aim >10 yds (same club) 1; tee position >15 yds 1; club flip (geometry ~same) 1

Headline on these four courses: same club + aim within 10 yds goes from **2/32 to 17/33 (back)** and **3/32 to 17/33
(2nd)**. Regret per tee shot drops from 1.26 to 0.29 (back) and from 1.11 to 0.16 (2nd). The previous published
"after" for these courses (cardless v1, old routing) was 10/32 back and 9/32 2nd. tomahawk_hills (0 -> 10/12) and
national_kc (1 -> 4/7, back tee median 799 -> 3 yds) gain most. hot_springs_park stays bounded: OSM has fewer than 13
greens, so the hole count guess is 9 of the true 18, and the ref is itself routed (structure with the card), so
"routing right" there is against a routed ref. Remaining misses are mostly wrong greens (9 of 16 back-set misses).
The 13 fully mapped courses are not affected: routing is not needed there.

## Headline: before (fallback card) -> after (`tees/cardless.py`), n = 1000 quick decisions per plan, 2026-11-01

Tee shots where the card-blind plan has **the same club and an aim within 10 yds** of the true-card plan. The same
17 courses are scored in both arms, now including tomahawk_hills (its crash is fixed: see below).

| courses | back set | 2nd set | back tee err median | regret per tee shot (back / 2nd) |
|---|---|---|---|---|
| OSM maps every hole (13 courses) | 142/168 (85 %) -> **136/168 (81 %)** | 117/154 (76 %) -> **111/154 (72 %)** | 3.1 -> 4.0 yds | 0.013 / 0.021 -> 0.020 / 0.026 |
| OSM hole ways missing (hot_springs_park, jayhawk_club, national_kc, tomahawk_hills) | 8/32 -> **10/32** | 7/32 -> **9/32** | 266 -> 241 yds | 0.58 / 0.84 -> 0.37 / 0.50 |
| all 17 | 150/200 (75 %) -> **146/200 (73 %)** | 124/186 (67 %) -> **120/186 (65 %)** | 4.0 -> 4.8 yds | 0.095 / 0.148 -> 0.072 / 0.103 |

**`tees/cardless.py` does not beat the hole-line fallback where OSM maps every hole.** There the OSM hole line
already starts at the back box: the back tee is a median 3.1 yds off and par is right on 217/219 holes.
infer_card's "0.9 of the way back in the farthest box" rule is worse on two counts:
* On a few holes it takes a box 40-125 yds behind the real back tee, so the back length comes out +36 to +111 yds:
  hot_springs_arlington 5 and 10, pine_dunes 18, spirit_hollow 4, veenker 18. That is probably another hole's box
  assigned to this hole by `place_tee.assign_tees_to_holes`. These moved "routing / tee > 40 yds off" back-set
  misses from 14 to 19.
* Its 2nd set does not beat 0.94 x back either: 102 -> 97 holes within 10 yds. hot_springs_arlington 2nd 11 -> 6/14
  and veenker 2nd 9 -> 7/13 are the drops; gateway, coldwater, finkbine and wakonda 2nd sets improve by one each.

Where the hole ways are missing, infer_card helps a little: 8 -> 10 back and 7 -> 9 2nd, with regret down a third.
tomahawk_hills goes from 6/12 to 8/12 on the back set: the fallback has no hole lines there, so it falls back to no
card. Those courses are still bounded by routing (wrong green).

Suggested next step, for the owner of `tees/cardless.py`: on a hole with an OSM hole way, do not let Back stand
more than about 25 yds behind the way's start unless a box is assigned to that hole alone. Or simply prefer the
line length as B there. That would keep the fallback's back set and use infer_card for the other sets and par.

## Results (after: `tees/cardless.py`; the before rows are in `cardblind_eval_fallback.json`)

<!-- cardblind_eval:begin -->
| course | set (ref / blind) | ref | routing right | par right | back-tee err med (<=10 yds) | |len err| med | same club | same or ref tie | same club + aim <=10 | no plan | aim diff med (same club) | regret / tee shot |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| blue_hills | back: Black / Back | hand | 18/18 | 18/18 | 1.1 (16/18) | 3.0 | 10/14 | 13/14 | **10/14** | 0 | 1.2 | 0.007 |
| blue_hills | second: Blue / 2nd | hand | 18/18 | 18/18 | 9.8 (9/18) | 11.5 | 10/14 | 10/14 | **9/14** | 0 | 2.2 | 0.038 |
| coldwater | back: Black / Back | card | 17/18 | 17/18 | 2.0 (15/18) | 2.0 | 13/14 | 13/14 | **13/14** | 0 | 0.0 | 0.002 |
| coldwater | second: Blue / 2nd | card | 18/18 | 17/18 | 4.5 (13/18) | 5.5 | 13/14 | 13/14 | **13/14** | 0 | 2.2 | 0.003 |
| eagle_knoll | back: Eagle / Back | hand | 18/18 | 18/18 | 1.9 (15/18) | 4.0 | 12/14 | 13/14 | **12/14** | 0 | 1.9 | 0.007 |
| eagle_knoll | second: Back / 2nd | hand | 18/18 | 18/18 | 14.2 (7/18) | 12.5 | 11/14 | 12/14 | **10/14** | 0 | 2.5 | 0.034 |
| ellis | back: Blue / Back | card | 18/18 | 18/18 | 4.0 (14/18) | 4.0 | 14/14 | 14/14 | **14/14** | 0 | 0.6 | 0.003 |
| ellis | second: White / 2nd | card | 18/18 | 18/18 | 4.0 (15/18) | 4.0 | 12/14 | 13/14 | **11/14** | 0 | 0.2 | 0.007 |
| gateway_national | back: The Tips / Back | card | 16/18 | 17/18 | 1.7 (15/18) | 2.0 | 12/13 | 12/13 | **12/13** | 0 | 0.1 | 0.054 |
| gateway_national | second: Champions / 2nd | card | 17/18 | 17/18 | 23.4 (5/18) | 21.5 | 10/13 | 12/13 | **7/13** | 0 | 7.2 | 0.063 |
| creekmoor (review-OK holes) | back: Black / Back | card | 9/9 | 9/9 | 2.0 (9/9) | 4.0 | 7/7 | 7/7 | **7/7** | 0 | 0.1 | 0.0 |
| creekmoor (review-OK holes) | second: Green / 2nd | card | 9/9 | 9/9 | 7.8 (7/9) | 8.0 | 7/7 | 7/7 | **7/7** | 0 | 0.6 | 0.0 |
| hot_springs_arlington | back: Gold / Back | card | 14/18 | 18/18 | 3.0 (13/18) | 3.5 | 12/14 | 12/14 | **10/14** | 0 | 0.4 | 0.025 |
| hot_springs_arlington | second: Blue / 2nd | card | 13/18 | 18/18 | 25.9 (3/18) | 26.0 | 8/14 | 9/14 | **6/14** | 0 | 5.3 | 0.04 |
| hot_springs_park | back: Gold / Back | card | 0/11 | 4/11 | 400.7 (0/9) | 77.0 | 5/7 | 5/7 | **0/7** | 0 | 180.4 | 0.402 |
| hot_springs_park | second: Blue / 2nd | card | 0/11 | 4/11 | 423.0 (0/9) | 82.0 | 5/7 | 5/7 | **0/7** | 0 | 194.0 | 0.45 |
| jayhawk_club | back: Black / Back | card | 1/10 | 3/10 | 349.8 (0/7) | 55.0 | 4/6 | 4/6 | **1/6** | 1 | 83.7 | 0.902 |
| jayhawk_club | second: Green / 2nd | card | 2/10 | 3/10 | 317.8 (0/7) | 52.0 | 3/6 | 3/6 | **2/6** | 1 | 3.2 | 0.456 |
| mozingo_lake | back: App / Back | card | 11/18 | 16/18 | 30.7 (5/18) | 27.5 | 10/14 | 10/14 | **6/14** | 0 | 6.3 | 0.072 |
| national_kc | back: Black / Back | card | 1/18 | 3/18 | 223.4 (2/9) | 167.0 | 3/7 | 3/7 | **1/7** | 0 | 10.4 | 0.464 |
| national_kc | second: Blue / 2nd | card | 1/18 | 3/18 | 255.6 (1/9) | 165.0 | 2/7 | 2/7 | **1/7** | 0 | 854.4 | 1.049 |
| finkbine (review-OK holes) | back: Black / Back | card | 12/12 | 12/12 | 3.5 (11/12) | 3.5 | 9/9 | 9/9 | **9/9** | 0 | 0.6 | 0.0 |
| finkbine (review-OK holes) | second: Gold / 2nd | card | 12/12 | 12/12 | 5.0 (9/12) | 5.0 | 9/9 | 9/9 | **9/9** | 0 | 0.3 | 0.001 |
| oaks_margaritaville | build failed: RuntimeError: ref build failed: ['no holes built (no golf=hole ways and no tee/green pairs | | | | | | | | | | | |
| pine_dunes | back: Gold / Back | card | 17/18 | 18/18 | 6.0 (17/18) | 2.0 | 12/14 | 12/14 | **11/14** | 0 | 2.6 | 0.038 |
| pine_dunes | second: Blue / 2nd | card | 18/18 | 18/18 | 9.2 (9/18) | 10.0 | 12/14 | 13/14 | **11/14** | 0 | 1.4 | 0.035 |
| spirit_hollow | back: Gold / Back | card | 13/18 | 18/18 | 4.0 (12/18) | 8.0 | 10/14 | 12/14 | **8/14** | 0 | 1.0 | 0.017 |
| spirit_hollow | second: Black / 2nd | card | 14/18 | 18/18 | 19.1 (5/18) | 14.0 | 10/14 | 11/14 | **9/14** | 0 | 3.4 | 0.023 |
| tomahawk_hills | back: Blue / Back | card | 9/18 | 10/18 | 17.6 (9/18) | 27.5 | 10/12 | 11/12 | **8/12** | 1 | 2.5 | 0.037 |
| tomahawk_hills | second: White / 2nd | card | 9/18 | 10/18 | 8.0 (10/18) | 29.0 | 8/12 | 8/12 | **6/12** | 1 | 2.5 | 0.206 |
| veenker | back: Blue / Back | card | 16/18 | 17/18 | 4.4 (12/18) | 6.5 | 13/13 | 13/13 | **11/13** | 0 | 3.7 | 0.011 |
| veenker | second: Gold / 2nd | card | 15/18 | 17/18 | 11.5 (9/18) | 11.5 | 8/13 | 8/13 | **7/13** | 0 | 2.1 | 0.04 |
| wakonda | back: Black / Back | card | 16/18 | 18/18 | 4.0 (13/18) | 4.0 | 13/14 | 13/14 | **13/14** | 0 | 0.2 | 0.005 |
| wakonda | second: Blue / 2nd | card | 15/18 | 18/18 | 14.5 (6/18) | 14.0 | 14/14 | 14/14 | **12/14** | 0 | 1.9 | 0.011 |
| sycamore_ridge | build failed: RuntimeError: excluded: the ref build has no card either, so there is no card truth | | | | | | | | | | | |
| **all** | **back** | | 206/276 (75 %) | 234/276 (85 %) | 4.8 (178/262 (68 %)) | 5.0 | 169/200 (84 %) | 176/200 (88 %) | **146/200 (73 %)** | 2 | 2.0 | 0.072 |
| **all** | **second** | | 197/258 (76 %) | 218/258 (84 %) | 14.0 (108/244 (44 %)) | 13.0 | 142/186 (76 %) | 149/186 (80 %) | **120/186 (65 %)** | 2 | 2.3 | 0.103 |

Failure causes, back set (54 tee shots not same club + aim <= 10 yds): routing / tee >40 yds off 19; routing (wrong green) 19; club flip on a ref tie 6; club flip (geometry ~same) 4; tee position >15 yds 3; aim >10 yds (same club) 2; par wrong 1

Failure causes, second set (66 tee shots not same club + aim <= 10 yds): tee position >15 yds 23; routing (wrong green) 19; routing / tee >40 yds off 14; club flip (geometry ~same) 5; club flip on a ref tie 2; aim >10 yds (same club) 2; length >15 yds (same tee area) 1

<!-- cardblind_eval:end -->

### Top failure causes (after; tee shots not same club + aim <= 10)

1. **Routing on courses whose OSM hole ways are missing: 19 + 19 of the 54 back-set misses.** hot_springs_park
   (its OSM hole ways belong to the other course), jayhawk_club (OSM maps 8 of 18), national_kc and tomahawk_hills
   (no hole ways) route the wrong green on most holes. That is teammate (a)'s `zero_tap/pathroute/`. The mapped
   courses' share of "tee > 40 yds off" is Mozingo Lake (the ref "App" set comes from request yardages; the OSM
   line starts at another box) plus the infer_card back-box overshoots listed above.
2. **2nd-set tee position: 23 of the 66 2nd-set misses.** Neither 0.94 x back nor infer_card gets the 2nd box
   right on about half the holes (median 11-14 yds).
3. **Club flips the reference calls a tie: 6 back, 2 2nd.** Margin < 0.01 strokes. That is noise ("same or ref
   tie" column), and n = 1000 adds more.
4. Par: infer_card is right on 214/219 mapped holes (fallback 217). On unmapped courses par follows routing.

## Honest caveats / coverage

* **Covered:** 16 courses with committed raw OSM in `packages/` (two hand-truth references: Blue Hills and Eagle
  Knoll `courses/<slug>/truth/package.json`; the rest have the true web card plus the request's review overrides).
  Also 3 reviewed library courses (creekmoor, finkbine, sycamore_ridge) with a cached OSM snapshot
  (`osm_inventory.json`), scored on review-OK holes. sycamore_ridge is excluded because its reference build has no
  card either.
* **tomahawk_hills crash, fixed.** `geometry/build_holes.World` now keeps the largest part of a multi-part green
  or tee (`largest_polygon`). The crash was a MultiPolygon green from an OSM multipolygon or a buffer(0) bow-tie
  reaching `frame_for` / `.exterior`, not routing. The test is `geometry/test_build_holes_multipolygon.py`, and it
  fails without the fix.
* **Not covered:** oaks_margaritaville (OSM maps nothing; the reference build fails too). colbert_hills / shoal_creek truth
  sets and the 33 other reviewed library courses have no OSM geojson in the repo (library `raw/` keeps only course,
  summary, scorecard_web), so they cannot be built offline. The gate courses (`library/gate`) are the same 7
  courses as `packages/` and are scored there.
* The reference is "the plan with the true card", not ground truth. Where the true-card plan is itself wrong, the
  blind plan is scored against that wrong plan. Only Blue Hills and Eagle Knoll are hand truth.
* Regret uses the quick model's prior means on the reference geometry (the blind club and aim transferred to the
  reference tee). Misses on unmapped courses are "another hole's plan", so their regret is only indicative.
* Imagery and DEM are symlinked where committed (`packages/<slug>/imagery`). The library courses build without
  imagery in both arms.
* Rows and per-hole details: `platform/cardblind_eval.json` (each row carries routed, par, tee_err, len_err, clubs,
  aims, aim_d, regret and the failure cause).

### Per course: before (fallback card) -> after (`tees/cardless.py`)

Regenerate with `cardblind_eval.py --compare cardblind_eval_fallback.json cardblind_eval.json --md`. A before run is
`--cardless fallback`.

<!-- cardblind_compare:begin -->
| course | set | same club + aim <=10 (before -> after) | tee err med yds | tee <=10 yds | par right | regret / tee shot |
|---|---|---|---|---|---|---|
| blue_hills | back | 11/14 -> **10/14** | 2.4 -> 1.1 | 18 -> 16 / 18 | 17 -> 18 / 18 | 0.003 -> 0.007 |
| blue_hills | second | 9/14 -> **9/14** | 10.9 -> 9.8 | 9 -> 9 / 18 | 17 -> 18 / 18 | 0.039 -> 0.038 |
| coldwater | back | 13/14 -> **13/14** | 2.5 -> 2.0 | 14 -> 15 / 18 | 17 -> 17 / 18 | 0.001 -> 0.002 |
| coldwater | second | 12/14 -> **13/14** | 6.0 -> 4.5 | 12 -> 13 / 18 | 17 -> 17 / 18 | 0.002 -> 0.003 |
| eagle_knoll | back | 12/14 -> **12/14** | 3.2 -> 1.9 | 15 -> 15 / 18 | 18 -> 18 / 18 | 0.007 -> 0.007 |
| eagle_knoll | second | 10/14 -> **10/14** | 16.6 -> 14.2 | 8 -> 7 / 18 | 18 -> 18 / 18 | 0.023 -> 0.034 |
| ellis | back | 13/14 -> **14/14** | 3.0 -> 4.0 | 15 -> 14 / 18 | 18 -> 18 / 18 | 0.003 -> 0.003 |
| ellis | second | 12/14 -> **11/14** | 4.7 -> 4.0 | 15 -> 15 / 18 | 18 -> 18 / 18 | 0.006 -> 0.007 |
| gateway_national | back | 12/13 -> **12/13** | 1.9 -> 1.7 | 16 -> 15 / 18 | 18 -> 17 / 18 | 0.053 -> 0.054 |
| gateway_national | second | 6/13 -> **7/13** | 27.1 -> 23.4 | 5 -> 5 / 18 | 18 -> 17 / 18 | 0.062 -> 0.063 |
| creekmoor | back | 7/7 -> **7/7** | 4.0 -> 2.0 | 9 -> 9 / 9 | 9 -> 9 / 9 | 0.0 -> 0.0 |
| creekmoor | second | 7/7 -> **7/7** | 6.0 -> 7.8 | 8 -> 7 / 9 | 9 -> 9 / 9 | 0.001 -> 0.0 |
| hot_springs_arlington | back | 10/14 -> **10/14** | 2.4 -> 3.0 | 16 -> 13 / 18 | 18 -> 18 / 18 | 0.015 -> 0.025 |
| hot_springs_arlington | second | 11/14 -> **6/14** | 16.1 -> 25.9 | 6 -> 3 / 18 | 18 -> 18 / 18 | 0.01 -> 0.04 |
| hot_springs_park | back | 0/7 -> **0/7** | 399.1 -> 400.7 | 0 -> 0 / 9 | 4 -> 4 / 11 | 0.414 -> 0.402 |
| hot_springs_park | second | 0/7 -> **0/7** | 427.9 -> 423.0 | 0 -> 0 / 9 | 4 -> 4 / 11 | 0.457 -> 0.45 |
| jayhawk_club | back | 1/6 -> **1/6** | 347.1 -> 349.8 | 0 -> 0 / 7 | 2 -> 3 / 10 | 0.85 -> 0.902 |
| jayhawk_club | second | 1/6 -> **2/6** | 344.3 -> 317.8 | 0 -> 0 / 7 | 2 -> 3 / 10 | 0.419 -> 0.456 |
| mozingo_lake | back | 7/14 -> **6/14** | 29.8 -> 30.7 | 7 -> 5 / 18 | 18 -> 16 / 18 | 0.044 -> 0.072 |
| national_kc | back | 1/7 -> **1/7** | 305.4 -> 223.4 | 2 -> 2 / 9 | 2 -> 3 / 18 | 1.426 -> 0.464 |
| national_kc | second | 1/7 -> **1/7** | 293.2 -> 255.6 | 2 -> 1 / 9 | 2 -> 3 / 18 | 2.676 -> 1.049 |
| finkbine | back | 9/9 -> **9/9** | 6.0 -> 3.5 | 8 -> 11 / 12 | 12 -> 12 / 12 | 0.002 -> 0.0 |
| finkbine | second | 8/9 -> **9/9** | 9.5 -> 5.0 | 7 -> 9 / 12 | 12 -> 12 / 12 | 0.006 -> 0.001 |
| oaks_margaritaville | - | not scored: RuntimeError: ref build failed: ['no holes built (no golf=hole ways and no tee/green pairs: OSM maps | | | | |
| pine_dunes | back | 14/14 -> **11/14** | 1.8 -> 6.0 | 18 -> 17 / 18 | 18 -> 18 / 18 | 0.001 -> 0.038 |
| pine_dunes | second | 12/14 -> **11/14** | 6.3 -> 9.2 | 12 -> 9 / 18 | 18 -> 18 / 18 | 0.007 -> 0.035 |
| spirit_hollow | back | 10/14 -> **8/14** | 5.7 -> 4.0 | 12 -> 12 / 18 | 18 -> 18 / 18 | 0.02 -> 0.017 |
| spirit_hollow | second | 10/14 -> **9/14** | 19.1 -> 19.1 | 4 -> 5 / 18 | 18 -> 18 / 18 | 0.019 -> 0.023 |
| tomahawk_hills | back | 6/12 -> **8/12** | 79.8 -> 17.6 | 5 -> 9 / 18 | 9 -> 10 / 18 | 0.063 -> 0.037 |
| tomahawk_hills | second | 5/12 -> **6/12** | 42.9 -> 8.0 | 4 -> 10 / 18 | 9 -> 10 / 18 | 0.216 -> 0.206 |
| veenker | back | 11/13 -> **11/13** | 4.6 -> 4.4 | 14 -> 12 / 18 | 18 -> 17 / 18 | 0.011 -> 0.011 |
| veenker | second | 9/13 -> **7/13** | 11.5 -> 11.5 | 9 -> 9 / 18 | 18 -> 17 / 18 | 0.046 -> 0.04 |
| wakonda | back | 13/14 -> **13/14** | 3.5 -> 4.0 | 15 -> 13 / 18 | 18 -> 18 / 18 | 0.004 -> 0.005 |
| wakonda | second | 11/14 -> **12/14** | 11.5 -> 14.5 | 7 -> 6 / 18 | 18 -> 18 / 18 | 0.015 -> 0.011 |
| sycamore_ridge | - | not scored: RuntimeError: excluded: the ref build has no card either, so there is no card truth | | | | |
| **OSM maps every hole** (13 courses, both scored) | **back** | 142/168 -> **136/168** | 3.1 -> 4.0 | 177 -> 167 / 219 | 217 -> 214 / 219 | 0.013 -> 0.02 |
| **OSM maps every hole** (13 courses, both scored) | **second** | 117/154 -> **111/154** | 10.0 -> 11.6 | 102 -> 97 / 201 | 199 -> 198 / 201 | 0.021 -> 0.026 |
| **OSM maps few / no holes** (4 courses, both scored) | **back** | 8/32 -> **10/32** | 265.9 -> 241.1 | 7 -> 11 / 43 | 17 -> 20 / 57 | 0.584 -> 0.366 |
| **OSM maps few / no holes** (4 courses, both scored) | **second** | 7/32 -> **9/32** | 267.8 -> 252.1 | 6 -> 11 / 43 | 17 -> 20 / 57 | 0.84 -> 0.501 |
| **all** (17 courses, both scored) | **back** | 150/200 -> **146/200** | 4.0 -> 4.8 | 184 -> 178 / 262 | 234 -> 234 / 276 | 0.095 -> 0.072 |
| **all** (17 courses, both scored) | **second** | 124/186 -> **120/186** | 14.1 -> 14.0 | 108 -> 108 / 244 | 216 -> 218 / 258 | 0.148 -> 0.103 |

After, failure causes, back set: routing / tee >40 yds off 19; routing (wrong green) 19; club flip on a ref tie 6; club flip (geometry ~same) 4; tee position >15 yds 3; aim >10 yds (same club) 2; par wrong 1

After, failure causes, second set: tee position >15 yds 23; routing (wrong green) 19; routing / tee >40 yds off 14; club flip (geometry ~same) 5; club flip on a ref tie 2; aim >10 yds (same club) 2; length >15 yds (same tee area) 1

<!-- cardblind_compare:end -->
