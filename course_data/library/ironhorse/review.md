# Ironhorse GC (Leawood KS): course review (rv07)

**Verdict: do not publish as-is** because of hole 18. The other 16 holes check out and are fine.

* Card: golfify, par 72, Black 6889 / Blue 6375. OSM hole ways carry the same pars, and the OSM "Tee n" boxes match the card yardages.
* Evidence: `qa_page.js` phone screenshots (0 page problems), the page pictures, the OSM tee `ref` tags in raw/summary.json, and the package geometry.

| result | holes |
|---|---|
| OK | 2-17 (the CHECKs on 7 Blue, 11 Black and 14 Blue are benign; see review.json) |
| fixed | 1 (Black tee), 18 (green and par) |
| still uncertain | none |

* **Hole 18**: built to hole 4's green, so it reads 1607 yds as a par 5 and the pick is a mid iron into OB. The real green is OSM 497967743 by the clubhouse: Black 471 (card 475), Blue 434 (card 434), par 4.
* **Hole 1 Black**: the tee sits on OSM 837929723, "Driving Range Tee Box (Turf)". It is moved to 405 yds out on the line through the back "Tee 1" box.

`osm_supplement.geojson` adds the hole 1 Black tee and a hole 18 way to the correct green. The range box is still a `golf=tee` in OSM, so apply the `tee_ll` fix in review.json if the localizer picks it again.
