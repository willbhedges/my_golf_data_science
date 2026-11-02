# Painted Hills Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18

* page: `course_data/library/painted_hills/page.html` (2.4 MB); request `course_data/requests/course_page_painted_hills.json`; built 2026-11-02T17:00Z
* course: Painted Hills Golf Club (Kansas City, KS), OSM relation/8086481; holes: osm (tier unmapped_card); card: golfify (golfify)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2021-06-12,2021-06-13; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Blue tees, library check cards): none (not asked: no agent_layers in the request)

Course-level reasons:

* 17 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +12 | tee: tee marker not on an OSM tee box (lidar_pad; 289 yds from the nearest OSM tee box) |
| 2 | 4 | CHECK | Driver -6 | tee: tee marker not on an OSM tee box (lidar_pad; 319 yds from the nearest OSM tee box) |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 646 yds from the nearest OSM tee box) |
| 4 | 5 | CHECK | Driver -4 | tee: tee marker not on an OSM tee box (lidar_pad; 601 yds from the nearest OSM tee box) |
| 5 | 5 | CHECK | Driver -4 | tee: tee marker not on an OSM tee box (lidar_pad; 205 yds from the nearest OSM tee box) |
| 6 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 536 yds from the nearest OSM tee box) |
| 7 | 4 | CHECK | 2-wood -40 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 637 yds from the nearest OSM tee box) |
| 8 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 423 yds from the nearest OSM tee box) |
| 9 | 4 | CHECK | Driver +22 | tee: tee marker not on an OSM tee box (lidar_pad; 241 yds from the nearest OSM tee box) |
| 10 | 5 | CHECK | Driver +15 | tee: tee marker not on an OSM tee box (texture_pad; 416 yds from the nearest OSM tee box) |
| 11 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 403 yds from the nearest OSM tee box) |
| 12 | 5 | CHECK | Driver -24 | tee: tee marker not on an OSM tee box (lidar_pad; 600 yds from the nearest OSM tee box) |
| 13 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 722 yds from the nearest OSM tee box) |
| 14 | 4 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (lidar_pad; 636 yds from the nearest OSM tee box) |
| 15 | 4 | CHECK | Driver -5 | tee: tee marker not on an OSM tee box (lidar_pad; 618 yds from the nearest OSM tee box) |
| 16 | 4 | CHECK | 4-wood +10 | tee: tee marker not on an OSM tee box (walkback; 404 yds from the nearest OSM tee box) |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | Driver -12 | tee: tee marker not on an OSM tee box (lidar_pad; 228 yds from the nearest OSM tee box) |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +21 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 280 yds from the nearest OSM tee box) |
| 2 | 4 | CHECK | Driver -8 | tee: tee marker not on an OSM tee box (lidar_pad; 336 yds from the nearest OSM tee box) |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 638 yds from the nearest OSM tee box) |
| 4 | 5 | CHECK | Driver -3 | tee: tee marker not on an OSM tee box (lidar_pad; 565 yds from the nearest OSM tee box) |
| 5 | 5 | CHECK | Driver +12 | tee: tee marker not on an OSM tee box (lidar_pad; 214 yds from the nearest OSM tee box) |
| 6 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 541 yds from the nearest OSM tee box) |
| 7 | 4 | CHECK | 2-wood -48 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 620 yds from the nearest OSM tee box) |
| 8 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 401 yds from the nearest OSM tee box) |
| 9 | 4 | CHECK | 2-wood +22 | tee: tee marker not on an OSM tee box (lidar_pad; 228 yds from the nearest OSM tee box) |
| 10 | 5 | CHECK | Driver +23 | tee: tee marker not on an OSM tee box (lidar_pad; 405 yds from the nearest OSM tee box) |
| 11 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 411 yds from the nearest OSM tee box) |
| 12 | 5 | CHECK | Driver -40 | tee: tee marker not on an OSM tee box (lidar_pad; 619 yds from the nearest OSM tee box) |
| 13 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 689 yds from the nearest OSM tee box) |
| 14 | 4 | CHECK | Driver +12 | tee: tee marker not on an OSM tee box (lidar_pad; 633 yds from the nearest OSM tee box) |
| 15 | 4 | CHECK | 4-wood -0 | tee: tee marker not on an OSM tee box (lidar_pad; 597 yds from the nearest OSM tee box) |
| 16 | 4 | CHECK | Driver +13 | tee: tee marker not on an OSM tee box (lidar_pad; 364 yds from the nearest OSM tee box) |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | 2-wood -12 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 207 yds from the nearest OSM tee box) |

