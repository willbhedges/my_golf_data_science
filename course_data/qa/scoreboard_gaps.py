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
    "1. **Trees and long grass in the landing corridor (vision).** Mean corridor IoU on Spirit Hollow is ~0.27 for "
    "trees and ~0.15 for long grass (bar 0.6). Every Spirit Hollow miss where the tee is right (10, 18, 9B) is a tree "
    "or long-grass edge the package draws in the wrong place, so the product plays Driver where the hand map lays up. "
    "Expected gain: **+2 to +3 holes on Spirit Hollow**, and the same failure mode on any wooded course. Owner: "
    "vision_any v2 long-grass / tree-edge model (in flight) - merge into the package only when the scoreboard's IoU "
    "columns move.",
    "2. **Tee boxes 20-30 yds off on the holes where 18Birdies' marker sits on a box behind the Black one** (1, 14, "
    "16, 17 tee error 22-29 yds; 2B 29 yds). A 25-yd tee error shifts every landing zone; hole 1 (Driver CHECK vs "
    "4-wood) and 16 (4-wood vs Driver tie) follow from it. Expected gain: **+1 to +2 holes**. Owner: tees (joint "
    "assignment picks the wrong OSM box when two boxes hold similar card yardage; use lidar pad + card order + the "
    "app's tee when known).",
    "3. **Product model settings vs the published Bayesian pick.** On 13-type coin flips (margin < 0.01) quick mode "
    "and final_decision.json disagree even on the same map (see 'hand map, quick'). Expected gain: **+1 hole** if "
    "the product reports ties as ties (it does) and the scoreboard counts same-or-tie; +1 to +2 holes of same-club "
    "if the product ran the full Bayesian mode (plan.py default; minutes on Actions).",
    "4. **Water and OB corridor geometry** (water IoU ~0.33, OB ~0.12: creek buffers too narrow, OB lines from the "
    "course boundary, not lot lines). Expected gain: **+1 hole** (10, 2B/2F, 6 sit near water/OB edges). Owner: "
    "platform water rule + ob/ (OB inference, in flight).",
    "5. **Package hygiene that can flip a pick**: Veenker tees 7 (Blue) inside OB and 12 (Blue) in a bunker since the "
    "00:00 tee rebuild; zones vs zones_ll drift on SH 9/10/11 and Veenker 3/7/8/15/16; self-intersecting polygons "
    "on all three courses. Expected gain: 0-1 hole on the scored courses, but they are wrong-answer risks on new ones.",
    "6. **No truth for Veenker (or any third course).** The 80% bar is measured on 30 tee shots from two courses. "
    "A hand map (or a golfer's 18Birdies screenshots + picks) for Veenker would make the scoreboard a real "
    "generalisation test. Expected gain: 0 holes directly; it is what makes the other numbers trustworthy.",
    "7. **Stale product outputs.** Every `packages/<slug>/out/` predates the 00:00 package rebuild; the scoreboard "
    "re-runs the decision itself, but the book / wind page a golfer opens are older. Re-run plan_course requests "
    "after each package rebuild (0 holes; a delivery gap).",
]
