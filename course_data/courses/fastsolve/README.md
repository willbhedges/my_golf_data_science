# fastsolve: the tee-strategy solver in C

Built ALONGSIDE the engine: nothing outside this folder is edited, nothing is wired in. Two things live here:

1. **The exact kernel** (`kernel.c` + `fast.py`): the engine's per-ball loops in C. Same numbers as the engine,
   bit for bit on this box, and equal to the Actions rev 7 solve of Gateway to the last float bit or two.
2. **The adaptive Sobol solver** (`adaptive.py`, `run.py --adaptive 1 --swings sobol`): fewer, better-placed
   swings and a stopping rule. Different numbers from the engine by design (less Monte Carlo noise).

| Full Gateway solve (Back book + 10 offset grids, Middle book + card grid), 4 CPUs | wall time |
|---|---|
| Actions (engine, ~20 runners) | ~1 h 45 min |
| exact kernel, `run.py` | 873 s (Back 600 s, Middle 273 s) |
| adaptive Sobol, `run.py --adaptive 1 --swings sobol ...` | **183 s** (Back 113 s, Middle 70 s) |

The 1-minute target was not reached. Outputs of the 183 s run, in the engine's file format:
`solved/gateway_national/truth/v2/` and `solved/gateway_national/truth_middle/v2/`.

## 1. Profile of the existing engine (one process, this box)

Engine = `spirit_hollow/v2/model.py` + `decide.py` + `wind_grid_v2.py` through `v2_course.py`. Gateway Back hole 8.

The brief said the slow part is a polygon test per simulated ball. It is not: the engine already paints the lies
into a 0.5-yd raster (`model.Raster`, 881 x 601 cells). What is slow is numpy around a per-ball loop:

| piece | time | share |
|---|---|---|
| **one refined wind cell** (7 clubs x (381 aims x 2,500 + 41 aims x 16,000 swings) = 11.3 M balls) | **3.06 s** | |
| `model.finish` (roll every ball out in 2-yd steps, a raster lookup per step) | 2.84 s | 93 % |
| of which `Raster.lie_at` / `idx` | 1.18 s | 39 % |
| of which full-array temporaries per roll step (`a + ua * st`, `np.where`, masks) | 1.4 s | 46 % |
| **decide.bayes, per prior draw** (6.7 M balls) | **3.35 s** | |
| `ev_curve` -> `finish` | 2.19 s | 65 % |
| `model.Raster(hd, map_seed)`: the map repainted for the draw's jitter | 1.03 s | 31 % |
| of which `matplotlib.Path.contains_points` (530 k cells x ~40 zones) | 0.82 s | 25 % |
| `Raster.strokes` | 0.10 s | 3 % |

Eagle Knoll (lidar flight-through-crowns): one refined cell of hole 14 takes 28.6 s, 26 s of it in
`v2_course.lidar_flight_ev_curve`.

## 2. The exact kernel

`kernel.c` (gcc -O3 -march=native -ffp-contract=off -fopenmp, loaded with ctypes; compiled on first use into
`_build/`). `fast.install(M, D)` points THIS PROCESS's `model.ev_curve` and `model.Raster` at it; every engine entry
point then runs unchanged on top, so the output formats are the engine's by construction.

- `fs_ev`: landing -> roll-out -> strokes lookup, summed per aim in swing order. AVX-512: 8 aims per register, 32
  aims of one swing per group. Includes the lidar crown trace (Eagle Knoll). Scalar path for other CPUs and for the
  per-ball outputs.
- `fs_fill` / `fs_fill_rect` / `fs_fill_band`: zone polygons into the lie raster with matplotlib's point-in-path
  arithmetic; per prior draw only the band along each shifted outline is re-tested.
- `fs_water_entry`, `fs_blocked`, `fs_strokes` (value raster incl. green putting; numpy's `interp` formula).
- `decide.bayes` runs unchanged: the three means it takes come from kernel sums through a lazy proxy.
- Coarse-to-fine aim sweep in the wind grids (`fast.c2f_aim`): same records, ~20 % less time.

Why it is exact: the same IEEE operations in the same order, no fused multiply-add, no fast-math; `hypot` is
glibc's algorithm written out and checked against the running libm at load (falls back to libm if they differ).

### Equivalence on this box (engine vs kernel, same process inputs)

| compared | result |
|---|---|
| Gateway Back, all 13 holes x 3 temps x {0, 5, 10 mph} x 4 directions, refined (351 cells) | JSON identical |
| Gateway Back hole 8 full decide (16 draws + ladder + sensitivities + sweep + shares) | JSON identical |
| Gateway Back holes 10, 16 `decide.bayes`, 32 prior draws | JSON identical |
| Eagle Knoll Back, all 14 holes x 50 F x {0, 10 mph x 4 directions}, refined (70 cells) | JSON identical |
| Eagle Knoll Back holes 9, 14, 15 `decide.bayes`, 8 draws | JSON identical |
| rasters (lie, entry_dist, blocked, native_depth), 13 holes x base + jittered maps | equal |
| strokes raster, 76 worlds (central, v1 ladder worlds, tour table, prior draws) | equal |

Not run: the engine at 256 draws on every hole (hours). The Actions comparison below covers that for Gateway.
One Eagle Knoll slice (temps 35 / 65 on 3 holes) failed to run because of my own bad arguments and was not redone.

### Acceptance against Actions

| Actions run | fastsolve vs committed outputs |
|---|---|
| rev 7, cee080946 (final map), Back: book + 11 grids, 23,790 cells | 0 differences above 1e-9; 4,775 numbers differ in the last float bit (max 3.6e-15) |
| rev 7, Middle: book + card grid, 2,379 cells | 0 differences above 1e-9; 754 last-bit differences |
| rev 6, 57dae0081 (map 222f7ece4) | 10 holes identical in all 13 files; 2 / 3 / 5 identical on a 0 / 10 mph sample |

The last-bit differences are numpy summation on the runner's CPU against this box (margin_se, crossfit, some cell
EVs); every pick, runner, aim, window and at_bound is identical. Note for rev 6: the `course.py` that Actions run
committed was re-prepared on the later map, so 2 / 3 / 5 only match with 222f7ece4's own `course.py`.

The engine's own seed noise (5 seeds, refined calm cell, all 13 holes): no pick flips; pick aim range median 1.0 yd,
max 2.0; EV sd median 0.0008, max 0.0026.

### Speed, exact kernel

| | engine | kernel | factor |
|---|---|---|---|
| refined wind cell, one core | 3.06 s | 0.15 s | ~20 |
| prior draw of the book, one core | 3.35 s | 0.17 s, later ~0.12 s | ~20-28 |
| full decide of hole 8 (16 draws) | 359 s | 12.7 s | 28 |
| Eagle Knoll, 14 holes x 5 refined cells (CPU-s) | 1,852 | 74 | 25 |
| per ball, one core | ~270 ns | 5-20 ns (fairway balls roll 13 steps) | |

A Back solve is about 200 billion balls (offset grids 143 G, card grid 27 G, book 32 G). At 8-20 ns a ball the
exact kernel cannot go under several minutes: the rest has to come from fewer balls.

## 3. The adaptive Sobol solver

Three changes, all behind flags:

- **Sobol swings** (`--swings sobol`, `fast.sobol_draws`): scrambled Sobol points in the 5 swing dimensions
  instead of independent draws.
- **Adaptive wind grids** (`--adaptive 1`, `adaptive.py` -> `fs_grid`): one C call per (hole, offset,
  temperature) does every cell and club. Per cell: coarse basin search (128 swings, 3-yd aims; every basin within
  0.04 strokes is kept), 0.5-yd window on 512 swings, racing on paired block differences (a club worse than the
  leader by more than max(3, t) SE is dropped), then doubling until the runner-up is separated at 99 % and the
  leader's aim (block jackknife) is within +/-1 yd at 99 %, or the cap. Cells that reach the cap unseparated
  carry `tie: true`.
- **Fewer swings where Sobol makes them unnecessary**: 512 per prior draw, 2,048 for the central worlds.

### Convergence (30 replications, converged answer = 1 M Sobol swings; `converge.py`, `converge_gateway.json`)

Smallest N meeting each criterion at that N and every larger N tested:

| hole (converged pick, margin) | pick right >= 99 % | aim within 1 yd >= 99 % | margin SE < 0.002 |
|---|---|---|---|
| 8 (Driver, 0.045) | random 128, Sobol 128 | random 32,768, Sobol 8,192 | random 4,096, Sobol 1,024 |
| 10 (2-wood, 0.018) | random 2,048, Sobol 512 | random > 32,768, Sobol 4,096 | random > 32,768, Sobol 4,096 |
| 16 (4-wood, 0.102) | random 128, Sobol 128 | random 8,192, Sobol 2,048 | random 32,768, Sobol 1,024 |
| 13 (Driver, 0.129) | random 128, Sobol 128 | random 32,768, Sobol 4,096 | random 16,384, Sobol 2,048 |

With 30 replications ">= 99 %" means all 30. Today's 16,000 random swings give an aim sd of 0.4-0.8 yd; Sobol 4,096
gives 0.3-0.7. So Sobol 4,096 is at least today's refine precision, and the pick is settled by a few hundred
swings; it is the +/-1 yd aim rule that sends most cells to the cap.

Not done: the saturation point for the number of prior draws (256 today). Antithetic pairs were tried on hole 10
only and did not help the EV (sd 0.0071 against 0.0049 for plain random at 16k).

### Agreement of the 183 s solve with Actions rev 7

- Book: same club on all 26 holes (Back + Middle), aims within 0.5 yd, margins within 0.002.
- Back wind grids, 23,790 cells: club differs in 357 (1.5 %). All but one are flagged tie or have a reference
  margin <= 0.02. The one clear disagreement: offset -80, hole 16, 50 F, 15 mph from 300: fastsolve Driver by 0.025
  (1,024 Sobol swings), rev 7 2-wood by 0.023 (2,500 random swings). I did not adjudicate it with a long run.
- 2,460 Back cells are flagged tie.
- Middle card grid, 2,379 cells: 18 club differences, none clear; aim differs by more than 1 yd in 4 %, more than
  2 yd in 0.3 %.
- Back including the nine offset grids: aim differs by more than 1 yd in 27 % of cells, more than 2 yd in 8 %.
  Those nine reference grids are 2,500 random swings, whose own aim sd is 2-3.5 yd.

Where the 183 s goes: books 459 CPU-s (map repaint + value raster, ~70 ms a draw x 6,656 draws), wind 229 CPU-s
(11 G balls). The per-draw raster is the floor now.

### 3-hole timings (8, 10, 16; seconds per hole, one process per hole)

| | exact kernel | adaptive Sobol |
|---|---|---|
| book (256 draws + ladder + sensitivities + sweep) | 40.9 | ~23 before the band repaint (not re-timed after) |
| refined card grid (183 cells) | 25.6 | 2.3 (cap 4,096) |
| one offset grid (183 cells) | 7.7 | 2.0 at cap 4,096; cap 1,024 used in the full run |

## 4. On demand

`ondemand.py`: one temperature / wind speed / wind direction, all 13 Gateway tee shots, no grid interpolation.
Exact kernel (2,500 + 16,000 swings): 1.07 s. Sobol 512 + 4,096: 0.42 s. Start-up (imports, map, rasters) is 2 s
on top unless the process stays alive.

## 5. Evaluated and rejected (`experiments.py`)

- **Aim sweep as a convolution.** The roll-out runs along each ball's own line from the tee and changes with the
  lies it crosses, so a finish is not the aim-0 finish shifted sideways: doing that moves EVs by 0.08-0.18 strokes
  and aims by up to 12 yds (holes 8, 10). A landing-value raster (roll-out from the landing cell centre, roll
  rounded to 1 yd) is closer: max EV error 0.0007-0.0051, aim moved 0.5 yd on 2 of 6 curves. Not adopted.
- **fast-math / FMA** (`-Ofast -ffp-contract=fast`): no faster (x0.71 in one noisy run), curves differ by up to
  2.7e-15, no aim changes. Rejected: nothing gained.
- **float32**: not tried.
- **Mirrored wind directions sharing one sweep**: skipped on instruction.

## 6. How to run

```
# exact (the engine's numbers), outputs into a separate folder
python3 course_data/courses/fastsolve/run.py solve --slug gateway_national --which truth \
    --request course_data/requests/nccga_v2_gateway_national.json --out /tmp/fs_gateway
# adaptive Sobol (the 183 s configuration)
python3 course_data/courses/fastsolve/run.py solve --slug gateway_national --which truth \
    --request course_data/requests/nccga_v2_gateway_national.json --out DIR --swings sobol \
    --swings-decide 512 --central 2048 --adaptive 1 --adaptive-cap 4096 --adaptive-cap-other 1024
python3 course_data/courses/fastsolve/run.py compare --slug gateway_national --out DIR [--ref OTHER_DIR]
python3 course_data/courses/fastsolve/ondemand.py --temp 41 --wind 12 --from 200
python3 -m pytest -q course_data/courses/fastsolve/test_fastsolve.py        # 85 s, exact kernel vs engine
```

`run.py` refuses to write inside a course folder. `--engine slow` runs the same tasks on the unpatched engine.
Other scripts: `bench.py`, `equiv.py seeds`, `noise.py`, `converge.py`, `experiments.py`.

## 7. Known differences and limits

- Exact path: identical to the engine on this box; against another CPU, last-bit differences in a few summed
  statistics.
- Adaptive path: wind cells carry extra fields (`n_swings`, `margin_se`, `tie`, `aim_se`, `aim_ok`, per-club `n`).
  The aim is the minimum of the smoothed curve by a parabola, not the engine's spline + Brent; the zone is clipped
  to the evaluated window. Clubs dropped early are reported from 512 swings.
- With Sobol swings `decide.bayes`'s `swing_noise_share` compares two halves of one Sobol set, not two independent
  halves.
- The adaptive grid has no lidar crown trace: on Eagle Knoll `--adaptive` falls back to the exact kernel.
- Times assume AVX-512. The scalar path is what the first measurements used (about 3x slower per ball); the scalar
  branch of `fs_grid` has not been run.
- The legacy constant-height flight-tree check is not ported (falls back to the engine's function).
- Tests cover the exact kernel only; the adaptive solver has no test yet.

## 8. Before it replaces the Actions solve

- A test for the adaptive path, and one run of its scalar branch (GitHub runners are mostly AVX2).
- Crown trace in `fs_grid` for Eagle Knoll-type courses.
- The prior-draw saturation study, and a cheaper per-draw raster if the book is to go under ~1 minute.
- A decision on the stopping rule: most cells hit the cap on the +/-1 yd aim rule.
- Page build and the par-3 target solve were not profiled.
