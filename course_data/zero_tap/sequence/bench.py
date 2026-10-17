"""Run the joint solver over the truth courses and write one row per (course, mode) for the gate.

    python course_data/zero_tap/sequence/bench.py --split dev --modes struct,struct_card,oracle -j 4 --out rows_dev.json
    python course_data/zero_tap/sequence/bench.py --split heldout --shard 0 --of 6 --out rows/rows_0.json

Courses: course_data/structure/sets.json (+ data/) and the generalize cached courses (dev; the 31 test courses of
generalize/validation_set.json are tagged split=valtest and are never used to fit anything here).
Hidden: every golf=hole way, pin, ref / name of golf features. Truth: the hidden hole ways (refs 1..N once each).

Modes (formation x anchors x card):
  struct*     the structure solver's formation hypotheses
  oracle*     the true (tee, green) pairs given: measures the order of play alone
  *_card      + an ideal card (pars + the hidden ways' lengths): the card prior
  *_v1        structure's own clubhouse candidates and nine classifier (baseline); default = this package's v2
"""
from __future__ import annotations

import argparse
import gzip
import importlib
import json
import os
import pickle
import sys
import time
import traceback

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(CD, "structure"))
E = importlib.import_module("e" + "val")                            # course_data/structure/eval.py
import solver as V                                                   # noqa: E402
import joint as J                                                    # noqa: E402
import anchors as A                                                  # noqa: E402

CACHE = os.environ.get("ZT_SEQ_CACHE", os.path.join(HERE, ".cache"))


def all_courses():
    """[(entry)] with split in dev / heldout / valtest (generalize validation test) and kind."""
    val = json.load(open(os.path.join(CD, "generalize", "validation_set.json")))["courses"]
    valtest = {c["slug"] for c in val if c["split"] == "test"}
    out = []
    seen = set()
    for e in E.courses(None):
        if e.get("src") == "generalize" and e["slug"] in valtest:
            e = dict(e, split="valtest")
        out.append(e)
        seen.add(e["slug"])
    # workstream D's benchmark courses (course_data/zero_tap/data/<slug>/), split by its frozen state split:
    # dev states -> "zdev", test states -> "ztest" (never fitted on)
    zd = os.path.join(CD, "zero_tap", "data")
    sp = os.path.join(CD, "zero_tap", "state_split.json")
    if os.path.isdir(zd) and os.path.exists(sp):
        states = json.load(open(sp))["states"]
        for slug in sorted(os.listdir(zd)):
            p = os.path.join(zd, slug, "osm.geojson.gz")
            if slug in seen or not os.path.exists(p):
                continue
            cj = os.path.join(zd, slug, "course.json")
            st = (json.load(open(cj)).get("state") if os.path.exists(cj) else None) or slug.rsplit("_", 1)[-1].upper()
            s = states.get(st)
            if s is None:
                continue
            out.append(dict(slug=slug, split="zdev" if s == "dev" else "ztest", kind=None, state=st, path=p,
                            course=cj, src="zero_tap"))
    return out


def web_card(e):
    """The course's web scorecard (scorecard/1) when one was found, else None."""
    for p in (os.path.join(os.path.dirname(e["path"]), "scorecard.json"),):
        if os.path.exists(p):
            try:
                js = json.load(open(p))
            except Exception:                                        # noqa: BLE001
                return None
            cards = js.get("cards") if isinstance(js, dict) and "cards" in js else ([js] if isinstance(js, dict) else js)
            chosen = js.get("chosen") if isinstance(js, dict) else None
            cards = sorted(cards or [], key=lambda c: 0 if isinstance(c, dict) and c.get("source") == chosen else 1)
            for c in cards:
                c = c.get("card", c) if isinstance(c, dict) else None
                if isinstance(c, dict) and (c.get("par") or c.get("pars") or c.get("tee_sets")):
                    return c
    return None


def load_course(e):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, f"{e['split']}_{e['slug']}.pkl.gz")
    if os.path.exists(p):
        try:
            with gzip.open(p, "rb") as fh:
                return pickle.load(fh)
        except Exception:                                            # noqa: BLE001
            pass
    sc, truth, N, course = E.load(e)
    if N not in (9, 18) or len(sc.greens) < N - 2 or len(sc.tees) < N - 2:
        d = dict(skip=True, N=N)
    else:
        allh, geo = V.hypotheses(sc, topk=400, clubs=list(sc.clubhouse))
        hyps = [hs[:V.TOPK] for hs in allh]
        fc = V_load_fc(e)
        d = dict(skip=False, sc=sc, truth=truth, N=N, course=course, allh=allh, hyps=hyps, geo=geo,
                 roads=A.roads_from_fc(fc, sc.proj), addr_street=A.addr_street(course), webcard=web_card(e))
    tmp = f"{p}.{os.getpid()}.tmp"
    with gzip.open(tmp, "wb") as fh:
        pickle.dump(d, fh)
    os.replace(tmp, p)
    return d


def V_load_fc(e):
    import scene as S
    return S.load_fc(e["path"])


def truth_anchors(d):
    t = d["truth"]
    out = dict(t1=t[0]["tee"].tolist(), gN=t[-1]["green"].tolist())
    if d["N"] == 18:
        out.update(g9=t[8]["green"].tolist(), t10=t[9]["tee"].tolist())
    return out


def run_mode(d, mode, models):
    sc, truth, N, geo = d["sc"], d["truth"], d["N"], d["geo"]
    if "webcard" in mode:
        card = d.get("webcard")
        if not card or len(card.get("par") or card.get("pars") or []) != N:
            return None
    else:
        card = E.card_from_truth(truth) if "card" in mode else None
    v1 = mode.endswith("_v1")
    kw = {}
    if mode.startswith("oracle"):
        o = J.oracle_hyps(sc, truth, geo, d["allh"], E.tee_ok, E.true_green)
        if o is None:
            return None
        kw.update(hyps=o[0], keep=o[1], n_holes=N, hyps_all=d["hyps"])
    else:
        kw.update(hyps=d["hyps"])
    if not v1:
        kw["cands"] = A.clubhouse_candidates(sc, geo, d["hyps"], roads=d["roads"], street=d["addr_street"],
                                             model=models.get("club"))
        nm = models.get("nine")
        kw["nine"] = nm.with_context(d["roads"], d["addr_street"]) if nm is not None else None
    t0 = time.time()
    res = J.solve(sc, card=card, geo=geo, **kw)
    sec = time.time() - t0
    r = E.score_course(res, sc, truth, N)
    dg = res["diag"]
    ch = np.array(res["clubhouse"]["xy"])
    ta = truth_anchors(d)
    r.update(mode=mode, seconds=round(sec, 2), diag=dg, n_guess=res["n_holes"],
             ch_how=res["clubhouse"]["how"], ch_err=float(min(np.hypot(*(ch - np.array(ta["t1"]))),
                                                              np.hypot(*(ch - np.array(ta["gN"]))))))
    r.pop("conf_raw", None)
    if N == 18 and dg.get("swap_x") is not None:
        # orientation features of the TRUE route (for fitting the nine model) when formation is right
        pass
    return r


def course_rows(e, modes, models):
    try:
        d = load_course(e)
    except Exception as ex:                                          # noqa: BLE001
        traceback.print_exc()
        return [dict(slug=e["slug"], split=e["split"], error=str(ex))]
    if d.get("skip"):
        return []
    rows = []
    for m in modes:
        try:
            r = run_mode(d, m, models)
        except Exception as ex:                                      # noqa: BLE001
            traceback.print_exc()
            r = dict(error=str(ex), mode=m)
        if r is None:
            continue
        r.update(slug=e["slug"], split=e["split"], state=e.get("state") or d["course"].get("state"))
        rows.append(r)
        print(f"{e['split']:8s} {e['slug'][:26]:26s} {m:16s} N={r.get('N')} form {r.get('formation')} "
              f"num {r.get('number')} swap {r.get('swap')} ok {r.get('all_correct')} {r.get('seconds')}s "
              f"ch={r.get('ch_how')} err={r.get('ch_err', 0):.0f}", flush=True)
    return rows


def _worker(args):
    e, modes = args
    return course_rows(e, modes, A.load_models())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev")
    ap.add_argument("--modes", default="struct,struct_card,oracle")
    ap.add_argument("--shard", type=int)
    ap.add_argument("--of", type=int, default=1)
    ap.add_argument("-j", type=int, default=1)
    ap.add_argument("--slug")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--out", required=True)
    ap.add_argument("--combine", nargs="*")
    a = ap.parse_args()
    if a.combine:
        return combine(a.combine, a.out)
    splits = a.split.split(",")
    ents = [e for e in all_courses() if e["split"] in splits or a.split == "all"]
    if a.slug:
        ents = [e for e in ents if e["slug"] in a.slug.split(",")]
    if a.shard is not None:
        ents = [e for i, e in enumerate(ents) if i % a.of == a.shard]
    if a.limit:
        ents = ents[:a.limit]
    modes = a.modes.split(",")
    rows = []
    if a.j > 1:
        from multiprocessing import Pool
        with Pool(a.j) as pool:
            for rs in pool.imap_unordered(_worker, [(e, modes) for e in ents]):
                rows += rs
    else:
        for e in ents:
            rows += _worker((e, modes))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(rows, open(a.out, "w"), default=float)
    print(table(rows))


def table(rows):
    from collections import defaultdict
    by = defaultdict(list)
    for r in rows:
        if "error" not in r:
            by[(r["split"], r["mode"])].append(r)
    out = ["| split | mode | courses | holes formed | hole number | number, nine-swap ok | all holes formed | "
           "fully correct | correct when all formed | clubhouse <= 100 yds |", "|" + "---|" * 10]
    for (sp, m), rs in sorted(by.items()):
        H = sum(r["N"] for r in rs)
        af = [r for r in rs if r["all_formed"]]
        out.append(f"| {sp} | {m} | {len(rs)} | {sum(r['formation'] for r in rs) / H:.1%} | "
                   f"{sum(r['number'] for r in rs) / H:.1%} | {sum(r['swap'] for r in rs) / H:.1%} | "
                   f"{np.mean([r['all_formed'] for r in rs]):.1%} | {np.mean([r['all_correct'] for r in rs]):.1%} | "
                   f"{sum(r['all_correct'] for r in af)}/{len(af)} | "
                   f"{np.mean([r.get('ch_err', 1e9) <= 100 for r in rs]):.0%} |")
    return "\n".join(out)


def combine(paths, out):
    rows = [r for p in paths for r in json.load(open(p))]
    os.makedirs(out, exist_ok=True)
    with gzip.open(os.path.join(out, "rows.json.gz"), "wt") as fh:
        json.dump(rows, fh, default=float)
    md = table(rows)
    open(os.path.join(out, "bench.md"), "w").write(md + "\n")
    print(md)


if __name__ == "__main__":
    main()
