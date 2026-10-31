# Bandon Dunes Golf Resort: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18

* page: `course_data/library/bandon_dunes/page.html` (1.9 MB); request `course_data/requests/course_page_bandon_dunes.json`; built 2026-10-31T03:57Z
* course: Bandon Dunes Golf Resort (Coos County, OR), OSM way/362513477; holes: osm (tier mapped_nocard); card: None (None)
* solved tee sets: osm_back (no scorecard: the package's own tee set); page sets: osm_back
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-06-23; package imagery 2022
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
| 1 | 4 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 355 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 2 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 3 | 4 | CHECK | 2-wood -40 (tie) | yardage: no card yardage for osm_back; par: no card par |
| 4 | 4 | CHECK | Driver +34 | yardage: no card yardage for osm_back; par: no card par |
| 5 | 4 | CHECK | Driver -10 | yardage: no card yardage for osm_back; par: no card par |
| 6 | 5 | CHECK | Driver +40 | yardage: no card yardage for osm_back; par: no card par |
| 7 | 4 | CHECK | Driver -6 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 154 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 8 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 210 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 9 | 4 | CHECK | Driver +5 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 106 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 10 | 4 | CHECK | Driver +16 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 182 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 11 | 4 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 129 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 12 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 144 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 13 | 4 | CHECK | Driver +23 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 192 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 14 | 4 | CHECK | Driver +16 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 140 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 15 | 5 | CHECK | Driver +39 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 195 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 16 | 4 | CHECK | Driver -38 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 211 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 17 | 5 | CHECK | Driver -8 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 354 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |
| 18 | 4 | CHECK | Driver -23 | yardage: no card yardage for osm_back; par: no card par |

