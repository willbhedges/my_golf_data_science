# OB inference: Spirit Hollow evaluation

Built 2026-10-17T00:43:10Z. Layers: osm, ms_buildings, parcels; 162 houses (non-golf buildings), 261 private parcels, 26 public road/rail lines.
Grid: hand tee line 190-335 yds, +/-55 yds, 5-yd cells inside the screenshot footprint; prediction limited to 60 yds of the package line of play, minus fairway/green/water/sand. Hand OB in the corridor on: 2F, 5, 8.

| | pooled IoU |
|---|---|
| geometry stage OB today (outline + OSM buildings/roads, as packaged) | 0.12 |
| same, clipped to the corridor rule | 0.08 |
| inferred, fitted on all holes (in-sample) | 0.28 |
| **inferred, leave-one-hole-out** | **0.28** |

Fitted parameters (497952 combinations searched): `{"mode": "replace", "house_d": null, "house_close": 0.0, "road_margin": null, "road_inside": true, "res_off": null, "out_off": -10, "out_dev": 60, "parcel_off": null, "parcel_mode": "houses"}`

Ablation at the fit (pooled IoU): without out 0.00, out only 0.28

Evidence precision (exclusive cells, priority order; p used as confidence): outside 78/242 -> 0.324

| hole | hand OB cells | geometry today: pred / IoU | LOHO: pred / IoU | LOHO params (house d/close, road, outside, mode) |
|---|---|---|---|---|
| 1 | 0 | 23 / 0.00 | 0 / - | None/0.0, None, -10 dev 60, replace |
| 2B | 0 | 90 / 0.00 | 0 / - | None/0.0, None, -10 dev 60, replace |
| 2F | 29 | 51 / 0.54 | 63 / 0.17 | None/0.0, None, -10 dev 60, replace |
| 4 | 0 | 11 / 0.00 | 64 / 0.00 | None/0.0, None, -10 dev 60, replace |
| 5 | 36 | 2 / 0.06 | 42 / 0.47 | None/0.0, None, -10 dev 60, replace |
| 6 | 0 | 15 / 0.00 | 0 / - | None/0.0, None, -10 dev 60, replace |
| 8 | 54 | 15 / 0.28 | 49 / 0.64 | None/0.0, None, -10 dev 60, replace |
| 9B | 0 | 6 / 0.00 | 0 / - | None/0.0, None, -10 dev 60, replace |
| 9F | 0 | 0 / - | 0 / - | None/0.0, None, -10 dev 60, replace |
| 10 | 0 | 5 / 0.00 | 24 / 0.00 | None/0.0, None, -10 dev 60, replace |
| 11 | 0 | 0 / - | 0 / - | None/0.0, None, -10 dev 60, replace |
| 13 | 0 | 0 / - | 0 / - | None/0.0, None, -10 dev 60, replace |
| 14 | 0 | 0 / - | 0 / - | None/0.0, None, -10 dev 60, replace |
| 16 | 0 | 67 / 0.00 | 0 / - | None/0.0, None, -10 dev 60, replace |
| 17 | 0 | 0 / - | 0 / - | None/0.0, None, -10 dev 60, replace |
| 18 | 0 | 0 / - | 0 / - | None/0.0, None, -10 dev 60, replace |

IoU is undefined (shown -) on holes with no OB in either; cells predicted there are false positives (the 'pred' column).

## Decision impact (product decide.py quick, Black tees vs spirit_hollow/output/final_decision.json)

| OB variant | same club | changed clubs vs no-OB |
|---|---|---|
| none | 9/14 | - |
| geometry | 9/14 | - |
| inferred | 9/14 | - |
| hand | 9/14 | - |

| hole | final_decision | none | geometry | inferred | hand |
|---|---|---|---|---|---|
| 1 | 4-wood | Driver | Driver | Driver | Driver |
| 2 | Driver | Driver | Driver | Driver | Driver |
| 4 | Driver | Driver | Driver | Driver | Driver |
| 5 | 2-wood | 4-wood | 4-wood | 4-wood | 4-wood |
| 6 | Driver | Driver | Driver | Driver | Driver |
| 8 | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood |
| 9 | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood |
| 10 | 4-wood | Driver | Driver | Driver | Driver |
| 11 | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood |
| 13 | Driver | Driver | Driver | Driver | Driver |
| 14 | 2-wood | 2-wood | 2-wood | 2-wood | 2-wood |
| 16 | Driver | 4-wood | 4-wood | 4-wood | 4-wood |
| 17 | Driver | Driver | Driver | Driver | Driver |
| 18 | 2-wood | Driver | Driver | Driver | Driver |
