# Heritage Park Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 5, 7, 9, 12, 18

* page: `course_data/library/heritage_park/page.html` (4.6 MB); request `course_data/requests/course_page_heritage_park.json`; built 2026-10-30T03:44Z
* course: Heritage Park Golf Course (Olathe, KS), OSM way/254360563; holes: v2+structure (tier mapped_card); card: golfify (golfify)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [50, 60, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-16; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* holes not all mapped in OSM (hole method: v2+structure)
* 16 holes built vs the card's 18
* pars sum to 64, card 71
* 5 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver +8 |  |
| 4 | 3 | PASS |  |  |
| 5 | 5 | CHECK | Driver -20 | tee: tee marker not on an OSM tee box (lidar_pad; 22 yds from the nearest OSM tee box) |
| 6 | 3 | PASS |  |  |
| 7 | 4 | CHECK | Driver -40 | tee: tee marker not on an OSM tee box (lidar_pad; 44 yds from the nearest OSM tee box) |
| 8 | 4 | PASS | Driver -8 |  |
| 9 | 5 | CHECK | Driver +31 | tee: tee marker not on an OSM tee box (lidar_pad; 65 yds from the nearest OSM tee box) |
| 10 | 4 | PASS | 4-wood +12 |  |
| 12 | 4 | CHECK | Driver -32 | tee: tee marker not on an OSM tee box (walkback; 50 yds from the nearest OSM tee box) |
| 13 | 4 | PASS | Driver -26 |  |
| 14 | 4 | PASS | Driver -22 |  |
| 15 | 5 | PASS | Driver -25 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver +0 |  |
| 18 | 5 | CHECK | Driver +11 | tee: tee marker not on an OSM tee box (walkback; 38 yds from the nearest OSM tee box) |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver +10 |  |
| 4 | 3 | PASS |  |  |
| 5 | 5 | CHECK | Driver -10 | tee: tee marker not on an OSM tee box (lidar_pad; 19 yds from the nearest OSM tee box) |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | Driver +32 |  |
| 8 | 4 | PASS | Driver -7 |  |
| 9 | 5 | CHECK | Driver +17 | tee: tee marker not on an OSM tee box (walkback; 25 yds from the nearest OSM tee box) |
| 10 | 4 | PASS | 4-wood +22 |  |
| 12 | 4 | CHECK | Driver -14 | tee: tee marker not on an OSM tee box (lidar_pad; 45 yds from the nearest OSM tee box) |
| 13 | 4 | PASS | Driver -20 |  |
| 14 | 4 | PASS | Driver -24 |  |
| 15 | 5 | PASS | Driver -26 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver -10 |  |
| 18 | 5 | CHECK | Driver +14 | yardage: measured 500 vs card 511 (-11) |

