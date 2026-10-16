# vision_any validation: mozingo vs the hand-traced map

Trees: 3DEP lidar HAG > 2.5 m. Native: NAIP self-supervised from OSM (seeds 107171 px). No hand-traced label was used to build the layers.

Landing zone = 220-340 yds along the traced tee line, +/-45 yds, 5-yd grid (425 points per hole), traced frame, georeferenced by the registration. `composed` = OSM + vision lie map (what the model sees); `raw` = the layer alone.

| class | pooled IoU (composed) | precision | recall | mean IoU over holes | raw pooled IoU | OSM-only pooled IoU |
|---|---|---|---|---|---|---|
| recovery | 0.17 | 0.45 | 0.21 | 0.14 | 0.17 | 0.0 |
| native | 0.14 | 0.2 | 0.32 | 0.1 | 0.14 | 0.0 |
| water | 0.21 | 0.23 | 0.7 | 0.11 | - | 0.36 |
| penal | 0.26 | 0.39 | 0.43 | 0.25 | - | 0.081 |

`penal` = any of trees / native / water (is the shot in trouble at all).

Tree height threshold (pooled IoU composed / raw): 2.5 m: 0.169 / 0.169; 4.0 m: 0.167 / 0.168

| hole | registration | trees IoU | trees P / R | native IoU | native P / R | water IoU | penal IoU | agree |
|---|---|---|---|---|---|---|---|---|
| 2 | lie_raster_fit dice 0.718 | 0.54 | 0.77 / 0.65 | 0.18 | 0.42 / 0.24 | None | 0.38 | 0.63 |
| 6 | lie_raster_fit dice 0.757 | 0.24 | 0.3 / 0.53 | 0.0 | 0.0 / None | 0.0 | 0.2 | 0.6 |
| 7 | lie_raster_fit dice 0.794 | 0.05 | 0.17 / 0.06 | 0.0 | 0.0 / None | 0.0 | 0.21 | 0.62 |
| 9 | lie_raster_fit dice 0.767 | None | None / None | 0.05 | 0.42 / 0.06 | 0.0 | 0.05 | 0.48 |
| 10 | lie_raster_fit dice 0.825 | 0.07 | 1.0 / 0.07 | 0.4 | 0.4 / 1.0 | None | 0.22 | 0.63 |
| 12 | lie_raster_fit dice 0.833 | 0.0 | 0.0 / 0.0 | 0.0 | 0.0 / None | 0.0 | 0.27 | 0.68 |
| 13 | lie_raster_fit dice 0.845 | 0.22 | 0.36 / 0.36 | 0.07 | 0.07 / 0.5 | 0.0 | 0.18 | 0.59 |
| 14 | lie_raster_fit dice 0.816 | 0.0 | 0.0 / None | 0.0 | 0.0 / None | 0.28 | 0.11 | 0.64 |
| 16 | lie_raster_fit dice 0.823 | 0.15 | 0.86 / 0.15 | 0.0 | 0.0 / None | None | 0.39 | 0.62 |
| 17 | lie_raster_fit dice 0.819 | None | None / None | 0.39 | 0.84 / 0.42 | None | 0.39 | 0.54 |
| 18 | lie_raster_fit dice 0.7 | 0.04 | 0.1 / 0.07 | 0.0 | 0.0 / None | 0.49 | 0.31 | 0.61 |

## Strategy: hand map vs hand map with the vision trees + native

Same best club (Driver / 2-wood / 4-wood) on **64%** of 11 tee shots; median aim change 2.5 yds; mean EV cost on the hand map of following the alternative pick +0.037 strokes.

| hole | club hand | club alt | aim hand (D/2w/4w) | aim alt (D/2w/4w) | EV cost |
|---|---|---|---|---|---|
| 2 | 4-wood | 4-wood | -10.0/-10.0/-7.5 | -7.5/-5.0/-2.5 | +0.007 |
| 6 | Driver | Driver | -5.0/-10.0/-12.5 | -7.5/-10.0/-12.5 | +0.000 |
| 7 | 4-wood | Driver | +2.5/+5.0/+7.5 | +0.0/+2.5/+2.5 | +0.088 |
| 9 | Driver | Driver | +5.0/+5.0/+5.0 | -5.0/-2.5/-2.5 | +0.052 |
| 10 | Driver | Driver | -5.0/-5.0/-7.5 | +0.0/-5.0/-5.0 | +0.008 |
| 12 | Driver | Driver | +0.0/-10.0/-12.5 | -7.5/-15.0/-12.5 | +0.003 |
| 13 | 4-wood | Driver | +2.5/+2.5/+2.5 | -2.5/+2.5/+5.0 | +0.013 |
| 14 | Driver | Driver | +2.5/+2.5/+2.5 | +0.0/-2.5/-2.5 | +0.002 |
| 16 | 2-wood | Driver | -5.0/-7.5/-10.0 | -5.0/-5.0/-7.5 | +0.003 |
| 17 | Driver | Driver | -30.0/-37.5/-40.0 | -10.0/-15.0/-12.5 | +0.149 |
| 18 | Driver | 2-wood | -17.5/-5.0/+0.0 | -17.5/-7.5/-12.5 | +0.081 |

## Strategy: hand map vs OSM-only (hand map with trees + native removed)

Same best club (Driver / 2-wood / 4-wood) on **64%** of 11 tee shots; median aim change 2.5 yds; mean EV cost on the hand map of following the alternative pick +0.035 strokes.

| hole | club hand | club alt | aim hand (D/2w/4w) | aim alt (D/2w/4w) | EV cost |
|---|---|---|---|---|---|
| 2 | 4-wood | 4-wood | -10.0/-10.0/-7.5 | -12.5/-10.0/-5.0 | +0.001 |
| 6 | Driver | Driver | -5.0/-10.0/-12.5 | -10.0/-12.5/-15.0 | +0.005 |
| 7 | 4-wood | Driver | +2.5/+5.0/+7.5 | +0.0/+2.5/+2.5 | +0.088 |
| 9 | Driver | Driver | +5.0/+5.0/+5.0 | -2.5/-2.5/-2.5 | +0.022 |
| 10 | Driver | Driver | -5.0/-5.0/-7.5 | -7.5/-7.5/-10.0 | +0.001 |
| 12 | Driver | Driver | +0.0/-10.0/-12.5 | +0.0/-10.0/-12.5 | +0.000 |
| 13 | 4-wood | Driver | +2.5/+2.5/+2.5 | -5.0/-2.5/+0.0 | +0.023 |
| 14 | Driver | Driver | +2.5/+2.5/+2.5 | +2.5/+2.5/+2.5 | +0.000 |
| 16 | 2-wood | Driver | -5.0/-7.5/-10.0 | -7.5/-5.0/-7.5 | +0.005 |
| 17 | Driver | Driver | -30.0/-37.5/-40.0 | -10.0/-7.5/-5.0 | +0.149 |
| 18 | Driver | 2-wood | -17.5/-5.0/+0.0 | -17.5/-10.0/-15.0 | +0.088 |
