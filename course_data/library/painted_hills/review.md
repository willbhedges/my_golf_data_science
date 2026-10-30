# Painted Hills Golf Club: course check (rv08, agent)

**Verdict: publish after the hole-17 fix.** 17 of 18 holes are OK.

* Card: golfify (Blue 5831, White 5398, par 70), re-fetched to confirm. OpenGolfAPI has only White, and it disagrees on holes 2, 6 and 11 (380/159/159). Its own total does not add up (5352 vs the stated 5440). The measured pads match golfify.
* Routing follows the OSM hole ways. Hole 1 starts at the clubhouse, and 9 and 18 both finish there.
* All 18 tee CHECKs come from OSM mapping no tee boxes at all. The lidar and texture pads measure within 11 yds of the card on every hole. Hole 7 Blue is the largest gap: 316 vs 327, with no clearer pad behind it on 2021 NAIP.
* **Hole 17 is broken.** OSM has no golf=hole way for it, and the geometry fallback built it with par "17", hcp 3 and no card yards. The page plays it as a tee-shot hole and the course par sums to 84. The card says par 3, Blue 144, White 142. The green and the back pad (139 yds) look right.
* Fix: `osm_supplement.geojson` adds the missing hole-17 way (ref 17, par 3) and its back tee pad. The coordinator rebuilds the page.
* Picks: the least certain is hole 7. Its calm pick aims 40 yds left on a dogleg left, and the Blue pick is a tie. Nothing is clearly wrong.
