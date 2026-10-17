"""Course package -> the golfer's deliverables, for any course.

  python3 course_data/product/plan.py --package course_data/packages/<slug>/package.json --tees Black [--quick]

Writes to course_data/packages/<slug>/out/ (or --out):
  <Name>_Strategy.pdf      the strategy book (cover card + one page per hole)
  <Name>_Aim_Sheets.pdf    one phone page per hole: the image, a star, one line of words
  wind_page/index.html     the interactive wind caddie (single self-contained page)
  decision.json / .md      club + aim per tee shot (quick: point estimate; full: Bayesian with margins)
  wind_grid.json           best club/aim for 61 winds on every tee shot (feeds the page)
  forecast.json            hourly forecast for the course (fetched on Actions), when available
  course.py                the generated course module (HOLES/PAR3/... in each hole's pixel frame)
  screenshots/holeNN.jpg   clean NAIP image per hole in that frame (+ index.json)
  plan.json                manifest: inputs, stage timings, files, picks, data gaps and per-hole badges

Badges (research/auto_course_lookup.md section 8): when out/review/review.json exists (verify.py, the 2-minute
check), each hole's label gets \u2713 auto / \u25d0 checked by you / \u26a0 unverified, the unverified holes' notes
open with the open question and what changes if the map is wrong, and the cover lists them.

Steps: 1 package -> course module (package.py), 2 NAIP render per hole (imagery.py), 3 decision
(decide.py: --quick = prior-mean point estimate; default/--full = Bayesian, --draws 32-128 Sobol draws),
4 book + aim sheets (book.py -> mozingo/yardage_book), 5 forecast + wind grid + page (forecast.py,
wind_page.py), 6 manifest.

Inputs accepted by --package: a package/1 package.json (course_data/platform), or a v1 course_model/1
holes.json (pipeline.py). --course "<name>" instead builds a stand-in package offline with
course_data/pipeline.build_course (for courses whose OSM/scorecard/tee files are already fetched).

Tee line: tee -> the point on the hole line 250 yds out (62% of the hole at most), so aims read as yards
left/right of a line over the landing area: course_data/platform/tee_line.py, the same rule the platform
uses for the package's aim_ll (package.TEE_LINE; 'package' uses the package's aim_ll as given).

Absurd-aim guard (decide.aim_problems): a best aim more than 40 yds off the line, on the search edge, whose
aim point is not fairway / first cut / rough, or that is more than 40 yds from the hole's line of play makes
the hole CHECK (plan.json picks[k].status, "Hole N CHECK" in the book); the best printable aim is shown.

Request-file trigger (GitHub Actions, .github/workflows/plan_course.yml): commit
course_data/product/requests/<slug>.json = {"package": "<path>", "tees": "Black", "mode": "quick"|"full"}.
"""
import argparse
import datetime as dt
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
sys.path.insert(0, HERE)

import package as PK                                # noqa: E402

T0 = time.time()
TIMES = {}


def log(*a):
    print(f"[{time.time() - T0:6.1f}s]", *a, flush=True)


class stage:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.t = time.time()
        log(f"== {self.name}")

    def __exit__(self, *exc):
        TIMES[self.name] = round(time.time() - self.t, 1)


def prefix_for(name):
    short = name
    for w in (" Golf Course", " Golf Club", " Country Club", " Golf Links", " GC", " CC"):
        short = short.replace(w, "")
    return "".join(ch if ch.isalnum() else "_" for ch in short.strip()).strip("_") or "Course"


def write_decision(results, mod, out, mode):
    with open(os.path.join(out, "decision.json"), "w") as fh:
        json.dump({str(k): v for k, v in results.items()}, fh, indent=1, default=float)
    lab = mod.LABELS
    head = ("Quick mode: the strategy model at the central settings of the Bayesian prior (driver pattern 70 "
            "yds, depth x1.25, trees 0.8, half of long-grass balls lost, 15% mishits, tour baselines)."
            if mode == "quick" else
            f"Full Bayesian run: {next(iter(results.values())).get('S')} Sobol prior draws x "
            f"{next(iter(results.values())).get('N')} swings (spirit_hollow/final_decision.py settings). "
            "Margin = expected strokes saved vs the next club; cross-fitted = corrected for picking the "
            "best of a noisy grid; P(best) = noise-corrected share of plausible worlds where the pick wins.")
    md = [f"# {mod.NAME} ({mod.TEE_SET} tees): tee-shot decisions", "", head, "",
          "| Hole | Par | Yds | Pick | Aim (yds, +R) | Zone | Runner-up | Margin | " +
          ("Cross-fitted | P(best) | Width break-even |" if mode == "full" else "Fairway | Approach |"),
          "|---|---|---|---|---|---|---|---|---|---|" + ("---|" if mode == "full" else "")]
    for k, r in results.items():
        hd = mod.HOLES[k]
        c = r["clubs"][r["pick"]]
        row = (f"| {lab.get(k, k)} | {hd['par']} | {hd['length']} | **{r['pick']}**{' (tie)' if r['tie'] else ''}"
               f"{' **CHECK**' if r.get('check') else ''} | "
               f"{r['aim']:+.1f} | {r['zone'][0]:+.0f} to {r['zone'][1]:+.0f} | {r['runner']} | {r['margin']:.3f} | ")
        if mode == "full":
            fl = "; ".join(f"{f['frm']}->{f['to']} at {f['width']:.0f}" for f in r.get("width_flips", [])) or "none 55-90"
            row += f"{r['crossfit_margin']:.3f} | {r['conf']}% | {fl} |"
        else:
            row += f"{c['share']['fairway'] + c['share'].get('first_cut', 0):.0%} | {c['approach']:.0f} |"
        md.append(row)
    chk = [(k, r["check"]) for k, r in results.items() if r.get("check")]
    if chk:
        md += ["", "## CHECK (absurd-aim guard: look at the map before playing these)", ""]
        md += [f"- {lab.get(k, k)}: " + "; ".join(why) for k, why in chk]
    with open(os.path.join(out, "decision.md"), "w") as fh:
        fh.write("\n".join(md) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--package", help="package.json (package/1) or holes.json (course_model/1)")
    src.add_argument("--course", help='stand-in: build the package offline with pipeline.py, e.g. "Spirit Hollow"')
    ap.add_argument("--tees", default=None, help="tee set (name or alias), e.g. Black")
    ap.add_argument("--quick", action="store_true", help="prior-mean point estimate (minutes)")
    ap.add_argument("--mode", choices=["quick", "full"], default=None, help="default full unless --quick")
    ap.add_argument("--draws", type=int, default=int(os.environ.get("PLAN_DRAWS", 64)), help="full: Sobol draws (32-128)")
    ap.add_argument("--swings", type=int, default=3000, help="full: swings per draw")
    ap.add_argument("--out", help="output dir (default course_data/packages/<slug>/out)")
    ap.add_argument("--forecast", default="auto",
                    help="auto (fetch on Actions, else a committed forecast within 5 km) | fetch | none | <file>")
    ap.add_argument("--days", default=os.environ.get("DAYS"), help="forecast days YYYY-MM-DD,... (default: next Sat,Sun)")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--no-wind", action="store_true")
    ap.add_argument("--no-book", action="store_true")
    a = ap.parse_args(argv)
    mode = a.mode or ("quick" if a.quick else "full")
    gaps = []

    # 1. package -> course ---------------------------------------------------------------------------
    with stage("1 package -> course module"):
        if a.course:
            sys.path.insert(0, CD)
            import pipeline
            slug = pipeline.slugify(a.course)
            pkg_path = os.path.join(HERE, "standin", slug, "package.json")
            PK.standin_from_pipeline(a.course, a.tees or "white", pkg_path)
            gaps.append(f"package: stand-in built by pipeline.build_course({a.course!r}) (no platform package.json)")
        else:
            pkg_path = a.package
        C = PK.load(pkg_path, a.tees)
        out = os.path.abspath(a.out or os.path.join(CD, "packages", C.slug, "out"))
        os.makedirs(out, exist_ok=True)
        log(f"{C.name} ({C.slug}), {C.tee_set} tees: {len(C.holes)} tee shots + {len(C.par3)} par 3s from {C.source}")
        for k, fl in C.flags.items():
            if any("skipped" in f for f in fl):
                gaps.append(f"hole {k}: " + "; ".join(fl))
        clamped = {}
        for c_, raw, cl in PK.ELEV_CLAMPED:
            clamped.setdefault(c_, 0)
            clamped[c_] += 1
        if clamped:
            gaps.append("elevation: package adjustments clamped (carry +/-30, roll x0.4-2, kick +/-15 yds) for "
                        + ", ".join(f"{c_} on {n} holes" for c_, n in clamped.items()))
        stages = (C.package.get("stages") or {})
        for s_, v in stages.items():
            if str(v).startswith(("missing", "failed", "skipped")):
                gaps.append(f"package stage {s_}: {v}")
        mod_path = os.path.join(out, "course.py")
        PK.write_module(C, mod_path)

    # 2. imagery -------------------------------------------------------------------------------------
    with stage("2 NAIP render per hole"):
        import imagery
        shots = os.path.join(out, "screenshots")
        if os.path.isdir(shots):
            shutil.rmtree(shots)
        index = imagery.render_all(C, shots, log=log)
        log(f"{len(index)} images, {sum(v['bytes'] for v in index.values()) / 1e6:.1f} MB, "
            f"imagery {next(iter(index.values())).get('imagery_date')}")

    # 3. decision ------------------------------------------------------------------------------------
    with stage(f"3 decision ({mode})"):
        import decide
        mod = PK.import_module(mod_path)
        kw = dict(n=8000) if mode == "quick" else dict(S=a.draws, N=a.swings)
        results = decide.run(mod.HOLES, mode, workers=a.workers, log=log, **kw)
        checks = {k: r["check"] for k, r in results.items() if r.get("check")}
        for k, why in checks.items():                      # absurd-aim guard (decide.aim_problems): never silent
            gaps.append(f"hole {k}: CHECK - " + "; ".join(why))
            C.labels[k] = f"{C.labels.get(k, k)} CHECK"
        import book
        badge = {}
        rv_path = os.path.join(out, "review", "review.json")
        if os.path.exists(rv_path):                        # the 2-minute check (verify.py): per-hole badges
            try:
                import verify
                badge = verify.badges(C.package, json.load(open(rv_path)))
            except Exception as e:                         # noqa: BLE001
                log(f"  ! badges skipped: {type(e).__name__}: {e}")
        for ref, b in badge.items():
            k = PK.key_of(ref)
            if k in C.holes or k in C.par3:
                lab = str(C.labels.get(k, k)).split(" ", 1)     # badge right after the number ("10 \u26a0 CHECK")
                C.labels[k] = " ".join([lab[0], b["symbol"]] + lab[1:])
        book.set_badges(badge)
        notes, aim_at = book.notes_and_aims(C.holes, C.par3, results, C.flags)
        PK.write_module(C, mod_path, notes=notes, aim_at=aim_at)
        mod = PK.import_module(mod_path)
        write_decision(results, mod, out, mode)

    # 4. book ----------------------------------------------------------------------------------------
    prefix = prefix_for(C.name)
    files = ["course.py", "decision.json", "decision.md", "screenshots/"]
    if not a.no_book:
        with stage("4 book + aim sheets"):
            rows, pdfs = book.build(mod, out, prefix, results, log=log)
            files += pdfs

    # 5. wind ----------------------------------------------------------------------------------------
    fc, fc_src = None, None
    if not a.no_wind:
        with stage("5 forecast + wind grid + page"):
            import forecast
            days = a.days.split(",") if a.days else None
            lat, lon = C.center
            if a.forecast in ("auto", "fetch") and (a.forecast == "fetch" or os.environ.get("GITHUB_ACTIONS")):
                try:
                    fc = forecast.fetch(lat, lon, C.name, days)
                    fc_src = "Open-Meteo (fetched now)" if fc else None
                except Exception as e:                             # noqa: BLE001
                    log(f"  ! forecast fetch failed: {type(e).__name__}: {e}")
            if fc is None and a.forecast not in ("none", "fetch") and os.path.isfile(a.forecast):
                fc, fc_src = json.load(open(a.forecast)), a.forecast
            if fc is None and a.forecast in ("auto", "fetch"):
                f, d = forecast.nearby(lat, lon)
                if d:
                    fc, fc_src = d, os.path.relpath(f, ROOT)
            if fc:
                with open(os.path.join(out, "forecast.json"), "w") as fh:
                    json.dump(fc, fh, indent=1)
                files.append("forecast.json")
                log(f"  forecast: {fc_src} ({', '.join(fc.get('days', []))})")
            else:
                gaps.append("forecast: none attached (runs on Actions; the page falls back to a hand-set wind)")
            import wind_page
            grid = wind_page.build_grid(mod, results, n=1500 if mode == "quick" else 3000, workers=a.workers, log=log)
            with open(os.path.join(out, "wind_grid.json"), "w") as fh:
                json.dump(grid, fh)
            html = wind_page.build_page(mod, C.slug, grid, results, fc, shots,
                                        os.path.join(out, "wind_page", "index.html"), mode, C.tee_set)
            log(f"  wrote {os.path.relpath(html, ROOT)} ({os.path.getsize(html) / 1e6:.1f} MB)")
            files += ["wind_grid.json", "wind_page/index.html"]

    # 6. manifest ------------------------------------------------------------------------------------
    if not any(z[0] in ("recovery", "native") for h in C.holes.values() for z in h["zones"]):
        gaps.append("no trees or long grass in any hole (vision gap-fill missing): unmapped hazards play as rough, "
                    "which biases toward driver")
    if not any("elev" in h for h in C.holes.values()):
        gaps.append("no elevation adjustments in the package (flat ground assumed)")
    sizes = {}
    for f in files:
        p = os.path.join(out, f)
        if os.path.isfile(p):
            sizes[f] = os.path.getsize(p)
    sizes["screenshots/"] = sum(os.path.getsize(os.path.join(shots, x)) for x in os.listdir(shots))
    man = dict(schema="plan/1", course=C.name, slug=C.slug, tee_set=C.tee_set, mode=mode,
               package=C.source, out=os.path.relpath(out, ROOT),
               built=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
               settings=dict(draws=a.draws, swings=a.swings) if mode == "full" else dict(swings=8000),
               forecast=fc_src, stage_seconds=TIMES, runtime_s=round(time.time() - T0, 1), files=sizes,
               picks={str(k): dict(club=r["pick"], aim=r["aim"], zone=r["zone"], margin=round(r["margin"], 4),
                                   tie=r["tie"], conf=r.get("conf"), check=r.get("check") or [],
                                   status="CHECK" if r.get("check") else "PLAY") for k, r in results.items()},
               check={str(k): r["check"] for k, r in results.items() if r.get("check")},
               badges={k: dict(state=b["state"], line=b["line"]) for k, b in badge.items()},
               tee_line=dict(rule=PK._tee_line_mod().RULE,
                             how={str(k): f.get("aim") for k, f in C.frames.items()}),
               par3={str(k): dict(center=p["center"], card=p.get("card"), haz=p["haz"]) for k, p in C.par3.items()},
               gaps=gaps)
    with open(os.path.join(out, "plan.json"), "w") as fh:
        json.dump(man, fh, indent=1, default=float)
    log(f"done in {man['runtime_s']:.0f}s -> {man['out']}")
    for g in gaps:
        log("  gap:", g)
    return man


if __name__ == "__main__":
    main()
