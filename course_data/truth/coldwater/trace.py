"""Coldwater Golf Links (Ames, IA), Blue tees: hand trace of the landing corridors (course_data/truth/corridor.py).

Coordinates: (x = yds right of the tee line, along = yds from the tee) in each hole's corridor frame
(render/frames.json). Order = precedence (later wins); unzoned = rough. Links-style course on open farmland:
fescue / prairie long grass (tan and tufted across NAIP years, pale grey in CIR), ponds, few trees.
"""
from corridor import Z, band, ell, poly, rect  # noqa: F401

H = {}

# ---------------------------------------------------------------- 1 (par 4, 307)
H["1"] = dict(zones=[
    Z("native", poly((-48, 228), (-40, 222), (-30, 222), (-28, 240), (-26, 260), (-25, 280), (-28, 300), (-35, 310),
                     (-45, 300), (-48, 270)), "tufted fescue between the cart path and the fairway (tan 2019-2023)"),
    Z("native", poly((-38, 205), (-25, 203), (-10, 210), (-6, 228), (-10, 248), (-25, 250), (-37, 240)),
      "fescue halo around the left fairway bunker"),
    Z("fairway", band([(145, -27), (180, -26), (205, -24), (215, -8), (250, -8), (260, -22), (280, -22), (300, -25), (318, -20)],
                      [(145, 9), (170, 14), (190, 21), (210, 30), (230, 37), (250, 40), (280, 40), (318, 40)])),
    Z("fairway", ell(2, 300, 13, 13), "green"),
    Z("sand", ell(-19, 231, 6, 9)),
    Z("sand", ell(-3, 262, 3.5, 6)),
    Z("sand", ell(28.5, 255, 4.5, 6)),
    Z("sand", poly((20, 295), (26, 290), (31, 300), (32, 312), (26, 316), (22, 305))),
    Z("water", band([(140, 11), (160, 14), (175, 18), (190, 24), (200, 29), (210, 33), (230, 40), (250, 43), (300, 43),
                     (330, 43), (352, 43)], [(140, 75), (352, 75)]), "lake (edge checked on NIR profiles)"),
    Z("ob", poly((-75, 140), (-35, 140), (-34, 180), (-35, 215), (-40, 225), (-75, 225)),
      "condominium buildings and yards left (property line at the hedge / tree row)"),
], note="Short par 4 along a lake (right). Fairway is wide and continuous; the left side between the cart path "
        "and the fairway has tan, tufted fescue in 2019-2023 (green in 2014-2017: it was let grow after ~2018). "
        "Condos left of the cart path to 220 = OB.", confidence="medium (fescue vs dormant mown rough)")

# ---------------------------------------------------------------- 2 (par 4, 425)
H["2"] = dict(zones=[
    Z("native", band([(140, -52), (200, -50), (250, -40), (270, -39), (300, -37), (340, -33), (352, -31)],
                     [(140, -31), (200, -28), (220, -26), (250, -19), (270, -16), (300, -13), (340, -10), (352, -9)]),
      "prairie strip between the two cart paths: tan in 2014, 2015, 2021, 2023"),
    Z("fairway", band([(145, -17), (200, -16), (240, -12), (260, -4), (300, 0), (345, 3)],
                      [(145, 17), (200, 18), (240, 20), (260, 25), (300, 28), (345, 28)])),
    Z("recovery", band([(140, 32), (180, 30), (200, 33), (220, 27), (240, 30), (260, 34), (280, 38), (300, 42), (320, 40),
                        (340, 33), (352, 33)], [(140, 75), (352, 75)]), "woods right: lidar crown edge (RGB shadows reach +22)"),
    Z("sand", ell(-56, 205, 4, 8)),
], note="Straight par 4 with woods right. Left: a permanent prairie strip between two cart paths (x -50..-30 "
        "at 150, -34..-8 at 300); beyond it another hole's fairway.", confidence="high")

# ---------------------------------------------------------------- 3 (par 5, 510)
H["3"] = dict(zones=[
    Z("fairway", band([(150, -15), (170, -20), (200, -28), (240, -33), (250, -30), (260, -22), (275, -20), (285, -30),
                       (300, -38), (320, -45), (345, -50)],
                      [(150, 18), (170, 20), (200, 24), (230, 28), (245, 30), (260, 45), (270, 65), (345, 65)])),
    Z("native", poly((23, 140), (75, 140), (75, 262), (60, 266), (45, 262), (38, 256), (34, 248), (32, 230), (27, 200),
                     (24, 170)), "wetland / prairie: coarse texture in every year, standing water in 2015"),
    Z("native", poly((-8, 322), (-3, 330), (4, 326), (16, 290), (13, 282), (6, 284)), "fescue island in the fairway"),
    Z("native", poly((54, 320), (62, 315), (68, 330), (65, 348), (57, 345))),
    Z("sand", poly((-36, 248), (-28, 250), (-27, 262), (-32, 266), (-36, 258))),
], note="Par 5 doglegging slightly left. A prairie / wetland area occupies the right of the corridor to 260 "
        "(x > +22): unmown in every NAIP year (standing water in 2015) - long grass. Fescue islands at 285-330. "
        "Two cart paths left; another hole beyond.", confidence="medium-high")

# ---------------------------------------------------------------- 4 (par 4, 371; dogleg left)
H["4"] = dict(zones=[
    Z("fairway", band([(150, -15), (200, -15), (240, -14), (250, -25), (260, -42), (300, -46), (345, -46)],
                      [(150, 20), (180, 22), (200, 26), (240, 28), (250, 15), (270, 8), (300, 3), (320, -2), (345, -15)])),
    Z("native", poly((2, 352), (4, 330), (10, 310), (20, 295), (32, 285), (42, 278), (48, 285), (46, 300), (50, 320),
                     (56, 352)), "prairie in the elbow of the dogleg: unmown in every year"),
    Z("native", ell(-18, 232, 5, 9), "fescue mound"),
    Z("native", ell(40, 221, 7, 26), "fescue island"),
    Z("native", poly((20, 140), (25, 160), (35, 172), (48, 175), (60, 168), (65, 155), (65, 140))),
    Z("recovery", band([(140, -43), (200, -42), (245, -40)], [(140, -37), (200, -36), (245, -35)]),
      "shrub / small-tree row between the cart path and the mobile-home park (lidar 0.5-4 m)"),
    Z("ob", poly((-75, 140), (-42, 140), (-40, 200), (-37, 245), (-45, 260), (-60, 280), (-70, 300), (-75, 300)),
      "mobile-home park left (property line at the shrub row)"),
], note="Dogleg left around the cart path; mobile-home park left = OB (behind a shrub row). Fescue islands and "
        "a prairie in the elbow (right, 280-350): long grass. Fairway edges are soft (mown rough the same colour "
        "in 2023): +/-4 yds.", confidence="medium")

# ---------------------------------------------------------------- 6 (par 4, 418)
H["6"] = dict(zones=[
    Z("fairway", band([(145, -24), (200, -25), (250, -25), (300, -25), (345, -24)],
                      [(145, 3), (180, 5), (200, 5), (240, 8), (250, 22), (300, 25), (345, 25)])),
    Z("native", poly((8, 140), (6, 160), (10, 172), (20, 178), (35, 178), (45, 170), (46, 150), (45, 140)),
      "unmown patch right of the tee line (coarse texture, tan in 2021 and 2023)"),
    Z("native", poly((34, 296), (36, 320), (37, 345), (47, 345), (46, 320), (44, 298)), "unmown strip along the right cart path"),
    Z("recovery", poly((36, 270), (45, 268), (52, 275), (52, 290), (44, 296), (37, 292)), "shrub thicket"),
    Z("sand", ell(-6, 262, 4.5, 4.5)),
    Z("ob", poly((-75, 250), (-55, 250), (-52, 280), (-50, 352), (-75, 352)), "mobile-home park left (road edge)"),
], note="Straight par 4 between two cart paths. Right of the tee line at 180-250 the turf is dry and tan but "
        "smooth (mown rough, also lighter in 2021); unmown patches at 145-178 and along the right cart path from "
        "296. Mobile-home park left of its road from 250 = OB.", confidence="medium")

# ---------------------------------------------------------------- 7 (par 5, 505)
H["7"] = dict(zones=[
    Z("fairway", band([(145, -28), (200, -28), (250, -30), (265, -15), (300, -12), (345, -12)],
                      [(145, 4), (200, 3), (250, 4), (265, 5), (280, 14), (300, 20), (330, 22), (345, 20)])),
    Z("native", poly((14, 140), (12, 160), (15, 178), (25, 182), (32, 175), (32, 150), (28, 140)),
      "unmown patch right of the cart path"),
    Z("native", poly((24, 300), (28, 285), (35, 272), (45, 268), (60, 268), (70, 275), (75, 280), (75, 335), (60, 333),
                     (40, 330), (28, 320)), "prairie right (coarse, tan in 2021, unmown every year)"),
    Z("recovery", band([(140, -75), (352, -75)], [(140, -40), (200, -38), (230, -40), (250, -43), (280, -45), (300, -46),
                                                  (320, -44), (335, -40), (352, -35)]),
      "tree belt left (lidar crown edge); mobile-home park behind it"),
    Z("ob", poly((-75, 140), (-62, 140), (-60, 250), (-62, 352), (-75, 352)), "mobile-home park behind the tree belt"),
], note="Long par 5; tree belt left with a mobile-home park behind it (OB), prairie / unmown patches right of the "
        "cart path. The grass hollow at 270-310 left (sand in 2021, grassed in 2023) is mapped as rough.",
                confidence="medium-high")

# ---------------------------------------------------------------- 9 (par 4, 371; lake right and across)
H["9"] = dict(zones=[
    Z("fairway", band([(145, -42), (200, -45), (230, -48), (250, -50), (280, -45), (295, -40)],
                      [(145, 14), (180, 15), (200, 18), (230, 25), (250, 25), (270, 10), (285, -10), (295, -30)])),
    Z("native", poly((15, 140), (18, 170), (22, 190), (30, 210), (40, 225), (52, 240), (62, 250), (75, 244), (75, 140)),
      "unmown bank between the fairway and the lake (pale, speckled in CIR; tan 2021)"),
    Z("native", poly((66, 241), (40, 255), (20, 268), (0, 281), (-20, 293), (-35, 300), (-35, 306), (-20, 300),
                     (0, 290), (20, 276), (40, 263), (66, 250)), "unmown lip along the lake bank (5-8 yds)"),
    Z("recovery", band([(140, -52), (200, -55), (230, -62)], [(140, -40), (200, -45), (230, -55)]),
      "shrub row along the left cart path (lidar 0.5-2.5 m)"),
    Z("sand", ell(-41, 237, 7, 6)),
    Z("sand", ell(-27, 283, 3, 4)),
    Z("water", poly((28, 140), (32, 160), (38, 180), (46, 200), (58, 220), (66, 232), (75, 238), (75, 140)), "lake (right)"),
    Z("water", poly((-75, 310), (-60, 310), (-35, 305), (-20, 300), (0, 290), (20, 276), (40, 263), (55, 256), (75, 246),
                    (75, 300), (60, 303), (40, 310), (20, 318), (0, 326), (-20, 335), (-40, 345), (-55, 352), (-75, 352)),
      "lake arm crossing the line of play (lidar no-return area)"),
], note="The lake runs up the right and then crosses the line of play diagonally (from 245 at the right edge to "
        "310 at the left), with an unmown lip along the bank. The far bank beyond the arm is another hole.",
                confidence="medium-high")

# ---------------------------------------------------------------- 10 (par 4, 396)
H["10"] = dict(zones=[
    Z("fairway", band([(145, -38), (200, -38), (240, -35), (260, -30), (290, -15), (320, -12), (345, -12)],
                      [(145, 0), (200, 2), (230, 3), (260, 5), (290, 2), (320, 0), (345, 0)])),
    Z("native", poly((12, 140), (12, 170), (15, 190), (21, 200), (22, 230), (20, 250), (10, 262), (7, 290), (6, 320),
                     (6, 352), (75, 352), (75, 140)), "prairie right of the fairway (tan in 2021, coarse / pale in CIR 2023)"),
    Z("native", band([(140, -68), (352, -68)], [(140, -50), (352, -50)]), "unmown strip with a shrub line left of the cart path"),
    Z("recovery", ell(24, 320, 6, 5)),
    Z("recovery", ell(36, 318, 4, 4)),
    Z("recovery", ell(30, 332, 5, 5)),
    Z("recovery", ell(48, 311, 3, 3)),
    Z("sand", ell(-27, 268, 7, 4)),
], note="Prairie hole: the whole right side of the corridor is unmown long grass (a few trees in it at 310-335), "
        "behind a 4-6 yd strip of mown rough from 260 (2nd pass); "
        "left of the cart path an unmown strip with a shrub line. Fairway edge to the prairie +/-3 yds.",
                confidence="medium-high")

# ---------------------------------------------------------------- 12 (par 4, 328)
H["12"] = dict(zones=[
    Z("fairway", band([(145, -25), (200, -27), (240, -28), (270, -24), (300, -20), (330, -18)],
                      [(145, 16), (170, 14), (190, 12), (210, 10), (230, 13), (250, 17), (270, 22), (290, 24), (310, 22),
                       (330, 15)])),
    Z("fairway", ell(5, 325, 12, 15), "green"),
    Z("native", band([(140, 75), (352, 75)], [(140, 22), (170, 24), (190, 28), (210, 34), (240, 40), (270, 44), (300, 47),
                                              (330, 50), (352, 52)]), "unmown grass and shrubs beyond the creek"),
    Z("water", band([(140, 18), (160, 19), (180, 21), (200, 26), (220, 32), (240, 37), (260, 40), (280, 43), (300, 45),
                     (330, 48), (352, 50)],
                    [(140, 27), (160, 27), (180, 29), (200, 33), (220, 39), (240, 43), (260, 46), (280, 48), (300, 50),
                     (330, 53), (352, 55)]), "stone-lined drainage creek (grey rock in NAIP, shrubs along it)"),
    Z("native", band([(140, -60), (352, -60)], [(140, -48), (200, -47), (250, -45), (300, -44), (352, -42)]),
      "unmown strip left of the left cart path"),
    Z("sand", ell(4, 310, 3, 4)),
    Z("sand", ell(9, 307, 4, 4)),
], note="Short par 4; a stone-lined drainage creek with shrubs runs down the right (x +18..+55), unmown grass and "
        "shrubs beyond it, an unmown strip left of the left cart path. The creek is mapped as water (penalty area; "
        "the inner edge is the rock line, +/-3 yds). The lidar no-return patch right of the creek at 150-200 is tall "
        "wet grass in the photo, not open water.", confidence="medium")

# ---------------------------------------------------------------- 13 (par 4, 413)
H["13"] = dict(zones=[
    Z("fairway", band([(145, -18), (200, -20), (250, -24), (290, -22), (310, -18), (345, -15)],
                      [(145, 18), (200, 20), (240, 18), (260, 14), (290, 15), (320, 18), (345, 20)])),
    Z("native", band([(140, -58), (180, -50), (220, -45), (260, -42), (300, -40), (330, -40), (352, -42)],
                     [(140, -40), (180, -32), (220, -27), (250, -24), (270, -27), (300, -28), (320, -25), (340, -22),
                      (352, -20)]), "fescue / prairie band left (tufted, tan in 2021, dark speckled in CIR)"),
    Z("native", band([(140, -75), (260, -75), (300, -75), (352, -75)], [(140, -62), (200, -60), (260, -58), (300, -50),
                                                                       (330, -45), (352, -45)])),
    Z("native", poly((36, 150), (32, 170), (31, 190), (35, 200), (45, 200), (49, 185), (49, 160), (44, 148)),
      "unmown oval between the two cart paths"),
    Z("native", poly((36, 290), (35, 310), (37, 330), (45, 330), (46, 310), (45, 290)), "unmown strip between the cart paths"),
    Z("sand", poly((18, 250), (22, 241), (28, 237), (33, 240), (31, 247), (26, 251), (25, 258), (20, 259))),
    Z("sand", poly((-30, 280), (-24, 279), (-23, 290), (-27, 297), (-31, 292))),
], note="Fairway between a diagonal fescue band (left) and two cart paths (right) with unmown islands between "
        "them. Fairway edges are soft in 2023 (fairway and rough the same green): +/-4 yds.", confidence="medium")

# ---------------------------------------------------------------- 14 (par 5, 476)
H["14"] = dict(zones=[
    Z("fairway", band([(165, -18), (175, -26), (200, -27), (250, -27), (300, -26), (345, -26)],
                      [(165, 10), (175, 16), (200, 16), (250, 16), (300, 16), (345, 16)])),
    Z("native", band([(225, -38), (260, -36), (300, -36), (352, -35)], [(225, -33), (260, -30), (300, -29), (352, -29)]),
      "unmown strip along the tree line (pale in CIR)"),
    Z("native", poly((24, 175), (22, 205), (23, 240), (24, 270), (25, 300), (26, 340), (36, 340), (34, 300), (34, 270),
                     (32, 240), (33, 210), (32, 175)), "unmown strip between the two cart paths"),
    Z("recovery", band([(140, -75), (352, -75)], [(140, -38), (160, -37), (200, -38), (225, -36), (250, -32), (270, -36),
                                                  (300, -40), (330, -40), (352, -38)]),
      "woods left: lidar crown edge (CIR + lidar agree to ~2 yds)"),
    Z("sand", poly((38, 182), (43, 178), (47, 186), (47, 198), (42, 203), (37, 196))),
], note="Par 5 along a wood (left). Mown fairway is a wide oval from 165; between it and the woods a narrow "
        "unmown strip; right of the first cart path an unmown strip with a bunker at 180-200.",
                confidence="medium-high")

# ---------------------------------------------------------------- 15 (par 4, 417)
H["15"] = dict(zones=[
    Z("fairway", band([(178, -12), (185, -17), (200, -18), (230, -20), (250, -24), (280, -28), (310, -26), (345, -22)],
                      [(178, 0), (185, 6), (200, 9), (230, 11), (250, 13), (280, 13), (300, 12), (330, 8), (345, 5)])),
    Z("native", poly((5, 145), (6, 160), (12, 168), (24, 168), (30, 160), (28, 146)), "tufted fescue carry patch"),
    Z("native", poly((55, 300), (50, 320), (52, 345), (65, 352), (75, 352), (75, 300)), "fescue beyond the right cart path"),
    Z("recovery", band([(140, -75), (352, -75)], [(140, -22), (170, -22), (190, -23), (200, -26), (215, -25), (225, -30),
                                                  (240, -36), (260, -38), (290, -40), (310, -40), (330, -42), (352, -40)]),
      "woods left: lidar crown edge"),
], note="Woods left, wide dry rough right of the fairway (tan, but mower stripes visible: rough, not long "
        "grass - ambiguous, see NOTES). Fescue only as the tufted carry patch at 145-168 and beyond the right "
        "cart path at 300+.", confidence="medium")

# ---------------------------------------------------------------- 17 (par 4, 395)
H["17"] = dict(zones=[
    Z("native", poly((-75, 140), (-38, 140), (-35, 170), (-36, 200), (-38, 230), (-40, 250), (-42, 270), (-38, 290),
                     (-30, 300), (-20, 302), (-5, 305), (10, 305), (20, 308), (28, 310), (35, 305), (75, 300), (75, 340),
                     (40, 330), (20, 322), (5, 318), (-10, 318), (-30, 320), (-45, 330), (-55, 345), (-75, 352)),
      "fescue left of the ditch and the band crossing the line of play beyond the fairway end"),
    Z("native", poly((40, 140), (39, 180), (40, 220), (42, 250), (45, 270), (75, 270), (75, 140)),
      "fescue right of the cart path (tan, tufted)"),
    Z("fairway", band([(150, -18), (180, -22), (220, -24), (250, -25), (270, -24), (290, -20), (300, -12), (303, 0)],
                      [(150, 25), (180, 27), (220, 28), (250, 26), (270, 24), (290, 25), (300, 18), (303, 0)])),
    Z("water", band([(140, -37), (160, -36), (180, -35), (200, -36), (220, -39), (240, -42)],
                    [(140, -29), (160, -28), (180, -28), (200, -29), (220, -32), (240, -36)]),
      "wet ditch (lidar no returns 150-190, standing water dark in CIR)"),
    Z("sand", poly((-27, 192), (-20, 190), (-17, 200), (-19, 211), (-25, 213), (-28, 203))),
    Z("sand", poly((-17, 270), (-10, 268), (-6, 274), (-9, 281), (-16, 281))),
], note="Fairway ends at ~305 against a band of fescue that crosses the line of play (305-330); fescue left of a "
        "wet ditch and right of the cart path. Card 395: driver over the crossing fescue is a real carry decision.",
                confidence="medium-high")

# ---------------------------------------------------------------- 18 (par 4, 433)
H["18"] = dict(zones=[
    Z("fairway", band([(145, -12), (170, -15), (185, -18), (215, -20), (240, -25), (270, -32), (300, -33), (320, -30),
                       (345, -25)],
                      [(145, 20), (200, 22), (230, 20), (250, 16), (270, 12), (300, 8), (320, 4), (345, 0)])),
    Z("native", band([(140, -75), (352, -75)], [(140, -46), (200, -50), (250, -52), (300, -52), (352, -50)]),
      "fescue left (tufted, tan) incl. the shrubby ditch"),
    Z("water", band([(140, -55), (200, -57), (250, -56), (300, -56), (352, -55)],
                    [(140, -46), (200, -48), (250, -48), (300, -48), (352, -47)]),
      "ditch / drainage channel with shrubs left (dark linear feature in every NAIP year)"),
    Z("native", band([(140, 40), (200, 46), (250, 52), (300, 45), (330, 38), (352, 30)], [(140, 75), (352, 75)]),
      "shrubby ditch and fescue right of the cart path"),
    Z("sand", poly((-30, 192), (-25, 188), (-18, 191), (-17, 200), (-21, 207), (-22, 213), (-29, 213))),
    Z("sand", poly((13, 265), (16, 258), (22, 259), (24, 270), (22, 282), (14, 281))),
], note="Finishing hole between a shrubby drainage ditch (left, mapped as water: penalty area) with fescue "
        "beyond, and a cart path with a second shrubby ditch and fescue right. Mown dry rough (tan, smooth) between "
        "the fairway and both ditches.", confidence="medium")

TRACE = dict(holes=H, missing=[])
