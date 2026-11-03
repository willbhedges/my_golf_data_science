# Tournament Club of Iowa: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 5, 6, 7, 10, 11, 12, 14, 16, 18

* page: `course_data/library/tournament_club_iowa/page.html` (5.2 MB); request `course_data/requests/course_page_tournament_club_iowa.json`; built 2026-11-03T13:06Z
* course: Tournament Club of Iowa (Polk City, IA), OSM relation/1507320; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: King, Palmer (the two longest sets on the card (combination sets skipped)); page sets: King, Palmer
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [40, 50, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-09-02; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (King tees, library check cards): holes 6 (1 asked of 13 framed holes; 1 kept on the page's own picks)

Course-level reasons:

* 12 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## King tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | 2-wood -4 (tie) | tee: tee marker not on an OSM tee box (review; 21 yds from the nearest OSM tee box) |
| 2 | 4 | PASS | Driver -9 |  |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (review (kept: snap snapped 3 yds along OSM tee 674003243 would measure 180, another set's box, point 188, card 186); 3 yds from the nearest OSM tee box) |
| 4 | 5 | PASS | Driver -34 |  |
| 5 | 3 | CHECK |  | yardage: measured 174 vs card 185 (-11) |
| 6 | 4 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (review; 17 yds from the nearest OSM tee box) |
| 7 | 4 | CHECK | Driver -38 | tee: tee marker not on an OSM tee box (review (kept: snap snapped 14 yds along OSM tee 676103845 would measure 374, point 383, card 386); 14 yds from the nearest OSM tee box); wide_aim: Driver aim -46 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -8 |  |
| 10 | 4 | CHECK | Driver -28 | aim: Driver -28 lands 319 yds out in rough (8 yds from fairway) |
| 11 | 4 | CHECK | 4-wood +1 | tee: tee marker not on an OSM tee box (review; 18 yds from the nearest OSM tee box) |
| 12 | 4 | CHECK | 4-wood +6 (tie) | tee: tee marker not on an OSM tee box (review (kept: snap snapped 7 yds along OSM tee 676110861 would measure 433, point 441, card 442); 7 yds from the nearest OSM tee box) |
| 13 | 5 | PASS | Driver -6 |  |
| 14 | 4 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (review; 18 yds from the nearest OSM tee box) |
| 15 | 3 | PASS |  |  |
| 16 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (review; 16 yds from the nearest OSM tee box) |
| 17 | 5 | PASS | Driver +4 |  |
| 18 | 4 | CHECK | Driver -6 | tee: tee marker not on an OSM tee box (review (kept: snap snapped 11 yds along OSM tee 676119305 would measure 449, another set's box, point 459, card 459); 11 yds from the nearest OSM tee box) |

## Palmer tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | 4-wood -0 | tee: tee marker not on an OSM tee box (review (kept: snap snapped 7 yds along OSM tee 787286057 would measure 517, another set's box, point 523, card 527); 7 yds from the nearest OSM tee box); aim: 4-wood -0 lands 294 yds out in rough (10 yds from fairway) |
| 2 | 4 | CHECK | Driver -1 | tee: tee marker not on an OSM tee box (review (kept: snap snapped 10 yds along OSM tee 674003237 would measure 383, another set's box, point 386, card 386); 10 yds from the nearest OSM tee box) |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | Driver -40 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | 4-wood +0 |  |
| 7 | 4 | CHECK | 2-wood -54 (tie) | wide_aim: 2-wood aim -58 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -2 (tie) |  |
| 10 | 4 | CHECK | Driver -29 | aim: Driver -29 lands 317 yds out in rough (8 yds from fairway) |
| 11 | 4 | CHECK | 4-wood -0 | tee: tee marker not on an OSM tee box (review; 16 yds from the nearest OSM tee box) |
| 12 | 4 | CHECK | 4-wood +0 | tee: tee marker not on an OSM tee box (review (kept: snap snapped 4 yds along OSM tee 676110861 would measure 433, point 426, card 427); 4 yds from the nearest OSM tee box) |
| 13 | 5 | PASS | Driver -4 |  |
| 14 | 4 | CHECK | 2-wood +13 (tie) | tee: tee marker not on an OSM tee box (review; 20 yds from the nearest OSM tee box) |
| 15 | 3 | PASS |  |  |
| 16 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (review (kept: snap snapped 8 yds along OSM tee 676112669 would measure 192, another set's box, point 188, card 188); 8 yds from the nearest OSM tee box) |
| 17 | 5 | PASS | Driver -9 |  |
| 18 | 4 | PASS | 2-wood -6 (tie) |  |

