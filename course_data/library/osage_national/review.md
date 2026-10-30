# Osage National: course review (agent)

The card is from OpenGolfAPI (Palmer 7120 / Tournament 6681, par 72). No other card source was reachable. The pars sum to 72, and every hole's measured length is within 10 yds of the card.

The club has 27 holes (Mountain, River, Links). The page's 18 are Mountain + River, the original Palmer 18. The Links nine is closed until April 2027. River and Mountain were renovated in 2025-26, and the page imagery is from 2016, so bunker and tree zones may be stale.

| hole | verdict | note |
|---|---|---|
| 1 | wrong tee position | Palmer marker is on a lidar pad 19 yds behind OSM back box 793605682, at the parking-lot edge. On the yardage ladder (OSM boxes 364/340/296/273 yds to green centre vs card 377/352/306/283) that back box is the Palmer box. Move Palmer to its back edge (369 yds, within 8 of the card). Tournament is OK (box 793605683). |
| 2 | OK | Palmer is a walkback 22 yds behind the back OSM box 793640956. That box measures 423 yds to green centre and holds Tournament (card 425), so the Palmer tips (card 455) are an unmapped box behind it. The marker distance matches the card. Lateral position unverified. |
| 3 | uncertain | Palmer marker (lidar pad, 377 yds) sits in the parking lot behind the pond. No OSM box is near the card's 370: the two back boxes, 793642994 and 793642993, are both about 330 yds and fit Tournament (card 335). Either the Palmer tee is unmapped and off-line, or the card is stale after the 2025-26 River/Mountain renovation. The 4-wood pick and 105 yds in assume the 370 tee. Tournament is OK. |
| 4 | OK | Par 3. Both tees are on OSM boxes, the box is on the green and the yardage matches the card. |
| 5 | OK | Both tees are on OSM boxes and the yardage matches the card. Driver lands on fairway. |
| 6 | OK | Palmer is on a lidar pad 18 yds behind the back OSM box 793659913. That box measures 388 to green centre and holds Tournament (card 397), so Palmer (card 428) needs an unmapped box behind it, which fits. The previous green sits beside the tee. Tournament is OK. |
| 7 | OK | Palmer is on a lidar pad 27 yds from back box 793663004, which holds Tournament (card 597), and Palmer is only 15 yds longer. The pad is in the trees behind the box: plausible unmapped tips. Yardage matches the card. |
| 8 | OK | Par 3. On an OSM box, the box is on the green and the yardage matches the card. |
| 9 | OK | On OSM boxes and the yardage matches the card. |
| 10 | OK | On OSM boxes (793694354/355) and the yardage matches the card. |
| 11 | OK | On OSM boxes and the yardage matches the card. |
| 12 | OK | On OSM boxes and the yardage matches the card. Driver lands near where the fairway bends; the checks pass. |
| 13 | OK | Par 3, on OSM boxes, and the box is on the green. |
| 14 | OK | On OSM boxes and the yardage matches the card. |
| 15 | OK | On OSM boxes. Long iron to a narrowing fairway on a 314-yd par 4 is reasonable. |
| 16 | OK | Par 3, on OSM boxes, and the box is on the green. |
| 17 | OK | On OSM boxes and the yardage matches the card. |
| 18 | OK | On OSM boxes. 626-yd par 5 and the yardage matches the card. |

**Fixes:** hole 1 Palmer tee moves to OSM box 793605682 (back edge, 38.2094845, -92.6017282; 369 yds). No osm_supplement is needed: the box is already in OSM, and the tee localizer chose a lidar pad behind it. Apply the fix as a tee override from review.json.

**Publish:** OK with the hole-1 fix. Hole 3 Palmer is uncertain: the marker is in a parking lot. The Tournament set is clean on every hole.
