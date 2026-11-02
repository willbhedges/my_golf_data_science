# Bethpage Black: automatic page QA

**Status: needs confirm** — confirm holes 4, 5, 13

* page: `course_data/library/bethpage_state_park/page.html` (0.1 MB); request `course_data/requests/course_page_bethpage_state_park.json`; built 2026-11-01T21:43Z
* course: Bethpage Black (Old Bethpage, NY), OSM node/2854158382; holes: geometry (tier unmapped_nocard); card: None (None)
* solved tee sets: osm_back (no scorecard: the package's own tee set); page sets: osm_back
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2015-05-14; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `failed: TypeError: 'float' object is not subscriptable`

Course-level reasons:

* holes not all mapped in OSM (hole method: geometry)
* OSM greens 1 of 3 holes
* scorecard not matched (source None, flags [])
* 3 holes built vs the card's 0
* pars sum to 14, card None
* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## osm_back tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 4 | 5 | CHECK | Driver -28 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 421 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par; aim: Driver -28 lands 300 yds out in rough (93 yds from fairway) |
| 5 | 4 | CHECK | Driver -16 | yardage: no card yardage for osm_back; par: no card par |
| 13 | 5 | CHECK | Driver -12 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); 461 yds from the nearest OSM tee box); yardage: no card yardage for osm_back; par: no card par |

