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
Holes 1-3 weren't provided. Hole 9 has two tees (back and forward).
"""
import numpy as np

HOLES = {
    4: dict(
        par=5, image="hole04.png", length=520,
        tee=(508, 1907), dot270=(435, 1188),
        zones=[
            ("fairway", [(385, 860), (495, 860), (500, 1000), (505, 1300), (515, 1500), (400, 1500),
                         (390, 1300), (385, 1000)]),
            ("recovery", [(0, 540), (300, 540), (260, 800), (215, 1000), (205, 1300), (240, 1600),
                          (0, 1600)]),                                           # woods left
            ("native", [(225, 800), (355, 800), (358, 1000), (360, 1300), (365, 1500), (240, 1500),
                        (215, 1300), (215, 1000)]),                              # long grass left
            ("native", [(525, 860), (585, 860), (590, 1500), (530, 1500)]),     # long grass right
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
            ("sand", [(490, 828), (555, 835), (555, 890), (495, 892)]),          # right, ~300 out
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
            ("native", [(200, 540), (300, 540), (330, 700), (340, 900), (330, 1050), (290, 1050),
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
            ("fairway", [(330, 540), (440, 540), (480, 700), (500, 800), (520, 900), (540, 1050),
                         (530, 1300), (330, 1300), (320, 1000), (330, 800)]),
            ("recovery", [(0, 540), (250, 540), (260, 800), (270, 1100), (280, 1300), (0, 1300)]),
            ("native", [(470, 540), (560, 540), (620, 700), (700, 900), (760, 1000), (860, 1150),
                        (920, 1250), (920, 1330), (820, 1250), (700, 1100), (600, 950), (520, 800),
                        (480, 680)]),                                            # creek banks
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
            ("fairway", [(130, 1450), (270, 1450), (330, 1300), (390, 1170), (440, 1050), (500, 900),
                         (560, 780), (620, 640), (650, 560), (450, 560), (330, 720), (250, 900),
                         (190, 1100), (150, 1300)]),                             # left of the creek
            ("fairway", [(480, 1450), (560, 1450), (600, 1200), (650, 1050), (720, 900), (800, 700),
                         (700, 700), (640, 850), (570, 1000), (520, 1150)]),     # right of the creek
            ("recovery", [(0, 540), (470, 540), (330, 720), (220, 900), (170, 1100), (110, 1300),
                          (70, 1450), (0, 1450)]),                               # woods left
            ("native", [(270, 1450), (480, 1450), (520, 1150), (570, 1000), (640, 850), (700, 700),
                        (760, 560), (650, 560), (620, 640), (560, 780), (500, 900), (440, 1050),
                        (390, 1170), (330, 1300)]),                              # creek banks
            ("water", [(370, 1450), (400, 1450), (460, 1250), (520, 1100), (590, 950), (650, 820),
                       (720, 600), (700, 600), (630, 800), (570, 930), (500, 1080), (440, 1230)]),
            ("sand", [(590, 1270), (640, 1270), (640, 1350), (590, 1350)]),
        ]),
}

HOLES[13]["irons"] = True                    # pond + bunker squeeze the landing zone

# Green centre for approach distances: along the tee line at the hole's length.
for _h in HOLES.values():
    _h.setdefault("aim_min", -40)
    _h.setdefault("aim_max", 40)
    _tee, _d = np.array(_h["tee"], float), np.array(_h["dot270"], float)
    _ppy = np.linalg.norm(_d - _tee) / 270
    _h["green"] = tuple(_tee + (_d - _tee) / np.linalg.norm(_d - _tee) * _h["length"] * _ppy)


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
             [(380, 762), (440, 758), (480, 780), (490, 830), (487, 900), (470, 945), (430, 960),
              (385, 952), (362, 915), (358, 850), (365, 795)],
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
    4: "Woods and long grass left; tree line then houses (OB) right. Wide enough for driver, which "
       "sets up ~225 for the second. Every club gives up ~0.1 to driver here.",
    5: "Highway (OB) left, houses (OB) right. Bunkers right at ~275-300 catch ~9% of drives even "
       "aimed left. Driver and 2-wood are a tie (0.003); 4-wood ~0.02 behind.",
    6: "Long grass both sides, nothing penal. Driver for the shorter approach.",
    8: "Bunker 5-25 yds right of the line at ~270-290 out catches about a third of drives. The "
       "4-wood stops short of it. Houses (OB) right behind the black line.",
    "9B": "Pond starts ~6 yds right of the line from ~140 to ~250 out. Driver carries past the end "
          "of it; aim left-centre so a slice doesn't find the front of the pond.",
    "9F": "From the forward tee driver and 2-wood are a tie (0.008); the pond is right at ~150-200. "
          "Long grass across the fairway at ~315-340, so don't hit it longer than driver.",
    10: "Pond right from ~237 to ~328, creek in the woods left. Aim a touch left; driver's extra "
        "20 yds is worth 0.08 on a par 5.",
    11: "Creek crosses the fairway at ~286-292. Driver carries 275 and rolls into it (3 in 4). "
        "4-wood stops ~270, short of it. 2-wood still reaches it 1 time in 6. Irons cost 0.14+.",
    13: "Pond right from ~173 to ~295, pot bunkers left at ~280-300. The 4-wood stops short of the "
        "pots; driver finds sand ~23%. Irons give up too much (0.2+).",
    14: "Creek with long-grass banks down the right. The trees on the left lean into the fairway "
        "because of the camera angle; they're modelled at the trunks.",
    16: "Three-way tie (0.01). Woods both sides, bunkers right at ~300 and left at ~255.",
    17: "Woods right, open field left. The fairway bunker is ~335 out, out of reach.",
    18: "The creek and its long-grass banks cut diagonally across from short-left to long-right. "
        "Carry it (~190-215 out) and stay well left; the trees left lean in on the photo.",
}

AIM_AT = {
    4: "Right-centre of the fairway",
    5: "Left-centre of the fairway, away from the right-side bunkers",
    6: "Centre of the fairway",
    8: "Centre of the fairway, short of the right-side bunker",
    "9B": "Left-centre of the fairway, away from the pond",
    "9F": "Left-centre of the fairway, away from the pond",
    10: "Left-centre of the fairway, away from the pond",
    11: "Centre of the fairway, short of the creek",
    13: "Left side of the fairway, away from the pond",
    14: "Left-centre of the fairway, away from the creek",
    16: "Left-centre of the fairway",
    17: "Centre of the fairway",
    18: "Left side of the fairway, well away from the creek",
}

ORDER = [4, 5, 6, 7, 8, "9B", "9F", 10, 11, 12, 13, 14, 15, 16, 17, 18]
LABELS = {"9B": "9 back tee", "9F": "9 forward tee"}
