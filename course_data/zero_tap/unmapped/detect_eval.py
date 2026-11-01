"""Unmapped tiers: detection (greens / tee complexes) measured separately from pairing.

    python course_data/zero_tap/unmapped/detect_eval.py --split dev [--results results/<method>/unmapped_card ...]

Detection is scored with the bench scorer's own tolerances (bench.Matcher.green_ok / tee_ok), so a "missed green"
here is exactly a green no method can form a hole on. Every number is reported on all unmapped courses and on the
perception hold-out subset (states the perception object models never trained on: GA KY MN UT ME WY); the other
courses were the perception models' training labels, so their detection is in-sample.
"""
import argparse
import gzip
import json
import math
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(ZT))
sys.path.insert(0, ZT)
import bench as B  # noqa: E402

PERC_TEST_STATES = {"GA", "KY", "MN", "UT", "ME", "WY"}


def perc_split(row):
    return "held_out" if str(row.get("state") or "").upper() in PERC_TEST_STATES else "in_sample"


def load_scene(row):
    p = row["files"].get("scene")
    with gzip.open(os.path.join(ROOT, p), "rt") as fh:
        return json.load(fh)


def green_cands(scene):
    return [dict(id=g["id"], ll=g["centroid"], p=float(g.get("p", 1)), p_hole=float(g.get("p_hole", g.get("p", 1))),
                 kind=g.get("kind"), area=float(g.get("area_m2") or 0)) for g in scene.get("greens", [])]


def tee_cands(scene):
    out = []
    for t in scene.get("tee_complexes", []):
        pts = [t["centroid"]] + [b["centroid"] for b in t.get("boxes", []) if b.get("centroid")]
        out.append(dict(id=t["id"], ll=t["centroid"], pts=pts, p=float(t.get("p", 1)) * (1 - float(t.get("p_range_tee") or 0)),
                        virtual=bool(t.get("virtual"))))
    return out


def detect_course(t, greens, tees, gsel, tsel):
    """greens / tees: candidate lists; gsel / tsel: predicates selecting the 'detected' ones.
    -> dict of counts (true holes N, greens found, selected greens, selected greens that are true, same for tees)."""
    M = B.Matcher(t)
    N = len(M.holes)
    gsel_l = [g for g in greens if gsel(g)]
    tsel_l = [x for x in tees if tsel(x)]
    gp = [M.pj.fwd(*g["ll"][:2]) for g in gsel_l]
    tp = [[M.pj.fwd(*q[:2]) for q in x["pts"]] for x in tsel_l]
    g_hit = [any(M.green_ok(j, p) for p in gp) for j in range(N)]
    t_hit = [any(M.tee_ok(j, pts) for pts in tp) for j in range(N)]
    g_true = sum(1 for p in gp if any(M.green_ok(j, p) for j in range(N)))
    t_true = sum(1 for pts in tp if any(M.tee_ok(j, pts) for j in range(N)))
    return dict(N=N, g_rec=sum(g_hit), g_sel=len(gp), g_true=g_true, t_rec=sum(t_hit), t_sel=len(tp), t_true=t_true,
                both=sum(1 for a, b in zip(g_hit, t_hit) if a and b), g_hit=g_hit, t_hit=t_hit)


def pairing_course(res, t, det_any):
    """Formed holes + why the unformed ones failed: no green candidate at all / no tee candidate / both exist."""
    sc = B.score_course(res, t)
    N = sc["N"]
    M = B.Matcher(t)
    formed = set()
    for ph in (res or {}).get("holes") or []:
        j, _ = M.match(ph)
        if j is not None:
            formed.add(j)
    why = defaultdict(int)
    for j in range(N):
        if j in formed:
            continue
        if not det_any["g_hit"][j]:
            why["no_green_cand"] += 1
        elif not det_any["t_hit"][j]:
            why["no_tee_cand"] += 1
        else:
            why["mispaired"] += 1
    return dict(N=N, formed=len(formed), all_right=int(len(formed) == N and sc["n_pred"] == N), number=sc["number"],
                holes_ok=int(sc["holes_ok"]), why=dict(why))


SELECTORS = {
    "hole_kind": (lambda g: g["kind"] == "hole", lambda x: x["p"] >= 0.5),
    "p>=0.5": (lambda g: g["p"] >= 0.5, lambda x: x["p"] >= 0.5),
    "any": (lambda g: True, lambda x: True),
}


def agg(rows, keys):
    s = defaultdict(float)
    for r in rows:
        for k in keys:
            s[k] += r[k]
    return s


def pct(a, b):
    return f"{100.0 * a / b:.1f}%" if b else "-"


def run(split, result_dirs, extra_scene=None):
    rows = [r for r in B.courses(split, tier="unmapped_card")]
    out = dict(split=split, n=len(rows), detection={}, pairing={})
    per = []
    for r in rows:
        t = B.truth(r["slug"])
        sc = extra_scene(r) if extra_scene else load_scene(r)
        G, T = green_cands(sc), tee_cands(sc)
        d = {name: detect_course(t, G, T, *sel) for name, sel in SELECTORS.items()}
        per.append(dict(row=r, t=t, det=d))
    for sub in ("all", "held_out", "in_sample"):
        P = [x for x in per if sub == "all" or perc_split(x["row"]) == sub]
        out["detection"][sub] = {}
        for name in SELECTORS:
            s = agg([x["det"][name] for x in P], ["N", "g_rec", "g_sel", "g_true", "t_rec", "t_sel", "t_true", "both"])
            out["detection"][sub][name] = dict(
                courses=len(P), holes=int(s["N"]), green_recall=s["g_rec"] / max(1, s["N"]),
                green_precision=s["g_true"] / max(1, s["g_sel"]), tee_recall=s["t_rec"] / max(1, s["N"]),
                tee_precision=s["t_true"] / max(1, s["t_sel"]), both_recall=s["both"] / max(1, s["N"]),
                courses_all_greens=sum(1 for x in P if x["det"][name]["g_rec"] == x["det"][name]["N"]),
                courses_all_both=sum(1 for x in P if x["det"][name]["both"] == x["det"][name]["N"]))
    for rd in result_dirs:
        res = {x["slug"]: x for x in (B.load_results(rd) if os.path.exists(rd) else [])}
        key = os.path.relpath(rd, os.path.join(ZT, "results"))
        out["pairing"][key] = {}
        prs = [(x, pairing_course(res.get(x["row"]["slug"]), x["t"], x["det"]["any"])) for x in per]
        for sub in ("all", "held_out", "in_sample"):
            P = [p for x, p in prs if sub == "all" or perc_split(x["row"]) == sub]
            N = sum(p["N"] for p in P)
            why = defaultdict(int)
            for p in P:
                for k, v in p["why"].items():
                    why[k] += v
            out["pairing"][key][sub] = dict(courses=len(P), holes=N, paired=sum(p["formed"] for p in P) / max(1, N),
                                            all_pairs_right=sum(p["all_right"] for p in P) / max(1, len(P)),
                                            numbered=sum(p["number"] for p in P) / max(1, N),
                                            holes_right=sum(p["holes_ok"] for p in P) / max(1, len(P)),
                                            unformed=dict(why))
    return out


def show(o):
    print(f"== {o['split']} ({o['n']} unmapped courses)")
    print("detection   subset     selector    holes  green R / P     tee R / P     both R  courses all greens / all both")
    for sub, d in o["detection"].items():
        for name, v in d.items():
            print(f"  {sub:10s} {name:10s} {v['holes']:5d}  {100*v['green_recall']:5.1f} / {100*v['green_precision']:5.1f}  "
                  f"{100*v['tee_recall']:5.1f} / {100*v['tee_precision']:5.1f}  {100*v['both_recall']:5.1f}  "
                  f"{v['courses_all_greens']}/{v['courses']}  {v['courses_all_both']}/{v['courses']}")
    for m, d in o["pairing"].items():
        for sub, v in d.items():
            print(f"  {m:34s} {sub:10s} paired {100*v['paired']:5.1f}  all-pairs {100*v['all_pairs_right']:5.1f}  "
                  f"numbered {100*v['numbered']:5.1f}  holes-right {100*v['holes_right']:5.1f}  unformed {v['unformed']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev")
    ap.add_argument("--results", nargs="*", default=[])
    ap.add_argument("--json")
    a = ap.parse_args()
    o = run(a.split, a.results)
    show(o)
    if a.json:
        json.dump(o, open(a.json, "w"), indent=1)
