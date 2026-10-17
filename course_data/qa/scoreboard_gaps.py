"""Hand-written part of SCOREBOARD.md: table notes and the ranked gap list (QA lead's judgement, from the
per-hole rows). Edit, then `python3 course_data/qa/scoreboard.py --md-only`."""

NOTES = [
    "Spirit Hollow is scored on 16 tee shots: 14 from the Black plan (holes 2 and 9 -> 2F / 9F) plus 2B and 9B from a "
    "Gold-tee product plan, because those screenshots (and the hand map) play from the Gold box.",
    "Mozingo's truth is its hand map run through the same quick decision as the product, so a disagreement there is "
    "map error only; Spirit Hollow's truth is the published Bayesian final_decision.json (map + model-settings "
    "error; the 'hand map, quick' column separates them).",
    "Veenker has no hand map: agreement, regret and geometry are n/a until one exists (gap 6).",
    "Geometry columns need a georeferenced hand map, which only Spirit Hollow has (hand_zones_ll.json).",
]

GAPS = [
    "Path to the 80% bar on Spirit Hollow (13/16; today 9/16 vs the refreshed final_decision.json): gaps 1-3 below "
    "are worth about +4 to +5 holes together, and the quick-mode ceiling (hand map through the product's own "
    "decision) is 13/16, so 1-3 are enough without changing the decision mode.",
    "",
    "1. **Irons are never offered on lay-up holes (product / platform).** The package carries no `irons` flag on any "
    "hole (course.py sets it on 11 and 13), and `decide.clubs_for` only adds Long / Mid iron when the hole has it. "
    "Hole 11 (creek across the fairway): truth and the hand map both say Long iron; the product can only say "
    "4-wood - **the largest regret on the board, 0.22 strokes**. Fix: offer irons whenever a water / OB / tree "
    "band crosses the line of play inside driver range (or always; it costs ~40% more sims). Expected gain: "
    "**+1 hole** (11), and it removes the worst regret.",
    "2. **Trees and long grass in the landing corridor (vision).** Map error alone: the product agrees with the hand "
    "map run through the *same* quick decision on only 7/16 Spirit Hollow and 10/14 Mozingo tee shots. Corridor "
    "IoU on Spirit Hollow: trees 0.27, long grass 0.15 (bar 0.6; one hole passes each). Misses that trace to it: "
    "SH 18 (trees IoU 0.07: Driver vs 2-wood), 6 (trees / long grass 0.0: Driver vs 2-wood), 9B (Driver vs "
    "2-wood); Mozingo 14 (4-wood vs Driver, 0.14 strokes) and 18. Expected gain: **+2 to +4 holes over both "
    "courses**. Owner: vision_any v2 long grass / tree edges and the open segmentation model (in flight) - merge "
    "into the package only when these IoU columns move.",
    "3. **Tee boxes 20-30 yds off** where 18Birdies' marker sits on a box behind the Black one (tee error 1: 26, "
    "16: 26, 17: 29, 14: 22, 2B: 29 yds; 8/16 within 10 yds). A 25-yd tee error moves the whole landing corridor: "
    "1 (Driver CHECK at -40 vs 4-wood) and 16 (4-wood vs 2-wood) follow from it. Expected gain: **+1 to +2 "
    "holes**. Owner: tees (joint assignment takes the box behind when two boxes hold similar yardage; lidar pad + "
    "card order + the golfer's app tee when known).",
    "4. **Decision mode (quick point estimate vs the published Bayesian pick).** On the perfect map, quick mode "
    "matches final_decision.json on 13/16 (10, 14, 17 differ, all margins < 0.02). Scoring the product's full "
    "Bayesian mode (plan.py default, `decide.full_hole`, minutes per hole on Actions) would remove this. Expected "
    "gain: **+1 hole** (mostly via same-or-tie already).",
    "5. **Water and OB corridor geometry** (water IoU 0.32, 2/10 holes pass; OB 0.12, 0/4: creek buffers narrow, OB "
    "from the course boundary, not lot lines). Expected gain: **+0 to +1 hole** (10, 2F, 6 sit on water/OB edges). "
    "Owner: platform water rule + ob/ (OB inference, in flight).",
    "6. **Package hygiene that can flip a pick on a new course**: Veenker tees 7 (Blue) inside OB and 12 (Blue) in a "
    "bunker since the tee rebuild; zones vs zones_ll drift (SH 9/10/11, Veenker 3/7/8/15/16); self-intersecting "
    "polygons on all three courses; forward-tee par-3 lengths 15-38% over the card. 0 holes on the scored courses, "
    "wrong-answer risk on new ones. Owner: platform / tees.",
    "7. **No truth for Veenker (or any third course).** The bar is measured on 30 tee shots from two courses, one of "
    "which (Mozingo) tuned vision thresholds. A golfer's 18Birdies screenshots + picks for Veenker would make this "
    "a generalisation test. 0 holes directly; it is what makes the other numbers trustworthy.",
    "8. **Stale deliverables.** Every `packages/<slug>/out/` (book, wind page, decision.json) predates the 00:00-00:44 "
    "package rebuilds; the scoreboard re-runs the decision itself, but what a golfer opens is older. Re-run the "
    "plan_course requests after each package rebuild. 0 holes; a delivery gap.",
]
