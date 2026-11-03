# Automatic greens (green_auto.py): leave-one-course-out vs OSM greens

40 courses, 688 holes with an OSM green (the detector never reads an OSM green: they are the labels of the other courses and this course's truth). Pick threshold 0.40 and move cap 12 yds (line_end) / 30 yds (moved): green_auto.SCORE_THR / MAX_MOVE_YD, read off the pooled held-out curve below (two scalars chosen on held-out results). Priors: `line_end` = the OSM hole line's end (what the build uses), `moved` = moved 10-25 yds in a random direction (a greenless course's estimate).

| prior | holes | found | on the green | centroid err med / p75 / p90 (yds) | <= 5 yds | IoU med | baseline 24-yd circle: err med / p90, <= 5 yds, IoU | page green (found -> detected, else circle): err med / p90, <= 5, IoU |
|---|---|---|---|---|---|---|---|---|
| line_end | 688 | 632 (92 %) | 100 % | 2.0 / 3.1 / 4.8 | 92 % | 0.716 | 1.3 / 4.9, 90 %, 0.628 | 2.0 / 4.9, 91 %, 0.71 |
| moved | 688 | 628 (91 %) | 99 % | 2.0 / 3.2 / 4.9 | 90 % | 0.72 | 17.4 / 23.9, 0 %, 0.12 | 2.2 / 9.5, 82 %, 0.706 |
| line_end (par 3s) | 159 | 146 (92 %) | 100 % | 2.0 / 2.6 / 3.9 | 93 % | 0.708 | 1.4 / 4.5, 91 %, 0.622 | 2.1 / 4.3, 92 %, 0.703 |
| moved (par 3s) | 159 | 147 (92 %) | 99 % | 2.0 / 2.9 / 4.5 | 92 % | 0.709 | 16.8 / 22.9, 0 %, 0.106 | 2.1 / 6.2, 86 %, 0.7 |
| line_end (no lidar) | 21 | 13 (62 %) | 100 % | 2.6 / 3.1 / 3.3 | 100 % | 0.726 | 0.0 / 0.0, 95 %, 0.677 | 1.9 / 3.4, 95 %, 0.721 |
| moved (no lidar) | 21 | 13 (62 %) | 100 % | 2.1 / 3.0 / 3.4 | 100 % | 0.731 | 19.8 / 23.3, 0 %, 0.06 | 3.0 / 21.6, 62 %, 0.7 |

Threshold curve (moved prior): 0.1: found 95 %, <= 5 yds 89 %, med 2.0, p90 5.2; 0.2: found 94 %, <= 5 yds 89 %, med 2.0, p90 5.2; 0.3: found 93 %, <= 5 yds 90 %, med 2.0, p90 5.0; 0.4: found 91 %, <= 5 yds 90 %, med 2.0, p90 4.9; 0.5: found 83 %, <= 5 yds 92 %, med 2.0, p90 4.8; 0.6: found 60 %, <= 5 yds 91 %, med 2.0, p90 4.8; 0.7: found 36 %, <= 5 yds 90 %, med 2.0, p90 5.3

## Per course (moved prior)

| course | holes | found | <= 5 yds | err med | IoU med | baseline err med |
|---|---|---|---|---|---|---|
| amana_colonies | 18 | 18 | 83 % | 2.5 | 0.754 | 16.3 |
| annbriar | 18 | 18 | 89 % | 2.4 | 0.692 | 19.2 |
| blue_hills | 18 | 17 | 100 % | 2.1 | 0.807 | 17.3 |
| buffalo_dunes | 18 | 12 | 83 % | 3.5 | 0.621 | 19.7 |
| buffalo_ridge | 18 | 18 | 83 % | 1.8 | 0.704 | 18.7 |
| colbert_hills | 17 | 17 | 47 % | 5.6 | 0.552 | 16.6 |
| coldwater | 18 | 18 | 100 % | 2.2 | 0.736 | 16.8 |
| creekmoor | 17 | 17 | 88 % | 2.3 | 0.649 | 18.5 |
| drumm_farm | 18 | 14 | 100 % | 1.7 | 0.634 | 16.2 |
| dubs_dread | 18 | 18 | 100 % | 1.1 | 0.738 | 17.2 |
| eagle_bend | 18 | 18 | 94 % | 1.3 | 0.688 | 14.8 |
| eagle_knoll | 18 | 17 | 88 % | 1.8 | 0.721 | 15.1 |
| ellis | 18 | 18 | 100 % | 1.7 | 0.833 | 17.3 |
| falcon_ridge | 10 | 10 | 100 % | 1.0 | 0.792 | 15.9 |
| gateway_national | 18 | 18 | 89 % | 2.3 | 0.693 | 16.4 |
| gustin | 18 | 18 | 94 % | 1.9 | 0.699 | 19.3 |
| hodge_park | 18 | 18 | 83 % | 1.9 | 0.587 | 17.0 |
| hot_springs_arlington | 12 | 11 | 91 % | 2.5 | 0.718 | 16.5 |
| hot_springs_park | 11 | 10 | 100 % | 2.2 | 0.736 | 19.8 |
| jayhawk_club | 10 | 3 | 100 % | 2.0 | 0.724 | 18.9 |
| la_nickell | 18 | 14 | 86 % | 2.5 | 0.523 | 14.8 |
| mariah_hills | 18 | 7 | 100 % | 0.9 | 0.763 | 17.5 |
| mozingo_lake | 18 | 15 | 100 % | 1.1 | 0.834 | 17.3 |
| national_kc | 17 | 17 | 100 % | 2.5 | 0.749 | 16.1 |
| old_kinderhook | 18 | 17 | 88 % | 2.1 | 0.711 | 14.6 |
| osage_national | 18 | 16 | 88 % | 2.9 | 0.706 | 17.9 |
| pevely_farms | 18 | 18 | 100 % | 1.4 | 0.825 | 13.9 |
| pine_dunes | 18 | 18 | 94 % | 2.1 | 0.73 | 17.8 |
| prairie_dunes | 18 | 18 | 61 % | 3.0 | 0.692 | 15.9 |
| rivercut | 18 | 16 | 94 % | 1.8 | 0.745 | 15.9 |
| sand_creek_station | 18 | 16 | 69 % | 4.5 | 0.607 | 20.6 |
| st_andrews_op | 18 | 17 | 100 % | 1.6 | 0.806 | 19.2 |
| swope_memorial | 18 | 16 | 94 % | 2.8 | 0.686 | 21.5 |
| the_falls_ofallon | 18 | 18 | 100 % | 1.5 | 0.72 | 13.9 |
| tomahawk_hills | 18 | 17 | 88 % | 1.9 | 0.765 | 17.8 |
| tournament_club_iowa | 18 | 16 | 94 % | 1.8 | 0.715 | 18.2 |
| tpc_deere_run | 18 | 15 | 100 % | 2.2 | 0.721 | 18.4 |
| veenker | 18 | 15 | 100 % | 1.8 | 0.757 | 18.8 |
| wakonda | 18 | 18 | 78 % | 2.2 | 0.665 | 17.9 |
| weaver_ridge | 18 | 16 | 88 % | 3.0 | 0.654 | 19.4 |

## Par-3 plan effect (the page's par-3 plan: product/package.load -> yardage_book.par3_plan, calm)

Per par 3 the plan's aim point and target box on the green the variant gives, against the plan on the OSM green (the truth). `assumed` = the 24-yd round green at the prior; `detected` = the detector's green where found (score >= the threshold), else the assumed one. Hazards come from the same package zones.

| variant | par 3s | aim err med / p90 (yds) | aim <= 5 yds | plays-as distance <= 5 yds | aim on the real green | box share on the real green (med) | box OK (centre on, >= 60 % on) |
|---|---|---|---|---|---|---|---|
| line_end:assumed | 159 | 2.2 / 6.0 | 86 % | 91 % | 100 % | 1.0 | 100 % |
| line_end:detected | 159 | 2.4 / 5.7 | 87 % | 91 % | 99 % | 1.0 | 99 % |
| moved:assumed | 159 | 16.6 / 23.0 | 0 % | 28 % | 28 % | 0.0 | 24 % |
| moved:detected | 159 | 2.5 / 8.7 | 79 % | 86 % | 92 % | 1.0 | 91 % |

## Decision (2026-11-03): adopted as package stage S4g

Rule: a hole whose green is only the hole-line-end estimate gets the detected green when score >= 0.40 and the
centre moves <= 12 yds (OSM hole way) / 30 yds (routed / inferred line). Held out, the used detections are within
5 yds of the OSM green centroid on 92 % (line-end prior) / 90 % (moved prior) of holes (median 2.0 yds, IoU 0.72 vs
0.63 for the assumed circle). Where the estimate is already on the green (the OSM line end on these courses) the
par-3 plan is unchanged (aim <= 5 yds 86 -> 87 %); where it is 10-25 yds off, aim <= 5 yds 0 -> 79 % and the
target box sits on the real green 24 -> 91 %. Not measured: the tee-shot plans (error_budget.py scores par-4/5 tee
shots on hand truth with OSM greens, not par 3s; the approach target moves with the green centre, median 2 yds).

Old Works (MT, 0 OSM greens, no lidar; never in training), checked by eye on NAIP 2023: 15 of 18 holes get a green.
Good outlines on 1, 2, 5, 6, 7, 8, 9, 12, 15, 16, 17, 18; 13 and 14 partly (collar / half the green); 11 wrong
(approach + part of the green, centre ~9 yds off); 3, 4, 10 none (striped, large greens score low: the estimate
stays). The mapper's green edit (BRIEF step 3b) is the fix for 3, 4, 10, 11, 14.

Library pages with estimated greens (would change on a rebuild; none queued except Old Works): old_works (18 holes),
falcon_ridge (8), bethpage_state_park (2 of its 3 holes), colbert_hills, creekmoor, hawktree (1 each). Picture
checks keep a detected green's par-3 box a CHECK ("green outline from the imagery detector"); a mapper green passes.
