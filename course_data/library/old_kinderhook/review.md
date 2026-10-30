# Old Kinderhook: course review (rv14)

**Verdict: not safe to publish as-is (hole 15).** 16 holes OK and 2 need a fix (9, 15). There are no routing or par errors.

* Card: the page uses the OpenGolfAPI "Web" set (6726, par 71). It matches the club site's hole-by-hole Championship column (oldkinderhook.com/golf) on 17 holes. **Hole 15 is wrong.** The card has 273, but the club guide gives 402-365-332-293. Its other columns sum to the club's stated totals, a 273 back tee would be shorter than the 365 Club tee, and the guide says water crosses the fairway about 300 yds out. The club also states 6726, but its own Championship values add up to 6855.
* **Hole 15:** the page tee is a forward box at the pond (272 yds). The OSM hole line starts 60 yds further north and measures 332, which is the Member tee. The Championship tee is about 70 yds further back. I estimated it at 38.00318,-92.80561 (404 yds) on the line extension, but I could not see it in the page imagery. The page now plays a 273-yd hole (4-wood -40), so this hole's pick is wrong.
* **Hole 9:** the page tee is a lidar pad in the woods, about 22 yds left of the hole line (the CHECK). Moving it to the OSM hole-line start, a visible tee pad, gives 505 yds against the card's 514.
* Rebuild suggestion: request `yardages` = the Championship column (in review.json `rebuild_hint`) plus `osm_supplement` = `course_data/library/old_kinderhook/osm_supplement.geojson` (tee boxes for 9 and 15).
* qa_page.js: 18 holes, 0 problems.
