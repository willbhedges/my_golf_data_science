# Creekmoor: rebuild QA, second pass (2026-11-02)

**Verdict: PUBLISH.** Hole 10 is now the real 482-yd par 4 off the supplement way, and every other hole is as in the
first pass.

Page checked: `course_data/library/creekmoor/page.html`, built 2026-11-02T05:57Z (GitHub Actions run 41392580512).
Both solved sets (Black, Green) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems. I
looked at every phone hole picture. Card: golfify, Black 7,406 / Green 6,806, par 72. The page yardage equals the card
on all 36 hole-sets. The measured length is within 2 yds of the card everywhere except 18 (Black 536 / 541, Green
503 / 508). The build no longer drops way 1553245446; its only warning is about 2 practice tee boxes.

## First-pass fixes

| fix | applied? |
|---|---|
| 10: real hole from supplement way 1553245446 (tee 38.827625, -94.471104; green 38.828278, -94.466313; 482 / 448) | **yes.** The hole line runs exactly through those points. The Black tee is OSM box 1490350641 (481 measured), Green 449. The picture shows the tee boxes, the fairway with its bunkers and the green, not the range. |
| 12 / 17 per-set yards (Black 240 / 214, Green 187 / 184) | **yes.** Review tees snapped 0-1 yds to OSM boxes; measured 239 / 215 (Black), 186 / 185 (Green). |

## Holes

| hole | Black | Green | note |
|---|---|---|---|
| 1-9, 11, 13, 15, 16 | OK | OK | OSM maps no fairways here, so the landings read "fairway 0%"; the pictures show them on fairway |
| 10 | **fixed** | **fixed** | Black Driver aim 12 left, sand 16% (the fairway bunker pair at about 300). Plausible on a 482-yd par 4 |
| 12, 17 | OK | OK | par 3s, boxes on the green |
| 14 | OK (marginal) | OK (marginal) | Driver aim 28 left toward the fairway bunkers (Black sand 14%). Model choice, as before |
| 18 | OK (marginal) | OK | Black Driver by the centre-line fairway bunker (sand 13%). Model choice |

## Remaining (optional)

None blocking. The "fairway 0%" readings are an OSM gap (no fairway polygons on this course), not a page fault.
