# Truth set v2 (workstream 3: more hand truth)

Hand-checked truth for reviewed library courses, in the same formats as the tournament truth
(`course_data/truth/<slug>/holes_truth.json`, `hand_zones_ll.json`, `course_data/courses/<slug>/truth/package.json`),
kept here so the tournament folders stay untouched. Registry: `index.json` (status, corridor tee set, confidence).
Per course: `holes_spec.json`, `holes_truth.json`, `trace.py`, `hand_zones_ll.json`, `package.json`, `CHECK.md`
(read CHECK.md before trusting a hole: it lists every tee / hazard that is estimated or unsure).

## For the error-budget harness / picks_pipeline

```python
sys.path.insert(0, "course_data/truth_sets_v2")
import truth_sets as TS
TS.available()                                  # {slug: meta} with holes_truth.json present
T, HZ = TS.load(slug)                           # holes_truth (tees per set, greens, lines), hand corridors
pkg = TS.truth_package(slug, auto_pkg, tees,    # auto package with truth layers swapped in
                       layers=("routing", "tees", "zones"))   # any subset: swap one layer at a time
```

`truth_package` follows `course_data/courses/score_auto.py::truth_package` (hand corridor zones masked over the auto
zones inside `footprint_ll`, every set's tee, green centre + outline, par, card, hole line), plus a `layers` switch.
`<slug>/package.json` is that applied to the committed auto package (`course_data/packages/<slug>`) for the corridor
set, so it plans directly (`product/package.py load` + `decide.run`), like `courses/<slug>/truth/package.json`.

Scoring notes:
* Corridors cover the corridor set's par-4/5 tee shots only: footprint 130-420 yds along x +/-65 yds from the
  package tee of that set (wider than the tournament truth's 145-345 so a truth tee up to ~40 yds from the package tee
  keeps its 180-330 landing zone inside). Outside the footprint the auto zones stay (not truth).
* Zones: fairway, recovery (trees: 3DEP lidar canopy > 2.5 m, checked against NAIP), water, sand, native (long
  grass), ob. Later zones win; unzoned inside the footprint = rough.
* Tees of sets with no visible box are "estimated" in `holes_truth.json` `tee_method` (moved along the line to the
  card length); score tee error only on sets with `pad` / `hand` methods if you need a clean denominator.
* The auto packages in `course_data/packages/<slug>` were built blind (name + town + tees) for this set; they are the
  "before" side of any comparison. Rebuilds of those packages change the auto side only; the truth here does not
  depend on them except for `package.json` (re-run `python3 course_data/truth_sets_v2/truth_sets.py build <slug>`).

## How a course is made

1. `course_package.yml` (request `course_data/requests/package_<slug>.json`): package with NAIP + DEM + raw OSM.
2. `tourn_truth.yml` (request `tourn_truth_*.json`): 3DEP lidar HAG + NAIP years (`vision_any/<slug>/raw`), OB
   evidence (`ob/<slug>/raw`), corridor renders + `render/frames.json` in `course_data/truth/<slug>/`.
3. `course_data/truth/course_map.py` -> `draft_spec.py --package-lines` -> hand edits of `holes_spec.json` (tee per set
   decided on tee -> green sheets) -> `build_holes_truth.py`.
4. `trace.py` (auto start layers + hand corrections from the corridor renders) -> `corridor.py build`.
5. `truth_sets.py build <slug>`; CHECK.md.

The truth tools (`course_data/truth/*.py`) read and write the truth files here when `truth_sets_v2/<slug>/` exists
(`corridor.tdir`); renders and maps stay in `course_data/truth/<slug>/`.
