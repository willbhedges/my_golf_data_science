# Prairie Highlands: course review (2026-10-30)

**Verdict: the published page is safe, with one wrong tee (Blue 11).** Pars, routing, greens and 35 of the 36 tee
positions are right.

* Card: golfify (Black 7,066 / Blue 6,481 / White 5,770 / Red 5,122, par 72). OpenGolfAPI has the same Black, Blue
  and White yardages on all 18 holes. It differs from golfify only on Red hole 7. The card is copied into
  `card_review.json` (scorecard/1).
* Pars: 4 4 4 5 3 4 4 3 5 / 4 4 5 4 3 5 3 4 4 = 72. They match on all 18 holes.
* Routing and greens: all 18 match the 2019/2023 imagery. I drew each hole on the page photo with OSM greens, hole
  lines, all four tee sets and the calm landing spot.
* Tees: the Black and Blue tees measure within 3 yds of the card on every hole except these two:
  * **Black 11:** 388 against 400. This is the back OSM tee box, and the imagery shows no tee box behind it. It is
    acceptable, but I marked it uncertain.
  * **Blue 11 (wrong):** the page tee is a lidar pad in the trees, about 30 yds right of the tee complex. Because the
    tee line runs down the right-hand tree line, the Blue 11 calm pick (Driver +8) was solved from the wrong spot. The
    real Blue tee is the long tee strip just past the cart path, about 21 yds ahead of Black (366 against 367). It is
    in `osm_supplement.geojson`, and `review.json` has a fix point.
* Calm picks: all the tee-shot picks land in fairway or first cut except one:
  * **Black 17 (questionable):** Driver -6 on a 340-yd hole lands 308 yds out in the greenside bunker. This is an
    aggressive drive at the green, not a data error. I marked it uncertain.
  * Black 6 lands in rough just past the fairway end, at 325 on a 377-yd hole. That is fine.
* qa_page.js on Black and Blue found 0 problems.

**Rebuild:**

```
"scorecard": "course_data/library/prairie_highlands/card_review.json"
"tees": ["Black", "Blue"]
"osm_supplement": "course_data/library/prairie_highlands/osm_supplement.geojson"
```

This is low priority; it only changes Blue 11.
