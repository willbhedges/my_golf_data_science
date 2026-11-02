# Error budget: which map layer causes the wrong clubs and aims

Built 2026-11-01 22:53Z by `course_data/platform/error_budget.py` (quick decision n=4000, seed 31 for every configuration: common random numbers). Re-run: `python3 course_data/platform/error_budget.py --n 4000` (decisions are cached by hole fingerprint in `error_budget_cache.json`); `--report` rewrites this file from `error_budget.json`.

## Set-up

* **Auto** = the automatic build with the true card (`course_data/packages/<slug>/package.json`, the builds `picks_pipeline.py` scores; Colbert Hills: `library/colbert_hills/package.json`). **Truth** = the same package with every hand-checked layer put in (truth tees, greens, hole line, card, hole numbering; the hand corridor zones over the auto zones inside the traced footprint; the elevation table sampled along the truth tee line).
* **Match** = same club and the two aim points (club carry along the printed aim line) within 10 yds, against the all-truth plan through the same decision. **Regret** = truth-map EV of the configuration's club at its aim point minus the truth plan's EV (strokes, summed over holes; only where the aim point is within 80 yds of the truth's, i.e. on the same hole).
* **+layer** = auto with that one truth layer. **-layer** = truth with that one auto layer (does the auto layer alone break the plan?). Hazard layers are swapped as visible-lie regions (see the module docstring). **routing** = hole numbering (each number gets the auto hole whose green is that truth green, within 25 yds, keeping the auto geometry) + the truth hole line.
* **Headline: 138 par-4/5 tee shots on the 10 courses whose build has the card.** Auto vs all-truth: **102/138 match** (74%), same club 123 (89%), same club or tie 129; total regret 2.654 strokes. 36 misses, of which 7 are reference ties (truth margin < 0.01 strokes). National KC (no web card found, so the build numbered the holes itself: 1/14 match) is reported apart.

## The table (card courses)

| layer | misses fixed (+layer) | of them not a reference tie | share of misses | new misses it causes | regret with +layer | holes wrong with -layer (truth + this auto layer) | regret with -layer |
|---|---|---|---|---|---|---|---|
| *none (auto)* | | | | | 2.654 | 36 | |
| card | 0 | 0 | 0% | 0 | 2.654 | 0 | 0.0 |
| routing | 0 | 0 | 0% | 1 | 2.679 | 0 | 0.003 |
| tees | 15 | 12 | 42% | 6 | 2.544 | 16 | 0.523 |
| greens | 0 | 0 | 0% | 0 | 2.655 | 0 | -0.001 |
| fairway | 4 | 2 | 11% | 1 | 1.879 | 9 | 0.388 |
| trees | 5 | 2 | 14% | 3 | 2.491 | 10 | 0.334 |
| water | 1 | 0 | 3% | 1 | 2.663 | 1 | 0.018 |
| ob | 1 | 1 | 3% | 3 | 2.722 | 3 | 0.1 |
| long_grass | 9 | 8 | 25% | 0 | 0.968 | 10 | 1.158 |
| bunkers | 0 | 0 | 0% | 0 | 2.662 | 2 | 0.028 |
| elevation | 0 | 0 | 0% | 1 | 2.753 | 2 | 0.026 |
| *group frame* (card, routing, tees, greens) | 14 | 12 | 39% | 6 | 2.523 | | |
| *group hazards* (fairway, trees, water, ob, long_grass, bunkers) | 21 | 14 | 58% | 1 | 0.538 | | |

**Residual**: 5 of 36 misses are fixed by no single layer (veenker:3, veenker:12, ellis:15, ellis:18, spirit_hollow:14); of these the two groups fix 2 (ellis:15, ellis:18).

Shares can add to more than 100%: one miss can be fixed by either of two layers.

### All 11 courses, National KC included

| layer | misses fixed (+layer) | of them not a reference tie | share of misses | new misses it causes | regret with +layer | holes wrong with -layer (truth + this auto layer) | regret with -layer |
|---|---|---|---|---|---|---|---|
| *none (auto)* | | | | | 2.654 | 49 | |
| card | 0 | 0 | 0% | 0 | 2.654 | 3 | 0.001 |
| routing | 3 | 2 | 6% | 1 | 2.781 | 3 | 0.16 |
| tees | 15 | 12 | 31% | 6 | 4.053 | 24 | 0.589 |
| greens | 0 | 0 | 0% | 0 | 2.655 | 1 | 0.04 |
| fairway | 4 | 2 | 8% | 1 | 1.879 | 11 | 0.458 |
| trees | 5 | 2 | 10% | 3 | 2.492 | 13 | 0.519 |
| water | 1 | 0 | 2% | 1 | 2.663 | 1 | 0.018 |
| ob | 1 | 1 | 2% | 3 | 2.722 | 3 | 0.144 |
| long_grass | 9 | 8 | 18% | 0 | 0.969 | 10 | 1.158 |
| bunkers | 0 | 0 | 0% | 0 | 2.662 | 2 | 0.029 |
| elevation | 0 | 0 | 0% | 1 | 2.753 | 3 | 0.174 |
| *group frame* (card, routing, tees, greens) | 23 | 20 | 47% | 6 | 2.935 | | |
| *group hazards* (fairway, trees, water, ob, long_grass, bunkers) | 21 | 14 | 43% | 1 | 0.538 | | |

**Residual**: 15 of 49 misses are fixed by no single layer (national_kc:1, national_kc:3, national_kc:7, national_kc:8, national_kc:9, national_kc:10, national_kc:11, national_kc:13, national_kc:15, national_kc:18, veenker:3, veenker:12, ellis:15, ellis:18, spirit_hollow:14); of these the two groups fix 8 (national_kc:1, national_kc:10, national_kc:11, national_kc:13, national_kc:15, national_kc:18, ellis:15, ellis:18).

## Per course

| course | set | tee shots | auto match | same club | regret | misses fixed by (layer: n) |
|---|---|---|---|---|---|---|
| blue_hills | Black | 14 | 14 | 14 | 0.048 | - |
| eagle_knoll | Back | 14 | 12 | 13 | 0.017 | tees: 1, water: 1 |
| gateway_national | Back | 13 | 9 | 11 | 0.425 | long_grass: 3, tees: 1 |
| national_kc | Black | 14 | 1 | 3 | 0.0 | routing: 3 |
| hot_springs_arlington | Gold | 14 | 8 | 12 | 0.13 | trees: 4, tees: 2, ob: 1 |
| pine_dunes | Gold | 14 | 10 | 12 | 0.163 | tees: 4, trees: 1 |
| veenker | Blue | 13 | 9 | 13 | 0.103 | tees: 2 |
| coldwater | Blue | 14 | 9 | 12 | 0.471 | long_grass: 3, fairway: 2, tees: 1 |
| ellis | Blue | 14 | 11 | 12 | 0.375 | fairway: 1 |
| spirit_hollow | Black | 14 | 7 | 10 | 0.893 | long_grass: 3, tees: 3, fairway: 1 |
| colbert_hills | Black/Blue | 14 | 13 | 14 | 0.027 | tees: 1 |

Not scored: mozingo_lake (hand map in screenshot pixels (mozingo/tee_strategy.HOLES), no WGS84 registration)

## Every miss

| hole | truth plan | auto plan | aim apart | regret | fixed by | tee / green err | layer evidence (corridor, sq yds missing / extra) |
|---|---|---|---|---|---|---|---|
| eagle_knoll 4 | Driver -12 | Driver -5 | 10.4 | 0.009 | tees | 9.0 / 0.0 | trees -10/+163 (L40) |
| eagle_knoll 17 | 4-wood +10 (tie) | Driver -25 | 40.3 | 0.0032 | water | 0.0 / 0.0 | trees -668 (L30)/+424 (R21); water -3/+1128 (L28) |
| gateway_national 9 | 4-wood +0 | 2-wood +10 | 14.1 | 0.0987 | long_grass | 0.0 / 0.0 | trees -269 (R46)/+36; long_grass -3507 (R2)/+0 |
| gateway_national 11 | 4-wood +8 | Driver +22 | 25.0 | 0.1961 | long_grass | 0.0 / 0.0 | long_grass -5420 (R2)/+0 |
| gateway_national 13 | Driver +0 | Driver +10 | 10.0 | 0.045 | long_grass | 0.0 / 0.0 | long_grass -2769 (R25)/+0 |
| gateway_national 18 | Driver +18 | Driver +15 | 14.7 | 0.0053 | tees | 14.5 / 0.0 | trees -196 (R46)/+2; long_grass -2634 (L36)/+0 |
| national_kc 1 | 4-wood +2 | None +0 | None | None | groups: frame | None / None |  |
| national_kc 3 | 4-wood +12 | Driver +38 | 796.7 | None | none | 919.1 / 1016.3 | fairway -4020 (R11)/+0; trees -1207 (R40)/+0; ob -510 (R20)/+0; bunkers -177 (L0)/+0 |
| national_kc 5 | Driver -22 | 4-wood +18 | 551.9 | None | routing | 616.9 / 601.5 | trees -3241 (R30)/+32; ob -612 (R17)/+2883 (R32) |
| national_kc 7 | 4-wood +8 | Driver -2 | 1282.6 | None | none | 1290.9 / 1391.7 | trees -225 (R32)/+35; water -231 (R41)/+2 |
| national_kc 8 | 4-wood -10 (tie) | None +0 | None | None | none | None / None |  |
| national_kc 9 | 4-wood -2 | Driver +38 | 1252.0 | None | none | 1225.7 / 1347.6 | fairway -4450 (L0)/+0; trees -204 (L16)/+0; water -2517 (R40)/+0; ob -456 (L44)/+0; bunkers -446 (L33)/+0 |
| national_kc 10 | Driver +8 | Driver +35 | 1005.6 | None | groups: frame | 500.9 / 1489.7 | trees -1338 (L12)/+4 |
| national_kc 11 | Driver -8 | 4-wood +12 | 1266.8 | None | groups: frame | 1609.5 / 1037.8 | fairway -3738 (L7)/+0; trees -890 (R27)/+0 |
| national_kc 12 | 4-wood +10 (tie) | Driver -20 | 964.4 | None | routing | 981.9 / 919.4 | trees -188 (L28)/+2 |
| national_kc 13 | Driver -2 | None +0 | None | None | groups: frame | None / None |  |
| national_kc 15 | Driver -8 | 4-wood +8 | 295.2 | None | groups: frame | 317.6 / 722.6 |  |
| national_kc 17 | 4-wood +8 | Driver +8 | 451.0 | None | routing | 939.4 / 157.9 | trees -1971 (R17)/+8; ob -0/+634 (R46) |
| national_kc 18 | Driver -20 | Driver -38 | 164.7 | None | groups: frame | 59.6 / 259.0 | trees -4104 (R23)/+1; water -1/+206 (L21); ob -0/+3432 (R37) |
| hot_springs_arlington 1 | 4-wood -22 (tie) | Driver -25 | 19.0 | 0.0063 | trees | 1.2 / 1.7 | trees -928 (R12)/+39; ob -0/+385 (R46) |
| hot_springs_arlington 4 | 4-wood -5 | Driver +5 | 25.9 | 0.0338 | trees | 17.6 / 1.8 | trees -1132 (R1)/+105 |
| hot_springs_arlington 9 | Driver +40 | Driver +10 | 36.2 | 0.0231 | tees | 28.1 / 0.0 | trees -579 (L13)/+125 |
| hot_springs_arlington 10 | Driver +0 | Driver +15 | 17.3 | 0.0359 | ob | 8.6 / 2.3 | trees -2837 (L24)/+38; ob -0/+3425 (L38) |
| hot_springs_arlington 13 | Driver +15 (tie) | Driver +5 | 10.1 | 0.0131 | tees, trees | 1.0 / 0.2 | trees -873 (R6)/+17 |
| hot_springs_arlington 18 | Driver +8 | Driver +38 | 30.3 | 0.0093 | trees | 0.7 / 0.0 | trees -990 (R2)/+103 |
| pine_dunes 4 | Driver +2 | Driver -10 | 23.5 | 0.0471 | tees | 20.0 / 2.5 | trees -1321 (L8)/+27 |
| pine_dunes 13 | 4-wood -5 (tie) | 2-wood -5 | 9.2 | 0.0048 | tees, trees | 2.1 / 1.7 | trees -939 (R11)/+59 |
| pine_dunes 15 | Long iron -5 | Driver -22 | 77.1 | 0.0674 | tees | 10.1 / 1.0 | trees -871 (L23)/+86 |
| pine_dunes 18 | 4-wood +22 | 4-wood +28 | 14.0 | 0.0348 | tees | 10.9 / 0.8 | trees -486 (L26)/+0 |
| veenker 3 | 4-wood +20 | 4-wood +5 | 18.5 | 0.0448 | none | 25.7 / 0.0 | fairway -1184 (R20)/+296 (R1); trees -1303 (R0)/+132 |
| veenker 7 | Driver +5 | Driver +2 | 11.2 | -0.0004 | tees | 11.0 / 0.0 | fairway -214 (L5)/+235 (R21); trees -2465 (R1)/+8; water -0/+293 (R45) |
| veenker 10 | Driver -40 | Driver +0 | 46.6 | -0.0123 | tees | 80.8 / 0.0 | fairway -515 (L10)/+844 (L12); trees -2738 (R10)/+863 (L20) |
| veenker 12 | Driver +30 | Driver +40 | 16.6 | 0.0134 | none | 15.8 / 0.0 | fairway -939 (R22)/+915 (L5); trees -910 (R4)/+318 (L5); water -0/+188 (L46); ob -570 (L43)/+107 |
| coldwater 2 | 4-wood +10 | Driver +5 | 19.0 | 0.0473 | long_grass | 29.0 / 0.0 | fairway -172 (R2)/+1092 (L10); trees -1293 (R40)/+0; long_grass -3083 (L31)/+0 |
| coldwater 3 | Driver -35 | Driver -12 | 22.5 | 0.0626 | long_grass | 0.6 / 0.0 | fairway -1003 (R5)/+214 (L3); long_grass -2019 (R32)/+0 |
| coldwater 9 | 4-wood -28 | 4-wood -40 | 12.5 | 0.0231 | fairway | 0.0 / 0.0 | fairway -1515 (L25)/+1504 (R26); trees -150 (L47)/+0; water -166 (R46)/+808 (L9); long_grass -1527 (R25)/+0 |
| coldwater 10 | 4-wood -15 | Driver -8 | 21.4 | 0.2347 | fairway, long_grass | 0.0 / 0.0 | fairway -564 (L24)/+2693 (R6); long_grass -4891 (R31)/+0 |
| coldwater 17 | 4-wood +5 | 4-wood +12 | 17.4 | 0.0176 | tees | 15.5 / 0.0 | fairway -766 (L6)/+268 (R4); water -403 (L34)/+167 (L44); long_grass -3792 (L8)/+0; bunkers -124/+81 |
| ellis 13 | 4-wood -35 (tie) | Long iron +2 | 58.6 | 0.0686 | fairway | 0.0 / 0.0 | fairway -2331 (L28)/+227 (R7); trees -2638 (L5)/+524 (R42); ob -1376 (R34)/+2373 (R13) |
| ellis 15 | 4-wood +12 | Driver +2 | 22.4 | 0.1044 | groups: hazards | 0.0 / 0.0 | fairway -2197 (R8)/+231 (R4); trees -104/+462 (L23); long_grass -1843 (L20)/+0 |
| ellis 18 | Driver -15 | Driver +8 | 22.5 | 0.1243 | groups: hazards | 0.0 / 0.0 | fairway -2461 (L24)/+831 (R32); trees -2294 (R23)/+24; water -0/+418 (R33); bunkers -36/+242 (L0) |
| spirit_hollow 1 | 4-wood -15 | Driver -40 | 39.8 | 0.4591 | long_grass | 25.8 / 1.5 | fairway -3088 (L17)/+377 (L19); trees -1674 (R25)/+501 (L35); long_grass -809 (L41)/+0 |
| spirit_hollow 4 | Driver -12 | Driver -5 | 13.8 | 0.0579 | tees | 10.8 / 3.4 | fairway -1114 (L27)/+802 (R6); trees -372 (R48)/+533 (R34); ob -0/+614 (R48); long_grass -3968 (R26)/+0 |
| spirit_hollow 6 | 4-wood -22 (tie) | Driver -40 | 28.6 | 0.1289 | long_grass | 12.9 / 14.4 | fairway -2074 (L20)/+400 (L16); trees -40/+201 (L41); long_grass -1226 (L8)/+0 |
| spirit_hollow 13 | Driver +5 (tie) | Driver +15 | 10.6 | 0.0256 | tees, fairway | 3.3 / 3.5 | fairway -4477 (L6)/+0; trees -1173 (L42)/+315 (L32); water -250 (R36)/+22 |
| spirit_hollow 14 | 4-wood -12 | 2-wood -40 | 25.3 | 0.0285 | none | 21.8 / 5.4 | fairway -4269 (R10)/+427 (R1); trees -1272 (L17)/+25; water -7/+708 (R33); long_grass -1860 (R32)/+0 |
| spirit_hollow 16 | 4-wood -2 | 4-wood -2 | 11.2 | 0.0064 | tees | 25.5 / 1.7 | fairway -2967 (L14)/+110; trees -2408 (R31)/+34; water -347 (R31)/+0; long_grass -1164 (L43)/+0; bunkers -190 (L2)/+79 |
| spirit_hollow 18 | 4-wood -15 | Driver -12 | 17.0 | 0.1484 | long_grass | 5.7 / 1.5 | fairway -4443 (R6)/+579 (R13); trees -0/+191 (L43); water -99/+3908 (R4); long_grass -4776 (R2)/+0 |
| colbert_hills 1 | Driver -28 | Driver -10 | 35.4 | 0.0287 | tees | 32.0 / 1.8 |  |

Layer evidence: area of that layer in the truth tee shot's landing corridor (180-320 yds along the truth tee line, +/-50 yds) that the truth has and the auto map lacks (-) / the auto map has and the truth lacks (+); L/R n = the mean side of that area, yds left / right of the line.

## Honesty notes

* n = 4000 swings per club and aim, not the scoreboard's 8000: 26 configurations x 152 holes on a shared 4-core box. Every configuration uses the same seed, so a changed pick is a changed map; picks with a margin under 0.01 strokes are marked as reference ties.
* The all-truth plan here is the hand map in the package through the quick decision, for every course. It is not the scoreboard's truth (Spirit Hollow's Bayesian final_decision.json; Veenker / Coldwater / Ellis rough outside the corridor). So the 89% same club here does not compare one to one with PIPELINE.md section 5's 77.5%.
* Elevation has no hand truth: both sides sample the same 3DEP DEM, so the elevation layer only tests the table along the wrong tee line. Colbert Hills' truth has no trees, OB or long grass, so those stay auto there.
* The hand corridor maps cover 150-340 yds of each tee shot. Lies outside the footprint are the auto map's in the truth too, so a layer error outside the corridor is not counted.
* Mozingo Lake is not scored: its hand map is in screenshot pixels. `vision_any/register_mozingo.py` may give the WGS84 registration needed to add it.

## Recommendation

Ranked by what fixing the layer buys (card courses, 138 tee shots, 36 misses, 2.65 strokes of regret):

1. **Long grass first: the auto build has none.** +long_grass fixes 9 misses (8 not ties, 25%) and takes the regret from 2.65 to 0.97 strokes: 64% of all regret, more than any other layer or the whole frame group. In all 43 landing corridors where the hand map has more than 300 sq yds of native / fescue (Gateway 13 of 13, Spirit Hollow 13, Coldwater 12, Ellis 3), the auto map has none. The only long grass in the 10 packages is 3 OSM polygons on Coldwater. The packages' vision note reads `LightGBM P(native) >= None`: the native classifier's threshold is None, so vision_any/2 emits no native polygons. This looks like a configuration bug, not a modelling limit. Check `vision_any/gapfill.py` / the v2 model's native threshold, then re-run this budget. Failure pattern: "native rough missing on every links / prairie corridor; the plan hits Driver into fescue (Gateway 9, 11, 13; Spirit Hollow 1, 6, 18; Coldwater 2, 3)".
2. **Tees: the most misses, the fewest strokes.** +tees fixes 15 misses (12 not ties, 42%), and truth with only the auto tees is wrong on 16 holes. It recovers only 0.11 strokes, though: a moved tee mostly shifts the aim 10-30 yds. 22 of 138 scored tees are more than 10 yds off (median 1 yd). The fixed holes are 9-32 yds off along the tee complex: Pine Dunes 4 (20), Hot Springs 9 (28), Spirit Hollow 16 (25), Colbert 1 (32), Veenker 10 (81). That is the wrong box on a long or split tee complex for the back set. Caveat: the truth tee alone breaks 6 holes the auto plan had right (Blue Hills 10, Hot Springs 7, Pine Dunes 5, Veenker 9, Spirit Hollow 8 and 17). Three of these also break with only the auto trees, so the auto tree edge and the auto tee offset each other there. Fix tees together with trees and re-measure.
3. **Trees: the canopy edge sits about 5 yds off the hand tree line.** +trees fixes 5 (Hot Springs 1, 4, 13, 18; Pine Dunes 13), and truth with only the auto trees is wrong on 10 holes. In the corridors the hand map has a median 680 sq yds of trees the auto map lacks, against 60 the other way. Over a 140-yd corridor that is a strip about 5 yds wide on the fairway side. The lidar canopy (HAG > 2.5 m, +3 m buffer) stops short of where the golfer's "in the trees" starts.
4. **Fairway** (+4, regret 2.65 -> 1.88): the OSM fairway is narrower than the traced one on Spirit Hollow (3,000-4,500 sq yds of fairway missing per corridor), and is on the wrong side on Coldwater 9.

Not worth work now: card, routing, greens (0 misses on the card courses), water, OB, bunkers (1 each, OB breaks as many as it fixes), elevation (fixes 0, breaks 1). The one routing failure is National KC: no web card, so the build numbered the holes itself and 13 of 14 holes are wrong. That is a card problem (typed card / card search), not a map layer. Residual: 5 misses no single layer fixes. Ellis 15 and 18 need the hazard layers together; Veenker 3 and 12 and Spirit Hollow 14 need tee + trees + fairway at once.

<!-- hand-written follow-ups below: kept by --report / re-runs -->
## Follow-up 2026-11-02: is the missing long grass a configuration bug? No.

**Root cause.** `model_v2/model.json` has `native_thr: null` on purpose. Four held-out selections each chose
"no long grass" over every threshold: decision calibration (`vision_any/v2_decision_calibration.md`), the 3-course
holdout (`v2_holdout_calibration.md`), and leave-one-course-out rev 1 and rev 2 (`v2_longgrass_cv.md`,
`v2_longgrass_cv_rev2.md`; rev 2 out of fold: 129/151 with long grass vs 130/151 without). `v2_model.infer` reads
None as "off". So no model file is missing and no fit failed to save. The bug is only in the package note: it
printed `LightGBM P(native) >= None`, which looks like a lost setting. Fixed: `v2_model.check_native_settings`
refuses a None threshold unless `settings.native_off` says why, and the note now reads "no long grass (native)
layer: <reason>". Test: `vision_any/test_v2.py::test_native_threshold_none_must_be_explained`. The packages pick up
the new note on their next vision build. Their zones are unchanged.

**What a threshold would do (measured).** `vision_any/v2_longgrass_eb_build.py` thresholds the committed product
P(native) (band 2 of `layers_v2.tif`; model trained on Spirit Hollow + Mozingo only, so out of sample on every
course below). It applies `v2_model.native_mask`, strict mode, and rebuilds each package with
`v2_calibrate.rebuild_package`. `platform/error_budget_variant.py` then runs this budget's configs (n = 4000,
seed 31). The threshold the existing pixel method picks on the training courses (mean of the Spirit Hollow and
Mozingo leave-one-hole-out IoU bests) is 0.04. The others are a sensitivity sweep, not chosen on these courses.
The control (the same rebuild with no long grass) reproduces the committed rows exactly on the 7 courses below.

The 7 card courses every variant finished: Blue Hills, Eagle Knoll, Gateway, Hot Springs, Pine Dunes, Veenker,
Coldwater, 96 tee shots. Ellis and Spirit Hollow were not finished for every threshold and are left out.

| auto long grass | auto match | same club | regret (strokes) | Hot Springs / Pine Dunes / Veenker match |
|---|---|---|---|---|
| none (committed = control) | **71/96** | 86 | **1.36** | 8 / 10 / 9 |
| P >= 0.04 (training-course pick) | 47/96 | 66 | 4.84 | 0 / 6 / 5 |
| P >= 0.3 | 63/96 | 79 | 3.18 | 4 / 8 / 8 |
| P >= 0.5 | 61/96 | 78 | 2.58 | 2 / 10 / 8 |
| hand long grass (+long_grass) | 77/96 | - | 0.51 | |

**Precision vs hand truth, per landing corridor** (180-320 yds, +/-50 yds, these 7 courses + National KC, all held
out):

| threshold | corridors with hand native > 300 yd2: IoU / precision / recall (pooled), median corridor IoU | corridors with no hand native: auto long grass, corridors with > 300 yd2 of it |
|---|---|---|
| 0.04 | 0.41 / 0.50 / 0.69, median 0.39 (n = 29) | 247,000 yd2; 73 of 78 |
| 0.3 | 0.25 / 0.57 / 0.30, median 0.17 (n = 28) | 101,000 yd2; 47 of 79 |
| 0.5 | 0.18 / 0.61 / 0.21, median 0.14 (n = 28) | 59,000 yd2; 26 of 79 |

Pooled over all corridors, precision is 0.14-0.17 at every threshold: 83-86 % of the auto long grass sits where the
hand map has mown rough or nothing. The model's P(native) is high on mown rough of parkland courses. At P >= 0.5 it
calls 85 % of Pine Dunes' and 42 % of Hot Springs' eligible area native, and the hand maps have none on either
course. That costs more than the missing fescue: regret 1.36 -> 2.58 at the best threshold, against 0.51 with the
true layer.

**Decision: long grass stays off.** No package was regenerated and no vision workflow was run: the cached rasters
were enough, and every candidate layer makes the plans worse. The error budget's 64 % stays as a target for a
better classifier, not a quick fix. That classifier needs to separate native from mown rough per course: e.g. a
per-course "mown turf" reference, leaf-off / peak-season NAIP contrast, or a links / prairie gate with a better
signal than share of outline. Score it with `error_budget_variant.py` (precision on the no-native corridors is the
number to watch).

Not verified: Ellis and Spirit Hollow at every threshold (runs stopped at the time budget; partial rows in the
scratch run only); the relaxed mode, dmin and gate settings (covered by `v2_longgrass_cv_rev2.md` with the
corridor-focused model); Colbert Hills (no vision layers; its truth has no long grass).

## Tees and trees (follow-up, 2026-11-02)

The two fixes recommended above, scored the same way: the 10 packages had only their tee layer and/or their tree layer rebuilt offline (`platform/rebuild_tees_trees.py`: the S2 tee stage on the package's raw OSM + DEM pads, or the vision_any/2 trees with buffer k re-clipped by `vision_any/gapfill.py`; everything else as committed), then `error_budget.py --auto-dir DIR --configs ...` with n = 4000 and seed 31 (a fresh run on the committed Eagle Knoll package gives exactly the committed picks). Colbert Hills has no raw OSM in the repo, so its tees stay as built (its hole 1 is not re-run). Per-shot results: `error_budget_tees_trees.json`.

**Card courses, 138 tee shots (auto vs all-truth):**

| variant | match | same club | same club or tie | regret | tees > 10 yds off | fixed / broken vs before |
|---|---|---|---|---|---|---|
| before (committed) | 102 | 123 | 129 | 2.654 | 22 | |
| **tees: new rule (adopted)** | **105** | 122 | 128 | 2.672 | **16** | 4 / 1 |
| trees: buffer 0 m | 102 | 122 | 127 | 2.591 | 22 | 4 / 4 |
| trees: buffer +1 m (edge optimum) | 100 | 120 | 126 | 2.603 | 22 | 5 / 7 |
| tees + trees +1 m | 105 | 119 | 125 | 2.644 | 16 | 9 / 6 |

**Tees (adopted; `tees/localize.py`, `platform/package.py`).** The misses were not a wrong box on most of the named holes but the right box drawn short of the real back tee: the card yardage sits 6-18 yds behind the mapped box and the hand tee sits at the card yardage (Pine Dunes 4: tagged Gold box 437-453 yds, card 463, hand tee 465; Veenker 12, Coldwater 17, Gateway 18, Hot Springs 10 the same on untagged boxes). Two rule changes: (1) a card more than 5 yds outside the chosen pad's extent moves the point off the pad along its axis by the excess, at most 20 yds (`beyond_free_yd` / `beyond_max_yd`; within 5 yds it stays clamped: on Blue Hills 2, 6, 10 and Eagle Knoll 1, 9, 14 the card is 2-5 yds past the box and the hand tee is on the box); (2) an OSM box tagged with the set's colour is placed on its axis at the card yardage (same rule), the tagged box nearest the card when several, not at its centroid (all 6 Pine Dunes tagged tees that were 7-20 yds short are now 0.4-7 yds off). Tees more than 10 yds off 22 -> 16 of 138, median 1.0 -> 0.9 yds; one tee worse by more than 3 yds (Pine Dunes 1: 1.5 -> 6.0, card 391 inside a box whose hand tee is at 385). Plans: fixed Eagle Knoll 4, Pine Dunes 4 and 18, Coldwater 17; broken Pine Dunes 5 (the tee went from 7.6 to 1.3 yds off: one of the holes the truth tee alone breaks, see above); Veenker 12 changes club (Driver -> 4-wood, regret +0.09), which is most of the regret change. `tees/eval_localize.py` on its own sets: generalize train (OSM hidden) <= 10 yds 707 -> 711 of 778, p90 8.4 -> 7.6; test split (scored once) 441 -> 446 of 513; Mozingo 17 -> 18 of 18; Spirit Hollow hand map unchanged (8 of 16). The 5 is from the hand-truth tees (train split: 3 is one placement better, but breaks Hot Springs 3 on the hand truth).

Not fixed, with the reason:
* Veenker 10 (81 yds): the Veenker / Coldwater hand corridors are framed on an older package's own Blue tee (`tees/eval_localize.md`), so they hold no independent tee truth: the hand tee is 568 yds from the green, the card says 520, and the box at 518 yds is chosen.
* Hot Springs 9 (28): two lidar pads both fit Gold 565 / Blue 556; the chosen one is 28 yds off the hole line, the hand tee is on the line. A lateral-offset cost (off_free 10-20 yds, 0.05-0.2 / yd) was tried and rejected: it fixes this hole and Spirit Hollow 16 but breaks 4-6 others (Gateway 2 and 8, Veenker 16, Spirit Hollow 9; 15 -> 16-20 tees over 10 yds).
* Spirit Hollow 16 (26): the hand Black tee measures 389 yds against a 378 card; the box at the card yardage is the one 21 yds left. Spirit Hollow 1, 14, 17 (22-29): across the line, the hand point is outside every OSM box (`eval_localize.md` A).
* Colbert Hills 1 (32): not re-run (no raw OSM offline). Diagnosis from the package: the card (590) is 26 yds past the back box's back edge (564), beyond the localizer's 25-yd limit, so Black/Blue walks back 80 yds behind the line start; the hand tee is on that back box. A "back set falls back to the back-most own box" rule is the candidate; not implemented (nothing offline to verify it on). `sanity.py` walk-back caps and `tees/cardless.py` anchoring are unchanged.

**Trees (calibrated, not adopted; `vision_any/v2_treeline_handcal.md`).** The 11 hand-truth courses are the only georeferenced hand tree lines, so the edge was calibrated leave-one-course-out on them (10 courses; Colbert Hills has no hand trees): canopy threshold 1.5-3 m x buffer -1..+8 m, scored inside the hand landing corridors against the trees the product sees. Every held-out fold picks buffer +1 m (HAG 2.5 and 3.0 tie): held-out IoU 0.561 -> 0.581, median per corridor 1515 / 285 -> 716 / 786 sq yds missing / extra (with -1 m the auto edge is 0-5 yds short of the hand line, median 1.6 yds over the 9 courses other than Spirit Hollow, which is an outlier at every setting). In this error budget the median tree area missing per corridor goes 677 -> 383 sq yds (extra 58 -> 196), and the +1 m layer alone in the truth breaks 4 holes (-1 m: 10; regret 0.334 -> 0.258): the layer itself is closer to the hand map. But the auto plans get worse: +1 m fixes the 5 holes the hand trees fixed (Hot Springs 1, 13, 18; Pine Dunes 13; Spirit Hollow 13; 4 of them reference ties) and breaks 7 that were right (Blue Hills 10 and 18, Hot Springs 6, Pine Dunes 5, Veenker 14, Ellis 10, Spirit Hollow 9; 6 not ties), each by making the auto plan more conservative (Driver -> 4-wood / 2-wood). Buffer 0 m is neutral on matches (102) with the lowest regret (2.591). A decision-level leave-one-course-out over k in {-1, 0, +1} (choose on 8 card courses, score the ninth) gives 86 matches vs 89 for keeping -1 m. So `model_v2` keeps -1 m: the short edge offsets other auto-layer errors (the hand corridors' long grass and wider fairways), as the tees/trees interaction above suggested. Re-measure when the long-grass or fairway layer changes: `python3 course_data/platform/rebuild_tees_trees.py --out DIR --layers tees,trees --k 1` then `python3 course_data/platform/error_budget.py --auto-dir DIR`.

**Not done here:** the committed packages are not re-teed (the next package build picks up the rule; `rebuild_tees_trees.py --layers tees` does it offline); the full 26-configuration table was not re-run for the new tees (only auto / truth / +-tees / +-trees), so the tables above this section are the pre-fix budget.

## Fairway (follow-up, 2026-11-02)

**Quality per landing corridor** (`platform/fairway_quality.py` -> `fairway_quality.json`; 180-330 yds along the truth tee line, +/-50 yds; fairway = visible fairway + first_cut of the auto map as numbered to the truth routing vs the truth stack; 165 corridors on the 11 error-budget courses + Tomahawk Hills and Wakonda from `truth_sets_v2`):

| source of the auto fairway | corridors | pooled IoU | median IoU | median width error (auto - truth) | median sq yds missing / extra |
|---|---|---|---|---|---|
| OSM, independent hand trace (Spirit Hollow, Ellis, Veenker, Coldwater) | 55 | 0.63 | 0.65 | -6.6 yds | 1568 / 448 |
| - Spirit Hollow | 14 | 0.52 | 0.53 | -23.0 | 3632 / 392 |
| - Ellis | 14 | 0.61 | 0.58 | -11.2 | 1962 / 339 |
| - Veenker | 13 | 0.72 | 0.73 | -1.8 | 787 / 321 |
| - Coldwater | 14 | 0.72 | 0.73 | **+5.8** (OSM wider) | 592 / 1456 |
| OSM, hand trace that started from the OSM fairway (Blue Hills, Eagle Knoll, Gateway, Pine Dunes, National KC, Colbert, Tomahawk, Wakonda) | 106 | 0.999 | 0.999 | 0.0 | 3 / 3 |
| none (OSM has no fairway, hand map has one: National KC 3, 9, 11) | 3 | 0 | 0 | -27 | 4020 / 0 |
| vision / segment | 0 | | | | |

* **No package fairway comes from vision.** Every auto fairway zone in the 10 packages is OSM; `segment` gap-fill ran only on Spirit Hollow and Veenker (+1 zone, outside the corridors) and not at all on Coldwater / Ellis (no `segment.geojson`); vision_any/2 makes no fairway class. Hot Springs has no OSM fairway on 13 of 14 corridors and its hand map has none either ("dormant Bermuda, fairway not separable on NAIP"), so missing fairway there is unscored.
* **Only 4 courses have independent fairway truth.** The holes_truth / truth_sets_v2 traces start from the OSM fairway (`trace.py` `auto(..., fairway=True)`) and were corrected only where visibly wrong, so their IoU 0.999 says "OSM was not visibly wrong", not "OSM width is right". Spirit Hollow's hand map traces first cut separately (8.5 yds per side); the others trace one fairway.
* No corridor is "wrong side" (IoU < 0.25 with both > 1500 sq yds). Coldwater 9 is shifted 12 yds right (IoU 0.63); Ellis 13 15 yds, Ellis 18 11 yds.

**The fix tried: widen the OSM fairway by a band measured from the course's own NAIP** (`platform/fairway_edge.py`, `platform/fairway_band.py`, `rebuild_tees_trees.py --layers fairway`). Per course, a Fisher direction on every NAIP year (4 bands + 3x3 texture of green / NIR) between OSM fairway (>= 4 m inside) and rough (25-40 m outside, HAG <= 1 m, not OSM features) scores 1 m rings outward from the OSM edge (trees, bunkers, water, greens excluded); the band is where the ring score drops below theta (0 below 2 yds = grid noise, cap 15 m), then added as fairway (or first_cut) only over rough (every other zone of the hole cut out). No hand map is used. Edge extension at theta 0.5: Spirit Hollow 8.2 yds, Ellis 5.9, Coldwater 4.8, Wakonda 4.8, Pine Dunes 2.4, Veenker 0.8, Blue Hills 0.4, Gateway 0.3, Eagle Knoll / National KC / Tomahawk 0. The detector separates the two narrow-OSM courses from the right-OSM ones, except Coldwater (a false positive: the hand fairway there is narrower than OSM).

Leave-one-course-out on the 4 independent courses (corridor IoU at the band the held-out course gets, theta chosen on the other 3): Spirit Hollow 0.52 -> 0.65, Ellis 0.61 -> 0.71, Veenker 0.73 -> 0.74, Coldwater 0.72 -> 0.58; a single global band (3-6 yds, chosen the same way) is worse on 3 of 4 (0.60 / 0.68 / 0.71 / 0.65). theta = 0.5 (the midpoint, LOCO picks 0.3-0.6; all-4 optimum 0.45 is within 0.001) is used below. Per-hole profiles correlate only 0.3-0.4 with the per-corridor best buffer, and pixel-level region growing from the score map (theta 0.5 / 0.6, <= 15 m) is no better than the per-course band (Spirit Hollow 0.62, Ellis 0.70, Coldwater 0.63-0.66), so the band is per course.

**Error budget** (10 card courses, 138 tee shots, n = 4000, seed 31; only Pine Dunes, Coldwater, Ellis, Spirit Hollow change, the others' rows are the baseline's; tee positions reproduce `error_budget_tees_trees.json` within 0.2 yds; per shot: `error_budget_fairway.json`):

| variant | match | same club | regret | fixed / broken vs its baseline |
|---|---|---|---|---|
| before (committed) | 102 | 123 | 2.654 | |
| fairway band (fairway lie) | 99 | 123 | 2.735 | 0 / 3 (Coldwater 7, Ellis 6, Spirit Hollow 9) |
| fairway band as first_cut | 95 | 118 | 2.962 | 0 / 7 |
| hand fairway (+fairway, for scale) | 105 | | 1.879 | 4 / 1 |
| tees (new rule, adopted) | 105 | 122 | 2.672 | |
| tees + fairway band | 101 | 118 | 3.164 | 2 / 6 |
| tees + trees +1 m | 105 | 119 | 2.644 | |
| tees + trees +1 m + fairway band | 99 | 115 | 2.974 | 0 / 6 |

**Not adopted.** The band brings the layer closer to the hand map on the two narrow-OSM courses but moves none of the plans the hand fairway fixes: Spirit Hollow 1 (regret 0.46 -> 0.42, hand 0.14), 6 (0.13 -> 0.13, hand 0.004), Ellis 13, 18, Coldwater 9, 10 keep their picks. Those gains come from the fairway's shape on one side (Spirit Hollow 1 / 6 / 13: 2,000-4,900 sq yds missing on the left; Ellis 13: 15 yds right; Coldwater 10: 2,700 sq yds extra on the right), not a uniform width. The band instead nudges aims across the 10-yd line on holes that were right (Ellis 6 aim +2.5 -> +5, Spirit Hollow 9, Coldwater 7) and on Spirit Hollow 14 turns 2-wood into the truth's 4-wood but at an aim 40 yds left (regret 0.03 -> 0.11). As first cut it is worse (Pine Dunes 10, 11, 17 break at 2.4 yds). With the new tees the band breaks 6 and fixes 2 (Pine Dunes 5, Spirit Hollow 13); with tees + trees +1 m it breaks 6 and fixes 0, so no error cancellation in favour of the band: the narrow OSM fairway and the short tree edge are not offsetting each other in the corridors the band touches. The packages keep the OSM fairway as mapped (`--fw-*` is off by default; nothing in the build calls `fairway_band`).

What would move it (not done here): a per-side fairway outline (the score map along each side of the hole line, with lidar smoothness / mowing-pattern texture at 0.3-0.6 m rather than the 1 m stack); a "fairway too wide" test for Coldwater-like courses (the band only widens); a vision fairway where OSM has none (National KC 3, 9, 11; Hot Springs, whose hand map has no fairway to score against); and more independent fairway truth: today 4 courses / 55 corridors, so any calibration is thin. Fixed on the way: `platform/package.par3_haz` crashed on a `first_cut` zone (KeyError).
