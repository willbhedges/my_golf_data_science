# Auto-course acceptance: Spirit Hollow (package.json as built)

Same club (Driver / 2-wood / 4-wood) on **56%** of 16 tee shots (bar 80%). Tee within 10 yds: 25%; green within 10 (or the traced green's own rounding spread): 75%; length within 5: 12%. Median tee error 26.35 yds, green 6.3 yds.

Decision regret (strokes lost on the hand map by playing the auto map's club): mean 0.0179, max 0.1045 (bar mean <= 0.02, max <= 0.05): not met.

Mean landing-zone IoU by class: fairway 0.58, rough 0.17, recovery 0.14, native 0.09, water 0.32, sand 0.39, ob 0.20

Holes passing every check: none

| hole | len err | tee err | green err (traced +/-) | registration | club traced / auto | IoU water | IoU ob | IoU trees | IoU fairway | failed |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | -22 | 58.4 | 41.6 (+/-2 along, +/-4 lat) | lie_raster_fit (dice 0.732) | Driver / 4-wood | - | - | 0.216 | 0.668 | tee, green, length, iou_recovery, club |
| 2B | -102 | 40.6 | 215.4 (+/-6 along, +/-8 lat) | lie_raster_fit (dice 0.388) | Driver / Driver | 0.097 | - | 0.0 | 0.672 | tee, green, length, iou_water, iou_recovery |
| 2F | -13 | 99.1 | 4.4 (+/-4 along, +/-8 lat) | naip_registration (ecc 0.399) | Driver / Driver | 0.333 | 0.593 | 0.091 | 0.503 | tee, length, iou_water, iou_ob, iou_recovery |
| 4 | +12 | 10.0 | 4.8 (+/-4 along, +/-32 lat) | naip_registration (ecc 0.363) | Driver / Driver | - | - | 0.0 | 0.439 | length, iou_recovery |
| 5 | -13 | 16.3 | 6.3 (+/-2 along, +/-16 lat) | naip_registration (ecc 0.468) | Driver / 4-wood | - | - | 0.0 | 0.665 | tee, length, iou_recovery, club |
| 6 | -13 | 21.7 | 8.2 (+/-2 along, +/-5 lat) | naip_registration (ecc 0.34) | Driver / Driver | - | 0.0 | 0.0 | 0.558 | tee, length, iou_ob, iou_recovery |
| 8 | +8 | 22.8 | 15.0 (+/-2 along, +/-9 lat) | lie_raster_fit (dice 0.518) | 4-wood / 4-wood | - | 0.0 | 0.0 | 0.659 | tee, green, length, iou_ob, iou_recovery |
| 9B | -34 | 82.2 | 1.6 (+/-2 along, +/-2 lat) | naip_registration (ecc 0.382) | 4-wood / 4-wood | 0.72 | - | 0.12 | 0.569 | tee, length, iou_recovery |
| 9F | -8 | 9.0 | 2.9 (+/-2 along, +/-2 lat) | naip_registration (ecc 0.443) | 4-wood / 4-wood | 0.146 | - | 0.079 | 0.401 | length, iou_water, iou_recovery |
| 10 | -19 | 22.2 | 7.7 (+/-4 along, +/-7 lat) | naip_registration (ecc 0.416) | 4-wood / Driver | 0.448 | - | 0.021 | 0.695 | tee, length, iou_water, iou_recovery, club |
| 11 | -10 | 8.1 | 5.2 (+/-1 along, +/-4 lat) | naip_registration (ecc 0.37) | 4-wood / 4-wood | 0.127 | - | 0.241 | 0.408 | length, iou_water, iou_recovery |
| 13 | +2 | 5.7 | 5.0 (+/-2 along, +/-8 lat) | lie_raster_fit (dice 0.432) | Driver / 4-wood | 0.782 | - | 0.0 | 0.528 | iou_recovery, club |
| 14 | -25 | 35.7 | 6.3 (+/-2 along, +/-6 lat) | naip_registration (ecc 0.352) | 2-wood / Driver | 0.476 | - | 0.656 | 0.475 | tee, length, iou_water, club |
| 16 | -10 | 43.2 | 6.3 | lie_raster_fit (dice 0.462) | 2-wood / 4-wood | 0.0 | - | 0.329 | 0.691 | tee, length, iou_water, iou_recovery, club |
| 17 | -8 | 29.9 | 2.6 (+/-3 along, +/-25 lat) | naip_registration (ecc 0.467) | Driver / Driver | - | - | 0.209 | 0.772 | tee, length, iou_recovery |
| 18 | +5 | 47.2 | 72.7 (+/-4 along, +/-7 lat) | lie_raster_fit (dice 0.431) | 4-wood / Driver | 0.025 | - | 0.217 | 0.557 | tee, green, iou_water, iou_recovery, club |

Par 3s (centre distance):

| hole | traced | auto | err | hazards traced | hazards auto |
|---|---|---|---|---|---|
| 7 | 159 | 154 | -5 | {'left': 'bunker', 'right': 'bunker', 'short': 'rough', 'long': 'native'} | {'left': 'bunker', 'right': 'bunker', 'short': 'rough', 'long': 'rough'} |
| 12 | 177 | 184 | +7 | {'left': 'native', 'right': 'bunker', 'short': 'rough', 'long': 'rough'} | {'left': 'rough', 'right': 'bunker', 'short': 'rough', 'long': 'rough'} |
| 15 | 134 | 144 | +10 | {'left': 'rough', 'right': 'native', 'short': 'water', 'long': 'bunker'} | {'left': 'rough', 'right': 'native', 'short': 'water', 'long': 'native'} |

IoU is on the landing-zone grid (220-340 yds, +/-45) in the traced frame after registration; classes absent from both maps are omitted. Trees are traced at the trunks by hand and are unmapped in OSM, so `recovery` IoU is expected to be the weakest until the imagery gap-fill lands.
