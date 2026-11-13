# holesolve: a full-hole value solver (backward induction on the lie raster)

Research build, beside the engine. It imports `course_data/courses/v2_course.py` and `spirit_hollow/v2/model.py`
and edits nothing: no course data, config, solved output or page reads from this folder. Report and validation
tables: `course_data/courses/gateway_national/second_pass/HOLESOLVE.md`.

## What it does

The engine values a tee ball by a table: expected strokes by lie and distance to the middle of the green. This
solver replaces that table, away from the green, by the value of actually playing the hole from there:

    V(s) = c(lie, d) + min over (club, direction) of E[ 1 + V(finish) ]

* **State**: a ball at rest at a point of a 4-yd grid in the hole's tee frame (yds along the tee line, yds right of
  it), in one of three lie classes of the start: fairway, rough, sand. Every node carries a rough value; fairway
  and sand values exist where such ground is within one node. First cut = the engine's blend of fairway and rough.
* **Anchor**: on the green and inside 30 yds of the middle of it the engine's own value is used as it is (putts by
  distance on the green, short game by lie and distance off it). Putting is not modelled.
* **Shot**: the engine's swing model (`model.shots`: sideways and carry spread, tilt, slight and heavy mishits, roll
  noise) with the deck clubs and lie rules of `gateway_national/PAR5.md`, the part swings of `opt/layup10.py` and
  the par-3 bag's 5- and 7-iron; all of it in `solver.CONFIG`. 256 scrambled-Sobol swings per club and lie, the same
  swings for every state and direction (so the DP solves one fixed discrete swing distribution exactly; there is no
  Monte Carlo noise between states). Each ball lands, then rolls on along its own line as in the engine's
  `finish()`.
* **Where a ball finishes** (kernel.c):
  * fairway, first cut, rough, sand: the DP's value of that lie at that point (bilinear between nodes, see below);
  * trees: the engine's finish-lie rule, as a premium over rough at the same spot (0.8 punch-out + 0.2 restricted
    shot, in table strokes) on top of the DP's rough value there; the engine's "tree line in the way" charge is kept
    the same way. Trees in the flight path are not priced;
  * red penalty area (water, and tall native grass under the course's drop rule): one stroke, then the better of
    the DP's value at the point where the ball last crossed the edge on its own line, in that point's own lie
    (sand included), and back-on-the-line (the best dry spot up to 150 yds back on the line from the hole through
    that point);
  * out of bounds, and tall grass under the lost-ball rule (`--tall lost`): stroke and distance from the same spot,
    in closed form per club and direction, E = (n + sum of found values + n_gone (1 + c)) / (n - n_gone)
    (fastsolve's `--tall-grass lost` arithmetic).
* **Values are stored as DP minus table.** A cell's value is the engine's own value of the cell plus the DP's
  difference for its lie class, interpolated from the nodes. The difference is smooth where the value is steep, so
  a 4-yd grid is enough, and every engine rule that is not re-derived (trees, tree line, first cut) carries over
  unchanged.
* **Sweep**: states in 20-yd bands of distance to the hole, nearest first; a band's new values are used by the
  bands behind it in the same sweep. 2-3 sweeps to a change under 0.002.
* **Tee shot**: the engine's own. `HoleSolve.tee_values()` writes the DP's values onto the engine's raster and
  `World.tee_solve()` runs the engine's two-stage central-world solve (3,000 swings on the whole aim grid, 16,000
  on aim +/-10, `opt/solve2.py`) on it. Same swings, same aim search, same roll and elevation as the table solve:
  only the value of the finishing spot differs.

## The calibration (the important part)

On a flat hole with no trouble the raw DP is 0.2-0.65 strokes below the engine's table (the stated patterns are
Tour-accurate; the table is Tour + 0.36 and more with distance). The table is fitted to real scoring; the DP is a
model. So every state pays a per-shot term

    c(lie, d) = table(lie, d) - min over shots of E[ 1 + table(finish) ]      (on the flat hole)

which makes the table its own fixed point there: on trouble-free ground the calibrated DP returns the table
(fairway states sd 0.003, every state within 60 yds of the line sd 0.006, worst 0.03). On a real hole what is left
is what the hole's own trouble does. `World.calibration()`; `cal=None` gives the raw DP; `run.level_cal()` is a
level-only variant (one constant per lie class, the mean of c between 40 and 200 yds: the table's level per shot
without the table's value of distance). c is charged to the state, not to the shot, so it never changes which shot
is best from a spot: it only sets the level of the values the previous shot is choosing between. Note what this
does: the calibrated DP inherits the table's value of distance on clean ground (HOLESOLVE.md section 2).

## Files

| file | what |
|---|---|
| `solver.py` | `CONFIG` (every assumption), `Bag` (swings), `Ground` (raster + table), `HoleSolve` (the DP, queries, tee values), `World` (engine, rasters, calibration, tee solve) |
| `kernel.c` | the Bellman backup in C (gcc -O3 -march=native -fopenmp, built on first use into `_build/`, ctypes) |
| `run.py` | the validation runs: `flat`, `hole10`, `par5`, `tee`, `timing` |
| `report.py` | results -> the tables of HOLESOLVE.md |
| `test_holesolve.py` | kernel against a numpy copy of its swing loop; flat hole returns the table; closed-form gone balls |
| `results/` | JSON of every run quoted in the report |

## Run

    python3 course_data/courses/holesolve/run.py flat
    python3 course_data/courses/holesolve/run.py hole10 --which truth            (truth_middle = Middle)
    python3 course_data/courses/holesolve/run.py par5 --holes 13
    python3 course_data/courses/holesolve/run.py tee --holes 1,2,3 --tag _a
    python3 course_data/courses/holesolve/run.py tee --holes 11 --vals dp_level --tag _level_11   (level-only calibration)
    python3 course_data/courses/holesolve/run.py hole10 --tall lost              (tall grass = lost ball)
    python3 course_data/courses/holesolve/run.py timing                          (one solve per hole, timed)
    python3 course_data/courses/holesolve/report.py tee                          (the report's tables from results/)
    python3 course_data/courses/holesolve/test_holesolve.py

    ... --eased            an eased 4-wood (226 / 240) joins the bag      ... --spread 1.5   every non-tee shot 50 % wider

One process per course base and rule set (the engine is activated once per process). 4 threads: a hole takes
4-13 s (one valuation) plus 2-4 s for its raster; `run.py` solves each hole twice (calibrated and raw).

**Frozen inputs.** The shared checkout moves while a study runs (hole 10's map changed between two runs of this
build). Every result quoted in the report was run on a frozen copy and carries its commit in `"state"`:

    S=<scratch>/snap_281442149; mkdir -p $S
    git archive 281442149 -- course_data/courses/v2_course.py course_data/courses/gateway_national/config.json \
        course_data/courses/gateway_national/truth/{course.py,meta.json,package.json,v2/v2_decisions.json} \
        course_data/courses/gateway_national/truth_middle/{course.py,meta.json,v2/v2_decisions.json} \
        ':(glob)spirit_hollow/*.py' ':(glob)spirit_hollow/v2/*.py' ':(glob)mozingo/*.py' \
        course_data/weather/forecast_gateway_national.json ':(glob)course_data/imagery/*.py' | tar -x -C $S
    HOLESOLVE_SNAP=$S HOLESOLVE_STATE=281442149 python3 course_data/courses/holesolve/run.py tee --holes 9,10,11 --tag _9_10_11

Without `HOLESOLVE_SNAP` the working tree is used.

## Use

    import solver as S
    W = S.World("gateway_national", "truth")          # Back; calm, 45 F (CONFIG["temp_f"])
    hs = W.solve_hole(13, cal=W.calibration())
    hs.query(294, 1, "fairway")                        # every club's best line from a spot: strokes, target, shares
    hs.value_at(480, 1, "fairway")                     # strokes to hole out from a spot
    R0 = hs.R0                                         # the engine's raster of the hole
    St = R0.strokes(W.P, W.M.HOLES[13]["length"])      # the engine's table values
    W.tee_solve(13, R0, hs.tee_values(R0, St))         # tee club and aim on the DP's values
