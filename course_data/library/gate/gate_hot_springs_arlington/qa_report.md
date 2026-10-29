# Hot Springs Country Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18

* page: `course_data/library/gate/gate_hot_springs_arlington/page.html` (2.6 MB); request `course_data/requests/course_page_gate_hot_springs_arlington.json`; built 2026-10-29T20:32Z
* course: Hot Springs Country Club (Hot Springs, AR), OSM way/250816543; holes: osm (tier mapped_nocard); card: None (None)
* solved tee sets: osm_back (no scorecard: the package's own tee set); page sets: osm_back
* weather: climate normals for 2027-04-24, 2027-04-25; grid temperatures [55, 65, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-03; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* scorecard not matched (source None, flags [])
* 18 holes built vs the card's 0
* pars sum to 72, card None
* qa_page.js did not run for osm_back (rc 1)
* 18 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## osm_back tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -26 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 408 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par; aim: Driver -26 lands 296 yds out in rough (107 yds from fairway) |
| 2 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 3 | 4 | CHECK | Driver -18 (tie) | yardage: no card yardage for osm_back; par: no card par; aim: Driver -18 lands 320 yds out in rough (175 yds from fairway) |
| 4 | 4 | CHECK | 4-wood +6 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 259 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par; aim: 4-wood +6 lands 264 yds out in rough (64 yds from fairway) |
| 5 | 4 | CHECK | 4-wood +12 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 71 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par; aim: 4-wood +12 lands 273 yds out in rough (216 yds from fairway) |
| 6 | 5 | CHECK | Driver +6 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 237 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par; aim: Driver +6 lands 304 yds out in rough (111 yds from fairway) |
| 7 | 4 | CHECK | 4-wood -30 | yardage: no card yardage for osm_back; par: no card par; aim: 4-wood -30 lands 277 yds out in rough (77 yds from fairway) |
| 8 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par; par3_box: no OSM green outline (the target box is drawn on an estimated green) |
| 9 | 5 | CHECK | Driver -6 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 87 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par; aim: Driver -6 lands 296 yds out in rough (112 yds from fairway) |
| 10 | 5 | CHECK | Driver +12 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 272 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par; aim: Driver +12 lands 312 yds out in rough (172 yds from fairway) |
| 11 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par; par3_box: no OSM green outline (the target box is drawn on an estimated green) |
| 12 | 4 | CHECK | Driver +6 | yardage: no card yardage for osm_back; par: no card par; aim: Driver +6 lands 308 yds out in rough (83 yds from fairway) |
| 13 | 4 | CHECK | Driver +8 | yardage: no card yardage for osm_back; par: no card par; aim: Driver +8 lands 300 yds out in rough (134 yds from fairway) |
| 14 | 4 | CHECK | Driver +0 | yardage: no card yardage for osm_back; par: no card par; aim: Driver +0 lands 312 yds out in rough (80 yds from fairway) |
| 15 | 4 | CHECK | Driver -40 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 78 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par; aim: Driver -40 lands 308 yds out in rough (12 yds from fairway) |
| 16 | 4 | CHECK | Driver -28 | yardage: no card yardage for osm_back; par: no card par; aim: Driver -28 lands 291 yds out in rough (91 yds from fairway) |
| 17 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 18 | 5 | CHECK | Driver +7 | yardage: no card yardage for osm_back; par: no card par; aim: Driver +7 lands 305 yds out in rough (113 yds from fairway) |

