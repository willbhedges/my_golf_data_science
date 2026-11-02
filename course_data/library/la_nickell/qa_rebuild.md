# L.A. Nickell Golf Course: rebuild QA (2026-11-02)

**Verdict: PUBLISH.** The one fix (5 Blue tee and yardage) is applied, and every hole on both sets matches the card.
Four picks sit on the ±40-yd aim bound on this tree-lined course. They are worth a solver look but are not blocking.

Page checked: `course_data/library/la_nickell/page.html`, built 2026-11-01T21:00Z. Both solved sets (Blue 6,335,
White 5,862, par 70) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems. I looked at every
phone hole picture. The page yardage equals the golfify card on all 36 hole-sets. The measured length is within 10 yds
of the card on every hole-set.

## Review fixes

| fix in review.md | applied? |
|---|---|
| 5 Blue: tee about 12 yds behind White (38.97467, -92.37072), 325 | **yes.** Tee source `review`, 0 yds from the point, 325 measured = card. White 5 stays 315 (the `"*"` override did not touch it). |

## Holes

| hole | Blue | White | note |
|---|---|---|---|
| 1-4, 6-14, 18 | OK | OK | walk-backs on Blue 9, 10, 12, 18 and the texture/lidar pads on 4 and 13 are at card length, as reviewed. Parkland: most landings carry 5-20% trees |
| 5 | **fixed**; pick on the bound | OK | Blue Driver aim 39.5 left cuts the dogleg to 32 yds short (fairway 25%, trees 10%) |
| 15 | OK | OK | Blue Driver aim 33 left toward the left trees, fairway 28% |
| 16 | pick on the bound | pick on the bound | Blue 2-wood / White 2-wood (calm) aim **40.0 right** into the tree clump at the corner, trees 18-22%, about 40 yds in. Model choice |
| 17 | OK | pick on the bound | White 4-wood aim 40.0 left, fairway 23%. Model choice |

## Next fix

None blocking. Solver (all courses): picks that sit exactly on the ±40 aim bound (here 5 Blue, 16 both sets, 17
White; also St Andrews 15, Gustin 16, Colbert 13) suggest that the aim grid clamps there. Widen it or flag bound hits.
