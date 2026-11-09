# Gateway National: eye check of the hazard map, holes 1-6 (reviewer A, 2026-11-09, for the Nov 14-15 event)

## Method

- Map checked: the effective lie map of `course_data/courses/gateway_national/truth/package.json`, i.e. every
  `zones_ll` entry painted in package order (later wins, unzoned = rough), which includes the hand corridor (footprint
  145-345 yds, +/-65 yds, around the Back tee -> aim line of `truth/gateway_national/render/frames.json`) and the auto
  OSM / lidar / OB layers outside it.
- Imagery: NAIP 2023 0.3 m RGB plus 0.3 m NIR as CIR (`packages/gateway_national/imagery`), NAIP 2022 0.6 m, lidar HAG
  2014 (`vision_any/gateway_national/raw/hag.tif`, 0.25 m steps). I could not fetch NAIP Plus: the proxy refused
  imagery.nationalmap.gov. The package's NAIP 2023 is already 0.3 m, so it was used instead.
- Renders (scratch, not committed): for each par 4/5, the landing area 120-350 yds from the Back tee at 3 px/yd with
  carry arcs at 210/255/275/300 in 4 panels (RGB, CIR, NAIP 2022, HAG), 4-6 px/yd zooms of each side, a whole-hole
  view, and a tee-pad zoom showing all 5 sets. For hole 4: the green surround at 5-6 px/yd. I also checked the
  lidar canopy along the line from every tee of every set (0-150 yds), the OSM tee polygons, and the live page
  (`qa_page.js ... Back`: 18 holes, 0 problems).
- Independent check: `product/native_auto.build_layer` on `packages/gateway_national/package.json`. The S2 stack is
  present and the course gate fires (share 0.92, thr 0.675). Side p for holes 1-6: 1 L .999 / R .999; 2 L .989 /
  R .978; 3 L .997 / R .922; 5 L .997 / R .998; 6 L .885 / R .997 (hole 4 is a par 3 and not scored). All of these
  agree with the hand map's native sides except 2 R, which the hand map leaves as rough (see hole 2, cosmetic edit C2).

## Summary

| hole | verdict | must fix | cosmetic |
|---|---|---|---|
| 1 | OK | none | C1 (vision "water" swale 40-80 yds in front of the tees) |
| 2 | **Back tee is wrong** | **M1: Back tee is on the wrong pad, behind 20 m trees** | C2 (native right of the path, 262-345) |
| 3 | missing OB / trees right | **M2: industrial yard OB right from +44, plus tree / shrub line +32..+44** | C3 (Forward tee not on a visible pad) |
| 4 (par 3) | OK | none | C4 (native beyond the path ~15 yds long; left lobe of the green complex) |
| 5 | OK | none | C5 (native between the two cart paths right, +44..+57) |
| 6 | OK | none | none |

---

## Hole 1 (par 4, Back 376): OK

Checked:
- Fairway (OSM) edges: they match the mowing line in RGB / CIR from 150 to 340 yds.
- The two bunkers right at 235-255: they match.
- Native left beyond the cart path (-42..-70) and native right (+28..+52) are both tufted tan in RGB, grey-speckled in
  CIR, and unmown in 2022.
- The mown rough strips between the fairway and the native bands are left as rough, which is correct.
- The road right at about +60..+70 sits beyond the native band, so it is not needed.
- No canopy in play. HAG shows only a small 0.5-2.5 m blip at 200-210 / +18, which is a bunker lip.
- Tees: Back, Middle, Champions/Tips and Forward all sit on visible pads. Card and measured yards agree.

Cosmetic:
- **C1.** Two `vision:naip_ndwi+dtm+osm_stream` water polygons (areas 396 and 464 yd2) lie 40-80 yds in front of the
  tees, across the cart path. The left part, -57..-30 at 40-50, looks like a real channel (dark in CIR). The triangle
  reaching x +12 at 60-80 is grass in both years.
  - Edit: optional. Trim or remove the triangle.
  - Reach: topped drives only. No club or aim effect. Confidence medium.

## Hole 2 (par 4, Back 422): MUST FIX the Back tee

**M1. Back tee on the wrong pad.**
- The package and `frames.json` put the Back tee at OSM tee way 720212696, [-90.1430832, 38.6630884]. That is
  hole 18's tee: 18 Back, Champions and Tips use the same way.
- From that spot the line to the hole-2 aim crosses a tree block 8-20 m tall from 5 to 40+ yds (2014 HAG). The trees
  are still there in the 2023 photo.
- The tee localizer itself was split on this choice: p_assign 0.49 for 720212696 against 0.48 for 719497753.
- The real Back pad is OSM way **719497753**: a large pad between the Tips/Champions pad (719497752) and the Middle
  pad (719497754), on the same chain. The other sets of hole 2 are on that chain, and the line from that pad is clear
  (HAG 0 m for 0-150 yds).
- Measured from 719497753 via the OSM dogleg point [-90.1455572, 38.6617296]: 417.5 yds to the green centre (card
  422). The Tips measure 465.5 against a card of 469 the same way, so the ~4-yd short read is consistent.

Edit, machine-applicable:
- `package.json` holes["2"].tees["Back"]:
  - `tee_ll` = [-90.1434917, 38.663402] (vertex-mean centroid of OSM way 719497753)
  - `bearing_deg` = 224.1 (towards the dogleg point above)
  - `tee_id` = 719497753
  - `measured_yards` ~ 418
- Also holes["2"].`tee_ll` / `bearing_deg` (top level, which mirrors the Back set).
- `render/frames.json["2"]`: `tee_ll` as above, `aim_ll` = [-90.1454657, 38.6618048] (270 yds along 224.1 deg).
  Then rebuild the hole-2 corridor and footprint (`corridor.py build`), the edge table and the page.

Notes on the rebuild:
- The hand zones are in lon/lat and stay valid geographically: pond left, native left beyond the pond from 265, and the
  OSM fairway / bunkers / canopy.
- The old footprint is rotated about 12 deg relative to the true line. It still covers the 250-310 landing area, but
  not the right side beyond about +50 at 250+ or the left beyond about -40 at 300+, where the auto layers apply.
- Seen from the true tee:
  - pond left at 150-260, 25-75 yds left of the line (farther than the current page assumes);
  - fairway -25..+20;
  - path +35..+45;
  - trees right +50..+80 at 180-260 (mapped as auto recovery);
  - maintenance yard and buildings right from +62 at 270+ (mapped as auto recovery).

Effect and confidence:
- Every Back-tee number on the page for hole 2 (aim, club, carry over the pond, "about 131 yds in", elevation) is
  computed from the wrong spot, about 54 yds left of the real tee.
- Confidence **high**: OSM tee chain, imagery and lidar all agree.

Checked and fine:
- The pond outline matches the dark CIR water at every edge.
- The fairway and the 2 bunkers right at 230-250 match.
- The trees right match the lidar.
- Native left beyond the pond (-40..-70, 265-345) is grey-speckled in CIR.

Cosmetic:
- **C2.** A strip right of the cart path, between the path and the yard, is textured and unmown in both years. This
  is likely why native_auto gives R .978.
  - Edit: add native, hand_zones form
    `{"lie": "native", "poly_ll": [[-90.1457453, 38.6621099], [-90.1463517, 38.661619], [-90.1464799, 38.6617163], [-90.1458736, 38.6622073]], "note": "unmown strip right of the cart path (true Back tee frame +45..+62, 262-345)"}`.
  - Reach: 25-35 yds right of the fairway edge, beyond the Driver 95 % half-width from any sensible aim. No club or
    aim effect. Confidence medium.

## Hole 3 (par 5, Back 630): MUST FIX the right side (OB plus tree line)

**M2. The industrial yard right of the corridor plays as rough.**
- Right of the hand fescue strip (+18..+32) there is a continuous tree and shrub line from about +32 to +44: bright
  red in CIR along the whole 145-345, and dark clumps in NAIP 2022 and 2023.
- Lidar 2014 maps it only in pieces (recovery at 150-195, 225-260 and 280-295).
- Beyond about +44 is the paved and gravelled industrial yard: trucks, pallets, buildings.
- Outside the footprint the package already carries `ob:outside` along the same boundary (from 345 on, and near the
  tee). Inside the footprint, the hand `rough` footprint erases it, so 145-345 right of +44 plays as plain rough.
  The live page mentions no OB on 3.
- Edit: append, in this order after the hand zones (LATE in trace.py) so they win:
  1. `{"lie": "recovery", "poly_ll": [[-90.14806, 38.6596038], [-90.1494178, 38.6583473], [-90.1495139, 38.6584112], [-90.1481561, 38.6596677]], "note": "tree / shrub line before the industrial yard right (CIR 2023, NAIP 2022); corridor x +32..+44, 145-345"}`
     - trace.py form: `Z("recovery", band([(145, 32), (345, 32)], [(145, 44), (345, 44)]), ...)`
  2. `{"lie": "ob", "poly_ll": [[-90.1481561, 38.6596677], [-90.1495139, 38.6584112], [-90.1496822, 38.658523], [-90.1483244, 38.6597795]], "note": "industrial yard right (off the property; OSM course boundary): corridor x +44..+65, 145-345"}`
     - trace.py form: `Z("ob", band([(145, 44), (345, 44)], [(145, 65), (345, 65)]), ...)`
  - I drew both on the 2023 photo: the OB band sits on pavement and gravel along its whole length, and the recovery
    band sits on the shrub line.
- Reach:
  - The fairway right edge is +10..+15 at 250-300, so OB is about 30 yds off it.
  - The page's Driver aim is 7.5 L with a 68-yd 95 % width (half-width 34), so +44 is about 1.5 half-widths from the
    aim: a tail event. A slice, or the 2-wood / 4-wood with the forecast right-to-left wind held off, reaches it.
- Expected effect: it should push the aim a little left and stop any "bail right" reading of the rough. I don't
  expect the club to change. It is a missing stroke-and-distance boundary that currently scores as rough.
- Confidence **high** that it is off-property. Medium on the exact edge (+/-3 yds).

Checked and fine:
- Native left beyond the cart path (-45..-70): tufted, grey in CIR.
- The mown strip between the path and the fairway.
- The fairway outline and the bunker at 275 / +20.
- The pond far left at 285-345 (-62..-80) matches the water.
- Tees Back, Middle and Champions/Tips sit on pads.
- On the Back tee shot, the OB along the trees right of the tee (x +5..+30, 20-140 yds) is only for a shank.

Cosmetic:
- **C3.** The Forward tee [-90.147694, 38.6592376] (card 475) sits on rough next to the path with no pad visible. It
  doesn't matter for Will (Back), and its landing area (about 380-420 from the Back tee) is outside the hand corridor
  anyway. Confidence low.

## Hole 4 (par 3, Back 180): OK

The map is auto only: no hand zones, because the hand corridor covers par 4/5 tee shots only. The page says
"bunker short, safe miss left".

Checked at 5-6 px/yd:
- The OSM green polygon matches the smooth light putting surface: right lobe, about -18..+17, 160-190 from the Back
  tee.
- The two bunkers short-left (-15..-8 at 150-170, -5..0 at 138-148) match.
- Surrounds:
  - left: mown rough, pink in CIR with mowing stripes;
  - right: mown rough to the path at +25..+30, then trees and OB from about +40 (mapped auto recovery and
    `ob:outside`);
  - long: rough to the path at about 195-200.
- No native within about 12 yds of the green on any side. The page's edge read ("3-9 yds off the green") is right.
- Pond short-left from 20 to 110 yds: duffed shots only.
- Tees: all 5 sets sit on pads, in order.

Cosmetic:
- **C4.** Beyond the path behind the green (about 200+ yds from the Back tee, 12-15 yds past the back edge) the grass
  is native: grey-speckled in CIR, textured.
  - Optional add: native band from 200 to 230 along the tee -> green line, -60..+20.
  - It doesn't change the box (176-182). Confidence medium.
- The fairway-tagged left lobe of the green complex (-35..-15, 168-188) is as smooth as the green. It may be part of
  the putting surface. Either way it is short-grass; no play effect. Confidence low.

## Hole 5 (par 4, Back 452): OK

Checked:
- Fairway outline from 165 to 345, including the wide part on the right to about +40 at 190-240.
- The bunker left at 235-250: it matches.
- Native left: tufted strip from -40 outwards at 250-345, from -30 at 150-200. The edge is within the noted +/-5 yds.
- Native right +32..+45 before the first cart path.
- Prairie beyond the second path +56..+70.
- No canopy. The tees sit on pads. The pond left of the tee boxes is behind the hitting line.

Cosmetic:
- **C5.** Between the two cart paths on the right (+44..+57) the ground is native in both years (textured, grey and
  red mottled CIR), but it plays as rough. The whole right side beyond +32 is native or path.
  - Edit: add native, hand_zones form
    `{"lie": "native", "poly_ll": [[-90.1499795, 38.655094], [-90.1478673, 38.6554216], [-90.1478361, 38.6552838], [-90.1499556, 38.6549887]], "note": "native between the two cart paths right (corridor +44/+40..+57, 140-345)"}`.
    trace.py form: `N([(140, 44), (345, 40)], [(140, 57), (345, 57)], ...)`.
  - Reach: 25+ yds off the fairway edge. No club or aim effect. Confidence medium-high.

## Hole 6 (par 5, Back 530): OK

Checked:
- Fairway outline from 150 to 345.
- Bunker left at 240-255.
- Trees left (lidar) at 140-200 and 250-345: the 2023 photo and CIR show the same stands. The creek water inside the
  left trees at 140-195 matches.
- Fescue left -30..-48 from 255.
- Mown rough and path on the right to +48, then prairie to +70 (grey in CIR). The native edge is within about 5 yds of
  the visible line, 20 yds off the fairway.
- native_auto L .885 / R .997 agrees.
- Tees: all on pads, in order.

## Other things the manager should know

- Hole 18's Back/Champions/Tips use the same OSM tee (720212696) that hole 2 has wrongly taken. That is probably
  correct for 18 (bearing 155), but the reviewer of 18 should confirm.
- Ask the reviewers of 7-18 to check the other `tee_centroid` picks with p_assign < 0.6 in the same way: lidar canopy
  along each set's line in the first 150 yds. That check found hole 2's tee instantly; on holes 1, 3, 4, 5 and 6
  every set is clear (hole 5 shows only isolated 2.8 m single cells at 35-95 yds, not a stand).
- `package.json` holes["3"].landing_lies reports `ob 0.101`, but the effective map has no OB in the landing corridor
  (the hand footprint rough erases it). That figure comes from the pre-hand stage and is misleading.
