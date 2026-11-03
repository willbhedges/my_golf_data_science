# Old Kinderhook Resort, Golf, Club & Spa: automatic page QA

**Status: needs confirm** — confirm holes 7

* page: `course_data/library/old_kinderhook/page.html` (1.3 MB); request `course_data/requests/course_page_old_kinderhook.json`; built 2026-11-02T23:54Z
* course: Old Kinderhook Resort, Golf, Club & Spa (Camdenton, MO), OSM way/393079215; holes: osm (tier mapped_card); card: request file yardages (request)
* solved tee sets: Championship (tee sets of interest); page sets: Championship
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2016-08-04,2016-08-21; package imagery 2016
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Championship tees, library check cards): holes 1 (1 asked of 14 framed holes; 1 kept on the page's own picks)

Course-level reasons:

* 1 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Championship tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -5 |  |
| 2 | 4 | PASS | 4-wood -8 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver -3 |  |
| 5 | 4 | PASS | 4-wood +4 |  |
| 6 | 4 | PASS | Driver -12 |  |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 8 | 4 | PASS | 4-wood -6 (tie) |  |
| 9 | 5 | PASS | Driver +6 (tie) |  |
| 10 | 4 | PASS | Driver -4 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | 4-wood +3 |  |
| 13 | 4 | PASS | Driver +2 |  |
| 14 | 5 | PASS | Driver +23 |  |
| 15 | 4 | PASS | 4-wood +2 (tie) |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver +10 |  |
| 18 | 5 | PASS | Driver +13 |  |

