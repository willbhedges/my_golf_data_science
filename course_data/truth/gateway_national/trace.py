"""Gateway National Golf Links (Madison, IL), Back tees: hand-checked landing corridors (course_data/truth/corridor.py).

Coordinates: (x = yds right of the tee line, along = yds from the tee) in each hole's corridor frame
(render/frames.json: the package's Back tee -> its aim point). Order = precedence (later wins); unzoned = rough.
Links-style course on reclaimed flood-plain land (Keith Foster, 1998): native prairie / fescue framing almost
every hole, ponds and wetlands, few trees (lidar 2014 leaf-off), industrial park / interstate / race track around.
Start polygons: OSM fairway / bunker / water and the 3DEP lidar canopy (assist.py), checked on NAIP 2023 0.6 m + CIR,
NAIP 2012-2022 and the lidar render; long grass traced by hand (tan / textured, unmown in every NAIP year).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from corridor import Z, band, ell, poly, rect  # noqa: E402,F401
import assist as A  # noqa: E402

S = "gateway_national"
H = {}


def auto(ref, trees=True, fairway=True, sand=True, water=True):
    """The checked start layers for a hole: trees (lidar), fairway, water, bunkers (OSM)."""
    z = []
    if trees:
        z += A.canopy(S, ref)
    if fairway:
        z += A.osm(S, ref, "fairway")
    if water:
        z += A.osm(S, ref, "water")
    if sand:
        z += A.osm(S, ref, "sand")
    return z



def N(left, right, note):
    """native (prairie / fescue) band between a left and right edge [(along, x)]."""
    return Z("native", band(left, right), note)


EXTRA = {
    "1": [N([(140, -70), (345, -70)], [(140, -42), (200, -56), (270, -50), (345, -40)], "prairie left of the cart path"),
          N([(140, 28), (200, 28), (260, 32), (345, 35)], [(140, 52), (345, 52)], "fescue right (tufted, tan / grey CIR)")],
    "2": [N([(265, -70), (345, -70)], [(265, -40), (300, -36), (345, -34)], "prairie left beyond the pond")],
    "3": [N([(140, -70), (345, -70)], [(140, -45), (345, -43)], "prairie left of the cart path"),
          # 2026-11-13 (F1): the "fescue strip before the tree line right" (x +18..+32) is a bare track / thin rough
          # (no lidar height, no dormant-grass signal): removed. Trees (LATE) and the yard beyond are unchanged.
          ],
    "5": [N([(140, -70), (345, -70)], [(140, -30), (200, -30), (250, -38), (300, -40), (345, -40)], "prairie left"),
          N([(140, 32), (345, 34)], [(140, 45), (345, 46)], "fescue between the rough and the cart path right"),
          N([(140, 56), (345, 58)], [(140, 70), (345, 70)], "prairie beyond the cart path right")],
    "6": [N([(255, -48), (345, -48)], [(255, -30), (345, -30)], "fescue between rough and trees left"),
          N([(140, 48), (345, 48)], [(140, 70), (345, 70)], "prairie beyond the cart path right")],
    # 2026-11-13 second pass: a mown collar ~10-12 yds wide runs round the outside of the fairway (tan, smooth on NAIP
    # 2023, like the ring round the square inside the bend; green in the Sentinel-2 NDVI of Nov 2026); the unmown
    # ground starts beyond it. "beyond the end" moved from 300 to 312, "inside the dogleg" from the fairway edge to
    # 12 yds off it.
    "8": [N([(312, -35), (345, -35)], [(312, 25), (345, 25)], "prairie beyond the end of the fairway (past the mown collar)"),
          # 2026-11-13 (F1, second_pass/FEATURES_1_9.md): "fescue before the trees right" (x +25..+45 at 220-345)
          # removed: mown rough to the brush line (Dec 2020 lidar: no standing grass; NDVI Nov 2024-26 0.76-0.84).
          # The summer photos show it tan because it is unirrigated, not because it is long.
          # 2026-11-09 eye check B (must fix): the fairway's right edge bends left round the 270 bunker; the ground
          # from it to the trees is the same fescue (NIR/red 1.03-1.13 vs turf 1.3; native_auto 8 R p 0.89)
          # inner edge = F1's lidar line (first standing grass): 47 at 220, 45 at 250, 34 / 28 / 21 / 9 / -7 at 260 /
          # 270 / 280 / 290 / 300 (Sentinel-2 Nov 2026 within 0-6 yds of it); my own collar line was 10-25 yds too close
          N([(220, 47), (250, 45), (260, 34), (270, 28), (280, 21), (290, 9), (300, -7), (312, -25)], [(220, 65), (312, 65)],
            "unmown ground inside the dogleg: from the lidar brush line to the trees"),
          # 2026-11-13 second pass: the unmown square inside the bend, ringed by a mown bank (NAIP 2023 RGB + CIR:
          # dark, tufted; outside the +/-65 corridor, so it was priced as "unverified"). Driver territory (300-337).
          Z("native", poly((-67, 299), (-53, 309), (-48, 316), (-72, 336), (-83, 330), (-88, 318), (-82, 306)),
            "unmown square inside the dogleg, left of the line (302-337)")],
    # 2026-11-09 audit item 3 (checked on NAIP 2023 RGB + CIR): the tufted strip left runs in to 5-8 yds off the
    # fairway at 250-340 (CIR grey / dark red, textured), not only x -48..-33
    "9": [N([(140, -48), (300, -48)], [(140, -33), (300, -33)], "fescue strip left"),
          # 2026-11-13 second pass: (a) the Nov 9 inner edge overshot at 290-340 (drawn to x -14..-22): on NAIP 2023 the
          # tufted grass stops at a worn line x -18 (265-280) -> -22 (300) -> -27 (320) -> -28 (340), and the Sentinel-2
          # NDVI of Nov 8 / 10 2026 puts the dormant-grass edge in the same place; (b) the "fescue before the tree line
          # right" (x +30..+45) is mown turf: mowing stripes on NAIP 2023, NDVI 0.87 in Nov 2026 (= the fairway's):
          # removed
          N([(250, -50), (340, -50)], [(250, -34), (260, -33), (265, -29), (270, -20), (280, -19), (300, -22), (320, -27), (340, -28)],
            "unmown strip left, in to the worn line 6-15 yds off the fairway (250-340)")],
    "10": [N([(140, -70), (345, -70)], [(140, -45), (345, -45)], "prairie left"),
           N([(140, 52), (300, 30), (345, 30)], [(140, 70), (345, 70)], "prairie beyond the cart path right")],
    # 2026-11-09 eye check B: left inner edge 5-9 yds off the fairway at 160-280 (was on it); right fescue starts
    # beyond the cart path (was 15-20 yds too close: mown rough + path mapped as native)
    "11": [N([(160, -68), (200, -62), (230, -50), (260, -42), (345, -27)], [(160, -48), (180, -48), (220, -35), (250, -23), (280, -17), (300, -10), (345, -6)], "prairie strip between 11 and the parallel fairway"),
           N([(150, 32), (170, 33), (210, 39), (250, 47), (280, 57), (300, 64)], [(150, 70), (300, 70)], "fescue beyond the cart path right")],
    # 2026-11-09 eye check C: right fescue inner edge 20 -> 50 up the hole (was a flat 32: 8-15 yds too close at
    # 250-345); the left "fescue strip" is mown rough (removed); native / wetland between the left path and the ditch
    "13": [N([(140, 20), (170, 28), (200, 36), (250, 44), (300, 48), (345, 50)], [(140, 56), (200, 61), (250, 69), (300, 70), (345, 70)], "fescue right: unmown blocks inside the cart path"),
           N([(140, -54), (160, -59), (180, -64), (200, -72), (225, -80)], [(140, -44), (180, -44), (225, -46)], "native / wetland between the left cart path and the ditch")],
    # 2026-11-09 eye check C: left inner edge 5-10 yds too close before the bunkers; the mapped "prairie right" was
    # mown rough (removed); the real fescue is beyond the cart path as it crosses in, 230-345
    "15": [N([(140, -70), (345, -70)], [(140, -15), (170, -20), (200, -20), (230, -28), (260, -33), (300, -38), (345, -40)], "prairie left"),
           N([(230, 73), (260, 63), (290, 53), (320, 43), (345, 41)], [(230, 103), (260, 90), (290, 80), (320, 70), (345, 66)], "fescue right beyond the cart path")],
    # 2026-11-09 eye check C: the inner right band (x 25-38) was mown rough; the fescue runs from the cart path out
    # 2026-11-09 audit item 2 (NAIP 2023 RGB + CIR): the tufted mound with a stone edge in the fairway's right notch,
    # 264-298 yds, x +6..+43 (it was rough after the Nov 9 right-band edit)
    "16": [Z("native", poly((8, 297), (25, 298), (38, 292), (43, 282), (40, 270), (30, 264), (18, 266), (10, 272), (6, 285)),
             "fescue mound right of the fairway, inside the cart path"),
           # 2026-11-13 second pass: inner edge at 240-300 is x -27 -> -22 (NAIP 2023 at 7 px / yd: the tan tufted
           # patch starts 6-8 yds off the fairway edge at -16), was -30..-34
           N([(140, -70), (300, -70)], [(140, -32), (220, -33), (240, -27), (260, -24), (280, -22), (295, -23), (300, -28)], "prairie left"),
           N([(140, 33), (170, 38), (180, 45), (200, 51), (220, 57), (260, 55), (280, 52), (300, 49)], [(140, 70), (300, 70)], "fescue right from the cart path out")],
    # 2026-11-09 eye check C: the fescue swings out with the cart path from 260 (was a straight strip 15-30 yds too close)
    "18": [N([(140, -46), (170, -46), (200, -48), (230, -48), (260, -52), (290, -75), (320, -90), (345, -90)], [(140, -18), (200, -22), (245, -30), (275, -36), (290, -42), (305, -48), (320, -58), (345, -64)], "fescue left between the cart path and the rough")],
}
NOTE = {
    "1": ("Wide fairway (OSM) with fescue / prairie both sides: left beyond the cart path, right from x +28.", "medium-high"),
    "2": ("Pond left (OSM) 140-260; prairie beyond it; trees and the maintenance yard right.", "high"),
    "3": ("Prairie left of the cart path; a fescue strip then the tree line along the industrial park right.", "high"),
    "5": ("Fescue both sides beyond ~10 yds of mown rough; bunker left 245.", "medium (fescue edges +/-5)"),
    "6": ("Trees left (lidar), fescue between them and the rough at 255+; prairie right beyond the path.", "high"),
    "8": ("Dogleg left: fairway ends ~300, prairie beyond it; trees right; fescue before them.", "medium"),
    "9": ("Fescue strip left between the fairways; trees right at +45.", "medium"),
    "10": ("Short par 4: pond / ditch left (OSM water), prairie left and right beyond the path.", "medium"),
    "11": ("Prairie strip between 11 and the parallel fairway left; fescue right.", "medium"),
    "13": ("Water / ditch left (OSM), prairie right.", "medium-high"),
    "15": ("Prairie left (the fairway angles right), prairie right beyond the path.", "medium"),
    "16": ("Fescue both sides; pond beyond 300 left (OSM).", "medium"),
    "18": ("Fescue strip left between the path and the fairway; trees right (lidar).", "high"),
}
# 2026-11-09 eye check A (must fix): the tree / shrub line right of the fescue strip, then the industrial yard (off the
# property, OSM course boundary; the package's ob:outside along the same line was erased by the hand footprint)
LATE = {"3": [Z("recovery", band([(145, 32), (345, 32)], [(145, 44), (345, 44)]), "tree / shrub line before the industrial yard right (CIR 2023, NAIP 2022)"),
              Z("ob", band([(145, 44), (345, 44)], [(145, 65), (345, 65)]), "industrial yard right (off the property)")]}
# 2026-11-13 (golfer's question on 10, second_pass/HOLE10.md): the ditch from the pond's outlet to the cart-path culvert,
# hard against the green's right edge (236-308 yds). Dec 2020 lidar ground: a trench 4.0-4.8 ft below the green, a
# vertical wall on the green side, wall to the top of the steep right bank 3-5 yds (median 3.8), no lidar returns on
# its floor (standing water). The OSM "water" way is a 2.3-2.8-yd strip along its right half. This polygon = lidar
# wall (moved 1 yd left: the wall's shadow line on NAIP 2023 is 0-2 yds left of the lidar wall, clipped at the mapped
# green's edge) to the lidar bank top: 3.5-5.5 yds wide. The OSM strip stays (union).
LATE["10"] = [Z("water", poly((-16.6, 236), (-14.1, 240), (-12.4, 244), (-10.4, 248), (-9.9, 252), (-9.6, 256), (-9.9, 260),
                              (-9.9, 264), (-8.6, 268), (-8.4, 272), (-8.4, 276), (-8.9, 280), (-8.6, 284), (-8.9, 288),
                              (-9.6, 292), (-9.6, 296), (-9.9, 300), (-9.1, 304), (-8.1, 308), (-4.6, 308), (-3.4, 304),
                              (-3.9, 300), (-4.1, 296), (-4.4, 292), (-4.6, 288), (-4.6, 284), (-4.9, 280), (-4.6, 276),
                              (-4.9, 272), (-4.6, 268), (-4.6, 264), (-5.1, 260), (-5.4, 256), (-5.9, 252), (-6.4, 248),
                              (-7.6, 244), (-8.4, 240), (-10.4, 236)),
                "ditch beside the green, wall to bank top (lidar ground Dec 2020 + NAIP 2023), 236-308")]

# 2026-11-13 second pass (specialist F2, second_pass/FEATURES_10_18.md): long grass re-traced from the USGS 3DEP lidar
# point clouds of Dec 2020 / Dec 2023 (vegetation height on a 0.5 m grid: mown 0.02-0.04 m, standing fescue / prairie
# 0.10-0.35 m). Applied ONLY where it moves a Back or Middle aim by >= 3 yds or changes a club, and only after the
# integrator checked the hole on a lidar-height + NAIP render: holes 10 and 16. There the hand native bands above are
# replaced by the frozen copy of the proposals in features_applied.json (action add, kind native / rough, confidence
# >= 0.7). Every other hole keeps its hand bands. Any other action in that file is an error.
import json as _json  # noqa: E402
_FA = _json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "features_applied.json")))["holes"]
for _r, _eds in _FA.items():
    _z = []
    for _k in ("native", "rough"):
        for e in _eds:
            if e["action"] != "add" or e["kind"] not in ("native", "rough"):
                raise ValueError("features_applied.json: hole %s: unhandled edit %s %s" % (_r, e["action"], e["kind"]))
            if e["kind"] == _k:
                if e.get("polygon_ll"):                 # WGS84 ring -> this hole's corridor frame (x, along)
                    import numpy as _np
                    import corridor as _CO
                    _yd = _CO.frame_of(_CO.frames(S)[_r], 1.0).ll_to_yds(_np.asarray(e["polygon_ll"], float)[:, :2])
                    _pts = [(float(x), float(-y)) for x, y in _yd]
                else:
                    _pts = [(x, a) for x, a in e["polygon_frame_x_along"]]
                _z.append(Z(_k, poly(*_pts), "second pass (lidar height): " + e["target"][:70]))
    EXTRA[_r] = _z
# 16, the mound right of the fairway at 264-298 (x +6..+43, white stones on its left edge): tufted on NAIP Aug 2023, but
# the Dec 2023 lidar has its grass at 0.036 m (the fescue block across the fairway reads 0.22 m in the same flight) and
# the Nov 2026 NDVI is 0.78. Decision (recorded in OPTIMIZE.md): not a lost-ball lie, but not plain rough either (a
# hummocky mound, an awkward stance). The engine has no heavy-rough lie; it is priced as "sand" (ball found, stops
# where it lands, about 0.3-0.4 strokes over fairway at 90 yds), between rough and native.
EXTRA["16"].append(Z("sand", poly((8, 297), (25, 298), (38, 292), (43, 282), (40, 270), (30, 264), (18, 266), (10, 272), (6, 285)),
                     "mound right of the fairway, inside the cart path: short tufted grass (priced as a penal lie, not lost-ball)"))

for _r, (_n, _c) in NOTE.items():
    H[_r] = dict(zones=EXTRA.get(_r, []) + auto(_r) + LATE.get(_r, []), note=_n, confidence=_c)

TRACE = dict(holes=H, missing=[])
