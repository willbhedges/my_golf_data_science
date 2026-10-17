"""Hand-written part of SCOREBOARD.md: table notes and the ranked gap list (QA lead's judgement, from the
per-hole rows). Edit, then `python3 course_data/qa/scoreboard.py --md-only`."""

NOTES = [
    "Headline mode: where the truth is a Bayesian decision (Spirit Hollow, final_decision.json) the headline is the "
    "product's full Bayesian mode (decide.full_hole, 64 draws x 3000 swings, ~11 min on 4 cores, Actions only); the "
    "quick point estimate is kept as its own column. Mozingo's truth is the hand map through the quick decision, so its "
    "headline stays quick.",
    "Spirit Hollow is scored on 16 tee shots: 14 from the Black plan (holes 2 and 9 -> 2F / 9F) plus 2B and 9B from a "
    "Gold-tee product plan, because those screenshots (and the hand map) play from the Gold box.",
    "'Same club as hand map, quick' isolates map error (same decision on both maps); 'quick-mode ceiling' isolates the "
    "decision-mode error. Decision parity (product code on the hand map vs the reference model) is 14/14 "
    "(course_data/packages/spirit_hollow/out/parity/summary.md), and full mode on the hand map matches final_decision "
    "15/16: what is left is the map.",
    "Veenker has no hand map: agreement, regret and geometry are n/a until one exists.",
    "Geometry columns need a georeferenced hand map, which only Spirit Hollow has (hand_zones_ll.json).",
]

GAPS = [
    "Decision parity is solved (14/14 on the hand map; full mode on the hand map 15/16 vs final_decision.json), so "
    "**map error is now the limit**. Direction of every current miss (quick mode, 04:50 run): the product picks a "
    "*shorter* club than the truth on all 6 Spirit Hollow misses (4, 9B, 10, 13, 17, 18) and all 6 Mozingo misses "
    "(9, 10, 14, 16, 17, 18): since the vision_any v2 + OB rebuilds the packages over-penalise the driver landing zone.",
    "",
    "1. **Long grass / OB over-prediction in the driver landing zone (vision_any v2 + OB inference).** The rebuilds "
    "that took Spirit Hollow 10 -> 8/16 and Mozingo 10 -> 7/14 added long grass and inferred OB where the hand maps have "
    "rough; on Mozingo every miss is Driver -> 4-wood / 2-wood (14: 0.09, 17: 0.05, 18: 0.04 strokes). Calibrate the v2 "
    "long-grass threshold and the OB inference against the hand maps' corridor (long grass IoU 0.19, OB 0.39 with 0/2 "
    "passing on Spirit Hollow) before merging into packages; gate the merge on this scoreboard. Expected gain: **+4 to "
    "+6 holes on Mozingo, +2 to +3 on Spirit Hollow** (4, 17, 18).",
    "2. **Tree edges in the corridor** (trees IoU 0.30, 2/16 holes > 0.6): 10 (0.05) and 18 (0.06) are tree-line "
    "holes where the product lays up. Expected gain: **+1 to +2 holes** on Spirit Hollow. Owner: vision_any v2 tree "
    "edges / segment model.",
    "3. **Tee boxes 20-30 yds off** where 18Birdies' marker sits on a box behind the Black one (1: 26, 16: 26, 17: 29, "
    "14: 22, 2B: 29 yds; 8/16 within 10 yds). 17 (4-wood vs Driver) follows from it. Expected gain: **+1 hole**. "
    "Owner: tees.",
    "4. **Water and OB corridor geometry** (water IoU 0.32, 2/10 holes pass): 10 and 13 sit on creek edges. Expected "
    "gain: **0 to +1 hole**. Owner: platform water rule + ob/.",
    "5. **Package hygiene that can flip a pick on a new course**: tees inside hazards (Veenker), zones vs zones_ll "
    "drift, self-intersecting polygons, forward-tee par-3 lengths 15-38% over the card. 0 holes on the scored courses; "
    "wrong-answer risk elsewhere. Owner: platform / tees.",
    "6. **No truth for Veenker (or any third course).** The bar rests on 30 tee shots from two courses. A golfer's "
    "18Birdies screenshots + picks for Veenker would make this a generalisation test. 0 holes directly.",
    "7. **Ship full mode in the product's default path.** The headline uses full mode on Actions; the phone deliverables "
    "of Mozingo / Veenker are still quick plans. 0 holes on the scoreboard; it is what the golfer gets.",
]
