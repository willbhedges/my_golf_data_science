# Heritage Park GC (Olathe KS): course review (rv07)

**Verdict: do not publish as-is.** OSM has no `golf=hole` ways here and the router lost two holes and shifted three others.

* Card: golfify, par 71 (35/36), Blue 6876 / White 6327. Only one source: the second-source web fetch did not come back in time. It agrees with the OSM tee boxes hole by hole.
* Evidence: `qa_page.js` phone screenshots (0 page problems), the page's own NAIP pictures, and the package's OSM greens, tees and fairways. Holes were matched to the card using the mapper's way-id order (tees then green, hole by hole) and the length from each box to its green.

| result | holes |
|---|---|
| OK | 3, 4, 6, 8, 13, 14, 15, 16, 17 |
| fixed (review.json `fix` + osm_supplement) | 1, 2, 5, 10, 11, 12 |
| still uncertain | 7, 9, 18 (Blue back tees not in OSM; lengths only match the card on lidar pads or walkbacks) |

Routing errors:

* **Hole 1** (missing): OSM tees 930838113-115 -> green 930838116. The page shows this as "hole 10".
* **Hole 2**: the page shows hole 11. Real hole 2 is tees 930838117-120 -> green 930838121.
* **Hole 10**: real hole 10 is the page's "hole 12": north tees -> green 930838168.
* **Hole 11** (missing): tees 930838170-173 measure 224/192/158/98 against a card of 227/193/157/98 -> green 930838176.
* **Hole 12**: tees 930838177-179 measure 393/344/314 against a card of 395/346/314 -> green 930838182, which the build left unused.
* **Hole 5**: small tee fix, Blue moved onto OSM box 930838135 (623 yds; card 629).

`osm_supplement.geojson` adds 18 `golf=hole` ways (Blue tee -> green, with ref and par) and 5 hand tee boxes. Rebuild with `"osm_supplement": "course_data/library/heritage_park/osm_supplement.geojson"`.
