# TPC Deere Run: course review (rv04, 2026-10-30)

**Verdict: not safe to publish as-is.** Routing, greens and pars are right, but the page has no card, and its
"osm_back" tee set is a mix of real tee boxes.

* Card: AllSquare (Gold 6,646 / Black 6,387 / Blue 5,875 / White 5,477 / Red 4,735, par 71). It is typed into
  `card_review.json` (scorecard/1). golfify returned 404, GolfPass 403 and BlueGolf 405.
* Pars: the page's 4 5 3 4 4 4 3 4 4 / 5 4 3 4 4 4 3 5 4 = 71 match the card on all 18 holes.
* Routing and greens: all 18 match the imagery. Hole 18 has the lake left of the green and the grandstands; the par
  3s are 3, 7, 12 and 16.
* Tees: only hole 1 (356 against the Gold 361) is right.
  * Holes 2, 4, 5 and 6 play from behind the Gold tee (+19 to +36 yds).
  * Holes 7-18 play from forward tees, short of the Gold card by 23-111 yds (9: 350 against 460; 18: 324 against
    435).
  * Calm-day picks on 8-18 are made for the wrong yardage.
* Hole counts: 1 OK, 17 with the wrong tee. The approximate Gold tee points are in `review.json`. Seven of the 17 are
  uncertain (3, 5, 7, 8, 10, 15, 17), because no OSM tee falls within 10 yds of the Gold yardage.

**Fix (no osm_supplement needed: OSM maps 65 tees):** rebuild with
`"scorecard": "course_data/library/tpc_deere_run/card_review.json", "tees": ["Gold", "Black"]`.
