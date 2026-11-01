# Roadmap: name any US course → right club and aim on every hole

Owner: the coordinating Claude session (2-hourly manager check-in, scheduled task "Golf pipeline manager check-in").
Success = per hole, the plan's club matches and the aim is within 10 yds of the plan built on a hand-checked map.

## Where we are (2026-11-01)

| link | today | source |
|---|---|---|
| find the course | ~89 % first try (66-course national batch); resorts with several courses weakest | library/status.json |
| build without crashing | 37/66 first pass; all causes engineering, fixes queued | course-page runs |
| pair tee ↔ green, no card | 86.9 % of holes; 35 % of courses all 18 | zero_tap/PATHROUTE.md v2 |
| tee yardage, no card | back within 10 yds 70 %; par 96 % | tees/CARDLESS.md |
| hazards (trees / water / OB / fairway edge) | not measured on its own | — |
| plan, well-mapped course, no card | 80–85 % of holes same club + aim ≤ 10 yds | platform/CARDBLIND.md |
| plan, barely-mapped course | ~50 % | platform/CARDBLIND.md |
| plan with the TRUE card vs hand truth | ~77 % of clubs | platform/PIPELINE.md §5 |
| national OSM coverage | unknown (index run broken: every course tier D) | library/us_readiness.json |

## Workstreams (in order of payoff)

1. **Error budget (first).** On every hand-truth course, swap one truth layer at a time (routing, tees, greens,
   fairway, trees, water, OB, elevation) into the auto build and measure how many wrong clubs/aims each layer
   fixes. Decides where the next weeks go. → `course_data/platform/ERROR_BUDGET.md`
2. **Hazard layers.** Fix the layers the error budget ranks worst (expected: trees/OB lines and fairway edges),
   measured against hand zones.
3. **More truth.** Grow the hand-truth set from 5 to 15–20 courses (reviewed library courses first) so every
   number above has a real denominator.
4. **Unmapped courses.** Greens / tees / fairways from NAIP + lidar where OSM has nothing; score on the
   zero_tap `unmapped_*` tiers.
5. **National coverage.** Fix the national index so we know what share of US courses is tier A/B/C/D.
6. **Confirm taps.** App asks only about low-confidence holes, re-solves after each answer (pathroute_v2
   confidence + confirm-and-resolve), "this is hole 1" fixes numbering.
7. **Build reliability.** Every failed build gets a cause and a re-queue within one check-in.

## Milestones

- M1: error budget published; national coverage numbers real.
- M2: well-mapped course, ≤ 5 taps → ≥ 95 % of holes right, measured on ≥ 15 truth courses.
- M3: well-mapped course, no taps → ≥ 90 %; barely-mapped → ≥ 75 %.
- M4: unmapped course → usable with taps.
