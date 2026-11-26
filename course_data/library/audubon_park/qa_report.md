# Audubon Park Golf Course: automatic page QA

**Status: blocked** — confirm holes 1, 3, 5, 7, 9, 10, 11, 12, 13, 14, 18

* page: `course_data/library/audubon_park/page.html` (2.7 MB); request `course_data/requests/course_page_audubon_park.json`; built 2026-11-26T07:47Z
* course: Audubon Park Golf Course (New Orleans, LA), OSM way/27887431; holes: v2+structure (tier mapped_card); card: golfify (golfify)
* solved tee sets: Gold, Blue (the two longest sets on the card (combination sets skipped)); page sets: Gold, Blue
* weather: forecast for 2026-11-28, 2026-11-29; grid temperatures [50, 65, 80] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-05-03,2023-05-04; package imagery 2025
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Gold tees, library check cards): none (0 asked of 6 framed holes (priors: native_auto p; automatic band off: course gate shut: 0% of sides >= 0.675 (< 25%)))

Course-level reasons:

* 16 holes built, the card has 18: holes are missing or mis-routed
* built pars sum to 56, the card's to 62 (more than 2 apart): holes or pars are wrong
* holes not all mapped in OSM (hole method: v2+structure)
* 16 holes built vs the card's 18
* pars sum to 56, card 62
* 11 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +32 | tee: tee marker not on an OSM tee box (lidar_pad; 39 yds from the nearest OSM tee box) |
| 2 | 3 | PASS |  |  |
| 3 | 3 | PASS |  |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | CHECK | Driver -13 | tee: tee marker not on an OSM tee box (tee_axis; 133 yds from the nearest OSM tee box); aim: Driver -13 lands 297 yds out in rough (9 yds from fairway) |
| 6 | 3 | PASS |  |  |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 105 yds from the nearest OSM tee box) |
| 8 | 3 | PASS |  |  |
| 9 | 5 | CHECK | Long iron +36 | aim: Long iron +36 lands 223 yds out in rough (51 yds from fairway) |
| 10 | 4 | CHECK | Driver +40 | aim: Driver +40 lands 300 yds out in rough (61 yds from fairway) |
| 11 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 286 yds from the nearest OSM tee box) |
| 12 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 425 yds from the nearest OSM tee box) |
| 13 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 343 yds from the nearest OSM tee box) |
| 14 | 4 | CHECK | Driver +16 | tee: tee marker not on an OSM tee box (tee_centroid; 166 yds from the nearest OSM tee box); aim: Driver +16 lands 298 yds out in rough (8 yds from fairway) |
| 16 | 3 | PASS |  |  |
| 18 | 5 | CHECK | Driver +14 | tee: tee marker not on an OSM tee box (lidar_pad; 277 yds from the nearest OSM tee box); aim: Driver +14 lands 305 yds out in rough (172 yds from fairway) |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | 2-wood +10 (tie) | tee: tee marker not on an OSM tee box (tee_axis; 85 yds from the nearest OSM tee box) |
| 2 | 3 | PASS |  |  |
| 3 | 3 | CHECK |  | yardage: measured 264 vs card 200 (+64) |
| 4 | 3 | PASS |  |  |
| 5 | 4 | CHECK | 4-wood -10 | tee: tee marker not on an OSM tee box (tee_axis; 138 yds from the nearest OSM tee box) |
| 6 | 3 | PASS |  |  |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 90 yds from the nearest OSM tee box) |
| 8 | 3 | PASS |  |  |
| 9 | 5 | CHECK | Driver +40 (tie) | aim: Driver +40 lands 303 yds out in rough (62 yds from fairway); oval: landing pattern 46% trees / water / OB (recovery 20%, water 23%, unverified 6%) |
| 10 | 4 | CHECK | Driver +28 | aim: Driver +28 lands 296 yds out in rough (42 yds from fairway) |
| 11 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 304 yds from the nearest OSM tee box) |
| 12 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 413 yds from the nearest OSM tee box) |
| 13 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 322 yds from the nearest OSM tee box) |
| 14 | 4 | CHECK | 4-wood +12 | tee: tee marker not on an OSM tee box (tee_axis; 149 yds from the nearest OSM tee box) |
| 16 | 3 | PASS |  |  |
| 18 | 5 | CHECK | Driver +24 | tee: tee marker not on an OSM tee box (lidar_pad; 256 yds from the nearest OSM tee box); aim: Driver +24 lands 300 yds out in rough (194 yds from fairway) |

