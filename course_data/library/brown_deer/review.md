# Brown Deer GC (Coralville, IA): course check (rv01)

Card: golfify = OpenGolfAPI (Gold 6315 / Blue 5853, par 71). Pars and yards on the page match the card hole for hole; the course-level par mismatch (67 vs 71) is the missing hole 1.

Verdict: **not safe to publish.** 6 OK (3, 5, 6, 11, 12, 17), 7 wrong, 5 uncertain, 0 fixed.

* OSM maps 19 greens and 66 tee boxes but no `golf=hole` ways; routing v2+structure placed 17/18 holes.
* Hole 1 is missing (green way/690066085 known, no tee).
* Wrong: 7 (tee by another green, line down a cart path), 8 (walk-back 191 yds into woods), 10 (480-yd par 5 straight across the lake), 15 (tee in back yards), 16 (tee left of the hole in the trees), 18 (across the lake from the houses).
* Uncertain: 2 (plays over another green), 4 (+12 yds, lidar pad), 9, 13, 14 (tees 25-106 yds from any OSM box).
* Fix path: an `osm_supplement.geojson` with 18 `golf=hole` ways (tee -> green) drawn from the OSM tee/green polygons. An Overpass extract is requested (`course_data/requests/webfetch_rv01_amana_browndeer.json`, output `course_data/research/web/rv01_amana_browndeer/00.html`) but was still queued when this review was written.
