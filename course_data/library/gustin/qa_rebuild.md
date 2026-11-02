# A. L. Gustin GC: rebuild QA, third pass (2026-11-02)

**Verdict: PUBLISH.** 15 Gold now plays from its own box at 350 (340 measured), and 15 Black stays at 399. The Gold
total is 5,839.

Page checked: `course_data/library/gustin/page.html`, built 2026-11-02T06:26Z (GitHub Actions run 41392580512). Both
solved sets (Black, Gold) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems. I looked at
every phone hole picture.

## Second-pass fix

| fix | applied? |
|---|---|
| 15: `tee_ll {"Gold": [38.9303307, -92.3459911]}`, `yards {"Black": 399, "Gold": 350}` | **yes.** The Gold tee is OSM box 591649551, 0.7 yds from the fix point, 340 measured. The Black tee is 4 yds from its fix, 396 measured. 4-wood, fairway 72% (Gold); 2-wood, fairway 73% (Black). |

`raw/scorecard_web.json` still lists the consensus change (Gold 15 350 -> 401), but the per-set override now wins.
The pipeline issue (the guard does not see review overrides) is still open; see the second-pass notes.

## Holes

| hole | Black | Gold | note |
|---|---|---|---|
| 1-5, 8, 10, 12-14, 17, 18 | OK | OK | page yardage = card; measured within 5 |
| 6 | OK | OK (marginal) | Gold 4-wood aim 40.0 left on the bound into the dogleg corner (trees 11%); long iron 0.02 behind. Model choice |
| 7 | OK (chute tee, as reviewed) | OK (marginal) | Gold 2-wood/4-wood aim 39.5 left over the corner, sand 10%, 30 yds in. Model choice |
| 9 | OK (marginal) | OK (marginal) | Driver to 39-54 yds short of the green, trees 13-21%. Model choice |
| 11 | OK | OK | Black on a capped lidar pad (moved off a road), 416 measured / 424 card |
| **15** | **fixed** | **fixed** | see above |
| 16 | OK (marginal) | OK | Black 4-wood aim 40.0 right (on the bound), trees 16%. Model choice |

## Remaining (optional)

Pipeline: let `card_consensus` see the review's `yardage_overrides` before its longer-set guard (second-pass note 2).
The aim-bound picks on 6 / 7 are the shared decide-step clamp issue.
