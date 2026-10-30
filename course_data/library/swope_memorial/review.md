# Swope Memorial Golf Course (Kansas City MO): course review (rv_swope_falls, 2026-10-30)

**Verdict: not safe to publish as-is.** Holes 3-9 show the wrong hole: the build put card pars and yardages on the
lines of different OSM holes.

* Card: golfify (Blue 6,274 / White 5,770 / Red 4,517, par 72). AllSquare (in meters, Blue 5,737 m) and OpenGolfAPI
  give the same card, hole for hole. It is copied into `card_review.json` (scorecard/1, all 3 sets). The club site
  has no scorecard page, GolfLink returned 403 and BlueGolf 405.
* Cause: OSM numbers the front nine in a different order from every card source.
  * OSM pars are 4 4 4 3 5 5 3 4 4; the card's are 4 4 4 4 5 3 4 3 5.
  * Card holes 3-9 are OSM ways 8, 9, 6, 7, 3, 4, 5. Both orders chain green to next tee.
  * The build matched by number, so it put the card's 368-yd par-4 4th on OSM's 169-yd par-3 line, with the tee
    walked 200 yds back into the woods. It put the par-3 6th on a 407-yd par-5 line, with the tee in the middle of
    that fairway.
  * On 3, 7 and 9 it snapped tees to other holes' boxes, so those pictures cross other holes.
* Per hole: 11 OK (1, 2, 10-18: routing, green, par, and Blue/White tees on OSM boxes within 7 yds), 7 with the
  wrong hole geometry (3-9). Uncertain:
  * 5: the OSM way is 407 yds against Blue 451, so expect a CHECK.
  * The hole 2 Blue pick, which finishes in a fairway bunker 9 yds off the fairway.
* `osm_supplement.geojson`: all 18 golf=hole ways, renumbered to the card (OSM geometry, card par). Use it with
  `"ignore_osm_holes": true`. OSM's greens and tees stay as they are.
* Renovation caveat: the course was closed from January 2025 to July 2026 for new tees, greens, bunkers and a pond
  (kcparks.org). The card and the NAIP 2020 imagery are both from before that. A 2026 club card exists
  (swopememorialgolfcourse.com/docs/Scorecard-2026.pdf), but the web fetch could not read it. Check it before
  publishing, in case the renovation changed yardages or the hole order.

**Fix:** rebuild with
`"scorecard": "course_data/library/swope_memorial/card_review.json", "osm_supplement":
"course_data/library/swope_memorial/osm_supplement.geojson", "ignore_osm_holes": true, "tees": ["Blue", "White"]`.
