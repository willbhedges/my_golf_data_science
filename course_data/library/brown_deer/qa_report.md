# Brown Deer Golf Club: automatic page QA

**Status: blocked** — confirm holes 4, 7, 8, 9, 10, 12, 13, 14, 15, 16, 18

* page: `course_data/library/brown_deer/page.html` (4.8 MB); request `course_data/requests/course_page_brown_deer.json`; built 2026-11-26T07:59Z
* course: Brown Deer Golf Club (Coralville, IA), OSM way/191258543; holes: v2+structure (tier mapped_card); card: golfify (golfify)
* solved tee sets: Gold, Blue (the two longest sets on the card (combination sets skipped)); page sets: Gold, Blue
* weather: forecast for 2026-11-28, 2026-11-29; grid temperatures [35, 45, 55] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-09-01; package imagery 2025
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Gold tees, library check cards): holes 7, 3 (2 asked of 12 framed holes (priors: native_auto p; automatic band off: course gate shut: 0% of sides >= 0.675 (< 25%)); 2 kept on the page's own picks)

Course-level reasons:

* 17 holes built, the card has 18: holes are missing or mis-routed
* built pars sum to 67, the card's to 71 (more than 2 apart): holes or pars are wrong
* holes not all mapped in OSM (hole method: v2+structure)
* 17 holes built vs the card's 18
* pars sum to 67, card 71
* 11 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 2 | 5 | PASS | Driver +15 |  |
| 3 | 4 | PASS | Driver +20 |  |
| 4 | 5 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (tee_axis; 9 yds from the nearest OSM tee box) |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Driver -14 |  |
| 7 | 4 | CHECK | Driver -10 | yardage: measured 321 vs card 383 (-62); aim: Driver -10 lands 301 yds out in rough (12 yds from fairway) |
| 8 | 4 | CHECK | Driver -16 | tee: tee marker not on an OSM tee box (tee_axis_far_cap; 86 yds from the nearest OSM tee box); yardage: measured 283 vs card 414 (-131); aim: Driver -16 lands 296 yds out in rough (9 yds from fairway) |
| 9 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 67 yds from the nearest OSM tee box) |
| 10 | 5 | CHECK | Driver -40 | aim: Driver -40 lands 305 yds out in water (25 yds from fairway); oval: landing pattern 57% trees / water / OB (water 57%, unverified 0%) |
| 11 | 4 | PASS | 4-wood -2 (tie) |  |
| 12 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 3 yds from the nearest OSM tee box) |
| 13 | 4 | CHECK | 2-wood +15 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 25 yds from the nearest OSM tee box) |
| 14 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 106 yds from the nearest OSM tee box) |
| 15 | 5 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (lidar_pad; 45 yds from the nearest OSM tee box); aim: Driver +40 lands 312 yds out in recovery (14 yds from fairway); oval: landing pattern 68% trees / water / OB (recovery 28%, ob 36%, unverified 6%) |
| 16 | 4 | CHECK | Driver -22 | tee: tee marker not on an OSM tee box (lidar_pad; 47 yds from the nearest OSM tee box) |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | Long iron -39 | aim: Long iron -39 lands 234 yds out in rough (43 yds from fairway); wide_aim: Long iron aim -51 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 2 | 5 | PASS | Driver +15 |  |
| 3 | 4 | PASS | Driver +16 |  |
| 4 | 5 | PASS | Driver +40 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Driver -1 |  |
| 7 | 4 | CHECK | Driver -10 | yardage: measured 321 vs card 369 (-48); aim: Driver -10 lands 301 yds out in rough (12 yds from fairway) |
| 8 | 4 | CHECK | Driver -16 | tee: tee marker not on an OSM tee box (tee_axis_far_cap; 86 yds from the nearest OSM tee box); yardage: measured 283 vs card 388 (-105); aim: Driver -16 lands 296 yds out in rough (9 yds from fairway) |
| 9 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_centroid; 83 yds from the nearest OSM tee box) |
| 10 | 5 | CHECK | 2-wood -40 (tie) | tee: tee marker not on an OSM tee box (tee_axis; 7 yds from the nearest OSM tee box); aim: 2-wood -40 lands 285 yds out in water (33 yds from fairway); oval: landing pattern 82% trees / water / OB (water 80%, unverified 4%) |
| 11 | 4 | PASS | Long iron -4 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | 4-wood +2 |  |
| 14 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 94 yds from the nearest OSM tee box) |
| 15 | 5 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (lidar_pad_capped; 23 yds from the nearest OSM tee box); yardage: measured 463 vs card 474 (-11); oval: landing pattern 57% trees / water / OB (recovery 40%, ob 15%, unverified 4%) |
| 16 | 4 | PASS | 4-wood -24 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | Mid iron -40 | tee: tee marker not on an OSM tee box (lidar_pad; 32 yds from the nearest OSM tee box); aim: Mid iron -40 lands 206 yds out in rough (45 yds from fairway); wide_aim: Mid iron aim -56 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |

