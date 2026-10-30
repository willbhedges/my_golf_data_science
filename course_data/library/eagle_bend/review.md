# Eagle Bend GC (Lawrence KS): course check (rv06)

**Verdict: do not publish as-is.** 2 holes OK (1, 10), 16 wrong par or yardage. Nothing uncertain.

* The golfify card the page used is scrambled: its holes 2-9 are the real holes 11-18 and its 11-18 are the real 2-9
  (1 and 10 stay put), and it lists the 547-yd 18th as a par 4, so par 71.
* The OSM golf=hole ways (refs, pars and lengths) and OpenGolfAPI agree on the real order:
  par 4 4 5 3 4 4 5 3 4 / 4 4 3 5 4 4 4 3 5 = 72, Gold 7,052, Blue 6,542.
* The page pairs OSM hole n's geometry with golfify hole n's par and yardage. It then walks tees back, or onto lidar
  pads, to fit the wrong yardages. That puts the hole-4 tee off the course, makes holes 3 and 12 par 3s from a
  par-5 corridor, and so on. Holes 5 and 14 are right for Blue only.
* The geometry is fine (18 hole ways, 20 greens, 74 tees). **Fix:** rebuild with request
  `"scorecard": "course_data/library/eagle_bend/card_fix.json"`. That file is the golfify sets re-ordered, with Gold 13
  set to 610 (OpenGolfAPI, and the OSM way measures 611; golfify's 542 is a typo). Its Gold and Blue match
  OpenGolfAPI hole for hole. No osm_supplement is needed.

Evidence: qa_page.js screenshots (0 page problems), the page's hole pictures, a schematic of the OSM hole ways and
greens, and `raw/scorecard_web.json` (golfify vs OpenGolfAPI). Per-hole details are in `review.json`.
