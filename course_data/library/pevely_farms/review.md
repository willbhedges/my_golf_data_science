# Pevely Farms: course review (agent)

The card is from golfify (Black 7032 / Blue 6704, par 72), and a refetch matches the package. The pars sum to 72.

**Main problem: holes 1, 9, 10 and 18 are the wrong course.** The OSM relation borders **Crescent Farms Golf Club** (OSM way 365165194), which has its own OSM holes 1-18. The fetch got 23 hole ways (18 inside the Pevely boundary), and the router took Crescent Farms' 1, 9, 10 and 18. Those holes show black pictures, no elevation and 0% fairway, and their tees are walkbacks 379-478 yds from any Pevely tee.

| hole | verdict | note |
|---|---|---|
| 1 | wrong routing | The page plays OSM hole way 884242539 (ref 1, hcp 9). This is the neighbouring Crescent Farms Golf Club (OSM way 365165194), not Pevely Farms: its OSM handicaps (1:9, 9:1, 10:10, 18:2) do not match the Pevely card (1:16, 9:4, 10:13, 18:3). The real Pevely hole 1 is OSM way 848080943 (par 4, 445 yds; the card says 446), inside the Pevely boundary. Its green is outside the fetch bbox, so the page has no photo for most of the hole, no elevation, and no fairway (fairway 0%, aim in recovery). Re-route to 848080943. |
| 2 | OK | On OSM boxes and the yardage matches the card. Driver lands on the fairway. |
| 3 | OK | 277-yd par 4. Black is on a lidar pad 28 yds behind the OSM box, in trees by the path, at the card distance; plausible unmapped tips. A 4-wood finishing about 20 yds short is reasonable. Blue lands 8 yds into the rough (minor). |
| 4 | OK | On OSM boxes and the yardage matches the card. |
| 5 | OK | Par 3. On an OSM box and the box is on the green. |
| 6 | OK | On OSM boxes and the yardage matches the card. |
| 7 | OK | On OSM boxes and the yardage matches the card. |
| 8 | OK | Par 3. On an OSM box and the box is on the green. |
| 9 | wrong routing | The page plays OSM way 884242547 (Crescent Farms hole 9, hcp 1). This is the neighbouring Crescent Farms Golf Club (OSM way 365165194), not Pevely Farms. The tee is a walkback 379 yds from any Pevely tee and is mostly off the imagery (black picture). The real Pevely hole 9 (527/506, par 5) is the inside-boundary OSM ref-9 way. Re-route. |
| 10 | wrong routing | The page plays OSM way 884242548 (Crescent Farms hole 10). This is the neighbouring Crescent Farms Golf Club (OSM way 365165194), not Pevely Farms. The green is the hole-line end (no OSM green fetched), the picture is black, and the pick aims +40 yds at the bound with fairway 0%. The real Pevely 10 (403/384, par 4) is the inside-boundary ref-10 way. Re-route. |
| 11 | OK | Black is a walkback 24 yds behind the back OSM box (Blue is on that box), at card distance: unmapped tips. Driver on the fairway's left side, 33% fairway; acceptable. |
| 12 | OK | On OSM boxes and the yardage matches the card. |
| 13 | OK | On OSM boxes. The landing area is at the end of the fairway before the cross path; 4-wood is sensible. |
| 14 | OK | Par 3. On OSM boxes and the box is on the green. |
| 15 | OK | On OSM boxes and the yardage matches the card. |
| 16 | bad pick | The geometry looks right (OSM boxes, card yardage, dogleg right at about 260 yds). The calm pick (2-wood/4-wood tie) aims +40 yds right, at the aim bound, and lands in rough by the trees at the corner with 2% fairway. On the photo the fairway sits left of that line. Likely a zone/vision problem near the corner; treat the pick as unreliable. No geometry fix. |
| 17 | OK | On OSM boxes and the yardage matches the card. |
| 18 | wrong routing | The page plays OSM way 884242556 (Crescent Farms hole 18, hcp 2). This is the neighbouring Crescent Farms Golf Club (OSM way 365165194), not Pevely Farms. The tee is a walkback 478 yds from any Pevely tee, the picture is black and the fairway is 0%. The real Pevely 18 (468/453, par 4, hcp 3) is the inside-boundary ref-18 way. Re-route. |

**Fix:** re-route 1, 9, 10 and 18 to the Pevely hole ways inside the boundary (hole 1 = OSM way 848080943), and drop ways 884242539/547/548/556. In general, routing should prefer inside-boundary holes when refs are duplicated. The supplement is not written yet: the OSM extract request `webfetch_rv15_osmapi_pevely.json` was still queued.

**Publish:** NO, not until holes 1, 9, 10 and 18 are re-routed. The other 14 holes are OK, except that hole 16's pick is unreliable (aim at the +40 bound into rough).
