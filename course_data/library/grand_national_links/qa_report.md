# RTJ Grand National Golf: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27

* page: `course_data/library/grand_national_links/page.html` (1.3 MB); request `course_data/requests/course_page_grand_national_links.json`; built 2026-10-30T23:30Z
* course: RTJ Grand National Golf (Opelika, AL), OSM way/328838760; holes: osm (tier mapped_nocard); card: None (None)
* solved tee sets: osm_back (no scorecard: the package's own tee set); page sets: osm_back
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [60, 70, 80] F; calm-day picks with 48 prior draws
* imagery on the page: 2019-09-23; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* scorecard not matched (source None, flags [])
* 27 holes built vs the card's 0
* pars sum to 95, card None
* 27 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## osm_back tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -40 (tie) | yardage: no card yardage for osm_back; par: no card par |
| 2 | 5 | CHECK | Driver -6 | yardage: no card yardage for osm_back; par: no card par |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 757 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 4 | 4 | CHECK | Driver -33 | yardage: no card yardage for osm_back; par: no card par |
| 5 | 4 | CHECK | Driver -10 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 838 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 6 | 4 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 231 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 7 | 4 | CHECK | Driver -10 | yardage: no card yardage for osm_back; par: no card par |
| 8 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 483 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 9 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 10 | 4 | CHECK | Driver -40 | yardage: no card yardage for osm_back; par: no card par |
| 11 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 12 | 5 | CHECK | Driver +16 | yardage: no card yardage for osm_back; par: no card par |
| 13 | 4 | CHECK | Driver -37 | yardage: no card yardage for osm_back; par: no card par; aim: Driver -37 lands 300 yds out in rough (30 yds from fairway) |
| 14 | 4 | CHECK | Driver -8 | yardage: no card yardage for osm_back; par: no card par |
| 15 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee nearest the hole-line start; 261 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 16 | 4 | CHECK | Long iron +8 | tee: tee marker not on an OSM tee box (tee nearest the hole-line start; 473 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 17 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 18 | 4 | CHECK | Driver -2 | yardage: no card yardage for osm_back; par: no card par |
| 19 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 20 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 21 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 22 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 23 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 24 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 25 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 26 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 27 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |

