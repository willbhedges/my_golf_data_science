# Eagle Knoll: hole-by-hole eye check of the hazard map (2026-11-06, before the Nov 7-8 event)

Method: every hole's truth map (course_data/courses/eagle_knoll/truth/package.json zones) drawn over
NAIP 2022 and NAIP 2020 RGB, 2022 colour-infrared and lidar height above ground; landing area at ~265 yds
(par 4/5) or the green surround (par 3), plus whole-hole views. Independent algorithm check:
product/native_auto.build_layer on the course package (S2 stack present).

- Native / tall grass: mapped only on 9 R and 11 R (beside the tree stands). Detector agrees there is none
  in play anywhere: max side p 0.08 vs threshold 0.675 (course gate 0%). Lidar cannot see grass here
  (0.25 m steps, leaf-off), so the call rests on imagery + S2. No unmapped tall grass found in any landing area.
- Mown/hay fields well off line (no change): striped field right of 1 (range side, 150-280 yds), hay field
  left of 9 and right of 8 (>= ~50 yds off the line, beyond the Driver 95 % half-width of ~36 yds).
- 4 L: darker strip along the tree line at 230-300 in 2020 - longer rough next to mapped trees; left as rough.
- Water (3, 6, 14, 16, 17 creek) and OB (18 R houses) outlines match the imagery. Trees match lidar canopy.
- Par 3s 2, 6, 12, 16: green outlines and water short/left match both years.
Verdict: map OK for play; no edits.
