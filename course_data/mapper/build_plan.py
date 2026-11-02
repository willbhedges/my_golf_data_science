"""Plan from package + agent layers: the product's quick decision on the base (AUTO) package and on AUTO + AGENT.

  python3 course_data/mapper/build_plan.py <slug> [--set Blue] [--n 4000] [--workers 4]

-> course_data/mapper/<slug>/out/package.json   the base package with the agent layers (apply.py)
   course_data/mapper/<slug>/plan.json / PLAN.md per par-4/5 tee shot: club + aim on AUTO and on AUTO + AGENT,
                                               aim points apart (yds), what the agent changed on that hole
The same decision as the error budget (product/package.load -> product/decide.run quick, n swings, seed 31; common
random numbers, so a changed pick is a changed map). The published page (wind grids, Bayesian decide) is built by
the library workflow: put "agent_layers": "course_data/mapper/<slug>/" in the course-page request
(course_data/requests/course_page_<slug>.json; pkgreq passes it to platform/package.py, which applies the layers
after vision + OB). That push is the coordinator's (course_page_* requests start long builds).
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as M  # noqa: E402


def eb():
    p = os.path.join(M.CD, "platform")
    if p not in sys.path:
        sys.path.append(p)
    import error_budget as E
    return E


def plan(pkg, S, n, workers, cache, name):
    """{hole: {pick, aim, ev, margin, tie, aim_ll}} through the error budget's quick decision."""
    E = eb()
    base = E.prepare(pkg, S)
    C, holes = E.load_models(base, S, name)
    jobs = {E.fp(h): h for h in holes.values()}
    res = E.run_decisions(jobs, n, workers, cache)
    out = {}
    for k, h in holes.items():
        r = res[E.fp(h)]
        ll = E.aim_point_ll(C, k, h, r["pick"], r["aim"])
        out[str(k)] = dict(pick=r["pick"], aim=round(r["aim"], 1), ev=round(r["ev"], 4), margin=round(r["margin"], 4),
                           tie=bool(r["tie"]), runner=r["runner"], aim_ll=[round(float(ll[0]), 7), round(float(ll[1]), 7)])
    return out


def run(slug, S=None, n=4000, workers=None):
    import apply as AP
    E = eb()
    base = M.load_base(slug)
    S = M.tee_set_of(base, S or (M.rj(M.mdir(slug, "frames.json")) or {}).get("set"))
    out, rep = AP.apply(base, M.mdir(slug))
    os.makedirs(M.mdir(slug, "out"), exist_ok=True)
    with open(M.mdir(slug, "out", "package.json"), "w") as fh:
        json.dump(out, fh)
    E.CACHE_JSON = M.mdir(slug, "out", "plan_cache.json")
    cache = M.rj(E.CACHE_JSON, {}) or {}
    a = plan(base, S, n, workers, cache, f"mapper_{slug}_auto")
    b = plan(out, S, n, workers, cache, f"mapper_{slug}_agent")
    with open(E.CACHE_JSON, "w") as fh:
        json.dump(cache, fh)
    rows = []
    for k in sorted(set(a) & set(b), key=M.hole_key):
        d = M.yd_between(a[k]["aim_ll"], b[k]["aim_ll"])
        rows.append(dict(hole=k, auto=a[k], agent=b[k], aim_apart=round(d, 1),
                         changed=bool(a[k]["pick"] != b[k]["pick"] or d > 10.0),
                         agent_edits=(rep["holes"].get(k) or {}).get("summary", "")))
    res = dict(schema="mapper_plan/1", slug=slug, set=S, n=n, base=os.path.relpath(M.base_package_path(slug), M.ROOT),
               agent_layers=out.get("agent_layers"), rows=rows)
    M.wj(M.mdir(slug, "plan.json"), res)
    L = [f"# Plan with the mapper's layers: {base['course']['name']} ({S} tees)", "",
         f"Quick decision (n = {n}, seed 31) on the base package and on base + agent layers "
         f"({out['stages']['agent_layers']}). Changed = other club, or aim points > 10 yds apart.", "",
         "| hole | AUTO | AUTO + AGENT | aim apart (yds) | changed | agent edits on the hole |", "|---|---|---|---|---|---|"]
    for r in rows:
        f = lambda x: f"{x['pick']} {x['aim']:+.0f}" + (" (tie)" if x["tie"] else "")      # noqa: E731
        L.append(f"| {r['hole']} | {f(r['auto'])} | {f(r['agent'])} | {r['aim_apart']} | {'**yes**' if r['changed'] else ''} | "
                 f"{r['agent_edits']} |")
    L += ["", f"{sum(r['changed'] for r in rows)} of {len(rows)} tee shots change. Page: add `\"agent_layers\": "
              f"\"course_data/mapper/{slug}/\"` to `course_data/requests/course_page_{slug}.json` (coordinator)."]
    open(M.mdir(slug, "PLAN.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    ap.add_argument("--set")
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--workers", type=int, default=None)
    a = ap.parse_args()
    run(a.slug, a.set, a.n, a.workers)


if __name__ == "__main__":
    main()
