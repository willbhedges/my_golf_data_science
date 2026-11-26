# Lake of the Woods Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18

* page: `course_data/library/lake_of_the_woods_como/page.html` (1.3 MB); request `course_data/requests/course_page_lake_of_the_woods_como.json`; built 2026-11-26T06:30Z
* course: Lake of the Woods Golf Course (Columbia, MO), OSM way/387184389; holes: osm (tier mapped_nocard); card: None (None)
* solved tee sets: osm_back (no scorecard: the package's own tee set); page sets: osm_back
* weather: forecast for 2026-11-28, 2026-11-29; grid temperatures [35, 45, 55] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-06-20; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (osm_back tees, library check cards): none (0 asked of 14 framed holes (priors: native_auto p; automatic band off: course gate shut: 0% of sides >= 0.675 (< 25%)))

Course-level reasons:

* holes placed from aerial photos (OpenStreetMap maps none): none marked approximate
* scorecard not matched (source None, flags [])
* 18 holes built vs the card's 0
* pars sum to 71, card None
* 18 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## osm_back tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | 4-wood +5 | yardage: no card yardage for osm_back; par: no card par |
| 2 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 3 | 4 | CHECK | Long iron +14 | yardage: no card yardage for osm_back; par: no card par |
| 4 | 4 | CHECK | Long iron +0 (tie) | yardage: no card yardage for osm_back; par: no card par |
| 5 | 4 | CHECK | Long iron -1 | yardage: no card yardage for osm_back; par: no card par |
| 6 | 4 | CHECK | 4-wood +0 | yardage: no card yardage for osm_back; par: no card par |
| 7 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 8 | 4 | CHECK | 4-wood -4 (tie) | yardage: no card yardage for osm_back; par: no card par |
| 9 | 5 | CHECK | 4-wood +22 | yardage: no card yardage for osm_back; par: no card par |
| 10 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 11 | 5 | CHECK | Driver +3 | yardage: no card yardage for osm_back; par: no card par; oval: landing pattern 45% trees / water / OB (recovery 33%, water 12%) |
| 12 | 4 | CHECK | Driver +2 | yardage: no card yardage for osm_back; par: no card par; oval: landing pattern 41% trees / water / OB (recovery 38%, water 3%) |
| 13 | 4 | CHECK | 4-wood +5 | yardage: no card yardage for osm_back; par: no card par |
| 14 | 4 | CHECK | Long iron -40 | yardage: no card yardage for osm_back; par: no card par; wide_aim: 4-wood aim -71 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 15 | 4 | CHECK | Long iron -10 | yardage: no card yardage for osm_back; par: no card par |
| 16 | 5 | CHECK | 4-wood -8 (tie) | yardage: no card yardage for osm_back; par: no card par |
| 17 | 3 | CHECK |  | yardage: no card yardage for osm_back; par: no card par |
| 18 | 4 | CHECK | Driver +6 (tie) | yardage: no card yardage for osm_back; par: no card par |

