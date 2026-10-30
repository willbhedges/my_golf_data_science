# Brown Deer Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 4, 7, 8, 9, 10, 13, 14, 15, 16, 18

* page: `course_data/library/brown_deer/page.html` (4.6 MB); request `course_data/requests/course_page_brown_deer.json`; built 2026-10-30T12:11Z
* course: Brown Deer Golf Club (Coralville, IA), OSM way/191258543; holes: v2+structure (tier mapped_card); card: golfify (golfify)
* solved tee sets: Gold, Blue (the two longest sets on the card (combination sets skipped)); page sets: Gold, Blue
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [45, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-09-01; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* holes not all mapped in OSM (hole method: v2+structure)
* 17 holes built vs the card's 18
* pars sum to 67, card 71
* 10 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 2 | 5 | PASS | Driver +15 |  |
| 3 | 4 | PASS | Driver +19 |  |
| 4 | 5 | CHECK | Driver +32 | tee: tee marker not on an OSM tee box (lidar_pad; 28 yds from the nearest OSM tee box); yardage: measured 525 vs card 513 (+12) |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Driver -14 |  |
| 7 | 4 | CHECK | Long iron -40 | tee: tee marker not on an OSM tee box (walkback; 61 yds from the nearest OSM tee box); aim: Long iron -40 lands 224 yds out in rough (16 yds from fairway) |
| 8 | 4 | CHECK | 4-wood -12 | tee: tee marker not on an OSM tee box (walkback; 191 yds from the nearest OSM tee box); aim: 4-wood -12 lands 275 yds out in rough (7 yds from fairway) |
| 9 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 67 yds from the nearest OSM tee box) |
| 10 | 5 | CHECK | Driver -40 | aim: Driver -40 lands 305 yds out in water (25 yds from fairway); oval: landing pattern 84% trees / water / OB (water 83%, unverified 3%) |
| 11 | 4 | PASS | 4-wood -2 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | CHECK | 2-wood +16 | tee: tee marker not on an OSM tee box (lidar_pad; 25 yds from the nearest OSM tee box) |
| 14 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 106 yds from the nearest OSM tee box) |
| 15 | 5 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (lidar_pad; 45 yds from the nearest OSM tee box); aim: Driver +40 lands 312 yds out in rough (14 yds from fairway); oval: landing pattern 54% trees / water / OB (recovery 42%, ob 12%) |
| 16 | 4 | CHECK | Driver -22 | tee: tee marker not on an OSM tee box (lidar_pad; 39 yds from the nearest OSM tee box); yardage: measured 445 vs card 459 (-14) |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | Mid iron -38 | tee: tee marker not on an OSM tee box (lidar_pad; 49 yds from the nearest OSM tee box); aim: Mid iron -38 lands 201 yds out in rough (81 yds from fairway) |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 2 | 5 | PASS | Driver +14 |  |
| 3 | 4 | PASS | Driver +16 |  |
| 4 | 5 | PASS | Driver +38 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Driver -8 |  |
| 7 | 4 | CHECK | Mid iron -40 | tee: tee marker not on an OSM tee box (walkback; 47 yds from the nearest OSM tee box); aim: Mid iron -40 lands 193 yds out in rough (17 yds from fairway) |
| 8 | 4 | CHECK | 4-wood -38 | tee: tee marker not on an OSM tee box (lidar_pad; 162 yds from the nearest OSM tee box); aim: 4-wood -38 lands 275 yds out in rough (46 yds from fairway) |
| 9 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_centroid; 83 yds from the nearest OSM tee box) |
| 10 | 5 | CHECK | Driver -40 (tie) | tee: tee marker not on an OSM tee box (tee_axis; 7 yds from the nearest OSM tee box); aim: Driver -40 lands 305 yds out in water (41 yds from fairway); oval: landing pattern 100% trees / water / OB (water 100%) |
| 11 | 4 | PASS | Driver +9 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | 4-wood +2 |  |
| 14 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 94 yds from the nearest OSM tee box) |
| 15 | 5 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (lidar_pad; 28 yds from the nearest OSM tee box) |
| 16 | 4 | PASS | 4-wood -26 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | Mid iron -40 | tee: tee marker not on an OSM tee box (lidar_pad; 32 yds from the nearest OSM tee box); aim: Mid iron -40 lands 206 yds out in rough (45 yds from fairway) |

