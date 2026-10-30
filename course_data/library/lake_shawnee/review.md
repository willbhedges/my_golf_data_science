# Lake Shawnee Golf Course: course check (rv08, agent)

**Verdict: do not publish.** The page has 4 of 18 holes, and those 4 are numbered wrong.

* Card: golfify, the same as OpenGolfAPI (Blue 6357, White 5915, par 70). The address is 4141 SE East Edge Rd, so the clubhouse is on the east side.
* OSM maps only 4 holes (4 greens, 13 tees, 5 fairways). The routers placed those 4 and nothing else, so card holes 4-17 are missing.
* Numbering: structure inference called the chain 1-4. The evidence says it is **18, 1, 2, 3**:
  * Page 1 has OSM tee boxes at 434/406/383/366 yds. These fit hole 18 (White 429, Red 405, Gold 389), not hole 1. Its green sits next to the clubhouse and the next tee.
  * Page 2's tee is by the clubhouse and car park. Its OSM boxes at 341/308/260 fit hole 1 (348/334/300/263).
  * Page 3's OSM boxes at 366/385 fit hole 2 (369).
  * Page 4 is tagged **par 4** in OSM. Its hole line is 339 yds, with boxes at 365/338/306/277. The page made it a 148-yd par 3 by walking the tee 125 yds up the fairway. This is card hole 3 (353/320).
* Per-hole fixes (renumber, par, card yards, and tee points on the hole line) are in `review.json`.
* I wrote no `osm_supplement.geojson`. A usable page needs the 14 missing holes traced from imagery or mapped in OSM, and renumbering 4 holes would not make it publishable.
