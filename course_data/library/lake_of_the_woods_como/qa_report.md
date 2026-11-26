# Lake of the Woods Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 3, 7, 9, 14, 15, 17

* page: `course_data/library/lake_of_the_woods_como/page.html` (2.6 MB); request `course_data/requests/course_page_lake_of_the_woods_como.json`; built 2026-11-26T16:01Z
* course: Lake of the Woods Golf Course (Columbia, MO), OSM way/387184389; holes: osm (tier mapped_card); card: course_data/library/lake_of_the_woods_como/routed_card.json (file)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-11-28, 2026-11-29; grid temperatures [35, 45, 55] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-06-20; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Blue tees, library check cards): none (0 asked of 14 framed holes (priors: native_auto p; automatic band off: course gate shut: 0% of sides >= 0.675 (< 25%)))

Course-level reasons:

* holes placed from aerial photos (OpenStreetMap does not map them all): 3 marked approximate (9, 14, 17)
* 6 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +12 (tie) |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | CHECK | 4-wood +6 | tee: tee marker not on an OSM tee box (tee_axis; 10 yds from the nearest OSM tee box) |
| 4 | 4 | PASS | Driver +10 |  |
| 5 | 4 | PASS | 4-wood -5 |  |
| 6 | 4 | PASS | Driver +16 |  |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 8 | 4 | PASS | 4-wood -16 |  |
| 9 | 5 | CHECK | 4-wood +22 | yardage: measured 367 vs card 495 (-128) |
| 10 | 3 | PASS |  |  |
| 11 | 5 | PASS | Long iron +12 |  |
| 12 | 4 | PASS | Long iron -0 |  |
| 13 | 4 | PASS | Driver -17 |  |
| 14 | 4 | CHECK | 4-wood -38 | tee: tee marker not on an OSM tee box (tee_axis_capped; 20 yds from the nearest OSM tee box); yardage: measured 304 vs card 377 (-73) |
| 15 | 4 | CHECK | Long iron -0 | wide_aim: 2-wood aim -66 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 16 | 5 | PASS | Driver -6 |  |
| 17 | 3 | CHECK |  | yardage: measured 103 vs card 165 (-62) |
| 18 | 4 | PASS | Driver +6 (tie) |  |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +12 (tie) |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Long iron +12 |  |
| 4 | 4 | PASS | Driver +10 |  |
| 5 | 4 | PASS | Driver +0 |  |
| 6 | 4 | PASS | Driver -6 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | 4-wood -16 |  |
| 9 | 5 | CHECK | 4-wood +22 | yardage: measured 367 vs card 495 (-128) |
| 10 | 3 | PASS |  |  |
| 11 | 5 | PASS | Long iron +12 |  |
| 12 | 4 | PASS | Long iron -0 |  |
| 13 | 4 | PASS | Driver -8 |  |
| 14 | 4 | PASS | 4-wood -15 |  |
| 15 | 4 | CHECK | Long iron -2 | wide_aim: 2-wood aim -62 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 16 | 5 | PASS | Driver -6 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver +6 (tie) |  |

