# Auto-course acceptance: Spirit Hollow (package.json as built)

Same club (Driver / 2-wood / 4-wood) on **69%** of 16 tee shots (bar 80%). Tee within 10 yds: 38%; green within 10 (or the traced green's own rounding spread): 75%; length within 5: 75%. Median tee error 12.5 yds, green 6.3 yds.

Decision regret (strokes lost on the hand map by playing the auto map's club): mean 0.0097, max 0.1134 (bar mean <= 0.02, max <= 0.05): not met.

Mean landing-zone IoU by class: fairway 0.57, rough 0.26, recovery 0.30, native 0.00, water 0.31, sand 0.42, ob 0.19

Holes passing every check: none

| hole | len err | tee err | green err (traced +/-) | registration | club traced / auto | IoU water | IoU ob | IoU trees | IoU fairway | failed |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | +0 | 48.7 | 43.5 (+/-2 along, +/-4 lat) | lie_raster_fit (dice 0.738) | 4-wood / 4-wood | - | - | 0.391 | 0.682 | tee, green, iou_recovery |
| 2B | -2 | 53.8 | 90.2 (+/-6 along, +/-8 lat) | lie_raster_fit (dice 0.379) | Driver / Driver | 0.0 | 0.0 | 0.182 | 0.68 | tee, green, iou_water, iou_ob, iou_recovery |
| 2F | +0 | 1.2 | 4.4 (+/-4 along, +/-8 lat) | naip_registration (ecc 0.399) | Driver / Driver | 0.474 | 0.147 | 0.047 | 0.432 | iou_water, iou_ob, iou_recovery |
| 4 | +12 | 11.2 | 4.8 (+/-4 along, +/-32 lat) | naip_registration (ecc 0.363) | Driver / Driver | - | - | 0.0 | 0.439 | tee, length, iou_recovery |
| 5 | +0 | 11.9 | 6.3 (+/-2 along, +/-16 lat) | naip_registration (ecc 0.468) | 4-wood / 4-wood | - | - | 0.083 | 0.665 | tee, iou_recovery |
| 6 | +0 | 13.1 | 8.2 (+/-2 along, +/-5 lat) | naip_registration (ecc 0.34) | Driver / 2-wood | - | - | 0.4 | 0.548 | tee, iou_recovery, club |
| 8 | +8 | 24.5 | 16.3 (+/-2 along, +/-9 lat) | lie_raster_fit (dice 0.563) | 4-wood / Driver | - | 0.429 | - | 0.631 | tee, green, length, iou_ob, club |
| 9B | +11 | 8.6 | 1.6 (+/-2 along, +/-2 lat) | naip_registration (ecc 0.382) | 2-wood / Driver | 0.693 | - | 0.5 | 0.636 | length, iou_recovery, club |
| 9F | -8 | 9.0 | 2.9 (+/-2 along, +/-2 lat) | naip_registration (ecc 0.443) | 4-wood / 4-wood | 0.167 | - | 0.348 | 0.5 | length, iou_water, iou_recovery |
| 10 | +0 | 5.4 | 7.8 (+/-4 along, +/-7 lat) | naip_registration (ecc 0.416) | 4-wood / 4-wood | 0.419 | - | 0.019 | 0.675 | iou_water, iou_recovery |
| 11 | +0 | 2.0 | 5.2 (+/-1 along, +/-4 lat) | naip_registration (ecc 0.37) | 4-wood / 4-wood | 0.14 | - | 0.372 | 0.336 | iou_water, iou_recovery |
| 13 | +2 | 6.4 | 4.4 (+/-2 along, +/-8 lat) | lie_raster_fit (dice 0.491) | Driver / 4-wood | 0.811 | - | 0.265 | 0.471 | iou_recovery, club |
| 14 | +0 | 23.3 | 6.3 (+/-2 along, +/-6 lat) | naip_registration (ecc 0.352) | Driver / Driver | 0.316 | - | 0.755 | 0.469 | tee, iou_water |
| 16 | +0 | 19.2 | 7.2 | lie_raster_fit (dice 0.454) | 4-wood / 4-wood | 0.0 | - | 0.578 | 0.683 | tee, iou_water, iou_recovery |
| 17 | +0 | 28.8 | 2.7 (+/-3 along, +/-25 lat) | naip_registration (ecc 0.467) | Driver / Driver | - | - | 0.456 | 0.712 | tee, iou_recovery |
| 18 | +5 | 49.0 | 65.5 (+/-4 along, +/-7 lat) | lie_raster_fit (dice 0.43) | 2-wood / 4-wood | 0.107 | - | 0.109 | 0.555 | tee, green, iou_water, iou_recovery, club |

Par 3s (centre distance):

| hole | traced | auto | err | hazards traced | hazards auto |
|---|---|---|---|---|---|
| 7 | 159 | 154 | -5 | {'left': 'bunker', 'right': 'bunker', 'short': 'rough', 'long': 'native'} | {'left': 'bunker', 'right': 'bunker', 'short': 'rough', 'long': 'rough'} |
| 12 | 177 | 186 | +9 | {'left': 'native', 'right': 'bunker', 'short': 'rough', 'long': 'rough'} | {'left': 'rough', 'right': 'bunker', 'short': 'rough', 'long': 'rough'} |
| 3 | 148 | 148 | +0 | {'left': 'trees', 'right': 'rough', 'short': 'water', 'long': 'rough'} | {'left': 'trees', 'right': 'rough', 'short': 'rough', 'long': 'trees'} |
| 15 | 134 | 132 | -2 | {'left': 'rough', 'right': 'native', 'short': 'water', 'long': 'bunker'} | {'left': 'trees', 'right': 'trees', 'short': 'water', 'long': 'bunker'} |

IoU is on the landing-zone grid (220-340 yds, +/-45) in the traced frame after registration; classes absent from both maps are omitted. Trees are traced at the trunks by hand and are unmapped in OSM, so `recovery` IoU is expected to be the weakest until the imagery gap-fill lands.
