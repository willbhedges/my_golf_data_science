# Anchorage Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 2, 7, 9, 11

* page: `course_data/library/anchorage/page.html` (0.7 MB); request `course_data/requests/course_page_anchorage.json`; built 2026-10-30T21:55Z
* course: Anchorage Golf Course (Anchorage, AK), OSM way/29357224; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [25, 40, 50] F; calm-day picks with 48 prior draws
* imagery on the page: 2,0,2,6,-,0,8,-,2,6; package imagery None
* stages: vision `missing: no vision_any layers for 'anchorage' (FileNotFoundError: no NAIP for anchorage (c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -10 |  |
| 2 | 4 | CHECK | Driver +40 | aim: Driver +40 lands 302 yds out in rough (25 yds from fairway) |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | 2-wood -40 |  |
| 5 | 4 | PASS | Driver -4 |  |
| 6 | 5 | PASS | Driver -8 |  |
| 7 | 4 | PASS | Driver +10 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | CHECK | Driver +12 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 10 | 4 | PASS | Driver -0 |  |
| 11 | 4 | CHECK | Driver +27 | tee: tee marker not on an OSM tee box (tee_axis; 5 yds from the nearest OSM tee box) |
| 12 | 4 | PASS | Driver -14 |  |
| 13 | 3 | PASS |  |  |
| 14 | 5 | PASS | Driver -4 |  |
| 15 | 4 | PASS | Driver -11 |  |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver -4 |  |
| 18 | 4 | PASS | Driver +2 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -10 |  |
| 2 | 4 | CHECK | Driver +40 | aim: Driver +40 lands 303 yds out in rough (24 yds from fairway) |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | 4-wood -40 |  |
| 5 | 4 | PASS | Driver -8 |  |
| 6 | 5 | PASS | Driver -8 |  |
| 7 | 4 | CHECK | Driver +29 | aim: Driver +29 lands 298 yds out in rough (8 yds from fairway) |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver +18 |  |
| 10 | 4 | PASS | Driver +6 |  |
| 11 | 4 | PASS | Driver +37 |  |
| 12 | 4 | PASS | Driver -24 |  |
| 13 | 3 | PASS |  |  |
| 14 | 5 | PASS | Driver -8 |  |
| 15 | 4 | PASS | Driver -12 |  |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver -2 |  |
| 18 | 4 | PASS | Driver -2 |  |

