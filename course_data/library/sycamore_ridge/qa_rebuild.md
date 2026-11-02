# Sycamore Ridge Golf Club (Spring Hill KS): rebuild QA, third pass (2026-11-02)

**Verdict: NEEDS FIX (wide aim on 18, pipeline).** The hole 1 tee fix is in: Black 468 / 467 and Blue 444 / 445,
both from OSM boxes at the top of the hole line. But hole 18 now prints Driver **58.5 yds right** on both sets, with
no wide-aim CHECK (Blue has no CHECK at all).

Page checked: `course_data/library/sycamore_ridge/page.html`, GitHub Actions run 41479479995 (committed 18:57Z). Both
solved sets (Black 7,081, Blue 6,465, par 72) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page
problems. I looked at every phone hole picture, and at the desktop picture of 18.

## Second-pass fixes

| fix | applied? |
|---|---|
| Card hole 1 (OSM 10): Black on the 463 box, Blue off the blue tag (yards Black 467 / Blue 445) | **yes.** Black: on an OSM box, 468 measured / 467 card. Blue: on an OSM box, 444 / 445 (the untagged box, not the tag 50 yds short). Pick Driver +8 / +12, fairway 65-68% |
| Optional card 9 (OSM 18) back boxes | Black **yes** (on a box, 466 / 466). Blue still on the tagged box, 408 / 416 (CHECK on the page) |
| Card / renumber / 5 as par 4 | still right: pars 4 5 4 3 4 4 5 3 4 / 4 5 3 4 3 5 4 3 5 = 72; page yardage = card on all 36 |

## Checks

| check | result |
|---|---|
| Mapper layers / native cards | not used here (no `agent_layers` in the request): `native.json` has 0 items, as expected |
| Water filter | ran; no vision water. Water only at the 3 / 13 / 18 ponds (3 Black 8%, 18 1%) |
| Aims past ±40 | **18 Black and Blue Driver +58.5**; Blue 2 Driver -40.0 on the bound |

## Holes

| hole | Black | Blue | note |
|---|---|---|---|
| **1** | **fixed** | **fixed** | see above |
| 2-8, 10-12, 14-17 | OK | OK | yardage = card ±6 |
| 2 | OK | OK (marginal) | Blue Driver -40 on the bound, trees 15% |
| 9 | OK | minor (CHECK) | Blue tagged box 8 short |
| 13 | OK (CHECK) | OK (marginal) | Black tee_axis 7 yds off; Blue Driver +20.5 into the greenside bunkers (sand 20%). Model choice, as before |
| **18** | **wide aim** (CHECK for tee only) | **wide aim, no CHECK** | 525 / 479 par 5, green 224 yds right of the tee line at 417: a hard dog-leg right. Driver +58.5 crosses the pond corner to the fairway past it (fairway 58%, water 1%). The line is plausible, but the landing oval sits off the right edge of the hole picture, and the golfer is not asked to confirm it |

## Next fix

1. **Pipeline (blocks the publish):** carry the wide-aim CHECK (`product/decide.py wide_aim_flags`) into the library
   page / auto-map QA. Then rebuild; 18 becomes a CHECK. PUBLISH after that.
2. Optional: Blue tee on card 9 (OSM 18) onto the untagged 416 box.
