# Auto-course acceptance: Spirit Hollow (holes.json as built)

Same club (Driver / 2-wood / 4-wood) on **69%** of 16 tee shots (bar 80%). Tee within 10 yds: 25%; green within 10 (or the traced green's own rounding spread): 75%; length within 5: 12%. Median tee error 23.75 yds, green 6.3 yds.

Decision regret (strokes lost on the hand map by playing the auto map's club): mean 0.0116, max 0.1192 (bar mean <= 0.02, max <= 0.05): not met.

Mean landing-zone IoU by class: fairway 0.58, rough 0.28, recovery 0.00, native 0.00, water 0.37, sand 0.38, ob 0.17

Holes passing every check: none

| hole | len err | tee err | green err (traced +/-) | registration | club traced / auto | IoU water | IoU ob | IoU trees | IoU fairway | failed |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | -22 | 59.5 | 40.2 (+/-2 along, +/-4 lat) | lie_raster_fit (dice 0.736) | Driver / Driver | - | 0.0 | 0.0 | 0.742 | tee, green, length, iou_ob, iou_recovery |
| 2B | -102 | 24.2 | 205.2 (+/-6 along, +/-8 lat) | lie_raster_fit (dice 0.409) | Driver / Driver | 0.104 | - | 0.0 | 0.642 | tee, green, length, iou_water, iou_recovery |
| 2F | -13 | 99.1 | 4.4 (+/-4 along, +/-8 lat) | naip_registration (ecc 0.399) | Driver / Driver | 0.333 | 0.688 | 0.0 | 0.503 | tee, length, iou_water, iou_recovery |
| 4 | +12 | 10.0 | 4.8 (+/-4 along, +/-32 lat) | naip_registration (ecc 0.363) | Driver / Driver | - | - | - | 0.439 | length |
| 5 | -13 | 16.3 | 6.3 (+/-2 along, +/-16 lat) | naip_registration (ecc 0.468) | 4-wood / 4-wood | - | - | 0.0 | 0.641 | tee, length, iou_recovery |
| 6 | -13 | 21.7 | 8.2 (+/-2 along, +/-5 lat) | naip_registration (ecc 0.34) | Driver / Driver | - | 0.0 | 0.0 | 0.558 | tee, length, iou_ob, iou_recovery |
| 8 | +8 | 28.9 | 16.7 (+/-2 along, +/-9 lat) | lie_raster_fit (dice 0.597) | 4-wood / Driver | - | 0.0 | - | 0.684 | tee, green, length, iou_ob, club |
| 9B | -34 | 82.2 | 1.6 (+/-2 along, +/-2 lat) | naip_registration (ecc 0.382) | Driver / 4-wood | 0.693 | - | 0.0 | 0.602 | tee, length, iou_recovery, club |
| 9F | -8 | 9.0 | 2.9 (+/-2 along, +/-2 lat) | naip_registration (ecc 0.443) | 4-wood / 4-wood | 0.156 | - | 0.0 | 0.449 | length, iou_water, iou_recovery |
| 10 | -19 | 22.2 | 7.7 (+/-4 along, +/-7 lat) | naip_registration (ecc 0.416) | Driver / Driver | 0.448 | - | 0.0 | 0.807 | tee, length, iou_water, iou_recovery |
| 11 | -10 | 8.1 | 5.2 (+/-1 along, +/-4 lat) | naip_registration (ecc 0.37) | 4-wood / 4-wood | 0.231 | - | 0.0 | 0.403 | length, iou_water, iou_recovery |
| 13 | +2 | 5.7 | 5.0 (+/-2 along, +/-8 lat) | lie_raster_fit (dice 0.432) | Driver / 4-wood | 0.782 | - | 0.0 | 0.528 | iou_recovery, club |
| 14 | -25 | 35.7 | 6.3 (+/-2 along, +/-6 lat) | naip_registration (ecc 0.352) | 2-wood / Driver | 0.526 | - | - | 0.37 | tee, length, iou_water, club |
| 16 | -10 | 43.2 | 6.3 | lie_raster_fit (dice 0.462) | 2-wood / 4-wood | 0.0 | - | 0.0 | 0.691 | tee, length, iou_water, iou_recovery, club |
| 17 | -8 | 29.9 | 2.6 (+/-3 along, +/-25 lat) | naip_registration (ecc 0.467) | Driver / Driver | - | - | 0.0 | 0.772 | tee, length, iou_recovery |
| 18 | +5 | 23.3 | 25.5 (+/-4 along, +/-7 lat) | lie_raster_fit (dice 0.44) | Driver / Driver | 0.45 | - | 0.0 | 0.425 | tee, green, iou_water, iou_recovery |

Par 3s (centre distance):

| hole | traced | auto | err | hazards traced | hazards auto |
|---|---|---|---|---|---|
| 7 | 159 | 154 | -5 | {'left': 'bunker', 'right': 'bunker', 'short': 'rough', 'long': 'native'} | {'left': 'bunker', 'right': 'bunker', 'short': 'rough', 'long': 'rough'} |
| 12 | 177 | 184 | +7 | {'left': 'native', 'right': 'bunker', 'short': 'rough', 'long': 'rough'} | {'left': 'rough', 'right': 'bunker', 'short': 'rough', 'long': 'rough'} |
| 15 | 134 | 144 | +10 | {'left': 'rough', 'right': 'native', 'short': 'water', 'long': 'bunker'} | {'left': 'rough', 'right': 'rough', 'short': 'water', 'long': 'bunker'} |

IoU is on the landing-zone grid (220-340 yds, +/-45) in the traced frame after registration; classes absent from both maps are omitted. Trees are traced at the trunks by hand and are unmapped in OSM, so `recovery` IoU is expected to be the weakest until the imagery gap-fill lands.
