"""Drop-in runner: the calm-day book (v2_decisions.json) and the wind grids (wind_grid*.json) of one course, in the
engine's formats, into a SEPARATE folder (never the course's own v2/), on the C kernels.

  python3 course_data/courses/fastsolve/run.py solve --slug gateway_national --which truth \
      --request course_data/requests/nccga_v2_gateway_national.json --out /tmp/fs_gateway [--jobs 4]
  python3 course_data/courses/fastsolve/run.py solve --slug S --which W --out DIR --offsets 0,-20 --temps 35,50,65 \
      --draws 256 --refine 16000 --refine-offsets 0 [--holes 8,9] [--only decide|wind] [--engine slow]
  python3 course_data/courses/fastsolve/run.py compare --slug S --which W --out DIR [--ref <slug>/<which>/v2]

It runs the engine's own entry points (decide.main; wind_grid_v2.main with v2_course.refined_solver, exactly as
v2_course.run_decide / run_wind set them up) in forked worker processes in which fast.install() has pointed
model.ev_curve / model.Raster at kernel.c. One task = one hole of the book or one hole of one tee offset's grid;
the parts are merged as v2_course.merge does. The request file is only read. `--engine slow` runs the same tasks on
the unpatched engine (A/B and benchmark slices).
"""
import argparse
import glob
import json
import multiprocessing as mp
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
COURSES = os.path.dirname(HERE)
for p in (COURSES, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

_STATE = {}


def _activate(slug, which, engine, swings=None):
    import v2_course as vc
    course, meta, M, D = vc.activate(slug, which)
    if engine == "fast":
        import fast
        fast.THREADS = 1                     # one kernel thread per worker process: the workers are the parallelism
        fast.lib()                           # compile before the fork
        fast.install(M, D, swings=swings)
    _STATE.update(vc=vc, course=course, M=M, D=D, slug=slug, which=which)
    return course, M, D


def _slot():
    """FASTSOLVE_SLOTS=<dir>:<n>: several run.py processes (Back and Middle) share n cores. A task holds one of n
    lock files while it runs (released when the child exits), so at most n tasks run at once across all of them."""
    spec = os.environ.get("FASTSOLVE_SLOTS")
    if not spec:
        return None
    import fcntl
    d, n = spec.rsplit(":", 1)
    os.makedirs(d, exist_ok=True)
    while True:
        for k in range(int(n)):
            f = open(os.path.join(d, f"slot{k}"), "w")
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return f
            except OSError:
                f.close()
        time.sleep(0.05)


def _task(t):
    """Runs in a forked child (one task per child: a tee shift and the engine's module globals stay in it)."""
    import numpy as np
    vc, M, D = _STATE["vc"], _STATE["M"], _STATE["D"]
    slot = _slot()
    t0 = time.time()
    sys.stdout = open(t["log"], "w", buffering=1)
    sys.stderr = sys.stdout
    if t["kind"] == "decide":
        # v2_course.run_decide after activate()
        os.environ.update(V2_HOLES=str(t["hole"]), V2_DRAWS=str(t["draws"]), V2_SWINGS=str(t["swings"]),
                          V2_CENTRAL_SWINGS=str(t["central"]), V2_OUT=t["out"], V2_GEOM="")
        if t.get("parts"):
            os.environ["V2_PARTS"] = t["parts"]
        if t.get("book"):                    # book.py: the prior-draw loop on a coarser raster / shared maps / racing
            import book
            book.install(M, D, **t["book"])
        D.main()
    else:
        # v2_course.run_wind after activate()
        os.environ.update(TEE_BACK=str(t["back"]), WIND_TEMPS=",".join(str(x) for x in t["temps"]),
                          WIND_SWINGS=str(t["swings"]), WIND_OUT=t["out"], V2_GEOM="", WIND_HOLES=str(t["hole"]))
        import wind_grid as WG
        WG.osm_bearings = lambda: {}
        import wind_grid_v2 as WG2
        if getattr(D, "_aim_limit", None):
            L = float(D._aim_limit)
            WG2.AIMS = np.arange(-(L + 35.0), L + 35.0 + 1e-9, 0.5)
        WG2.TEMPS = [float(x) for x in t["temps"]]
        WG2.N = t["swings"]
        if t.get("speeds"):                  # test / benchmark slices only
            WG2.SPEEDS = [int(s) for s in t["speeds"]]
        if t.get("dirs"):
            WG2.DIRS = [int(s) for s in t["dirs"]]
        if t.get("c2f"):                     # coarse-to-fine aim sweep (fast.c2f_aim): the same records, fewer aims
            import fast
            WG2.solve = fast.wind_solve(M._fastsolve, WG2)
        if t.get("adaptive"):                # adaptive Sobol grid in one C call per (hole, temperature): adaptive.py
            import adaptive
            WG2.solve = adaptive.install(M, D, WG2, cap=t["adaptive"], n0=t.get("adaptive_n0"), min_all=t.get("adaptive_n0"),
                                         f32=t.get("f32"))
            t = dict(t, refine=0)
        if t["refine"]:
            WG2.solve = vc.refined_solver(M, D, WG2, t["refine"])
        WG2.main()
        if t.get("adaptive"):
            t = dict(t, stats=dict(adaptive.STATS))
    return dict(t, secs=time.time() - t0)


def plan(a, course, M):
    q = json.load(open(a.request)) if a.request else {}
    cfg = json.load(open(os.path.join(COURSES, a.slug, "config.json")))

    def opt(v, key, default):
        return v if v is not None else q.get(key, default)
    offsets = [float(x) for x in a.offsets.split(",")] if a.offsets else [float(x) for x in q.get("offsets", [0])]
    temps = [float(x) for x in a.temps.split(",")] if a.temps else [float(x) for x in q.get("temps", cfg["temps"])]
    draws = int(opt(a.draws, "draws", 64))
    refine = int(opt(a.refine, "refine_swings", 0))
    if a.card_only:
        offsets = [0.0]
    r_off = ([float(x) for x in a.refine_offsets.split(",")] if a.refine_offsets
             else [float(x) for x in q.get("refine_offsets", [0])])
    order = [str(k) for k in course.ORDER if k in course.HOLES]
    d_holes = a.holes.split(",") if a.holes else ([str(h) for h in q["holes"]] if q.get("holes") else order)
    w_holes = a.holes.split(",") if a.holes else ([str(h) for h in q["wind_holes"]] if q.get("wind_holes") else order)
    parts = os.path.join(a.out, "parts")
    os.makedirs(parts, exist_ok=True)
    tasks = []
    if a.only in (None, "decide"):
        for h in d_holes:
            tasks.append(dict(kind="decide", hole=h, draws=draws, swings=a.swings_decide, central=a.central,
                              parts=a.decide_parts, out=os.path.join(parts, f"v2dec_{h}.json"),
                              book=(dict(res=a.book_res, maps=a.book_maps, race=a.book_race)
                                    if a.engine == "fast" and (a.book_res or a.book_maps or a.book_race) else None),
                              log=os.path.join(parts, f"log_dec_{h}.txt")))
    if a.only in (None, "wind"):
        for b in offsets:
            for h in w_holes:
                tasks.append(dict(kind="wind", hole=h, back=b, temps=temps, swings=a.swings_wind,
                                  refine=refine if b in r_off else 0, speeds=a.speeds, dirs=a.dirs,
                                  c2f=bool(a.c2f and a.engine == "fast"),
                                  adaptive=(a.adaptive_cap if b in r_off else a.adaptive_cap_other) if a.adaptive else 0,
                                  adaptive_n0=None if b in r_off else a.adaptive_n0_other,
                                  f32=a.f32,
                                  out=os.path.join(parts, f"v2wind_{b:g}_{h}.json"),
                                  log=os.path.join(parts, f"log_wind_{b:g}_{h}.txt")))
    return tasks, order


def merge(out, order):
    """v2_course.merge, into `out` (parts under out/parts)."""
    parts = os.path.join(out, "parts")
    dec = {}
    for p in sorted(glob.glob(os.path.join(parts, "v2dec_*.json"))):
        dec.update(json.load(open(p)))
    if dec:
        old = os.path.join(out, "v2_decisions.json")
        merged = json.load(open(old)) if os.path.exists(old) else {}
        merged.update(dec)
        json.dump({k: merged[k] for k in order if k in merged}, open(old, "w"), indent=1)
        print("v2_decisions:", len(dec), "holes")
    grids = {}
    for p in sorted(glob.glob(os.path.join(parts, "v2wind_*.json"))):
        d = json.load(open(p))
        if d["back"] not in grids:
            prev = os.path.join(out, "wind_grid.json" if not d["back"] else f"wind_grid_back{d['back']:+.0f}.json")
            base = json.load(open(prev)) if os.path.exists(prev) else {}
            same = base.get("speeds") == d["speeds"] and base.get("dirs") == d["dirs"]
            grids[d["back"]] = dict(speeds=d["speeds"], dirs=d["dirs"], temps=list(base.get("temps", [])) if same else [],
                                    bearings=dict(base.get("bearings", {})) if same else {},
                                    holes=dict(base.get("holes", {})) if same else {},
                                    par3=dict(base.get("par3", {})) if same else {}, tee_back=d["back"], model="v2")
        g = grids[d["back"]]
        g["temps"] = sorted(set(g["temps"]) | set(d.get("temps", [])))
        for h, byT in d["holes"].items():
            g["holes"].setdefault(h, {}).update(byT)
        g["bearings"].update(d["bearings"])
        g["par3"].update(d["par3"])
    for b, g in grids.items():
        g["holes"] = {k: g["holes"][k] for k in order if k in g["holes"]}
        name = "wind_grid.json" if not b else f"wind_grid_back{b:+.0f}.json"
        json.dump(g, open(os.path.join(out, name), "w"))
        print(name, len(g["holes"]), "holes", g["temps"])


def solve(a):
    out = os.path.abspath(a.out)
    v2dir = os.path.join(COURSES, a.slug)
    if os.path.commonpath([out, v2dir]) == v2dir:
        sys.exit("refusing to write inside the course's own folder: choose a separate --out")
    a.out = out
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    course, M, D = _activate(a.slug, a.which, a.engine, a.swings)
    tasks, order = plan(a, course, M)
    jobs = a.jobs or os.cpu_count()
    print(f"{len(tasks)} tasks ({sum(t['kind'] == 'decide' for t in tasks)} decide, "
          f"{sum(t['kind'] == 'wind' for t in tasks)} wind), {jobs} processes, engine {a.engine}", flush=True)
    done = []
    with mp.get_context("fork").Pool(jobs, maxtasksperchild=1) as pool:
        # longest first: the book and the refined grids, then the coarse grids
        tasks.sort(key=lambda t: (t["kind"] != "decide", not t.get("refine")))
        for r in pool.imap_unordered(_task, tasks, chunksize=1):
            done.append(r)
            what = f"decide {r['hole']}" if r["kind"] == "decide" else f"wind {r['back']:+g} hole {r['hole']}"
            print(f"  [{len(done)}/{len(tasks)}] {what}: {r['secs']:.1f}s  (elapsed {time.time() - t0:.0f}s)", flush=True)
    merge(out, order)
    wall = time.time() - t0
    json.dump(dict(slug=a.slug, which=a.which, engine=a.engine, swings=a.swings or "mc", jobs=jobs, wall_s=round(wall, 1),
                   task_cpu_s=round(sum(r["secs"] for r in done), 1),
                   tasks=[dict(kind=r["kind"], hole=r["hole"], back=r.get("back"), refine=r.get("refine"), stats=r.get("stats"),
                               secs=round(r["secs"], 2)) for r in done]),
              open(os.path.join(out, "run_meta.json"), "w"), indent=1)
    print(f"done in {wall:.0f}s -> {out}")


# ------------------------------------------------------------------------------------------------ compare
def _num_diff(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append((path + "/" + k, "missing in " + ("out" if k not in a else "ref"), None))
            else:
                _num_diff(a[k], b[k], path + "/" + k, out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((path, f"len {len(a)} vs {len(b)}", None))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                _num_diff(x, y, f"{path}[{i}]", out)
    elif isinstance(a, bool) or isinstance(b, bool) or isinstance(a, str) or isinstance(b, str) or a is None or b is None:
        if a != b:
            out.append((path, f"{a!r} vs {b!r}", None))
    else:
        if a != b:
            out.append((path, f"{a!r} vs {b!r}", abs(float(a) - float(b))))


def compare(a):
    ref = a.ref or os.path.join(COURSES, a.slug, a.which, "v2")
    names = sorted(os.path.basename(p) for p in glob.glob(os.path.join(a.out, "*.json"))
                   if os.path.basename(p) != "run_meta.json")
    total = 0
    for n in names:
        if not os.path.exists(os.path.join(ref, n)):
            print(n, ": not in", ref)
            continue
        x, y = json.load(open(os.path.join(a.out, n))), json.load(open(os.path.join(ref, n)))
        if n.startswith("wind_grid"):
            x = dict(x, holes={h: v for h, v in x["holes"].items()})
            y = dict(y, holes={h: {T: c for T, c in v.items() if T in x["holes"][h]}
                               for h, v in y["holes"].items() if h in x["holes"]},
                     temps=x["temps"], bearings={k: v for k, v in y["bearings"].items() if k in x["bearings"]})
            for h in x["holes"]:
                for T in x["holes"][h]:
                    if h in y["holes"] and T in y["holes"][h]:
                        y["holes"][h][T] = {k: v for k, v in y["holes"][h][T].items() if k in x["holes"][h][T]}
        else:
            y = {h: v for h, v in y.items() if h in x}
        d = []
        _num_diff(x, y, "", d)
        num = [e for e in d if e[2] is not None]
        oth = [e for e in d if e[2] is None]
        print(f"{n}: {'IDENTICAL' if not d else 'DIFFERENT'} to {ref} "
              f"({len(num)} numbers differ, max |diff| {max((e[2] for e in num), default=0):.3g}; "
              f"{len(oth)} other differences)")
        for e in (oth + sorted(num, key=lambda e: -e[2]))[:a.show]:
            print("   ", e[0], e[1])
        total += len(d)
    return total


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["solve", "compare"])
    ap.add_argument("--slug", required=True)
    ap.add_argument("--which", default="truth")
    ap.add_argument("--out", required=True)
    ap.add_argument("--request", help="course_data/requests/nccga_v2_<slug>.json (read only): offsets, temps, draws, "
                                      "refine_swings, refine_offsets, holes")
    ap.add_argument("--offsets")
    ap.add_argument("--temps")
    ap.add_argument("--holes", default="")
    ap.add_argument("--draws", type=int, help="prior draws (default 64 = saturation; --exact: the request's)")
    ap.add_argument("--refine", type=int)
    ap.add_argument("--refine-offsets")
    ap.add_argument("--only", choices=["decide", "wind"])
    ap.add_argument("--decide-parts", default="", help="V2_PARTS, e.g. bayes (default: bayes,ladder,sens,sweep)")
    ap.add_argument("--speeds", default="", help="wind speeds (test slices; default the engine's 0..25)")
    ap.add_argument("--dirs", default="", help="wind directions (test slices; default every 30 deg)")
    ap.add_argument("--swings-decide", type=int, default=512)
    ap.add_argument("--central", type=int, default=2048)
    ap.add_argument("--swings-wind", type=int, default=2500)
    ap.add_argument("--jobs", type=int, default=0)
    ap.add_argument("--engine", choices=["fast", "slow"], default="fast")
    ap.add_argument("--swings", choices=["mc", "sobol", "antithetic"], default="sobol",
                    help="opt-in swing set (fast engine only). mc = the engine's (default, identical outputs); sobol = "
                         "scrambled Sobol points: NOT the engine's numbers, ~8x less Monte Carlo noise (README)")
    ap.add_argument("--c2f", type=int, default=1, help="1 (default): coarse-to-fine aim sweep in the wind grids "
                                                       "(same records as the full sweep); 0: every aim")
    ap.add_argument("--adaptive", type=int, default=1, help="1: adaptive Sobol wind grids (adaptive.py): NOT the "
                                                            "engine's numbers; see README")
    ap.add_argument("--adaptive-cap", type=int, default=8192, help="swing cap, refined (card-tee) offsets")
    ap.add_argument("--adaptive-n0-other", type=int, default=None, help="first-stage swings, the other offsets (512)")
    ap.add_argument("--adaptive-cap-other", type=int, default=2048, help="swing cap, the other offsets")
    ap.add_argument("--book-res", type=float, default=1.0, help="raster cell (yds) of the book's prior-draw maps and "
                    "value rasters (book.py; 0 = the engine's 0.5)")
    ap.add_argument("--book-maps", type=int, default=16, help="book: K jittered maps per hole shared by the prior "
                    "draws (book.py; 0 = a map per draw)")
    ap.add_argument("--book-race", type=int, default=1, help="book: 1 = stop simulating clearly worse clubs after "
                    "16 draws (book.py)")
    ap.add_argument("--f32", type=int, default=None, help="1: float32 lanes (16 aims per register) in the adaptive "
                    "wind grids: ~30 %% less time, picks unchanged, an aim moves 0.5 yd in ~2 cells per 1,000 (README)")
    ap.add_argument("--ref")
    ap.add_argument("--show", type=int, default=8)
    ap.add_argument("--card-only", action="store_true", help="no offset grids: the book and the card-tee grid only")
    ap.add_argument("--exact", action="store_true", help="the engine's own numbers: random swings, the request's "
                    "draws, 3,000 / 12,000 swings, full refined grids (identical to Actions)")
    a = ap.parse_args()
    if a.exact:
        a.swings, a.adaptive, a.swings_decide, a.central = "mc", 0, 3000, 12000
        a.book_res, a.book_maps, a.book_race = 0, 0, 0
    elif a.draws is None:
        a.draws = 64
    a.speeds = [s for s in a.speeds.split(",") if s]
    a.dirs = [s for s in a.dirs.split(",") if s]
    if a.cmd == "solve":
        solve(a)
    else:
        sys.exit(1 if compare(a) else 0)


if __name__ == "__main__":
    main()
