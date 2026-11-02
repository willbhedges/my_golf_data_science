# Osage National, Mountain + River (Lake Ozark, MO): truth v2 check

Card: OpenGolfAPI only (Palmer 7,120 / Tournament 6,681 / Middle 6,135 / Members 5,624 / Forward 4,783 / Green 4,049,
par 72). Corridor set **Palmer** (14 tee shots). Lidar: MO FEMA R7 North A4 2017 (3DEP EPT, LAS 2019).

**Confidence: high for routing / greens / Tournament tees / trees / fairway / water as mapped; medium for Palmer tees;
LOW for currency: River and Mountain were renovated in 2025-26 and the package photo is NAIP 2016 (lidar 2017), so
bunkers, greens and trees may have changed.**

How it was checked: routing = the OSM golf=hole ways (draft_spec), greens = OSM outlines, all 18 greens agree with the reviewed library package (within 15 yds) and the library review checked routing on the page screenshots; pars = card; whole-course routing map viewed; tee areas zoomed (3 px/yd) on every hole where the corridor-set tee is estimated by more than ~20 yds. Corridors: every par-4/5 tee shot viewed as photo + zones | photo | lidar HAG at ~1.6 px/yd; OB candidates (OSM course outline / house-lot rule) kept only where the photo shows houses, a road or a fence line, otherwise dropped (woods stay trees). "est" = tee moved along the line to the card length because no OSM box measures within 8 yds (no box visible there in NAIP at 0.6 m unless said).

## Uncertain items

| hole | item | what |
|---|---|---|
| all | renovation | 2025-26 renovation after both the imagery and the lidar: re-check against newer imagery before trusting sand / fairway edges. |
| 3 | Palmer tee | **card 370 not on the ground**: 41 yds back is the parking lot. Palmer on the back OSM box T11 (**327 vs 370**), Tournament on T10 (329, 38 yds right). |
| 1 | Palmer tee | estimated 12 yds behind OSM box 793605682 (review fix: its back edge, 369). |
| 2 6 7 9 | Palmer tee | estimated 18-27 yds behind the Tournament box (review: plausible unmapped tips in the trees). |
| 5 | OB | house lots right drawn by hand at x +22 (rooftops at +30..+60). |
| 3 10 | OB | house-lot rule (3 beyond the green; 10 a building right of the tee shot at 130-200). |
| 14 17 18 | OB (not drawn) | outline strips beyond the lake / trees: water and trees drawn instead. |
| 6 | water | OSM pond left offset ~10 yds from the lidar water edge (old mapping vs 2017 lidar). |
| all | long grass | none traced. |
