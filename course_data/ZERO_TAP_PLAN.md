# Zero-tap course mapping: plan

**Goal:** pick any US course and get every hole right (hole number, tee and green for each tee set, par) with
no golfer input.

**Where we are (held-out courses, 2026-10-17):**

| Inputs | Holes numbered right | Courses fully right, no taps |
|---|---|---|
| OSM greens/tees + scorecard | 76% | 13% |
| Unmapped + scorecard | 63% | ~0% |
| No scorecard | 24% | 5% |

## How we will measure it

"100% correct with zero taps" cannot be promised for every course. What we can build is a system that knows
when it is right. The metric is two numbers on a large held-out benchmark:

- **Zero-tap precision:** of the courses the system marks "certain", the share that are fully right.
  Target **≥ 99%**. This is the promise to the golfer.
- **Zero-tap coverage:** the share of all courses marked "certain". Target: rise from ~10% toward 90%+.

Every other course falls back to the quick confirm, so a wrong map never reaches the golfer silently.

## Where the errors come from

The research so far gives a clear order:

1. **Pairing each green with its own tee** (hole formation) is about 73% right without OSM hole lines, and
   that caps everything after it. About 63% of per-green errors take another hole's tee. With the true pairs
   supplied, the order of play is right on 13 of 15 courses.
2. **Front versus back nine**, and where the round starts (the clubhouse), cost about 10 points each.
3. **Missed tees**: forward and hidden tees cap candidate recall at about 86%.
4. **Too little truth**: there are only 5 hand-checked courses, plus OSM hole lines on about 100 sampled
   courses. That is not enough to check 99% precision.

## Workstreams (one agent each)

**A. Hole formation v2 (pairing greens with tees).** A learned pair model trained on hundreds of courses
whose OSM hole lines are complete. It uses:
- imagery: mowing-stripe direction, the fairway corridor joining tee to green, tee-box axis, lidar terrain;
- a global assignment, so each tee complex starts one hole;
- the scorecard: per-tee-set yardages pin each pair's length to within a few yards.

Output: `hole_pairs/1`, giving P(tee complex → green) per pair. Target: ≥ 95% holes formed on held-out
courses, ≥ 99% with a card.

**B. Outside evidence.** Many courses publish hole-by-hole maps or flyover images on their websites, scorecard
images with a course layout, or are in open course databases. Each of these can be registered against the
aerial image to read hole numbers directly.
- Measure coverage and accuracy on the benchmark.
- Respect robots.txt and site terms, and keep only what is needed to locate holes.

Output: `hole_evidence/1`, giving per-hole number evidence with a confidence.

**C. Sequence, anchors and the certainty gate.**
- A joint solver over A's pair probabilities and B's evidence, plus:
  - clubhouse location (buildings, parking, pro-shop tags, and the hole sequence itself as evidence);
  - the first tee and the last green;
  - a front/back nine model;
  - walking and cart-path continuity.
- A calibrated "certain" gate, using conformal calibration on held-out data, so the zero-tap precision target
  is met by construction.

**D. Truth at scale and the benchmark.**
- 300+ US courses with complete OSM hole lines, plus scorecards where available, split held-out by state.
- One `zero_tap_bench` scoreboard on GitHub Actions that every workstream reports against: precision,
  coverage, and failure types.
- Added hand checks on a random 30 courses to measure OSM's own error rate. OSM is not perfect truth.

The existing pipeline-integration agent wires the winners into `course_data/platform/package.py`.

## Rules for every workstream

- Never tune on the benchmark's test states.
- Do heavy compute on GitHub Actions, at most about 6 parallel jobs per agent.
- Use free and open data only.
- A gain counts only on the benchmark scoreboard.
