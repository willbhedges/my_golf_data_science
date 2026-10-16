# Auto-course acceptance: Spirit Hollow (oracle tees (traced lengths as the card), + LOHO imagery gap-fill)

Same club (Driver / 2-wood / 4-wood) on **62%** of 16 tee shots (bar 80%). Tee within 10 yds: 56%; green within 10 (or the traced green's own rounding spread): 75%; length within 5: 62%. Median tee error 8.75 yds, green 6.3 yds.

Mean landing-zone IoU by class: fairway 0.57, rough 0.26, recovery 0.07, native 0.04, water 0.40, sand 0.40, ob 0.18

Holes passing every check: 4

| hole | len err | tee err | green err (traced +/-) | registration | club traced / auto | IoU water | IoU ob | IoU trees | IoU fairway | failed |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | +6 | 53.0 | 48.7 (+/-2 along, +/-4 lat) | lie_raster_fit (dice 0.685) | Driver / Driver | - | - | 0.067 | 0.636 | tee, green, length, iou_recovery |
| 2B | -25 | 44.3 | 122.6 (+/-6 along, +/-8 lat) | lie_raster_fit (dice 0.416) | Driver / Driver | 0.125 | 0.0 | 0.0 | 0.653 | tee, green, length, iou_water, iou_ob, iou_recovery |
| 2F | +10 | 61.1 | 4.3 (+/-4 along, +/-8 lat) | naip_registration (ecc 0.399) | Driver / Driver | 0.327 | 0.71 | 0.0 | 0.503 | tee, length, iou_water, iou_recovery |
| 4 | +4 | 8.4 | 4.8 (+/-4 along, +/-32 lat) | naip_registration (ecc 0.363) | Driver / Driver | - | - | - | 0.439 |  |
| 5 | +3 | 5.4 | 6.3 (+/-2 along, +/-16 lat) | naip_registration (ecc 0.468) | 4-wood / 4-wood | - | - | 0.0 | 0.641 | iou_recovery |
| 6 | +7 | 1.4 | 8.2 (+/-2 along, +/-5 lat) | naip_registration (ecc 0.34) | Driver / Driver | - | 0.0 | 0.0 | 0.558 | length, iou_ob, iou_recovery |
| 8 | +3 | 9.1 | 11.0 (+/-2 along, +/-9 lat) | lie_raster_fit (dice 0.496) | 4-wood / 4-wood | - | 0.0 | - | 0.608 | green, iou_ob |
| 9B | -6 | 51.4 | 1.6 (+/-2 along, +/-2 lat) | naip_registration (ecc 0.382) | Driver / 2-wood | 0.795 | - | 0.091 | 0.602 | tee, length, iou_recovery, club |
| 9F | +2 | 1.9 | 3.0 (+/-2 along, +/-2 lat) | naip_registration (ecc 0.443) | 4-wood / 4-wood | 0.303 | - | 0.079 | 0.449 | iou_water, iou_recovery |
| 10 | +4 | 2.6 | 7.7 (+/-4 along, +/-7 lat) | naip_registration (ecc 0.416) | Driver / Driver | 0.523 | - | 0.059 | 0.812 | iou_water, iou_recovery |
| 11 | -3 | 3.8 | 5.2 (+/-1 along, +/-4 lat) | naip_registration (ecc 0.37) | 4-wood / 4-wood | 0.231 | - | 0.27 | 0.403 | iou_water, iou_recovery |
| 13 | +5 | 7.1 | 8.2 (+/-2 along, +/-8 lat) | lie_raster_fit (dice 0.43) | Driver / 4-wood | 0.742 | - | 0.0 | 0.521 | iou_recovery, club |
| 14 | +5 | 3.3 | 6.3 (+/-2 along, +/-6 lat) | naip_registration (ecc 0.352) | 2-wood / 4-wood | 0.526 | - | 0.0 | 0.37 | iou_water, iou_recovery, club |
| 16 | +4 | 11.0 | 5.2 | lie_raster_fit (dice 0.452) | 2-wood / 4-wood | 0.0 | - | 0.281 | 0.689 | tee, iou_water, iou_recovery, club |
| 17 | -20 | 33.0 | 2.6 (+/-3 along, +/-25 lat) | naip_registration (ecc 0.467) | Driver / 4-wood | - | - | 0.0 | 0.772 | tee, length, iou_recovery, club |
| 18 | +5 | 18.1 | 16.2 (+/-4 along, +/-7 lat) | lie_raster_fit (dice 0.483) | Driver / 4-wood | 0.4 | - | 0.143 | 0.401 | tee, green, iou_water, iou_recovery, club |

Par 3s (centre distance):

| hole | traced | auto | err | hazards traced | hazards auto |
|---|---|---|---|---|---|
| 7 | 159 | 149 | -10 | {'left': 'bunker', 'right': 'bunker', 'short': 'rough', 'long': 'native'} | {'left': 'bunker', 'right': 'bunker', 'short': 'rough', 'long': 'rough'} |
| 12 | 177 | 176 | -1 | {'left': 'native', 'right': 'bunker', 'short': 'rough', 'long': 'rough'} | {'left': 'rough', 'right': 'bunker', 'short': 'rough', 'long': 'rough'} |
| 15 | 134 | 130 | -4 | {'left': 'rough', 'right': 'native', 'short': 'water', 'long': 'bunker'} | {'left': 'rough', 'right': 'rough', 'short': 'water', 'long': 'bunker'} |

IoU is on the landing-zone grid (220-340 yds, +/-45) in the traced frame after registration; classes absent from both maps are omitted. Trees are traced at the trunks by hand and are unmapped in OSM, so `recovery` IoU is expected to be the weakest until the imagery gap-fill lands.
