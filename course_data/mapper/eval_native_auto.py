"""Held-out value of the automatic native-side classifier (product/native_auto.py): no agent, no taps / <= k taps.

  DECIDE_ADAPTIVE_AIM=0 V2_ADAPTIVE_AIM=0 python3 course_data/mapper/eval_native_auto.py \
      [--courses a,b] [--score a,b] [--n 4000] [--caps 2] [--feat-cache DIR] [--cache FILE] [--out JSON]
      [--write-model]
  -> course_data/mapper/eval_native_auto.json + EVAL_native_auto.md  (truth-bearing: never shown to a mapper)

Courses: every error-budget course with mapper frames (eval_mapper.course_list("all")) except those whose truth has
no traced long grass (NO_LONG_GRASS_TRUTH). Per course:
  labels   eval_native_confirm.truth_answers (side has native when >= 300 sq yds of truth native lies within 30 yds
           of the package fairway, 150-345 along): one 0 / 1 per hole side
  p        leave-one-course-out: the classifier fitted on the OTHER courses (native_auto.loco)
  thr      nested: native_auto.pick_threshold on the inner leave-one-course-out p of the other courses only
Plan variants (error_budget.score_course, configs auto + truth, n, seed 31, common random numbers, as eval_mapper):
  AUTO      the package the mapper reviewed (mapper/<slug>/base/package.json)
  ORACLE    AUTO + the band on every truth "yes" side (the ceiling of the band geometry with a perfect classifier)
  CLS       AUTO + the band on the sides with held-out p >= thr (the zero-tap layer)
  CLS+TAPk  CLS, then native_confirm.select with the classifier p as priors asks <= k holes; the simulated golfer
            answers from the truth ("yes" adds the band, "no" erases that side's native, the classifier's included)
  PRI+TAPk  AUTO (no automatic native), the classifier p only ranks the <= k questions
  GATED     the product rule: CLS when the course gate fires (native_auto.course_fires: >= COURSE_GATE of the
            course's sides reach thr), else AUTO; GATED+TAPk = CLS+TAPk when it fires, else PRI+TAPk (no new
            scoring: picked from the variants above)
--write-model fits the classifier on all courses (threshold from their leave-one-course-out p) ->
product/native_auto_model.json (for courses outside the truth set).
"""
import argparse
import datetime as dt
import json
import os
import shutil
import sys
import tempfile
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as M  # noqa: E402
import eval_mapper as EM  # noqa: E402
import eval_native_confirm as ENC  # noqa: E402

sys.path.insert(0, os.path.join(M.CD, "product"))
import native_auto as NA  # noqa: E402
import native_confirm as NC  # noqa: E402

NO_LONG_GRASS_TRUTH = {"colbert_hills", "buffalo_ridge"}     # truth has no long-grass layer traced (ERROR_BUDGET.md)
CONTROLS = ("ellis", "spirit_hollow", "blue_hills")         # parkland controls of the brief
OUT = os.path.join(HERE, "eval_native_auto.json")


def side_rows(E, cfg, feat_dir):
    """(rows with y / area, base package, frames, answers) for one course."""
    slug = cfg["slug"]
    base, _ = EM.base_for(cfg)
    frames = M.frames(slug)
    ans, areas, _ = ENC.truth_answers(E, cfg, base, frames, near=True)
    fp = os.path.join(feat_dir, f"{slug}.json") if feat_dir else None
    rows = M.rj(fp) if fp and os.path.exists(fp) else None
    if rows is None:
        rows = NA.side_features(slug, base, frames)
        if fp:
            M.wj(fp, rows)
    keep = []
    for r in rows:
        a = areas.get(r["hole"])
        if a is None:
            continue
        r = dict(r, area=a[r["side"]], y=int(a[r["side"]] >= ENC.MIN_YD2))
        keep.append(r)
    return keep, base, frames, ans


def side_stats(y, sel):
    y, sel = np.asarray(y, bool), np.asarray(sel, bool)
    return dict(pos=int(y.sum()), n=int(len(y)), tp=int((sel & y).sum()), fp=int((sel & ~y).sum()),
                fn=int((~sel & y).sum()))


def score(E, cfg, pkgs, n, cache, tmp):
    out = {}
    for k, pk in pkgs.items():
        d = os.path.join(tmp, k.replace(" ", "_").replace("+", "_"))
        os.makedirs(os.path.join(d, cfg["slug"]), exist_ok=True)
        with open(os.path.join(d, cfg["slug"], "package.json"), "w") as fh:
            json.dump(pk, fh)
        E.AUTO_DIR = d
        r = E.score_course(dict(cfg), n, 1, cache)
        out[k] = ENC.tot(r) if "rows" in r else dict(error=r.get("error"))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--courses", help="training / held-out set (default: every eligible course)")
    ap.add_argument("--score", help="courses to plan-score (default: all of --courses); the rest only train")
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--caps", default="2")
    ap.add_argument("--prec", type=float, default=NA.PREC)
    ap.add_argument("--feat-cache", help="directory for the per-course side features (re-used when present)")
    ap.add_argument("--cache", help="decision cache to load and keep (default: a temp file)")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--write-model", action="store_true")
    ap.add_argument("--no-plans", action="store_true", help="side-level numbers only")
    a = ap.parse_args()
    E = EM.eb()
    E.ONLY = {"auto", "truth"}
    cache = {}
    for p in (os.path.join(M.CD, "platform", "error_budget_cache.json"),
              os.path.join(M.CD, "platform", "error_budget_v2_cache.json"), ENC.CACHE, a.cache or ""):
        cache.update(M.rj(p, {}) or {})
    tmp = tempfile.mkdtemp(prefix="native_auto_")
    E.CACHE_JSON = os.path.join(tmp, "cache.json")
    if a.feat_cache:
        os.makedirs(a.feat_cache, exist_ok=True)
    want = set(a.courses.split(",")) if a.courses else None
    cfgs = [c for c in EM.course_list("all", want) if c["slug"] not in NO_LONG_GRASS_TRUTH]
    data = {}
    for cfg in cfgs:
        t0 = time.time()
        data[cfg["slug"]] = (cfg,) + side_rows(E, cfg, a.feat_cache)
        print(f"{cfg['slug']}: {len(data[cfg['slug']][1])} sides ({time.time() - t0:.0f} s)", flush=True)
    rows = NA.derive([r for v in data.values() for r in v[1]])
    y = np.array([r["y"] for r in rows])
    s = np.array([r["slug"] for r in rows])
    p = NA.loco(rows, y)
    thr = {}
    for c in data:
        tr = s != c
        sub = [r for r, t in zip(rows, tr) if t]
        thr[c] = NA.pick_threshold(NA.loco(sub, y[tr]), y[tr], a.prec)
    P = {}
    for r, pi in zip(rows, p):
        P.setdefault(r["slug"], {}).setdefault(r["hole"], {})[r["side"]] = round(float(pi), 4)
    from sklearn.metrics import roc_auc_score
    res = dict(schema="native_auto_eval/1", n=a.n, prec=a.prec, caps=[int(c) for c in a.caps.split(",")],
               made_utc=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%MZ"),
               features=NA.FEATURES, C=NA.C_L2, gate=NA.COURSE_GATE, auc=round(float(roc_auc_score(y, p)), 3) if 0 < y.sum() < len(y) else None,
               env={k: os.environ.get(k) for k in ("DECIDE_ADAPTIVE_AIM", "V2_ADAPTIVE_AIM")}, courses={})
    if a.write_model:
        m = NA.fit(rows, y, s)
        m.update(thr=NA.pick_threshold(p, y, a.prec), prec=a.prec, trained_on=sorted(data), loco_auc=res["auc"],
                 made_utc=res["made_utc"], note="mapper/eval_native_auto.py --write-model; held-out scores in "
                 "mapper/EVAL_BLIND.md 'Automatic native sides'")
        M.wj(NA.MODEL_JSON, m)
        print(f"wrote {os.path.relpath(NA.MODEL_JSON, M.ROOT)} (thr {m['thr']})")
    scored = set(a.score.split(",")) if a.score else set(data)
    prev = M.rj(a.out, {}) or {}
    try:
        for c, (cfg, crow, base, frames, ans) in data.items():
            m = s == c
            ent = dict(tees=cfg["tees"], thr=thr[c], p=P.get(c, {}), side=side_stats(y[m], p[m] >= thr[c]),
                       share=round(NA.course_share(P.get(c, {}), thr[c]), 3), answers=ans)
            ent["fires"] = ent["share"] >= NA.COURSE_GATE
            if a.no_plans or c not in scored:
                if c in (prev.get("courses") or {}) and "scores" in prev["courses"][c]:
                    ent.update({k: prev["courses"][c][k] for k in ("scores", "asked") if k in prev["courses"][c]})
                res["courses"][c] = ent
                continue
            t0 = time.time()
            pc = P.get(c, {})
            cls_sides = NA.sides_from_p(pc, thr[c])
            cls = NA.apply_sides(base, frames, cls_sides, pc)
            oracle = NA.apply_sides(base, frames, {r: [x for x in NC.SIDES if NC.sides_of(v)[x]] for r, v in ans.items()})
            pkgs = {"AUTO": base, "ORACLE": oracle, "CLS": cls}
            asked = {}
            pri = NA.confirm_priors(pc)
            for name, start in (("CLS+TAP", cls), ("PRI+TAP", base)):
                D = NC.EBDecider(cfg["tees"], n=a.n, cache=cache)
                qs = NC.select(start, frames, pri, D, cap=99)
                for k in res["caps"]:
                    hs = ENC.capped(qs, k)
                    asked[f"{name}{k}"] = hs
                    pkgs[f"{name}{k}"] = NC.apply_answers(start, {r: ans[r] for r in hs if r in ans}, frames)
            ent["scores"] = score(E, cfg, pkgs, a.n, cache, tmp)
            ent["asked"] = asked
            ent["secs"] = round(time.time() - t0)
            res["courses"][c] = ent
            print(f"{c} (thr {thr[c]}): " + "; ".join(f"{k} {v.get('match')}/{v.get('regret')}" for k, v in ent["scores"].items())
                  + f" ({ent['secs']} s)", flush=True)
            M.wj(a.out, res)
            if a.cache:
                M.wj(a.cache, cache)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    M.wj(a.out, res)
    md = report(res)
    open(os.path.join(os.path.dirname(a.out), os.path.basename(a.out).replace("eval_native_auto", "EVAL_native_auto")
                      .replace(".json", ".md")), "w").write(md)
    print(md)


def gated(e, caps):
    """Adds the GATED / GATED+TAPk scores (picked from CLS / CLS+TAPk / AUTO / PRI+TAPk by the course gate)."""
    sc, ak = e.get("scores") or {}, e.get("asked") or {}
    if "CLS" not in sc:
        return
    on = e.get("fires")
    sc["GATED"] = sc["CLS"] if on else sc["AUTO"]
    for k in caps:
        src = f"CLS+TAP{k}" if on else f"PRI+TAP{k}"
        if src in sc:
            sc[f"GATED+TAP{k}"] = sc[src]
            ak[f"GATED+TAP{k}"] = ak.get(src, [])


def report(res):
    ks = (["AUTO", "CLS", "GATED"] + [f"PRI+TAP{k}" for k in res["caps"]] + [f"CLS+TAP{k}" for k in res["caps"]]
          + [f"GATED+TAP{k}" for k in res["caps"]] + ["ORACLE"])
    for e in res["courses"].values():
        gated(e, res["caps"])
    L = [f"# Automatic native sides: held-out plan value (product/native_auto.py)", "",
         f"Made {res['made_utc']} by `course_data/mapper/eval_native_auto.py` (n = {res['n']}, seed 31, env "
         f"{res['env']}). Leave-one-course-out p (side AUC {res['auc']}); per held-out course the threshold is chosen "
         f"on the other courses only (pooled side precision >= {res['prec']}). **Truth-bearing: never show to a mapper.**", "",
         "match / regret (strokes) over the corridor tee shots; taps asked in brackets; sides TP / FP / FN at the "
         "held-out threshold.", "",
         f"GATED = CLS only on courses where >= {res.get('gate')} of the sides reach the threshold (share column).", "",
         "| course | thr | share | sides TP / FP / FN (pos) | " + " | ".join(ks) + " |", "|---|---|---|---|" + "---|" * len(ks)]
    tot = {k: [0, 0.0, 0] for k in ks}
    T = [0, 0, 0, 0]
    for c, e in res["courses"].items():
        sd = e["side"]
        T = [T[0] + sd["tp"], T[1] + sd["fp"], T[2] + sd["fn"], T[3] + sd["pos"]]
        cells = []
        for k in ks:
            v = (e.get("scores") or {}).get(k)
            if not v or "match" not in v:
                cells.append("-")
                continue
            q = len((e.get("asked") or {}).get(k, [])) if "TAP" in k else None
            tot[k][0] += v["match"]
            tot[k][1] += v["regret"]
            tot[k][2] += q or 0
            cells.append(f"{v['match']} / {v['regret']:.3f}" + (f" ({q})" if q is not None else ""))
        L.append(f"| {c}{' (control)' if c in CONTROLS else ''} | {e['thr']} | {e.get('share')}{' on' if e.get('fires') else ''} | {sd['tp']} / {sd['fp']} / {sd['fn']} ({sd['pos']}) | "
                 + " | ".join(cells) + " |")
    L.append(f"| **pooled** | | | {T[0]} / {T[1]} / {T[2]} ({T[3]}) | " + " | ".join(
        f"**{v[0]} / {v[1]:.3f}**" + (f" ({v[2]})" if "TAP" in k else "") for k, v in tot.items()) + " |")
    L += ["", "## Holes whose plan changed (AUTO -> CLS; truth)", ""]
    for c, e in res["courses"].items():
        sc = e.get("scores") or {}
        if "AUTO" not in sc or "CLS" not in sc or "holes" not in sc["AUTO"]:
            continue
        ch = []
        for h, a0 in sc["AUTO"]["holes"].items():
            b = sc["CLS"]["holes"].get(h) or {}
            if a0["plan"] != b.get("plan"):
                tag = "fixed" if b.get("match") and not a0["match"] else "BROKEN" if a0["match"] and not b.get("match") else ""
                ch.append(f"{h} {a0['plan']} -> {b.get('plan')} (truth {a0['truth']}; {a0['regret']} -> {b.get('regret')}{'; ' + tag if tag else ''})")
        L.append(f"- **{c}**: " + ("; ".join(ch) if ch else "no change"))
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
