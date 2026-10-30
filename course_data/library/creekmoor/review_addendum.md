# Creekmoor: review addendum (hole lines)

**Finding: OSM has a golf=hole way for all 18 holes. The page build did not get them.** The OSM snapshot of
2026-10-17 in `course_data/structure/data/creekmoor_mo/osm.geojson.gz` (relation 4249741, the same course) holds
ways 1553244856-64 and 1553245446-54, refs 1-18. Each way has a `dist` tag equal to the golfify Black yardage
(404, 371, 440, ..., 541), starts on a mapped OSM tee box and ends on a mapped OSM green.
`course_data/zero_tap/truth/creekmoor_mo.json` lists the tee and green way ids. The page's fetch on 2026-10-30 had
`osm_hole_ways: 0`, so the router guessed all 18 holes. That is the source of rv12's "wrong routing" holes.

I drew the ways over the page's own NAIP hole pictures, holes 3, 8, 9, 10 and 16, using the page frame. Every way
starts on a visible tee box and ends on a visible green. None of them crosses the houses that the page's lines
cross.

`osm_supplement.geojson` now holds those 18 ways, with card pars and the OSM `dist` and `handicap` tags. They
replace rv12's 11 hand lines. Five of rv12's lines had the wrong number, because rv12 "confirmed" them against the
page's own tees, which the build had already fitted to the card:

| rv12 line | really | evidence |
|---|---|---|
| "2" (tee -94.4740, 38.8272) | card 1 | OSM way ref 1 (dist 404) starts 7 yds away. Its green is the same green. |
| "11" | card 10 | It ends on OSM hole 10's green. |
| "14" | card 15 | It ends on OSM hole 15's green. |
| "15" | card 16 | It ends on OSM hole 16's green. |
| "18" | card 9's green | Its end point is OSM hole 9's green, not hole 18's (about 120 yds away). |

The page's numbering slipped against the card from hole 1 onward. The page's "hole 3" joins hole 2's tees, the N-S
row along the cart path, to hole 3's green. That is why its straight line crossed the subdivision. It is not a
dogleg from those tees.

- **Hole 3** is OSM way 1553244858. It is a bent line: tee (-94.476726, 38.833479), bend at (-94.47864, 38.832603),
  green (-94.4806694, 38.8320453), 406 yds along the line. It starts at the tee boxes north of the subdivision,
  next to hole 8's tees.
- **Holes 1, 8, 9, 10 and 16** are OSM ways ref 1, 8, 9, 10 and 16. Each one's line length is within 1-5 yds of
  card Black: 403/404, 442/441, 662/663, 478/482 and 459/455.

## Still uncertain

- **Hole 3 Black tee.** The way starts 34 yds short of card Black 440: 406 yds along the line to the green centre.
  The Black box is either unmapped or further back along the line. The rebuild's tee localizer decides between a
  walk-back and a lidar pad. Check the hole 3 Black tee on the rebuilt page.
- **Hole 18.** The line is 526 yds against card 541, with a 3-point way. The Black tee is probably about 15 yds
  behind the way's start.
- **Why the 2026-10-30 fetch had no hole ways** is not known. They may have been deleted from OSM after
  2026-10-17. Until they are restored there, the supplement carries them, so rebuild with it. `ignore_osm_holes` is
  not needed: the supplement's ways come after OSM's, so they win by ref.
- rv12's per-hole fixes in `review.json` (holes 12 and 17: tees and green) agree with OSM ways 12 and 17 (within a
  few yards), so they still apply under card numbering.
