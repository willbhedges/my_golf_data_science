# Mozingo Lake Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18

* page: `course_data/library/gate/gate_mozingo_lake/page.html` (1.2 MB); request `course_data/requests/course_page_gate_mozingo_lake.json`; built 2026-10-29T20:54Z
* course: Mozingo Lake Golf Course (Maryville, MO), OSM way/385067034; holes: osm (tier mapped_nocard); card: None (None)
* solved tee sets: osm_back (no scorecard: the package's own tee set); page sets: osm_back
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [50, 60, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2018-08-25; package imagery 2018
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
| 1 | 4 | CHECK | Driver +2 | yardage: no card yardage for osm_back; par: no card par |
| 2 | 4 | CHECK | Driver +7 (tie) | yardage: no card yardage for osm_back; par: no card par |
| 3 | 5 | CHECK | Driver +5 | yardage: no card yardage for osm_back; par: no card par |
| 4 | 4 | CHECK | Driver -2 | yardage: no card yardage for osm_back; par: no card par |
| 5 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 6 | 5 | CHECK | Driver -6 | yardage: no card yardage for osm_back; par: no card par |
| 7 | 4 | CHECK | Driver +8 | yardage: no card yardage for osm_back; par: no card par |
| 8 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 9 | 4 | CHECK | Driver +1 | yardage: no card yardage for osm_back; par: no card par |
| 10 | 4 | CHECK | Driver +2 | yardage: no card yardage for osm_back; par: no card par |
| 11 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 12 | 5 | CHECK | Driver +33 | yardage: no card yardage for osm_back; par: no card par; aim: Driver +33 lands 304 yds out in rough (6 yds from fairway) |
| 13 | 4 | CHECK | Driver +4 | yardage: no card yardage for osm_back; par: no card par |
| 14 | 5 | CHECK | 2-wood -8 | yardage: no card yardage for osm_back; par: no card par |
| 15 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 16 | 4 | CHECK | Driver -2 | yardage: no card yardage for osm_back; par: no card par |
| 17 | 4 | CHECK | Driver +10 | yardage: no card yardage for osm_back; par: no card par |
| 18 | 4 | CHECK | Driver +4 | yardage: no card yardage for osm_back; par: no card par |

