# Auto-course acceptance: Spirit Hollow (package.json as built)

Same club (Driver / 2-wood / 4-wood) on **56%** of 16 tee shots (bar 80%). Tee within 10 yds: 38%; green within 10 (or the traced green's own rounding spread): 75%; length within 5: 75%. Median tee error 12.5 yds, green 6.3 yds.

Decision regret (strokes lost on the hand map by playing the auto map's club): mean 0.0107, max 0.094 (bar mean <= 0.02, max <= 0.05): not met.

Mean landing-zone IoU by class: fairway 0.57, rough 0.23, recovery 0.25, native 0.14, water 0.32, sand 0.44, ob 0.13

Holes passing every check: none

| hole | len err | tee err | green err (traced +/-) | registration | club traced / auto | IoU water | IoU ob | IoU trees | IoU fairway | failed |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | +0 | 48.7 | 43.5 (+/-2 along, +/-4 lat) | lie_raster_fit (dice 0.738) | 4-wood / 4-wood | - | - | 0.359 | 0.682 | tee, green, iou_recovery |
| 2B | -2 | 53.8 | 90.2 (+/-6 along, +/-8 lat) | lie_raster_fit (dice 0.378) | Driver / 2-wood | 0.0 | - | 0.13 | 0.68 | tee, green, iou_water, iou_recovery, club |
| 2F | +0 | 1.2 | 4.4 (+/-4 along, +/-8 lat) | naip_registration (ecc 0.399) | Driver / Driver | 0.474 | 0.395 | 0.081 | 0.432 | iou_water, iou_ob, iou_recovery |
| 4 | +12 | 11.2 | 4.8 (+/-4 along, +/-32 lat) | naip_registration (ecc 0.363) | Driver / Driver | - | - | 0.0 | 0.439 | tee, length, iou_recovery |
| 5 | +0 | 11.9 | 6.3 (+/-2 along, +/-16 lat) | naip_registration (ecc 0.468) | 4-wood / 4-wood | - | - | 0.0 | 0.665 | tee, iou_recovery |
| 6 | +0 | 13.1 | 8.2 (+/-2 along, +/-5 lat) | naip_registration (ecc 0.34) | Driver / Driver | - | 0.0 | 0.0 | 0.548 | tee, iou_ob, iou_recovery |
| 8 | +8 | 24.7 | 15.8 (+/-2 along, +/-9 lat) | lie_raster_fit (dice 0.551) | 4-wood / 4-wood | - | 0.0 | 0.0 | 0.636 | tee, green, length, iou_ob, iou_recovery |
| 9B | +11 | 5.5 | 1.6 (+/-2 along, +/-2 lat) | naip_registration (ecc 0.382) | 2-wood / Driver | 0.72 | - | 0.556 | 0.636 | length, iou_recovery, club |
| 9F | -8 | 9.0 | 2.9 (+/-2 along, +/-2 lat) | naip_registration (ecc 0.443) | 4-wood / 4-wood | 0.143 | - | 0.296 | 0.5 | length, iou_water, iou_recovery |
| 10 | +0 | 5.4 | 7.8 (+/-4 along, +/-7 lat) | naip_registration (ecc 0.416) | 4-wood / Driver | 0.474 | - | 0.019 | 0.675 | iou_water, iou_recovery, club |
| 11 | +0 | 3.4 | 5.1 (+/-1 along, +/-4 lat) | naip_registration (ecc 0.37) | 4-wood / 4-wood | 0.136 | - | 0.303 | 0.336 | iou_water, iou_recovery |
| 13 | +2 | 6.4 | 4.4 (+/-2 along, +/-8 lat) | lie_raster_fit (dice 0.5) | Driver / 4-wood | 0.811 | - | 0.429 | 0.471 | iou_recovery, club |
| 14 | +0 | 23.3 | 6.3 (+/-2 along, +/-6 lat) | naip_registration (ecc 0.352) | 4-wood / Driver | 0.357 | - | 0.74 | 0.469 | tee, iou_water, club |
| 16 | +0 | 19.2 | 7.2 | lie_raster_fit (dice 0.454) | 2-wood / 4-wood | 0.0 | - | 0.382 | 0.683 | tee, iou_water, iou_recovery, club |
| 17 | +0 | 28.8 | 2.7 (+/-3 along, +/-25 lat) | naip_registration (ecc 0.467) | 2-wood / Driver | - | - | 0.6 | 0.712 | tee, iou_recovery, club |
| 18 | +5 | 50.3 | 69.4 (+/-4 along, +/-7 lat) | lie_raster_fit (dice 0.421) | Driver / Driver | 0.098 | - | 0.167 | 0.549 | tee, green, iou_water, iou_recovery |

Par 3s (centre distance):

| hole | traced | auto | err | hazards traced | hazards auto |
|---|---|---|---|---|---|
| 7 | 159 | 154 | -5 | {'left': 'bunker', 'right': 'bunker', 'short': 'rough', 'long': 'native'} | {'left': 'bunker', 'right': 'bunker', 'short': 'rough', 'long': 'rough'} |
| 12 | 177 | 186 | +9 | {'left': 'native', 'right': 'bunker', 'short': 'rough', 'long': 'rough'} | {'left': 'rough', 'right': 'bunker', 'short': 'rough', 'long': 'rough'} |
| 3 | 148 | 148 | +0 | {'left': 'trees', 'right': 'rough', 'short': 'water', 'long': 'rough'} | {'left': 'trees', 'right': 'rough', 'short': 'rough', 'long': 'trees'} |
| 15 | 134 | 130 | -4 | {'left': 'rough', 'right': 'native', 'short': 'water', 'long': 'bunker'} | {'left': 'rough', 'right': 'rough', 'short': 'water', 'long': 'bunker'} |

IoU is on the landing-zone grid (220-340 yds, +/-45) in the traced frame after registration; classes absent from both maps are omitted. Trees are traced at the trunks by hand and are unmapped in OSM, so `recovery` IoU is expected to be the weakest until the imagery gap-fill lands.
