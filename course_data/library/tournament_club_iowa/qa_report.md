# Tournament Club of Iowa: automatic page QA

**Status: needs confirm** — confirm holes 1, 5, 6, 7, 10, 11, 14, 15, 16

* page: `course_data/library/tournament_club_iowa/page.html` (5.2 MB); request `course_data/requests/course_page_tournament_club_iowa.json`; built 2026-11-02T23:41Z
* course: Tournament Club of Iowa (Polk City, IA), OSM relation/1507320; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: King, Palmer (the two longest sets on the card (combination sets skipped)); page sets: King, Palmer
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [40, 50, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-09-02; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (King tees, library check cards): none (not asked: no agent_layers in the request)

Course-level reasons:

* 9 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## King tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | 2-wood -14 | tee: tee marker not on an OSM tee box (review; 21 yds from the nearest OSM tee box) |
| 2 | 4 | PASS | Driver -8 |  |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | Driver -36 |  |
| 5 | 3 | CHECK |  | yardage: measured 174 vs card 185 (-11) |
| 6 | 4 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (review; 17 yds from the nearest OSM tee box) |
| 7 | 4 | CHECK | Driver -40 (tie) | yardage: measured 374 vs card 386 (-12) |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -10 |  |
| 10 | 4 | CHECK | Driver -27 | aim: Driver -27 lands 319 yds out in rough (9 yds from fairway) |
| 11 | 4 | CHECK | 4-wood +1 | tee: tee marker not on an OSM tee box (review; 18 yds from the nearest OSM tee box) |
| 12 | 4 | PASS | 4-wood +2 |  |
| 13 | 5 | PASS | Driver -6 |  |
| 14 | 4 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (review; 18 yds from the nearest OSM tee box) |
| 15 | 3 | PASS |  |  |
| 16 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (review; 16 yds from the nearest OSM tee box) |
| 17 | 5 | PASS | Driver +12 |  |
| 18 | 4 | PASS | Driver -4 |  |

## Palmer tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | 4-wood -2 | aim: 4-wood -2 lands 295 yds out in rough (18 yds from fairway); wide_aim: Driver aim -63 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 2 | 4 | PASS | Driver -4 |  |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | Driver -40 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | 4-wood +0 |  |
| 7 | 4 | CHECK | 2-wood -54 (tie) | wide_aim: 2-wood aim -54 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -2 |  |
| 10 | 4 | CHECK | Driver -28 | aim: Driver -28 lands 317 yds out in rough (9 yds from fairway) |
| 11 | 4 | CHECK | 4-wood -0 | tee: tee marker not on an OSM tee box (review; 16 yds from the nearest OSM tee box) |
| 12 | 4 | PASS | 4-wood +2 |  |
| 13 | 5 | PASS | Driver -4 |  |
| 14 | 4 | CHECK | 2-wood +13 (tie) | tee: tee marker not on an OSM tee box (review; 20 yds from the nearest OSM tee box) |
| 15 | 3 | CHECK |  | yardage: measured 193 vs card 182 (+11) |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver -6 |  |
| 18 | 4 | PASS | 2-wood -5 (tie) |  |

