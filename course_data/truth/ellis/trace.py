"""Ellis Golf Course (Cedar Rapids, IA), Blue tees: hand trace of the landing corridors (course_data/truth/corridor.py).

Coordinates: (x = yds right of the tee line, along = yds from the tee) in each hole's corridor frame
(render/frames.json). Order = precedence (later wins); unzoned = rough. Hilly, tree-lined municipal course on the
Cedar River bluffs. The 3DEP lidar here is 2019, before the August 2020 derecho that felled many of the course's
trees: tree zones follow the crowns standing in NAIP 2023 (bright, textured in CIR; shadows - the dark side
toward the NW vector of each review - excluded), and lidar crowns absent in 2023 are NOT trees.
"""
from corridor import Z, band, ell, poly, rect  # noqa: F401

H = {}

# ---------------------------------------------------------------- 1 (par 4, 395)
H["1"] = dict(zones=[
    Z("fairway", band([(145, -22), (200, -22), (230, -26), (260, -27), (300, -27), (345, -28)],
                      [(145, 17), (200, 17), (230, 17), (260, 16), (300, 16), (345, 19)])),
    Z("recovery", ell(-38, 190, 10, 10)),
    Z("recovery", ell(-42, 250, 6, 6.5)),
    Z("recovery", ell(-43, 290, 5.5, 7)),
    Z("recovery", ell(-40, 314, 6, 7.5)),
    Z("recovery", ell(-36, 143, 7, 5)),
    Z("recovery", ell(34, 256, 4.5, 5.5)),
    Z("recovery", ell(36.5, 215.5, 3.5, 4.5)),
    Z("recovery", ell(36, 208, 3, 3)),
    Z("recovery", ell(52, 211, 4.5, 5.5)),
    Z("recovery", ell(59.5, 191.5, 3, 3)),
    Z("recovery", ell(47, 178.5, 3, 3.5)),
    Z("recovery", ell(62, 176, 3, 3.5)),
], note="Straight par 4 with single trees both sides. 2023 is a drought image (dormant rough white in CIR, the "
        "fairway irrigated pink). Several 2019-lidar crowns right (+15..+60, 140-200) and left (-45..-30, 150-175, "
        "260) are gone in 2023 (derecho; small replanted trees / stumps remain): not trees.", confidence="medium-high")

# ---------------------------------------------------------------- 2 (par 4, 365; dogleg right)
H["2"] = dict(zones=[
    Z("native", poly((-75, 140), (-30, 140), (-28, 170), (-30, 200), (-33, 220), (-40, 232), (-55, 238), (-75, 240)),
      "replanted prairie where the 2019-lidar woods stood (felled in the 2020 derecho): tufted, tan, unmown in 2023"),
    Z("fairway", poly((-22, 145), (-24, 200), (-22, 240), (-17, 255), (-8, 268), (0, 282), (5, 295), (15, 305), (25, 320),
                      (35, 345), (65, 345), (65, 250), (40, 248), (30, 245), (15, 240), (12, 200), (6, 170), (5, 145))),
    Z("sand", poly((16, 212), (19, 205), (24, 207), (25, 216), (23, 222), (17, 221))),
    Z("sand", poly((16, 235), (19, 230), (25, 231), (27, 238), (24, 243), (17, 242))),
    Z("recovery", poly((38, 212), (42, 205), (50, 205), (55, 215), (57, 228), (60, 240), (55, 246), (47, 242), (42, 232))),
    Z("recovery", ell(56, 185, 3, 3)),
    Z("recovery", ell(47, 176, 3, 3)),
    Z("recovery", ell(47, 151, 3.5, 3.5)),
    Z("recovery", ell(49, 258, 5, 6)),
    Z("recovery", ell(-40, 247, 6, 7)),
], note="Dogleg right. In the 2019 lidar a wood fills the left (-70..-30, 140-260) and a tree line crosses the "
        "corner (-35..0, 250-310); both are gone in 2023 (2020 derecho): the left is now tufted, unmown prairie "
        "(native) and the corner a stump-dotted band of dormant rough. Trees right only at 205-250.",
                confidence="medium (fairway edges in drought-dormant turf +/-4 yds)")

# ---------------------------------------------------------------- 3 (par 5, 481)
H["3"] = dict(zones=[
    Z("fairway", band([(145, -25), (200, -25), (240, -24), (270, -21), (300, -20), (345, -18)],
                      [(145, 19), (200, 20), (240, 19), (260, 16), (300, 14), (345, 15)])),
    Z("recovery", band([(140, 39), (170, 37), (200, 37), (230, 37), (250, 34), (258, 40), (265, 46), (280, 48), (300, 50),
                        (320, 51), (340, 48), (352, 46)], [(140, 75), (352, 75)]),
      "woods right (crowns in CIR 2023 and the 2019 lidar agree here)"),
    Z("recovery", ell(24, 262, 4.5, 6)),
    Z("recovery", ell(23, 282, 4.5, 6)),
    Z("recovery", ell(28, 301, 5.5, 7)),
    Z("recovery", ell(-36, 312, 5, 8)),
    Z("recovery", ell(-46, 344, 5, 5)),
], note="Straight par 5 along woods right; a row of three single trees right of the fairway at 255-310. The 2019 "
        "lidar's tree row left (-55..-35, 140-300) is gone in 2023 (derecho; stumps in dormant rough).",
                confidence="medium-high")

# ---------------------------------------------------------------- 5 (par 4, 385)
H["5"] = dict(zones=[
    Z("fairway", band([(145, -25), (200, -24), (250, -22), (300, -25), (345, -28)],
                      [(145, 20), (200, 18), (250, 14), (300, 14), (345, 15)])),
    Z("sand", ell(-21, 260, 5, 7)),
    Z("sand", ell(17, 219, 6, 8)),
    Z("sand", ell(54, 148, 6, 7)),
    Z("recovery", ell(37, 278, 5, 6.5)),
    Z("recovery", ell(33, 245, 5, 6.5)),
    Z("recovery", ell(37, 213, 5, 6.5)),
    Z("recovery", ell(42, 189, 3.5, 3.5)),
    Z("recovery", ell(-55, 244, 7, 7)),
    Z("recovery", ell(-63, 212, 8, 9)),
    Z("recovery", ell(-55, 176, 7, 7)),
    Z("recovery", ell(-68, 187, 5, 6)),
    Z("recovery", poly((-62, 140), (-62, 152), (-55, 162), (-45, 165), (-33, 160), (-28, 150), (-30, 140))),
], note="Straight par 4 with single trees both sides. The 2019 lidar has two rows of big trees (left -60..-35 "
        "and right +30..+50) the whole length; about half survive in 2023 (derecho). The thin linear 'canopy' at "
        "+15..+30 in the lidar is a power line, not trees.", confidence="medium")

# ---------------------------------------------------------------- 6 (par 4, 420; Blue tee on a lidar pad)
H["6"] = dict(zones=[
    Z("fairway", band([(145, -22), (200, -22), (250, -24), (300, -27), (345, -30)],
                      [(145, 11), (200, 11), (250, 11), (300, 13), (345, 15)])),
    Z("sand", ell(18, 237, 5, 9.5)),
    Z("sand", ell(-29, 203, 5, 12)),
    Z("sand", ell(53, 168, 5, 8)),
    Z("recovery", ell(-43, 253, 7.5, 8)),
    Z("recovery", ell(-37, 244, 3.5, 5)),
    Z("recovery", ell(-55, 152, 7, 7)),
    Z("recovery", ell(32, 251, 9, 7)),
    Z("recovery", ell(32, 281, 4.5, 4.5)),
    Z("recovery", ell(32, 194, 3.5, 4)),
    Z("recovery", ell(33, 173, 5, 8)),
], note="Straight, open par 4 with single trees; the 2019 lidar's tree rows (left -70..-50 at 145-225, right "
        "+20..+45 the whole length) are mostly gone in 2023. Linear lidar returns at +45..+55: power line.",
                confidence="medium-high")

# ---------------------------------------------------------------- 7 (par 4, 463)
H["7"] = dict(zones=[
    Z("first_cut", band([(145, -38), (200, -38), (240, -33), (270, -30), (300, -25), (330, -22), (345, -14)],
                        [(145, 9), (200, 12), (240, 15), (270, 20), (290, 30), (310, 34), (330, 30), (345, 30)]),
      "irrigated collar (green in the drought image, pink in CIR) outside the striped fairway"),
    Z("fairway", band([(145, -30), (200, -28), (250, -25), (280, -22), (320, -18), (345, -12)],
                      [(145, 5), (200, 8), (250, 12), (280, 15), (320, 18), (345, 20)])),
    Z("recovery", ell(31, 166, 7, 7)),
    Z("recovery", ell(40, 182, 3, 3)),
    Z("recovery", ell(41, 212, 3.5, 3.5)),
    Z("recovery", ell(-64, 220, 5, 5)),
    Z("recovery", ell(-56, 290, 3.5, 3.5)),
    Z("ob", band([(140, 61), (352, 61)], [(140, 75), (352, 75)]), "street right (fence line / curb at +61)"),
], note="Long straight par 4, very open (2019-lidar tree groups right at 200-280 and left at 210-340 are gone in "
        "2023). Drought image: the irrigated fairway + collar are the only green; the collar is mapped as first cut. "
        "A street runs along the right edge (+61): OB.", confidence="medium-high")

# ---------------------------------------------------------------- 9 (par 5, 534)
H["9"] = dict(zones=[
    Z("fairway", poly((-14, 170), (-20, 180), (-22, 200), (-25, 250), (-28, 280), (-30, 300), (-32, 345), (12, 345),
                      (12, 300), (18, 280), (22, 250), (22, 200), (18, 180), (10, 170))),
    Z("recovery", ell(-36, 152, 4, 4)),
    Z("recovery", ell(-38, 165, 4, 4.5)),
    Z("recovery", ell(-40, 176, 4, 4)),
    Z("recovery", ell(-31, 199, 3, 3.5)),
    Z("recovery", ell(-32, 218, 4, 4.5)),
    Z("recovery", ell(-40, 222, 4, 5)),
    Z("recovery", ell(-37, 238, 5, 5)),
    Z("recovery", poly((-62, 245), (-48, 245), (-44, 255), (-46, 275), (-55, 285), (-62, 285))),
    Z("recovery", ell(40, 232, 6, 6)),
    Z("recovery", ell(25, 273, 7, 6)),
    Z("recovery", ell(40, 272, 4, 4)),
    Z("recovery", ell(45, 263, 4, 4)),
    Z("recovery", ell(23, 290, 3.5, 3.5)),
    Z("recovery", ell(19, 312, 4, 4)),
    Z("recovery", ell(35, 309, 3.5, 3.5)),
    Z("recovery", ell(37, 338, 3, 3)),
    Z("ob", poly((-75, 140), (-46, 140), (-49, 200), (-53, 250), (-57, 300), (-61, 352), (-75, 352)),
      "street + houses left (line at the course-side curb)"),
], note="Par 5 along a residential street (left, OB at the curb); a row of small trees between the street and "
        "the fairway, single trees right. Fairway starts at ~170.", confidence="medium-high")

# ---------------------------------------------------------------- 10 (par 4, 321)
H["10"] = dict(zones=[
    Z("fairway", band([(145, -30), (200, -28), (250, -25), (270, -20), (290, -12), (300, -5)],
                      [(145, 17), (180, 16), (200, 18), (240, 16), (260, 17), (280, 22), (300, 22)])),
    Z("fairway", ell(13, 318, 12, 12), "green"),
    Z("sand", ell(-8, 315, 5, 7)),
    Z("sand", ell(-5, 298, 3.5, 3)),
    Z("sand", ell(17, 257, 5, 5.5)),
    Z("recovery", ell(34, 211, 12, 11)),
    Z("recovery", ell(31, 160, 13, 10)),
    Z("recovery", ell(36, 271, 9, 8)),
    Z("recovery", ell(40, 311, 8, 6)),
    Z("recovery", ell(46, 337, 9, 7)),
    Z("recovery", ell(-26, 278, 5, 5)),
    Z("recovery", ell(-26, 236, 5, 4)),
    Z("recovery", ell(-52, 305, 5, 4.5)),
    Z("recovery", ell(-32, 167, 3, 3)),
    Z("recovery", ell(-24, 171, 3.5, 3)),
    Z("recovery", ell(-30, 155, 4.5, 4.5)),
], note="Short par 4 to a green at (+13, 318); trees right (big crowns at 150-220 and 260-340) and small ones "
        "left. The tan area left of -35 is drought-dormant mown rough (mowing stripes), not long grass.",
                confidence="medium-high")

# ---------------------------------------------------------------- 12 (par 5, 519)
H["12"] = dict(zones=[
    Z("fairway", band([(145, -22), (200, -22), (250, -21), (300, -20), (345, -18)],
                      [(145, 12), (200, 12), (225, 14), (240, 20), (260, 22), (285, 20), (305, 14), (345, 12)])),
    Z("recovery", band([(140, 19), (180, 19), (200, 19), (215, 21), (225, 26), (235, 32), (250, 35), (270, 31), (290, 25),
                        (305, 19), (315, 17), (345, 16), (352, 16)], [(140, 75), (352, 75)]),
      "woods right (lidar edge; 2nd pass moved it 2-3 yds out: the dark band at +13..+19 is crown shadow)"),
    Z("recovery", poly((-75, 140), (-48, 140), (-35, 150), (-31, 170), (-32, 190), (-36, 210), (-45, 218), (-75, 218))),
    Z("recovery", poly((-75, 233), (-52, 236), (-38, 240), (-30, 248), (-35, 258), (-48, 268), (-60, 285), (-75, 290))),
    Z("recovery", ell(-27, 248, 5, 5)),
    Z("recovery", ell(-31, 298, 7, 8)),
    Z("recovery", poly((-75, 308), (-55, 305), (-45, 315), (-42, 335), (-45, 352), (-75, 352))),
], note="Par 5 in a wooded valley: woods right the whole way (crown edge +15..+35), a cart path and tree groups "
        "left. The 2019 lidar and 2023 crowns agree on this hole (no derecho loss in the landing area).",
                confidence="high")

# ---------------------------------------------------------------- 13 (par 4, 350; sharp dogleg left, green at (-82, 340))
H["13"] = dict(zones=[
    Z("fairway", poly((-22, 145), (-27, 200), (-37, 240), (-50, 258), (-65, 268), (-75, 272), (-75, 305), (-60, 302),
                      (-45, 295), (-30, 280), (-15, 262), (0, 250), (15, 240), (20, 220), (27, 200), (30, 150))),
    Z("recovery", poly((-75, 318), (-60, 320), (-45, 305), (-35, 297), (-25, 285), (-15, 268), (-5, 255), (5, 250),
                       (15, 236), (25, 238), (35, 246), (45, 250), (60, 250), (75, 248), (75, 352), (-75, 352)),
      "tree belt in front of the houses (crown edge: lidar + CIR)"),
    Z("recovery", ell(37, 211, 5, 5)),
    Z("recovery", ell(-42, 236, 3, 3)),
    Z("recovery", ell(-46, 205, 3.5, 3.5)),
    Z("ob", poly((-6, 352), (-8, 320), (0, 292), (10, 270), (28, 258), (50, 252), (75, 250), (75, 352)),
      "houses and yards (residential lots ahead / right)"),
], note="Sharp dogleg left (green at -82, 340): the tee line points at a tree belt and the back yards of houses "
        "(OB) from ~250 straight on; the landing area is the wide fairway bending left at 230-300. Some 2019-lidar "
        "trees left (-70..-40, 145-185) are gone in 2023.", confidence="medium")

# ---------------------------------------------------------------- 15 (par 4, 306; green at (+3, 305))
H["15"] = dict(zones=[
    Z("native", poly((-55, 245), (-35, 243), (-17, 248), (-15, 268), (-17, 290), (-35, 296), (-52, 293), (-58, 270)),
      "shrubs / tall grass on the slope left (lidar 0.5-2.5 m returns, dark tufts in 2023)"),
    Z("native", poly((42, 280), (50, 285), (58, 300), (62, 320), (55, 330), (45, 318), (40, 300)),
      "tall grass on the bank right of the right cart path"),
    Z("fairway", band([(165, -18), (200, -22), (250, -17), (280, -10), (292, -5)],
                      [(165, 15), (200, 17), (230, 22), (250, 27), (280, 25), (292, 20)])),
    Z("fairway", ell(3, 305, 16, 12), "green"),
    Z("recovery", ell(-31, 254, 6, 7)),
    Z("recovery", ell(-36, 182, 5, 5)),
    Z("recovery", ell(-62, 213, 4, 5)),
    Z("recovery", ell(-31, 228, 3, 3)),
    Z("recovery", ell(-65, 272, 5, 5)),
    Z("recovery", ell(43, 172, 6, 6)),
    Z("recovery", ell(37, 333, 6, 6)),
    Z("recovery", ell(-35, 345, 8, 6)),
    Z("recovery", poly((20, 140), (30, 150), (45, 165), (60, 175), (75, 175), (75, 140))),
], note="Short par 4 (306) to a green at (+3, 305); fairway between two cart paths. Left slope 245-295 is shrubby "
        "tall grass (2019 lidar 0.5-2.5 m, dark tufts in 2023): native. Most 2019-lidar crowns left (-45..-20, "
        "195-245) are gone in 2023.", confidence="medium")

# ---------------------------------------------------------------- 16 (par 4, 314; green at (-25, 315))
H["16"] = dict(zones=[
    Z("fairway", band([(145, -17), (200, -20), (240, -22), (270, -25), (295, -32)],
                      [(145, 16), (200, 18), (230, 18), (250, 14), (270, 10), (295, 0)])),
    Z("fairway", ell(-25, 315, 14, 12), "green"),
    Z("sand", ell(-32, 290, 5, 6)),
    Z("recovery", poly((-75, 140), (-25, 140), (-28, 160), (-33, 180), (-40, 195), (-48, 205), (-75, 205))),
    Z("recovery", poly((-62, 228), (-45, 228), (-35, 240), (-30, 255), (-28, 268), (-38, 283), (-55, 283), (-62, 265))),
    Z("recovery", poly((12, 262), (13, 285), (18, 300), (28, 305), (35, 298), (34, 278), (30, 260), (20, 255)),
      "crown right of the fairway (lidar crown edge; 2nd pass moved it 8 yds left onto the lidar)"),
    Z("recovery", poly((42, 250), (55, 245), (70, 248), (75, 252), (75, 300), (62, 302), (48, 296), (42, 275))),
    Z("recovery", ell(31, 242, 7, 7)),
    Z("recovery", ell(40, 206, 11, 8)),
    Z("recovery", ell(45, 182, 3, 3)),
    Z("recovery", ell(45, 170, 2.5, 2.5)),
    Z("recovery", poly((-75, 330), (-55, 330), (-45, 340), (-45, 352), (-75, 352))),
], note="Short par 4 (314) bending slightly left to a green at (-25, 315), between tree groups on both sides "
        "(crowns from lidar + CIR; NAIP shadows fall away from the tee here). Cart path right of the fairway.",
                confidence="medium-high")

# ---------------------------------------------------------------- 17 (par 5, 569)
H["17"] = dict(zones=[
    Z("fairway", poly((2, 175), (-2, 200), (0, 240), (2, 260), (5, 280), (-5, 300), (-10, 320), (-8, 345), (25, 345),
                      (20, 320), (15, 305), (25, 292), (35, 280), (38, 250), (37, 220), (36, 195), (33, 178))),
    Z("native", poly((-60, 335), (-50, 340), (-35, 328), (-20, 315), (-8, 300), (-2, 292), (-6, 288), (-15, 296),
                     (-28, 308), (-42, 320), (-58, 328)), "shrubby tall-grass ridge (lidar 0.5-2.5 m, tufted in 2023)"),
    Z("native", poly((14, 292), (22, 297), (35, 292), (45, 283), (50, 275), (45, 272), (35, 280), (22, 288)),
      "shrubby tall-grass ridge right"),
    Z("sand", ell(-43, 235, 4.5, 9)),
    Z("recovery", ell(-14, 218, 9, 9)),
    Z("recovery", ell(-24, 266, 3.5, 3.5)),
    Z("recovery", ell(-24, 247, 3, 3)),
    Z("recovery", ell(-25, 241, 2.5, 2.5)),
    Z("recovery", ell(-48, 312, 8, 7)),
    Z("recovery", ell(-8, 155, 5, 5)),
    Z("recovery", poly((-75, 140), (-50, 140), (-50, 160), (-60, 182), (-75, 186))),
    Z("recovery", poly((55, 140), (48, 150), (48, 165), (55, 178), (52, 195), (55, 215), (52, 245), (50, 262), (60, 270),
                       (75, 270), (75, 140)), "tree row along the right cart path"),
    Z("recovery", ell(50, 263, 5, 5)),
], note="Long par 5: the fairway runs right of a dormant-rough slope with single trees and a bunker (left), "
        "past two shrubby tall-grass ridges at 270-340 (native). The 2019-lidar crowns at (-45..-10, 140-235) are "
        "mostly gone in 2023 (one big tree at (-14, 218) remains).", confidence="medium")

# ---------------------------------------------------------------- 18 (par 4, 418)
H["18"] = dict(zones=[
    Z("fairway", band([(145, -25), (190, -40), (230, -45), (260, -45), (290, -40), (320, -32), (345, -28)],
                      [(145, 2), (200, 2), (240, 2), (260, 4), (275, 15), (290, 25), (320, 30), (345, 32)])),
    Z("sand", ell(-11, 302, 4.5, 7)),
    Z("recovery", band([(140, 4), (170, 5), (190, 8), (210, 9), (230, 8), (250, 9), (262, 10), (270, 13), (280, 25), (290, 33), (300, 40),
                        (320, 55), (335, 62), (352, 65)], [(140, 75), (352, 75)]),
      "woods right of the cart path (lidar + CIR crown edge; 2nd pass: 3-5 yds out at 190-260, shadows excluded)"),
    Z("recovery", poly((-75, 140), (-48, 140), (-45, 160), (-48, 180), (-55, 195), (-60, 215), (-58, 228), (-75, 230))),
    Z("recovery", ell(-46, 240, 7, 8)),
    Z("recovery", ell(-38, 324, 10, 13), "2nd pass: moved onto the lidar / CIR crown"),
    Z("recovery", ell(-52, 278, 3, 3)),
    Z("recovery", ell(-51, 291, 3, 3)),
], note="Wide fairway with woods tight on the right (the cart path runs along the tree line), tree groups left. "
        "Crown edges from lidar + CIR agree to ~2 yds.", confidence="high")

TRACE = dict(holes=H, missing=[])
