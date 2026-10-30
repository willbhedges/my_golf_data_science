# The Falls Golf Club (O'Fallon MO): course review (rv_swope_falls, 2026-10-30)

**Verdict: not safe to publish as-is.** The card, pars and routing are right. But the page's main "Gold" set is
played from made-up tee spots on 9 holes, and several of those spots are on streets or house lots.

* Card: golfify (Gold 6,510 / Blue 6,011 / White 5,594 / Red 4,825, par 71). AllSquare gives the same card in
  meters (Gold 5,951 m = 6,508 yd), hole for hole. It is copied into `card_review.json` (scorecard/1, all 4 sets).
  The club site resolves at fallsgolf.com, not thefallsgolfclub.com. GolfLink returned 403 and BlueGolf 405.
* Pars (36-35 = 71) and routing: all 18 match the card and the imagery. The set names are right.
* Per hole: 9 OK (1, 4, 5, 6, 7, 8, 12, 14, 17) and 9 with the wrong tee (2, 3, 9, 10, 11, 13, 15, 16, 18).
* Gold tees: OSM maps no Gold box on those 9 holes. The build made up Gold tees (lidar pads or walkbacks) 19-48 yds
  behind the back OSM tee, where nobody tees off:
  * 13 is on the road.
  * 11 is on a residential street.
  * 15 and 16 are on house lots or back yards.
  * 18 is at the road edge.
  * 2, 3, 9 and 10 are in trees or beside cart paths. These four are uncertain, because a lidar pad suggests an
    unmapped box may be nearby.
  * `review.json` gives each one's fix.tee_ll: the back OSM box, 330-506 yds.
* Blue: on OSM boxes within 7 yds of the card on 17 holes. Hole 18 is a walkback 18 yds behind the back box
  (uncertain, because the card may measure the dogleg). The Blue pick on 16 (Driver -40 into greenside sand on a
  330-yd par 4) needs a look (uncertain).

**Fix:** rebuild with
`"scorecard": "course_data/library/the_falls_ofallon/card_review.json", "tees": ["Blue", "White"]`. Both sets sit on
mapped OSM boxes. Expect hole 18 Blue to stay a CHECK. Gold needs its boxes mapped. None were visible on NAIP 2022, so
I wrote no osm_supplement.
