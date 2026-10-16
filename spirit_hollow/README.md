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
