"""Proposed map patches from the landing-zone evidence check (spirit_hollow/qa_landing/findings.md).

NOT applied: the coordinator reviews and copies the ones to keep into course.AUDIT_FIXES.

PATCHES has the AUDIT_FIXES format ({hole: [(lie, polygon in 920x2000 screenshot px), ...]}) and is
meant to be APPENDED to the hole's AUDIT_FIXES list (later zones override earlier ones; "rough" /
"fairway" / "first_cut" entries undo hazards that were drawn too big).

!! course.py AUDIT_FIXES has the keys 5 and 8 twice. In a dict literal the second entry wins, so the
   first 5 fix (right bunker ~2x) and the first 8 fixes (long grass left ends 10-19 yds further left;
   L-bunker grass block) are silently dropped today. Merge the duplicate entries when applying these.

PROPOSED: finding id -> hole, verdict (map wrong / evidence wrong / unclear), rank(s) in disagree.md,
note, patches. Only "map wrong" findings carry patches. Polygons from `disagree.py` (the disputed cells
grown back to the hand edge, limited to where the evidence agrees) or, for sand, the OSM bunker
outlines (disagree.sand_patch). Re-check after a map change: python3 spirit_hollow/qa_landing/disagree.py
"""

PROPOSED = {
    '1-trees-right-305': dict(
        hole=1, verdict='map wrong', ids=['1-mrec-324R20'], ranks=[1],
        note=('Woods right: from ~305 out the canopy (lidar 2019, NAIP 2023, and the dark tree texture in the '
              "screenshot) comes right to the fairway's right edge; the map leaves a 15-29 yd wedge of rough "
              'before its tree line.'),
        patches=[
            ('recovery', [(702, 1089), (687, 1104), (643, 1104), (619, 1084), (633, 1064),
                         (629, 1054), (614, 1054), (594, 1084), (569, 1093), (540, 1078), (510, 1029),
                         (511, 994), (491, 945), (501, 935), (624, 936), (639, 951)]),
        ]),
    '18-creek-bank-right': dict(
        hole=18, verdict='map wrong', ids=['18-pnat-292R22'], ranks=[2],
        note=("Creek bank right, 231-335: the long-grass polygon's fairway-side edge sits 9-15 yds inside where "
              'the tan bank starts in the screenshot zoom and where NAIP shows the unmown strip; vision2 '
              '(screenshot, LOHO) agrees (p(native) 0.04 on the strip). A 4-yd fringe of long grass is kept '
              "next to the evidence edge. NB this partly reverses the earlier landing-zone check's hole-18 fix "
              "(the 'tan bank starts right at the fairway edge' native polygon): see crops/zoom_18_340_830.png "
              '(photo | NAIP) before accepting.'),
        patches=[
            ('rough', [(371, 1228), (364, 1221), (387, 1171), (439, 1008), (476, 926), (496, 907),
                      (529, 836), (540, 825), (564, 825), (579, 838), (572, 863), (559, 888), (487, 964),
                      (481, 992), (464, 1011), (461, 1046), (441, 1064), (449, 1099), (429, 1131),
                      (429, 1145), (409, 1174), (409, 1185)]),
        ]),
    '9F-trees-left-260': dict(
        hole='9F', verdict='map wrong', ids=['9F-mrec-288L48'], ranks=[3],
        note=('Tree clump left at 261-312, -34..-55 (same clump as 9B 310-335 left): canopy in lidar, NAIP and '
              'the screenshot; the map has rough / first cut there.'),
        patches=[
            ('recovery', [(303, 833), (290, 808), (300, 778), (308, 773), (305, 762), (313, 738),
                         (338, 722), (324, 701), (333, 673), (341, 669), (352, 679), (377, 673),
                         (385, 703), (395, 703), (399, 711), (388, 724), (402, 735), (407, 751),
                         (389, 765), (371, 766), (366, 761), (354, 768), (345, 795), (321, 798),
                         (324, 809), (338, 807), (343, 812), (334, 840)]),
        ]),
    '9F-trees-long-300': dict(
        hole='9F', verdict='map wrong', ids=['9F-mrec-306L1'], ranks=[4],
        note=('Tree line across the hole at 294-318 (-34..+15): the traced fairway runs ~15 yds into the trees '
              'before the long-grass band.'),
        patches=[
            ('recovery', [(580, 718), (562, 776), (532, 794), (520, 780), (505, 741), (470, 744),
                         (457, 722), (422, 735), (405, 713), (415, 702), (573, 709)]),
        ]),
    '9B-9F-tree-clump-right': dict(
        hole='9B', verdict='map wrong', ids=['9B-prec-285R20'], ranks=[6],
        note=("Tree clump right of the fairway at 268-297 (9B) / 231-262 (9F): the map's clump starts at +14 "
              "(9B) / +6 (9F) but in NAIP the dark area there is the clump's shadow; the crowns (and the 2019 "
              'lidar canopy) start ~+30 (9B) / ~+25 (9F). The winter screenshot shows the shadow and leaning '
              'branches. The canopy edge is moved out 13-18 yds.'),
        patches=[
            ('rough', [(479, 882), (469, 860), (476, 779), (483, 772), (557, 767), (564, 775),
                      (541, 796), (545, 803), (537, 811), (530, 807), (511, 828), (518, 843), (502, 857),
                      (506, 872)]),
        ]),
    '9F-tree-clump-right': dict(
        hole='9F', verdict='map wrong', ids=['9F-prec-252R16'], ranks=[8],
        note=('Same clump from the 9F tee (see 9B-9F-tree-clump-right).'),
        patches=[
            ('rough', [(504, 999), (493, 961), (493, 887), (547, 877), (569, 880), (573, 889),
                      (537, 918), (534, 927), (540, 939), (528, 979), (537, 982), (540, 993), (528, 1000)]),
        ]),
    '13-pot-bunkers-left': dict(
        hole=13, verdict='map wrong', ids=['13-psan-297L19', '13-msan-304L4', '13-msan-317R2'], ranks=[5, 14, 23],
        note=('Pot bunkers left: the photo and NAIP show two bunkers (a figure-8 at 270-292, -32..-15 and a '
              "larger one at 305-325, -14..+4). The map's top box at 294-300 is grass, and the upper bunker is "
              '~2.5x the traced square. Boxes replaced by the OSM outlines (which sit on the NAIP sand).'),
        patches=[
            ('first_cut', [(418, 798), (410, 798), (417, 806), (418, 806)]),
            ('first_cut', [(402, 798), (402, 808), (404, 801), (410, 798)]),
            ('fairway', [(377, 894), (380, 894), (382, 891), (375, 886), (371, 880), (373, 876),
                        (381, 871), (391, 870), (393, 872), (395, 889), (393, 894), (395, 894), (395, 890),
                        (397, 890), (395, 848), (365, 848), (372, 892), (377, 892)]),
            ('fairway', [(358, 896), (358, 898), (361, 897), (370, 903), (374, 903), (379, 896)]),
            ('first_cut', [(358, 922), (362, 922), (360, 915), (358, 914)]),
            ('sand', [(382, 914), (390, 904), (395, 889), (393, 872), (391, 870), (381, 871),
                     (373, 876), (371, 880), (375, 886), (382, 891), (374, 903), (370, 903), (361, 897),
                     (357, 899), (355, 903), (354, 910), (356, 913), (360, 915), (363, 927), (366, 929),
                     (372, 928), (380, 923), (382, 918)]),
            ('sand', [(415, 844), (420, 842), (426, 835), (427, 826), (423, 819), (423, 817),
                     (433, 812), (437, 805), (436, 796), (434, 792), (431, 789), (427, 790), (424, 793),
                     (422, 803), (419, 805), (417, 806), (410, 798), (404, 801), (402, 808), (403, 817),
                     (410, 826), (408, 836), (409, 841)]),
        ]),
    '5-right-bunker-300': dict(
        hole=5, verdict='map wrong', ids=['5-msan-295R15'], ranks=[7],
        note=("Right bunker ~300 out is a hook shape reaching 291-304, +8..+25 (photo, NAIP, OSM); the map's "
              "box stops at ~302. NOTE course.py AUDIT_FIXES has key 5 twice: the earlier '~2x the trace' box "
              'is silently dropped. Replaced by the OSM outline.'),
        patches=[
            ('fairway', [(535, 835), (501, 835), (510, 842), (512, 852), (505, 861), (505, 868),
                        (525, 880), (528, 873), (527, 865), (531, 859), (535, 859)]),
            ('sand', [(482, 835), (476, 845), (475, 862), (483, 873), (490, 881), (493, 907),
                     (501, 916), (509, 921), (524, 922), (529, 917), (532, 907), (542, 899), (551, 889),
                     (554, 876), (547, 863), (539, 859), (531, 859), (527, 865), (528, 873), (526, 881),
                     (505, 868), (505, 861), (512, 852), (510, 842), (504, 836), (496, 833)]),
        ]),
    '17-lone-tree-right-310': dict(
        hole=17, verdict='map wrong', ids=['17-mrec-308R36'], ranks=[9],
        note=('A single large tree in the right rough at 298-320, +25..+45 (NAIP crown ~20 yds across, lidar '
              'canopy; visible in the screenshot); the map has rough there.'),
        patches=[
            ('recovery', [(497, 958), (498, 950), (488, 934), (497, 903), (516, 890), (548, 894),
                         (557, 912), (548, 946), (520, 966), (514, 960)]),
        ]),
    '11-canopy-left-245': dict(
        hole=11, verdict='map wrong', ids=['11-mrec-245L26', '11-mrec-261L30'], ranks=[11, 22],
        note=('Left of the fairway at 238-277: the canopy of the trees on the far side of the cart path '
              'overhangs the path and the left rough to ~-20 (lidar + NAIP crowns); the map stops the trees at '
              '~-38 (trunks). Under-canopy lies are often playable, so this is the upper bound of the effect.'),
        patches=[
            ('recovery', [(373, 884), (349, 876), (329, 843), (333, 807), (350, 791), (362, 803),
                         (353, 811), (365, 827), (401, 848), (401, 860)]),
            ('recovery', [(353, 835), (333, 815), (333, 787), (346, 775), (338, 759), (346, 751),
                         (366, 771), (366, 787), (358, 795), (362, 803), (353, 811), (365, 823)]),
        ]),
    '8-right-bunker-280': dict(
        hole=8, verdict='map wrong', ids=['8-psan-273R6'], ranks=[12],
        note=('The kidney bunker at 272-295 right is drawn as a 75x70 px box, twice the sand area (photo, NAIP, '
              'OSM); the corners are fairway. NOTE AUDIT_FIXES has key 8 twice: the earlier grass-block fix for '
              'this bunker is silently dropped. Replaced by the OSM outline.'),
        patches=[
            ('fairway', [(520, 875), (520, 805), (445, 805), (447, 875), (480, 875), (472, 857),
                        (459, 853), (453, 848), (448, 840), (448, 822), (452, 814), (467, 809), (476, 810),
                        (483, 816), (486, 822), (484, 831), (488, 840), (514, 844), (518, 851), (517, 861),
                        (513, 865), (496, 868), (486, 875)]),
            ('sand', [(518, 851), (514, 844), (505, 842), (495, 842), (488, 840), (484, 831),
                     (486, 822), (483, 816), (476, 810), (467, 809), (458, 811), (452, 814), (448, 822),
                     (448, 840), (453, 848), (459, 853), (472, 857), (476, 864), (478, 873), (482, 878),
                     (496, 868), (506, 867), (513, 865), (517, 861)]),
        ]),
    '8-long-grass-left': dict(
        hole=8, verdict='map wrong', ids=['8-pnat-312L29'], ranks=[26],
        note=('Long grass left at 267-335 ends 12-21 yds further left than drawn (screenshot and NAIP: mown to '
              "~-38). This is exactly the earlier audit's rough patch that is lost to the duplicate key 8 in "
              'AUDIT_FIXES; restored verbatim.'),
        patches=[
            ('rough', [(245, 650), (325, 650), (330, 700), (340, 900), (333, 975), (330, 975),
                      (310, 900), (278, 800), (250, 700)]),
        ]),
    '9B-trees-left-310': dict(
        hole='9B', verdict='map wrong', ids=['9B-mrec-325L41'], ranks=[13],
        note=('9B left at 309-335 (-55..-19): the tree clump that 9F also shows; unmapped from the Gold tee.'),
        patches=[
            ('recovery', [(257, 712), (236, 686), (237, 664), (223, 649), (223, 638), (276, 599),
                         (361, 602), (375, 621), (356, 639), (323, 634), (311, 644), (314, 659),
                         (299, 673), (285, 666), (277, 673), (277, 680), (295, 695), (298, 718),
                         (286, 724)]),
        ]),
    '5-right-strip': dict(
        hole=5, verdict='map wrong', ids=['5-prec-251R41'], ranks=[15],
        note=("The 'trees' strip right (+33..+45, 209-303) is rough and the cart path in the screenshot and "
              'NAIP, no canopy in lidar; only a couple of small trees at ~200. OB (houses) beyond is unchanged.'),
        patches=[
            ('rough', [(605, 1224), (591, 1214), (597, 1207), (590, 1201), (585, 996), (591, 989),
                      (609, 991), (615, 974), (614, 956), (586, 947), (582, 864), (592, 857), (625, 886),
                      (647, 920), (651, 1000), (649, 1201), (636, 1209), (628, 1202), (635, 1195),
                      (617, 1189), (618, 1199), (608, 1207), (615, 1217)]),
        ]),
    '13-pond-corner': dict(
        hole=13, verdict='map wrong', ids=['13-pwat-283R20'], ranks=[16],
        note=("The pond's top-left corner (279-286, +18..+23) is drawn square; the shore is rounded (photo, "
              'NAIP, OSM). Small.'),
        patches=[
            ('rough', [(482, 904), (476, 900), (478, 882), (493, 875), (498, 880)]),
        ]),
    '16-woods-left-270': dict(
        hole=16, verdict='map wrong', ids=['16-snat-286L47'], ranks=[17],
        note=('Left: the woods reach down to ~271 (canopy in lidar/NAIP and dark trees in the photo); the map '
              'switches from trees to the long-grass field at 300 (a straight line at y=900).'),
        patches=[
            ('recovery', [(275, 1016), (255, 1016), (244, 1009), (231, 971), (206, 953), (207, 915),
                         (224, 898), (280, 898), (287, 905), (286, 940), (279, 954), (286, 961),
                         (289, 992)]),
        ]),
    '13-tree-right-300': dict(
        hole=13, verdict='map wrong', ids=['13-mrec-296R33'], ranks=[18],
        note=('Tree(s) right of the fairway above the pond at 291-317, +21..+43 (grey winter crown in the '
              'photo, NAIP crown, lidar); the map has fairway / first cut.'),
        patches=[
            ('recovery', [(500, 878), (492, 865), (499, 860), (496, 855), (506, 844), (505, 836),
                         (520, 827), (531, 834), (526, 842), (534, 847), (538, 860), (528, 871)]),
        ]),
    '2B-trees-right-290': dict(
        hole='2B', verdict='map wrong', ids=['2B-mrec-298R23', '2B-snat-288R35'], ranks=[19, 29],
        note=('Right at 279-302: a tree clump inside the long-grass band (+25..+42) whose canopy overhangs the '
              'cart path to +22 (photo, NAIP, lidar).'),
        patches=[
            ('recovery', [(529, 818), (509, 792), (508, 773), (515, 765), (527, 765), (539, 776),
                         (544, 802)]),
            ('recovery', [(581, 877), (545, 833), (531, 772), (538, 764), (546, 764), (582, 797),
                         (583, 824), (614, 838)]),
        ]),
    '2B-long-grass-left-320': dict(
        hole='2B', verdict='map wrong', ids=['2B-pnat-322L39'], ranks=[21],
        note=('Left at 300-335: mown rough runs to the bank of the water at ~-47 (photo, NAIP); the long-grass '
              'band is drawn 10-16 yds further in (to -35).'),
        patches=[
            ('rough', [(284, 806), (263, 765), (262, 742), (238, 712), (225, 663), (231, 644),
                      (247, 658), (255, 658), (266, 638), (285, 638), (293, 645), (295, 794)]),
        ]),
    '17-long-grass-left': dict(
        hole=17, verdict='map wrong', ids=['17-mnat-303L42'], ranks=[24],
        note=("Left at 273-335: the field's long grass starts at the cart path (~-38) in NAIP, the photo and "
              'both classifiers; the map starts it 12-15 yds further left.'),
        patches=[
            ('native', [(248, 1005), (243, 999), (290, 823), (307, 804), (327, 807), (334, 816),
                       (316, 849), (308, 930), (274, 1002), (254, 1000)]),
        ]),
    '4-long-grass-left': dict(
        hole=4, verdict='evidence wrong', ids=['4-mnat-273L31'], ranks=[10],
        note=("vision_any's long-grass layer bleeds ~8 yds over the cart path; the photo zoom and NAIP show "
              "mown rough between the path and the fairway, as the audit's rough strip says."),
        patches=[]),
    '16-trees-right-265': dict(
        hole=16, verdict='unclear', ids=['16-prec-264R23'], ranks=[20],
        note=('NAIP shows a dark patch (shadow or low shrubs) at +20..+28; lidar has no canopy until +30. 0.4% '
              'of shots; left as is.'),
        patches=[]),
    '2F-pond-corner': dict(
        hole='2F', verdict='unclear', ids=['2F-pwat-283L36'], ranks=[25],
        note=('5 yds at one corner of the creek polygon: at the tolerance; not worth a patch.'),
        patches=[]),
    '10-creek-bank-left': dict(
        hole=10, verdict='unclear', ids=['10-pnat-298L24'], ranks=[28],
        note=('Tan creek-bank strip at 283-306 may be ~5-9 yds narrower than drawn; 0.2% of shots.'),
        patches=[]),
}

# Alternative for the three sand fixes (13, 5, 8): edit the traced boxes in place instead of appending
# (old polygon as it appears in HOLES / AUDIT_FIXES -> new (lie, polygon), or None = delete). Appending
# the PATCHES version adds 'fairway' pieces, which moves course.py's first_cut insertion point (it goes
# after the LAST fairway zone) so the first cut bands are drawn over ~25 yd2 of the other hole-8 boxes.
REPLACE = {
    13: [
        ([(365, 848), (395, 848), (397, 890), (372, 892)],
         ('sand', [(382, 914), (390, 904), (395, 889), (393, 872), (391, 870), (381, 871),
                 (373, 876), (371, 880), (375, 886), (382, 891), (374, 903), (370, 903), (361, 897),
                 (357, 899), (355, 903), (354, 910), (356, 913), (360, 915), (363, 927), (366, 929),
                 (372, 928), (380, 923), (382, 918)])),
        ([(377, 870), (395, 870), (395, 894), (377, 894)],
         None),
        ([(358, 896), (382, 896), (382, 922), (358, 922)],
         None),
        ([(402, 798), (418, 798), (418, 822), (402, 822)],
         ('sand', [(415, 844), (420, 842), (426, 835), (427, 826), (423, 819), (423, 817),
                 (433, 812), (437, 805), (436, 796), (434, 792), (431, 789), (427, 790), (424, 793),
                 (422, 803), (419, 805), (417, 806), (410, 798), (404, 801), (402, 808), (403, 817),
                 (410, 826), (408, 836), (409, 841)])),],
    5: [
        ([(490, 835), (535, 835), (535, 880), (492, 882)],
         ('sand', [(482, 835), (476, 845), (475, 862), (483, 873), (490, 881), (493, 907),
                 (501, 916), (509, 921), (524, 922), (529, 917), (532, 907), (542, 899), (551, 889),
                 (554, 876), (547, 863), (539, 859), (531, 859), (527, 865), (528, 873), (526, 881),
                 (505, 868), (505, 861), (512, 852), (510, 842), (504, 836), (496, 833)])),],
    8: [
        ([(445, 805), (520, 805), (520, 875), (447, 875)],
         ('sand', [(518, 851), (514, 844), (505, 842), (495, 842), (488, 840), (484, 831),
                 (486, 822), (483, 816), (476, 810), (467, 809), (458, 811), (452, 814), (448, 822),
                 (448, 840), (453, 848), (459, 853), (472, 857), (476, 864), (478, 873), (482, 878),
                 (496, 868), (506, 867), (513, 865), (517, 861)])),],
}

PATCHES = {}
for _f in PROPOSED.values():
    if _f["verdict"] == "map wrong" and _f["patches"]:
        PATCHES.setdefault(_f["hole"], []).extend(_f["patches"])
