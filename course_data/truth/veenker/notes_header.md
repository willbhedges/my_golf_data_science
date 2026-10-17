# Veenker Memorial (Ames, IA): hand-checked landing corridors

Independent truth for the any-course scoreboard. 13 tee shots (every par 4 / 5) from the **Blue** tees (the back
set on the card, 6680 yds; the scoreboard's set). Corridor 150-340 yds along the package's Blue tee line, +/-60 yds
(mapped footprint 145-345 x +/-65). Files: `trace.py` (the hand trace, in each hole's corridor yards),
`hand_zones_ll.json` (WGS84, schema of `course_data/spirit_hollow/hand_zones_ll.json`), `render/` (evidence:
NAIP 2023 0.3 m photo, CIR, NAIP 2023 / 2021 / 2019 / 2017 / 2015 / 2014 at 1 m, 3DEP lidar canopy height),
`review/` (trace over photo | photo + lidar canopy edge | NAIP 2021 | lidar | CIR).

## Method

* Each hole gets one planar corridor frame (UTM, tee and aim of the Blue set from the package): x = yds right of
  the tee line, along = yds out. Every render of a hole is in that frame with a 5- or 10-yd grid; I read the edges
  off the grid by eye and wrote them as polygons (`trace.py`), converted to WGS84 by the same frame.
* Fairway = the mown, striped turf (bright pink in CIR); a separate first cut only where a collar is visible
  (holes 1, 4, 9). Rough = everything mown and unzoned.
* Trees = the crown edge (the golfer's tree line), from the bright sunlit crowns in CIR and the lidar canopy edge
  (HAG > 2.5 m; 2020 leaf-off survey). NAIP 2023 was flown 2 Sep in the morning: crowns cast long shadows toward
  the north-west; shadows are never traced as trees. Where 2020 lidar and 2023 crowns differ (open-grown
  deciduous trees: lidar crowns are smaller), the 2023 crown wins.
* Long grass = unmown: tan / tufted in NAIP across several years and pale grey (not irrigated) in CIR. Veenker is
  a parkland course: only two such areas are in the corridors (hole 15 top-left, hole 16 carry strip).
* Water = dark in CIR / no lidar returns. OB = the US-30 highway left of hole 12 (the only property line in a
  corridor). Buildings / service roads inside the property are not OB.
* Second pass: every place a hazard starts within 10 yds of the fairway edge was re-checked on 6-8 px/yd zooms
  (photo, CIR, lidar, photo + lidar canopy edge). That pass moved the right tree line of 2 (cart path side), 5, 12
  and 16 by 2-5 yds outward (lidar crown edge vs RGB shadow) and the creek on 15 by ~4 yds.
* Registration: NAIP 2023 / 2021 and the lidar agree to < 3 m (cross-correlation of tree masks: lidar -2 / -3 m
  vs NAIP), i.e. ~2-3 yds; the frame itself is exact (no screenshot registration involved).

## Ambiguities (overall)

* Tree shadows on 2, 3, 4, 18 (RGB) - resolved with CIR + lidar; residual +/-3 yds on the left edge of 2.
* Tee positions: 7, 12, 16 use the package's Blue tee on a lidar pad (no OSM box). The overviews
  (`render/hNN_overview.png`) show a tee pad there on every hole; card and measured yardage agree within 8 yds
  except 3 (card 333, measured 318) - the corridor is measured from the package tee as the product plays it.
* Weedy, mottled rough left of 12 (290-345) is mown in 2021 and 2019: rough, not long grass.
* Dead trees (1: 308; 18: 175) are kept as trees (they still block).
