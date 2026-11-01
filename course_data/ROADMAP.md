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

## Target dates (estimates, revised every Sunday)

| milestone | target | confidence |
|---|---|---|
| M1 error budget + real national coverage | 2026-11-08 | high |
| M2 well-mapped, ≤ 5 taps → ≥ 95 % of holes right (≥ 15 truth courses) | 2026-12-06 | medium |
| M3 well-mapped no taps ≥ 90 %; barely-mapped ≥ 75 % | 2027-02-28 | low–medium |
| M4 unmapped courses usable with taps | 2027-04-30 | low |

Dates slip if the error budget shows the hazard layers need a new model rather than fixes, or if hand truth
can't be produced fast enough (each truth course needs imagery renders on Actions + a careful trace).

## How this is managed

**Cadence (scheduled tasks bound to this session):**
- *Manager check-in, every 2 h* ("Golf pipeline manager check-in"): every finished build gets a cause and a
  re-queue; stalled agents (container restarts) are resumed; agent reports are integrated; rebuilt courses are
  checked hole by hole and only passing pages are published; idle capacity gets the next workstream task.
  Messages the user only when something changed. Disables itself after 3 idle check-ins.
- *Daily digest, 6:47 pm Central* ("Golf pipeline daily digest"): one short message — headline numbers vs
  milestones, what finished/failed/fixed, what runs next, decisions needed (usually none). Re-enables the
  check-in if work is pending.
- *Weekly review, Sundays (inside the digest):* re-rank workstreams by measured payoff, update "Where we are"
  and the target dates above, say plainly when a date slips and why.
- Tournament pages keep their own scheduled refreshes (Eagle Knoll: Nov 5, Nov 6 evening).

**Agents:**
- Every agent gets a written brief: goal, files it owns, files it must not touch, the metric it must move, a
  budget, and "report honestly what was not verified". Shared rules: `course_data/AGENT_RULES.md` (survives
  container restarts; the scratchpad copy is refreshed from it). Coordinator to-dos: `course_data/MANAGER_TODO.md`.
- Up to ~10 agents at once (20 is the hard limit; usage is not the constraint, GitHub runners and file ownership
  are), so builds and the coordinator keep headroom; two agents never own the same file.
- No result is accepted on an agent's word: numbers are on held-out data (tuned on dev, test run once), tests
  pass before every push, and the coordinator re-runs the key check before anything reaches a published page.
- Negative results are kept and written down (e.g. tip candidates, sequence_v3) so work isn't repeated.

**Servers and compute (GitHub Actions, 20 shared runners):**
- Long builds go out as one batch at a time; small jobs (forecasts, web fetches) are never starved for hours.
- Every workflow reads the request files from its own triggering push (no "latest file" guessing).
- Commit loops use `--autostash` and retry; failed jobs are read from the logs at the next check-in.
- Disk in the session container is watched; finished worktrees are removed once their work is pushed.

**Quality gates (never skipped):**
- A page is published only after a hole-by-hole check of its screenshots.
- The live Spirit Hollow page is never modified; tournament pages change only through their own refreshes.
- Every accuracy number in this file names its test set and size.

**Limits to know:**
- Work runs only when a scheduled task, an agent report or the user wakes the session; if the session is
  archived or the scheduled tasks are disabled, work stops until the next message.
- Container restarts stop running agents; the next check-in resumes them from their transcripts.
- Usage: the user monitors their own plan usage (not visible to the session) and says "pause until <time>" if
  needed; otherwise capacity is used fully.
