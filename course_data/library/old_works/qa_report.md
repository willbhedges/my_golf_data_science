# Old Works Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18

* page: `course_data/library/old_works/page.html` (2.6 MB); request `course_data/requests/course_page_old_works.json`; built 2026-11-03T20:49Z
* course: Old Works Golf Club (Anaconda, MT), OSM way/296526499; holes: osm (tier unmapped_card); card: golfify (golfify)
* solved tee sets: Slag, Gold (the two longest sets on the card (combination sets skipped)); page sets: Slag, Gold
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [35, 50, 60] F; calm-day picks with 48 prior draws
* imagery on the page: 2021-06-28; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Slag tees, library check cards): none (0 asked of 14 framed holes)

Course-level reasons:

* OSM greens 0 of 18 holes
* 18 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Slag tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +11 | tee: tee marker not on an OSM tee box (agent; OSM maps no tee boxes on this course); yardage: measured 428 vs card 451 (-23) |
| 2 | 4 | CHECK | Driver +26 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 3 | 5 | CHECK | Driver +6 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 4 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); par3_box: no OSM green outline (the target box is drawn on an estimated green) |
| 5 | 4 | CHECK | Driver -19 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 6 | 5 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); par3_box: green outline from the imagery detector, not mapped (the target box is drawn on a detected green) |
| 8 | 4 | CHECK | Driver +18 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 9 | 4 | CHECK | Driver +33 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 10 | 4 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (agent; OSM maps no tee boxes on this course); yardage: measured 425 vs card 442 (-17) |
| 11 | 5 | CHECK | Driver -22 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 12 | 4 | CHECK | Driver -16 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 13 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); par3_box: green outline from the imagery detector, not mapped (the target box is drawn on a detected green) |
| 14 | 4 | CHECK | 4-wood +7 (tie) | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 15 | 5 | CHECK | Driver +4 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 16 | 4 | CHECK | Driver +12 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 17 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); par3_box: green outline from the imagery detector, not mapped (the target box is drawn on a detected green) |
| 18 | 4 | CHECK | Driver +11 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +10 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 2 | 4 | CHECK | Driver +22 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 3 | 5 | CHECK | Driver +6 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 4 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); par3_box: no OSM green outline (the target box is drawn on an estimated green) |
| 5 | 4 | CHECK | 2-wood -19 (tie) | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 6 | 5 | CHECK | Driver -14 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); par3_box: green outline from the imagery detector, not mapped (the target box is drawn on a detected green) |
| 8 | 4 | CHECK | 4-wood +16 (tie) | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 9 | 4 | CHECK | Driver +26 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 10 | 4 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 11 | 5 | CHECK | Driver -18 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 12 | 4 | CHECK | Driver -16 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 13 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); par3_box: green outline from the imagery detector, not mapped (the target box is drawn on a detected green) |
| 14 | 4 | CHECK | Driver +20 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 15 | 5 | CHECK | Driver +7 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 16 | 4 | CHECK | Driver +9 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 17 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); par3_box: green outline from the imagery detector, not mapped (the target box is drawn on a detected green) |
| 18 | 4 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |

