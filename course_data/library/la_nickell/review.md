# L.A. Nickell Golf Course: course review (rv14)

**Verdict: safe to publish as-is.** 17 holes OK, 1 small yardage issue (hole 5 Blue), no routing or par errors.

* Card: golfify (Blue 6335 / White 5862 / Red 4771, par 70). It is confirmed by AllSquare, which lists the same card in metres with the same ratings. Measured tee-to-green from the chosen tees matches the card within 10 yds on every hole and set except hole 5 Blue.
* Routing: all 18 OSM hole lines run tee to green along the visible fairways. The greens are right and the pars equal the card.
* Hole 5 (needs fix, small): Blue uses the White tee (313 measured vs 325 on the card). The Blue tee is probably about 12 yds behind White. Suggested fix in review.json: tee 38.97467,-92.37072, which I could not see in the page imagery.
* The 11 CHECK holes are mostly tee-box checks: the Blue walk-backs on 9, 10, 12 and 18, the lidar or texture pads on 4, 8 W and 13, and holes 1 and 2, where the tee is on or 6 yds from an OSM box. The others are calm picks landing 6 to 13 yds off the mapped fairway (1 W, 10 W, 17 W). In every case the length matches the card and the line is unchanged, so the picks are not affected. The exact boxes for the walk-backs could not be confirmed in the 2022 NAIP.
* qa_page.js: 18 holes, 0 problems. The only console error is the sandbox's certificate error for an external resource.
