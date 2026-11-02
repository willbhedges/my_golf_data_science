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
| Sentinel-2 stack (the S2 native suggestion) | `course_data/vision_any/s2/<slug>/s2_stack.npz` | after `raw/` exists (the S2 grid is the raw grid at 10 m): edit `course_data/requests/s2_stack.json` (`slugs` = the courses without a stack, `rev` + 1) and push (`.github/workflows/s2_stack.yml`, ~1 min per course + queue). Counts toward the 4 builds in flight |

Without the lidar stack the mapper can still work (trees from the photo only); say so in the brief. Without the S2
stack it works without S2 suggestions (`inputs.md` says "none"). The S2 native P is LOCO-safe
(`vision_any/s2/native_model.py`): a course in the S2 training set (`native_model/model.json` `courses`, every S2
truth course) gets the fold model trained without it, any other course the full model (computed at render time from
the stack + package masks, ~1 min). The mapper's
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
  "/course_data/vision_any/s2/$S/" '/course_data/vision_any/s2/native_model/' \
  "/course_data/imagery/$S/naip_rgb.tif" "/course_data/imagery/$S/naip_nir.tif" "/course_data/imagery/$S/dem.tif" \
  "/course_data/imagery/$S/georef.json" \
  '!/course_data/truth/*/**' '!/course_data/truth_sets*/**' '!/course_data/zero_tap/truth_sets/**' \
  '!/course_data/courses/*/truth/**' '!/course_data/spirit_hollow/**' '!/course_data/mapper/eval_*' \
  '!/course_data/mapper/EVAL_*' && git checkout -q
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
`hNN_tees.png` (every set's auto tee, OSM tee boxes, DEM hillshade, other year), and when the course has a Sentinel-2
stack `hNN_corridor_s2.png` (S2 native probability over the photo | "S2 suggested native" candidates on the photo |
the same on the 2nd year; see "S2 suggestions" below). Look at images with the Read tool.
For a closer look at an edge, crop: `python3 -c "from PIL import Image; im=Image.open('...'); im.crop((x0,y0,x1,y1)).resize(...).save('/tmp/...')"`.

**Coordinates.** Each corridor panel has a 10-yd grid: `x` = yards right (+) / left (-) of the tee line (magenta 0
line, labels along the top and bottom), `along` = yards from the corridor-set tee (labels on the left and middle,
yellow every 50). The window is along 120-400, x -70..+70. Every shape you write is `[x, along]` in that hole's
frame. The tee sheet uses the same frame (along < 0 = behind the corridor tee).

## 2. Per corridor: what to check and mark (~2 min per hole)

Go hole by hole (all par 4s and 5s). Look at `corridor_a` (auto layers vs photo vs 2nd year) and `corridor_b`
(lidar / CIR). Read "How the planner uses your map" below first: it decides where care pays. Mark, in this order
of value:

1. **Long grass (native / fescue / prairie)** - the auto build has almost none (detection is off by decision). Start
   from `hNN_corridor_s2.png` when it exists (S2 suggested native: decide every candidate, "S2 suggestions" below). Per
   side (L / R), where does unmown grass start and how far along does it run? Native = coarse / mottled / tufted, no
   mowing stripes, often with mown paths cut through it, **behind a mowing line that is in the same place in both
   photo years** (rule 1 below). Its colour is not the test: native can be green and mottled in a wet summer and tan
   in a dry one. *Second-year check:* drought or dormant mown rough is tan in one year and green and *smooth* in the
   other, with no second mowing line between the fairway and the trees / boundary. Lidar 0.5-2.5 m (yellow) speckle
   and a mottled CIR support native. Write a verdict for **both sides of every corridor hole** in `long_grass`
   (`"L"` / `"R"`: `"native: edit 0, 2"` or `"none: <what both years show>"`); S2 silence is not a verdict. **Mown rough is
   the default beside a fairway**: measure its width per side at 3+ places on the 0.3 m photo (crop and zoom) and
   start the native where the coarse, tufted texture starts, not where the colour changes. Shapes: a `poly` that
   follows the visible tall-grass edge (best), or `beyond_fairway` with `w` = the measured mown-rough width and
   `a0` / `a1` limited to where you saw it. Erase auto `native` that sits on mown rough. See the long-grass rules
   below: unsure native within 10 yds of the fairway is removed by `write_layers.py`.
2. **Tree edges** - the auto trees are the lidar canopy (> 2.5 m) and usually stop a few yards short of where a ball
   is "in the trees" on the fairway side. Compare the auto outline (corridor_a, dark green) with the crowns in the
   photo and lidar: where the crown edge is consistently beyond it, `grow` the trees by that many yards inside a
   region on that side (only the fairway-facing edge matters). Add crowns the lidar missed (trees newer than the
   lidar, or no lidar: `ell` per crown; a `poly` only for a closed stand whose crowns touch); erase trees that are
   gone in both photo years. Do not grow every edge by a fixed amount: grow only where you measured the gap.
3. **OB** - only where houses, back yards, a road or a fence line are visible. The line is the lot / fence line, not
   the house. Erase auto OB that is woods or course land with no development visible (outline-only OB). A course
   boundary with nothing built behind it is not OB.
4. **Water** - pond and creek edges at the water line (not the bank top). Add missed water (creeks under trees:
   check both years and CIR, water is black in NIR); erase water that is dry / filled in both years.
5. **Fairway sides** - only when OSM is visibly wrong: no fairway, a fairway shifted or > 5 yds too narrow / wide on
   a side (the mowing line is visible in both years). `add` fairway (`band` or `poly`) or `erase` fairway.
   Bunkers only if a big landing-zone bunker is missing. Sandy waste areas: see the sand rule below.

Precedence is automatic (later wins): native < trees < OB < first cut < fairway < green < water < sand. Native never
covers a fairway, trees or water, **but it does cover mown rough**: precedence does not protect the rough, so draw
native exactly, not generously. "Rough" is not a lie: to make an area mown rough, `erase` the lie that is there.

### How the planner uses your map (where care pays)

* **Long grass is priced almost like OB**: half the balls in it are lost (stroke and distance), the rest are hacked
  out. A native edge drawn 5 yds too close to the fairway in the driver landing zone changes the club (driver ->
  3-wood) on that hole; native 25+ yds out or past the green-side end of the landing zone rarely changes anything.
  So near the fairway, a wrong native edge costs more than a missing one.
* Trees cost less (a share of the balls is blocked), sand less again (played like a fairway bunker). A tree edge off
  by 2 yds or an extra crown 15+ yds from the fairway is noise for the plan; spend the time on edges that face the
  landing zone (about 200-320 yds from the tee on par 4/5 tee shots).
* Mown rough is what an unmarked area is: leaving an unsure area unmarked is the safe default **near the
  fairway** (inside ~10 yds). A whole side of real native left out beyond the mown rough in the landing zone is the
  other common miss: it also keeps the driver in the bag when it should not.

### Long-grass rules

1. **Two-year test: the mowing line first, then texture.** Native sits behind a *second mowing line*: a boundary
   beyond the fairway edge (often 8-30 yds out, often along a cart path or a smooth curve parallel to the fairway)
   with smooth, uniform or striped mown turf inside and coarser grass outside (mottled, streaky, tufted, seed heads,
   no stripes). It is native when that line is **in the same place in both photo years** and the outer side is
   coarser in both, **whatever its colour**: on many courses native is green and mottled in a wet summer and tan /
   streaky in a dry one, so "green in one year" is not a reason to reject. It is mown rough when there is no such
   line: the rough runs smooth from the fairway to the trees / boundary, or it is tan in one year and green and
   smooth (stripes, no second edge) in the other. An irrigation edge (green inside, tan outside, in a dry year only)
   is not a mowing line: in the other year the same ground is one smooth green sheet. Tan alone is not native. A
   dark band under or just beside crowns (within ~10 yds of the canopy, on the shadow side) is shade / leaf litter
   on rough, not native; a mottled area that runs on into open ground, away from the crowns, is not shade.
   Courses mix: parkland holes (no second line) and native holes (a line on one or both sides) on the same course.
   Decide each side of each hole on its own; never carry a verdict over from other holes ("parkland course").
2. **Mown-rough width.** Next to a fairway there is mown rough on nearly every course, typically 8-20 yds wide. A
   strip narrower than ~8 yds between the fairway and a tree line, cart path, ditch or pond bank is mown rough (or
   the trees / water) unless the tall grass is unmistakable in both years.
3. **Keep-out (enforced).** `write_layers.py` removes any `add native` that is not `confidence: "high"` from within
   10 yds of the package fairway / first cut / green, and lists it under "Checks" in `review.md`. Use `high` only
   when the area is unmistakable in both years and its edge is crisp; then say in `evidence` where the edge is
   (e.g. "tufted edge 6 yds off the fairway on 2021 and 2023, mown strip visible between"). Islands and big blocks
   of prairie that come right to the fairway are the typical high-confidence case.
4. **No template strips.** Do not lay one `beyond_fairway` strip over the whole window (120-400, both sides) on
   every hole. Limit each to the along range where you saw tall grass; where a fairway ends (dog-leg, lay-up,
   cross-hazard) `beyond_fairway` covers the full width, so stop `a1` at the tall grass's real edge.
5. **Check the result**: `review.md` lists per hole the gap from the fairway to your native (min / median per side).
   A median gap under ~8 yds on a hole should be one you can defend from the photo.

### S2 suggestions (Sentinel-2 native probability)

`inputs.md` and `hNN_corridor_s2.png` show a Sentinel-2 model's native probability (10 m cells = 11 yds; blue
0.3-0.5, yellow -> red above 0.5) and its **suggested native**: the P >= 0.5 clusters outside the package fairway,
first cut, green, water, sand and trees, numbered per side (`L1`, `R1`, ...). The model reads the season (native is
dormant in March and browns and greens with the weather; irrigated turf stays green). It finds most real prairie, but
it also fires on parkland rough that browns in a drought summer, on dry tan rough beside houses and on rough under
scattered trees. **S2 never decides alone: it tells you where to look.** Every candidate is in
`edits.template.json` -> `holes.<n>.s2_suggested.L / R` with an empty `decision`; decide each one from the photos:

* **accept** only where the photo shows unmown native (behind a mowing line in the same place in both years, coarser
  texture outside it; long-grass rule 1) over the candidate. Set `confidence` and `evidence` (what you saw, both years). The candidate's shape
  becomes `add native`, and the 10-yd keep-out applies as to any native you draw (non-high native within 10 yds of
  the fairway is removed).
* **replace** when there is native but the shape is wrong: S2's edges are +/-10 yds and its fairway-side edge
  usually comes in over the mown rough. Trace the real edge yourself as a native edit in `edits` (`poly`, measured
  mown-rough width) and give the candidate `decision: "replace"` with evidence. This is the normal case on a prairie
  course: S2 says which side has native and roughly how far it runs; you place the edge.
* **reject** (with evidence) where the photos show mown rough: no second mowing line and smooth / striped turf in
  one of the years (drought or dormant rough is tan in one year only), parkland rough between scattered trees,
  lawns / lots, cart paths, bare ground. Many candidates on tree-lined holes are false; most on open prairie holes
  are real. Write each rejection from that candidate's own panel (where it is, what both years show there):
  `write_layers.py` flags the same evidence text pasted on many candidates.
* **S2 is often silent on real native**: it misses native that stays green in summer and narrow bands (< ~20 yds,
  two 10 m cells) beside the mown rough. A side with no candidate still needs your own verdict from the photos
  (`long_grass` L / R); add the native you see as edits as before.

`write_layers.py` lists every undecided candidate under "Checks" and an "S2 suggestions" table in `review.md`
(accepted / rejected / replaced); decide them all before you commit. A course with no S2 stack has no candidates.

### Trees, sand, OB rules

* **Scattered trees** (crowns with grass between): one `ell` per crown that is within ~25 yds of the fairway. Never
  a polygon around a group of separate crowns (`write_layers.py` warns on a big tree polygon over open ground).
* **Isolated crowns far from play** (> ~25 yds from the fairway, or outside 180-330 along) are not worth adding.
* **Sand / waste areas**: open bare sand that is white / tan in both years (white-cyan in CIR) is `sand`, waste
  areas included. Not pine straw, bare soil, cart paths or sand under crowns: sand wins over trees in the precedence,
  so draw sand only outside the canopy (`write_layers.py` warns when a sand edit lies on the auto canopy). Sand has
  little effect on the plan: do it last.
* **OB**: draw from what is built (lots, fences, roads); a `low` confidence OB guess is not worth adding.

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
        "note": "fescue left beyond ~10 yds of rough; trees right short by ~5",
        "long_grass": {"L": "native: edit 0 (mowing line ~10 yds off the fairway, same place 2021 / 2023)",
                       "R": "none: smooth mown rough to the tree line in both years, no second mowing line"},
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

* `long_grass` (per hole, from the template): one verdict per side, `"native: ..."` (which edits) or
  `"none: ..."` (what both years show). `write_layers.py` lists empty ones under "Checks" and shows them in
  `review.md` ("Long grass per side").
* `s2_suggested` (per hole, from the template; keep the `id` and `shape` as written): fill in each candidate's
  `decision` (`accept` | `reject` | `replace`), `evidence` (always) and `confidence` (accept). Example:
  `{"id": "S2-4-L1", ..., "decision": "replace", "evidence": "tufted fescue both years, edge 14 yds off the fairway (traced as edit 0); S2 shape hugs the fairway"}`.
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
(unknown lie / op, a shape outside the window or with x / along swapped, a move without evidence), clips unsure
native within 10 yds of the fairway, and lists checks in `review.md` ("Native gap to the fairway", "Checks and
problems"): read both and fix or justify every check before you commit.

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
| `render_inputs.py` | base package (+ offline lidar trees / tee rule when stale), frames, course map, corridor / tee / S2 sheets, `inputs.md`, template (with `s2_suggested`) |
| `s2_suggest.py` | S2 native P in a corridor frame, candidate shapes per side, template block, `decision` -> `add native` (used by render_inputs / write_layers) |
| `vision_any/s2/native_model.py`, `native_model/` | the 23-course S2 native model: `loco/<slug>.npz` fold grids (P of the model trained without that course), `full_model.txt` for new courses; `export` (evaluator) re-makes them from the s2_loco datasets |
| `write_layers.py` | `edits.json` (yard frame) -> `agent_zones.geojson` + `agent_tees.json` (WGS84), `review.md`, review renders |
| `apply.py` | apply the agent layers to any package, layer by layer (erase / add / grow per lie, tee moves with aim / length / elevation re-derived, `reframe`), recorded in `package.agent_layers`, `stages.agent_layers`, `holes[].provenance.agent` |
| `build_plan.py` | quick decision on AUTO and AUTO + AGENT -> `plan.json`, `PLAN.md` |
| `eval_mapper.py` | error budget AUTO vs AUTO + AGENT vs truth (per course, pooled, per layer area, tee error) -> `eval_<set>.json`, `EVAL_<set>.md` (never shown to a mapper) |
| `EVAL_BLIND.md` | evaluator's analysis of the first blind runs (why the agent layers helped / hurt; where the brief's rules come from). Truth-bearing: never shown to a mapper |
| `test_mapper.py` | `python3 -m pytest -q course_data/mapper/test_mapper.py` |
| `platform/package.py` `apply_agent_layers` | package request `"agent_layers": "course_data/mapper/<slug>/"`: applied after vision + OB in every build (course_package.yml, course_page_one.yml); `library/course_page.py pkgreq` passes the key from a course-page request |
