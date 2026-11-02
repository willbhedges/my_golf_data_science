# Gaylord Springs Golf Links: automatic page QA

**Status: needs confirm** — confirm holes 2, 3

* page: `course_data/library/gaylord_springs/page.html` (0.4 MB); request `course_data/requests/course_page_gaylord_springs.json`; built 2026-11-01T20:48Z
* course: Gaylord Springs Golf Links (Nashville, TN), OSM way/499135540; holes: structure (tier unmapped_card); card: allsquare (allsquare)
* solved tee sets: Black, Gold (the two longest sets on the card (combination sets skipped)); page sets: Black, Gold
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [50, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-05-25; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* holes not all mapped in OSM (hole method: structure)
* 3 holes built vs the card's 18
* pars sum to 12, card 72
* 2 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver +5 |  |
| 2 | 4 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (lidar_pad; 424 yds from the nearest OSM tee box) |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 46 yds from the nearest OSM tee box) |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver +6 |  |
| 2 | 4 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (lidar_pad; 404 yds from the nearest OSM tee box) |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 35 yds from the nearest OSM tee box) |

