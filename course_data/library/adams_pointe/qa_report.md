# Adams Pointe Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18

* page: `course_data/library/adams_pointe/page.html` (1.1 MB); request `course_data/requests/course_page_adams_pointe.json`; built 2026-10-30T00:33Z
* course: Adams Pointe Golf Course (Blue Springs, MO), OSM way/371984147; holes: osm (tier mapped_nocard); card: None (None)
* solved tee sets: osm_back (no scorecard: the package's own tee set); page sets: osm_back
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [55, 65, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2018-09-22; package imagery 2018
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* scorecard not matched (source None, flags [])
* 18 holes built vs the card's 0
* pars sum to 72, card None
* 18 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## osm_back tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -40 | yardage: no card yardage for osm_back; par: no card par |
| 2 | 5 | CHECK | Driver -6 | yardage: no card yardage for osm_back; par: no card par |
| 3 | 4 | CHECK | Driver +2 | yardage: no card yardage for osm_back; par: no card par |
| 4 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 5 | 4 | CHECK | 4-wood -6 | yardage: no card yardage for osm_back; par: no card par |
| 6 | 4 | CHECK | Driver -4 | yardage: no card yardage for osm_back; par: no card par |
| 7 | 4 | CHECK | Driver +15 | yardage: no card yardage for osm_back; par: no card par |
| 8 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 9 | 5 | CHECK | Driver -2 | yardage: no card yardage for osm_back; par: no card par |
| 10 | 5 | CHECK | Driver -2 | yardage: no card yardage for osm_back; par: no card par |
| 11 | 4 | CHECK | Driver +2 | yardage: no card yardage for osm_back; par: no card par |
| 12 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 13 | 4 | CHECK | Driver -10 | yardage: no card yardage for osm_back; par: no card par |
| 14 | 5 | CHECK | Driver -7 | yardage: no card yardage for osm_back; par: no card par |
| 15 | 4 | CHECK | Driver +18 | yardage: no card yardage for osm_back; par: no card par |
| 16 | 4 | CHECK | Driver +5 | yardage: no card yardage for osm_back; par: no card par |
| 17 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 18 | 4 | CHECK | Driver +20 | yardage: no card yardage for osm_back; par: no card par |

