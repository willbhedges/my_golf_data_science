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
    "Decision parity is solved (product code on the hand map 14/14; full mode on the hand map matches "
    "final_decision.json 15/16), so **map error is now the limit**. Headline (06:15, full mode): Spirit Hollow 9/16 "
    "same club, 12/16 same-or-tie; the 4 full-mode misses are 13, 14, 17, 18, and 4, 6, 9B are ties. On Mozingo "
    "(quick, 7/14) and on every Spirit Hollow miss but 14, the product picks a *shorter* club than the truth: since the "
    "vision_any v2 + OB rebuilds the packages over-penalise the driver landing zone. Bar: 13/16 and 12/14.",
    "",
    "1. **Long grass / OB over-prediction in the driver landing zone (vision_any v2 + OB inference).** The rebuilds "
    "took Spirit Hollow 10 -> 8/16 (quick) and Mozingo 10 -> 7/14; every Mozingo miss is Driver -> 4-wood / 2-wood "
    "(9, 10, 14: 0.09, 16, 17: 0.05, 18: 0.04 strokes); on Spirit Hollow 17 and 18 (long grass IoU 0.33 / 0.08) and the "
    "4 tie follow the same pattern. Calibrate the v2 long-grass threshold and the inferred OB against the hand maps' "
    "corridors (SH long grass IoU 0.19, OB 0.39 with 0/2 holes passing) and gate the package merge on this scoreboard. "
    "Expected gain: **+4 to +6 holes on Mozingo, +1 to +2 on Spirit Hollow**.",
    "2. **Tee boxes 20-30 yds off** where 18Birdies' marker sits on a box behind the Black one (17: 29, 14: 22, 1: 26, "
    "16: 26, 2B: 29 yds; 8/16 within 10). 17 (4-wood vs Driver) and 14 (full mode Driver at the -40 limit, CHECK, vs "
    "2-wood/4-wood tie) trace to it. Expected gain: **+1 to +2 holes** on Spirit Hollow. Owner: tees.",
    "3. **Tree edges in the corridor** (trees IoU 0.30, 2/16 > 0.6): 18 (trees 0.06: 4-wood vs 2-wood) and 13 (0.25: "
    "4-wood vs Driver). Expected gain: **+1 to +2 holes**. Owner: vision_any v2 tree edges / segment model.",
    "4. **Water / creek corridor geometry** (water IoU 0.32, 2/10 pass): 13 and 10 sit on creek edges. Expected gain: "
    "**0 to +1 hole**. Owner: platform water rule.",
    "5. **Full-mode runtime**: 45 min on one Actions runner (16 holes x 64 draws x 3000 swings), not the 11 min "
    "measured on 4 local cores; split it per hole like plan_spirit_hollow.yml so the scoreboard turns around in "
    "~15 min. 0 holes; cadence.",
    "6. **Package hygiene that can flip a pick on a new course**: tees inside hazards (Veenker), zones vs zones_ll "
    "drift, self-intersecting polygons, forward-tee par-3 lengths 15-38% over the card. 0 holes on the scored courses. "
    "Owner: platform / tees.",
    "7. **No truth for Veenker (or any third course).** The bar rests on 30 tee shots from two courses. 0 holes "
    "directly; it is what makes the numbers a generalisation test.",
    "8. **Ship full mode in the golfer's deliverables.** The phone pages of Mozingo / Veenker are quick plans; full "
    "mode gains +1 same club and +2 same-or-tie on Spirit Hollow. 0 holes on the scoreboard; it is what the golfer gets.",
]
