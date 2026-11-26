# The Golf Course at Glen Mills: automatic page QA

**Status: blocked** — confirm holes 4, 6, 9, 10, 12, 17, 18

* page: `course_data/library/glen_mills/page.html` (2.8 MB); request `course_data/requests/course_page_glen_mills.json`; built 2026-11-26T07:53Z
* course: The Golf Course at Glen Mills (Thornbury Township, PA), OSM way/284570622; holes: v2+structure (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-11-28, 2026-11-29; grid temperatures [35, 50, 60] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-05-10,2022-05-17; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): holes 1 (1 asked of 11 framed holes (priors: native_auto p; automatic band off: course gate shut: 0% of sides >= 0.675 (< 25%)); 1 kept on the page's own picks)

Course-level reasons:

* 15 holes built, the card has 18: holes are missing or mis-routed
* built pars sum to 59, the card's to 71 (more than 2 apart): holes or pars are wrong
* holes not all mapped in OSM (hole method: v2+structure)
* 15 holes built vs the card's 18
* pars sum to 59, card 71
* 7 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +0 |  |
| 2 | 4 | PASS | Driver -8 |  |
| 3 | 4 | PASS | 4-wood -2 |  |
| 4 | 5 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 5 | 3 | PASS |  |  |
| 6 | 5 | CHECK | Driver +4 | tee: tee marker not on an OSM tee box (tee_axis; 8 yds from the nearest OSM tee box) |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver +15 |  |
| 9 | 4 | CHECK | 4-wood +10 | yardage: measured 373 vs card 433 (-60) |
| 10 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 139 yds from the nearest OSM tee box) |
| 11 | 4 | PASS | 4-wood +1 (tie) |  |
| 12 | 4 | CHECK | Driver -9 | tee: tee marker not on an OSM tee box (lidar_pad; 7 yds from the nearest OSM tee box) |
| 16 | 3 | PASS |  |  |
| 17 | 5 | CHECK | Driver -12 | tee: tee marker not on an OSM tee box (tee_axis; 3 yds from the nearest OSM tee box) |
| 18 | 4 | PASS | Driver +38 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +4 |  |
| 2 | 4 | PASS | Driver -16 |  |
| 3 | 4 | PASS | Driver -14 |  |
| 4 | 5 | CHECK | Driver -8 | aim: Driver -8 lands 307 yds out in rough (9 yds from fairway) |
| 5 | 3 | PASS |  |  |
| 6 | 5 | PASS | Driver +16 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver +16 |  |
| 9 | 4 | PASS | 4-wood +10 |  |
| 10 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 133 yds from the nearest OSM tee box) |
| 11 | 4 | PASS | 4-wood -12 (tie) |  |
| 12 | 4 | CHECK | Driver -6 | tee: tee marker not on an OSM tee box (lidar_pad; 9 yds from the nearest OSM tee box) |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver -14 |  |
| 18 | 4 | CHECK | Driver +32 | yardage: measured 504 vs card 427 (+77) |

