# Ironhorse Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 7, 11

* page: `course_data/library/ironhorse/page.html` (5.7 MB); request `course_data/requests/course_page_ironhorse.json`; built 2026-11-26T20:26Z
* course: Ironhorse Golf Club (Leawood, KS), OSM way/237531758; holes: v2+structure (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-11-28, 2026-11-29; grid temperatures [35, 45, 55] F; calm-day picks with 48 prior draws
* imagery on the page: 2025-05-11; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): holes 14 (1 asked of 14 framed holes (priors: native_auto p; automatic band off: course gate shut: 0% of sides >= 0.675 (< 25%)); 1 kept on the page's own picks)

Course-level reasons:

* holes not all mapped in OSM (hole method: v2+structure)
* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +9 | yardage: measured 413 vs card 374 (+39) |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver +4 |  |
| 4 | 5 | PASS | Driver -3 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | 2-wood -4 (tie) |  |
| 7 | 4 | PASS | Long iron +8 (tie) |  |
| 8 | 4 | PASS | 4-wood -8 |  |
| 9 | 5 | PASS | Driver -6 |  |
| 10 | 5 | PASS | Driver -6 |  |
| 11 | 4 | CHECK | Driver +10 | yardage: measured 312 vs card 371 (-59) |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | 4-wood -4 |  |
| 14 | 5 | PASS | Driver +29 |  |
| 15 | 4 | PASS | 4-wood -4 |  |
| 16 | 4 | PASS | 4-wood +5 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver +4 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -21 |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver +2 |  |
| 4 | 5 | PASS | Driver +3 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | 4-wood -3 |  |
| 7 | 4 | CHECK | Driver -39 | aim: Driver -39 lands 295 yds out in rough (12 yds from fairway); wide_aim: Driver aim -45 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 8 | 4 | PASS | 4-wood -14 |  |
| 9 | 5 | PASS | Driver -8 |  |
| 10 | 5 | PASS | Driver -4 |  |
| 11 | 4 | PASS | Driver +18 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | 4-wood +7 |  |
| 14 | 5 | PASS | Driver +31 |  |
| 15 | 4 | PASS | Driver -40 |  |
| 16 | 4 | PASS | 4-wood +6 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | 4-wood +4 |  |

