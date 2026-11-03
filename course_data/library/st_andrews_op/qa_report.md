# St Andrews Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 5, 9, 10, 15

* page: `course_data/library/st_andrews_op/page.html` (5.2 MB); request `course_data/requests/course_page_st_andrews_op.json`; built 2026-11-02T23:47Z
* course: St Andrews Golf Club (Overland Park, KS), OSM way/68744841; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-16; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): holes 2 (1 asked of 13 framed holes; 1 kept on the page's own picks)

Course-level reasons:

* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -22 |  |
| 2 | 4 | PASS | Driver -21 |  |
| 3 | 4 | PASS | 4-wood -14 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | CHECK | 4-wood -52 | wide_aim: 4-wood aim -52 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 6 | 3 | PASS |  |  |
| 7 | 5 | PASS | Driver -4 |  |
| 8 | 4 | PASS | Driver -10 (tie) |  |
| 9 | 4 | CHECK | 4-wood +1 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 10 | 5 | CHECK | Driver +22 | tee: tee marker not on an OSM tee box (lidar_pad; 25 yds from the nearest OSM tee box) |
| 11 | 4 | PASS | 4-wood -6 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver -26 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | CHECK | 4-wood -39 | aim: 4-wood -39 lands 286 yds out in rough (10 yds from fairway) |
| 16 | 4 | PASS | Driver +21 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | 4-wood -1 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -6 |  |
| 2 | 4 | PASS | Driver -30 |  |
| 3 | 4 | PASS | 4-wood -22 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | CHECK | 4-wood -55 | aim: 4-wood -55 lands 260 yds out in rough (11 yds from fairway); wide_aim: 4-wood aim -55 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 6 | 3 | PASS |  |  |
| 7 | 5 | PASS | Driver -4 |  |
| 8 | 4 | PASS | Driver -10 |  |
| 9 | 4 | PASS | 4-wood -6 |  |
| 10 | 5 | PASS | Driver +30 |  |
| 11 | 4 | PASS | 4-wood -6 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver -30 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | CHECK | 4-wood -30 | aim: 4-wood -30 lands 287 yds out in recovery (22 yds from fairway); oval: landing pattern 73% trees / water / OB (recovery 65%, water 8%) |
| 16 | 4 | PASS | Driver +22 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | 4-wood +1 |  |

