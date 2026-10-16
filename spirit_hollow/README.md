# Spirit Hollow GC — tee and par-3 strategy

Same model as `../mozingo` (Fawcett / DECADE style), same clubs:
Driver 275 carry / 300 total / 65 wide, 2-wood 265/280/60, 4-wood 255/270/50.

`python3 spirit_hollow/build.py --stats` re-runs the confidence numbers and writes
`output/Spirit_Hollow_Strategy.pdf` (full book) and `output/Spirit_Hollow_Aim_Sheets.pdf`
(one page per hole: screenshot + star, or the green + rule box on par 3s).
Drop `--stats` to rebuild the PDFs from the last confidence run.

Holes are in `course.py`, traced from the screenshots in `screenshots/`
(holes 1-3 weren't provided; hole 9 has a back and a forward tee).

Par 3 rule (`mozingo/yardage_book.py: par3_plan`): cushion = distance / 20 yds in from
each edge, +3 water/OB, +2 trees/tall grass, +1 bunker. If both sides of an axis don't
fit on the green, the worse miss keeps its full cushion and the lesser side gives up room;
with the same trouble both sides (or none), the aim splits them — the middle.

## Review checklist (do this for every hole before trusting a pick)

Thumbnails and numeric checks don't catch tracing mistakes; these did, after the fact
(4: fairway drawn over tan grass; 18: fairway drawn under the woods; 9: creek missed;
7: approach mistaken for the green).

1. `python3 spirit_hollow/review.py out.png <holes>`: full-resolution landing zone with the
   outlines, the star, the 95% oval and every simulated ball coloured by its modelled lie.
   Any ball shown as fairway/rough that sits on tan grass, trees, a creek or a bunker in
   the photo means the outline is wrong.
2. Tan/yellow = long grass. White streaks = creek beds. Trees: trace at the trunks; the
   photos lean, so canopy and shadows over the fairway are grass.
3. Par 3 greens: trace on a contrast-boosted zoom. The green is the smooth oval, not the
   darker approach in front of it.
4. Re-run and recheck the holes you changed; then run `build.py --stats`.
