# Will's sanity check (running list)

Read-only reviewer playing the golfer. Each entry: question in Will's voice -> what I checked -> verdict
(fine / doubt / wrong) -> what to do. Most important first. Times are UTC.

## Top 5 push-backs (pass 2, Nov 13 03:17Z)

1. **16 mound: answered in 222f7ece4 (now a penal lie), not yet proven.** The rev 6 solve has to bring the 4-wood aim back to about the middle of the neck (0 to +3) and the 2-wood back to clearly worse. Until I see that, 16 is open.
2. **The picture does not show the green on 8 (113 yds left, cut off) and barely on 11; on 3, 5, 6, 13, 18 "Whole hole" stops ~440 yds from the tee.** On a 46-left corner cut I want to see what I am cutting toward.
3. **9 Driver is still only a 0.03-0.04 call** (a tie on firm ground by the integrator's own roll test). F1 now confirms the right side is mown, so I accept Driver, but it must be shown as a close call with "4-wood centre is the same score".
4. **Map is frozen (good). Keep it frozen.** Anything F1 / F2 find from here goes in a list for after the tournament unless it moves an aim 3+ yds on a hole where the club is close (8, 9, 10, 16).
5. **Model workstream has produced no finding yet and most of it cannot change a club** (scratch / 5-handicap levels, "what-if golfers"). Only the second-shot check on 10 and 16 earns its time. And nobody has asked Will for his real iron carries, which decide every par-3 club.

Closed since pass 1: map freeze + 3-yd rule (222f7ece4); frost / firm-ground roll test done (8 holds, 9 ties, 10 goes
back to 4-wood on very firm ground and the page will say so, 16 holds); page wording clean-up is in the template
(one aim number, "N % sure", the not-in-bag club last): to be checked on the rebuilt page.

<details><summary>Pass 1 top 5 (03:05Z)</summary>
1. **16: tonight's map swap deleted the rocky mound right of the fairway, and the aim walked 10 yds toward it.** Put it back (penalised), keep 4-wood, aim the middle of the neck.
2. **Six holes' hand-checked long grass (10, 11, 13, 15, 16, 18) were replaced wholesale at 02:53Z by machine polygons, read from a file that is still being edited.** Freeze that file now; no map change after tonight unless it moves a club or an aim by 3+ yds.
3. **8 Driver: I buy it. 9 Driver: coin flip (0.03-0.04) that has flipped twice tonight on one label.** Ship 9 as a close call, not as a confident change; wait for the holes 1-9 feature check before publishing either.
4. **The page I would hold on the tee is still the Nov 12 build and has things I would have to stop and think about:** 8's green is not in the picture; three different aim numbers per hole; "what-if worlds / golfers"; a club I do not own listed above my club.
5. **Nobody is checking the frost.** 24 F overnight, 35 F at 9:00 Saturday: frost delay (tee times and temperatures shift) and firm ground (more roll) hit exactly the three "longer club" changes (8 Driver, 9 Driver, 10 2-wood). Meanwhile the model workstream is running player what-if cases that cannot change a club.

</details>

---

## Pass 1 (Nov 13, 02:50-03:05Z)

Looked at: the published-candidate page (`wind_page/index.html`, last built 7526bd568, Nov 12 forecast) rendered per
hole on Back (whole hole + landing area, 2x) and Middle (text + whole hole); the integrator's local re-solves
(`scratchpad/gw_final/new_back.json` = rev 4 map, `new_back2.json` = rev 5 map, `new_mid.json`); the built maps
`truth/course.py` at 42c3e3f15 and at 814ad99d4 (grid diff of every landing area, holes 8-18); PHYSICS.md;
FEATURES_10_18.md / json; `second_pass/model/*.py` (no MODEL.md yet); FEATURES_1_9 not landed yet.
**The page has not been rebuilt since Nov 12, so every picture comment below is about the old build.**

### A. Tonight's proposed changes

**[16 Back, 4-wood] "Why did my aim on 16 go from 3 left to 8 right? There is a pile of rocks and weeds over there."**
- Checked: built map before / after 814ad99d4. At (10..43 R, 264..298 yds) the zone was `native`, now plain `rough`.
  Cause: `trace.py` applies only `action == "add"` edits from `features_10_18.json`; the mound is a `replace` edit
  ("keep the outline, downgrade the lie: rough-plus, or native with p <= 0.4") so it was dropped altogether.
  The specialist asked for a downgrade, the code did a delete.
- Effect in the integrator's own numbers: 4-wood aim -3.0 -> +3.5 (rev 4) -> **+7.5** (rev 5); 2-wood from +0.156 /
  +0.211 worse to only **+0.038** worse; Driver (19 % fairway) only +0.089. The rev 5 Actions solve is running on this map.
- Picture (NAIP Aug 2023, page landing view and the integrator's panel): a lumpy, tufted mound with a line of white
  stones on its fairway side. Lidar says the grass on it is short. Short grass on a rock-edged mound is still not a
  normal rough lie.
- Verdict: **wrong** (implementation), the idea behind it (left fescue is the real trouble, 10 yds closer than
  mapped) is **fine**.
- Do: restore the mound as a penalised zone (what F2 asked for), re-solve 16 Back + Middle. Expect 4-wood, aim
  about centre of the neck (0 to +3). Do not let 16 drift to 2-wood on a 0.04 margin made by a deleted hazard.
  Fairway in the neck at 266 runs about 15 L to 12 R; left fescue starts ~20 L. "Middle of the neck, 4-wood" is the
  whole instruction.

**[map, 10 / 11 / 13 / 15 / 16 / 18] "You had three people eye-check this map on Nov 9. Why was it replaced at 3 am Friday?"**
- Checked: `EXTRA[hole] = <second-pass polygons>` replaces every hand native band on those holes. Source: lidar of
  Dec 2020 (10-14, parts of 15 / 16) and Dec 2023 (16-18). Grid diff of the landing areas: 16 left edge moved in
  (good, three sources agree); 16 mound lost (above); 10 lost native 30 yds left and right of the green and gained
  it 30 yds past; 11 and 15 left bands shifted 5-10 yds; 13, 18 edges only.
- Also: `features_10_18.json` is modified and uncommitted in the shared checkout right now (the committed file and
  the working file differ on 10, 13, 15, 16, 18). The trace reads whatever is on disk, so a local rebuild and the
  Actions run can be solving different maps.
- Verdict: **doubt** (risky, not reproducible). Only 16 changed a number that matters (aim 10 yds). No club flipped
  on 10, 11, 13, 15, 18 (all Driver / 2-wood by 0.06-0.13).
- Do: (1) commit / freeze the features file before any more solves; (2) keep the lidar edge only where it moves an
  aim by 3+ yds or a club, list those in one table (hole, old edge, new edge, aim before / after); (3) set a hard
  map freeze tonight. Everything after that is forecast only.

**[8 Back, 2-wood 41 L -> Driver 46 L] "Is 46 left a real dog-leg or is the computer aiming me into the weeds?"**
- Checked: picture + map. Real dog-leg left: green is 113 yds left of the tee line (371 along). At 290-300 yds the
  fairway runs 60 L to 20 L; long is rough until ~310, then the unmown square (35 L and right of it). Driver 293
  total: fairway 65 %, rough 33 %, long grass 0.1 %, nothing with a penalty. 2-wood +0.056, 4-wood +0.10. 100 in vs 122.
- Why it flipped: ground left of the fairway used to be priced "unverified" (half trees). It is mown rough.
- Verdict: **fine, I buy Driver.** No penalty ground in the pattern, 20 yds closer: that is the DECADE answer.
- Doubts to close: (a) the only way to hurt yourself is long through the bend; firm / frozen ground adds roll
  (see frost). Room past the Driver's finish is ~20-25 yds. (b) FEATURES_1_9 has not confirmed the left side yet.
- Do: say the reason on the page in one line ("cut the corner: fairway turns left at 290"). If Saturday morning is
  frozen, 2-wood on the same line is the same shot with no run-out risk.

**[9 Back, 4-wood 3 R -> Driver 19 R (15 R after the tree fix)] "Fairway 50 % and you want Driver?"**
- Checked: picture: 4-wood stops in a neck at 267 with two bunkers right; Driver at 296 reaches the upper fairway,
  which is no wider (~35 yds) but 30 yds closer (94 in vs 123). Left of it is tufted long grass, right is striped
  mown rough to the cart path, then trees. Numbers (rev 5): Driver best, 2-wood +0.030, 4-wood +0.037; Driver
  fairway 50 %, long grass 3 %, trees 4 %. On Nov 9 the 4-wood won by 0.056, at 02:41Z Driver won by 0.063, at
  02:52Z by 0.037.
- The whole flip is one label: the band right of the fairway (30-45 R) was "fescue", now "mown" (stripes on the
  2023 photo, green on this week's satellite). I agree it looks mown in the picture.
- Verdict: **doubt.** Direction is right (aim away from the long grass, right rough is fine), size is a coin flip.
- Do: show it as a close call: "Driver 15 R; 4-wood centre is within 0.04". Do not present it as a confident
  change. If F1 (holes 1-9) says the right band is mown: Driver. If not: back to 4-wood. Either is fine.

**[10 Back, 271 yds, 4-wood -> 2-wood] "Go for it or lay up?"**
- Checked: cold-ball physics takes ~10 yds off every club, so the 2-wood (not the 4-wood) is now the 271 club.
  2-wood aimed at the green (20 L; green centre is 18.5 L): on / by the green ~half the time, water 5.7 %.
  4-wood +0.060 (more balls short in the creek side: 7.1 %), Driver +0.21 (through the back), lay-up long iron +0.46.
- Picture: green sits left of a thin creek, the aim line runs along it, pond short-left at 200-220. The 2-wood
  carries all of that.
- Verdict: **fine.** Go, with the club that gets there. The 0.46 for laying up looks big but the sign is right.
- Doubt: frozen ground: a 2-wood that lands on a firm green goes through. Model team: this is the one hole where
  the second-shot rollout is worth running (see C).

**[16 Middle, 325 yds, long iron] "Long iron on a 325-yd hole?"**
- Checked: from the Middle tee the neck starts ~210 and the pond is ~278 on the line. 4-wood (266) finishes past
  the neck with the pond 12 yds on. Long iron 216 stops short of the neck, 108 in, fairway 94 %. Mid iron +0.10.
- Verdict: **fine.** There is no club between 216 and 266 in the bag; that gap is the real story on this hole.

### B. Hole by hole, Back (old build)

| hole | play (book) | picture | verdict |
|---|---|---|---|
| 1 | Driver 7 L | on the fairway past the two right bunkers; right edge of the oval in long grass | fine |
| 2 | Driver 17 R | past the pond, right half of the fairway; right edge reaches the cart path | fine |
| 3 | Driver 8 L | right edge of the oval touches the bunker and the tree line by the yard | fine (aim left is right) |
| 4 | par 3, 175 target | box right-centre of an angled green | fine |
| 5 | Driver 1 L | centre | fine |
| 6 | Driver 6 R | centre-right | fine |
| 7 | par 3, 177 target | box centre | fine |
| 8 | 2-wood 41 L (-> Driver 46 L) | real corner cut; **the green is not in the picture** | see A; picture **wrong** |
| 9 | 4-wood 3 R (-> Driver) | in the neck by the right bunkers | see A |
| 10 | 4-wood / 2-wood at the green | oval on the green, creek under the line | see A |
| 11 | Driver 19 R | diagonal across a right-bending fairway; green 76 R is at the very edge of the picture | fine; check the green shows |
| 12 | par 3, 130 target | box centre of the peninsula green, a touch short-right | fine |
| 13 | Driver 4 R | past three right bunkers | fine |
| 14 | par 3, 194 target on a 200 card | box front-centre, 6 short of the middle | fine if long is the bad miss; say so in one line |
| 15 | Driver 12 R | centre-right, bunkers short-left | fine |
| 16 | 4-wood 3 L | in the neck between left fescue and the right mound, pond 40 yds on | fine (the OLD aim); see A |
| 17 | par 3, 189 target | box centre-left, trees right | fine |
| 18 | Driver 13 R | right of the left bunker | fine |

No path mistaken for water, no shadow mistaken for trees in any landing area I looked at. Lines sit on the real
holes. Every 40+ yd aim (8 only) is a real dog-leg.

**[oval shape] "Is it a wide oval or did it go round again?"**
- Checked the page's own numbers (Driver, 95 %): hole 8: 70 wide x 47 deep; hole 10: 72 x 38; hole 16: 70 x 47;
  but hole 1: 72 x 59, hole 5: 71 x 60, hole 15: 74 x 60 (38 yds short of the dot, 22 long).
- Verdict: **doubt** on 1, 5, 15: nearly round, because the short side carries a 38-yd tail. Wide-not-long everywhere
  else. No club depends on it. Do: nothing tonight unless it is one constant; do not open a workstream for it.

### C. The team's process: "why are we doing this?"

- **Physics (PHYSICS.md): worth it.** Cold ball + high pressure take ~4 more yds off the Driver and add ~3 to every
  par 3; that flipped 10 and moves par-3 clubs. Signs read right: colder / denser = shorter, par 3 plays longer; a
  warm ball goes farther (so "keep one in your pocket" is correct this time). Pressure alone is 1 yd: fine folded
  in, do not show it. Crosswind drift 1.5 yds per mph = 6 yds on a par 3 in 4 mph: believable, small.
  Doubt: the reference model's Tour table was "typed from memory"; it reproduces the altitude and TrackMan wind
  rules, so I accept it, but do not add anything else on top of it.
- **Features 10-18: worth it for 16 left (aim) only.** The rest moved edges that change no club. See A.
- **Features 1-9: the one that matters tonight** (it decides 8 and 9) and it has not landed.
- **Model (`second_pass/model/`): mostly cannot change a club.** `exp1_value.py` runs "am level 0.20 (scratch) /
  0.50 (5+ hcp)" and a Tour table; `exp6` compares "what-if golfers". These are the player what-if cases Will
  said not to do. Stroke-and-distance fixed point: there is no OB in any chosen pattern except 3 (0.3 %): cannot
  matter. **Keep only:** the second-shot rollout on hole 10 (does going for it still win with the creek and the
  pond around the green?) and on 16 (88 in from the neck vs 137 in). Stop the rest.
- **Nobody is checking: frost and firm ground.** Forecast (02:27Z): 24 F at 7:00 Sat, 35 F at 9:00, 46 F at noon.
  PHYSICS.md says roll for the Driver is ~11 yds on soft thawed turf and ~43 on frozen. That is a bigger number
  than every correction made tonight, and it points at the three changes (8 Driver through the bend, 9 Driver,
  10 2-wood through the green) and at 16 (pond 40 yds past the 4-wood). One table is enough: those four holes,
  roll x1.5: does the club hold? Also: a frost delay moves every hole's temperature; the page's "change" tee time
  must be the answer, and the rebuilt page should say so in the footer in one line.
- **Nobody is checking: Will's numbers.** Iron carries are still assumed (5-iron 198, 6-iron 185, 7-iron 174, PW 138,
  SW 113). Par-3 clubs are only as good as those. One question to Will beats any more modelling.

### D. The page as a product (old build; re-check on the rebuild)

1. **8: the green is cut off** (it is 113 yds left; the picture is 83 yds each side). "Whole hole" must show the
   whole hole. Check 11 (green 76 R) too. **wrong**
2. **Three aim numbers on one screen.** Hole 1: header "Aim 5 yds left", text "finishes about 3 yds left", note "Aim
   7.0 yds left; anywhere from 10.0 to 4.0". Hole 9: header "2 yds left", note "3.0 yds right". They are wind-day
   aim, finish, and calm-day aim, but on the tee that reads as a contradiction. Show one aim; move the calm-day book
   out of sight. **wrong**
3. **"256 what-if worlds", "what-if golfers", "± 0.002", "within 0.005 strokes", "Driver-pattern break-even (all
   clubs scaled)".** This is the player-case language Will rejected, and none of it helps pick a club. Replace with
   one plain reason per hole ("Driver: nothing to lose; 4-wood: neck at 266, pond at 300"). **doubt**
4. **"Hybrid ~235 (not in bag)" is in every table, and on 16 Back, 9 and 10 Middle it sorts above the pick with
   "would gain".** A club he does not own, listed first. Drop the row, or one line in the footer. **doubt**
5. **Par-3 numbers: too many.** Hole 4 shows 180 (header), "180 on the card" (badge), 176 (map), 175 (target), 176
   (plays), 174 (7-iron carries), 165 / 180 / 194 (card row), 172-177 (box). He needs: plays 176, 7-iron. **doubt**
6. **14: card 200, map 200, target 194.** Fine if deliberate (front half is the fat part, long is trees), but the
   page does not say why. One line. **doubt**
7. **Driver carry will read ~257-262 after the cold-ball change (his number is 275).** He will ask. One line under
   the table: "275 at 70 F: -13 cold air and ball, -4 wind". **do on the rebuild**
8. Hazard words / outlines: none found. The dashed white ring on par 3s is the green edge: fine. Par-3 photos are
   sharp at 2x. Club is above the hole number. **fine**
9. Middle 3 and 18 carry "Lands past the hand-checked map". If the map is not checked there, either check it or say
   what to do; a warning with no instruction is noise. **doubt**

### E. Waiting on

- Rebuilt page (watch `git log -- wind_page/index.html`); then re-render and redo B and D.
- FEATURES_1_9.md (8 left side, 9 right band), MODEL.md.
- Rev 5 Actions solve: check 16 again after the mound is restored.

## Pass 2 (Nov 13, 03:00-03:17Z): what landed, and does it answer the question?

- **FEATURES_1_9 checkpoint 1 (946a0398f).** "Is the right side of 9 really mown?" -> F1 measured it independently:
  no lidar height, green on Nov 2024 / 2025 / 2026 satellite out to the trees. **fine**: 9 Driver's reason stands.
  "Is the left of 8 what the integrator says?" -> right-side long grass on 8 starts 13-26 yds further right than
  mapped; fairway left edge on the Driver side is 3-7 yds narrower than mapped. Net: still Driver (0.042 even with
  roll x1.25). **fine.**
  Why-are-we-doing-this check: a 7-year fairway-edge table to 0.1 yd is more than the question needs, but it took
  minutes and it settled 8 and 9. Stop there on 1-7 unless a club is close (none is: all Driver by 0.05+).
- **16 mound evidence (ddafc786a).** F2: unmown every summer, short in December, "a stone retaining wall on its
  fairway face". That is a place you do not want to be whatever the grass height. **fine**: penal lie is right.
- **Final map (222f7ece4).** Checked the built map: mound points now carry a penal zone (priced as sand); left
  fescue edge on 16 at about 20 L. Lidar long grass kept on 10 and 16 only, from a frozen copy. **fine.**
  Open: the solve result (rev 6) and the page.
- **Frozen ground (config `condition_source`).** Roll x1.25 / x1.5: 8 Driver 0.042 / 0.028, 9 Driver 0.020 / 0.007,
  10 2-wood 0.019 then 4-wood by 0.015, 16 4-wood holds. One line on 10: "Frozen or very firm ground (drives
  running 35+ yds): 4-wood, same line". **fine**, that is the right size of answer. One nit: on the tee of 10
  (his 10th hole, or his 1st off a split start) he may not yet know how far drives are running. If he starts on
  the back nine, default to 4-wood on a frosty morning.

**[pictures] "Where is the green?"** (old build, measured from the page data)
- 8 Back / Middle: green centre is 19-21 yds outside the left edge of the picture. 11: 8-9 yds inside the right edge
  (half a green). 3, 6, 13, 18 (par 5s) and 5 (452): the picture ends before the green; 15: green centre is on the
  top edge. 1, 2, 9, 10, 16: fine.
- Verdict: **wrong** on 8 (the aim only makes sense if you can see the green), **doubt** on 11, acceptable on the
  par 5s if the button did not say "Whole hole".
- Do: widen / shift the crop on 8 and 11 so the green is in; rename the button "Tee shot" on holes where the
  green is not shown, or leave it. Do not spend more than one edit on this.
