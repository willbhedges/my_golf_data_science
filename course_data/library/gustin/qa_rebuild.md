# A. L. Gustin GC: rebuild QA, second pass (2026-11-02)

**Verdict: NEEDS FIX.** 15 Gold is **still 401 yds on the Black box**. The card-consensus fix (commit 0ceff9dc) did not
take effect on this course. 15 Black stays fixed, and everything else is as in the first pass.

Page checked: `course_data/library/gustin/page.html`, built 2026-11-02T03:15Z (GitHub Actions run 41378614486, the
retry after the consensus fix). Both solved sets (Black, Gold) were run through `qa_page.js`: 18 holes each, phone and
desktop, 0 page problems. I looked at every phone hole picture. Gold total is still 5,890; it would be 5,839 with 15 at
350.

## 15 Gold: why the consensus fix missed it

`raw/scorecard_web.json` (re-fetched by this build) still has `consensus.changes = [{hole 15, set Gold, card 350,
chosen 401, source opengolfapi, ground_err [50, 1]}]`. The page's 15 Gold tee is `osm/tee_axis` at
(38.9306022, -92.3471012), 401 measured, 2 yds behind the Black tee (399).

The new guard in `course_data/platform/card_consensus.py` skips a replacement only when it lands within 5 yds of, or
behind, a **longer set's card yardage on that hole**. It compares with `merged` Black, which is still the card's
**467**. The review's `yardage_overrides {"15": {"Black": 399}}` is applied later in the build, so the guard sees 401
< 462 and lets the change through. The guard never sees the 399 that the page actually uses.

Also note that golfify **and** AllSquare both say Gold 15 = 350; `corroborated_by` is 0 for every source. But the
"two cards agree" brake does not apply when the base card's ground misfit is large (ground_err 50, the OSM ground fit
does not find the forward box), so it does not stop the change either.

## Holes

| hole | Black | Gold | note |
|---|---|---|---|
| 1-5, 8, 10-14, 17, 18 | OK | OK | page yardage = card; same as first pass |
| 6 | OK | OK | Gold now Long iron (calm 4-wood), the first-pass concern is gone |
| 7 | OK (chute tee, as reviewed) | OK (marginal) | Gold 2-wood aim 39 left over the corner, sand 11%, trees 8%, 31 yds in. Aim-bound pick, model choice |
| 9 | OK (marginal) | OK | Black Driver to 54 yds short, trees 21%, fairway 7%; long iron is 0.053 behind. Model choice |
| **15** | **fixed** (399, 2-wood aim 30 left, fairway 73%) | **still wrong** | Gold on the Black box at 401 instead of its own box at about 341-350 |
| 16 | OK (marginal) | OK | Black 4-wood aim 40.0 right (on the bound), trees 16%. Model choice |

## Next fix

1. **Quickest:** `course_data/library/gustin/review.json`, hole 15 `fix`: add `"tee_ll": {"Gold": [38.9303307,
   -92.3459911]}` (the OSM tee box at the foot of the fairway) and `"yards": {"Black": 399, "Gold": 350}`. A per-set
   yardage override wins over the consensus. Then rebuild (coordinator: course_page_gustin request).
2. **Pipeline:** `card_consensus.consensus()` should see the request's `yardage_overrides` (apply them to `merged`
   before the longer-set guard), or the build should re-run the guard after the overrides. As written, the guard cannot
   catch a case where the review shortened the longer set, and that is exactly the Gustin case.
3. Optional (pipeline): when two consistent sources agree on a value, a single source flagged `consistent: false`
   should not replace it, whatever the ground fit says.

After that rebuild: PUBLISH, provided 15 Gold reads about 350 from the forward box and the Gold total is 5,839.
