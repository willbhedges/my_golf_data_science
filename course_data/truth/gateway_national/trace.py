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
# 2026-11-13, the golfer's first drawing on the page picture of 10 (red outline: "this is all penalty area in that
# native as well"): the band of rougher grass between the ditch and the right-hand fairway, from the footbridge /
# pond corner (226) to the cart path past the green (303), capped at x +13 past the fairway's end as he drew it.
# Fitted to NAIP 2023 (left = the ditch, right = the mown fairway's edge, 0.5 yd off the mapped fairway).
# EVIDENCE AGAINST: Dec 2020 lidar grass height in the band 0.01 m (0 % over 0.10 m; the tall grass left of the green
# reads 0.11-0.14 m, 50 % over 0.10) and Sentinel-2 NDVI Nov 2026 0.86-0.88 (= fairway; standing native 0.55-0.60):
# it reads as mown rough. He later said he "could be wrong" on the right side. Kept as penalty area because it is
# the low-regret map: its 2-wood / 4-wood aim (26 L) costs 0.025 strokes if the band is in fact mown, while the
# ditch-only map's aim (19.5 L) costs 0.05 if he is right; the club and "go at the green" are the same either way
# (second_pass/HOLE10.md section 7). His second drawing took the right side on to the cart path (276-305, x up to
# +41): same lidar / NDVI reading, changes no aim or club, not mapped.
LATE["10"].append(Z("water", poly((11.1, 272.2), (6.7, 266.2), (4.1, 260.5), (-2.9, 239.9), (-8.4, 226.2), (-12.7, 226), (-6.4, 248), (-5.4, 256), (-4.6, 264), (-4.6, 284.2), (-3.4, 303), (13, 302.8), (13, 283), (14.8, 275)),
                    "band between the ditch and the right fairway (golfer's first drawing; lidar / NDVI read it as mown: low-regret choice), 226-303"))

# 2026-11-13 strategy pass (reviewer B, second_pass/REVIEW_B.md P1): 11's left long grass from 300 on is 6-19 yds
# closer to the fairway than the Nov 9 band and goes on to 385 (photo / CIR 2023 and F1's lidar edge agree within
# 1-5 yds). Matters now that native is penalty area (golfer's rule).
EXTRA["11"].append(Z("native", poly((-10, 300), (-3, 300), (-2, 310), (2, 320), (8, 330), (13, 340), (21, 350), (24, 360), (28, 372),
                                    (28, 385), (8, 385), (4, 370), (-2, 350), (-8, 335), (-10, 320)),
                     "long grass left of the fairway 300-385, inner edge from the lidar (310-360) and the photo (370-385)"))
# reviewer C (REVIEW_C.md v2, 18-A): the left fescue's fairway-side edge is 10-12 yds closer at 300-340 than the Nov 9
# band (which followed the cart path) and goes on to 395 (lidar + NAIP 2023)
EXTRA["18"].append(Z("native", poly((-30, 260), (-34, 280), (-38, 300), (-45, 320), (-52, 340), (-53, 360), (-55, 380), (-52, 395),
                                    (-100, 395), (-100, 380), (-98, 360), (-92, 340), (-85, 320), (-75, 300), (-62, 280), (-52, 262)),
                     "left fescue, fairway-side edge 260-395 (lidar + NAIP 2023)"))
# reviewer A (REVIEW_A.md v2, 1a): 1's right fescue starts at x +28.5..+30.5 from 268 to 345 (mapped +32..+35), and
# runs to the road (x +58; the Nov 9 band stopped at +52)
EXTRA["1"].append(Z("native", poly((30, 268), (29, 290), (28.5, 300), (29.5, 312), (30.5, 345), (58, 345), (58, 268)),
                    "right fescue, fairway-side edge 268-345 to the road (NAIP 2023; F1 lidar)"))
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

# 2026-11-13 strategy pass, after the lidar replacement above:
# the golfer's second drawing of 10 (every dead area round the green in red on the page picture, Nov 13; here the
# Dec 2020 lidar agrees: grass 0.11 m median, 51 % over 0.10 m, NDVI Nov 2026 0.56-0.64;
# /root/.claude/uploads/.../01e42326-image.jpg, described in second_pass/HOLE10.md): the tall grass starts right
# behind the left greenside bunkers and wraps round the back-left to the cart path; the lidar polygons left 6-8 yds
# of "rough" between the bunkers and the tall grass at 255-296. Painted before the bunkers / surround (EXTRA).
EXTRA["10"].append(Z("native", poly((-66, 252), (-60, 255), (-56, 259), (-55.5, 266), (-55, 275), (-54, 283), (-53, 290), (-50, 297),
                                    (-44, 299), (-36, 297), (-30, 299), (-22, 299), (-12, 298), (-10, 300), (-10, 305), (-70, 305), (-70, 252)),
                     "tall grass behind the left greenside bunkers and behind the green to the cart path (golfer's drawing)"))
# reviewer A 2a (mown strip left of 2's fairway) was withdrawn in REVIEW_A.md v2: not applied.
# reviewer A 3a: the tree row in front of the yard beyond the hand corridor (345-413)
LATE["3"].append(Z("recovery", poly((38.3, 345.4), (39.6, 363.4), (41.9, 383.4), (45.4, 413.3), (52.4, 413.2), (48.9, 383.3), (45.6, 363.3), (43.3, 345.4)),
                   "tree row before the yard 345-413 (NAIP 2023)"))
# reviewer C 13-A: the ditch across 13 bank to bank (8 yds; the OSM strip is 4-5 and leaves rough between the fairway
# edge and the water, which stops rolling balls in the engine); the staked margin is outside the trench (see 10)
LATE["13"] = [Z("water", poly((-37, 297.6), (-28.1, 307), (-14.4, 327.2), (-8, 337.5), (-2, 349), (10.6, 369.1), (17.4, 364.9), (5, 345),
                              (-1, 333.5), (-14.7, 312.2), (-21.9, 302), (-31, 292.4), (-37.8, 283.5), (-44.2, 288.5)),
                "ditch across the hole, bank to bank 284-369 (DTM + NAIP 2023)")]

# 2026-11-13 strategy pass, reviewer D (second_pass/REVIEW_D.md, second shots): ground near the greens. None is inside a
# tee-shot oval (the tee solve is unchanged); mapped so the lie under a ball there is right. Lidar Dec 2020 grass
# height / Sentinel-2 NDVI Nov 2026 inside each: 6-B 0.10 m, 52 % over 0.10 m, NDVI 0.71; 15-C 0.09 m, 48 %, 0.67;
# 3-D 0.08 m, 45 %, 0.70; 1-E 0.09 m, 48 %, 0.48 (mown rough reads 0.01 m, 0 %; standing native 0.55-0.60 NDVI).
LATE.setdefault("6", []).append(Z("water", poly((-45.8, 573), (-28, 575), (-20, 569), (-5, 567.5), (2, 575), (10, 582), (13, 578), (12, 567), (3, 561), (-3, 564),
                                                (-20, 564), (-27.5, 561), (-37, 550), (-45, 539), (-47.5, 550), (-48, 567)),
                                   "pond behind and back-left of the green (NAIP 2023 RGB + CIR), 6-A"))
EXTRA.setdefault("6", []).append(Z("native", poly((50, 350), (52, 380), (50, 400), (44, 420), (38, 440), (36, 460), (24, 480), (21, 500), (23, 520), (20, 540),
                                                  (12, 556), (14, 566), (90, 566), (90, 350)),
                                    "unmown field right of the hole from 350 to the green, 6-B"))
EXTRA.setdefault("15", []).append(Z("native", poly((-44, 452), (-30, 450), (-20, 449), (-12, 447), (-4, 446), (7, 448), (11, 456), (9, 466), (0, 473), (-25, 473), (-44, 465)),
                                     "tall vegetation 5-8 yds behind the green, 15-C"))
EXTRA.setdefault("3", []).append(Z("native", poly((72, 560), (73, 600), (74, 630), (70, 645), (55, 653), (35, 652), (35, 658), (60, 660), (78, 650), (84, 630), (84, 560)),
                                    "tall-grass strip before the right tree line by the green, wrapping behind, 3-D"))
EXTRA.setdefault("1", []).append(Z("native", poly((30, 345), (31, 370), (33, 390), (28, 400), (15, 404), (-5, 402), (-5, 412), (30, 412), (52, 400), (52, 345)),
                                    "tall grass right of and behind the green, 1-E"))
