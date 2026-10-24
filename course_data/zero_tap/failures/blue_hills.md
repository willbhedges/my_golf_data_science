# Blue Hills Country Club (Kansas City, MO): blind automatic pipeline vs hand truth

NCCGA event, Tue Oct 27 2026 (tee set unknown: Black = back, Blue = second-to-back, or Blue/White, the three sets over 6,700 yds). Blind request = name + town +
state + "Black" (`course_data/requests/package_blue_hills.json`): resolved to OSM way/315837565 (777 W Burning Tree
Dr, south KC; not Blue Springs or the other "Blue Hills" courses), golfify card. Truth: `course_data/truth/blue_hills/`
(holes_truth.json: numbering, par, tees per set, greens, line of play; trace.py / hand_zones_ll.json: 14 landing
corridors 145-440 yds x +/-65 from the Black tee; NOTES.md). Scores: `course_data/courses/blue_hills/score_*.md`
(`course_data/courses/score_auto.py`, quick v1 decision n=8000, corridor IoU on 220-340 x +/-45).

## Before / after

| | v0: first package build | blind auto (= v0 + vision_any / OB evidence request + rebuild) |
|---|---|---|
| routing / par / green within 10 yds | 18/18, 18/18, 18/18 | 18/18, 18/18, 18/18 |
| par 3s planned as par 3 (with outline) | 4/4 (4/4) | 4/4 (4/4) |
| tees within 10 yds (8 sets x 18) | 136/144 | 136/144 |
| trees IoU (corridor) | 0.0 | 0.66 |
| water IoU | 0.0 | 0.36 |
| OB IoU | 0.99 | 0.44 |
| tee-shot club: same / same-or-tie | 9/14, 9/14 | 13/14, 14/14 |
| total regret (truth-map EV) | 0.285 strokes | 0.0004 strokes (10: 4-wood vs 2-wood, a tie) |

No algorithm change was kept for this course ("after" = "blind auto"). The OSM mapping here is unusually complete
(17 of 18 hole ways, 60 tee pads, 69 bunkers, 22 fairways) and the card was found, so routing, greens and tees were
right from the first build; what the first build lacked was trees.

## Failures, root causes, proposals

| # | holes | category | what went wrong | root cause | proposed fix | owner |
|---|---|---|---|---|---|---|
| B1 | all 14 tee shots (v0) | formation / orchestration | the first package had no trees in any landing zone: 5 picks wrong (3, 4, 10, 11, 17: Driver where the truth plays 4-wood or 2-wood), 0.29 strokes | as Eagle Knoll F1: vision / OB evidence only arrive with a separate `tourn_truth` request and a rebuild | as Eagle Knoll F1 (run fetch_any + v2_fetch + v2_model --infer + ob/fetch inside the package job) | A / pipeline |
| B2 | 1, 3, 6, 9, 11, 13, 18 | perception: tree recency | the 3DEP lidar is KS_JacksonCo_2006 (April 2006, 20 years old): trees grown since are missing (1 left 295, 3 right 240, 6 left 330, 9 left 229, 11 right 306-332, 13 right 372, 18 left 352), crowns gone are still trees (1 right 325-360; 18 right 333-386, cleared with the renovation, in the Black / Blue landing zone). Product and truth start from the same layer, so the blind score does not see it | lidar canopy taken as current regardless of age; package QA does not report the lidar date | report the lidar acquisition year in qa.md and flag > 10 years; run `vision_any/canopy_recency.py` (GONE + ADD) whenever the lidar predates the newest NAIP by > 8 years; truth examples: the LATE zones in trace.py | A |
| B3 | 17 | water extent | the creek across 17 (338-360 from Black, 300-325 from Blue, downhill landing) is a 6-yd OSM strip; the channel is 15-20 yds wide at the line, with dense vegetation on the far bank | OSM water mapped as a line-like strip; vision water (NDWI + DTM) adds only part of it (water IoU 0.36) | widen an OSM water polygon narrower than ~8 yds to the contiguous CIR-dark / NDWI channel, capped at ~25 yds | A |
| B4 | 1, 2, 4, 7, 9, 10, 11, 18 | OB | inferred OB starts 7-8 yds inside the OSM course outline (auto-only OB 900-2200 yd2 per hole) | `ob/params.json` out_off -8 with the OSM outline standing in for parcels (as Eagle Knoll F3); here the outline is the property line (it follows the tree line / lot lines behind the houses) | same as Eagle Knoll F3: needs stake-level truth on more outline-only courses before changing the offset; candidate: no inward offset when the outline runs along a tree line with house lots behind it | B |
| B5 | 2 (Black) | tees | Black tee put on a "lidar pad" 22 yds behind the OSM pad, next to the cart building (card 419: lidar pad 420, OSM pad 414) | `tees/localize.py` prefers a pad matching the card within 1 yd over the visible OSM pad 5 yds short; the lidar pads come from the 2006 DTM (pre-renovation tees can survive there) | weight lidar pads by lidar age, require the pad to be visible as turf in the current NAIP, and accept an OSM pad up to ~6 yds off the card before looking further | C |
| B6 | 4, 14, 15 (White / Gold / combos) | tees | non-key sets 10-15 yds off (White 4 and 15, Gold 14) | combo sets and shared complexes (as Eagle Knoll F5) | as Eagle Knoll F5 | C |
| T1 | - | tooling | the sandbox cannot reach GolfPass / BlueGolf / golfify / OpenGolfAPI / weather APIs | network policy | `.github/workflows/web_fetch.yml` (request-file page fetch) and `weather_course.yml` + `weather/fetch_course_forecast.py` (any course's forecast) added | - |
| T2 | - | tooling | the v2 page solved one base tee set; other sets were offsets of it (20-yd grid) | single `which` per page | `alt_bases` in config: a set can be a fully solved base (own tees, aims, Bayesian calm-day picks) shown in the same page (Blue and Blue/White here); `nccga_v2.yml` takes an optional `holes` list for decide re-runs | - |

| T3 | - | tooling (all v2 courses) | the calm-day Bayesian decide ran every hole at 48 F on every course built with `v2_course.py` (Eagle Knoll, Gateway, National KC, Pine Dunes, Arlington too) | `spirit_hollow/v2/model.hole_temp(h, day=TEE_DAY, ...)` binds Spirit Hollow's day as a default at import; setting `M.TEE_DAY` later does not change it, no forecast row matches, fallback 48 F | `v2_course.activate` rebinds the defaults; Blue Hills decisions rerun at the Oct 27 forecast (60-68 F by hole). The other courses' decisions should be rerun (decide-only request: `"offsets": []`) | - |
| T4 | - | tooling | two solved bases of one course merged each other's parts (identical v2 dirs) | artifacts named `v2-<slug>-<kind>-<i>`, the merge copied every `v2-<slug>-*` | artifacts carry the which; `.github/workflows/v2_remerge.yml` re-merges an earlier run by matrix index | - |

## Uncertain in the truth

* Black tees on 2, 5 and 6: 5 yds short of the card at the back of the pad (no box visible further back).
* Forward boxes not in OSM (Gold 5 / 6 / 12 / 18, Red 3 / 5 / 9 / 12 / 17 / 18) keep the blind package's tee; White 10
  and Gold 16 are 10-11 yds off the card (estimated).
* Tree edges: the 2006 lidar corrected by eye on 1 m / 0.6 m photos; new-tree crowns +/-3 yds (11 right especially).
* 17: creek channel edges +/-4 yds; the far-bank vegetation (traced as trees) may be a wider pool.
* OB = the OSM course outline (no stakes visible in NAIP): +/-5 yds.
