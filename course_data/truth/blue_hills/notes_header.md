# Blue Hills Country Club (Kansas City, MO): hand-checked truth

NCCGA event, Tue Oct 27 2026. Private parkland course at 777 W Burning Tree Dr, Kansas City MO 64145 (south KC;
1963, Bob Dunning; Korn Ferry Tour AdventHealth Championship host). OSM way/315837565. No NCCGA event at Blue Hills
was found (NCCGA site / BlueGolf / web search), so the tournament set is unknown: **Black (back) and Blue
(second-to-back) are both treated as likely and both solved as full base sets.**

Card (golfify = AllSquare Golf teebox data; GolfPass agrees except Black hole 1 = 540, its rows summing to 7364 vs its
own 7347 total): par 72 (5 4 4 4 3 5 4 3 4 / 4 4 3 5 3 4 4 4 5).

| set | yards | rating / slope |
|---|---|---|
| **Black (back)** | 7347 | 75.8 / 134 |
| **Blue (second-to-back)** | 7025 | 74.2 / 133 |
| Blue/White (combo) | 6781 | 73.2 / 131 |
| White | 6567 | 72.2 / 130 |
| White/Gold (combo) | 6275 | 71.4 / 123 |
| Gold | 6063 | 69.9 / 121 |
| Gold/Red (combo) | 5730 | 68.9 / 116 |
| Red (M) (= Red (L) tees) | 5312 | 66.8 / 112 |

Files: `holes_spec.json` (OSM hole lines, green / pad ids, pad per set) -> `holes_truth.py` -> `holes_truth.json`
(hole number, par, card per set, tee per set, green, line of play); `trace.py` -> `hand_zones_ll.json` (landing
corridors of the 14 par 4 / 5 tee shots, 145-415 yds x +/-65 from the Black tee: extended past 345 so that the Blue
tees, up to 65 yds ahead, stay on the hand map); `map/features.json` (OSM greens G / tee pads T).

## Method

* Routing: the 17 OSM golf=hole ways + the package line for the unmapped one give a continuous routing (1 N, 2 E, 3 W,
  4 SE, 5 par 3 E over the pond, 6 W over the pond, 7 E, 8 par 3 S, 9 NW to the clubhouse, 10 SE, 11 SE, 12 par 3 S,
  13 NW, 14 par 3 NE, 15 SE, 16 NW, 17 S over the creek, 18 N to the clubhouse); every Black and Blue length measured
  along the line matches the card within 5 yds: numbering correct on 18/18. Greens: OSM outlines on the visible greens
  (NAIP 2021 / 2023, CIR) on 18/18. Pars = card (sum 72).
* Tees (tee-area zooms, NAIP 2021 0.6 m + CIR + NAIP 2023, with the OSM pads): each set on a visible pad, at the
  point of the pad's centre line whose measured length equals the card. Black and Blue are on pads on all 18 holes;
  Black is 5 yds short of the card at the back edge of its pad on 2, 5 and 6 (no box visible further back: kept on the
  pad). Combination sets play from the parent box whose yardage they share. Forward boxes the OSM pads miss (Gold on
  5, 6, 12, 18; Red on 3, 5, 9, 12, 17, 18) keep the blind package's lidar / walk-back tee after a look at the zoom;
  White 10 (-10 yds) and Gold 16 (+11) sit on the nearest pad edge: estimated.
* Line of play: the OSM hole line, so doglegs bend at the fairway (1, 2, 3, 4, 6, 7, 10, 11, 13, 17, 18): the 250-yd
  aim point of the Black and Blue tees sits in the fairway on every hole (checked on whole-hole renders), well inside
  the engine's +/-40 yd aim search.
* Corridors: start layers = OSM fairway / bunker / water (mapped on the current layout), 3DEP lidar canopy > 2.5 m
  and OB beyond the OSM course outline (the property line: it follows the tree line / lot lines behind the houses; the
  footprint + 25-yd house-lot rule reaches 10-20 yds inside it on 2 and 18, so the outline is used), each reviewed on
  NAIP 2023 (1 m), NAIP 2021 (0.6 m) + CIR, NAIP 2018-2022 and the Meta / WRI canopy height map.
* **Lidar date: KS_JacksonCo_2006 (April 2006, leaf-off), 20 years old.** Recency check: every landing area zoomed
  (5-7 px / yd) on NAIP 2021 / 2023 + CIR, plus a screen of NAIP canopy (NDVI, darker than turf) not covered by the
  2006 lidar within 15 yds of a fairway. Hand corrections: trees grown since 2006 on 3 (right 240, left 223), 6 (left
  330), 9 (left 229), 11 (right 306-332, three young trees), 18 (left 352); 2006 crowns gone on 1 (right 325-360).
* Second pass: every hazard edge within ~10 yds of the fairway in each landing zone (Black 220-345, Blue to 415) was
  re-checked on the zooms above; the 17 creek was widened to its channel (15-20 yds at the line vs the 6-yd OSM strip).

## Elevation (USGS 3DEP 1 m DEM, The National Map best available)

Driver landing area vs the Black tee (ft, + = below the tee): 1 +12, 2 -3, 3 -29, 4 +30, 6 +1, 7 +3, 9 -14, 10 +46,
11 +1, 13 -12, 15 +1, 16 -10, 17 +41, 18 -23. 10 and 17 play steeply downhill (extra carry and roll: on 17 that brings
the creek into reach); 3 and 18 uphill. Par-3 greens vs tee: 5 1 ft below, 8 18 ft below (~5 yds shorter), 12 10 ft
below (~3), 14 6 ft above (~2 longer).
