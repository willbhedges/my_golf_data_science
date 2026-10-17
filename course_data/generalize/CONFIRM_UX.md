# Golfer confirm: the fewest taps to a 100 % correct hole routing

Routing v2 (`course_data/platform/routing_v2.py`) places every hole from the scorecard and the detected greens / tee boxes, and keeps a posterior over whole-round routings. When it is not sure, the app asks the golfer a few questions before the round. This page specifies those questions, the JSON contract for the app prototype, and what a simulation on the held-out test courses says it costs.

<!-- RESULTS -->

## Results on the held-out test split (test, `route_eval.py final`, eval_v2.json)

Test courses are the 32 fully mapped courses held out by `sample.py holdout` (8 per Census region). Hurstbourne (KY, 27 holes) has fewer than 9 numbered OSM holes 1-18 and is skipped, which leaves the counts below. None of them was used to tune `routing_v2_weights.json`. Each course's OSM golf=hole ways and refs are hidden. Median / mean taps count only the courses that reached 100 %.

### Automatic routing: v1 (routing.py) vs v2 (routing_v2.py)

| inputs | card | courses | method | hole-number acc | green acc | all holes correct, no input | every wrong hole flagged | flags / course | wrong / course |
|---|---|---|---|---|---|---|---|---|---|
| OSM greens / tees + model + lidar | web, else pars + lengths | 31 | v1 | 68% | 76% | **10%** | 48% | 7.58 | 5.13 |
| OSM greens / tees + model + lidar | web, else pars + lengths | 31 | v2 | 76% | 86% | **13%** | 48% | 6.74 | 3.68 |
| model + lidar only (unmapped) | web, else pars + lengths | 31 | v1 | 62% | 73% | **6%** | 61% | 9.58 | 6.13 |
| model + lidar only (unmapped) | web, else pars + lengths | 31 | v2 | 63% | 71% | **0%** | 45% | 8.9 | 6.03 |
| OSM greens / tees + model + lidar | none | 31 | v1 | 10% | 15% | **0%** | 61% | 15.58 | 15.26 |
| OSM greens / tees + model + lidar | none | 31 | v2 | 16% | 21% | **0%** | 94% | 17.52 | 14.19 |

### Golfer confirm: taps until every hole is right (oracle golfer, test split)

| inputs | policy | courses | reach 100 % (<= 30 taps) | 0 taps | <= 2 taps | <= 4 taps | <= 8 taps | median taps | mean taps | app stops after (mean taps) | all right when the app stops |
|---|---|---|---|---|---|---|---|---|---|---|---|
| OSM greens / tees + model + lidar | least-sure hole first | 31 | 90% | 13% | 16% | 23% | 32% | 14.0 | 14.64 | 7.43 | 23% |
| OSM greens / tees + model + lidar | max bits per tap (default) | 31 | 94% | 13% | 16% | 26% | 36% | 15.0 | 13.86 | 7.0 | 30% |
| OSM greens / tees + model + lidar | v1 style: confirm each flagged hole | 31 | 100% | 13% | 16% | 19% | 36% | 17.0 | 14.58 | 8.29 | 42% |
| OSM greens / tees + model + lidar | no routing: tap all 18 tees + greens | 31 | 100% | 0% | 0% | 0% | 0% | 36.0 | 34.0 | - | - |
| model + lidar only (unmapped) | least-sure hole first | 31 | 77% | 0% | 3% | 10% | 26% | 21.0 | 16.58 | 9.29 | 11% |
| model + lidar only (unmapped) | no routing: tap all 18 tees + greens | 31 | 100% | 0% | 0% | 0% | 0% | 36.0 | 34.0 | - | - |

Weights: `course_data/platform/routing_v2_weights.json` (coordinate search (route_eval.py tune), train split, 102 course x input runs); posterior temperature tau 0.75, flag threshold p_hole < 0.95.

<!-- /RESULTS -->

### What the numbers say

* **Automatic routing improves on courses with OSM greens and tees** (the "partial" tier, plus full-tier courses with a hole way missing):
  * hole-number accuracy goes from 68 % to 76 % and green accuracy from 76 % to 86 %
  * wrong holes per course fall from 5.1 to 3.7, and flags per course from 7.6 to 6.7
  * courses fully right with no input go from 10 % to 13 % (3 to 4 of 31)

  The biggest per-course gains are routings v1 had shifted by whole nines: Towne Lake Hills 0 % to 78 %, Kingwood 6 % to 65 %, Cinder Ridge 13 % to 80 %. On the train split v2 reaches 83 % (eval_v2_train.json); the test figure is the honest one.
* **"All 18 correct with no human input" stays rare**, at 13 %, because a whole round has 18 chances to be wrong. With 3.7 wrong holes per course, the golfer confirm is the realistic path to 100 %.
* **Unmapped courses (model + lidar only) did not improve**: 62 % to 63 % hole accuracy, and all-correct fell from 6 % to 0 %. The learned weights lean on cues the model inputs lack or get wrong: exact green positions, tee polygons, and OSM fairways for the corridor term. These courses need the perception work (course_data/perception/).
* **Without a card, numbering is still a guess**: 16 % hole accuracy. v2 flags almost every hole there (17.5 per course, so 94 % of courses have every wrong hole flagged), which is the right behaviour: ask for the card. Typing the 18 yardages (`typed_card.py`) takes the course to the "card" rows above.
* **Flags are better targeted but not fewer than about 7 per course.** Calibrated on train at tau 0.75 and p_hole < 0.95, the posterior flags 6.7 holes per course and catches every wrong hole on 48 % of courses, the same rate as v1, which needed 7.6 flags. The remaining errors are confident ones: a green the detectors never found, or a tee complex shared between two holes.

### Taps to a correct routing

* With OSM greens / tees, the default policy (max bits per tap) gets **94 % of courses 100 % right within 30 taps**, at a **mean of 13.9 taps (median 15)**. Tapping every tee and green with no routing costs 34-36 taps.
  * 13 % of courses need no input at all (the router is already right).
  * 26 % need at most 4 taps, and 36 % at most 8.
* The lower bound, if the app knew which holes were wrong, is 2 taps x 3.7 wrong holes, or about 7.4 taps. The policies spend the difference confirming holes that were already right.
* The three policies are close. "Confirm each flagged hole" (v1's check list, a locate after a "no") always finishes but needs a median of 17 taps. "Max bits per tap" has the best mean, and with the stop rule it stops after 7 taps with all holes right on 30 % of courses.
* **The stop rule is not safe yet.** When the app stops on its own (every unconfirmed hole at p_hole >= 0.95), 1.4 holes per course are still wrong on average. Until the posterior is better calibrated, the app should keep showing "this isn't hole n" during the round.
* On unmapped courses (model + lidar only), 77 % of courses reach 100 % within 30 taps, at a mean of 16.6 taps.


## The questions

There are two kinds of question. Each answer is a constraint, and the whole round is solved again under it ("propagation"), so one answer usually fixes the holes next to it as well. Every hole is played once, greens and tee boxes are used at most once, and green n leads on to tee n+1.

| kind | prompt | taps | the map shows | answer | effect |
|---|---|---|---|---|---|
| `confirm` | "Is this hole 7? (par 4)" | 1 | hole 7's line from its back tee to its green | `yes` / `no` | yes: hole 7 is pinned. no: that green, with any tee box within 45 yds of the one shown, is ruled out for hole 7, and the next question about hole 7 is a `locate` |
| `locate` | "Tap hole 7's tee, then its green" | 2 | the course map (no line) | two map points | hole 7 is pinned to the detected tee box within 25 yds and the green within 15 yds of the taps. A tap with nothing detected near it becomes a new candidate |

**Which question comes next.** The app asks the question with the highest expected information per tap, measured over the posterior of routings: the distinct top routings of the beam, Boltzmann-weighted at the calibrated temperature `tau`.

* A `confirm` on hole n is worth H(p) bits, where p is the posterior probability of the line shown. It never drops below the value of a 2 % doubt, because the posterior can be overconfident.
* A `locate` is worth the entropy of hole n's whole answer distribution, split across its 2 taps. After a "no" it is worth at least 1 bit.

This tends to put "tap hole 1's tee" first on courses where the start is unclear, since the start fixes the round's direction and the clubhouse end. Pairs of holes that the router may have swapped (9 and 18, 1 and 10) come next.

**When to stop.** The app stops asking once every unconfirmed hole has `p_hole >= p_stop`, the calibrated flag threshold, and starts the round. The golfer can still use "this isn't hole n" at any time; it becomes a `confirm` answered "no".

## JSON contract: `golf_confirm/1` (`platform/confirm.py`, `Session.payload()`)

```json
{
 "schema": "golf_confirm/1",
 "course": {"name": "...", "osm": {"type": "way", "id": 123}, "state": "MA"},
 "method": "routing/2", "n_holes": 18, "card": true,
 "holes": [
  {"ref": 1, "par": 4, "card_yards": [358, 397, 417],
   "tee": {"ll": [lon, lat], "id": "osm:way/1", "src": "osm|segment|lidar|golfer"},
   "green": {"ll": [lon, lat], "id": "osm:way/2", "src": "osm|segment|golfer"},
   "line": [[lon, lat], [lon, lat]], "straight_yd": 401.2,
   "p_hole": 0.93, "confirmed": false, "status": "ok|check|confirmed", "flags": ["ambiguous (61% of the posterior)"]}
 ],
 "summary": {"confirmed": 0, "to_check": 3, "taps_so_far": 0, "done": false, "p_stop": 0.8,
             "expected_correct_holes": 16.4},
 "questions": [
  {"id": "l1", "kind": "locate", "ref": "1", "taps": 2, "bits": 1.9, "bits_per_tap": 0.95, "p_hole": 0.55,
   "prompt": "Tap hole 1's tee, then its green", "show": {"line": null, "tee_ll": null, "green_ll": null},
   "answers": [{"tee_ll": "[lon, lat]", "green_ll": "[lon, lat]"}]},
  {"id": "c9", "kind": "confirm", "ref": "9", "taps": 1, "bits": 0.9, "bits_per_tap": 0.9, "p_hole": 0.7,
   "prompt": "Is this hole 9? (par 5)", "show": {"line": [[lon, lat], [lon, lat]], "tee_ll": [..], "green_ll": [..]},
   "answers": ["yes", "no"]}
 ],
 "history": [{"question": "c9", "kind": "confirm", "ref": "9", "answer": "yes"}],
 "candidates": {"greens": [{"id": "...", "ll": [lon, lat], "src": "osm"}], "tees": [...]},
 "answer_format": {"question": "<questions[].id>", "answer": "'yes' | 'no' | {'tee_ll': [...], 'green_ll': [...]}"}
}
```

The app returns one answer at a time, as `{"question": "c9", "answer": "yes"}` or `{"question": "l1", "answer": {"tee_ll": [lon, lat], "green_ll": [lon, lat]}}`. `Session.answer()` applies it and solves again, and the next `payload()` carries the updated holes and questions. When `summary.done` is true, `questions` is empty. `candidates` lets the app snap taps on the device or draw the detected features. An example generated from a cached course is in `course_data/generalize/confirm_example.json` (`python course_data/platform/confirm.py course_data/generalize/courses/<slug> --hide-holes --out ...`).

Screen flow (the minimal confirm):

1. "We mapped 18 holes. Help us check 3 of them (about 10 seconds)." This is shown only when `questions` is not empty.
2. One full-screen card per question, map first. For a `confirm`, the line is drawn and the two buttons are **Yes, that's hole 7** and **No**. For a `locate`, a crosshair and the hint "tap where hole 7 starts", then "now its green".
3. After each answer the map animates to the re-solved routing, so the holes that changed show the propagation. The next card is whatever `questions[0]` says.
4. Done: "All 18 holes placed", then the hole list. Holes the golfer confirmed get a check mark, and the rest show their confidence.

**In the app prototype** (`course_data/app`): `confirm_engine.js` runs this flow in the page (same questions, policy and stop rule) over a routing pool precomputed by `confirm_pool.py` (base solve + every hole's likely greens pinned; the page keeps the posterior exact over the pool), and `typed_card.js` ports `typed_card.py`. `app/SCHEMA.md` ("Hole map confirm") documents the data; `test_confirm.js` / `test_confirm_ui.js` replay the oracle golfer against `confirm.Session` on the same courses.

## Cards when none is online: typed yardages (`platform/typed_card.py`)

Without a card, routing has no yardage sequence and hole numbers are close to a guess (REPORT.md). The cheapest fix is to ask for the 18 numbers on the card. `parse_typed_card(yards, pars=None, tee=..., unit="yd"|"m", total=...)` returns a `scorecard/1` card, which routing reads directly, plus a list of issues:

* **Accepted input:** any separator (spaces, commas, `/`, new lines); `hole: value` pairs in any order; the card's OUT / IN / TOT columns, which are recognised by their sums and removed; a run of par digits typed together (`443545344`); metres.
* **Errors** (re-ask, pointing at the hole):
  * not 9 / 18 values, with a hint when one is missing or extra; 27 / 36 values means "type the nines you play"
  * a non-number
  * a value over 999, which is two values typed together
  * yards outside 50-720
  * pars outside 3-6 or in a different count from the yards
  * a par total outside 27-38 (9 holes) or 54-76 (18 holes)
  * a stated total that differs from the sum
* **Warnings** (accept, highlight):
  * the par does not fit the yardage (par 3 over 270, par 4 under 230 or over 520, par 5 under 400)
  * an OUT / IN subtotal that disagrees with its nine
  * the same nine typed twice

## Photo of the scorecard: how it would work (research, not implemented)

1. **Capture.** A camera view with a card-shaped guide, plus two shots for folded cards (front nine, back nine). Correct the perspective from the card's outline: VNDetectRectanglesRequest on iOS, or a document scanner (VisionKit `VNDocumentCameraViewController`, ML Kit Document Scanner on Android).
2. **Text with positions.** On-device OCR returns each token with its bounding box: Apple Vision `VNRecognizeTextRequest` (accurate mode, language correction off for digits) or Google ML Kit Text Recognition v2. Both are free and run offline. Cloud table extractors (AWS Textract `AnalyzeDocument` TABLES, Azure Document Intelligence layout, Google Document AI) also return cell structure, but they cost money per page and need the network. A vision-language model prompted for a strict JSON grid is another option. Whatever the source, the output goes through the same validation below.
3. **Rebuild the grid.**
   * Cluster tokens into rows by their centre y after deskewing, and into columns by x.
   * Find the header row (`HOLE 1 2 ... 9 OUT 10 ... 18 IN TOT`) to fix the column for each hole.
   * Label rows by their first token: a tee name or colour (BLACK / BLUE / WHITE / GOLD / RED / COMBO, as in `scorecard.COLOURS`), `PAR`, `HCP` / `HANDICAP`. The blank player-score rows are ignored.
4. **Validate and repair.** The card checks itself, which typed lists cannot:
   * Each yardage row must match its OUT / IN / TOT. One OCR digit error almost always breaks a sum, and a single-digit substitution that restores all three sums (3/8, 1/7, 5/6, 0/8 are typical OCR confusions) can be proposed as a fix.
   * Across tee rows, each hole must be at least as long on the longer set (`scorecard.consistency`).
   * The par row must fit within 3-6 per hole, sum to its OUT / IN, and fit the yardages (`typed_card.PAR_FIT`).
   * The handicap row must be a permutation of 1-18, usually odd on one nine and even on the other.
   * Every row then goes through `typed_card.parse_typed_card`.
5. **Show the golfer the grid over the photo.** Cells that fail a check are highlighted, and one tap edits a cell. The golfer picks their tee row, which becomes the card's `tee_sets` entry.
6. **Measure before shipping.** Collect 50 or more card photos, with glare, folds, and hand-written scores among them. Report cells right, cards fully right after the sum checks, and taps to fix. Accuracy should not be assumed: the score boxes and logos on real cards are where OCR goes wrong.

Implementation order: typed card (done, `typed_card.py`), then on-device OCR plus grid assembly feeding the same validator, then a photo eval set.
