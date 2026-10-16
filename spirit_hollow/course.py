"""Spirit Hollow GC: holes traced from the GPS app's Tee-view screenshots.

Coordinates are screenshot pixels in a 920 x 2000 frame (the same frame as
mozingo/). The tee and the 300/270/240 dots were found automatically from the
red markers. Holes 10 and 18 have the tee just off the bottom of the screen, so
it's placed by extending the dot line 270 yds back from the 270 dot.

Reading the imagery (winter, dormant grass):
  * fairway = mown green; rough = mown tan/green right next to it.
  * native = the wispy, yellow-tan long grass (creek banks, field edges).
  * trees are traced at the trunks, not the canopy. The imagery is shot at a
    slight angle, so tree lines lean and throw shadows over the fairway (left
    side of 14 and 18 especially); those shadows are treated as grass.
  * ob = houses, the highway on 5 and back yards.
Hole 3 wasn't provided. Holes 2 and 9 have two tees (back and forward).
"""
import os

import numpy as np

HOLES = {
    1: dict(
        par=4, image="hole01.png", length=419,
        tee=(470, 2622), dot270=(479, 1290),       # tee off-screen: 9 x the 30-yd dot spacing
        zones=[
            ("fairway", [(340, 1600), (600, 1600), (620, 1300), (600, 1150), (540, 1000), (470, 850),
                         (420, 700), (300, 700), (320, 900), (330, 1100), (330, 1400)]),
            ("native", [(100, 870), (190, 870), (260, 1000), (310, 1100), (348, 1200), (350, 1320),
                        (300, 1420), (240, 1350), (205, 1250), (170, 1150), (105, 1050)]),  # diagonal
                                                       # tan band left (found by vision.py QA)
            ("recovery", [(0, 1000), (150, 1000), (230, 1300), (265, 1700), (0, 1700)]),  # trees left
            ("recovery", [(470, 600), (560, 800), (660, 1000), (760, 1200), (830, 1400), (920, 1400),
                          (920, 540), (440, 540)]),  # tree line right, traced at the trunks: the
                                                     # photo is tilted so the canopy leans over the fairway
        ]),
    "2B": dict(
        par=5, image="hole02_b.png", length=616,
        tee=(476, 1925), dot270=(433, 895),
        zones=[
            ("fairway", [(300, 1150), (470, 1150), (500, 1000), (510, 850), (500, 700), (470, 540),
                         (340, 540), (330, 700), (310, 850), (300, 1000)]),
            ("recovery", [(0, 540), (110, 540), (200, 700), (300, 900), (380, 1050), (440, 1200),
                          (440, 1400), (0, 1400)]),                              # woods + creek left
            ("native", [(200, 640), (290, 640), (300, 1000), (360, 1080), (330, 1080), (260, 900)]),
            ("native", [(520, 640), (560, 640), (610, 800), (650, 950), (690, 1100), (700, 1200),
                        (640, 1200), (600, 1050), (560, 900), (530, 750)]),      # long grass right
        ]),
    "2F": dict(
        par=5, image="hole02_a.png", length=525,
        tee=(337, 1800), dot270=(374, 953),
        zones=[
            ("fairway", [(290, 1450), (440, 1450), (460, 1200), (470, 1000), (470, 850), (440, 700),
                         (400, 620), (280, 620), (250, 800), (260, 1000), (280, 1200)]),
            ("recovery", [(0, 540), (60, 540), (200, 800), (250, 1000), (280, 1200), (300, 1450),
                          (0, 1450)]),                                           # trees left
            ("water", [(0, 700), (140, 700), (185, 780), (215, 850), (235, 950), (245, 1050), (255, 1150),
                       (270, 1300), (200, 1300), (130, 1100), (40, 900), (0, 850)]),  # creek left, to the
                                                       # rough edge (found by vision.py QA)
            ("native", [(460, 880), (495, 880), (515, 1000), (535, 1450), (470, 1450), (468, 1200)]),
            ("recovery", [(495, 850), (920, 850), (920, 1450), (540, 1450), (520, 1100), (505, 950)]),
            ("ob", [(400, 540), (920, 540), (920, 850), (495, 850), (470, 700)]),  # houses right
            ("sand", [(395, 800), (450, 800), (450, 860), (400, 860)]),          # right, ~300 out
            ("sand", [(280, 670), (330, 670), (330, 720), (285, 720)]),          # left, ~350 out
        ]),
    4: dict(
        par=5, image="hole04.png", length=520,
        tee=(508, 1907), dot270=(435, 1188),
        zones=[
            ("fairway", [(380, 860), (462, 860), (468, 1000), (472, 1300), (480, 1500), (385, 1500),
                         (375, 1300), (372, 1000)]),             # re-traced at full zoom: ~37 yds wide
            ("recovery", [(0, 540), (300, 540), (260, 800), (215, 1000), (205, 1300), (240, 1600),
                          (0, 1600)]),                                           # woods left
            ("native", [(225, 800), (378, 800), (370, 1000), (373, 1300), (383, 1500), (240, 1500),
                        (215, 1300), (215, 1000)]),                              # long grass left
            ("native", [(463, 860), (585, 860), (590, 1500), (481, 1500), (473, 1300), (469, 1000)]),
            ("recovery", [(585, 540), (625, 540), (630, 1600), (590, 1600)]),   # tree line right
            ("ob", [(625, 540), (920, 540), (920, 1600), (630, 1600)]),         # houses right
            ("sand", [(330, 860), (372, 860), (372, 925), (330, 925)]),
        ]),
    5: dict(
        par=4, image="hole05.png", length=397,
        tee=(511, 1930), dot270=(470, 994),
        zones=[
            ("fairway", [(350, 1450), (560, 1450), (560, 1100), (570, 950), (575, 700), (320, 700),
                         (330, 900), (360, 1100)]),
            ("native", [(225, 540), (310, 540), (315, 800), (325, 1100), (330, 1450), (270, 1450),
                        (240, 1100), (225, 800)]),                               # long grass left
            ("ob", [(0, 540), (215, 540), (220, 1100), (250, 1450), (0, 1450)]),  # highway
            ("recovery", [(580, 540), (645, 540), (650, 1450), (600, 1450), (590, 1100)]),
            ("ob", [(650, 540), (920, 540), (920, 1450), (655, 1450)]),          # houses right
            ("sand", [(490, 835), (535, 835), (535, 880), (492, 882)]),          # right, ~300 out
            ("sand", [(560, 950), (615, 950), (615, 992), (562, 992)]),          # right, ~275 out
            ("sand", [(335, 1140), (395, 1140), (400, 1260), (340, 1260)]),      # left cluster ~200
            ("sand", [(400, 1255), (455, 1255), (455, 1320), (405, 1320)]),
        ]),
    6: dict(
        par=4, image="hole06.png", length=421,
        tee=(598, 1852), dot270=(413, 900),
        zones=[
            ("fairway", [(270, 700), (430, 690), (470, 800), (500, 900), (540, 1000), (600, 1100),
                         (640, 1250), (560, 1300), (450, 1300), (390, 1150), (340, 1000), (300, 900),
                         (270, 800)]),
            ("recovery", [(100, 800), (200, 800), (260, 950), (330, 1150), (370, 1300), (250, 1300),
                          (180, 1100), (120, 950)]),                             # tree row left
            ("native", [(200, 800), (260, 800), (300, 900), (340, 1000), (390, 1150), (440, 1300),
                        (370, 1300), (330, 1150), (270, 1000), (220, 900)]),
            ("native", [(470, 690), (510, 690), (560, 800), (600, 900), (640, 1000), (690, 1100),
                        (640, 1100), (590, 1000), (540, 900), (500, 800)]),      # long grass right
            ("water", [(0, 560), (70, 560), (70, 720), (0, 720)]),               # pond far left
        ]),
    8: dict(
        par=4, image="hole08.png", length=375,
        tee=(538, 1886), dot270=(431, 886),
        zones=[
            ("fairway", [(330, 1300), (560, 1300), (620, 1150), (610, 1000), (560, 900), (530, 780),
                         (500, 650), (470, 540), (320, 540), (335, 700), (345, 900), (340, 1100)]),
            ("native", [(200, 540), (300, 540), (330, 700), (340, 900), (330, 1075), (285, 1075),
                        (250, 900), (220, 700)]),                                # long grass left
            ("ob", [(465, 540), (920, 540), (920, 960), (668, 960), (585, 800), (520, 650)]),  # houses
            ("water", [(720, 1000), (920, 1000), (920, 1300), (730, 1300), (700, 1150)]),
            ("sand", [(445, 805), (520, 805), (520, 875), (447, 875)]),
            ("sand", [(565, 1000), (625, 1000), (630, 1095), (570, 1095)]),
            ("sand", [(395, 1140), (445, 1140), (445, 1205), (395, 1205)]),
        ]),
    "9B": dict(
        par=4, image="hole09_back.png", length=399,
        tee=(386, 1861), dot270=(421, 869),
        zones=[
            ("fairway", [(250, 1300), (420, 1300), (428, 1100), (430, 960), (500, 915), (560, 880),
                         (560, 760), (470, 700), (300, 620), (260, 700), (240, 900), (230, 1100)]),
            ("native", [(0, 900), (220, 900), (210, 1100), (200, 1350), (0, 1350)]),
            ("water", [(430, 960), (500, 920), (620, 950), (650, 1000), (660, 1100), (640, 1180),
                       (600, 1300), (560, 1360), (500, 1340), (450, 1250), (430, 1150),
                       (425, 1050)]),                                            # pond right
            ("water", [(540, 690), (600, 690), (700, 620), (720, 560), (690, 560), (660, 620),
                       (580, 670), (540, 680)]),                                 # creek long-right
            ("ob", [(650, 1150), (920, 1150), (920, 1400), (650, 1400)]),        # houses
            ("recovery", [(475, 790), (555, 780), (560, 860), (500, 870), (470, 840)]),  # trees right ~300
            ("water", [(560, 690), (585, 690), (605, 740), (625, 790), (650, 840), (670, 880), (650, 890),
                       (625, 850), (600, 800), (580, 750), (560, 710)]),          # creek right of the fairway
        ]),
    "9F": dict(
        par=4, image="hole09_forward.png", length=373,
        tee=(220, 1689), dot270=(485, 857),
        zones=[
            ("fairway", [(260, 1200), (360, 1200), (420, 1050), (450, 990), (530, 900), (560, 820),
                         (560, 720), (500, 700), (400, 700), (330, 760), (300, 900), (280, 1050)]),
            ("water", [(455, 1000), (500, 990), (570, 1010), (575, 1100), (560, 1230), (480, 1240),
                       (450, 1150), (450, 1050)]),                               # pond right
            ("native", [(380, 620), (620, 620), (640, 700), (560, 712), (480, 705), (380, 705)]),
            ("recovery", [(200, 540), (920, 540), (920, 615), (200, 615)]),     # trees behind green
            ("water", [(670, 630), (750, 630), (745, 780), (680, 780)]),         # creek right
            ("recovery", [(560, 800), (600, 790), (620, 840), (600, 890), (560, 890)]),  # trees right ~300
            ("water", [(600, 760), (620, 760), (635, 800), (650, 840), (670, 880), (650, 890), (628, 850),
                       (612, 810), (598, 780)]),                                  # creek right of the fairway
        ]),
    10: dict(
        par=5, image="hole10.png", length=521,
        tee=(599, 2021), dot270=(532, 984),
        zones=[
            ("fairway", [(400, 540), (480, 540), (560, 800), (600, 900), (640, 1000), (680, 1100),
                         (700, 1250), (560, 1450), (460, 1450), (420, 1250), (405, 1000),
                         (400, 800)]),
            ("recovery", [(150, 540), (390, 540), (395, 800), (400, 1000), (410, 1200), (440, 1450),
                          (150, 1450)]),                                         # woods left
            ("water", [(372, 800), (392, 800), (398, 1100), (420, 1450), (400, 1450),
                       (378, 1100)]),                                            # creek in the woods
            ("water", [(600, 770), (640, 760), (700, 800), (760, 880), (810, 980), (830, 1060),
                       (800, 1110), (740, 1090), (690, 1000), (650, 920), (610, 850)]),  # pond right
            ("sand", [(648, 1135), (692, 1135), (695, 1190), (650, 1190)]),
        ]),
    11: dict(
        par=4, image="hole11.png", length=348, irons=True,
        tee=(468, 1841), dot270=(479, 752),
        zones=[
            ("fairway", [(420, 1300), (560, 1300), (590, 1000), (590, 700), (575, 540), (360, 540),
                         (340, 700), (330, 850), (400, 950), (430, 1100)]),
            ("recovery", [(0, 540), (305, 540), (310, 950), (330, 1300), (0, 1300)]),   # woods left
            ("native", [(290, 950), (400, 950), (430, 1100), (440, 1260), (320, 1260), (300, 1100)]),
            ("recovery", [(592, 540), (720, 540), (720, 1300), (600, 1300), (596, 1000)]),  # woods R
            ("water", [(100, 630), (300, 652), (600, 662), (600, 692), (300, 688), (100, 668)]),
        ]),                                                                      # creek ~286-292 out
    13: dict(
        par=4, image="hole13.png", length=407,
        tee=(479, 1614), dot270=(434, 923),
        zones=[
            ("fairway", [(330, 1300), (460, 1300), (465, 1100), (462, 960), (480, 860), (560, 820),
                         (560, 640), (420, 560), (350, 640), (330, 800), (320, 1000)]),
            ("recovery", [(0, 540), (305, 540), (310, 800), (300, 1000), (305, 1300), (0, 1300)]),
            ("water", [(480, 880), (530, 868), (548, 900), (550, 1050), (540, 1150), (510, 1168),
                       (485, 1120), (475, 1000), (476, 920)]),                   # pond right
            ("sand", [(365, 848), (395, 848), (397, 890), (372, 892)]),         # two pot bunkers left
        ]),
    14: dict(
        par=4, image="hole14.png", length=418,
        tee=(443, 1898), dot270=(443, 943),
        zones=[
            # retraced from the clean photo: the left trees reach the line short of the landing
            # (~25 yds left of it at 270 out, nearly on it at 225); the fairway runs up the left
            # between the tree line and the creek's long-grass bank
            ("fairway", [(170, 600), (385, 600), (420, 675), (455, 725), (520, 800), (545, 850),
                         (560, 900), (580, 950), (600, 1000), (610, 1050), (620, 1100), (600, 1150),
                         (470, 1150), (445, 1100), (400, 1000), (360, 950), (320, 900), (290, 860),
                         (250, 800), (200, 725), (170, 650)]),
            ("recovery", [(0, 540), (160, 540), (170, 650), (200, 725), (250, 800), (290, 860),
                          (320, 900), (360, 950), (400, 1000), (445, 1100), (470, 1150), (400, 1250),
                          (350, 1300), (0, 1300)]),                              # woods left
            ("native", [(380, 560), (560, 540), (620, 700), (700, 900), (760, 1000), (860, 1150),
                        (920, 1250), (920, 1330), (820, 1250), (700, 1100), (620, 1090), (610, 1050),
                        (600, 1000), (580, 950), (560, 900), (545, 850), (520, 800), (480, 750),
                        (455, 725), (420, 675), (390, 620)]),                    # creek banks
            ("water", [(520, 640), (545, 640), (600, 800), (660, 920), (740, 1040), (860, 1170),
                       (920, 1220), (920, 1260), (850, 1210), (720, 1070), (640, 950), (580, 830),
                       (525, 700)]),                                             # creek right
        ]),
    16: dict(
        par=4, image="hole16.png", length=388,
        tee=(415, 1953), dot270=(421, 1017),
        zones=[
            ("fairway", [(300, 1300), (480, 1300), (490, 1100), (490, 950), (470, 850), (470, 700),
                         (310, 700), (300, 900), (295, 1100)]),
            ("recovery", [(0, 540), (285, 540), (285, 900), (0, 900)]),          # woods left
            ("native", [(0, 900), (285, 900), (290, 1300), (0, 1300)]),          # field left
            ("recovery", [(495, 540), (700, 540), (700, 1300), (500, 1300), (495, 1100),
                          (500, 950)]),                                          # woods right
            ("recovery", [(470, 760), (560, 760), (560, 900), (495, 920), (470, 880)]),  # trees R ~300
            ("water", [(505, 1100), (530, 1100), (530, 1260), (505, 1260)]),     # creek in woods R
            ("sand", [(435, 830), (470, 830), (470, 860), (435, 860)]),
            ("sand", [(455, 875), (495, 875), (495, 920), (458, 920)]),
            ("sand", [(298, 1030), (345, 1030), (345, 1100), (300, 1100)]),
        ]),
    17: dict(
        par=4, image="hole17.png", length=453,
        tee=(322, 1801), dot270=(403, 1024),
        zones=[
            ("fairway", [(255, 1300), (440, 1300), (470, 1100), (500, 950), (540, 800), (580, 600),
                         (420, 560), (380, 700), (330, 900), (280, 1100)]),
            ("recovery", [(450, 1300), (470, 1150), (510, 950), (560, 800), (610, 560), (920, 560),
                          (920, 1300)]),                                         # woods right
            ("native", [(0, 560), (370, 560), (330, 700), (270, 900), (230, 1050), (170, 1300),
                        (0, 1300)]),                                             # field left
            ("sand", [(400, 815), (430, 815), (430, 860), (400, 860)]),          # ~335 on the line
        ]),
    18: dict(
        par=5, image="hole18.png", length=516,
        tee=(419, 2033), dot270=(392, 1083),
        zones=[
            ("fairway", [(180, 1450), (270, 1450), (330, 1300), (390, 1170), (440, 1050), (500, 900),
                         (560, 780), (620, 640), (650, 560), (380, 560), (345, 700), (320, 800),
                         (295, 900), (285, 1000), (250, 1100), (215, 1200), (185, 1300)]),  # left of creek
            ("fairway", [(480, 1450), (560, 1450), (600, 1200), (650, 1050), (720, 900), (800, 700),
                         (700, 700), (640, 850), (570, 1000), (520, 1150)]),     # right of the creek
            ("recovery", [(0, 540), (390, 540), (300, 750), (200, 950), (140, 1100), (95, 1300),
                          (65, 1450), (0, 1450)]),                               # woods left, to the black line
            ("native", [(390, 540), (380, 560), (345, 700), (320, 800), (295, 900), (285, 1000), (250, 1100),
                        (215, 1200), (185, 1300), (180, 1450), (65, 1450), (95, 1300), (140, 1100),
                        (200, 950), (300, 750)]),                                # tan strip inside the woods
            ("native", [(270, 1450), (480, 1450), (520, 1150), (570, 1000), (640, 850), (700, 700),
                        (760, 560), (650, 560), (620, 640), (560, 780), (500, 900), (440, 1050),
                        (390, 1170), (330, 1300)]),                              # creek banks
            ("water", [(370, 1450), (400, 1450), (460, 1250), (520, 1100), (590, 950), (650, 820),
                       (720, 600), (700, 600), (630, 800), (570, 930), (500, 1080), (440, 1230)]),
            ("sand", [(590, 1270), (640, 1270), (640, 1350), (590, 1350)]),
        ]),
}

HOLES[13]["irons"] = True

# Corrections from the independent full-zoom map audit (spirit_hollow/output/audit_findings.txt).
# Appended zones override earlier ones; "rough" patches undo hazards that were drawn too big.
def _line_poly(pts, half):
    """A strip of +/-half px around a polyline (creek beds)."""
    left = [(x - half, y) for x, y in pts]
    right = [(x + half, y) for x, y in pts][::-1]
    return left + right


AUDIT_FIXES = {
    4: [("rough", [(468, 860), (505, 860), (508, 1150), (525, 1250), (528, 1500), (475, 1500),
                   (470, 1300), (467, 1000)]),                 # 9-15 yds of rough before the tan, right
        ("rough", [(335, 860), (372, 860), (370, 1000), (373, 1300), (383, 1500), (345, 1500),
                   (335, 1300), (330, 1000)])],                # ...and left
    5: [("sand", [(478, 843), (549, 843), (549, 925), (478, 925)])],   # right bunker ~2x the trace
    13: [("sand", [(377, 870), (395, 870), (395, 894), (377, 894)]),   # second pot bunker
         ("sand", [(358, 896), (382, 896), (382, 922), (358, 922)]),
         ("sand", [(402, 798), (418, 798), (418, 822), (402, 822)])],  # small third bunker ~314 out
    18: [("fairway", [(500, 900), (545, 900), (486, 1015), (456, 1109), (427, 1192), (385, 1192),
                      (421, 1109), (454, 1015)]),              # creek-bank grass starts 10-13 yds further right
         ("native", [(295, 850), (365, 850), (370, 920), (295, 920)])],  # leaf litter under the left trees
    "2F": [("water", [(235, 900), (262, 900), (268, 950), (285, 1000), (285, 1050), (275, 1100),
                      (255, 1150), (245, 1050), (235, 950)]),  # creek reaches ~-28 yds
           ("sand", [(420, 860), (450, 860), (450, 884), (420, 884)])],  # lower lobe of the bunker
    "2B": [("water", _line_poly([(205, 650), (240, 760), (290, 860), (310, 900), (330, 950),
                                 (345, 1000)], 7)),           # the creek was never mapped from this tee
           ("native", [(310, 880), (370, 890), (375, 960), (345, 1000), (322, 950)])],
    8: [("rough", [(245, 650), (325, 650), (330, 700), (340, 900), (333, 975), (330, 975), (310, 900),
                   (278, 800), (250, 700)]),                   # long grass ends 10-19 yds further left
        ("fairway", [(480, 805), (520, 805), (520, 835), (480, 835)])],  # L-shaped bunker: grass block
    "9F": [("rough", [(560, 790), (620, 790), (620, 890), (560, 890)]),  # trees were drawn on grass
           ("rough", [(598, 760), (670, 760), (670, 890), (598, 890)]),  # ...and so was the creek strip
           ("recovery", [(497, 896), (578, 896), (578, 972), (497, 972)]),  # the real tree clump
           ("water", _line_poly([(574, 809), (599, 873), (642, 893)], 6)),  # west creek
           ("water", _line_poly([(703, 796), (642, 893)], 6))],             # east creek
    6: [("rough", [(200, 800), (260, 800), (300, 900), (340, 1000), (270, 1000), (220, 900)]),
        ("native", [(140, 800), (190, 800), (198, 850), (255, 900), (263, 950), (270, 1000),
                    (185, 1000), (182, 950), (190, 900), (152, 850)]),  # left band sits further left
        ("rough", [(505, 690), (535, 800), (575, 900), (625, 1000), (675, 1100), (640, 1100), (590, 1000),
                   (540, 900), (500, 800), (470, 690)])],      # right band starts 30-40 px further right
    11: [("rough", [(290, 950), (400, 950), (430, 1100), (440, 1260), (320, 1260), (300, 1100)]),
         ("native", [(356, 1110), (430, 1110), (506, 1205), (506, 1220), (387, 1220), (356, 1125)])],
    17: [("rough", [(450, 1300), (470, 1150), (510, 950), (560, 800), (610, 560), (645, 560), (595, 800),
                    (545, 950), (505, 1150), (485, 1300)]),    # grass out to the black line before the woods
         ("sand", [(430, 815), (442, 815), (442, 860), (430, 860)])],
    16: [("sand", [(467, 882), (506, 882), (506, 933), (467, 933)])],
}
for _k, _extra in AUDIT_FIXES.items():
    HOLES[_k]["zones"] = HOLES[_k]["zones"] + _extra


# ---- Fairway width from OpenStreetMap -------------------------------------------------------
# Three independent checks (stats calibration: model ~75% fairways vs ~49% published for a
# 5-hcp; OSM geometry; the course-data spike) found the traced fairways include the first cut:
# 55-65 yds wide where the mown fairway in OSM (which sits on the stripes in the NAIP photo)
# is 25-40. At each 10 yds from 200-340 out we narrow the traced fairway to the OSM width at
# the same distance from the green (keeping the traced centre) and mark the trimmed edges
# "first_cut" (scored between fairway and rough in tee_strategy).
def _osm_widths():
    import json
    from matplotlib.path import Path as _P
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "course_data", "spirit_hollow",
                        "holes_osm.json")
    if not os.path.exists(path):
        return {}
    holes = json.load(open(path))["holes"]
    out = {}
    xs = np.arange(-80, 80.01, 0.5)
    for ref, hd in holes.items():
        polys = [_P(np.array(z[1])) for z in hd["zones"] if z[0] == "fairway"]
        gy = hd["green"][1]

        def width(dist_to_green, polys=polys, gy=gy):
            y = gy + dist_to_green
            inside = np.zeros_like(xs, bool)
            for p in polys:
                inside |= p.contains_points(np.c_[xs, np.full_like(xs, y)])
            best = cur = 0
            for v in inside:
                cur = cur + 1 if v else 0
                best = max(best, cur)
            return best * 0.5
        out[ref] = width
    return out


def _first_cut_bands(hd, width_at, alongs=range(200, 341, 10), min_width=18.0):
    from matplotlib.path import Path as _P
    tee, d = np.array(hd["tee"], float), np.array(hd["dot270"], float)
    ppy = np.linalg.norm(d - tee) / 270
    f = (d - tee) / np.linalg.norm(d - tee)
    r = np.array([-f[1], f[0]])
    lats = np.arange(-70, 70.01, 0.5)
    left, right = [], []
    for a in alongs:
        pts = tee + (a * f + lats[:, None] * r) * ppy
        lie = np.array(["rough"] * len(pts), dtype=object)
        for name, poly in hd["zones"]:
            lie[_P(poly).contains_points(pts)] = name
        fw = lie == "fairway"
        if not fw.any():
            continue
        runs, start = [], None                        # widest fairway run
        for i, v in enumerate(np.r_[fw, False]):
            if v and start is None:
                start = i
            elif not v and start is not None:
                runs.append((start, i - 1)); start = None
        i0, i1 = max(runs, key=lambda q: q[1] - q[0])
        l0, l1 = lats[i0], lats[i1]
        w = width_at(hd["length"] - a)
        if w < min_width or (l1 - l0) <= w:
            continue
        c = (l0 + l1) / 2
        left.append((a, l0, c - w / 2))
        right.append((a, c + w / 2, l1))

    def poly(rows):
        if len(rows) < 2:
            return None
        outer = [tuple(tee + (a * f + x0 * r) * ppy) for a, x0, _ in rows]
        inner = [tuple(tee + (a * f + x1 * r) * ppy) for a, _, x1 in rows][::-1]
        return outer + inner
    return [p for p in (poly(left), poly(right)) if p]


_W = _osm_widths()
FAIRWAY_WIDTH_SOURCE = "OSM" if _W else "traced"
for _k, _h in HOLES.items():
    _ref = str(_k if isinstance(_k, int) else int(_k[:-1]))
    if _ref not in _W:
        continue
    _bands = _first_cut_bands(_h, _W[_ref])
    if not _bands:
        continue
    _last_fw = max(i for i, (nm, _) in enumerate(_h["zones"]) if nm == "fairway")
    _h["zones"] = (_h["zones"][:_last_fw + 1] + [("first_cut", b) for b in _bands]
                   + _h["zones"][_last_fw + 1:])
                    # pond + bunker squeeze the landing zone

# The app's "Center" numbers: yds to the green centre from the 300 / 270 / 240 dots.
APP = {1: (119, 143, 168), "2B": (316, 339, 363), "2F": (225, 250, 276), 4: (221, 250, 280),
       5: (98, 127, 157), 6: (126, 151, 177), 8: (76, 105, 134), "9B": (115, 129, 148),
       "9F": (89, 103, 123), 10: (227, 251, 277), 11: (53, 78, 106), 13: (110, 137, 166),
       14: (123, 148, 175), 16: (88, 118, 148), 17: (153, 183, 212), 18: (222, 246, 271)}
# Which side of the tee line the green sits (the three numbers fix how far, not which side).
# From the green marker (1, 10), the hole outline (9, 18) or the app's dashed line;
# 11 is left on the line: its offset (~34) is within the app's 1-yd rounding at that range.
GREEN_SIDE = {1: -1, "2B": -1, "2F": -1, 4: 1, 5: -1, 6: -1, 8: -1, "9B": 1, "9F": 1, 10: -1,
              11: -1, 13: 1, 14: -1, 16: 0, 17: 1, 18: 1}
# Verified by projecting OSM's green into each screenshot through the imagery engineer's NAIP
# registration (course_data/imagery/traced_registration.json): 13 holes agreed within a few yards;
# 4 and 13 had the green on the wrong side and 11 is ~38 yds left (fixed here).


def green_from_app(d300, d270, d240, side):
    """Trilaterate the green from the three dot distances: (yds along the line, yds right)."""
    along = (d240 ** 2 - d300 ** 2 + 32400) / 120
    lat = np.sqrt(max(d270 ** 2 - (along - 270) ** 2, 0.0))
    return along, side * lat


for _k, _h in HOLES.items():
    _h.setdefault("aim_min", -40)
    _h.setdefault("aim_max", 40)
    _tee, _d = np.array(_h["tee"], float), np.array(_h["dot270"], float)
    _ppy = np.linalg.norm(_d - _tee) / 270
    _f = (_d - _tee) / np.linalg.norm(_d - _tee)
    _r = np.array([-_f[1], _f[0]])
    _a, _l = green_from_app(*APP[_k], GREEN_SIDE[_k])
    if GREEN_SIDE[_k] == 0:                  # straight hole: green on the line
        _a, _l = 270 + APP[_k][1], 0.0
    _h["green"] = tuple(_tee + (_a * _f + _l * _r) * _ppy)
    _h["length"] = 270 + APP[_k][1]          # same convention on every hole


def _par3(image, tee, center, green_px, haz, note, short):
    """Par 3 from pixels: flag = centroid of the traced green, scale from the app's centre number."""
    g = np.array(green_px, float)
    flag = g.mean(axis=0)
    tee_a = np.array(tee, float)
    v = flag - tee_a
    ppy = np.linalg.norm(v) / center
    fwd = v / np.linalg.norm(v)
    right = np.array([-fwd[1], fwd[0]])
    rel = g - flag
    yds = [(float(r @ right / ppy), float(r @ fwd / ppy)) for r in rel]
    on_line = sorted(d for l, d in yds if abs(l) < 6)
    return dict(image=image, tee=tuple(tee), flag=tuple(flag), center=center,
                front=round(center + min(d for _, d in yds)), back=round(center + max(d for _, d in yds)),
                green=yds, haz=haz, note=note, short=short)


PAR3 = {
    7: _par3("hole07.png", (449, 1828), 159,
             [(365, 748), (420, 742), (470, 752), (500, 775), (505, 815), (490, 850), (478, 890),
              (470, 925), (440, 940), (400, 942), (365, 930), (345, 900), (340, 860), (335, 820),
              (340, 780)],                    # re-traced on a contrast-boosted zoom: the smooth oval,
                                              # not the darker approach below it
             haz=dict(left="bunker", right="bunker", short="rough", long="native"),
             note="Bunkers both sides (the pair left, the C-shaped one right) and long grass over the "
                  "back. The front-right bunker is short-right, short of the green. Narrow, deep green.",
             short="Bunkers both sides, long grass behind."),
    12: _par3("hole12.png", (430, 1790), 177,
              [(390 + 60 * np.cos(a), 935 + 60 * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 24,
                                                                                    endpoint=False)],
              haz=dict(left="native", right="bunker", short="rough", long="rough"),
              note="Round green. Bunker tight right, long grass left beyond a few yards of rough. "
                   "Short is fairway, so the short miss is fine.",
              short="Bunker right, long grass left. Short is safe."),
    15: _par3("hole15.png", (395, 1672), 134,
              [(375, 1000), (390, 960), (430, 930), (470, 922), (520, 925), (545, 945), (540, 980),
               (515, 1015), (475, 1045), (440, 1052), (400, 1040), (380, 1020)],
              haz=dict(left="rough", right="native", short="water", long="bunker"),
              note="All carry over the pond, with a bunker short and two bunkers behind. The green is "
                   "deep enough for the full water cushion (10 yds) and the bunker cushion behind "
                   "(8 yds), so the box sits mid-green. Never short.",
              short="Pond short, sand behind. Never short."),
}

NOTES = {
    1: "Tree line down the right is traced at the trunks: the photo is tilted, so the canopy and "
       "shadows look like they're over the fairway. Tan long grass left at ~230-330. The green sits "
       "left of the line; driver by only 0.02 over the 2-wood.",
    "2B": "From the back tee it's ~616: the extra 20-30 yds of driver still matters (0.04). Woods and "
          "the creek left, long grass right of the cart path.",
    "2F": "Creek and trees left, houses (OB) and trees right. Small bunker ~5 yds right of the line "
          "at ~300 out, so aim left-centre. Driver by 0.08.",
    4: "Narrow: the fairway is only ~37 yds wide at 300 with tan long grass both sides, so ~29% of drives find it. Driver still edges it (0.03) because it's a par 5; 4-wood is the safe alternative on a bad driving day.",
    5: "Highway (OB) left, houses (OB) right. Bunkers right at ~275-300 catch ~9% of drives even "
       "aimed left. Driver and 2-wood are a tie (0.003); 4-wood ~0.02 behind.",
    6: "Long grass both sides, nothing penal. Driver for the shorter approach.",
    8: "Bunker 5-25 yds right of the line at ~270-290 out catches about a third of drives. The "
       "4-wood stops short of it. Houses (OB) right behind the black line.",
    "9B": "Creek and a tree clump just right of the fairway at ~280-320, pond right earlier. Coin flip: driver by 0.01 over 2-wood. Aim left-centre.",
    "9F": "2-wood and 4-wood tie (0.002); driver 0.04 behind. Pond right at ~150-200, creek and trees right at ~280-320.",
    10: "Pond right from ~237 to ~328, creek in the woods left. Aim a touch left; driver's extra "
        "20 yds is worth 0.06 on a par 5.",
    11: "Creek crosses the fairway at ~286-292. Driver carries 275 and rolls into it (3 in 4). "
        "4-wood stops ~270, short of it. 2-wood still reaches it 1 time in 6. Irons cost 0.14+.",
    13: "Pond right from ~173 to ~295, pot bunkers left at ~280-300. The 4-wood stops short of the "
        "pots; driver finds sand ~23%. Irons give up too much (0.2+).",
    14: "Creek with long-grass banks down the right. The trees on the left lean into the fairway "
        "because of the camera angle; they're modelled at the trunks.",
    16: "Three-way tie (0.01). Woods both sides, bunkers right at ~300 and left at ~255.",
    17: "Woods right, open field left. The fairway bunker is ~335 out, out of reach.",
    18: "Narrow corridor: tan long grass inside the woods line on the left and the creek bank on the right leave ~45 yds of fairway. ~24% of drives find long grass, but the 2-wood and 4-wood land in the same band, so driver still wins (0.05).",
}

AIM_AT = {
    1: "Centre of the fairway",
    "2B": "Centre of the fairway",
    "2F": "Left side of the fairway, away from the bunker on the right",
    4: "Centre of the narrow fairway",
    5: "Left-centre of the fairway, away from the right-side bunkers",
    6: "Centre of the fairway",
    8: "Centre of the fairway, short of the right-side bunker",
    "9B": "Left-centre of the fairway, away from the creek on the right",
    "9F": "Left-centre of the fairway, away from the pond (2-wood or driver)",
    10: "Left-centre of the fairway, away from the pond",
    11: "Centre of the fairway, short of the creek",
    13: "Left side of the fairway, away from the pond",
    14: "Left-centre of the fairway, away from the creek",
    16: "Left-centre of the fairway",
    17: "Centre of the fairway",
    18: "Centre-left of the fairway, between the long grass and the creek",
}

ORDER = [1, "2F", "2B", 4, 5, 6, 7, 8, "9F", "9B", 10, 11, 12, 13, 14, 15, 16, 17, 18]
# Official card (course_data/tees/scorecard.json): the golfer plays the Black tees. On 2 and 9 the
# "forward" screenshots are the Black tees (2: 520 vs card 507; 9: 373 vs 365) and the "back" ones
# are the Gold tips (2: 609 vs 607; 9: 399 vs 410).
LABELS = {"2B": "2 Gold tee", "2F": "2 Black tee", "9B": "9 Gold tee", "9F": "9 Black tee"}


# ---- Elevation (USGS 3DEP 1 m DEM, course_data/elevation/) -----------------------------------
# Per club: carry change from the tee-to-landing drop, roll factor from the landing slope, and the
# sideways kick on a side slope (+ = right). Par 3s get a plays-like change.
def _load_elevation():
    import sys as _sys
    here = os.path.dirname(os.path.abspath(__file__))
    _sys.path.insert(0, os.path.join(here, "..", "course_data", "elevation"))
    try:
        import adjust as _E
    except Exception:
        return False
    for k, hd in HOLES.items():
        try:
            a = _E.adjustments(str(k))
        except Exception:
            continue
        hd["elev"] = {c: (v["carry_delta_yds"], v["roll_factor"], v["lateral_kick_yds"])
                      for c, v in a.get("clubs", {}).items()}
        hd["elev_info"] = dict(bearing=a.get("bearing_deg_true"))
    for k, p in PAR3.items():
        try:
            a = _E.adjustments(str(k))
            p["plays_like_delta"] = float(a.get("plays_like_delta_yds", 0.0))
            p["bearing"] = a.get("bearing_deg_true")
        except Exception:
            pass
    return True


ELEVATION = _load_elevation()
