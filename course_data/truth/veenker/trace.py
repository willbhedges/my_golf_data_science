"""Veenker Memorial (Ames, IA), Blue tees: hand trace of the landing corridors (course_data/truth/corridor.py).

Coordinates: (x = yds right of the tee line, along = yds from the tee) in each hole's corridor frame
(render/frames.json). Order = precedence (later wins); unzoned = rough. Per zone source: fairway / first cut
from the NAIP 2023 0.3 m photo + CIR (mowing pattern); trees from the 3DEP lidar canopy (HAG > 2.5 m, the
crown edge) checked on the photo; long grass from the photo across NAIP years + lidar low vegetation.
"""
from corridor import Z, band, ell, poly, rect  # noqa: F401

H = {}

# ---------------------------------------------------------------- 1 (par 4, 435)
H["1"] = dict(zones=[
    Z("first_cut", band([(145, -26), (200, -25), (250, -27), (300, -31), (345, -36)],
                        [(145, 21), (200, 21), (250, 19), (300, 16), (345, 13)])),
    Z("fairway", band([(145, -17), (200, -17), (250, -19), (300, -21), (345, -25)],
                      [(145, 18), (200, 18), (250, 15), (300, 11.5), (345, 8.5)])),
    Z("recovery", ell(-38, 190, 9.5, 10)),
    Z("recovery", ell(-57, 183.5, 9, 9.5)),
    Z("recovery", ell(-35, 160, 11, 10)),
    Z("recovery", ell(-22, 145, 6, 5)),
    Z("recovery", ell(29, 215, 7, 8)),
    Z("recovery", ell(47, 227, 15, 15)),
    Z("recovery", ell(48, 191, 16, 11)),
    Z("recovery", ell(42.5, 157, 10.5, 9)),
    Z("recovery", poly((25, 352), (43, 352), (50, 338), (51, 320), (50, 306), (45, 302), (33, 302), (28, 310), (29, 330), (25, 342))),
    Z("recovery", ell(37.5, 279, 6, 5)),
    Z("recovery", ell(66, 285, 6, 6)),
    Z("recovery", ell(56, 311, 4, 4)),
    Z("recovery", ell(22.5, 308.5, 5, 4.5), "dead / leafless tree (lidar 2.5-8 m, grey in NAIP 2023)"),
    Z("recovery", ell(-52, 282.5, 7.5, 6)),
    Z("recovery", ell(-29.5, 255, 6.5, 7.5)),
    Z("recovery", ell(-51, 344, 11, 9)),
    Z("recovery", poly((-72, 300), (-62, 302), (-60, 312), (-61, 335), (-72, 337))),
], note="Straight par 4. Mown fairway ~35 yds, a lighter first-cut collar (wider on the left, 8-11 yds) inside "
        "the irrigated band; tan rough beyond is mown (cart paths run through it, no texture), not long grass. "
        "Trees = lidar crowns, scattered both sides from 30 yds out.", confidence="high")

# ---------------------------------------------------------------- 2 (par 4, 334)
H["2"] = dict(zones=[
    Z("fairway", band([(150, -21), (160, -23), (180, -24), (200, -23), (220, -22), (240, -18), (250, -15), (260, -13),
                       (285, -10), (290, -2)],
                      [(150, 4), (170, 5), (200, 6), (230, 8), (245, 10), (255, 14), (280, 15), (288, 8), (290, -2)])),
    Z("fairway", ell(-14, 334, 11, 11), "green (product LIE_MAP: green -> fairway)"),
    Z("recovery", poly((-75, 140), (-14, 140), (-16, 150), (-20, 160), (-24, 170), (-29, 180), (-31, 190), (-26, 200),
                       (-27.5, 210), (-23, 220), (-24, 230), (-19, 240), (-18, 250), (-21, 260), (-20, 270), (-12, 280),
                       (-11, 290), (-15, 300), (-27, 310), (-37, 320), (-40, 330), (-45, 340), (-47, 352), (-75, 352))),
    Z("recovery", poly((75, 140), (12, 140), (11, 150), (10, 160), (10, 170), (10, 180), (8, 190), (8, 200), (9, 210),
                       (10, 220), (10, 230), (11, 240), (15, 248), (22, 250), (22, 262), (35, 265), (35, 285),
                       (22.5, 287), (22.5, 306), (40, 307), (60, 300), (75, 300)),
      "right tree line just right of the cart path (lidar crown edge, 2nd pass); incl. 0.5-2.5 m shrubs at 205-220"),
    Z("recovery", poly((38, 322), (65, 320), (75, 320), (75, 352), (30, 352), (35, 340))),
], note="Tree-lined chute, cart path down the right edge of the fairway. NAIP 2023 (2 Sep) has long tree SHADOWS "
        "across the left half of the fairway (dark purple in CIR, no crowns): the left tree line is the lidar crown "
        "edge (-20 to -31), fairway edges from NAIP 2021 (less shadow). Fairway ends ~288; rough approach to the "
        "green (322-345, x -25..-3). No distinct first cut.", confidence="medium (left fairway edge under shadow, +/-3 yds)")

# ---------------------------------------------------------------- 3 (par 4, 333; measured 318)
H["3"] = dict(zones=[
    Z("fairway", poly((0, 167), (-7, 170), (-10, 180), (-10, 220), (-8, 240), (-9, 262), (-6, 272), (-6, 279),
                      (10, 286), (46, 299), (48, 290), (44, 280), (38, 270), (33, 262), (32, 250), (32, 230), (29, 200),
                      (26, 175), (20, 167))),
    Z("fairway", poly((10, 288), (46, 299), (48, 305), (30, 306), (12, 302)), "approach above the cart path"),
    Z("fairway", ell(56.5, 288.5, 8.5, 8.5), "green"),
    Z("fairway", ell(-56, 290, 11, 17), "green of another hole (left)"),
    Z("sand", ell(54.5, 271, 7.5, 6)),
    Z("recovery", poly((-75, 140), (-12, 140), (-11.7, 150), (-10.8, 160), (-14, 170), (-17.5, 180), (-20, 190),
                       (-24, 200), (-30, 210), (-32.5, 215), (-35, 220), (-38, 226), (-75, 226))),
    Z("recovery", ell(-14, 229.5, 8.5, 8.5)),
    Z("recovery", ell(-25, 236, 7, 7)),
    Z("recovery", poly((-75, 236), (-38, 237), (-36, 250), (-40, 256), (-75, 256))),
    Z("recovery", ell(-6, 265, 5, 5), "small trees at the cart-path junction: 2023 CIR crowns vs 2020 lidar differ by ~5 yds"),
    Z("recovery", ell(-5, 276, 6, 4.5)),
    Z("recovery", poly((75, 140), (2, 140), (5, 150), (13, 155), (21.7, 160), (26, 165), (38, 170), (41.7, 175), (46.7, 180),
                       (46.7, 190), (51.7, 195), (46.7, 200), (46.7, 210), (41.7, 220), (35, 230), (29, 235), (40, 240),
                       (40, 250), (34, 260), (38, 268), (45, 275), (60, 278), (75, 278))),
    Z("recovery", poly((-75, 310), (-40, 314), (-10, 312), (20, 312), (45, 314), (75, 318), (75, 352), (-75, 352))),
], note="Dogleg right to a green at (57, 289) behind a bunker; cart path crosses at 280-300. RGB shadows put the "
        "right tree line ~15 yds too far in: crowns from lidar + CIR (the right trees start 5-20 yds outside the "
        "fairway). Trees straight ahead from 312 (hole is 318 measured).", confidence="medium-high")

# ---------------------------------------------------------------- 4 (par 4, 349)
H["4"] = dict(zones=[
    Z("first_cut", band([(145, -39), (200, -38), (245, -34)], [(145, -32), (200, -31), (245, -27)]),
      "left collar (lighter in CIR) between the fairway and the cart path"),
    Z("fairway", band([(145, -33), (200, -32), (245, -28), (250, -25), (260, -23), (270, -20), (276, -17), (280, -5),
                       (300, 1), (310, 3), (319, 6)],
                      [(145, 1), (190, 2), (200, 4), (230, 5), (245, 8), (250, 10), (270, 20), (290, 25), (300, 26),
                       (310, 28), (319, 27)])),
    Z("fairway", ell(39, 334, 11, 9), "green"),
    Z("sand", ell(13, 325.5, 7, 6)),
    Z("sand", ell(39.5, 314, 6.5, 3.5)),
    Z("recovery", poly((-28, 300), (-25, 311), (-15, 312), (-6, 308), (-1, 298), (0, 290), (-6, 283), (-15, 277),
                       (-20, 280), (-25, 290)), "big tree on the left edge of the fairway, 277-312"),
    Z("recovery", poly((75, 140), (-1.7, 140), (-1.7, 150), (0.8, 160), (1, 175), (1.7, 190), (9, 200), (11.7, 206),
                       (20, 212), (26, 220), (25, 230), (25, 245), (30, 250), (26.7, 260), (26, 280), (28, 290),
                       (21.7, 300), (28, 305), (35, 310), (48, 315), (58, 320), (62, 330), (75, 335))),
    Z("recovery", poly((-55, 187.5), (-38, 190), (-38, 200), (-45, 205.5), (-55, 205))),
    Z("recovery", poly((-75, 162), (-48, 163), (-48, 183), (-75, 184))),
    Z("recovery", poly((-48, 237.5), (-32.5, 240), (-32.5, 250), (-32, 253), (-48, 255), (-53, 250), (-53, 230), (-75, 230), (-75, 257), (-53, 257))),
    Z("recovery", poly((-75, 322), (-32, 350), (-75, 352))),
    Z("recovery", ell(-38.5, 323, 6.5, 6)),
    Z("recovery", poly((8, 342), (21, 342), (21, 352), (8, 352))),
], note="Slight dogleg right along a wooded right side; a single big tree guards the left of the landing area at "
        "277-312 (x -28..0). RGB shadows overstate the right trees at 190-210; crowns from lidar + CIR. Fairway "
        "right edge has a tan rough strip (5-20 yds) to the trees from 200 on.", confidence="medium-high")

# ---------------------------------------------------------------- 5 (par 4, 402)
H["5"] = dict(zones=[
    Z("fairway", poly((-20, 145), (-27, 148), (-29, 160), (-31, 200), (-29, 240), (-24, 250), (-10, 253), (5, 253),
                      (13, 245), (13, 240), (8, 200), (7, 160), (5, 150), (0, 145))),
    Z("recovery", poly((-75, 157), (-43, 158), (-43, 187), (-55, 190), (-55, 236), (-75, 236))),
    Z("recovery", ell(-43, 218, 5, 5)),
    Z("recovery", ell(-40, 246, 5, 5)),
    Z("recovery", poly((75, 140), (11.7, 140), (12, 150), (12, 160), (13, 170), (13, 180), (12, 190), (11, 200),
                       (10, 210), (13, 220), (15, 230), (25, 238), (40, 240), (55, 245), (75, 245)),
      "right tree line = lidar crown edge over the cart path (2nd pass)"),
    Z("recovery", ell(-65, 251, 10, 13)),
    Z("recovery", poly((-37, 262), (-30, 256), (-22, 258), (-20, 270), (-22, 287), (-33, 288), (-35, 280))),
    Z("recovery", poly((-75, 280), (-50, 282), (-38, 287), (-35, 285), (-15, 285), (-10, 288), (5, 288), (7, 300),
                       (15, 300), (15, 327), (0, 330), (-75, 335))),
    Z("recovery", poly((0, 320), (28, 320), (28, 352), (0, 352))),
    Z("recovery", poly((21, 280), (42, 272), (45, 272), (65, 272), (75, 272), (75, 352), (55, 352), (43, 342), (43, 317),
                       (55, 317), (55, 290), (28, 287)), "right tree line; 0.5-2.5 m shrubs at the pond's south bank"),
    Z("water", poly((18, 300), (20, 290), (28, 284), (45, 284), (55, 288), (56, 295), (50, 305), (40, 312), (35, 316),
                    (25, 316), (20, 310)), "pond (algae: pale in RGB, no lidar returns)"),
    Z("water", poly((-53, 345), (-50, 330), (-45, 322), (-35, 316), (-20, 314), (-8, 318), (-5, 330), (-8, 345),
                    (-15, 352), (-50, 352)), "pond (2023 CIR; the 2020 lidar no-return area sits ~10 yds right)"),
], note="Oval fairway ends at 253; beyond is mown rough among scattered trees, a pond at 284-316 right of the line "
        "(x +18..+56) and a second pond / tree band from 285 left. Card 402: the drive lands in the oval or the "
        "rough short of the ponds. A building and service road at the bottom right (x > +55, 150-185) are not "
        "marked OB (no property line visible in the corridor).", confidence="medium")

# ---------------------------------------------------------------- 7 (par 5, 590; Blue tee on a lidar pad)
H["7"] = dict(zones=[
    Z("fairway", poly((-8, 268), (-10, 285), (-13, 300), (-15, 320), (-12, 335), (-8, 345), (0, 350), (2, 348), (10, 340),
                      (20, 330), (26, 325), (22, 310), (20, 300), (25, 285), (26, 278), (22, 272), (10, 268))),
    Z("fairway", ell(-58, 283, 10, 12), "green of another hole"),
    Z("sand", ell(-50, 288, 4, 6)),
    Z("recovery", poly((-48, 203), (-38, 202), (-30, 210), (-15, 205), (-10, 212), (0, 212), (4, 220), (2, 232), (-8, 238),
                       (-25, 241), (-38, 236), (-45, 228))),
    Z("recovery", poly((-39, 198), (-30, 201), (-20, 198), (-18, 185), (-11, 178), (-12, 168), (-20, 162), (-33, 163),
                       (-37, 175), (-40, 188))),
    Z("recovery", ell(-36, 152, 9, 8)),
    Z("recovery", ell(-47.5, 238.5, 3.5, 3.5)),
    Z("recovery", ell(-47.5, 225.5, 2.5, 3.5)),
    Z("recovery", ell(-23.5, 307, 11.5, 14)),
    Z("recovery", ell(-35, 271, 7.5, 9)),
    Z("recovery", ell(-28, 255, 4.5, 5)),
    Z("recovery", poly((-24, 245), (-15, 245), (-15, 268), (-24, 268))),
    Z("recovery", ell(27, 261.5, 12, 11.5)),
    Z("recovery", poly((75, 140), (21.7, 140), (21.7, 150), (21, 160), (26, 170), (22.5, 180), (24, 190), (22.5, 200),
                       (21.7, 210), (21, 220), (21.7, 230), (26, 240), (35, 245), (42, 250), (38, 270), (35, 285),
                       (29, 290), (29, 300), (28, 310), (31, 320), (33, 330), (40, 340), (45, 352), (75, 352))),
    Z("recovery", poly((-75, 312), (-50, 312), (-50, 345), (-55, 352), (-75, 352))),
], note="The Blue tee (590) sits far back: 150-262 is an open band of mown, sun-bleached rough between tree clumps "
        "(left) and woods (right); the fairway starts at ~268 (x -15..+26) and runs to the creek beyond 345. "
        "A 0.5-2.5 m lidar strip along the cart path at 330-350 right is not marked (no canopy, hedge or tall grass "
        "not visible in 2023). Highway OB right is beyond +60 here.", confidence="medium (fairway start / rough tone)")

# ---------------------------------------------------------------- 9 (par 5, 537)
H["9"] = dict(zones=[
    Z("first_cut", band([(162, -26), (170, -34), (245, -34), (250, -33)], [(162, 0), (170, 2), (240, 2), (250, 6)]),
      "collar visible in CIR on both sides of the lower fairway"),
    Z("fairway", poly((-26, 163), (-30, 172), (-30, 260), (-27, 270), (-20, 280), (-8, 300), (2, 320), (12, 340),
                      (14, 350), (62, 350), (62, 345), (60, 330), (50, 320), (35, 310), (28, 300), (27, 290),
                      (15, 280), (6, 275), (5, 260), (3, 250), (0, 245), (-2, 240), (-2, 170), (-6, 163))),
    Z("recovery", ell(10, 241, 8, 9)),
    Z("recovery", ell(15.5, 222.5, 4.5, 5)),
    Z("recovery", ell(11, 195, 7.5, 8)),
    Z("recovery", ell(30, 213, 7, 8)),
    Z("recovery", ell(39, 190, 13, 15)),
    Z("recovery", ell(42, 166, 9, 9)),
    Z("recovery", ell(43, 231, 9, 10)),
    Z("recovery", ell(-56, 237, 10, 13)),
    Z("recovery", ell(-55, 180, 8, 7)),
    Z("recovery", ell(-54, 154, 9, 9)),
    Z("recovery", ell(21, 262, 13, 15)),
    Z("recovery", ell(45, 295, 14, 14)),
    Z("recovery", poly((-30, 285), (-22, 282), (-12, 292), (-5, 305), (-2, 318), (0, 330), (5, 345), (-5, 352),
                       (-22, 345), (-25, 330), (-20, 315), (-28, 300))),
    Z("recovery", ell(-30, 316, 7, 9)),
    Z("recovery", ell(-47, 311, 5, 6)),
    Z("recovery", ell(-57, 290, 9, 12)),
    Z("recovery", poly((-75, 245), (-58, 245), (-58, 273), (-75, 273))),
    Z("recovery", ell(-50.5, 251, 6.5, 6)),
    Z("recovery", ell(63, 331, 5, 9)),
], note="Fairway bends right after 250 between two tree groups. The 2020 lidar (leaf-off) shows these open-grown "
        "deciduous trees as small 2.5-8 m crowns, much smaller than NAIP 2021 / 2023: crowns traced on the CIR "
        "(bright, textured) with the shadow (dark, up-left of each crown) excluded.", confidence="medium")

# ---------------------------------------------------------------- 10 (par 5, 560)
H["10"] = dict(zones=[
    Z("fairway", band([(145, -25), (200, -20), (245, -13), (255, -10), (275, 0), (300, 25), (320, 30), (345, 30)],
                      [(145, -3), (180, 8), (200, 13), (225, 22), (250, 32), (270, 40), (285, 52), (300, 62), (345, 65)])),
    Z("recovery", ell(7.5, 163, 10, 16)),
    Z("recovery", ell(34.5, 196, 6.5, 9)),
    Z("recovery", ell(37, 180, 5, 8)),
    Z("recovery", ell(36.5, 160, 8.5, 15)),
    Z("recovery", ell(57, 156, 10, 11)),
    Z("recovery", ell(41, 227, 6.5, 10)),
    Z("recovery", poly((37, 237), (58, 237), (58, 250), (37, 250))),
    Z("recovery", ell(-35.5, 178.5, 4.5, 5.5)),
    Z("recovery", ell(-41, 150, 5, 5)),
    Z("recovery", poly((-15, 250), (-5, 244), (12, 250), (14, 262), (17, 275), (17, 290), (10, 300), (-2, 300), (-7, 290),
                       (-12, 278), (-15, 265))),
    Z("recovery", poly((-45, 352), (5, 352), (5, 325), (0, 310), (-2, 300), (-8, 290), (-15, 292), (-25, 300), (-30, 315),
                       (-38, 322), (-45, 335))),
    Z("recovery", poly((7, 352), (30, 352), (30, 315), (25, 300), (12, 300), (8, 315))),
    Z("recovery", ell(48, 259, 11, 14)),
], note="The fairway runs up the right, past a tree group that blocks the tee line from 250 (x -15..+17) and a "
        "second tree band straight on at 290-350; the play is right of the trees toward the cart path. Left of the "
        "trees (x -35..-15) is rough, beyond the left cart path another hole's fairway. Crowns from CIR (2020 "
        "lidar under-sizes these leaf-off crowns).", confidence="medium-high")

# ---------------------------------------------------------------- 12 (par 4, 330; Blue tee on a lidar pad)
H["12"] = dict(zones=[
    Z("fairway", band([(145, -7), (200, -7), (240, -5), (250, 0), (260, 3), (270, 2), (280, 8), (290, 14), (300, 25)],
                      [(145, 11), (200, 12), (230, 14), (240, 22), (255, 35), (270, 45), (290, 50), (300, 52)])),
    Z("fairway", ell(50, 318, 12, 15), "green"),
    Z("sand", ell(31, 311, 6, 7)),
    Z("recovery", poly((17, 140), (17, 200), (18, 215), (20, 228), (30, 238), (45, 243), (60, 240), (75, 238), (75, 140)),
      "right woods: lidar crown edge (2nd pass, was 2 yds further in)"),
    Z("recovery", poly((55, 352), (55, 305), (58, 290), (55, 270), (58, 255), (75, 250), (75, 352))),
    Z("recovery", ell(-18, 172, 10, 12)),
    Z("recovery", ell(-25, 191, 3.5, 4)),
    Z("recovery", ell(-21, 213, 10, 12)),
    Z("recovery", ell(-17, 150, 9, 8)),
    Z("recovery", ell(-50, 173, 4, 4)),
    Z("recovery", ell(-50, 190, 4, 3.5)),
    Z("recovery", ell(-69, 215, 6, 12)),
    Z("recovery", ell(-10, 244, 13, 8)),
    Z("recovery", ell(-58, 245, 7, 6)),
    Z("recovery", ell(-2, 274, 9, 8)),
    Z("recovery", ell(-21, 324, 6, 6)),
    Z("recovery", ell(-22, 340, 6, 5)),
    Z("recovery", ell(20, 341, 6, 5)),
    Z("recovery", ell(25, 322, 5, 4)),
    Z("ob", poly((-75, 352), (-24, 352), (-26, 340), (-33, 310), (-44, 280), (-55, 250), (-66, 220), (-75, 197)),
      "the highway (US 30 frontage) left: line at the grass edge of the shoulder; no fence visible"),
], note="Dogleg right; big woods on the right to 240, then the fairway swings right to the green (50, 318). Left "
        "of the cart path at 290-345 the rough is mottled / weedy in 2023 (pale texture in CIR) but not tan or "
        "tall in 2021: kept as rough (ambiguous, see NOTES). Highway OB on the left from ~200 out.",
                confidence="medium")

# ---------------------------------------------------------------- 14 (par 4, 416)
H["14"] = dict(zones=[
    Z("fairway", band([(145, -25), (200, -25), (220, -23), (230, -20), (250, -10), (260, -3), (270, 2), (280, 7), (290, 13),
                       (300, 18), (320, 26), (345, 37)],
                      [(145, 0), (200, 2), (228, 6), (240, 8), (255, 10), (262, 25), (270, 38), (285, 40), (300, 48),
                       (320, 55), (345, 63)])),
    Z("recovery", poly((6, 215), (6, 228), (9, 240), (10, 255), (14, 262), (23, 262), (28, 253), (32, 246), (45, 247),
                       (52, 250), (60, 254), (75, 256), (75, 178), (60, 177), (45, 175), (33, 180), (28, 193), (22, 200),
                       (10, 205), (7, 210))),
    Z("recovery", ell(13, 192, 5, 5.5)),
    Z("recovery", ell(15, 179, 4.5, 5)),
    Z("recovery", ell(14, 147, 5, 4)),
    Z("recovery", poly((-75, 205), (-63, 205), (-55, 212), (-45, 220), (-43, 235), (-50, 245), (-75, 248))),
    Z("recovery", ell(-68, 192, 8, 10)),
    Z("recovery", ell(-42, 193, 3, 3.5)),
    Z("recovery", ell(-52, 148, 8, 6)),
    Z("recovery", poly((-75, 245), (-55, 245), (-45, 248), (-38, 255), (-32, 262), (-30, 280), (-35, 290), (-40, 305),
                       (-50, 315), (-60, 320), (-75, 322))),
    Z("recovery", ell(-11, 278, 7.5, 8)),
    Z("recovery", poly((-10, 286), (5, 284), (10, 292), (14, 305), (12, 318), (10, 328), (2, 335), (-8, 338), (-15, 330),
                       (-17, 315), (-15, 300))),
    Z("recovery", ell(-35, 330, 10, 17)),
    Z("recovery", poly((0, 340), (5, 330), (15, 325), (28, 325), (32, 335), (25, 352), (0, 352))),
    Z("recovery", ell(48, 274, 7, 10)),
    Z("recovery", ell(58, 293, 5, 7)),
], note="Fairway straight to ~230 then a diagonal band right (dogleg right) toward a green at ~(+75, 405). A crown "
        "at (+10..+28, 225-262) pinches the bend from the right; woods left beyond -30 from 245. Crowns from CIR 2023; "
        "the 2020 lidar has the big left woods but fewer crowns in the middle groups.", confidence="medium-high")

# ---------------------------------------------------------------- 15 (par 4, 420; dogleg right, green at (+151, 308))
H["15"] = dict(zones=[
    Z("native", poly((-75, 282), (-50, 278), (-35, 281), (-20, 282), (-8, 280), (2, 283), (4, 292), (-5, 296), (-10, 310),
                     (-15, 320), (-20, 328), (-35, 328), (-50, 325), (-75, 327)),
      "unmown: pale grey in CIR (dry, no irrigation), tan and tufted in NAIP 2023 and 2021"),
    Z("fairway", poly((-75, 145), (-75, 210), (-68, 222), (-55, 235), (-40, 248), (-30, 256), (-15, 264), (-2, 265),
                      (10, 258), (18, 248), (22, 240), (18, 232), (10, 224), (0, 214), (-10, 206), (-20, 196), (-25, 176),
                      (-27, 145))),
    Z("recovery", poly((-18, 140), (-18, 170), (-15, 185), (-10, 198), (0, 202), (10, 200), (20, 198), (25, 208), (30, 218),
                       (33, 230), (38, 240), (45, 248), (75, 255), (75, 140))),
    Z("recovery", poly((5, 295), (10, 285), (15, 275), (22, 268), (30, 270), (32, 285), (28, 300), (15, 305))),
    Z("recovery", poly((-30, 290), (-22, 285), (-10, 286), (-3, 292), (-2, 302), (-10, 307), (-25, 305))),
    Z("recovery", poly((-75, 330), (-55, 333), (-45, 328), (-35, 335), (-30, 345), (-25, 352), (-75, 352))),
    Z("recovery", poly((-75, 250), (-60, 252), (-45, 256), (-32, 262), (-28, 272), (-35, 279), (-55, 281), (-75, 279))),
    Z("recovery", poly((32, 287), (45, 280), (56, 288), (56, 300), (45, 308), (34, 303))),
    Z("recovery", poly((40, 235), (60, 238), (75, 240), (75, 262), (60, 258), (48, 250))),
    Z("recovery", poly((-25, 345), (-18, 322), (-10, 312), (-5, 322), (-8, 345), (-20, 352))),
    Z("water", band([(205, 42), (220, 36), (240, 26), (250, 23), (260, 21), (270, 19), (280, 18), (290, 12), (300, 5),
                     (310, 0), (320, -2), (330, -5), (345, -12), (352, -14)],
                    [(205, 58), (220, 50), (240, 40), (250, 38), (260, 35), (270, 32), (280, 32), (290, 28), (300, 20),
                     (310, 17), (320, 12), (330, 8), (345, 3), (352, 1)]), "creek (dark in CIR, no lidar returns)"),
], note="Sharp dogleg right (green at +151, 308 across the creek): the drive lands on the wide fairway left of a "
        "tree mass that covers the tee line from 150 to 200 (x > -18). Creek diagonally from (+50, 210) to (-12, 350). "
        "Top-left (-75..-5, 280-328): the only clearly unmown long grass at Veenker in these corridors (pale grey in "
        "CIR, tan in 2021 and 2023).", confidence="medium (native extent; creek under canopy +/-5 yds)")

# ---------------------------------------------------------------- 16 (par 5, 544; Blue tee on a lidar pad)
H["16"] = dict(zones=[
    Z("native", poly((-26, 145), (20, 145), (20, 174), (5, 176), (-10, 175), (-26, 173)),
      "unmown carry area in front of the fairway: tan / tufted in 2021 and 2023, pale-grey speckled in CIR"),
    Z("fairway", band([(176, -22), (200, -21), (240, -23), (250, -26), (280, -29), (310, -32), (345, -36)],
                      [(176, 18), (200, 18), (240, 16), (245, 8), (250, 2), (280, 0), (310, -2), (345, -5)])),
    Z("recovery", band([(140, -75), (352, -75)],
                       [(140, -28), (170, -27), (190, -27), (200, -23), (215, -22), (225, -26), (240, -28), (255, -32),
                        (270, -35), (280, -40), (290, -52), (295, -75)])),
    Z("recovery", band([(140, 21), (240, 20), (250, 12), (270, 10), (300, 9), (310, 7), (352, 6)], [(140, 75), (352, 75)]),
      "right woods: lidar crown edge (2nd pass: a 5-8 yd rough strip between fairway and trees from 250)"),
    Z("water", band([(300, 22), (330, 23), (352, 25)], [(300, 38), (330, 40), (352, 42)]), "creek inside the right woods"),
], note="Straight par 5 down a chute: woods both sides (crown edges from CIR 2023 + lidar), a creek inside the right "
        "woods from 300. The first ~30 yds of the corridor (145-175) is an unmown carry area (native, medium "
        "confidence: tan and tufted in both years, but it could be a dry, rarely-mown forward-tee strip).",
                confidence="medium-high")

# ---------------------------------------------------------------- 18 (par 5, 534)
H["18"] = dict(zones=[
    Z("fairway", band([(162, -30), (170, -33), (200, -32), (240, -28), (260, -22), (290, -15), (320, -10), (345, -5)],
                      [(162, 3), (170, 4), (200, 5), (240, 6), (260, 10), (290, 14), (320, 16), (345, 18)])),
    Z("recovery", ell(20, 178, 10, 17)),
    Z("recovery", ell(36, 175, 6, 10), "dead / leafless tree (grey in CIR and RGB, small lidar returns): still blocks"),
    Z("recovery", ell(56, 170, 5, 7)),
    Z("recovery", poly((10, 195), (8, 215), (9, 235), (5, 250), (5, 262), (10, 276), (28, 276), (33, 262), (33, 240),
                       (33, 215), (30, 197))),
    Z("recovery", poly((38, 195), (55, 192), (75, 195), (75, 230), (60, 228), (45, 225), (38, 215))),
    Z("recovery", poly((35, 252), (50, 248), (75, 250), (75, 292), (55, 292), (45, 290), (38, 278))),
    Z("recovery", ell(29, 307, 13, 22)),
    Z("recovery", poly((-25, 290), (-12, 288), (-8, 300), (-10, 330), (-15, 345), (-18, 352), (-28, 352), (-28, 320),
                       (-26, 300))),
    Z("recovery", ell(-53, 212, 9, 13)),
    Z("recovery", poly((-75, 160), (-65, 160), (-60, 175), (-62, 195), (-75, 200))),
    Z("recovery", poly((-75, 245), (-62, 248), (-50, 258), (-48, 275), (-52, 292), (-60, 300), (-75, 300))),
    Z("recovery", poly((-75, 305), (-62, 305), (-58, 315), (-60, 330), (-75, 332))),
    Z("recovery", ell(-22, 146, 8, 6)),
], note="Parkland: open-grown trees both sides, fairway 35 yds. NAIP 2023 shadows fall to the left (-x) of every "
        "crown in this frame: crowns traced on the bright CIR part, which the 2020 lidar confirms (crowns sit 5-10 "
        "yds right of the dark blobs).", confidence="medium-high")

TRACE = dict(holes=H, missing=[])
