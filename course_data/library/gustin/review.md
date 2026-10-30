# A. L. Gustin GC: course check (agent rv11, 2026-10-30)

Card: golfify, and AllSquare shows the same card in metres (Black 6,492 / Gold 5,839, par 70). Pars match on all 18 holes.
Evidence: qa_page.js phone and desktop renders (no page problems), hole pictures from the page with the OSM hole ways, greens
and every set's tee drawn over them, and the lidar tee profiles in package.json.

| hole | verdict | note |
|---|---|---|
| 1-2, 5-6, 8-10, 12-13, 16-18 | OK | tees on OSM boxes, yardages within 5 of the card |
| 3 | OK | Black uses the shared hole-6 box (440 = card); Gold is a small forward box (351 = card) |
| 4 | OK | Black tee in a tree chute, 5 yds from the OSM box |
| 7 | OK (uncertain) | Black is a flat lidar pad under full canopy, 42 yds behind the hole way; 364 vs card 369. Probably a chute tee |
| 11 | OK (minor) | Black lidar pad about 13 yds behind the visible box; 423 vs card 424 |
| 14 | OK | OSM maps no tee boxes on 14; lidar pads at the right distances |
| **15** | **wrong tee (Black)** | walk-back in the trees on a hillside by the pond. Move it to the OSM back box at the hole-way start (38.93061, -92.34709): 399 yds along the dogleg. The card's 467 cannot be found on the ground |

Fix: `review.json` hole 15 `fix.tee_ll.Black` / `fix.yards.Black`. No osm_supplement: the right box is already in OSM. The
localizer only walked back because the card says 467. A rebuild needs the hole-15 Black yardage overridden to about 399
(or the tee pinned).

Publish: OK after the hole-15 fix. As it stands, hole 15 Black plays from a spot that is not a tee (Long iron, tie);
everything else is sound.
