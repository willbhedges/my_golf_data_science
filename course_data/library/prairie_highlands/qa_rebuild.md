# Prairie Highlands GC (Olathe KS): rebuild QA (2026-11-02)

**Verdict: NEEDS FIX (wide aim on Blue 10, pipeline).** The build now completes, and the Blue 11 tee fix is in. All 36
hole-sets match the card. But Blue 10's calm book line is Driver **60 yds right**, printed with no CHECK.

Page checked: `course_data/library/prairie_highlands/page.html`, GitHub Actions run 41479479995 (committed 18:55Z).
Both solved sets (Black 7,066, Blue 6,481, par 72) were run through `qa_page.js`: 18 holes each, phone and desktop,
0 page problems. I looked at every phone hole picture, and at the desktop pictures of 10.

## Review fixes

| fix (review.md, 2026-10-30) | applied? |
|---|---|
| `card_review.json` (golfify, par 72) | **yes.** Pars 4 4 4 5 3 4 4 3 5 / 4 4 5 4 3 5 3 4 4; page = card on all 36 hole-sets |
| Blue 11 off the lidar pad in the trees, onto the tee strip past the cart path (366 / 367) | **yes.** On an OSM box, 367 / 367; Driver on the line, fairway 70% |
| Black 11 (uncertain) | now 394 / 400 (tee_axis, 6 yds off the box; was 388). CHECK on the page |

## Checks

| check | result |
|---|---|
| Yardage | measured within 6 yds of the card everywhere |
| Mapper / native cards | not used; `native.json` empty, as expected |
| Water filter | ran; 766 m2 dropped (379 on roads). Water in the stats is the creek / ponds on 6, 7, 10, 15 |
| Aims past ±40 | **Blue 10 Driver +60** (calm book), no CHECK |

## Holes

| hole | Black | Blue | note |
|---|---|---|---|
| 1-5, 7-9, 12-16, 18 | OK | OK | tees on OSM boxes |
| 6 | OK (marginal) | OK | Black Driver runs through the fairway end into rough at 325 (water 12% in the calm pattern). As reviewed |
| 10 | OK | **wide aim, no CHECK** | 357-yd dog-leg right over the creek. The forecast play is Long iron, short of the creek (fine). But the note's book line is "Driver ... Aim 60.0 yds right", over the creek and trees (rough, water 11-12%, 16% trouble). Not flagged |
| 11 | OK (CHECK) | **fixed** | |
| 17 | OK (CHECK) | OK (marginal) | Black Driver -6 into the greenside bunker on a 340 (the page flags it); Blue -16.5, sand 17-23%. Model choice, as reviewed |

## Next fix

1. **Pipeline (blocks the publish):** wide-aim CHECK on library pages (see gustin/qa_rebuild.md). Rebuild; PUBLISH if
   Blue 10 comes back as a CHECK.
