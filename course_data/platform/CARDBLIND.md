# Card-blind scoreboard: no scorecard -> how close is the tee-shot plan?

The question: a golfer names a US course and nothing else. No card from the web, no typed card, no review fixes.
How close is the plan (club + aim on every tee shot, back set and 2nd set) to the plan built with the true card
or the hand truth?

## How `"card": "none"` works (`platform/package.py`, new, isolated)

* A package request with `"card": "none"` (also `"blind"` / `"cardless"`) goes through `strip_card_inputs`. That
  drops `yardages`, `pars`, `scorecard`, `typed_card`, `yardage_overrides`, `par_overrides`, `tee_set`, `tees`, and
  the local card lookup. `pick_scorecard` is never called, so `raw/scorecard_web.json` is never read.
* `cardless_card(fc, course, raw_dir, req)` builds the synthetic card:
  1. **`tees/cardless.py`, if present** (teammate module). The first function it defines out of
     `synthetic_card`, `cardless_card`, `build_card`, `make_card`, `card` is called with whichever of
     `fc, course, raw_dir, req` it accepts. It must return a `scorecard/1` card (`tee_sets {name: {yards[],
     par[]?}}`, `par[]`) or `(card, info)`. On any error the build falls back to step 2 and records the reason in
     `scorecard.tried`.
  2. **Fallback, `cardless_fallback`**: the OSM hole lines only. Back set = hole-line length. `Second` = back x
     `CARDLESS_SET2_RATIO` (0.94). Par = the OSM `par` tag (3-6), else from length (<250 par 3, <480 par 4,
     else 5).
* After that the build runs as normal: routing for unmapped holes (stage selector, card tier), the tee localizer v2
  on the synthetic yardages, geometry, and zones. `package.scorecard.kind == "cardless"`.
* Default behaviour, with no `card` key in the request, is unchanged. `test_package.py` still passes (26 tests).

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

## Headline (n = 1000 quick decisions per plan, 2026-11-01, fallback synthetic card: no `tees/cardless.py` yet)

Tee shots where the card-blind plan has **the same club and an aim within 10 yds** of the true-card plan:

| courses | back set | 2nd set | back: same club / same or ref tie | mean regret per tee shot (back / 2nd) |
|---|---|---|---|---|
| OSM maps every hole (14 courses; 3 library ones on review-OK holes) | **142/168 (85 %)** | **117/154 (76 %)** | 149 (89 %) / 156 (93 %) | 0.013 / 0.021 strokes |
| OSM maps few or no holes (hot_springs_park, jayhawk_club, national_kc) | **2/20 (10 %)** | **2/20 (10 %)** | 11 / 11 | 0.87 / 1.19 strokes |
| all scored (17 courses) | **144/188 (77 %)** | **119/174 (68 %)** | | 0.09 / 0.14 strokes |

On a fully mapped course the OSM hole line already starts near the back tee: median back-tee error 3.1 yds,
177/219 within 10 yds, and par right on 217/219 holes. For comparison, the pipeline's own true-card plan
agrees with the hand truth on about 77 % of clubs (`PIPELINE.md` section 5). So **on a mapped course, a missing
card costs less than the map already does on the back set.** The 2nd set is where the guess shows: the 0.94 x back
rule puts the tee more than 10 yds off on half the holes (median 10-13 yds).

## Results

<!-- cardblind_eval:begin -->
| course | set (ref / blind) | ref | routing right | par right | back-tee err med (<=10 yds) | |len err| med | same club | same or ref tie | same club + aim <=10 | no plan | aim diff med (same club) | regret / tee shot |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| blue_hills | back: Black / Back | hand | 18/18 | 17/18 | 2.4 (18/18) | 6.0 | 11/14 | 14/14 | **11/14** | 0 | 2.4 | 0.003 |
| blue_hills | second: Blue / Second | hand | 18/18 | 17/18 | 10.9 (9/18) | 14.5 | 11/14 | 11/14 | **9/14** | 0 | 2.1 | 0.039 |
| coldwater | back: Black / Back | card | 17/18 | 17/18 | 2.5 (14/18) | 2.5 | 13/14 | 13/14 | **13/14** | 1 | 0.0 | 0.001 |
| coldwater | second: Blue / Second | card | 18/18 | 17/18 | 6.0 (12/18) | 6.0 | 12/14 | 13/14 | **12/14** | 1 | 2.5 | 0.002 |
| eagle_knoll | back: Eagle / Back | hand | 18/18 | 18/18 | 3.2 (15/18) | 6.0 | 12/14 | 13/14 | **12/14** | 0 | 2.5 | 0.007 |
| eagle_knoll | second: Back / Second | hand | 18/18 | 18/18 | 16.6 (8/18) | 15.0 | 12/14 | 13/14 | **10/14** | 0 | 3.5 | 0.023 |
| ellis | back: Blue / Back | card | 18/18 | 18/18 | 3.0 (15/18) | 3.0 | 14/14 | 14/14 | **13/14** | 0 | 0.2 | 0.003 |
| ellis | second: White / Second | card | 18/18 | 18/18 | 4.7 (15/18) | 5.0 | 13/14 | 13/14 | **12/14** | 0 | 0.2 | 0.006 |
| gateway_national | back: The Tips / Back | card | 17/18 | 18/18 | 1.9 (16/18) | 4.5 | 12/13 | 12/13 | **12/13** | 0 | 0.1 | 0.053 |
| gateway_national | second: Champions / Second | card | 17/18 | 18/18 | 27.1 (5/18) | 24.0 | 10/13 | 12/13 | **6/13** | 0 | 7.1 | 0.062 |
| creekmoor (review-OK holes) | back: Black / Back | card | 9/9 | 9/9 | 4.0 (9/9) | 4.0 | 7/7 | 7/7 | **7/7** | 0 | 0.6 | 0.0 |
| creekmoor (review-OK holes) | second: Green / Second | card | 9/9 | 9/9 | 6.0 (8/9) | 6.0 | 7/7 | 7/7 | **7/7** | 0 | 2.0 | 0.001 |
| hot_springs_arlington | back: Gold / Back | card | 18/18 | 18/18 | 2.4 (16/18) | 3.0 | 11/14 | 13/14 | **10/14** | 0 | 0.5 | 0.015 |
| hot_springs_arlington | second: Blue / Second | card | 18/18 | 18/18 | 16.1 (6/18) | 13.0 | 12/14 | 13/14 | **11/14** | 0 | 3.1 | 0.01 |
| hot_springs_park | back: Gold / osm_back | card | 0/11 | 4/11 | 399.1 (0/9) | 71.0 | 4/7 | 4/7 | **0/7** | 0 | 171.1 | 0.414 |
| hot_springs_park | second: Blue / osm_back | card | 0/11 | 4/11 | 427.9 (0/9) | 88.0 | 5/7 | 5/7 | **0/7** | 0 | 198.9 | 0.457 |
| jayhawk_club | back: Black / Back | card | 0/10 | 2/10 | 347.1 (0/7) | 55.0 | 4/6 | 4/6 | **1/6** | 1 | 90.5 | 0.85 |
| jayhawk_club | second: Green / Second | card | 1/10 | 2/10 | 344.3 (0/7) | 50.0 | 3/6 | 3/6 | **1/6** | 1 | 13.1 | 0.419 |
| mozingo_lake | back: App / Back | card | 11/18 | 18/18 | 29.8 (7/18) | 26.5 | 10/14 | 10/14 | **7/14** | 0 | 2.6 | 0.044 |
| national_kc | back: Black / Back | card | 1/18 | 2/18 | 305.4 (2/9) | 153.0 | 3/7 | 3/7 | **1/7** | 1 | 18.0 | 1.426 |
| national_kc | second: Blue / Second | card | 1/18 | 2/18 | 293.2 (2/9) | 167.0 | 3/7 | 3/7 | **1/7** | 1 | 18.9 | 2.676 |
| finkbine (review-OK holes) | back: Black / Back | card | 12/12 | 12/12 | 6.0 (8/12) | 6.0 | 9/9 | 9/9 | **9/9** | 0 | 2.3 | 0.002 |
| finkbine (review-OK holes) | second: Gold / Second | card | 12/12 | 12/12 | 9.5 (7/12) | 9.5 | 8/9 | 8/9 | **8/9** | 0 | 1.5 | 0.006 |
| oaks_margaritaville | build failed: RuntimeError: ref build failed: ['no holes built (no golf=hole ways and no tee/green pairs | | | | | | | | | | | |
| pine_dunes | back: Gold / Back | card | 18/18 | 18/18 | 1.8 (18/18) | 3.0 | 14/14 | 14/14 | **14/14** | 0 | 2.5 | 0.001 |
| pine_dunes | second: Blue / Second | card | 18/18 | 18/18 | 6.3 (12/18) | 9.0 | 13/14 | 14/14 | **12/14** | 0 | 2.3 | 0.007 |
| spirit_hollow | back: Gold / Back | card | 14/18 | 18/18 | 5.7 (12/18) | 8.0 | 11/14 | 12/14 | **10/14** | 0 | 0.3 | 0.02 |
| spirit_hollow | second: Black / Second | card | 15/18 | 18/18 | 19.1 (4/18) | 15.0 | 10/14 | 11/14 | **10/14** | 0 | 3.4 | 0.019 |
| tomahawk_hills | build failed: RuntimeError: blind build failed: ["AttributeError: 'MultiPolygon' object has no attribute | | | | | | | | | | | |
| veenker | back: Blue / Back | card | 17/18 | 18/18 | 4.6 (14/18) | 7.5 | 12/13 | 12/13 | **11/13** | 0 | 2.2 | 0.011 |
| veenker | second: Gold / Second | card | 16/18 | 18/18 | 11.5 (9/18) | 11.5 | 10/13 | 10/13 | **9/13** | 0 | 3.6 | 0.046 |
| wakonda | back: Black / Back | card | 17/18 | 18/18 | 3.5 (15/18) | 4.0 | 13/14 | 13/14 | **13/14** | 0 | 0.1 | 0.004 |
| wakonda | second: Blue / Second | card | 16/18 | 18/18 | 11.5 (7/18) | 11.5 | 12/14 | 12/14 | **11/14** | 0 | 2.0 | 0.015 |
| sycamore_ridge | build failed: excluded: the ref build has no card either (osm_back), so there is no card truth | | | | | | | | | | | |
| **all** | **back** | | 205/258 (79 %) | 225/258 (87 %) | 4.0 (179/244 (73 %)) | 5.0 | 160/188 (85 %) | 167/188 (89 %) | **144/188 (77 %)** | 3 | 1.6 | 0.097 |
| **all** | **second** | | 195/240 (81 %) | 207/240 (86 %) | 13.0 (104/226 (46 %)) | 12.0 | 141/174 (81 %) | 148/174 (85 %) | **119/174 (68 %)** | 3 | 2.5 | 0.144 |

Failure causes, back set (44 tee shots not same club + aim <= 10 yds): routing (wrong green) 15; routing / tee >40 yds off 14; club flip on a ref tie 6; tee position >15 yds 5; club flip (geometry ~same) 2; aim >10 yds (same club) 2

Failure causes, second set (55 tee shots not same club + aim <= 10 yds): tee position >15 yds 23; routing (wrong green) 15; routing / tee >40 yds off 9; club flip (geometry ~same) 3; club flip on a ref tie 3; par wrong (blind par 3) 1; aim >10 yds (same club) 1

<!-- cardblind_eval:end -->

### Top failure causes (tee shots not same club + aim <= 10, from the table above)

1. **Unmapped holes, i.e. routing (30 of 44 back-set misses).** hot_springs_park (its OSM hole ways belong to the other
   course: `ignore_osm_holes`, so no hole lines and no synthetic card at all), jayhawk_club (OSM maps 8 of 18) and
   national_kc (OSM greens and tees, no hole ways) route the wrong green on nearly every hole. Without a card
   the router has no length prior. This is the job of teammate (a), `zero_tap/pathroute/` (cart paths and
   green->tee chains). Mapped courses add 11 "tee > 40 yds off" misses: Mozingo Lake (the ref "App" set comes
   from request yardages, and the OSM line starts at another box) and Spirit Hollow (OSM line vs card box).
2. **2nd-set tee position (23 of 55 2nd-set misses).** `Second = 0.94 x back` is a placeholder. Real 2nd sets are
   0-40 yds shorter, more on par 5s, and sometimes share the back box. That is teammate (b)'s synthetic tee
   sets (`tees/cardless.py`), which `card: none` picks up automatically. Gateway National (6/13) and Eagle Knoll
   2nd sets are the worst.
3. **Club flips the reference itself calls a tie (6 back, 3 2nd).** Margin < 0.01 strokes, so this is noise, not
   error ("same or ref tie" column). The quick model runs at n = 1000; a full n = 8000 run would remove some.
4. Par: 2 wrong on mapped courses (blue_hills hole with OSM `par` != card, coldwater 1); par-from-length
   only matters where OSM has no `par` tag.

## Honest caveats / coverage

* **Covered:** 16 courses with committed raw OSM in `packages/` (two hand-truth references: Blue Hills and Eagle
  Knoll `courses/<slug>/truth/package.json`; the rest have the true web card plus the request's review overrides).
  Also 3 reviewed library courses (creekmoor, finkbine, sycamore_ridge) with a cached OSM snapshot
  (`osm_inventory.json`), scored on review-OK holes. sycamore_ridge is excluded because its reference build has no
  card either.
* **Not covered:** oaks_margaritaville (OSM maps nothing; the reference build fails too) and tomahawk_hills (the
  blind build crashes in routing with `MultiPolygon has no attribute exterior`, on the card tier fed a synthetic
  card with holes missing; it reproduces with `--build tomahawk_hills blind`). colbert_hills / shoal_creek truth
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
