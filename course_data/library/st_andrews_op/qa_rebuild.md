# St Andrews GC (Overland Park): rebuild QA, mapper wave 2b (2026-11-03)

**Verdict: PUBLISH.** The stale-lidar trees are gone from the open ground on 1, 2, 3, 13 and 15, and hole 11's creek
is now the narrow stone channel in front of the green. The earlier fix (16 Black tee) still holds. Two caveats are
not blocking: the calm-day badge on 15 Blue (4-wood into the trees past the corner), and a small leftover tree strip
on 3, 45-75 yds left of the line.

Page checked: `course_data/library/st_andrews_op/page.html`, GitHub Actions run 41539963949 (built 2026-11-02T23:47Z),
mapper layers `course_data/mapper/st_andrews_op/` (32 zone edits on 11 holes, 0 tees moved). Both solved sets (Black
6,336, Blue 5,986, par 71) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems, no
console errors. I looked at every phone hole picture. I also drew the package zones (`zones_ll`), tees and hole lines
on the page's own hole images for every par 4 and par 5.

## Mapper layers

| hole | mapper edit | on the page? |
|---|---|---|
| 1 | erase stale trees right of the fairway, 195-330 | **yes.** The right side from the fairway to the cart path has no recovery left. The only trees are along the creek on the left. Black Driver -21.5, fairway |
| 2 | erase stale crowns at 290-345, both sides | **yes.** The green complex and open rough are clear |
| 3 | erase trees over the open corridor | **yes**, the fairway corridor is clear. A rectangle of recovery is left over open mown grass 45-75 yds left of the line, at 230-330 (the corridor clip edge). It is outside every pattern: 4-wood lands on fairway with 0-4% trees |
| 11 | redraw the creek in front of the green as the narrow channel; crown groups right | **yes.** The water zone now follows the curved stone channel just short of the green, and no longer covers the fairway approach. Black 4-wood -5.5, fairway 79%, water 0% |
| 13 | erase stale trees over the fairway, rough and green complex | **yes.** The right of the fairway is clear. The trees left of the landing area are real trees |
| 15 | erase stale trees over the open rough around the dogleg | **yes.** The rough inside and outside the corner is clear. The tee chute (0-150 yds, no landing) still carries recovery; it does not affect any pick |

## Holes

| hole | Black | Blue | note |
|---|---|---|---|
| 1-4, 6-8, 11-14, 16-18 | OK | OK | yardage = card ±1 (16 Black 389 measured / 393 card, the review tee); par 3 boxes on the green |
| 5 | OK (CHECK) | OK (CHECK) | 4-wood -52 / -55 across the dogleg-left corner, landing 48% / 26% fairway. Wide aim is flagged with an Auto-map CHECK on the page |
| 9 | OK (CHECK) | OK | Black tee_axis 4 yds off the box, 381 / 386 |
| 10 | OK (CHECK) | OK | Black on the lidar pad behind the Blue box, 577 (as reviewed) |
| 15 | OK (CHECK) | caveat | Black 4-wood -39 lands at the top-left edge of the fairway at the corner (33% fairway, 3% trees). Blue: the forecast play shown is Long iron, which is sensible, but the **calm-day badge says 4-wood -30**, which runs through the fairway into the trees beyond the corner (calm pattern 73% trees / water, CHECK printed). Solver pick, not a layer problem |

## Next fix

None blocking. Solver: the 15 Blue calm pick prefers a 73%-trees landing over long iron (tie margin 0.025).
