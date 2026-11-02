"""Does the mapper agent help? Error budget of AUTO vs AUTO + AGENT layers vs the hand truth, per course and pooled.

  python3 course_data/mapper/eval_mapper.py [--set v1|v2|all] [--courses a,b] [--n 4000] [--workers 4]
        [--configs auto,truth,+trees,+long_grass]
  -> course_data/mapper/eval_<set>.json + EVAL_<set>.md   (NEVER read by a mapper agent: they contain the truth)

Courses: every course of the error-budget set (platform/error_budget.py --set v1 / v2) that has a mapper folder with
agent layers (course_data/mapper/<slug>/agent_zones.geojson or agent_tees.json). Per course:
  AUTO          the package the mapper reviewed (course_data/mapper/<slug>/base/package.json, else the committed one)
  AUTO + AGENT  the same package with the agent's layers (apply.py)
Both go through error_budget.score_course (--auto-dir machinery: same truth, renumbering, quick decision n, seed 31,
common random numbers) against the all-truth plan. Reported: match (same club, aim within 10 yds), same club,
regret (strokes on the truth map), holes fixed / broken by the agent; per hazard layer the landing-corridor area
the truth has and the map lacks (missing) / the map has and the truth lacks (extra), AUTO vs AUTO + AGENT
(error_budget.layer_diagnostics); tee error vs the truth tee (all / measured truth tees only). With --configs
+layer the "+truth layer" rows are computed on both sides (what is still left after the agent).
The decision cache (course_data/mapper/eval_cache.json) is seeded read-only from the error budget's caches.
"""
import argparse
import copy
import datetime as dt
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as M  # noqa: E402

CACHE = os.path.join(HERE, "eval_cache.json")


def eb():
    p = os.path.join(M.CD, "platform")
    if p not in sys.path:
        sys.path.append(p)
    import error_budget as E
    return E


def has_agent(slug):
    return any(os.path.exists(M.mdir(slug, f)) for f in ("agent_zones.geojson", "agent_tees.json"))


def course_list(set_name, want=None):
    E = eb()
    names = ["v1", "v2"] if set_name == "all" else [set_name]
    out, seen = [], set()
    for s in names:
        for cfg in E.SETS[s]():
            if cfg["slug"] in seen or (want and cfg["slug"] not in want):
                continue
            seen.add(cfg["slug"])
            if has_agent(cfg["slug"]):
                out.append(dict(cfg, set=s))
    return out


def base_for(cfg):
    p = M.mdir(cfg["slug"], "base", "package.json")
    if os.path.exists(p):
        return M.rj(p), os.path.relpath(p, M.ROOT)
    p = os.path.join(M.ROOT, cfg["package"]) if cfg.get("package") else M.committed_package_path(cfg["slug"])
    return M.rj(p), os.path.relpath(p, M.ROOT)


def layer_sums(rows):
    out = {}
    for r in rows:
        for L, d in ((r.get("geo") or {}).get("layers") or {}).items():
            o = out.setdefault(L, dict(missing=0, extra=0, truth=0))
            for k in o:
                o[k] += d.get(k) or 0
    return out


def tee_errs(rows, measured_only=False):
    v = [(r.get("geo") or {}).get("tee_err") for r in rows
         if not (measured_only and str(r.get("tee_method") or "").startswith("estimated"))]
    v = sorted(x for x in v if x is not None)
    if not v:
        return None
    return dict(n=len(v), median=round(v[len(v) // 2], 1), over10=sum(x > 10 for x in v))


def compare(slug, a, b, configs):
    """Per-course summary of base (a) vs agent (b) score_course results."""
    ra = {r["hole"]: r for r in a["rows"]}
    rb = {r["hole"]: r for r in b["rows"]}
    keys = [k for k in ra if k in rb]

    def tot(R, cf, f):
        return sum((R[k]["configs"].get(cf) or {}).get(f) or 0 for k in keys)
    fixed = [k for k in keys if not ra[k]["configs"]["auto"]["match"] and rb[k]["configs"]["auto"]["match"]]
    broke = [k for k in keys if ra[k]["configs"]["auto"]["match"] and not rb[k]["configs"]["auto"]["match"]]
    out = dict(slug=slug, holes=len(keys), ref_ties=sum(ra[k]["truth"]["tie"] for k in keys),
               auto=dict(match=tot(ra, "auto", "match"), club=tot(ra, "auto", "club"), same_or_tie=tot(ra, "auto", "same_or_tie"),
                         regret=round(tot(ra, "auto", "regret"), 3)),
               agent=dict(match=tot(rb, "auto", "match"), club=tot(rb, "auto", "club"), same_or_tie=tot(rb, "auto", "same_or_tie"),
                          regret=round(tot(rb, "auto", "regret"), 3)),
               fixed=fixed, broke=broke,
               layers=dict(auto=layer_sums([ra[k] for k in keys]), agent=layer_sums([rb[k] for k in keys])),
               tee_err=dict(auto=tee_errs([ra[k] for k in keys]), agent=tee_errs([rb[k] for k in keys]),
                            auto_measured=tee_errs([ra[k] for k in keys], True),
                            agent_measured=tee_errs([rb[k] for k in keys], True)),
               extra_configs={})
    for cf in configs:
        if cf in ("auto", "truth", "+routing"):
            continue
        out["extra_configs"][cf] = dict(auto=dict(match=tot(ra, cf, "match"), regret=round(tot(ra, cf, "regret"), 3)),
                                        agent=dict(match=tot(rb, cf, "match"), regret=round(tot(rb, cf, "regret"), 3)))
    out["holes_detail"] = [dict(hole=k, truth=f"{ra[k]['truth']['pick']} {ra[k]['truth']['aim']:+.0f}" + (" (tie)" if ra[k]["truth"]["tie"] else ""),
                                auto=f"{ra[k]['configs']['auto']['pick']} {ra[k]['configs']['auto']['aim']:+.0f}",
                                agent=f"{rb[k]['configs']['auto']['pick']} {rb[k]['configs']['auto']['aim']:+.0f}",
                                auto_match=ra[k]["configs"]["auto"]["match"], agent_match=rb[k]["configs"]["auto"]["match"],
                                auto_regret=ra[k]["configs"]["auto"]["regret"], agent_regret=rb[k]["configs"]["auto"]["regret"])
                           for k in keys if ra[k]["configs"]["auto"]["match"] != rb[k]["configs"]["auto"]["match"]
                           or (ra[k]["configs"]["auto"]["pick"], ra[k]["configs"]["auto"]["aim"]) !=
                           (rb[k]["configs"]["auto"]["pick"], rb[k]["configs"]["auto"]["aim"])]
    return out


def pooled(cs):
    P = dict(courses=len(cs), holes=sum(c["holes"] for c in cs), ref_ties=sum(c["ref_ties"] for c in cs))
    for side in ("auto", "agent"):
        P[side] = {k: round(sum(c[side][k] for c in cs), 3) for k in ("match", "club", "same_or_tie", "regret")}
    P["fixed"] = sum(len(c["fixed"]) for c in cs)
    P["broke"] = sum(len(c["broke"]) for c in cs)
    P["layers"] = {}
    for side in ("auto", "agent"):
        acc = {}
        for c in cs:
            for L, d in c["layers"][side].items():
                o = acc.setdefault(L, dict(missing=0, extra=0, truth=0))
                for k in o:
                    o[k] += d[k]
        P["layers"][side] = acc
    return P


def report(res):
    P = res["pooled"]
    pct = lambda a, n: f"{a:.0f}/{n} ({100 * a / max(n, 1):.0f}%)"      # noqa: E731
    L = [f"# Agent mapper evaluation ({res['set']})", "",
         f"Made {res['made_utc']} by `course_data/mapper/eval_mapper.py` (n = {res['n']}, seed 31, aim tolerance 10 yds). "
         "AUTO = the package the mapper reviewed; AUTO + AGENT = the same package with the agent's layers; both "
         "scored against the all-truth plan by `platform/error_budget.score_course`. **Do not show this file to a mapper.**", "",
         "## Pooled", "",
         "| | tee shots | match | same club | same club or tie | regret (strokes) |", "|---|---|---|---|---|---|",
         f"| AUTO | {P['holes']} | {pct(P['auto']['match'], P['holes'])} | {P['auto']['club']:.0f} | {P['auto']['same_or_tie']:.0f} | {P['auto']['regret']:.3f} |",
         f"| AUTO + AGENT | {P['holes']} | {pct(P['agent']['match'], P['holes'])} | {P['agent']['club']:.0f} | {P['agent']['same_or_tie']:.0f} | {P['agent']['regret']:.3f} |",
         "", f"Holes fixed by the agent: {P['fixed']}; broken: {P['broke']}. Reference ties among all holes: {P['ref_ties']}.", "",
         "Landing-corridor area vs truth (sq yds, 180-320 yds along the truth tee line, +/-50; summed over holes):", "",
         "| layer | truth | AUTO missing / extra | AUTO + AGENT missing / extra |", "|---|---|---|---|"]
    for Lr in sorted(P["layers"]["auto"]):
        a, b = P["layers"]["auto"][Lr], P["layers"]["agent"].get(Lr, {})
        L.append(f"| {Lr} | {a['truth']} | {a['missing']} / {a['extra']} | {b.get('missing')} / {b.get('extra')} |")
    L += ["", "## Per course", "",
          "| course | set | mapper | tee shots | match AUTO -> AGENT | same club | regret | fixed | broken | tee err median (measured truth tees) |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for c in res["courses"]:
        te = c["tee_err"]
        f = lambda t: "-" if not t else f"{t['median']} ({t['n']}, {t['over10']} > 10)"     # noqa: E731
        L.append(f"| {c['slug']} | {c.get('tees')} | {c.get('mapper') or '?'} | {c['holes']} | {c['auto']['match']} -> {c['agent']['match']} | "
                 f"{c['auto']['club']} -> {c['agent']['club']} | {c['auto']['regret']:.3f} -> {c['agent']['regret']:.3f} | "
                 f"{', '.join(c['fixed']) or '-'} | {', '.join(c['broke']) or '-'} | {f(te['auto_measured'])} -> {f(te['agent_measured'])} |")
    L += ["", "## Holes whose plan the agent changed", "", "| course | hole | truth | AUTO | AUTO + AGENT | match | regret |", "|---|---|---|---|---|---|---|"]
    for c in res["courses"]:
        for d in c["holes_detail"]:
            L.append(f"| {c['slug']} | {d['hole']} | {d['truth']} | {d['auto']} | {d['agent']} | {d['auto_match']} -> {d['agent_match']} | "
                     f"{d['auto_regret']} -> {d['agent_regret']} |")
    xc = sorted({k for c in res["courses"] for k in c["extra_configs"]})
    if xc:
        L += ["", "## What is left: + one truth layer, on AUTO and on AUTO + AGENT (match / regret)", "",
              "| config | AUTO | AUTO + AGENT |", "|---|---|---|"]
        for k in xc:
            a = [c["extra_configs"][k]["auto"] for c in res["courses"] if k in c["extra_configs"]]
            b = [c["extra_configs"][k]["agent"] for c in res["courses"] if k in c["extra_configs"]]
            L.append(f"| {k} | {sum(x['match'] for x in a)} / {sum(x['regret'] for x in a):.3f} | "
                     f"{sum(x['match'] for x in b)} / {sum(x['regret'] for x in b):.3f} |")
    if res.get("errors"):
        L += ["", "## Not scored", ""] + [f"- {k}: {v}" for k, v in res["errors"].items()]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--set", default="all", choices=["v1", "v2", "all"])
    ap.add_argument("--courses")
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--configs", default="auto,truth")
    ap.add_argument("--out")
    a = ap.parse_args()
    import apply as AP
    E = eb()
    configs = set(a.configs.split(",")) | {"auto", "truth"}
    E.ONLY = configs
    cache = {}
    seed = set()
    for p in (os.path.join(M.CD, "platform", "error_budget_cache.json"), os.path.join(M.CD, "platform", "error_budget_v2_cache.json")):
        cache.update(M.rj(p, {}) or {})
    seed = set(cache)
    cache.update(M.rj(CACHE, {}) or {})
    E.CACHE_JSON = CACHE
    want = set(a.courses.split(",")) if a.courses else None
    cl = course_list(a.set, want)
    if not cl:
        raise SystemExit("no truth course has mapper layers yet (course_data/mapper/<slug>/agent_zones.geojson)")
    tmp = tempfile.mkdtemp(prefix="mapper_eval_")
    courses, errors = [], {}
    try:
        for cfg in cl:
            slug = cfg["slug"]
            t0 = time.time()
            base, bpath = base_for(cfg)
            fr = M.rj(M.mdir(slug, "frames.json")) or {}
            if fr.get("set") and str(fr["set"]).lower() not in str(cfg["tees"]).lower():
                print(f"  ! {slug}: the mapper's corridor set {fr['set']} is not the scored set {cfg['tees']}")
            agent, rep = AP.apply(base, M.mdir(slug))
            for side, pk in (("base", base), ("agent", agent)):
                os.makedirs(os.path.join(tmp, side, slug), exist_ok=True)
                with open(os.path.join(tmp, side, slug, "package.json"), "w") as fh:
                    json.dump(pk, fh)
            res = {}
            for side in ("base", "agent"):
                E.AUTO_DIR = os.path.join(tmp, side)
                print(f"== {slug} ({cfg['tees']}): {side}", flush=True)
                res[side] = E.score_course(dict(cfg), a.n, a.workers, cache)
                with open(CACHE, "w") as fh:
                    json.dump({k: v for k, v in cache.items() if k not in seed}, fh)
            if "rows" not in res["base"] or "rows" not in res["agent"]:
                errors[slug] = res["base"].get("error") or res["agent"].get("error")
                continue
            c = compare(slug, res["base"], res["agent"], configs)
            c.update(tees=cfg["tees"], set=cfg["set"], base=bpath, mapper=rep.get("mapper"),
                     agent_layers=dict(ops=rep["ops"], tees_moved=rep["tees_moved"], tees_checked=rep["tees_checked"]))
            courses.append(c)
            print(f"  {slug}: match {c['auto']['match']} -> {c['agent']['match']} / {c['holes']}, regret "
                  f"{c['auto']['regret']:.3f} -> {c['agent']['regret']:.3f} ({time.time() - t0:.0f} s)", flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    res = dict(schema="mapper_eval/1", set=a.set, n=a.n, made_utc=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%MZ"),
               configs=sorted(configs), courses=courses, pooled=pooled(courses) if courses else None, errors=errors)
    out = a.out or os.path.join(HERE, f"eval_{a.set}.json")
    M.wj(out, res)
    md = report(res) if courses else "no course scored\n"
    open(os.path.join(os.path.dirname(out), f"EVAL_{a.set}.md" if not a.out else os.path.splitext(os.path.basename(out))[0] + ".md"), "w").write(md)
    print(md)


if __name__ == "__main__":
    main()
