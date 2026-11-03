# Creekmoor GC: rebuild QA, wide-aim pass (2026-11-03)

**Verdict: NEEDS FIX (no fairway layer).** The routing, tees, card and agent layers are all right. The 14 CHECKs are
real, but they are not wide-aim or tee faults. Every one except the 3 Black tee is the aim rule "the calm pick lands
on fairway". It fires because the page has no fairway at all. OSM maps no `golf=fairway` on this course: the
2026-10-17 snapshot holds tees, greens, bunkers, holes and cart paths, and no fairway. The vision stage does not add
fairway, and the mapper did not draw any. So every tee shot reads "fairway 0%", the planner cannot tell fairway from
rough, and several picks aim at bunkers.

Page checked: `course_data/library/creekmoor/page.html`, GitHub Actions run 41537321619 (committed 2026-11-03 01:24Z).
I ran both solved sets (Black, Green) through `qa_page.js`, phone and desktop: 18 holes each, 0 page problems, no
console errors. I looked at every Black phone hole picture, and checked every landing oval against the picture edge on
both sets. The 14 CHECK holes were already there in the 2026-11-02 19:50Z build: the count did not change in this run.

## Why 14 CHECKs

| cause | holes |
|---|---|
| "lands in rough (N yds from fairway)" / "no fairway mapped on this hole". The "fairway" it measures to is a few 60-900 yd2 OSM scraps by tees and greens, e.g. 1: 620 yd2 at 360-382 yds | 1, 2, 3, 5, 6, 8, 9, 10, 11, 13, 14, 15, 16, 18 (both sets) |
| tee (lidar pad 25 yds from a box, 441 / 440 card) | 3 Black |
| wide aim | none: no aim past ±40 |

So the wide-aim rule is not over-firing here. The CHECKs are justified as a data flag, but they all point to one
course-level gap, not to 14 separate hole problems.

## What the gap does to the page

- Every landing reads "fairway 0%, first cut 0%". The ovals are wide and flat (rough everywhere), and the aims steer
  only by sand, trees and OB. In the pictures the fairways are plainly visible. Black 14 Driver 28.5 left lands on the
  left fairway-bunker cluster (sand 15%); Black 3, 13 and 18 land among the centre / side bunkers (sand 12-13%); Black
  1 Driver 35 right (Green 39 right) heads for the right edge.
- Native cards: 8 were asked and 7 dropped, because answering "both sides native" re-plans to Driver ±95-120 yds.
  With no fairway, the planner sees no reason to stay in the corridor, so it aims into the next hole. Dropping them was
  right. Only 13 is kept ("current" Driver +3 = page, priors 0.75 / 0.75 from the mapper's native).
- One oval clips: Green 1 Driver 39 right is 1-9 px past the right edge (the aim is under 40, so the picture was not
  widened).

## Mapper layers (`course_data/mapper/creekmoor/review.md`)

In, applied 2026-11-02T23:17Z, 21 ops. Native added on 6, 8, 13 and 14 (agent zones in the package; "long grass 2-3%"
on 6 and 13). OB erased on 6, 8, 9, 10 and 11. OB added on 16 and 18 (an agent OB zone in each). Water erased on 8, 9,
10, 11 and 18. On 1, 5 and 16 the water erase shows "0 yd2": the new water filter had already removed those cells.
None of the 16 / 18 landings reads water now. The only landing water left is the real pond right of 9 (2-7%). Red 17
tee moved 44 yds (off the page sets).

## Holes

| hole | Black | Green | note |
|---|---|---|---|
| 4, 7, 12, 17 | OK | OK | par 3s; 12 / 17 review tees 0-1 yds from the boxes |
| 1 | aim CHECK | aim CHECK | Driver +35 / +39 toward the right edge (fairway-blind); Green oval clips 1-9 px |
| 2, 5, 6, 8, 9, 15, 16 | aim CHECK | aim CHECK | landings in the corridor; the picture shows them on or near fairway |
| 3 | tee + aim CHECK | aim CHECK | Black lidar pad 441 / 440, among the fairway bunkers (sand 13%) |
| 10 | aim CHECK | aim CHECK | supplement way, 481 / 482, still right |
| 11 | aim CHECK | aim CHECK | Driver 25.5-35 left by the bunkers, sand 6-9%, trees 6-8% |
| 13, 18 | aim CHECK | aim CHECK | Driver at the bunker line (sand 12-13%) |
| 14 | aim CHECK (poor pick) | aim CHECK | Black Driver 28.5 left into the left bunker cluster, sand 15% |

## Next fix

1. **Course data:** give Creekmoor a fairway layer. Either the mapper draws fairway zones (`agent_zones.geojson`,
   lie `fairway`) on the 14 par 4/5 landing areas from the NAIP picture, or a fairway class is taken from vision.
   Then rebuild. The aim CHECKs should clear, and the native cards should stop re-planning out of the corridor.
2. If the coordinator accepts fairway-blind plans, as the previous pass did, the page is otherwise publishable: no
   routing, tee or card faults.
