# Painted Hills Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18

* page: `course_data/library/painted_hills/page.html` (2.6 MB); request `course_data/requests/course_page_painted_hills.json`; built 2026-10-30T00:22Z
* course: Painted Hills Golf Club (Kansas City, KS), OSM relation/8086481; holes: geometry (tier unmapped_card); card: golfify (golfify)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [50, 60, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2021-06-12,2021-06-13; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* holes not all mapped in OSM (hole method: geometry)
* pars sum to 84, card 70
* 18 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +12 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 2 | 4 | CHECK | Driver -6 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 4 | 5 | CHECK | Driver -3 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 5 | 5 | CHECK | Driver -3 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 6 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 7 | 4 | CHECK | 2-wood -40 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course); yardage: measured 316 vs card 327 (-11) |
| 8 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 9 | 4 | CHECK | Driver +22 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 10 | 5 | CHECK | Driver +16 | tee: tee marker not on an OSM tee box (texture_pad; OSM maps no tee boxes on this course) |
| 11 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 12 | 5 | CHECK | Driver -28 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 13 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 14 | 4 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 15 | 4 | CHECK | Driver -6 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 16 | 4 | CHECK | 4-wood +10 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 17 | 17 | CHECK | Mid iron +8 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); OSM maps no tee boxes on this course); yardage: no card yardage for Blue; par: par 17 vs card 3; aim: Mid iron +8 lands 192 yds out in rough (40 yds from fairway) |
| 18 | 4 | CHECK | Driver -12 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +23 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 2 | 4 | CHECK | Driver -8 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 4 | 5 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 5 | 5 | CHECK | Driver +12 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 6 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 7 | 4 | CHECK | 4-wood -40 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 8 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 9 | 4 | CHECK | 2-wood +23 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 10 | 5 | CHECK | Driver +24 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 11 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 12 | 5 | CHECK | Driver -40 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 13 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 14 | 4 | CHECK | Driver +12 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 15 | 4 | CHECK | 4-wood -0 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 16 | 4 | CHECK | Driver +13 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 17 | 17 | CHECK | Mid iron +8 | tee: tee marker not on an OSM tee box (hole-line start (no golf=tee near it); OSM maps no tee boxes on this course); yardage: no card yardage for White; par: par 17 vs card 3; aim: Mid iron +8 lands 192 yds out in rough (40 yds from fairway) |
| 18 | 4 | CHECK | 2-wood -12 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |

