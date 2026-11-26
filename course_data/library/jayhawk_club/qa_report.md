# The Jayhawk Club: automatic page QA

**Status: blocked** — confirm holes 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

* page: `course_data/library/jayhawk_club/page.html` (1.7 MB); request `course_data/requests/course_page_jayhawk_club.json`; built 2026-11-26T07:53Z
* course: The Jayhawk Club (Lawrence, KS), OSM relation/2053560; holes: structure (tier unmapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Black, Green (the two longest sets on the card (combination sets skipped)); page sets: Black, Green
* weather: forecast for 2026-11-28, 2026-11-29; grid temperatures [40, 50, 60] F; calm-day picks with 48 prior draws
* imagery on the page: 2021-07-29; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): none (0 asked of 8 framed holes (priors: native_auto p; automatic band off: course gate shut: 0% of sides >= 0.675 (< 25%)))

Course-level reasons:

* 10 holes built, the card has 18: holes are missing or mis-routed
* built pars sum to 40, the card's to 72 (more than 2 apart): holes or pars are wrong
* holes out of order: green-to-next-tee walks up to 1123 yds, 1 over 500 (in order: under 800, at most 3 over 500); longest: 8->9 1123, 9->10 493, 1->2 409
* holes not all mapped in OSM (hole method: structure)
* 10 holes built vs the card's 18
* pars sum to 40, card 72
* 10 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood -3 |  |
| 2 | 5 | CHECK | Driver +10 | yardage: measured 412 vs card 534 (-122) |
| 3 | 4 | CHECK | 2-wood -5 | yardage: measured 290 vs card 408 (-118); aim: 2-wood -5 lands 304 yds out in recovery (2 yds from fairway) |
| 4 | 3 | CHECK |  | yardage: measured 538 vs card 208 (+330) |
| 5 | 4 | CHECK | Driver +26 | tee: tee marker not on an OSM tee box (lidar_pad; 24 yds from the nearest OSM tee box); aim: Driver +26 lands 274 yds out in rough (93 yds from fairway); oval: landing pattern 52% trees / water / OB (recovery 52%) |
| 6 | 4 | CHECK | 4-wood -12 | yardage: measured 337 vs card 444 (-107) |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 6 yds from the nearest OSM tee box) |
| 8 | 5 | CHECK | Driver -27 (tie) | yardage: measured 380 vs card 512 (-132) |
| 9 | 4 | PASS | Driver -19 |  |
| 10 | 4 | CHECK | 2-wood +6 (tie) | yardage: measured 299 vs card 408 (-109); aim: 2-wood +6 lands 275 yds out in sand (3 yds from fairway) |

## Green tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -6 | tee: tee marker not on an OSM tee box (lidar_pad; 11 yds from the nearest OSM tee box) |
| 2 | 5 | CHECK | Driver +10 | yardage: measured 412 vs card 505 (-93) |
| 3 | 4 | CHECK | 2-wood -5 | yardage: measured 290 vs card 380 (-90); aim: 2-wood -5 lands 304 yds out in recovery (2 yds from fairway) |
| 4 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 6 yds from the nearest OSM tee box) |
| 5 | 4 | CHECK | Driver +14 | tee: tee marker not on an OSM tee box (lidar_pad; 14 yds from the nearest OSM tee box); aim: Driver +14 lands 273 yds out in rough (84 yds from fairway) |
| 6 | 4 | CHECK | 4-wood -12 | yardage: measured 337 vs card 405 (-68) |
| 7 | 3 | PASS |  |  |
| 8 | 5 | CHECK | 4-wood -28 | aim: 4-wood -28 lands 280 yds out in rough (19 yds from fairway) |
| 9 | 4 | CHECK | Driver -4 | yardage: measured 466 vs card 389 (+77) |
| 10 | 4 | CHECK | 2-wood +6 (tie) | yardage: measured 299 vs card 386 (-87); aim: 2-wood +6 lands 275 yds out in sand (3 yds from fairway) |

