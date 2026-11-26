# Brown Deer Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18

* page: `course_data/library/brown_deer/page.html` (2.6 MB); request `course_data/requests/course_page_brown_deer.json`; built 2026-11-26T17:34Z
* course: Brown Deer Golf Club (Coralville, IA), OSM way/191258543; holes: osm (tier mapped_nocard); card: None (None)
* solved tee sets: osm_back (no scorecard: the package's own tee set); page sets: osm_back
* weather: forecast for 2026-11-28, 2026-11-29; grid temperatures [35, 45, 55] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-09-01; package imagery 2025
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (osm_back tees, library check cards): none (0 asked of 13 framed holes (priors: native_auto p; automatic band off: course gate shut: 0% of sides >= 0.675 (< 25%)))

Course-level reasons:

* holes placed from aerial photos (OpenStreetMap does not map them all): 5 marked approximate (1, 7, 8, 9, 10)
* scorecard not matched (source None, flags [])
* 18 holes built vs the card's 0
* pars sum to 71, card None
* 18 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## osm_back tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | 4-wood -18 | yardage: no card yardage for osm_back; par: no card par |
| 2 | 5 | CHECK | Driver -8 | yardage: no card yardage for osm_back; par: no card par |
| 3 | 4 | CHECK | Driver -16 | yardage: no card yardage for osm_back; par: no card par; aim: Driver -16 lands 305 yds out in rough (6 yds from fairway) |
| 4 | 5 | CHECK | Driver -0 | yardage: no card yardage for osm_back; par: no card par |
| 5 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 6 | 4 | CHECK | 2-wood +12 | yardage: no card yardage for osm_back; par: no card par |
| 7 | 4 | CHECK | Long iron -40 | yardage: no card yardage for osm_back; par: no card par |
| 8 | 4 | CHECK | Driver +34 | yardage: no card yardage for osm_back; par: no card par |
| 9 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 10 | 5 | CHECK | Driver +28 | yardage: no card yardage for osm_back; par: no card par; aim: Driver +28 lands 304 yds out in rough (13 yds from fairway) |
| 11 | 4 | CHECK | Long iron -6 | yardage: no card yardage for osm_back; par: no card par |
| 12 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 13 | 4 | CHECK | 4-wood +19 | yardage: no card yardage for osm_back; par: no card par |
| 14 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 15 | 5 | CHECK | Driver -30 | yardage: no card yardage for osm_back; par: no card par; aim: Driver -30 lands 327 yds out in water (21 yds from fairway) |
| 16 | 4 | CHECK | Mid iron -4 | yardage: no card yardage for osm_back; par: no card par |
| 17 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 18 | 4 | CHECK | Driver -22 | yardage: no card yardage for osm_back; par: no card par |

