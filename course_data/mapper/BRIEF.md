# Mapper agent brief

Product decision (user-approved): the layers the automatic build is bad at (long grass, tree edges, OB, water,
fairway sides, the back tee on long complexes) are reviewed and marked by ONE Claude agent per course, looking at the
course imagery the way the hand-truth agents did. Routing, greens, the card and the decision maths stay automatic.

Flow: course requested -> package built (with vision) -> coordinator spawns one mapper agent with the brief below
-> the agent writes `course_data/mapper/<slug>/` -> the page is built from package + agent layers
(`"agent_layers": "course_data/mapper/<slug>/"` in the request).

## Coordinator: before spawning

The mapper needs, committed in the repo:

| what | where | how to get it |
|---|---|---|
| package with imagery (NAIP 0.3-0.6 m + NIR + 3DEP DEM + raw OSM) | `course_data/packages/<slug>/` (`imagery/naip_rgb.tif`) | push `course_data/requests/package_<slug>.json` (copy a library course's `package_request.json`, drop `"builder"`) |
| lidar canopy + a second NAIP year (+ OB evidence, product vision layer) | `course_data/vision_any/<slug>/raw/` (`hag.tif`, `naip_YYYY.tif`), `course_data/ob/<slug>/` | push `course_data/requests/tourn_truth_<name>.json` `{"slugs": [slug], "infer": [slug], "ob": [slug], "rev": 1}` after the package exists (it also commits evidence renders to `course_data/truth/<slug>/render/`: the mapper never opens them) |

Without the lidar stack the mapper can still work (trees from the photo only); say so in the brief. The mapper's
`render_inputs.py --rebuild auto` re-makes the vision_any/2 lidar trees and the current tee rule offline when the
committed package predates them, so the agent reviews what a build with the lidar stack gives (`base/package.json`).

Corridor set: the set whose par-4/5 tee shots are mapped (default the package's `tee_set`; for an evaluation run on a
truth course use the scored set: `error_budget.py` COURSES / `truth_sets_v2/index.json` `corridor_set`. Pass it as
`<SET>`; never pass anything else from a truth file).

Spawn ONE agent per course with the text between the lines, `<slug>` and `<SET>` filled in. After it reports:
`git pull`, check `course_data/mapper/<slug>/review.md` and `PLAN.md`, then either score it
(`python3 course_data/mapper/eval_mapper.py --courses <slug>` on truth courses) or build the page (add
`"agent_layers": "course_data/mapper/<slug>/"` to `course_data/requests/course_page_<slug>.json`; the coordinator's push).

---8<--- brief to paste ---8<---

# Mapper agent: <slug> (corridor set <SET>)

You are the mapper for one golf course. The automatic build has made a course package; you look at the aerial
photos, lidar canopy and terrain of every par-4/5 tee shot's landing corridor and correct the map layers the
automatic detection is bad at, and check every tee. The planner then picks clubs and aims from your map. Work like
a careful surveyor: mark what the imagery shows, leave the auto layer where you cannot tell, write down what you are
unsure of. **Budget: about 45 minutes.** Repo: `/home/user/my_golf_data_science`, branch
`claude/mozingo-lake-tee-strategy-ef54wl`. Read `course_data/AGENT_RULES.md` first (worktree, commits, push loop).

## Strict rules (the evaluation depends on them)

* You are blind to any hand truth. **Never open, list, grep or render anything under** `course_data/truth/<any course>/`,
  `course_data/truth_sets*/`, `course_data/zero_tap/truth_sets/`, `course_data/courses/*/truth/`, any `holes_truth*`,
  `hand_zones*`, `CHECK.md` / `NOTES.md` of a truth set, `course_data/library/<slug>/review*`, `qa_report.md`,
  `course_data/platform/error_budget*`, `fairway_quality*`, `course_data/mapper/eval_*` / `EVAL_*`, and do not
  read other agents' reports about this course. Do not use `course_data/truth/corridor.py` stages (`panels`,
  `review`, `build`): they write into truth folders. The mapper scripts below import its drawing code only.
* Only these inputs: the package (`course_data/packages/<slug>/`), the imagery / lidar / OB evidence
  (`course_data/vision_any/<slug>/raw/`, `course_data/ob/<slug>/`) and the renders the mapper scripts make.
* Move a tee only when a tee box is visible where you put it. Draw a layer only where the photo (both years for
  long grass) shows it. When unsure, leave the auto layer and list it under `uncertain`.
* Write only in `course_data/mapper/<slug>/`. Commit only the files listed in step 6. Never push request files.

## 0. Worktree (blind sparse checkout)

```bash
S=<slug>; SC=<your scratchpad>; R=/home/user/my_golf_data_science
git -C $R fetch -q origin claude/mozingo-lake-tee-strategy-ef54wl
git -C $R worktree add --no-checkout $SC/wt-map-$S origin/claude/mozingo-lake-tee-strategy-ef54wl
cd $SC/wt-map-$S && git sparse-checkout set --no-cone '/*.py' '/mozingo/' '/course_data/**/*.py' \
  '/course_data/vision_any/model_v2/' '/course_data/platform/routing_v2_weights.json' \
  "/course_data/packages/$S/" "/course_data/vision_any/$S/" "/course_data/ob/$S/" '/course_data/mapper/' \
  '!/course_data/truth/*/**' '!/course_data/truth_sets*/**' '!/course_data/zero_tap/truth_sets/**' \
  '!/course_data/courses/*/truth/**' '!/course_data/mapper/eval_*' '!/course_data/mapper/EVAL_*' && git checkout -q
ls course_data/truth          # only the *.py tools: no course folder may appear here (else stop and report)
export OMP_NUM_THREADS=1
```

## 1. Render your inputs (~3 min)

```bash
python3 course_data/mapper/render_inputs.py $S --set <SET>
```

Writes `course_data/mapper/$S/`: `inputs.md` (per hole: card, auto tee method, the auto layers in the landing zone),
`frames.json`, `edits.template.json`, `base/package.json` (the package you review) and `render/`:
`map/map.jpg` (whole course: OSM greens G, tees T, hole lines, package holes P<n>), and per hole
`hNN_overview.png` (tee -> green), `hNN_corridor_a.png` (photo + AUTO layers | bare photo | 2nd NAIP year),
`hNN_corridor_b.png` (lidar canopy + auto tree outlines | CIR + lidar edge | 3rd year or DEM hillshade),
`hNN_tees.png` (every set's auto tee, OSM tee boxes, DEM hillshade, other year). Look at images with the Read tool.
For a closer look at an edge, crop: `python3 -c "from PIL import Image; im=Image.open('...'); im.crop((x0,y0,x1,y1)).resize(...).save('/tmp/...')"`.

**Coordinates.** Each corridor panel has a 10-yd grid: `x` = yards right (+) / left (-) of the tee line (magenta 0
line, labels along the top and bottom), `along` = yards from the corridor-set tee (labels on the left and middle,
yellow every 50). The window is along 120-400, x -70..+70. Every shape you write is `[x, along]` in that hole's
frame. The tee sheet uses the same frame (along < 0 = behind the corridor tee).

## 2. Per corridor: what to check and mark (~2 min per hole)

Go hole by hole (all par 4s and 5s). Look at `corridor_a` (auto layers vs photo vs 2nd year) and `corridor_b`
(lidar / CIR). Mark, in this order of value:

1. **Long grass (native / fescue / prairie)** - the auto build has almost none (detection is off by decision). Per
   side (L / R), where does unmown grass start and how far along does it run? Native = tan / textured / tufted, no
   mowing stripes, often with mown paths cut through it, **and the same in both photo years**. *Second-year check:*
   mown rough in a drought or dormant season can look tan in one year; if it is green and smooth in the other year
   it is mown rough, not native. Lidar 0.5-2.5 m (yellow) speckle and a mottled CIR support native. Usual shape:
   `beyond_fairway` with `w` = the mown-rough width you measure on the photo (typically 6-15 yds), limited to a side
   and an along range; or a `poly` for a patch. Erase auto `native` that sits on mown rough.
2. **Tree edges** - the auto trees are the lidar canopy (> 2.5 m) and usually stop a few yards short of where a ball
   is "in the trees" on the fairway side. Compare the auto outline (corridor_a, dark green) with the crowns in the
   photo and lidar: where the crown edge is consistently beyond it, `grow` the trees by that many yards inside a
   region on that side (only the fairway-facing edge matters). Add crowns the lidar missed (trees newer than the
   lidar, or no lidar: `ell` per crown or `poly` for a stand); erase trees that are gone in both photo years.
3. **OB** - only where houses, back yards, a road or a fence line are visible. The line is the lot / fence line, not
   the house. Erase auto OB that is woods or course land with no development visible (outline-only OB). A course
   boundary with nothing built behind it is not OB.
4. **Water** - pond and creek edges at the water line (not the bank top). Add missed water (creeks under trees:
   check both years and CIR, water is black in NIR); erase water that is dry / filled in both years.
5. **Fairway sides** - only when OSM is visibly wrong: no fairway, a fairway shifted or > 5 yds too narrow / wide on
   a side (the mowing line is visible in both years). `add` fairway (`band` or `poly`) or `erase` fairway.
   Bunkers only if a big landing-zone bunker is missing.

Precedence is automatic (later wins): native < trees < OB < first cut < fairway < green < water < sand. So long
grass may be drawn generously: it never covers a fairway, trees or water. "Rough" is not a lie: to make an area
mown rough, `erase` the lie that is there.

## 3. Tees, every set on every hole (~7 min)

`hNN_tees.png` shows each set's auto tee (dot, card yards, method) over the photo with the OSM tee boxes (cyan) and
the DEM hillshade (tee pads are raised, flat, often rectangular). For each set: is the dot on a visible box whose
distance fits the card (`inputs.md`: card yds; `review.md` after writing: measured)? `keep` if yes. If no, and a box
is visible where the card length puts it (usually on the hole line, behind or ahead of the dot), `move` to its
centre with evidence ("separate box 18 yds behind, on the line; card 463 vs auto box at 445"). The back set on long
or split complexes is the usual miss: the card sits 6-20 yds behind the mapped box. Never move to a spot with no
box; never move more than ~60 yds without saying why. Par 3 tees are checked the same way.

## 4. Write edits.json

Copy `edits.template.json` to `edits.json` and fill it in:

```json
{"schema": "mapper_edits/1", "slug": "<slug>", "corridor_set": "<SET>", "mapper": "<your agent name>",
 "started": "2026-11-02T06:00Z", "minutes": 42,
 "holes": {
  "4": {"reviewed": ["long_grass", "trees", "ob", "water", "fairway"], "confidence": "medium",
        "note": "fescue both sides beyond ~10 yds of rough; trees right short by ~5",
        "edits": [
   {"op": "add", "lie": "native", "shape": {"beyond_fairway": {"w": 10, "side": "L", "a0": 170, "a1": 330}},
    "confidence": "high", "evidence": "tan tufted grass both 2021 and 2023, lidar yellow speckle"},
   {"op": "grow", "lie": "recovery", "by": 5, "shape": {"rect": [10, 70, 200, 320]},
    "confidence": "medium", "evidence": "crown edge 4-6 yds beyond the auto outline on the right"},
   {"op": "erase", "lie": "ob", "shape": {"rect": [-70, -40, 120, 400]}, "evidence": "woods, no houses"},
   {"op": "add", "lie": "recovery", "shape": {"ell": [-22, 265, 6, 6]}, "evidence": "single oak, both years"}]}},
 "tees": {"4": {"Black": {"action": "move", "to": [1, -16], "confidence": "medium",
                          "evidence": "box visible 16 yds behind on the line; card 463, auto at 447"},
                "Blue": {"action": "keep"}}},
 "uncertain": [{"hole": "7", "what": "left edge of the fescue at 250-300 (+/-8 yds)"}]}
```

* ops: `add` (new zone of `lie`), `erase` (remove `lie` / `lies` inside the shape), `grow` (`by` yds; negative
  shrinks; only inside the shape). lies: `fairway`, `first_cut`, `recovery` (trees), `native` (long grass),
  `water`, `sand`, `ob`. `reviewed` layers: `fairway`, `trees`, `long_grass`, `water`, `ob`, `bunkers` (list a
  layer even when you changed nothing: it records that you checked it).
* shapes (yards, `[x, along]`): `poly` `[[x, a], ...]`; `rect` `[x0, x1, a0, a1]`; `ell` `[cx, ca, rx, ra]`;
  `band` `{"left": [[a, x], ...], "right": [[a, x], ...]}` (edges as `[along, x]`); `side`
  `{"side": "L", "from": 25, "to": 70, "a0": 180, "a1": 330}` (a lateral strip, distances from the line);
  `beyond_fairway` `{"w": 10, "side": "L"|"R"|"both", "a0", "a1", "x0", "x1"}` (the box minus the package fairway
  grown by w).
* tees: `"to": [x, along]` in the hole's tee-sheet frame (same as the corridor frame; par 3s: tee -> green), or
  `"to_ll": [lon, lat]`. Every edit and move: `confidence` (high / medium / low) and `evidence` (what you saw, which
  year / panel).

## 5. Convert, check, iterate (~5 min)

```bash
python3 course_data/mapper/write_layers.py $S      # -> agent_zones.geojson, agent_tees.json, review.md, render/hNN_review.png
python3 course_data/mapper/build_plan.py $S --n 2000 --workers 4   # optional: which plans your layers change (PLAN.md)
```

Open `render/hNN_review.png` (AUTO | AUTO + AGENT | your edits on the other year) for every hole you edited:
does the result match the photo? Fix `edits.json` and re-run until it does. `write_layers.py` refuses bad edits
(unknown lie / op, a shape outside the window or with x / along swapped, a move without evidence).

## 6. Commit and report

Commit only: `course_data/mapper/$S/{edits.json,agent_zones.geojson,agent_tees.json,frames.json,inputs.md,review.md,
edits.template.json,base/package.json}` (+ `plan.json`, `PLAN.md` if you ran build_plan). `render/` and `out/` are
not committed (.gitignore). Push loop as in AGENT_RULES.md, then remove the worktree.

Report (short): minutes spent; per layer what you changed (holes, sq yds, tee moves with yards); holes you could not
judge and why (missing year / lidar, shadows, renovation); your confidence per layer; the commit.

---8<--- end of brief ---8<---

## Files and tools

| file | what |
|---|---|
| `render_inputs.py` | base package (+ offline lidar trees / tee rule when stale), frames, course map, corridor / tee sheets, `inputs.md`, template |
| `write_layers.py` | `edits.json` (yard frame) -> `agent_zones.geojson` + `agent_tees.json` (WGS84), `review.md`, review renders |
| `apply.py` | apply the agent layers to any package, layer by layer (erase / add / grow per lie, tee moves with aim / length / elevation re-derived, `reframe`), recorded in `package.agent_layers`, `stages.agent_layers`, `holes[].provenance.agent` |
| `build_plan.py` | quick decision on AUTO and AUTO + AGENT -> `plan.json`, `PLAN.md` |
| `eval_mapper.py` | error budget AUTO vs AUTO + AGENT vs truth (per course, pooled, per layer area, tee error) -> `eval_<set>.json`, `EVAL_<set>.md` (never shown to a mapper) |
| `test_mapper.py` | `python3 -m pytest -q course_data/mapper/test_mapper.py` |
| `platform/package.py` `apply_agent_layers` | package request `"agent_layers": "course_data/mapper/<slug>/"`: applied after vision + OB in every build (course_package.yml, course_page_one.yml); `library/course_page.py pkgreq` passes the key from a course-page request |
