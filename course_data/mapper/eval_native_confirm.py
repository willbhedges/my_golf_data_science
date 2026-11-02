"""Offline value of the golfer native-side confirm tap (product/native_confirm.py), answers simulated from the truth.

  DECIDE_ADAPTIVE_AIM=0 V2_ADAPTIVE_AIM=0 python3 course_data/mapper/eval_native_confirm.py \
      [--courses eagle_bend,...] [--n 4000] [--caps 2,4,6] [--answer near|any] [--out <json>]
  -> course_data/mapper/eval_native_confirm.json + EVAL_native_confirm.md   (truth-bearing: never shown to a mapper)

Per course (every error-budget course with mapper layers, as eval_mapper.py):
  AUTO            the package the mapper reviewed
  AGENT           AUTO + the agent's layers (the map the questions start from)
  ASK <cap>       AGENT + the simulated golfer's answers on the holes native_confirm.select() asks (<= cap)
  ASK all         AGENT + the answers on every corridor hole (the ceiling of the tap with this geometry)
Simulated golfer: side S of hole n has native when the truth's visible native (truth stack over the AUTO package,
error_budget.truth_stack) covers >= MIN_YD2 sq yds of that side of the tee line, along 150-345, within REACH
yds of the line, and (--answer near, default) within NEAR yds of the package fairway (the native that can catch a
tee shot; --answer any drops this test). Scored by error_budget.score_course (configs auto + truth, n, seed 31,
common random numbers), the same as eval_mapper.py.
Caveat (as eval_mapper.py): the truth of a corridor hole is the hand map inside its traced footprint and the scored
map outside it, so golfer native outside the footprint is not penalised.
"""
import argparse
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
import eval_mapper as EM  # noqa: E402

sys.path.insert(0, os.path.join(M.CD, "product"))
import native_confirm as NC  # noqa: E402

COURSES = "eagle_bend,mariah_hills,ellis,prairie_dunes,buffalo_dunes,sand_creek_station,spirit_hollow"
MIN_YD2, NEAR, REACH = 300.0, 30.0, 65.0
CACHE = os.path.join(HERE, "eval_cache.json")


def truth_answers(E, cfg, base, frames, near=True):
    """{ref: answer} from the truth native (see the module doc) + {ref: {side: sq yds}}."""
    import shapely
    from shapely.geometry import box
    S = cfg["tees"]
    truth = E.truth_holes(cfg)
    prep = E.prepare(base, S)
    _, moved = E.renumber(prep, truth, S)
    inv = {j: r for r, j in moved.items()}
    P = E.PK()
    out, areas = {}, {}
    for ref, fj in frames.items():
        tref = inv.get(ref, None if ref in moved else ref)
        td = truth.get(tref) if tref else None
        h = prep["holes"].get(ref)
        if td is None or h is None:
            continue
        ent = E.tee_entry(h, S, prep.get("tee_set"))
        ref_ll = P._ll(ent.get("tee_ll")) or P._ll(h.get("tee_ll")) or td.get("tee_ll")
        eff = E.effective(E.truth_stack(E.auto_stack(prep, h, ref_ll), td))
        nat = eff.get("native")
        a = {"L": 0.0, "R": 0.0}
        if nat is not None and not nat.is_empty:
            g = shapely.transform(nat, lambda xy: M.ll_to_xy(fj, xy)).buffer(0)
            mown = NC.mown_xy(fj, base["holes"][ref])
            for s, bx in (("L", box(-REACH, 150, 0, 345)), ("R", box(0, 150, REACH, 345))):
                q = g.intersection(bx)
                if near and mown is not None:
                    q = q.intersection(mown.buffer(NEAR))
                a[s] = round(q.area)
        areas[ref] = a
        out[ref] = NC.answer_of({s: a[s] >= MIN_YD2 for s in NC.SIDES})
    return out, areas


def capped(qs, cap):
    n, out = 0, []
    for q in qs:
        if n < cap and q["changes"] and q["value"] >= NC.MIN_VOI:
            out.append(q["hole"])
            n += 1
    return out


def tot(res):
    rows = res["rows"]
    return dict(match=sum(r["configs"]["auto"]["match"] for r in rows),
                regret=round(sum(r["configs"]["auto"]["regret"] or 0 for r in rows), 3),
                holes={r["hole"]: dict(plan=f"{r['configs']['auto']['pick']} {r['configs']['auto']['aim']:+.0f}",
                                       match=r["configs"]["auto"]["match"], regret=r["configs"]["auto"]["regret"],
                                       truth=f"{r['truth']['pick']} {r['truth']['aim']:+.0f}") for r in rows})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--courses", default=COURSES)
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--caps", default="2,4,6")
    ap.add_argument("--answer", default="near", choices=["near", "any"])
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out")
    ap.add_argument("--cache", help="decision cache to load / keep (default: a temp file, dropped)")
    a = ap.parse_args()
    import apply as AP
    E = EM.eb()
    E.ONLY = {"auto", "truth"}
    cache = {}
    for p in (os.path.join(M.CD, "platform", "error_budget_cache.json"), os.path.join(M.CD, "platform", "error_budget_v2_cache.json"), CACHE, a.cache or ""):
        cache.update(M.rj(p, {}) or {})
    tmp = tempfile.mkdtemp(prefix="native_confirm_")
    E.CACHE_JSON = a.cache or os.path.join(tmp, "cache.json")
    caps = [int(c) for c in a.caps.split(",")]
    want = set(a.courses.split(","))
    out = []
    try:
        for cfg in EM.course_list("all", want):
            slug, S = cfg["slug"], cfg["tees"]
            t0 = time.time()
            base, _ = EM.base_for(cfg)
            agent, _ = AP.apply(base, M.mdir(slug))
            frames = M.frames(slug)
            edits = M.rj(M.mdir(slug, "edits.json"))
            zones = M.rj(M.mdir(slug, "agent_zones.geojson"))
            pri = NC.priors(edits, zones, frames, agent)
            ans, areas = truth_answers(E, cfg, base, frames, near=a.answer == "near")
            D = NC.EBDecider(S, n=a.n, workers=a.workers, cache=cache)
            print(f"== {slug} ({S}): selecting", flush=True)
            qs = NC.select(agent, frames, pri, D, cap=99)
            variants = {"AUTO": base, "AGENT": agent}
            asked = {}
            for c in caps:
                asked[f"ASK {c}"] = capped(qs, c)
            asked["ASK all"] = [r for r in frames if r in ans]
            for k, hs in asked.items():
                variants[k] = NC.apply_answers(agent, {r: ans[r] for r in hs if r in ans}, frames,
                                               {r: {s: pri[r][s]["w"] for s in NC.SIDES} for r in hs})
            scores = {}
            for k, pk in variants.items():
                d = os.path.join(tmp, k.replace(" ", "_"))
                os.makedirs(os.path.join(d, slug), exist_ok=True)
                with open(os.path.join(d, slug, "package.json"), "w") as fh:
                    json.dump(pk, fh)
                E.AUTO_DIR = d
                print(f"  scoring {k}", flush=True)
                r = E.score_course(dict(cfg), a.n, a.workers, cache)
                scores[k] = tot(r) if "rows" in r else dict(error=r.get("error"))
            c = dict(slug=slug, tees=S, answers=ans, areas=areas,
                     priors={r: {s: v[s]["p"] for s in NC.SIDES} for r, v in pri.items()},
                     questions=[{k: q[k] for k in ("hole", "value", "changes", "prior", "plans", "regret", "state_p")} for q in qs],
                     asked=asked, scores=scores, secs=round(time.time() - t0))
            out.append(c)
            print("  " + "; ".join(f"{k} {v.get('match')} / {v.get('regret')}" for k, v in scores.items())
                  + f"; asked {[(k, len(v)) for k, v in asked.items()]} ({c['secs']} s)", flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    res = dict(schema="native_confirm_eval/1", n=a.n, answer=a.answer, caps=caps, min_yd2=MIN_YD2, near=NEAR,
               made_utc=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%MZ"), courses=out)
    path = a.out or os.path.join(HERE, "eval_native_confirm.json")
    M.wj(path, res)
    md = report(res)
    open(os.path.splitext(path)[0].replace("eval_native_confirm", "EVAL_native_confirm") + ".md", "w").write(md)
    print(md)


def report(res):
    ks = ["AUTO", "AGENT"] + [f"ASK {c}" for c in res["caps"]] + ["ASK all"]
    L = [f"# Native-side confirm tap: offline value (answers simulated from the truth, '{res['answer']}')", "",
         f"Made {res['made_utc']} by `course_data/mapper/eval_native_confirm.py` (n = {res['n']}, seed 31; "
         "DECIDE_ADAPTIVE_AIM=0 V2_ADAPTIVE_AIM=0 for comparison with EVAL_BLIND rounds 3-4). **Truth-bearing: never "
         "show to a mapper.**", "", "match / regret (strokes) over the corridor tee shots; questions asked in brackets.", "",
         "| course | holes | " + " | ".join(ks) + " |", "|---|---|" + "---|" * len(ks)]
    P = {k: [0, 0.0, 0] for k in ks}
    for c in res["courses"]:
        cells = []
        for k in ks:
            s = c["scores"].get(k) or {}
            if "match" not in s:
                cells.append("-")
                continue
            q = len(c["asked"].get(k, [])) if k.startswith("ASK") else None
            P[k][0] += s["match"]
            P[k][1] += s["regret"]
            P[k][2] += q or 0
            cells.append(f"{s['match']} / {s['regret']:.3f}" + (f" ({q})" if q is not None else ""))
        n = len((c["scores"].get("AGENT") or {}).get("holes") or {})
        L.append(f"| {c['slug']} | {n} | " + " | ".join(cells) + " |")
    L.append("| **pooled** | | " + " | ".join(f"**{P[k][0]} / {P[k][1]:.3f}**" + (f" ({P[k][2]})" if k.startswith("ASK") else "")
                                         for k in ks) + " |")
    L += ["", "## Asked holes (simulated answer; plan AGENT -> after; truth)", ""]
    for c in res["courses"]:
        big = max((k for k in c["asked"] if k != "ASK all"), key=lambda k: len(c["asked"][k]), default=None)
        if not big:
            continue
        rows = []
        for r in c["asked"][big]:
            q = next(x for x in c["questions"] if x["hole"] == r)
            ag, af = c["scores"]["AGENT"]["holes"].get(r, {}), c["scores"][big]["holes"].get(r, {})
            rows.append(f"{r} [{c['answers'].get(r)}; p L {q['prior']['L']:.2f} R {q['prior']['R']:.2f}; value {q['value']:.3f}]: "
                        f"{ag.get('plan')} -> {af.get('plan')} (truth {ag.get('truth')}; regret {ag.get('regret')} -> {af.get('regret')})")
        L.append(f"- **{c['slug']}** ({big}): " + ("; ".join(rows) if rows else "none"))
    L += ["", "## Simulated answers vs mapper (every corridor hole)", "", "| course | hole | truth answer | sq yds L / R | prior L / R |",
          "|---|---|---|---|---|"]
    for c in res["courses"]:
        for r, ans in c["answers"].items():
            ar, pr = c["areas"].get(r, {}), c["priors"].get(r, {})
            if ans != "none" or max(pr.get("L", 0), pr.get("R", 0)) >= 0.5:
                L.append(f"| {c['slug']} | {r} | {ans} | {ar.get('L')} / {ar.get('R')} | {pr.get('L')} / {pr.get('R')} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
