# Gamble Sands Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18

* page: `course_data/library/gamble_sands/page.html` (1.1 MB); request `course_data/requests/course_page_gamble_sands.json`; built 2026-11-02T03:03Z
* course: Gamble Sands Golf Course (Okanogan County, WA), OSM way/876550790; holes: osm (tier unmapped_nocard); card: None (None)
* solved tee sets: osm_back (no scorecard: the package's own tee set); page sets: osm_back
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [35, 50, 60] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-07-16; package imagery 2023
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
| 1 | 4 | CHECK | Driver -24 | yardage: no card yardage for osm_back; par: no card par |
| 2 | 4 | CHECK | Driver -22 | yardage: no card yardage for osm_back; par: no card par |
| 3 | 5 | CHECK | Driver +10 | yardage: no card yardage for osm_back; par: no card par |
| 4 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 590 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 5 | 5 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 792 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 6 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 778 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 7 | 5 | CHECK | Driver +36 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 641 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 8 | 4 | CHECK | Driver -8 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 1052 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 9 | 4 | CHECK | Driver +9 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 1204 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 10 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 1485 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 11 | 5 | CHECK | Driver +22 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 1452 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 12 | 4 | CHECK | Driver +31 (tie) | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 1119 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 13 | 4 | CHECK | Driver -0 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 976 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 14 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 369 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 15 | 4 | CHECK | Driver +2 | yardage: no card yardage for osm_back; par: no card par |
| 16 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 471 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 17 | 4 | CHECK | Driver +21 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 613 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 18 | 5 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 200 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |

