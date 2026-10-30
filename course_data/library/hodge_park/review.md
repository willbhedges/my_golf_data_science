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
