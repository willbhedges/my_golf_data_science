# South River Golf Course: automatic page QA

**Status: blocked** — confirm holes 1, 2, 4, 5, 7, 8, 9

* page: `course_data/library/queenstown_harbor/page.html` (1.9 MB); request `course_data/requests/course_page_queenstown_harbor.json`; built 2026-11-03T15:03Z
* course: South River Golf Course (Edgewater, MD), OSM way/61239088; holes: structure (tier unmapped_card); card: golfify (golfify)
* solved tee sets: Green, Blue (the two longest sets on the card (combination sets skipped)); page sets: Green, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [40, 50, 60] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-07-13; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Green tees, library check cards): none (not asked: no agent_layers in the request)

Course-level reasons:

* 9 holes built, the card has 18: holes are missing or mis-routed
* built pars sum to 36, the card's to 71 (more than 2 apart): holes or pars are wrong
* resolved to 'South River Golf Course' 36.1 km from the request's near point with match score 0.42 (< 0.5): probably not the requested course
* holes not all mapped in OSM (hole method: structure)
* OSM greens 7 of 9 holes
* 9 holes built vs the card's 18
* pars sum to 36, card 71
* 7 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Green tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -12 (tie) | tee: tee marker not on an OSM tee box (walkback; 49 yds from the nearest OSM tee box); aim: Driver -12 lands 309 yds out in rough (56 yds from fairway); oval: landing pattern 41% trees / water / OB (recovery 3%, ob 38%) |
| 2 | 4 | PASS | Driver -5 |  |
| 3 | 3 | PASS |  |  |
| 4 | 5 | CHECK | Driver -40 | tee: tee marker not on an OSM tee box (tee_axis; 10 yds from the nearest OSM tee box) |
| 5 | 4 | CHECK | 4-wood +38 | tee: tee marker not on an OSM tee box (walkback; 41 yds from the nearest OSM tee box); aim: 4-wood +38 lands 265 yds out in ob (84 yds from fairway); oval: landing pattern 96% trees / water / OB (recovery 20%, ob 76%) |
| 6 | 3 | PASS |  |  |
| 7 | 5 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (tee_axis; 10 yds from the nearest OSM tee box) |
| 8 | 3 | CHECK |  | yardage: measured 323 vs card 206 (+117) |
| 9 | 5 | CHECK | Long iron -4 | tee: tee marker not on an OSM tee box (walkback_capped; 135 yds from the nearest OSM tee box); yardage: measured 345 vs card 567 (-222); aim: Long iron -4 lands 224 yds out in rough (83 yds from fairway) |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Long iron -3 | tee: tee marker not on an OSM tee box (walkback; 35 yds from the nearest OSM tee box); aim: Long iron -3 lands 220 yds out in rough (57 yds from fairway) |
| 2 | 4 | CHECK | Driver +4 | aim: Driver +4 lands 298 yds out in sand (4 yds from fairway) |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | Driver -40 |  |
| 5 | 4 | CHECK | Mid iron +36 | aim: Mid iron +36 lands 192 yds out in recovery (116 yds from fairway); oval: landing pattern 97% trees / water / OB (recovery 87%, ob 10%) |
| 6 | 3 | PASS |  |  |
| 7 | 5 | PASS | 4-wood +40 |  |
| 8 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 89 yds from the nearest OSM tee box) |
| 9 | 5 | CHECK | Long iron -4 | tee: tee marker not on an OSM tee box (walkback_capped; 135 yds from the nearest OSM tee box); yardage: measured 345 vs card 539 (-194); aim: Long iron -4 lands 224 yds out in rough (83 yds from fairway) |

