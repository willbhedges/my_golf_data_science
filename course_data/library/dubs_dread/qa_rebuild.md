# Dub's Dread GC: rebuild QA, mapper wave 2b (2026-11-03)

**Verdict: PUBLISH.** The card, the hole 4 routing, the hole 12 par and the tee fixes are still in, and the mapper
layers apply cleanly (15 recovery adds on 5 holes, 0 tees moved). The one wide aim (15 Back, Driver -60) carries a
CHECK and is a sensible cut over the dogleg. The tee left uncertain on 9 Championship (21 yds short) is unchanged.

Page checked: `course_data/library/dubs_dread/page.html`, GitHub Actions run 41539963949 (built 2026-11-02T23:54Z),
mapper layers `course_data/mapper/dubs_dread/`. Both solved sets (Championship 7,230, Back 6,687, par 72) were run
through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems, no console errors. I looked at every phone
hole picture.

## Checks

| check | result |
|---|---|
| Card / pars (`card_golfify.json`) | par 72; page yardage = card on all 36 hole-sets; measured within 6 yds except 9 Championship (397 / 418, build warning) |
| Earlier review fixes | 4 = par 3, 216 (218 measured); 12 = par 5, 547; 5 = 377 / 382; 3 / 6 / 7 / 13 = 441 / 468 / 550 / 421 |
| Mapper layers | recovery adds on 7, 9, 10, 15, 18 are in the landing stats; native 249 yd2 on 2 is unchanged |
| Aims past ±40 | 15 Back Driver -60 (CHECK printed). On the bound: 6 Championship Driver -40, 12 Back 2-wood -40 |

## Holes

| hole | Championship | Back | note |
|---|---|---|---|
| 1-5, 8, 10-12, 14, 16-18 | OK | OK | 1 Championship Driver +20.5 toward the dogleg, trees 28% (marginal, as before) |
| 6 | OK (on the bound) | OK | Driver -40 to the left edge at the bend, 34% fairway / 19% trees; Back 4-wood -20 |
| 7 | OK | OK (CHECK) | Back tee_axis 3 yds off the box, 540 / 535 |
| 9 | OK (uncertain, 21 short) | OK | as reviewed |
| 12 | OK | OK (on the bound) | Back 2-wood -40 up the left side of the bend, 49% fairway, 9% water |
| 13 | OK (CHECK) | OK | Championship on a lidar pad 23 yds behind the box, 421 / 420 |
| 15 | OK | OK (CHECK) | Back Driver -60 carries the dogleg-left corner trees to the fairway 51 yds short of the green (49% fairway, 13% trees). Aggressive but the line is real |

## Next fix

None blocking. 9 Championship still needs a back-tee point about 20 yds behind the hole-way start, if a mapper can
see it.
