# Blind re-check of 7 back tees (2026-11-03)

An independent reviewer re-checked the back (card) tee on the 5 holes whose truth tee was corrected in 7dd920c6b,
plus 2 controls where the old truth was kept (Veenker 16, Sand Creek 1). I recorded my verdicts **before** reading
the truth files, the 7dd920c6b diff or message, ERROR_BUDGET.md "Far cap" or any CHECK.md. The verdicts were saved
to my scratchpad at 21:42 UTC; I opened the truth after that.

**Method.** I wrote my own sheets because `tees/back_tee_sheets.py` frames on and marks the truth tee. Each sheet
uses the frame from the start of the OSM hole line to the green (packages/<slug>/package.json), with no truth and no
auto tee marked. Panels: package NAIP, the other NAIP years, NIR, 1 m DEM hillshade, a DEM relief map (DEM minus a
12-yard blur), slope, lidar HAG, OSM tee boxes (cyan) and `lidar_pads.detect_pads` (magenta). An orange contour
marks where the back-set card yardage falls (yards along the hole line: tee to the next line vertex at least 60 yds
ahead, then along the line to the green centre), with pale contours at +/-10 yds. Pad check: mean DEM over r < 5 m
minus the 12-20 m ring, plus the standard deviation inside. Cards come from the package scorecard. The images
(not committed) are in the session scratchpad under `tee_recheck/`.

## Verdicts (blind)

x = lateral and along = yards from the OSM hole-line start toward the green (negative = behind the start).

| hole | set, card | my back tee (lon, lat) | x, along | yds to green | conf | evidence |
|---|---|---|---|---|---|---|
| La Nickell 18 | Blue 427 | -92.3639034, 38.9807613 | 0, -17 | 376 | 0.6 | Back end of the long OSM box (it runs -23..+22). At the 427 contour are the 17 green (OSM) and a cart-path junction under trees. There is no pad or mown box anywhere from -25 to -110. The card cannot be reached; the box back is 383, which matches White 382. |
| Eagle Bend 14 | Gold 429 | -95.3169331, 38.9198595 | -22, -48 | 425 | 0.4 | A raised, flat DEM hump (+0.47 m, std 0.03 m), the same signature as the OSM round box (+0.58 m, 0.05 m), sits on the 429 contour beside the tree line. There is a faint mown or tan patch in NAIP 2021 / 2023, but no OSM box and no detected pad. Alternative (conf ~0.35): the OSM round box at 0, +4 (~380 yds). |
| Eagle Bend 18 | Gold 547 | -95.3222907, 38.9177465 | -2, +1 | 548 | 0.65 | DEM pad (+0.68 m) at the OSM hole-line start, at the end of the cart path, on the 547 contour. It has no OSM box (the OSM boxes are at 495-513). |
| Buffalo Dunes 11 | Blue 423 | -100.8730089, 37.8772946 | +1, -2 | 381 | 0.5 | Back of the OSM box at the line start (-6..+30). The 423 contour falls on hole 10's green and its trees, behind a new (2023) cart path, so there is no candidate. Card -42. |
| Buffalo Dunes 6 | Blue 400 | -100.8711243, 37.8737255 | -1.5, -3 | 353 | 0.5 | Back of the OSM box at the line start (-6..+13). Behind it are native rough and then cropland, with no pad. The long box at -48..-87, -11..-42 is **hole 12's tee**: the OSM hole 12 line starts at its east end and runs away from hole 6. Card -47. |
| Veenker 16 (control) | Blue 544 | -93.6559984, 42.0408429 | -17, -86 | 556 | 0.5 | Mown rectangle in NAIP 2021 that matches a detected lidar pad beside the cart path near the 15 green. It looks scrubby in 2023. The OSM box at the line start (~480) matches Gold 485. |
| Sand Creek 1 (control) | Championship 474 | -97.3652032, 38.0214016 | +40.5, -87 | 482 | 0.8 | Clearly groomed OSM box with a mown surround and a lidar pad, right of the line by the cart path, on the card contour. |

## Comparison with truth_sets_v2 / v1 truth (done after the verdicts)

| hole | truth tee (x, along; yds) | truth method | mine vs truth: distance apart | yds to green, mine / truth | verdict |
|---|---|---|---|---|---|
| La Nickell 18 | -3.5, -23.4; 383 | hand | **7 yds** | 376 / 383 | **agree** (both: back of the mapped box, card unreachable) |
| Eagle Bend 14 | 0.2, -2.6; 381 | hand | **51 yds** | 425 / 381 | **unsure, lean disagree**. Truth is my alternative (the round box). My pick is a DEM hump the corrector called "flat DEM, no lidar pad". I measure it raised +0.47 m and flat, like the box. Neither of us found a visible tee in the photos. |
| Eagle Bend 18 | -0.2, +0.8; 549 | hand | **2 yds** | 548 / 549 | **agree** |
| Buffalo Dunes 11 | 0.6, -4.3; 383 | hand | **2 yds** | 381 / 383 | **agree** |
| Buffalo Dunes 6 | -82.3, -39.8; 391 | hand | **89 yds** | 353 / 391 | **disagree**. Truth is the far (west) corner of hole 12's tee box, 82 yds left of hole 6's line. I read that box as hole 12's (OSM hole 12 starts at its east end), and the west corner as 12's front, not a hole 6 tee. I would put the hole 6 Blue on the back of its own line-start box (~353, card -47). Confidence is only medium: a shared tee there would explain the card better. |
| Veenker 16 (control) | -17.5, -81.6; 551 | v1 truth (kept) | **4 yds** | 556 / 551 | **agree** |
| Sand Creek 1 (control) | -1.4, -91.1; 480 | estimated: pad 420 moved +54 yds along the line (kept) | **42 yds** (lateral) | 482 / 480 | **disagree on position, agree on length**. The truth point is a walk-back on the line at the cart-path / bridge corner. There is a real back box 42 yds right of it at the same yardage (OSM tee + lidar pad, about -97.36520, 38.02140). |

**Summary.** I agree on 3 of the 5 corrections (La Nickell 18, Eagle Bend 18, Buffalo Dunes 11), disagree on
1 (Buffalo Dunes 6) and am unsure on 1 (Eagle Bend 14). On the controls I agree on Veenker 16, and on Sand Creek 1 I
agree on the length but not the position. For the far-cap question: on La Nickell 18, Buffalo Dunes 11 and
Buffalo Dunes 6 I also found nothing near the card, so "the back tee is the back mapped box, 40-50 yds short of the
card" holds up independently on those three. Buffalo Dunes 6's truth, though, is on another hole's box rather than
its own. Eagle Bend 14 is the one hole where a card-length candidate (weak DEM evidence only) exists and the
correction removed it.

Not verified: no ground photos or course tee maps. The 1 m DEM is smooth here, so pads show as soft humps, and the
pad evidence is relative. NAIP 2021 is offset ~20 yds from 2023 at Buffalo Dunes, and the "yds to green" model
(tee to the line vertex, then along the line) can differ from the card's measuring line by 5-10 yds.
