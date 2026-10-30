# Any-US-course pipeline: the stage selector, and what it scores end to end

`platform/package.py` now chooses the hole-inference method from the data that exists (`platform/stage_select.py`).
Every stage falls back to the next method on any error, and `package.json["pipeline"]` records what ran. The
numbers below come from the held-out **test** split of `generalize/validation_set.json` (31 courses). That split
was read once, after every choice had been made on the **train** split (51 courses).

## 1. What runs, by stage

| stage | data available | method that runs (fallbacks in order) |
|---|---|---|
| S1 card | request yardages > card file > web card (club site > golfify > OpenGolfAPI) > **golfer-typed card** (`"typed_card": {"yards": "...", "pars": "..."}`, `typed_card.py`, new) | none: the no-card tiers below |
| S2a holes | OSM maps every hole | OSM (`pipeline.holes.method = "osm"`) |
| | **mapped + card** (OSM greens and tee features for >= 80 % of the holes) | routing v2 + structure-solver prior, lam 0.5 > v2 > structure > geometry |
| | **unmapped + card** | routing v2 on segment model + lidar inputs, with a structure prior lam 0.25 from the **perception scene** > v2 > structure (perception scene) > geometry |
| | **mapped, no card** | structure solver alone > v2 > geometry |
| | **unmapped, no card** | structure solver on the perception scene > v2 > geometry |
| S2a confirm | any routed hole | `confirm.json` (golf_confirm/1): a routing v2 session. It uses the tier's prior; the no-card tiers use v2 + prior lam 1.0 (mapped) or v2 alone (unmapped) |
| S2 tees | card | **tees/localize.py v2 (now the default)** > place_tee.place_course_sets v1 (`"tee_localizer": "v1"` opts out) |

The **structure prior** is a new optional unary feature in routing v2 (`struct_prior`). It is the structure solver's
exact marginal P(green m is hole k), oriented front/back by its nine classifier (`solver.py` debug
`marg_oriented`), snapped to router greens within 25 yds, and scaled by lam. Without the prior the column is zero
and v2 behaves exactly as before. Perception greens and tees fed straight to the router as extra candidates scored
0.46-0.62 on train, against 0.69 without them, so the scene only feeds the structure prior.

## 2. Selection (train split, 51 courses; `pipeline_select.json`)

Hole-number accuracy. The grid is in `pipeline_eval.py select`.

| tier | previous default | v2 | structure | v2 + prior (lam 0.25 / 0.5 / 1 / 2 / 4) | chosen |
|---|---|---|---|---|---|
| mapped + card | 82.5 % | 82.5 % | 59.3 % | 83.5 / **83.6** / 76.6 / 69.9 / 66.2 % | v2 + prior 0.5 |
| unmapped + card | 68.9 % | 68.9 % | 46.1 % | **73.3** / 71.3 / 65.0 / 56.1 / 50.7 % | v2 + prior 0.25 |
| mapped, no card | 9.9 % (geometry) | 10.9 % | **21.9 %** | 13.9 / 18.7 / 20.0 / 16.1 / 18.7 % | structure |
| unmapped, no card | 0 % | 8.1 % | **14.0 %** | 3.8-6.7 % | structure (perception) |

## 3. End to end on the held-out test split (31 courses; `pipeline_eval.json`)

The tiers are simulated from fully mapped courses, and their OSM golf=hole ways and refs are always hidden.
"Unmapped" also removes the OSM greens, tees and fairways. The card is the web card, or pars and lengths when none
is online (28/31 courses have a web card). A hole counts as right when its green is within 20 yds and its tee
within 40 yds of the hidden way, with the same number (`routing.score`). Taps come from an oracle golfer answering
`confirm.py`'s questions (max bits per tap) until all holes are right, capped at 30 taps. A course that is not
right within the cap is counted at 2N, the cost of tapping every tee and green.

| tier | method | hole-number acc | all holes right, no input | wrong / course | flags / course | reach 100 % (<= 30 taps) | mean taps (all courses) | median taps (reached) |
|---|---|---|---|---|---|---|---|---|
| mapped + card | previous (v2) | 76.2 % | 12.9 % (4/31) | 3.68 | 6.74 | 93.5 % | 15.2 | 15.0 |
| | **pipeline** | **76.7 %** | **16.1 % (5/31)** | 3.55 | **4.68** | **96.8 %** | **13.7** | 15.5 |
| unmapped + card | previous (v2, model inputs) | 62.7 % | 0 % | 6.03 | 8.90 | 83.9 % | 19.3 | 16.5 |
| | **pipeline** | **70.1 %** | 0 % | **4.74** | 6.84 | **90.3 %** | **18.5** | 17.0 |
| mapped, no card | previous (geometry) | 6.1 % | 0 % | 15.97 | - | no confirm: tap all | 34.0 | 36 |
| | **pipeline** | **27.1 %** | **6.5 % (2/31)** | 12.35 | 17.35 | 38.7 % | **29.1** | 19.0 |
| unmapped, no card | previous (nothing) | 0 % | 0 % | 17.0 | - | no confirm: tap all | 34.0 | 36 |
| | **pipeline** | **15.8 %** | 0 % | 14.29 | 16.48 | 6.5 % | 33.8 | 15.0 |

**Perception-clean subset.** These are the 12 test courses in the perception agent's held-out states (GA KY MN UT
ME WY); its models were trained on the others.

| tier | previous | pipeline |
|---|---|---|
| mapped + card | 82.2 % (2/12 all right) | **85.5 %** (4/12) |
| unmapped + card | 56.4 % | **68.2 %** |
| mapped, no card | 5.7 % | **29.5 %** |
| unmapped, no card | 0 % | **11.2 %** |

On jato_highlands_me (unmapped + card) the segment model found no greens, so v2 had nothing to route. The selector
fell back to the structure solver on the perception scene. The previous default produced no holes there.

### Typed card

A golfer-typed card (`typed_card.py`, now a package request input) turns a no-card course into a card tier. On
test, typing the yardages moves a mapped course from 27 % to 77 % hole-number accuracy, and an unmapped course from
16 % to 70 %.

## 4. Tees: localizer v2 is now the default

`tees/eval_localize.md` (C3) covers the test split with the OSM tee boxes hidden, 513 set placements. v1 put 69 %
of them within 10 yds and v2 puts 86 % there (p90 24.6 to 14.6 yds). Where OSM maps the boxes the two are neutral:
on Spirit Hollow both have a median of 9.7-9.8 yds and 8/16 within 10 yds. Failures fall back to v1.

## 5. Product picks on the 5 truth courses (`picks_pipeline.py` -> `pipeline_picks.json`)

Each package is rebuilt from its committed raw data under both settings, then scored exactly as
`qa/scoreboard.py` does: the product's quick decision with n = 8000 against each course's truth. All 5 courses
have every hole in OSM, so only the tee stage differs.

| course | previous: same club | pipeline: same club | same or tie (prev -> new) | picks changed |
|---|---|---|---|---|
| Spirit Hollow (Black) | 11/16 | **12/16** | 14 -> 14 | 9B Driver -> 2-wood (now right) |
| Mozingo Lake | 11/14 | 11/14 | 12 -> 12 | - |
| Veenker | 10/13 | **11/13** | 11 -> 11 | 3 Driver -> 4-wood (now right); 12 2-wood -> 4-wood (still wrong) |
| Coldwater | 12/14 | 12/14 | 14 -> 13 | - (one tie flag) |
| Ellis | 9/14 | 9/14 | 9 -> 10 | - (one tie flag) |
| **total** | **53/71 (74.6 %)** | **55/71 (77.5 %)** | 60 -> 60 | |

## 6. Honesty notes

* **The structure solver was refitted for this evaluation.** The shipped `structure/params.json` included every
  generalize course in its dev set, test split included. `structure/params_noval.json` was refitted (Actions run
  39040874469) on the dev set minus all 82 validation-set courses, with fit, CRF, nine classifier and calibration.
  That leaves 37 CRF routes instead of 56. Every number above uses it (`STRUCTURE_PARAMS`); `package.py` keeps the
  shipped `params.json`. Some starting values and fixed constants in it (temperature, not-hole prior) predate the
  refit.
* **Perception scenes** for 19 of the 31 test courses come from the perception agent's training states, so the
  unmapped tiers are optimistic there. The clean subset is reported separately in section 3.
* The selection grid ran on train only. Test was read once, for the configuration committed in `stage_select.SELECT`.
* The tiers are simulated by hiding OSM data on fully mapped courses. Real unmapped courses may be harder: their
  perception and segment inputs were never cross-checked against OSM.
* **Without a card the pipeline is still mostly guessing.** At 27 % / 16 % hole accuracy the golfer confirm rarely
  finishes within 30 taps (39 % / 6 %). The practical path is to ask for the card: a typed card moves the course to
  the card rows.

## 7. Files

| file | what |
|---|---|
| `platform/stage_select.py` | data profile -> tier -> SELECT -> fallbacks; structure solve and prior; perception candidates; geometry fallback |
| `platform/routing_v2.py` | `struct_prior` feature (`prior_plane`), `route(n_holes=)` |
| `platform/package.py` | `route_missing_holes` through the selector, `package.pipeline`, `confirm.json`, typed card, tee v2 default |
| `platform/confirm.py` | `Session(n_holes=)` for no-card sessions |
| `platform/pipeline_eval.py`, `.github/workflows/pipeline_eval.yml` | selection grid (train), final (test), refit / collect stages |
| `platform/pipeline_select.json`, `pipeline_eval.json`, `pipeline_shards/` | results |
| `platform/picks_pipeline.py`, `pipeline_picks.json` | product picks before / after on the 5 truth courses |
| `structure/params_noval.json` | structure weights without any validation-set course |
| `platform/commit_packages.sh` | course-package commit step: never overwrites a package that changed on origin since the run's checkout |

## 8. sequence_v3 (formation-v2 pairs + zero-tap sequence solver v3): built, not adopted

`stage_select.sequence_v3`: hole_pairs/1 from `zero_tap/formation/hole_pairs.py` (no aux layers in production) on
the OSM scene (mapped) or the perception scene (unmapped), then `zero_tap/sequence/solve.run` with the v3 settings
(PAIRS_FORM_W 3, CARD_W 2, nesting). Card tiers only; falls back to v2+structure > v2 > structure > geometry on any
error; its golfer-confirm session is the tier's v2+structure. `package.json["pipeline"]["holes"]` records `method`,
`chosen`, `tried` and `fallbacks`. Opt in per request with `"hole_method": "sequence_v3"`; `stage_select.USE_V3`
(False) would make `SELECT_V3` the default.

Held-out test (`pipeline_eval.py v3`, request `requests/pipeline_eval_v3.json`, Actions run 41109695224 ->
`pipeline_eval_v3.json` when its last shards finish). Partial read (courses scored so far, same scorer as section 3):

| tier | courses | selector (v2 + structure prior) | sequence_v3 |
|---|---|---|---|
| mapped + card | 15 | 78.1 % hole-number acc, 3 all right | 66.9 %, 1 all right |
| unmapped + card | 11 | 65.0 %, 0 all right | 43.9 %, 1 all right |

Gate courses (`library/gate_eval.py`): a tie by construction. 9 of the 10 builds have a golf=hole way for every
hole (the hole stage is `osm`), National KC has no card (mapped_nocard: v3 does not run), Pine Dunes has no build.

Decision: **not adopted** (test is worse). The zero-tap benchmark gain (fully right 17 -> 22 %) used aux layers and
D's per-course scorer on courses where the router is not an option; against routing v2 + structure prior, with
hole ways and refs hidden, v3 loses many holes (e.g. riverwood_national_mn 1.00 -> 0.41).
