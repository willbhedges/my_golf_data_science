# Teton Pines Country Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 4, 7, 10, 13, 18

* page: `course_data/library/teton_pines/page.html` (2.9 MB); request `course_data/requests/course_page_teton_pines.json`; built 2026-10-31T05:30Z
* course: Teton Pines Country Club (Wilson, WY), OSM way/185769563; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [20, 35, 50] F; calm-day picks with 48 prior draws
* imagery on the page: 2015-09-12; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* scorecard not matched (source opengolfapi, flags ['Blue: holes sum to 6906 but the source says 6888 (+18): mixed card versions', 'Palmer: holes sum to 6604 but the source says 6585 (+19): mixed card versions'])
* 7 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -1 | tee: tee marker not on an OSM tee box (walkback; 18 yds from the nearest OSM tee box) |
| 2 | 5 | CHECK | Driver +3 | tee: tee marker not on an OSM tee box (walkback; 20 yds from the nearest OSM tee box) |
| 3 | 3 | PASS |  |  |
| 4 | 4 | CHECK | Driver -1 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 13 yds from the nearest OSM tee box) |
| 5 | 4 | PASS | Driver +2 |  |
| 6 | 4 | PASS | Driver +2 |  |
| 7 | 5 | CHECK | Driver -5 | tee: tee marker not on an OSM tee box (walkback; 15 yds from the nearest OSM tee box) |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -4 |  |
| 10 | 5 | CHECK | Driver -6 | tee: tee marker not on an OSM tee box (lidar_pad; 10 yds from the nearest OSM tee box) |
| 11 | 4 | PASS | Driver +1 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | CHECK | Driver -14 | tee: tee marker not on an OSM tee box (lidar_pad; 55 yds from the nearest OSM tee box) |
| 14 | 5 | PASS | Driver -4 |  |
| 15 | 4 | PASS | Driver -4 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | 4-wood +11 |  |
| 18 | 4 | CHECK | Driver -0 | tee: tee marker not on an OSM tee box (walkback_capped; 41 yds from the nearest OSM tee box) |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +11 |  |
| 2 | 5 | PASS | Driver +0 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | 4-wood -2 (tie) |  |
| 5 | 4 | PASS | Driver -8 |  |
| 6 | 4 | PASS | Driver -2 (tie) |  |
| 7 | 5 | PASS | Driver -11 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -3 |  |
| 10 | 5 | CHECK | Driver -1 | tee: tee marker not on an OSM tee box (lidar_pad; 18 yds from the nearest OSM tee box) |
| 11 | 4 | PASS | Driver +8 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver -2 |  |
| 14 | 5 | PASS | Driver -4 |  |
| 15 | 4 | PASS | 4-wood -3 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | 4-wood +11 |  |
| 18 | 4 | PASS | 4-wood +4 |  |

