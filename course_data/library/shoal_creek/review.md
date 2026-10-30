# Shoal Creek Golf Course (Kansas City MO): course check (rv16)

**Verdict: NOT publishable as-is.** 15 holes OK, 1 OK with an estimated Gold tee (2), 2 wrong routing (5, 6) -> fix supplied.

Evidence: `qa_page.js` phone/desktop renders of every hole, the package geometry, the OSM API ways for both ref-5 and
ref-6 holes (`course_data/research/web/rv16_osm/`), library/hodge_park's package, and the card (golfify = AllSquare on
every hole; OpenGolfAPI differs only on 16 Gold) in `course_data/research/web/rv16_rivercut_shoal/`.

* **Holes 5 and 6 are the wrong course.** OSM gained duplicate `golf=hole` ways ref 5 and 6 on 2026-10-07 (1565676851,
  1565676852) for neighbouring **Hodge Park GC**; the package took those. Their lines are identical to hodge_park holes
  5/6 and lie west of the Shoal Creek boundary, so the page pictures are black (no imagery), there is no elevation, all
  tees on 5 are walk-backs, and 6 Blue measured 278 vs the card's 333 (on a Hodge Park box). The real Shoal Creek 5
  (par 3, way 897738877, 234 yds) runs from beside the 4th green; the real 6 (par 4, way 897746434, 360 yds) ends beside
  the 7th tee.
* Fix: `osm_supplement.geojson` (all 18 Shoal Creek hole ways; 5/6 the original ones) **plus `ignore_osm_holes: true`**
  (in `review.json` `rebuild_hint`, read by `review_fixes.py`), so the Hodge Park ways are dropped. Tees and greens for
  the real 5/6 are already in OSM; `review.json` also carries card-length tee points on the real lines for snapping.
* The hand truth set `zero_tap/truth_sets/shoal_creek` took its routing from the same OSM lines and so also has the Hodge
  Park 5/6; its "6 Blue wrong box" and "no imagery over 6" findings are this same error.
* CHECK 2 (Gold walked back 32 yds behind the back OSM box): yardage correct, position estimated; left as is.
