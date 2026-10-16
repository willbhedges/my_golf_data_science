# vision_any validation: spirit_hollow vs the hand-traced map

Trees: 3DEP lidar HAG > 2.5 m; Meta CHM in 1.2% lidar gaps. Native: NAIP self-supervised from OSM (seeds 185199 px). No hand-traced label was used to build the layers.

Landing zone = 220-340 yds along the traced tee line, +/-45 yds, 5-yd grid (425 points per hole), traced frame, georeferenced by the registration. `composed` = OSM + vision lie map (what the model sees); `raw` = the layer alone.

| class | pooled IoU (composed) | precision | recall | mean IoU over holes | raw pooled IoU | OSM-only pooled IoU |
|---|---|---|---|---|---|---|
| recovery | 0.23 | 0.39 | 0.36 | 0.16 | 0.26 | 0.0 |
| native | 0.09 | 0.21 | 0.13 | 0.08 | 0.09 | 0.0 |
| water | 0.37 | 0.45 | 0.67 | 0.35 | - | 0.468 |
| penal | 0.42 | 0.63 | 0.57 | 0.39 | - | 0.142 |
| recovery within 5 yds | - | 0.48 | 0.56 | - | - | - |
| native within 5 yds | - | 0.29 | 0.22 | - | - | - |

`penal` = any of trees / native / water (is the shot in trouble at all). `within 5 yds`: a point counts when the other map has the class within one 5-yd grid step (edge offsets from registration and canopy-vs-trunk tracing).

Tree height threshold (pooled IoU composed / raw): 2.5 m: 0.23 / 0.258; 4.0 m: 0.216 / 0.234

| hole | registration | trees IoU | trees P / R | native IoU | native P / R | water IoU | penal IoU | agree |
|---|---|---|---|---|---|---|---|---|
| 1 | naip_ecc ecc 0.2178732475874067, corr 0.207 | 0.38 | 0.48 / 0.64 | 0.0 | 0.0 / 0.0 | None | 0.44 | 0.56 |
| 2F | naip_ecc ecc 0.39900187158844, corr 0.379 | 0.09 | 0.14 / 0.2 | 0.0 | 0.0 / 0.0 | 0.4 | 0.36 | 0.54 |
| 4 | naip_ecc ecc 0.36275026271855215, corr 0.339 | 0.0 | 0.0 / None | 0.22 | 0.51 / 0.28 | None | 0.23 | 0.45 |
| 5 | naip_ecc ecc 0.4684997621435311, corr 0.453 | 0.02 | 0.33 / 0.02 | 0.0 | 0.0 / 0.0 | None | 0.2 | 0.59 |
| 6 | naip_ecc ecc 0.3395094964901429, corr 0.313 | 0.21 | 0.38 / 0.33 | 0.01 | 0.02 / 0.03 | None | 0.1 | 0.59 |
| 8 | naip_ecc ecc 0.2726040260345223, corr 0.26 | 0.0 | 0.0 / None | 0.06 | 0.29 / 0.07 | None | 0.09 | 0.52 |
| 9B | naip_ecc ecc 0.38243299014670895, corr 0.356 | 0.13 | 0.22 / 0.24 | 0.23 | 0.3 / 0.5 | 0.73 | 0.42 | 0.61 |
| 9F | naip_ecc ecc 0.44278911068303567, corr 0.424 | 0.09 | 0.12 / 0.27 | 0.07 | 0.19 / 0.09 | 0.17 | 0.42 | 0.36 |
| 10 | naip_ecc ecc 0.41614545029322203, corr 0.395 | 0.0 | None / 0.0 | 0.0 | None / 0.0 | 0.43 | 0.65 | 0.68 |
| 11 | naip_ecc ecc 0.37045364388211194, corr 0.349 | 0.23 | 0.52 / 0.3 | 0.0 | 0.0 / 0.0 | 0.12 | 0.5 | 0.43 |
| 13 | naip_ecc ecc 0.2889457794967541, corr 0.267 | 0.0 | 0.0 / 0.0 | 0.0 | 0.0 / None | 0.68 | 0.46 | 0.6 |
| 14 | naip_ecc ecc 0.35194677540714653, corr 0.332 | 0.68 | 0.97 / 0.69 | 0.41 | 0.73 / 0.48 | 0.45 | 0.74 | 0.64 |
| 16 | naip_ecc ecc nan, corr 0.309 | 0.35 | 0.76 / 0.4 | 0.22 | 0.28 / 0.5 | 0.0 | 0.56 | 0.55 |
| 17 | naip_ecc ecc 0.46674998231097387, corr 0.437 | 0.17 | 0.21 / 0.47 | 0.04 | 0.04 / 1.0 | None | 0.12 | 0.76 |
| 18 | naip_ecc ecc 0.2786423273453841, corr 0.263 | 0.06 | 0.06 / 0.6 | 0.01 | 0.14 / 0.01 | 0.17 | 0.49 | 0.31 |

## Strategy: hand map vs hand map with the vision trees + native

Same best club (Driver / 2-wood / 4-wood) on **67%** of 15 tee shots; median aim change 5.0 yds; mean EV cost on the hand map of following the alternative pick +0.054 strokes.

| hole | club hand | club alt | aim hand (D/2w/4w) | aim alt (D/2w/4w) | EV cost |
|---|---|---|---|---|---|
| 1 | Driver | Driver | +2.5/+7.5/+7.5 | -10.0/+0.0/+2.5 | +0.141 |
| 2F | Driver | Driver | +0.0/+0.0/+0.0 | +5.0/+5.0/+2.5 | +0.027 |
| 4 | Driver | Driver | -5.0/-5.0/-5.0 | +5.0/+5.0/+0.0 | +0.074 |
| 5 | Driver | Driver | -5.0/-2.5/-5.0 | -7.5/-5.0/-5.0 | +0.007 |
| 6 | Driver | Driver | -5.0/-2.5/-2.5 | -5.0/-5.0/-2.5 | +0.000 |
| 8 | 4-wood | 4-wood | +7.5/+7.5/+10.0 | -5.0/-5.0/+5.0 | +0.007 |
| 9B | 4-wood | 2-wood | -25.0/-25.0/-22.5 | -12.5/-10.0/-15.0 | +0.178 |
| 9F | 4-wood | 4-wood | -7.5/-17.5/-27.5 | -12.5/-15.0/-20.0 | +0.022 |
| 10 | 4-wood | Driver | +5.0/+5.0/+2.5 | -7.5/-5.0/-5.0 | +0.213 |
| 11 | 4-wood | 4-wood | +40.0/-10.0/-7.5 | +32.5/+2.5/-7.5 | +0.000 |
| 13 | Driver | 4-wood | +0.0/-7.5/-7.5 | +0.0/-7.5/-7.5 | +0.028 |
| 14 | 2-wood | 2-wood | -25.0/-10.0/-2.5 | -30.0/-12.5/-2.5 | +0.006 |
| 16 | 4-wood | 2-wood | -7.5/-5.0/-7.5 | -10.0/-5.0/-5.0 | +0.003 |
| 17 | Driver | Driver | -7.5/-7.5/-10.0 | -5.0/-5.0/-10.0 | +0.001 |
| 18 | 4-wood | Driver | -2.5/-7.5/-12.5 | +5.0/+0.0/-2.5 | +0.106 |

## Strategy: hand map vs OSM-only (hand map with trees + native removed)

Same best club (Driver / 2-wood / 4-wood) on **67%** of 15 tee shots; median aim change 5.0 yds; mean EV cost on the hand map of following the alternative pick +0.067 strokes.

| hole | club hand | club alt | aim hand (D/2w/4w) | aim alt (D/2w/4w) | EV cost |
|---|---|---|---|---|---|
| 1 | Driver | Driver | +2.5/+7.5/+7.5 | -2.5/+0.0/+2.5 | +0.026 |
| 2F | Driver | Driver | +0.0/+0.0/+0.0 | +5.0/+5.0/+2.5 | +0.027 |
| 4 | Driver | Driver | -5.0/-5.0/-5.0 | -5.0/-5.0/-5.0 | +0.000 |
| 5 | Driver | Driver | -5.0/-2.5/-5.0 | -7.5/-7.5/-5.0 | +0.007 |
| 6 | Driver | Driver | -5.0/-2.5/-2.5 | -5.0/-5.0/-2.5 | +0.000 |
| 8 | 4-wood | 4-wood | +7.5/+7.5/+10.0 | -12.5/-5.0/+5.0 | +0.007 |
| 9B | 4-wood | 2-wood | -25.0/-25.0/-22.5 | -7.5/+0.0/-12.5 | +0.421 |
| 9F | 4-wood | 4-wood | -7.5/-17.5/-27.5 | -15.0/-15.0/-20.0 | +0.022 |
| 10 | 4-wood | Driver | +5.0/+5.0/+2.5 | -7.5/-5.0/-5.0 | +0.213 |
| 11 | 4-wood | 4-wood | +40.0/-10.0/-7.5 | +40.0/+40.0/-12.5 | +0.006 |
| 13 | Driver | Driver | +0.0/-7.5/-7.5 | +0.0/-7.5/-7.5 | +0.000 |
| 14 | 2-wood | Driver | -25.0/-10.0/-2.5 | -30.0/-15.0/-7.5 | +0.116 |
| 16 | 4-wood | Driver | -7.5/-5.0/-7.5 | -15.0/-7.5/-5.0 | +0.051 |
| 17 | Driver | Driver | -7.5/-7.5/-10.0 | -7.5/-7.5/-10.0 | +0.000 |
| 18 | 4-wood | Driver | -2.5/-7.5/-12.5 | +5.0/+0.0/-2.5 | +0.106 |
