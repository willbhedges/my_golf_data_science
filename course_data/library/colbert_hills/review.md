# Colbert Hills: course check (rv05, agent)

Evidence: `qa_page.js` phone and desktop shots (18 holes, 0 page problems), the page's hole pictures, the package geometry
(tees for every set, OSM greens, hole lines), the OpenGolfAPI card and the club site (7,525 yds total).

**Verdict: not safe to publish as-is.** 15 holes OK, 1 needs a tee fix, 2 have bad calm-day picks.

| hole | verdict | what |
|---|---|---|
| 1 | wrong tee | Web/Black tee is walked back 27 yds onto the clubhouse/parking area. It should be on the back OSM box (the one Silver uses). Driver +40 then sits on the aim bound. |
| 13 | bad pick | Driver +40 (on the bound) aims into the greenside bunker cluster (30% sand). The play is a 4-wood/long iron to the left fairway. |
| 18 | bad pick | The dogleg left around the pond is out of reach of the +/-40 aim window. Driver +40 carries the pond onto the 9th green. Needs the aim line on the hole line. OSM has no green polygon for 18. |
| 17 | OK (uncertain) | Black tee is a lidar pad 19 yds behind the back OSM box. That fits card 237 (the Silver box is exactly 214). |
| 3, 4, 7, 14 | OK | QA aim CHECKs: landings 12-20 yds into rough at a fairway end or dogleg. These are judgement calls, not geometry errors. (Silver 4: Driver runs into the gap between the fairway sections.) |

Course level: the solved set "Web" (7,505) is an OpenGolfAPI artefact. It equals Black/Blue except hole 12 (414 vs 434).
On a rebuild, request tees `["Black", "Silver"]`. No osm_supplement: the hole 1 box already exists in OSM. The tee and aim
fixes are in `review.json`.
