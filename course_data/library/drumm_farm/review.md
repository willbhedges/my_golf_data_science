# Drumm Farm GC: human-style review (rv13)

Card: AllSquare (figures there are in metres; converted to yards). Its handicaps match the OSM hole tags exactly. Par 72: 4 4 3 4 4 3 5 4 5 / 4 4 4 4 3 5 4 3 5. Sets: Tour 7121, Championship 6566, Preferred 6113, Forward 5110 yds.
The page was built with no card ("osm_back", the longest OSM box on each hole). That is why all 18 holes are CHECK.
Routing, pars and greens are right on every hole. The osm_back tee is the back box and sits 4-10 yds under the Tour card on 13 holes, the usual box-centre gap.

| verdict | holes |
|---|---|
| card missing only (fix: yards/par from the card) | 1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 14, 15, 16, 17, 18 |
| uncertain | 7: Tour 598 but the tee is on the 538 (Championship) box. OSM boxes at 576/591 sit near the 5th tee complex; the suggested tee is approximate. 8, 13: Tour box not mapped (34 yds short). 8 also has a 4-wood -40 pick at the aim limit near the left-side houses. |

Fix: rebuild with a typed card (Tour + Championship from review.json). No osm_supplement was written: the boxes exist in OSM, except the Tour boxes on 8 and 13, which I could not place without imagery.
Publish as-is? Usable as a back-tee page (yardages are within about 10 of the Tour card on 15 holes), but it shows no card, and holes 7, 8 and 13 play 34-60 yds shorter than the Tour tees. Rebuild with the card first.
