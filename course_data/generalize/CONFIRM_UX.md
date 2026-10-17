# Golfer confirm: the fewest taps to a 100 % correct hole routing

Routing v2 (`course_data/platform/routing_v2.py`) places every hole from the scorecard and the detected greens / tee boxes, and keeps a posterior over whole-round routings. When it is not sure, the app asks the golfer a few questions before the round. This page specifies those questions, the JSON contract for the app prototype, and what a simulation on the held-out test courses says it costs.

<!-- RESULTS -->

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
