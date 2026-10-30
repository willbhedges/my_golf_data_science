# Shoal Creek (Kansas City MO): truth map and auto-package score

Truth: `holes_truth.json` (holes_truth/1 + `tee_conf`, `fairway_ll`, `water_ll`, `bunker_ll`). Scores: `eval.json`.
Tee-area check sheets: `check/tees_*.jpg` (package tees drawn on the page's NAIP 2018 0.6 m photos). Tools: `../tools/`.

## How the truth was made
* Card: golfify (package source), Gold 6983, Blue 6363, White 5571, Black 4759 (Black is the forward set here).
* Routing / hole lines / greens: OSM golf=hole lines + OSM green polygons (all 18 mapped). Measured length matches
  the card within 10 yds on every hole-set except 18 Black (-11) and 18 Gold (-8).
* Tees: par 4 / 5 tees drawn on the photos and checked on visible boxes. The 2018 photo is soft and many boxes sit
  under trees, so this course is lower confidence than Colbert Hills.
* Hand fixes / estimates: **6 Blue** - the OSM-tagged box the package used measures 278 vs card 333 (wrong box);
  truth placed on the hole line at card length. **12 Black** - lidar tee measured 177 vs 166, off the line; truth on
  the hole line at card length. Estimated (no pad visible / no imagery): 2 Gold, Blue, White; 4 Gold; 5 all sets
  (par 3, no OSM pads); 6 all sets (the 2018 NAIP has no coverage over the tee half of 6); 10 Black; 18 White.
* Hazards: OSM fairway / water / bunker polygons per hole (presence checked on the photos). OB not included.

## Confidence
High: routing, pars, greens (18/18). Medium: tees (52 of 72 on visible boxes / OSM pads, 20 estimated). Same caveat as
Colbert Hills: truth and auto share OSM, so this checks tee assignment / fallbacks, not OSM.

## Auto package vs truth (current package.json; package_v0_no_vision.json scores identically)
| check | result |
|---|---|
| routing | 18/18 |
| par | 18/18 |
| green centre error | median 1.6 yds, max 3.0 |
| tee error, 72 hole-sets | median 0.0, mean 1.2, max 57.2 yds |
| tee error > 10 yds | 6 Blue 57 (wrong OSM box), 12 Black 31 (lidar pad off the line) |
| mean tee error by set | Gold 0, Blue 3.2, White 0, Black 1.7 |

Walk-back tees (2 Gold, 4 Gold, 5 all sets, 6 Gold) were kept as truth because nothing better is visible; their
error is unknown, not zero.
