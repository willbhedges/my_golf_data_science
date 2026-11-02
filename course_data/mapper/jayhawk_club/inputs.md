# Mapper inputs: The Jayhawk Club (Lawrence, KS)

Base package: `course_data/mapper/jayhawk_club/base/package.json` (built 2026-11-02T02:36:48Z; committed package: tees rebuilt: 0 tee(s) moved). Corridor set **Black**. Sets: Black, Green, White, Combo, Rust.
Photo NAIP 2021; other years: none; lidar canopy: NO (trees can only be checked on the photo); CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 36 candidate pad; vision: missing: no vision_any layers for 'jayhawk_club' (FileNotFoundError: course_data/vision_any/jayhawk_club/raw (; segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: geometry only (OSM outline / buildings / roads): no OB evidence fetched for this course; list it in course_dat

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) |
|---|---|---|---|---|---|
| 1 | 4 | 412 | tee_centroid, 0.9 | Black 412, Green 392, White 360, Combo 285, Rust 285 | fairway 4075, ob 1756 |
| 2 | 5 | 534 | walkback_capped, 0.5 | Black 534, Green 505, White 468, Combo 468, Rust 428 | fairway 2928, sand 24 |
| 3 | 4 | 408 | walkback, 0.5 | Black 408, Green 380, White 339, Combo 339, Rust 300 | ob 1723, recovery 65 |
| 5 | 4 | 396 | lidar_pad, 0.6 | Black 396, Green 381, White 359, Combo 271, Rust 271 | ob 3883, water 41 |
| 6 | 4 | 444 | walkback_capped, 0.5 | Black 444, Green 405, White 370, Combo 258, Rust 258 | fairway 4279, ob 2782, recovery 230, sand 109 |
| 8 | 5 | 512 | walkback_capped, 0.5 | Black 512, Green 471, White 441, Combo 441, Rust 405 | fairway 2939, ob 3177, recovery 220, sand 34, water 883 |
| 9 | 4 | 412 | tee_centroid, 0.9 | Black 412, Green 389, White 354, Combo 354, Rust 272 | fairway 4252, sand 135 |
| 10 | 4 | 408 | lidar_pad, 0.6 | Black 408, Green 386, White 351, Combo 305, Rust 305 | fairway 4530, recovery 14, sand 301, water 909 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
