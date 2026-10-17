# OB inference: Spirit Hollow evaluation

Built 2026-10-17T03:31:04Z. Layers: osm, ms_buildings, parcels; 162 houses (non-golf buildings), 261 private parcels, 26 public road/rail lines.
Grid: hand tee line 190-335 yds, +/-55 yds, 5-yd cells inside the screenshot footprint; prediction limited to 60 yds of the package line of play, minus fairway/green/water/sand. Hand OB in the corridor on: 2F, 5, 8.

| | pooled IoU |
|---|---|
| geometry stage OB today (outline + OSM buildings/roads, as packaged) | 0.12 |
| same, clipped to the corridor rule | 0.08 |
| inferred, fitted on all holes (in-sample) | 0.36 |
| **inferred, leave-one-hole-out** | **0.30** |
| inferred, leave-one-hole-out, vs the hand OB inside the corridor rule (87/119 hand OB cells) | 0.36 |

Fitted parameters (1122264 combinations searched): `{"mode": "replace", "house_d": null, "house_close": 0.0, "road_margin": null, "road_inside": true, "res_off": null, "out_off": -8, "out_dev": 60, "out_src": "parcels", "parcel_off": null, "parcel_mode": "houses"}`

Ablation at the fit (pooled IoU): without out 0.00, out only 0.37

Evidence precision (exclusive cells, priority order; p used as confidence): property_line 76/165 -> 0.461

| hole | hand OB cells | geometry today: pred / IoU | LOHO: pred / IoU | LOHO params (house d/close, road, outside, mode) |
|---|---|---|---|---|
| 1 | 0 | 23 / 0.00 | 0 / - | None/0.0, None, -8 parcels dev 60, replace |
| 2B | 0 | 90 / 0.00 | 0 / - | None/0.0, None, -8 parcels dev 60, replace |
| 2F | 29 | 51 / 0.54 | 48 / 0.20 | None/0.0, None, -8 parcels dev 60, replace |
| 4 | 0 | 11 / 0.00 | 17 / 0.00 | None/0.0, None, -8 parcels dev 60, replace |
| 5 | 36 | 2 / 0.06 | 11 / 0.15 | None/0.0, None, -5 parcels dev 60, replace |
| 6 | 0 | 15 / 0.00 | 0 / - | None/0.0, None, -8 parcels dev 60, replace |
| 8 | 54 | 15 / 0.28 | 65 / 0.55 | None/0.0, None, -8 parcels dev 60, replace |
| 9B | 0 | 6 / 0.00 | 0 / - | None/0.0, None, -8 parcels dev 60, replace |
| 9F | 0 | 0 / - | 0 / - | None/0.0, None, -8 parcels dev 60, replace |
| 10 | 0 | 5 / 0.00 | 2 / 0.00 | None/0.0, None, -8 parcels dev 60, replace |
| 11 | 0 | 0 / - | 0 / - | None/0.0, None, -8 parcels dev 60, replace |
| 13 | 0 | 0 / - | 0 / - | None/0.0, None, -8 parcels dev 60, replace |
| 14 | 0 | 0 / - | 0 / - | None/0.0, None, -8 parcels dev 60, replace |
| 16 | 0 | 67 / 0.00 | 0 / - | None/0.0, None, -8 parcels dev 60, replace |
| 17 | 0 | 0 / - | 0 / - | None/0.0, None, -8 parcels dev 60, replace |
| 18 | 0 | 0 / - | 0 / - | None/0.0, None, -8 parcels dev 60, replace |

IoU is undefined (shown -) on holes with no OB in either; cells predicted there are false positives (the 'pred' column).

## Decision impact (product decide.py quick, Black tees vs spirit_hollow/output/final_decision.json)

| OB variant | same club | changed clubs vs no OB | expected strokes vs no OB (holes with |d| >= 0.005) |
|---|---|---|---|
| none | 5/14 | - | - |
| geometry | 5/14 | - | - |
| inferred | 5/14 | - | - |
| hand | 5/14 | - | - |
| hand map | 12/16 | - | - |
| hand map without OB | 12/16 | - | - |

'hand map' rows run the same quick decision on spirit_hollow/course.py itself (keys 2B/2F/9B/9F), with and without its OB zones: the OB sensitivity of the truth map.

| hole | final_decision | none | geometry | inferred | hand | hand map | hand map without OB |
|---|---|---|---|---|---|---|---|
| 1 | 4-wood | Long iron | Long iron | Long iron | Long iron | 4-wood | 4-wood |
| 2 | Driver | Driver | Driver | Driver | Driver | - | - |
| 4 | Driver | 4-wood | 4-wood | 4-wood | 4-wood | Driver | Driver |
| 5 | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood |
| 6 | 2-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood |
| 8 | 4-wood | Long iron | Long iron | Long iron | Long iron | 4-wood | 4-wood |
| 9 | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | - | - |
| 10 | Driver | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood |
| 11 | Long iron | Long iron | Long iron | Long iron | Long iron | Long iron | Long iron |
| 13 | Driver | Long iron | Long iron | Long iron | Long iron | Driver | Driver |
| 14 | 2-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood |
| 16 | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood |
| 17 | Driver | 4-wood | 4-wood | 4-wood | 4-wood | Driver | Driver |
| 18 | 2-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood |
| 2B | Driver | - | - | - | - | Driver | Driver |
| 2F | Driver | - | - | - | - | Driver | Driver |
| 9B | 2-wood | - | - | - | - | 2-wood | 2-wood |
| 9F | 4-wood | - | - | - | - | 4-wood | 4-wood |
