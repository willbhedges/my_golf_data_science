# Cabot Citrus Farms: automatic page QA

**Status: blocked** — confirm holes 3, 4, 6, 7, 8, 9, 10, 11, 12, 15, 17

* page: `course_data/library/world_woods/page.html` (4.5 MB); request `course_data/requests/course_page_world_woods.json`; built 2026-11-26T12:20Z
* course: Cabot Citrus Farms ( Brooksville , FL), OSM way/410646892; holes: v2+structure (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Silver (the two longest sets on the card (combination sets skipped)); page sets: Black, Silver
* weather: climate normals for 2026-11-28, 2026-11-29; grid temperatures [55, 65, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2025-05-16; package imagery 2025
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): none (0 asked of 12 framed holes (priors: native_auto p; automatic band off: course gate shut: 0% of sides >= 0.675 (< 25%)))

Course-level reasons:

* 16 holes built, the card has 18: holes are missing or mis-routed
* built pars sum to 64, the card's to 72 (more than 2 apart): holes or pars are wrong
* holes out of order: green-to-next-tee walks up to 1315 yds, 1 over 500 (in order: under 800, at most 3 over 500); longest: 9->10 1315, 14->15 192, 16->17 124
* holes not all mapped in OSM (hole method: v2+structure)
* scorecard not matched (source golfify, flags ['1 hole(s) where a longer set is shorter than the next set: 1 Yellow(W) 300 < Green(M) 334'])
* 16 holes built vs the card's 18
* pars sum to 64, card 72
* 11 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -34 |  |
| 3 | 3 | CHECK |  | yardage: measured 238 vs card 292 (-54) |
| 4 | 5 | CHECK | Driver +2 | yardage: measured 446 vs card 511 (-65) |
| 5 | 4 | PASS | Long iron +40 |  |
| 6 | 5 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box); aim: Driver +40 lands 313 yds out in rough (7 yds from fairway) |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 5 yds from the nearest OSM tee box) |
| 8 | 4 | CHECK | 4-wood +32 (tie) | yardage: measured 375 vs card 426 (-51) |
| 9 | 4 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (walkback; 24 yds from the nearest OSM tee box) |
| 10 | 3 | CHECK |  | yardage: measured 195 vs card 242 (-47) |
| 11 | 4 | CHECK | Long iron -27 | tee: tee marker not on an OSM tee box (tee_axis; 10 yds from the nearest OSM tee box) |
| 12 | 4 | CHECK | 4-wood -28 | yardage: measured 420 vs card 496 (-76) |
| 14 | 5 | PASS | Driver -24 |  |
| 15 | 4 | CHECK | 4-wood -6 (tie) | aim: 4-wood -6 lands 259 yds out in recovery (95 yds from fairway); oval: landing pattern 55% trees / water / OB (recovery 55%) |
| 16 | 3 | PASS |  |  |
| 17 | 5 | CHECK | Driver +32 | yardage: measured 390 vs card 500 (-110) |
| 18 | 4 | PASS | 4-wood -40 (tie) |  |

## Silver tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood -32 (tie) |  |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 4 | 5 | CHECK | Driver -4 | tee: tee marker not on an OSM tee box (walkback; 35 yds from the nearest OSM tee box) |
| 5 | 4 | PASS | Mid iron +40 |  |
| 6 | 5 | PASS | Driver -40 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | CHECK | Driver +32 (tie) | tee: tee marker not on an OSM tee box (tee_axis; 11 yds from the nearest OSM tee box) |
| 9 | 4 | PASS | Driver +10 |  |
| 10 | 3 | PASS |  |  |
| 11 | 4 | PASS | Mid iron -28 |  |
| 12 | 4 | CHECK | 4-wood -28 | yardage: measured 420 vs card 472 (-52) |
| 14 | 5 | PASS | Driver -38 |  |
| 15 | 4 | CHECK | Driver -40 | tee: tee marker not on an OSM tee box (tee_axis; 81 yds from the nearest OSM tee box); aim: Driver -40 lands 299 yds out in recovery (21 yds from fairway); oval: landing pattern 68% trees / water / OB (recovery 64%, unverified 8%) |
| 16 | 3 | PASS |  |  |
| 17 | 5 | CHECK | Driver +32 | yardage: measured 390 vs card 460 (-70) |
| 18 | 4 | PASS | Driver -40 |  |

