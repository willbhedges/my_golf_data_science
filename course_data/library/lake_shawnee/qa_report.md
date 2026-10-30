# Lake Shawnee Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 4

* page: `course_data/library/lake_shawnee/page.html` (1.3 MB); request `course_data/requests/course_page_lake_shawnee.json`; built 2026-10-30T03:59Z
* course: Lake Shawnee Golf Course (Topeka, KS), OSM relation/2053245; holes: structure (tier unmapped_card); card: golfify (golfify)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [55, 65, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-16; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* holes not all mapped in OSM (hole method: structure)
* 4 holes built vs the card's 18
* pars sum to 15, card 70
* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | 4-wood +5 | yardage: measured 362 vs card 348 (+14) |
| 2 | 4 | CHECK | Driver +32 | tee: tee marker not on an OSM tee box (lidar_pad; 16 yds from the nearest OSM tee box) |
| 3 | 4 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (lidar_pad; 6 yds from the nearest OSM tee box) |
| 4 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 125 yds from the nearest OSM tee box) |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +4 | tee: tee marker not on an OSM tee box (walkback; 28 yds from the nearest OSM tee box) |
| 2 | 4 | PASS | Driver +15 |  |
| 3 | 4 | CHECK | Driver -1 | tee: tee marker not on an OSM tee box (walkback; 38 yds from the nearest OSM tee box) |
| 4 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 144 yds from the nearest OSM tee box) |

