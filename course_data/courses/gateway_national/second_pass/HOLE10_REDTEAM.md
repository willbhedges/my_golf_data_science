# Gateway National, hole 10: red-team of "go at the green" (Nov 13 2026)

Independent check, written to break the conclusion. Map: the working tree's published map (b) (channel beside the
green at true width, the band between it and the right fairway priced as penalty, tall grass left and behind as
penalty with relief). Calm, 43.6 F unless stated. Nothing in the map, config, v2 outputs or page was edited.

## Verdict

**From the Back (271) and Middle (251) tees, GO survives everything I could throw at it.** The smallest margin over
the best lay-up that I could produce with a defensible assumption is +0.19 strokes (Back) and the usual figure is
+0.25 to +0.43. From the **Tips (317) and Champions (315) the green is out of reach** (0 % of balls on it with any
club), so "go" does not exist there: the tee shot is a position shot to the right fairway, and wood against long iron
is a near tie (0.06-0.08) that flips to the long iron with a modest change in spread. From the Forward tee (202) the
long iron is the club that reaches the green.

What flips Back / Middle, and how plausible:

| assumption pushed | Back: go minus best lay-up | flips at | plausible? |
|---|---|---|---|
| as solved (engine valuation) | +0.30 | - | - |
| explicit next shot (short side, drop position, pitch back across), both options | +0.43 | - | makes the lay-up worse, not the go (below) |
| explicit next shot charged to the go only, lay-up left on the table value (most hostile mix) | +0.27 | - | deliberately one-sided |
| woods' sideways spread wider, irons as stated | +0.23 (x1.15), +0.18 (x1.3), +0.12 (x1.5), +0.04 (x2.0) | **x2.3** (engine value); beyond x3 (explicit) | x1.3-1.5 is believable for a cold first swing; x2.3 is a 150-yd-wide pattern, not believable |
| every club wider and longer / shorter together | +0.19 (x1.3), +0.15 (x1.5), +0.12 (x2.0), +0.13 (x2.5) | never | the lay-up gets worse too |
| long / short spread only x1.5 / x2 | +0.24 / +0.19 | never tested beyond | - |
| mishit share doubled | +0.26 | - | - |
| ground: soft (roll x0.5) / firm x1.25 / frozen x1.5 / x2.0 | +0.33 / +0.28 / +0.26 / +0.19 | no | club moves to the 4-wood from x1.25 |
| tall grass played as a lost ball (re-tee, hitting 3) instead of a drop | +0.28 | no | club moves to the 4-wood |
| flag position (centre / right / left / back / front) | +0.30 / +0.24 / +0.34 / +0.25 / +0.25 | no | front flag: 4-wood |
| forecast wind, Sat 5 (gust 9) from the right, Sun 4 (gust 6.5) from behind-left | +0.31 / +0.32 | no | Sun: 4-wood |
| any 10 mph direction, aim adjusted | +0.22 to +0.31 | no | - |
| 10 mph from the left and he does NOT adjust the aim | about 0.00 | **yes** | not in the forecast (Sat is from the right, Sun 4 mph) |
| each penalty ball costs more than priced | - | **+1.6 strokes extra per penalty ball** (18.5 % of balls) | no: that would be 5.5 strokes after the tee shot |
| share of tee balls in penalty | - | about 40 % (HOLE10.md, confirmed: 0.30 / 1.47 added to 18.5 %) | no aim or spread I tried exceeds 31 % |

Middle is the more fragile of the two: woods' spread x1.5 leaves +0.12, x2.0 gives -0.03 (explicit valuation; on the
engine valuation the break-even is about x1.6-1.7, estimated from the same runs, not run separately). Frozen ground
(roll x1.5) leaves Middle at +0.24.

Honest reading of the dispersion break-even: the model gives the 2-wood a 95 % sideways width of 65 yds (sigma 16 yds,
about 3.5 degrees) and the 4-wood 54 yds. I did not re-derive these from the MODEL.md sources in the time available.
For Back the conclusion needs the woods more than twice as wide as the model with the irons unchanged. For the back
tees it needs only x1.3.

## What the engine ignores, priced explicitly (assumption 1)

Crude model, stated in full: from every 1-yd cell within 150 yds of the flag the next shot is played at the best of
five targets (flag, 4 and 8 yds further from the right edge, green centre, centre + 4). Error is normal: along the
shot 20 / 17 / 14 / 11 / 9 % of the distance at 5 / 20 / 40 / 70 / 110 yds, sideways about half of that; x1.35 from
rough, x1.6 from sand, x1.2 when the line crosses penalty ground; 3 / 6 / 10 % of shots from fairway / rough / sand
are chunked or thinned (50-80 % or 100-160 % of the distance). A shot that finishes in penalty ground costs a stroke
and is replayed from where it was hit. A tee ball in penalty ground is dropped where its line from the tee last
crossed the edge, in rough, and plays the same explicit shot. Only the difference between this and the same shots with
the penalty ground painted as rough is added to the engine's value, so the engine's level and its value of distance
are kept. Not modelled: slope of the green, the exact two-club-length drop spot, stance on the bank, a chip that must
run through rather than fly, recursion beyond the third shot.

Back tee, 2-wood aimed 26 yds left of the tee line (7.5 yds left of the green centre):

| where the tee ball is | share | engine value (strokes after the tee shot) | explicit |
|---|---|---|---|
| on the green | 30 % | 1.98 | 1.98 |
| dry, off the green | 51.5 % | 2.74 | 2.77 |
| penalty | 18.5 % | 3.95 | 4.07 |

* Two thirds of the 2-wood's penalty balls (half of the 4-wood's) drop on the far side from the green and pitch back
  across; the median drop is 37 yds from the hole and 79 % are more than 30 yds out, because the band is entered at
  its near end (226 yds). This is the real cost Will is pointing at, and it is worth 0.12 a ball, 0.02 a hole.
* Short-siding for dry balls costs 0.03 a ball: with the flag as target 3.7 % of the chips finish in penalty, aimed
  4 yds away 0.7 %.
* **The lay-up is hurt more than the go**: from 64-90 yds in the right fairway the wedge crosses the same ground to
  a 19-yd-wide green; aimed at the flag 9-10 % of wedges finish in penalty, aimed 4 yds away 4-5 %, 8 yds away
  about 3 % with half of them missing the green. Lay-up value after the tee shot 3.03 (table) -> 3.19 (explicit).
  That 4-5 % may be too harsh for him; with the lay-up left at the table value the margin is still +0.27.
* Right flag (5 yds from the right edge): go +0.24 (engine) / +0.38 (explicit). Second-shot spread x1.5: +0.49.

## Best lay-up found (assumption 2)

Every club from PW to Driver was swept over aims 60 L to 60 R of the tee line (9-iron 150 and PW 138 added in memory).

| lay-up, Back tee | aim vs tee line | aim vs the tee-to-green line at the landing distance | leaves | fairway / penalty | strokes, engine | explicit |
|---|---|---|---|---|---|---|
| **Long iron** | 3 R to 10 R | 18 to 25 yds right | 64-67 | 9 % in the 198-yd sand, 0.6-1.4 % penalty | **4.04** | **4.20** |
| **Mid iron** (practical best: no sand in range) | 4 L to 0 | 9 to 13 yds right | 88 | 97 % fairway, 0.4 % penalty | 4.07 | 4.21 |
| 8-iron (a full-swing number) | 3 L | 9 right | 111 | 100 % fairway | 4.15 | 4.29 |
| 9-iron / PW | 4 L / 4 L | - | 124 / 135 | - | 4.20 / 4.25 | 4.31 / 4.37 |

* Leaving a full-swing number instead of 64-88 does not help: 8-iron to 111 is 0.08-0.11 worse. If 30-95 yd shots
  are made 40 % wilder (cold half wedges), the mid iron to 88 becomes the best lay-up at 4.25 and go wins by 0.47.
* There is no lay-up short or short-left of the green: that mown ground (228-264 yds, 4-28 yds left of the green
  centre) starts beyond a 222-yd carry, so only the clubs that reach the green reach it. The 4-wood aimed there is
  the go option itself.
* No line takes the trouble out of play for a wood: the lowest penalty share at any aim is about 14 % (4-wood).
* Best non-go option, priced: **mid iron, 0-4 yds left of the tee line, leaves 88: 4.07-4.21, against 3.74-3.77**.

## Penalty accounting (assumption 5)

At the Back pick (2-wood 26 L): 18.5 % penalty = 14.0 % right of the green centre (channel and band), 0.8 % short-left,
3.7 % tall grass on the left, 0.0 % behind the green. So 1 penalty ball in 5 is tall grass. Priced as a lost ball
(hitting 3 from the tee, 4.85 strokes after the tee shot) the 2-wood goes 3.774 -> 3.797, the 4-wood (1.7 % tall grass)
ties it at 3.797 and go still wins by 0.28 / 0.41. If the tall grass is not staked, take the 4-wood.

## Outcome spread (assumption 6; objective unchanged)

20,000 holes each, explicit next shot, then a crude conversion of the remaining expected strokes to whole strokes
(putts from Tour make-rates x0.92; missed greens: 4-10 % chance of one extra). The 6+ column for the lay-ups is
probably too high (it comes from the wedge penalty rate above); the means are 0.03-0.06 above the solver's.

| Back tee, centre flag | mean | 2 | 3 or better | 4 | 5 | 6+ | tee ball in penalty | tee ball on green |
|---|---|---|---|---|---|---|---|---|
| 2-wood 26 L | 3.83 | 4.6 % | 42 % | 35 % | 17 % | 5.5 % | 19 % | 29 % |
| 4-wood 27 L | 3.83 | 3.4 % | 39 % | 41 % | 16 % | 4.3 % | 15 % | 23 % |
| Long iron 3 R | 4.23 | 0 | 14 % | 60 % | 19 % | 8 % | 1 % | 0 |
| Mid iron 4 L | 4.26 | 0 | 12 % | 60 % | 20 % | 8.5 % | 0.4 % | 0 |
| right flag: 2-wood / 4-wood / mid iron | 3.95 / 3.96 / 4.32 | | 36 / 33 / 9 % | 39 / 43 / 61 % | 18 / 18 / 21 % | 7 / 6 / 9 % | | |

Go: about three times the birdies, bogey-or-worse about 22 % against 27 % (or against roughly 20 % if the lay-up's
wedge is as safe as the table says). Going for it does not raise the chance of a big number by more than 1-2 points
on any version; the 4-wood has the tighter spread of the two woods at the same mean.

## Wind (assumption 7), Back, aims re-solved

| cell | pick, aim vs tee line | go minus lay-up (engine / explicit) |
|---|---|---|
| Sat 5 mph NNW (84 deg, from the right) | 2-wood 18 L | +0.31 / +0.43 |
| Sat gust 9 | 2-wood 12 L | +0.31 / +0.43 |
| Sun 4 mph ESE (behind, slightly from the left) | 4-wood 30 L | +0.32 / +0.45 |
| Sun gust 6.5 / 8 | 4-wood 31-33 L | +0.32 / +0.44 |
| 10 mph head / tail / from right / from left | Driver 26 L / 4-wood 26 L / 2-wood 10 L / 2-wood 42 L | +0.22 / +0.27 / +0.30 / +0.30 |

Sunday's helping wind makes the 2-wood too long: 2-wood at the calm aim is 3.86, the 4-wood 3.73. A 10 mph wind from
the left with the calm aim kept costs 0.27-0.32 and brings go level with the lay-up; with the aim moved it costs
nothing. No forecast cell has wind from the left above 4 mph.

## Roll and temperature (assumption 4)

Soft x0.5: 2-wood, +0.33. Firm x1.25 and frozen x1.5: 4-wood 27-28 L, +0.28 / +0.26. Roll x2.0: 4-wood 29 L, +0.19,
green share falls to 20 %. No ball finishes in the tall grass behind the green at stated roll (2-wood 90th
percentile 279 yds, the grass starts at 299); the engine keeps the tee's per-club elevation numbers (2-wood carry
+0.9 yd, roll x1.04), not re-checked. 35 F: 2-wood, +0.31; 50 F: 4-wood, +0.30.

## Every tee set (assumption 8)

The Tips, Champions, Middle and Forward are modelled as the Back tee moved straight back or forward along the tee
line (+46, +44, -20, -69 yds), as the page's offset grids do; the true boxes may sit off that line. The lead's
own-box Middle solve gave 4-wood 21 L, go by 0.24: same answer. 8,000 swings, 1-yd aims: aims +/-1 yd, strokes
+/-0.01. Aims are yds from the tee line of that tee (green centre is 18.5 L of it).

**The Tips, 317 yds: green not reachable (0.0 % on the green with any club; Driver 0.1 %).**

| club | aim | strokes engine / explicit | penalty | leaves |
|---|---|---|---|---|
| 4-wood, right fairway | 8 R (23 right of the tee-to-green line) | 4.07 / 4.24 | 2.9 % | 64 |
| 2-wood, right fairway | 11 R | 4.07 / 4.22 | 7.8 % | 58 |
| Driver | 17 R | 4.12 / 4.26 | 17.6 % | 49 |
| Long iron | 0 to 2 L (10-12 right of the tee-to-green line) | 4.14 / 4.29 | 0.7 % | 106 |
| Mid iron / 8-iron | 1 L | 4.25 / 4.40 (engine) | 0.3 % / 0.1 % | 134 / 157 |

Wood over long iron: +0.07 (engine), +0.05-0.065 (explicit). Woods' spread x1.3: long iron by 0.01; x1.5: long iron
by 0.07. Frozen ground: 4-wood by 0.04. 35 F: +0.065. Score spread: 2-wood 14 % birdie / 55.5 % par / 20.5 % bogey /
10 % worse; long iron 10 / 58 / 22 / 10. **Pick: 4-wood 8 R** (same strokes as the 2-wood with 3 % rather than 8 %
penalty); the long iron is a fair alternative, 0.07 behind.

**Champions, 315 yds: the same.** 4-wood 8 R 4.06 / 4.22 (3.0 % penalty, leaves 63); 2-wood 12 R 4.07 / 4.22 (8.4 %);
long iron 0 to 3 L 4.14 / 4.28 (leaves 104). Wood over long iron +0.06 to +0.08; flips at woods' spread x1.3.

**Back, 271 yds: go.** 2-wood 26 L 3.74 / 3.77 (18.5 % penalty, 30 % on the green); 4-wood 27 L 3.76 / 3.79 (15.1 %,
23 %); Driver 28 L 3.97; long iron 3-10 R 4.04 / 4.20. Go by +0.30 / +0.43. 2-wood and 4-wood are inside 0.02: the
4-wood whenever the ground is firm, the wind helps, it is 50 F or the tall grass is not staked.

**Middle, 251 yds: go, 4-wood.** 4-wood 25-26 L 3.70 / 3.72 (14-15 % penalty, 31 % on the green); 2-wood 3.94 (23 %);
Driver 4.32 (47 %); long iron 13-14 R 3.94 / 4.09 (leaves 51, 3 % penalty). Go by +0.25 / +0.37. Flips at woods'
spread about x1.6-1.9. Score spread: 44 % birdie or better / 38 / 14 / 4 against 17 / 59 / 17 / 7.

**Forward, 202 yds: long iron at the green**, 25 L, 3.55 / 3.56 (40 % on the green, 8.9 % penalty); mid iron 27 L
3.69; best club short of the green is the 8-iron 9-11 R, 3.92 / 4.05. The woods are 0.6-0.8 worse (too long).

Does the answer change from farther back? **Yes.** At 315-317 there is no go; the choice is which club to the right
fairway, and it is close. Everything in the page's Back line (aim left half of the green) is wrong from those boxes:
the calm Back aim played from the Tips is 5.0 strokes with 60 % penalty.

## What survives, what does not

* Survives: go from Back and Middle; the published aim (left half of the green, 2-wood 26 L of the Back tee line =
  7.5 yds left of the green centre); the 4-wood as the co-pick.
* Does not survive: "2-wood" as a flat statement (4-wood is equal or better in 6 of the 10 conditions tested); any
  suggestion that the Back answer carries to the Tips / Champions.
* Crude and unverified here: my second-shot error sizes; the whole-stroke conversion; the tee positions of the other
  sets; the dispersion sources; the band right of the channel is kept as penalty (if it is mown, HOLE10.md has go
  by 0.41 and the aim 6 yds further right).

## Recommended page line (hole 10)

> **Back (271) / Middle (251):** wood at the green, start it at the left half of the green (2-wood from the Back
> box, 4-wood from the Middle box; 4-wood from the Back box if the ground is firm or the wind is helping). Miss
> left of the flag, never right. Worth about 0.3 a round over the iron off the tee.
> **Tips / Champions (315+):** the green is out of reach. 4-wood at the right-hand fairway, 8 yds right of the tee
> line, leaves about 65. Long iron on the same fairway (leaves 105) costs 0.07.
> **Forward (202):** long iron at the left half of the green.

Scripts and raw output (scratch, not committed):
`/tmp/claude-0/-home-user-my-golf-data-science/3c0900e1-ef71-58c8-8d72-7f70a9ca40ad/scratchpad/hole10_redteam/`
(`lib.py`, `dist.py`, `t2.py`, `t3.py`, `t4.py`, `outA.txt` ... `outS.txt`).
