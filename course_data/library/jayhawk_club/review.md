# The Jayhawk Club (Lawrence, KS): course review (rv10, agent)

**Not safe to publish.** The automatic page has 10 of 18 holes (pars sum to 40 vs 72), and several of those 10 are wrong.

Card: OpenGolfAPI only (Black 7,092 / Green 6,636, par 72). Not yet cross-checked with the club site, GolfPass or BlueGolf, because the web fetch had not returned by the deadline.

| hole | verdict | note |
|---|---|---|
| 1 | OK | OSM hole way and green; Black tee on an OSM box at 412 |
| 2 | wrong routing | Uses the same green as hole 9. Tee is a 76-yd walk-back. |
| 3 | wrong routing | Tee shot goes across the clubhouse parking lot. Tee is a 112-yd walk-back. |
| 4 | tee uncertain | Black tee walked back 25 yds |
| 5 | uncertain | Pick lands 90-99 yds from any fairway; measured 385 vs card 396 |
| 6 | tee uncertain | Black tee walked back 108 yds |
| 7 | tee uncertain | Lidar pad 42 yds off an OSM box |
| 8 | tee uncertain | Walked back 58 yds. Green set: the landing pattern is 42% trees / water / OB. |
| 9 | uncertain | Tee on an OSM box at 412, but the OSM way is tagged par 5 / 467, and the green is shared with hole 2 |
| 10 | tee uncertain | Lidar pad 45-59 yds off an OSM box |
| 11-18 | missing | Not built |

## The 18-hole hand trace (not done)

A hand trace needs whole-course imagery and a hole map. No imagery host can be reached from this sandbox, and tourn_truth.yml only renders courses that have `course_data/packages/<slug>/imagery`, which library courses lack. This review pushed `course_data/requests/package_jayhawk_club.json` (course_package.yml) so that a committed package with NAIP and a DEM exists. Its run had not finished by the deadline.

Next steps:
1. Once that package lands, run `course_data/truth/course_map.py --slug jayhawk_club`. It draws a whole-course NAIP map with every OSM green (10) and tee (32), numbered on a UTM grid.
2. Trace the 8 missing greens and the tees against the club's hole map.
3. Write `osm_supplement.geojson` with golf=hole LineStrings (ref, par), tee -> green; golf=green Polygons; and golf=tee Polygons.

No supplement was written. Greens invented without imagery would only add wrong holes.
