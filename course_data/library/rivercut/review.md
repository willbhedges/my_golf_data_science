# Rivercut Golf Course (Springfield MO): course check (rv16)

**Verdict: publishable as-is; one small fix queued (16 Black).** 17 holes OK, 1 fixed (16), 0 uncertain apart from that fix.

Evidence: `qa_page.js` phone/desktop renders of every hole (no page problems; the only console error is a sandbox
certificate block on an external resource), the package geometry, and the card re-fetched from golfify, AllSquare
(metres) and OpenGolfAPI (`course_data/research/web/rv16_rivercut_shoal/`).

* OSM maps a box per set on almost every hole; measured length equals the card within 1 yd on every solved hole-set
  except 16 Black. Pars 72, routing and greens all correct on the pictures.
* **CHECK 4 (Blue, aim)**: Driver -7 is a tie with 4-wood on the 323-yd dogleg and finishes ~18 yds short of the
  green in the unmapped apron, not a missed fairway. Accepted.
* **CHECK 15 (Black, tee)**: Black and Blue share one long OSM box; the Black marker sits at card length ~6 yds behind
  its back edge. Yardage and target box are right. Accepted.
* **CHECK 16 (Black, tee) -> fixed**: the cards disagree (golfify 345; AllSquare 289 m = 316 and OpenGolfAPI 316), and the
  OSM hole way is 309-312 yds. The page's lidar pad at 337 is 52 yds behind the Blue box in a hollow and 33 yds from
  any OSM tee. Fix in `review.json`: Black 316, tee on the hole line ~23 yds behind the Blue box. Medium confidence.
  No `osm_supplement` is needed (tee/yardage overrides only).
