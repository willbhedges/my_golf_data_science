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
    "1. **Decision mode: the product's quick point estimate cannot reach the published plan even on a perfect map.** "
    "The Spirit Hollow hand map itself, run through the product's quick decision, picks final_decision.json's club "
    "on only 9/16 tee shots (5, 6, 11, 14, 16, 17, 18 differ; most are < 0.02-stroke calls the Bayesian run "
    "settles differently). So the 80% bar vs final_decision.json is out of reach while the golfer's plan comes "
    "from `--quick`. Fix: produce the printed decision with plan.py's full Bayesian mode (`decide.full_hole`, "
    "S=32-64 draws; it is the plan.py default and runs on Actions in minutes per hole in parallel, like "
    "plan_spirit_hollow.yml) and score that. Expected gain: **+2 to +4 holes on Spirit Hollow** (removes the "
    "settings error; the remaining gap is map error). Owner: product.",
    "2. **Trees and long grass in the landing corridor (vision).** Map error alone: the product agrees with the "
    "hand map run through the *same* quick decision on only 7/16 Spirit Hollow and 10/14 Mozingo tee shots. "
    "Corridor IoU on Spirit Hollow: trees 0.27, long grass 0.15 (bar 0.6; 1 hole of 15-16 passes). Clear cases: "
    "SH 10 (trees IoU 0.02: product Driver, truth 4-wood), 18 (0.07: Driver vs 2-wood), 5 and 6 (0.0), 9B; Mozingo "
    "14 (4-wood vs Driver, 0.14 strokes) and 18. Expected gain: **+3 to +5 holes over both courses** once trees / "
    "long grass pass 0.6 in the corridor. Owner: vision_any v2 long-grass / tree-edge model and the open "
    "segmentation model (both in flight) - merge into the package only when these IoU columns move.",
    "3. **Tee boxes 20-30 yds off** where 18Birdies' marker sits on a box behind the Black one (tee error 1: 26, "
    "14: 22, 16: 26, 17: 29, 2B: 29 yds; 8/16 within 10 yds). A 25-yd tee error moves the whole landing corridor: "
    "hole 1 (Driver CHECK at -40 vs 4-wood, 0.09 strokes, the largest regret) and 16 (4-wood vs Driver) follow from "
    "it. Expected gain: **+1 to +2 holes**. Owner: tees (joint assignment picks the box behind when two boxes hold "
    "similar yardage; add lidar pad + card order + the app's tee when the golfer shares one).",
    "4. **Water and OB corridor geometry** (water IoU 0.33 with 2/10 passing; OB 0.12, 0/4: creek buffers narrow, OB "
    "from the course boundary, not lot lines). Expected gain: **+1 hole** (10, 2F, 6 sit on water/OB edges). Owner: "
    "platform water rule + ob/ (OB inference, in flight).",
    "5. **Package hygiene that can flip a pick on a new course**: Veenker tees 7 (Blue) inside OB and 12 (Blue) in a "
    "bunker since the tee rebuild; zones vs zones_ll drift (SH 9/10/11, Veenker 3/7/8/15/16); self-intersecting "
    "polygons on all three courses; forward-tee par-3 lengths 15-38% over the card. Expected gain: 0-1 hole on the "
    "scored courses. Owner: platform / tees.",
    "6. **No truth for Veenker (or any third course).** The bar is measured on 30 tee shots from two courses, one of "
    "which (Mozingo) tuned vision thresholds. A golfer's 18Birdies screenshots + picks for Veenker would make this a "
    "generalisation test. Expected gain: 0 holes directly; it is what makes the other numbers trustworthy.",
    "7. **Stale deliverables.** Every `packages/<slug>/out/` (book, wind page, decision.json) predates the 00:00-00:21 "
    "package rebuilds; the scoreboard re-runs the decision itself, but what a golfer opens is older. Re-run the "
    "plan_course requests after each package rebuild. 0 holes; a delivery gap.",
]
