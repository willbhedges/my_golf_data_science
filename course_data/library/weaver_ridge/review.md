# WeaverRidge Golf Club: course review (rv04, 2026-10-30)

**Verdict: not safe to publish as-is.** Routing, greens and pars are right, but the tee-set labels are swapped and
the hole 5 back tee is placed in the woods.

* Card: golfify (Black 7,030 / Gold 6,543 / Green 6,011 / White 5,487 / Red 5,046, par 72). GolfLink and
  GolfScoreKeeper give the same 7,030 total. It is typed into `card_review.json`. The OpenGolfAPI lists the build
  used mix card versions, which is why the build flagged "mixed card versions".
* Labels: the page's **"Gold" is really the Black tips** (rating 73.1/136), and its **"Black" is roughly the Gold
  set**, with forward tees on 5, 11, 13, 14, 16 and 18. A golfer who picks "Black" gets Gold-ish yardages.
* Pars: 36-36 = 72 match the card. Routing and greens: all 18 match the imagery.
* Per hole: 11 OK, 6 with the wrong tee, 1 bad pick.
  * Wrong tee: 5, 11, 13, 14, 16 and 18, mostly on the Gold set; the OSM tees at the card yardage exist. 5, 13, 14
    and 16 are uncertain.
  * Bad pick: 10 (uncertain). The calm pick aims into the creek and tree band 64 ft below the tee.
  * Hole 5: the tips tee is a walk-back 67 yds into forest. OSM maps only the forward tees (230-288 yds) and the
    Black/Gold boxes (362-387) can't be seen on NAIP. It is not feasible to map them, so there is no
    osm_supplement.
  * Hole 16: golfify's Black 439 conflicts with AllSquare and OpenGolfAPI (401) and with the longest OSM tee (396).
    The tips are probably 401.

**Fix:** rebuild with
`"scorecard": "course_data/library/weaver_ridge/card_review.json", "tees": ["Black", "Gold"]`. Expect hole 5 to stay
a CHECK.
