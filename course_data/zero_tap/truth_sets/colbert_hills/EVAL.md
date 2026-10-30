# Colbert Hills (Manhattan KS): truth map and auto-package score

Truth: `holes_truth.json` (schema holes_truth/1, the format `course_data/courses/score_auto.py` reads, plus
`tee_conf`, `fairway_ll`, `water_ll`, `bunker_ll`). Scores: `eval.json`. Tee-area check sheets: `check/tees_*.jpg`
(package tees per set drawn on the page's NAIP 2023 0.3 m photos, georeferenced from the page's hole frame).
Tools: `../tools/` (extract.py decodes the page photos, overlay.py / sheets.py draw, make_truth.py builds, evalt.py scores).

## How the truth was made
* Card: OpenGolfAPI (confirmed in review.md), sets Black/Blue 7525, Silver 7049, Purple 6432, White 5883, Gold 4982
  (the "Web" set is an OpenGolfAPI artefact = Black/Blue except 12: 414 vs 434; not a real set, left out).
* Routing / hole lines / greens: OSM golf=hole lines (doglegs = their corners) and OSM green polygons, as carried by
  the library package. Routing is continuous and every set's measured length (tee -> corners -> green centre)
  matches the card within 10 yds on all 90 hole-sets except hole 1 Black/Silver (below) and hole 7 / 15 Gold (+7 / +12).
* Tees: every par 4 / 5 tee of every set drawn on the photo and checked to sit on a visible mown box (14 holes x 5 sets).
  Par 3s (5, 8, 11, 17): the page photo shows only the green, so the tees are the OSM pads (tee_conf "osm_pad");
  17 Black is a lidar pad (estimated).
* Hand fixes: **hole 1 Black** - the package's walk-back tee sat on the clubhouse drive 27 yds behind the back box;
  truth = back edge of the back box. Measured 559 vs card 590: no box exists further back, so the card is
  unreachable on the ground (estimated). **Hole 1 Silver** = centre of the back box (554 vs 578, estimated).
* Hazards: OSM fairway / water / bunker polygons per hole (presence checked on the tee-shot photos; edges are OSM,
  not re-traced). OB not included.
* 18: OSM has no green polygon; green centre = hole-line end (estimated).

## Confidence
High for routing, pars, greens (17/18; 18 medium) and the 70 par-4/5 tees seen on pads. Medium for par-3 tees
(OSM pads not seen on a photo) and hole 1 Black/Silver. Caveat: truth and auto share the same OSM source for
lines, greens and pads, so this set checks tee *assignment* and walk-back / lidar fallbacks, not OSM itself.
NAIP fetches (Planetary Computer) are blocked from the sandbox; a raw Overpass pull was requested
(webfetch_truth5_osm.json) but had not run when this was written.

## Auto package vs truth (current package.json; package_v0_no_vision.json scores identically)
| check | result |
|---|---|
| routing (auto green within 25 yds of the same-number truth green) | 18/18 |
| par | 18/18 |
| green centre error | median 1.8 yds, max 5.0 |
| tee error, 90 hole-sets | median 0.0, mean 0.5, max 31.9 yds |
| tee error > 10 yds | 1 Black/Blue 32 (walk-back onto the clubhouse drive), 1 Silver 10 |
| mean tee error by set | Black/Blue 1.8, Silver 0.6, Purple 0, White 0, Gold 0 |

Also wrong in the auto page (not geometry): the solved set is "Web", which does not exist on the card.
