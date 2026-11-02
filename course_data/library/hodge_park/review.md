# Hodge Park GC: human-style review (rv13)

Card: golfify (AllSquare carries the same card in metres). Par 71, Blue 6181, White 5707. Pars, routing and greens all match OSM.
Evidence: qa_page.js phone/desktop screenshots (18 holes, 0 page problems), the page's hole pictures, OSM tee-box distances (`tee_options`) against the card.
The tourn_truth render failed (library courses have no 0.3 m package imagery for corridor.py), so no fresh imagery check.

| verdict | holes |
|---|---|
| OK | 2, 4, 5, 7, 9, 11, 14, 15, 16, 18 |
| wrong tee position (fix in review.json) | 1 White (373 box), 3 Blue + White (167 / 144 boxes), 17 White (489 box, not the 598 box behind Blue) |
| uncertain | 6, 8, 10, 12, 13: Blue card is 16-30 yds longer than any mapped box; the OSM colour tags look one box short (tagged Blue fits the White card). The Blue boxes are probably unmapped. 8 and 10 also have calm picks at the -40 aim limit (dogleg corners over trees). |

Many Blue holes come out 10-15 yds short of the card. That is the usual box-centre vs card gap, not an error.
No osm_supplement: the OSM boxes are colour-tagged, and a tagged OSM box beats any supplement box (`package.py`: `tagged[0]`). The tee fixes have to be applied as `fix.tee_ll` overrides, or the OSM tags corrected.

Publish as-is? Not yet. The White tee on 17 (598 vs 485) gives a wrong White-tee play on that hole. Everything else is usable with the CHECK notes.

## rv14 (2026-11-02): hole 10 routing + Red tees

**Hole 10.** The mapper's "corridor through woods, past a building, all sets 66-106 short" is a build regression, not the
course. OSM way/1565676856 (tee -> NE over the cart path -> fairway bend -> N to the green, 373 yds) is right: NAIP 2018
shows the three tee boxes at its start, the mown strip to the fairway and the green. The published page (build 12:02) used
it (Blue 400 / White 366). Later builds dropped it: the way is `inside_course: false` (its vertex mean lands in a notch of
the course polygon by the maintenance yard) and a neighbouring course's golf=hole ref 10 (way/898574075) duplicates the
ref, so `sanity.select_hole_ways` removed both and routing/2 re-routed 10 from a lidar pad beside the 1st tee straight
north through the woods and over the 18th green. Fix: `osm_supplement.geojson` carries the OSM line as a hand hole (wins
by ref, never dropped; checked it survives fetch summarise + clean_osm with `inside_course: true`).
Tees: along the line the boxes sit at blue-tag 365-380, white-tag 316-344, red-tag 230 vs card 405/371/329, so the colour
tags are one box short (as on 3, 12, 13). `fix.tee_ll`: White on the blue-tag box, Red on the white-tag box, Blue 25 yds
behind the blue box in the mown strip by the park road (no box mapped there; the 12:02 build's Blue point).

**Red tees 1, 3, 11, 12, 16** (measured 311/109/389/136/144 vs card 330/123/429/149/161). On every one the OSM red-tagged
box is a forward tee and the card Red distance falls inside the White-tagged teeing ground (1: long box 320-382; 3: 107-140;
11: 421-445; 12: 140-155; 16: 153-168). `fix.tee_ll.Red` puts a point inside that box at the card distance (kept as given).

Not verified: the exact Blue spot on 10 (no box or lidar pad confirmed there); the mapper's hole-10 zone edit (one crown at
along 338) was drawn in the wrong corridor's frame and should be re-checked after the rebuild.
