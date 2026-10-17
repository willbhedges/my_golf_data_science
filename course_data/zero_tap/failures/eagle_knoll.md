# Eagle Knoll Golf Club (Hartsburg, MO): blind automatic pipeline vs hand truth

NCCGA Regional 2 (Nov 7-8 2026). Blind request = name + town + state + "Blue" (`course_data/requests/package_eagle_knoll.json`).
Truth: `course_data/truth/eagle_knoll/` (holes_truth.json: numbering, par, tees per set, greens; trace.py /
hand_zones_ll.json: landing corridors 145-345 yds x +/-65 from the Back tee, checked on NAIP 2022 0.6 m + CIR,
NAIP 2012-2020 and the 2015 3DEP lidar). Scores: `course_data/courses/eagle_knoll/score_*.md`
(`course_data/courses/score_auto.py`, quick v1 decision n=6000, corridor IoU on 220-340 x +/-45).

## Before / after

| | v0: first package build | blind auto (= v0 + vision_any / OB evidence request + rebuild) |
|---|---|---|
| routing / par / green within 10 yds | 18/18, 18/18, 18/18 | 18/18, 18/18, 18/18 |
| par 3s planned as par 3 (with outline) | 4/4 (4/4) | 4/4 (4/4) |
| tees within 10 yds (all 4 sets) | 69/72 | 69/72 |
| trees IoU (corridor) | 0.14 | 0.85 |
| long grass IoU | 0.0 (9, 11) | 0.0 (9, 11) |
| water IoU | 1.0 | 0.75 |
| OB IoU | 0.18 | 0.62 |
| tee-shot club: same / same-or-tie | 9/14, 9/14 | 13/14, 14/14 |
| total regret (truth-map EV) | 0.261 strokes | 0.019 strokes |

No algorithm change was kept for this course: the one candidate (below, F3) did not improve the score here, so
"after" = "blind auto". Par-3 greens (the golfer's concern on other auto courses) were all present and planned.

## Failures, root causes, proposals

| # | holes | category | what went wrong | root cause | proposed fix | owner |
|---|---|---|---|---|---|---|
| F1 | 3,4,5,7,8,9,10,11,13,14,15,17,18 (v0) | formation / orchestration | the first package had trees on 1 of 14 landing corridors ("no trees or long grass mapped"); 5 club picks wrong, 0.26 strokes | `course_package.yml` builds from OSM + NAIP only; the vision layer (`vision_any/fetch_any.py`, `v2_fetch.py`, `v2_model.py --infer`) and OB evidence (`ob/fetch.py`) only run when someone commits a separate `truth_maps` / `tourn_truth` request, then a rebuild is needed | for a fresh fetch, run fetch_any + v2_fetch + v2_model --infer + ob/fetch inside the package job before the build (one workflow, no second request); a zero-tap course must never be planned on the OSM-only package | A (formation) / pipeline |
| F2 | 9, 11 | perception: long grass | unmown grass strips (11 left 175-305 x -70..-42; 9 right of the cart path from 280) not detected | vision_any v2 long-grass class does not fire on dense green unmown grass in a June image (it looks for tan / textured grass); the evidence that separates it here is temporal (tan in NAIP 2020, dark green 2022) and CIR brightness without lidar height | add a "not mown in any year" feature (per-pixel max-min NDVI / texture across NAIP years) and a CIR-bright + HAG < 0.5 m rule to the long-grass head; truth examples: these two polygons | A / D (benchmark) |
| F3 | 18 | OB | inferred OB reaches 25-35 yds left of the line (the left rough) where the truth lots start ~40-45 yds left | `ob/params.json` uses out_src "parcels" with out_off -8 (fitted on Iowa parcel lines); Missouri has no free parcel layer, so the OSM course outline stands in and is pulled 8 yds further in; the outline itself already runs 10-20 yds inside the yards | tried: skip the inward offset when parcels fall back to the OSM outline (unit test written); on this course OB IoU went 0.62 -> 0.55 against a truth line that is itself +/-8 yds (no stakes visible), so it was reverted. Needs more OSM-outline courses with stake-level truth before changing; candidate: OB from house footprints + ~25 yds of yard where no parcels exist | B (outside evidence) |
| F4 | 17 | water extent | the creek is mapped 2x wider than OSM / the photo (vision water added along the wooded creek) | vision water head treats lidar no-return / dark shade under the creek canopy as water | clip vision water to within ~4 yds of an OSM waterway/water_hazard when one exists | A |
| F5 | 7, 18 (Eagle), 17, 18 (Forward) | tees | the Eagle box is put on the Back pad (7: 11 yds, 18: 12 yds short of the card); Forward 9-14 yds off | `tees/localize.py` prefers an existing pad with up to 25 yds card error (cost ~ err + share 2) over a walk-back (cost 20) | not changed: the truth for these sets is itself an estimate (no separate pad visible in 0.6 m NAIP); the tournament set (Back) is right on every hole. If more courses confirm hidden back boxes, lower max_err_yd for a pad already used by another set | C |
| F6 | 17 | decision | auto Driver -30 vs truth 4-wood +10 (regret 0.019) | F4 (wider creek) | follows F4 | - |
| T1 | - | tooling | score_auto.py counted a 0.0-yd green error as missing (`(err or 99) <= 10`) | falsy zero | fixed (`is not None`) | - |

## Uncertain in the truth

* Eagle-set tees on 7 and 18 and Forward on 17 / 18: estimated from the card (pad tee moved along the line).
* Hole 18 OB line +/-8 yds (house lots, no stakes visible); hole 9 / 11 long-grass edges +/-5 yds; hole 17 creek width.
* Lidar is 2015 leaf-off: crowns have grown 2-5 yds on some edges (10 right was corrected by hand from NAIP 2020/2022).
