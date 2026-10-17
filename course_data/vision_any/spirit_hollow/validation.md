# vision_any validation: spirit_hollow vs the hand-traced map

Trees: 3DEP lidar HAG > 2.5 m; Meta CHM in 1.2% lidar gaps. Native: NAIP self-supervised from OSM (seeds 185199 px). No hand-traced label was used to build the layers.

Landing zone = 220-340 yds along the traced tee line, +/-45 yds, 5-yd grid (425 points per hole), traced frame, georeferenced by the registration. `composed` = OSM + vision lie map (what the model sees); `raw` = the layer alone.

| class | pooled IoU (composed) | precision | recall | mean IoU over holes | raw pooled IoU | OSM-only pooled IoU |
|---|---|---|---|---|---|---|
| recovery | 0.36 | 0.55 | 0.51 | 0.29 | 0.38 | 0.0 |
| native | 0.12 | 0.26 | 0.19 | 0.13 | 0.12 | 0.0 |
| water | 0.38 | 0.44 | 0.71 | 0.35 | - | 0.488 |
| penal | 0.51 | 0.68 | 0.66 | 0.47 | - | 0.145 |
| recovery within 5 yds | - | 0.67 | 0.71 | - | - | - |
| native within 5 yds | - | 0.33 | 0.29 | - | - | - |

`penal` = any of trees / native / water (is the shot in trouble at all). `within 5 yds`: a point counts when the other map has the class within one 5-yd grid step (edge offsets from registration and canopy-vs-trunk tracing).

Tree height threshold (pooled IoU composed / raw): 2.5 m: 0.358 / 0.382; 4.0 m: 0.344 / 0.36

| hole | registration | trees IoU | trees P / R | native IoU | native P / R | water IoU | penal IoU | agree |
|---|---|---|---|---|---|---|---|---|
| 1 | naip_ecc ecc 0.2178732475874067, corr 0.207 | 0.52 | 0.66 / 0.71 | 0.0 | 0.0 / 0.0 | None | 0.58 | 0.55 |
| 2F | naip_ecc ecc 0.39900187158844, corr 0.379 | 0.07 | 0.09 / 0.19 | 0.0 | 0.0 / 0.0 | 0.47 | 0.3 | 0.51 |
| 4 | naip_ecc ecc 0.36275026271855215, corr 0.339 | 0.0 | 0.0 / None | 0.22 | 0.51 / 0.28 | None | 0.23 | 0.45 |
| 5 | naip_ecc ecc 0.4684997621435311, corr 0.453 | 0.08 | 0.33 / 0.1 | 0.0 | 0.0 / 0.0 | None | 0.27 | 0.65 |
| 6 | naip_ecc ecc 0.3395094964901429, corr 0.313 | 0.4 | 0.67 / 0.5 | 0.01 | 0.02 / 0.03 | None | 0.04 | 0.57 |
| 8 | naip_ecc ecc 0.2726040260345223, corr 0.26 | 0.0 | 0.0 / None | 0.09 | 0.29 / 0.11 | None | 0.12 | 0.6 |
| 9B | naip_ecc ecc 0.38243299014670895, corr 0.356 | 0.57 | 0.7 / 0.76 | 0.23 | 0.3 / 0.5 | 0.73 | 0.62 | 0.71 |
| 9F | naip_ecc ecc 0.44278911068303567, corr 0.424 | 0.32 | 0.36 / 0.75 | 0.07 | 0.19 / 0.1 | 0.17 | 0.6 | 0.48 |
| 10 | naip_ecc ecc 0.41614545029322203, corr 0.395 | 0.0 | None / 0.0 | 0.0 | 0.0 / 0.0 | 0.45 | 0.63 | 0.69 |
| 11 | naip_ecc ecc 0.37045364388211194, corr 0.349 | 0.3 | 0.62 / 0.37 | 0.0 | 0.0 / 0.0 | 0.12 | 0.49 | 0.42 |
| 13 | naip_ecc ecc 0.2889457794967541, corr 0.267 | 0.28 | 0.37 / 0.54 | 0.0 | 0.0 / None | 0.71 | 0.52 | 0.61 |
| 14 | naip_ecc ecc 0.35194677540714653, corr 0.332 | 0.78 | 0.95 / 0.81 | 0.38 | 0.72 / 0.44 | 0.34 | 0.79 | 0.61 |
| 16 | naip_ecc ecc nan, corr 0.309 | 0.38 | 0.87 / 0.41 | 0.19 | 0.21 / 0.68 | 0.0 | 0.57 | 0.56 |
| 17 | naip_ecc ecc 0.46674998231097387, corr 0.437 | 0.57 | 0.67 / 0.79 | 0.77 | 0.79 / 0.96 | None | 0.65 | 0.79 |
| 18 | naip_ecc ecc 0.2786423273453841, corr 0.263 | 0.06 | 0.06 / 0.6 | 0.02 | 0.14 / 0.02 | 0.17 | 0.58 | 0.33 |

## Strategy: hand map vs hand map with the vision trees + native

Same best club (Driver / 2-wood / 4-wood) on **67%** of 15 tee shots; median aim change 2.5 yds; mean EV cost on the hand map of following the alternative pick +0.016 strokes.

| hole | club hand | club alt | aim hand (D/2w/4w) | aim alt (D/2w/4w) | EV cost |
|---|---|---|---|---|---|
| 1 | 4-wood | 4-wood | -10.0/-7.5/-2.5 | -20.0/-12.5/-7.5 | +0.027 |
| 2F | Driver | Driver | -15.0/-12.5/-7.5 | -17.5/-12.5/-7.5 | +0.000 |
| 4 | Driver | Driver | -5.0/-5.0/-5.0 | +7.5/+5.0/+2.5 | +0.098 |
| 5 | 4-wood | 4-wood | -10.0/-5.0/-5.0 | -15.0/-10.0/-7.5 | +0.002 |
| 6 | Driver | 2-wood | -5.0/-5.0/-5.0 | -10.0/-7.5/-5.0 | +0.005 |
| 8 | 4-wood | 4-wood | +0.0/+5.0/+7.5 | -2.5/-2.5/+5.0 | +0.002 |
| 9B | 4-wood | 2-wood | -17.5/-20.0/-20.0 | -17.5/-10.0/-15.0 | +0.039 |
| 9F | 4-wood | 4-wood | +40.0/-10.0/-20.0 | -12.5/-15.0/-17.5 | +0.000 |
| 10 | Driver | Driver | -2.5/+0.0/+2.5 | -7.5/-7.5/-7.5 | +0.022 |
| 11 | 4-wood | 4-wood | +40.0/-7.5/+0.0 | -35.0/+32.5/-2.5 | +0.000 |
| 13 | 4-wood | 4-wood | -10.0/-12.5/-15.0 | -10.0/-12.5/-12.5 | +0.001 |
| 14 | 4-wood | 2-wood | -40.0/-27.5/-17.5 | -40.0/-30.0/-20.0 | +0.019 |
| 16 | 2-wood | 2-wood | -12.5/-12.5/-12.5 | -12.5/-12.5/-12.5 | +0.000 |
| 17 | 2-wood | Driver | -5.0/-5.0/-7.5 | -2.5/-2.5/-7.5 | +0.010 |
| 18 | 2-wood | Driver | +2.5/-2.5/-7.5 | +5.0/+0.0/-2.5 | +0.021 |

## Strategy: hand map vs OSM-only (hand map with trees + native removed)

Same best club (Driver / 2-wood / 4-wood) on **53%** of 15 tee shots; median aim change 2.5 yds; mean EV cost on the hand map of following the alternative pick +0.071 strokes.

| hole | club hand | club alt | aim hand (D/2w/4w) | aim alt (D/2w/4w) | EV cost |
|---|---|---|---|---|---|
| 1 | 4-wood | Driver | -10.0/-7.5/-2.5 | -12.5/-7.5/-5.0 | +0.086 |
| 2F | Driver | Driver | -15.0/-12.5/-7.5 | -17.5/-12.5/-7.5 | +0.000 |
| 4 | Driver | Driver | -5.0/-5.0/-5.0 | -5.0/-5.0/-5.0 | +0.000 |
| 5 | 4-wood | 4-wood | -10.0/-5.0/-5.0 | -17.5/-10.0/-7.5 | +0.002 |
| 6 | Driver | Driver | -5.0/-5.0/-5.0 | -7.5/-7.5/-5.0 | +0.000 |
| 8 | 4-wood | 4-wood | +0.0/+5.0/+7.5 | -10.0/-2.5/+5.0 | +0.002 |
| 9B | 4-wood | 2-wood | -17.5/-20.0/-20.0 | -17.5/-2.5/-15.0 | +0.135 |
| 9F | 4-wood | 4-wood | +40.0/-10.0/-20.0 | -15.0/-15.0/-20.0 | +0.000 |
| 10 | Driver | Driver | -2.5/+0.0/+2.5 | -10.0/-7.5/-7.5 | +0.051 |
| 11 | 4-wood | 4-wood | +40.0/-7.5/+0.0 | +40.0/+40.0/-40.0 | +0.636 |
| 13 | 4-wood | Driver | -10.0/-12.5/-15.0 | -15.0/-15.0/-15.0 | +0.010 |
| 14 | 4-wood | Driver | -40.0/-27.5/-17.5 | -40.0/-30.0/-22.5 | +0.088 |
| 16 | 2-wood | Driver | -12.5/-12.5/-12.5 | -20.0/-15.0/-12.5 | +0.039 |
| 17 | 2-wood | Driver | -5.0/-5.0/-7.5 | -5.0/-5.0/-7.5 | +0.002 |
| 18 | 2-wood | Driver | +2.5/-2.5/-7.5 | +5.0/+0.0/-2.5 | +0.021 |
