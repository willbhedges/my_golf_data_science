# The National Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27

* page: `course_data/library/gate/gate_national_kc/page.html` (1.8 MB); request `course_data/requests/course_page_gate_national_kc.json`; built 2026-10-29T21:06Z
* course: The National Golf Club (Parkville, MO), OSM relation/2630633; holes: structure (tier mapped_nocard); card: None (None)
* solved tee sets: osm_back (no scorecard: the package's own tee set); page sets: osm_back
* weather: climate normals for 2027-04-10, 2027-04-11; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2020-06-05; package imagery 2020
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* holes not all mapped in OSM (hole method: structure)
* OSM greens 21 of 27 holes
* scorecard not matched (source None, flags [])
* 27 holes built vs the card's 0
* pars sum to 103, card None
* 27 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## osm_back tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 2 | 5 | CHECK | Driver -8 | yardage: no card yardage for osm_back; par: no card par |
| 3 | 5 | CHECK | Driver -16 | yardage: no card yardage for osm_back; par: no card par |
| 4 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 5 | 4 | CHECK | Driver -39 (tie) | yardage: no card yardage for osm_back; par: no card par |
| 6 | 4 | CHECK | 4-wood -10 | yardage: no card yardage for osm_back; par: no card par |
| 7 | 4 | CHECK | Long iron -12 | yardage: no card yardage for osm_back; par: no card par |
| 8 | 4 | CHECK | Long iron -38 | yardage: no card yardage for osm_back; par: no card par |
| 9 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 10 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 11 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 12 | 4 | CHECK | Driver +9 | yardage: no card yardage for osm_back; par: no card par |
| 13 | 5 | CHECK | Driver -8 | yardage: no card yardage for osm_back; par: no card par |
| 14 | 4 | CHECK | Driver +15 | yardage: no card yardage for osm_back; par: no card par |
| 15 | 4 | CHECK | Driver -2 | yardage: no card yardage for osm_back; par: no card par |
| 16 | 4 | CHECK | 4-wood +18 (tie) | yardage: no card yardage for osm_back; par: no card par |
| 17 | 5 | CHECK | Driver +36 | yardage: no card yardage for osm_back; par: no card par |
| 18 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 19 | 4 | CHECK | Driver -38 | yardage: no card yardage for osm_back; par: no card par |
| 20 | 4 | CHECK | Driver +11 | yardage: no card yardage for osm_back; par: no card par |
| 21 | 4 | CHECK | 4-wood +18 (tie) | yardage: no card yardage for osm_back; par: no card par; aim: 4-wood +18 lands 266 yds out in rough (8 yds from fairway) |
| 22 | 4 | CHECK | Long iron -10 | yardage: no card yardage for osm_back; par: no card par |
| 23 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 24 | 4 | CHECK | 4-wood -40 | yardage: no card yardage for osm_back; par: no card par |
| 25 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 26 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 27 | 4 | CHECK | Long iron -18 | yardage: no card yardage for osm_back; par: no card par |

