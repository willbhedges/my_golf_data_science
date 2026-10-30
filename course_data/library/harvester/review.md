# The Harvester Golf Club: course review (rv02, agent)

Card of record: golfify (the same as AllSquare), Black 7340 / Blue 6810, pars correct (72). The club site returns 403.
Where golfify disagrees with the ground, opengolfapi and the OSM tee boxes settle it.

| hole | verdict | note |
|---|---|---|
| 3 | OK | the back tee is on a lidar pad exactly at the OSM hole-line start (195). OSM has no tee polygon there, so one is added in osm_supplement.geojson |
| 6 | uncertain | Black walked back 19 yds behind the back box. Both cards say 560, so the back tee may be unmapped |
| 9 | uncertain | Black is on an OSM box **88 yds right of the hole line** (458 to the green). The hole line starts at 437 (opengolfapi 437). This passed the checks because the marker is on a box |
| 12 | bad pick | Driver +17 lands in a fairway bunker 3 yds off the fairway |
| 13 | yardage | the tee is right. The ground is 409-414 yds, golfify says 390 |
| 14 | wrong tee | golfify 230/205 have no tee: the marker was walked 54 yds into rough. The OSM back box is at 176 (opengolfapi 180). **Wrong club on a par 3** |
| 16 | yardage | the tee is right. The ground is ~500 yds, golfify says 480 |
| 18 | uncertain | Black walked back 39 yds behind the line-start box. Both cards say ~560 |
| others | OK | Black is on an OSM box within 10 yds of the card. The Blue texture / lidar pads on 3, 7 and 8 match the card |

Holes: 11 OK, 4 fixable (12, 13, 14, 16; fixes in review.json), 3 uncertain (6, 9, 18).
Page render: no problems. **Publish:** not as-is. Fix hole 14 first and confirm hole 9.
