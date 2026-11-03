# Roadmap: name any US course → right club and aim on every hole

Owner: the coordinating Claude session (2-hourly manager check-in, scheduled task "Golf pipeline manager check-in").
Success = per hole, the plan's club matches and the aim is within 10 yds of the plan built on a hand-checked map.

## Where we are (weekly review 2026-11-01)

| link | now | source |
|---|---|---|
| find the course | ~89 % first try (66-course national batch); resort/multi-course fixes queued | library/status.json |
| build without crashing | 37/66 first pass; every failure cause fixed, 45 courses re-queued | course-page runs 13–15 |
| pair tee ↔ green, no card (OSM-mapped) | 86.9 % of holes; 35 % of courses all right (153 test courses) | zero_tap/PATHROUTE.md v2 |
| pair tee ↔ green, unmapped (honest, 74 courses) | ~80 % of holes; 14–26 % all right | zero_tap/UNMAPPED.md |
| numbering | 25 % no taps → 94 % after confirms + one "hole 1" tap | PATHROUTE.md resolve |
| confirm taps to 98 % pairs | 4.7 / course (no re-solve); re-solve 7.1 (fix running) | summary_resolve_calib2.json |
| tee yardage, no card | back within 10 yds 70 %; 2nd set 52 %; par 96 % | tees/CARDLESS.md |
| plan, auto build with true card vs hand truth | **74 % same club + aim ≤ 10 yds** (138 tee shots, 10 courses) | platform/ERROR_BUDGET.md |
| what causes the misses | tees 42 %, long grass 25 % (64 % of regret; layer off: detector can't tell native from mown rough), trees 14 %, fairway 11 % | ERROR_BUDGET.md |
| long grass, no agent / no taps (held out, 18 truth courses, 250 tee shots) | **auto native sides: match 167 → 186, regret 8.79 → 4.34** (+ ≤ 2 classifier-ranked taps: 193 / 3.23; perfect sides 196 / 2.91); parkland controls unchanged | mapper/EVAL_BLIND.md "Automatic native sides" |
| plan, no card, well-mapped | 80–85 % (vs card plan) | platform/CARDBLIND.md |
| plan, barely-mapped | 17/33 holes (was 2/32) | CARDBLIND.md pathroute |
| hand-truth courses | 13 (5 + 2 new truth_sets_v2 + error-budget set); 7 more being traced | truth_sets_v2 |
| national OSM coverage | 13,090 US courses indexed, all states (2026-11-02, Geofabrik): tier A 5,858 (45 %: complete OSM holes + greens + tees + card), B 413, C 3,498 (partial OSM), D 3,321 (outline only); 74.6 % have some OSM golf mapping | library/us_readiness.json |

## Agent mapper (adopted 2026-11-02)

Blind evaluation on 9 hand-truth courses (course_data/mapper/EVAL_BLIND.md): strokes lost −18 % pooled, matches
98 → 99, no course broken in round 2. One mapper agent (~15–60 min) now reviews every course's hazard layers
(native/long grass, tree edges, OB, water, fairway sides) and tees before its page is built.

**Round 3 (2026-11-02, S2 native hints + 5 Kansas native courses + 2 parkland controls, 98 tee shots):**
match 50 → 66 (51 % → 67 %), strokes lost 6.17 → 2.25 (−63 %), 18 holes fixed, 2 broken (Mariah Hills 6, 10).
Prairie Dunes 1 → 7 matches, Buffalo Dunes 7 → 13; parkland controls not broken (Ellis 11 → 11, Spirit Hollow 7 → 8).
Native corridor area missing 296k → 151k sq yds. Gap: Eagle Bend mapper added no native (Will's holes 2/3/5/6) → brief fix for
mixed parkland/native courses, then re-run.

## Automatic native sides (adopted 2026-11-03, not yet in the build)

`product/native_auto.py` classifies each hole side (150-345 yds, 10-40 yds off the fairway) from the S2 native P,
open ground, lidar HAG and NAIP texture, and draws the confirm tap's native band on the sides it is sure of, only
on courses where >= 25 % of the sides fire. Leave-one-course-out on 18 truth courses (mapper/EVAL_native_auto.md):

| | match (250 tee shots) | regret | regret / round (excl. Mariah 7 artefact) |
|---|---|---|---|
| no long grass (today's auto build) | 167 (67 %) | 8.79 | 0.46 |
| auto native sides, 0 taps | 186 (74 %) | 4.34 | 0.28 |
| + ≤ 2 taps ranked by the classifier (21 taps on 18 courses) | 193 (77 %) | 3.23 | 0.22 |
| perfect side answers (ceiling of the band) | 196 (78 %) | 2.91 | 0.20 |

Per course 0 taps: Prairie Dunes 1 → 12, Buffalo Dunes 7 → 13, Mariah Hills 5 → 7, Sand Creek 12 → 12, Gateway /
Coldwater regret −0.12 / −0.06; Eagle Bend and Annbriar unchanged (gate shut; taps take Eagle Bend 7 → 9); parkland
controls Ellis 11 → 11, Blue Hills 14 → 14, Spirit Hollow 7 → 7 (0.892 → 0.886), 7 no-native courses unchanged.
On the 7 round-3 courses it beats the blind mapper with no agent (69 / 1.89 vs 66 / 2.25) and, with 2 taps,
mapper + 4 taps (74 / 0.93 vs 72 / 1.64). M2's 0.15 strokes / round is not reached by long grass alone (ceiling
0.20 with the band; the rest is tees, trees, fairway). A rebuild with the shipped model (all 18 courses)
would add native on Sand Creek Station, Prairie Dunes, Mariah Hills, Buffalo Dunes, Gateway National, Coldwater,
Annbriar (in-sample only: its held-out gate stayed shut), Spirit Hollow (package only; the live page is never
modified) and Tournament Club of Iowa (the one non-truth course with an S2 stack whose gate fires, 9 holes); 14
other S2 courses stay unchanged and courses without an S2 stack get nothing. No rebuild queued.

## Workstreams (re-ranked 2026-11-01 by measured payoff)

1. **Tee positions** (42 % of wrong plans): back-set box choice on long / split tee complexes. Agent running.
2. **Long grass** (64 % of regret): **per-side classifier adopted 2026-11-03** (`product/native_auto.py`, behind a
   course gate; S2 phenology + open ground carry it, lidar HAG / NAIP texture add little). Next: wire
   `native_auto.build_layer` into the package build + an S2 fetch stage, feed its p to the confirm taps, validate on
   the 7 courses being traced (the gate was set after seeing Ellis). Misses left: green-in-summer native (Eagle Bend,
   Annbriar) → taps.
3. **Tree edge** (~5 yds short) and **fairway outline**: with the tee fix (they interact).
4. **Build reliability + QA of rebuilt courses** → publish passes. QA agent running; consensus set-order bug fixed.
5. **Confirm taps**: sticky re-solve so taps drop below 4.7. Agent running.
6. **More hand truth**: 7 courses being traced (packages landed after the Overpass outage).
7. **Unmapped courses**: leakage-free perception retrain on Actions, then false-tee re-scorer and pairing evidence.
8. **National coverage**: full cell run queued.

## Milestones

- M1: error budget published; national coverage numbers real.
- M2: well-mapped course, ≤ 5 taps → ≥ 95 % of holes right, measured on ≥ 15 truth courses.
- M3: well-mapped course, no taps → ≥ 90 %; barely-mapped → ≥ 75 %.
- M4: unmapped course → usable with taps.


### Second yardstick: strokes, not just matching picks (added 2026-11-02)

"Same club + aim within 10 yds" is strict: many misses are near-ties where both plans score the same. The
error budget also measures **regret** — strokes the auto plan costs when played on the true map. On the
10-course set the auto build (true card) loses 2.65 strokes over 138 tee shots ≈ **0.019 strokes per tee shot,
~0.27 per 18-hole round** (the hand long-grass layer alone would cut that by ~60 %). Milestones are judged on
both: match % AND regret per round (target ≤ 0.15 strokes/round for M2, measured on held-out truth courses).

## Target dates (estimates, revised every Sunday)

| milestone | target | confidence |
|---|---|---|
| M1 error budget (**done 11-01**) + real national coverage (**done 11-02**: 13,090 courses, all states) | 2026-11-08 | **done** |
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
- A course reaches the user only after a hole-by-hole check of its screenshots. Since 11-03, passing library courses go into the main Aim Caddie app (no individual per-course artifacts).
- The live Spirit Hollow page is never modified; tournament pages change only through their own refreshes.
- Every accuracy number in this file names its test set and size.

**Limits to know:**
- Work runs only when a scheduled task, an agent report or the user wakes the session; if the session is
  archived or the scheduled tasks are disabled, work stops until the next message.
- Container restarts stop running agents; the next check-in resumes them from their transcripts.
- Usage: the user monitors their own plan usage (not visible to the session) and says "pause until <time>" if
  needed; otherwise capacity is used fully.
