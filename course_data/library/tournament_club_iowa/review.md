# Tournament Club of Iowa: course check (rv03)

Card: golfify (King 7041 / Palmer 6516 / Deacon 6113 / Legend 5039, par 71). AllSquare gives the same card in metres.
The club site could not be reached.

**Do not publish as-is. All 18 holes are wrong.**

* **OSM numbers the nines the wrong way round.** Card hole c is page hole c+9 (c <= 9) or c-9. The fit holds on every
  hole: King yardages land within 0-15 yds of an OSM tee box on 17 of 18 holes, and the handicaps on OSM holes 1-9 equal
  the card's back-nine stroke indexes. The clubhouse is beside OSM 8 tee / 9 green / 10 tee, which makes card hole 1 =
  OSM 10 and card hole 18 = OSM 9. The automatic build rejected the golfify card for this reason ("lengths don't fit"),
  so it fell back to "the OSM tee nearest the hole-line start".
* **Wrong tees on every hole.** The page plays mid tees: 5,923 yds in total against King 7,041. Examples: page hole 1 is
  270 against 356, and page hole 8 is 553 against 638.
* **Wrong pars.** Page hole 10 (card 1, 553 yds) is shown as a par 4 but is a par 5. Page hole 15 (card 6, 480 yds) is
  shown as a par 5 but is a par 4.
* **Picks** come from the wrong tees, so none can be trusted. Page hole 10 aims driver 40 yds left into waste ground,
  with 10% fairway.

Fix: `osm_supplement.geojson` holds the 18 hole ways renumbered to the card, with card par and handicap, each starting
at the King-yardage walk-back. It also adds one estimated King box on card hole 10, where OSM's back box is 39 yds short.
Rebuild with `ignore_osm_holes: true` and the golfify card (tees King and Palmer). `review.json` gives the per-hole
card, pars and walk-back tee estimates for both sets.

Still uncertain: the King/Palmer tee on card 10 (no OSM box), and card 13, 16 and 6, where King is 11-15 yds behind the
back mapped box.
