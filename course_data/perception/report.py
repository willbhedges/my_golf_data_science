"""Pool per-course eval.json files into REPORT.md + eval.json (train states vs held-out test states).

    python course_data/perception/report.py --scenes course_data/perception/scenes [--tables DIR]
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
import sys  # noqa: E402
sys.path.insert(0, HERE)
from train import TEST_STATES, split_of  # noqa: E402

PRF = ("greens_any", "greens_hole", "tee_complexes", "tee_boxes", "fairways", "bunkers", "water", "buildings", "parking")


def _load(d):
    out = []
    for p in sorted(glob.glob(os.path.join(d, "*", "eval.json"))):
        e = json.load(open(p))
        e["slug"] = e.get("slug") or os.path.basename(os.path.dirname(p))
        out.append(e)
    return out


def pool_prf(evs, key, eligible_key="eligible"):
    tp_p = n_p = tp_t = n_t = 0
    k = 0
    for e in evs:
        b = e.get(key) or {}
        if not b.get(eligible_key):
            continue
        k += 1
        tp_p += b.get("tp_pred", 0)
        n_p += b.get("n_pred", 0)
        tp_t += b.get("tp_true", 0)
        n_t += b.get("n_true", 0)
    return dict(courses=k, precision=round(tp_p / n_p, 3) if n_p else None, recall=round(tp_t / n_t, 3) if n_t else None,
                n_pred=n_p, n_true=n_t)


def pool(evs):
    out = {k: pool_prf(evs, k) for k in PRF}
    # tee-complex precision only where OSM tees are complete
    out["tee_complexes_precision_eligible"] = pool_prf(evs, "tee_complexes", "precision_eligible")
    g = [e["greens_hole"] for e in evs if e.get("greens_hole", {}).get("eligible")]
    out["greens_practice"] = dict(practice_true=sum(x.get("practice_true", 0) for x in g),
                                  practice_called_hole=sum(x.get("practice_called_hole", 0) for x in g),
                                  practice_called_practice=sum(x.get("practice_called_practice", 0) for x in g),
                                  hole_called_practice=sum(x.get("hole_called_practice", 0) for x in g),
                                  hole_uncertain=sum(x.get("hole_uncertain", 0) for x in g))
    cp = [e["cart_paths"] for e in evs if (e.get("cart_paths") or {}).get("eligible")]
    lp = [(c["length_precision"], c["pred_km"]) for c in cp if c.get("length_precision") is not None]
    lr = [(c["length_recall"], c["true_km"]) for c in cp if c.get("length_recall") is not None]
    con = [(c["connectivity_acc"], c["transitions_osm_connected"]) for c in cp if c.get("connectivity_acc") is not None]
    out["cart_paths"] = dict(courses=len(cp),
                             length_precision=_wavg(lp), length_recall=_wavg(lr),
                             connectivity_acc=_wavg(con), transitions=sum(n for _, n in con),
                             pred_km=round(sum(c["pred_km"] for c in cp), 1), true_km=round(sum(c["true_km"] for c in cp), 1))
    rel = [e["relations"] for e in evs if (e.get("relations") or {}).get("n")]
    out["relations"] = dict(courses=len(rel), n=sum(r["n"] for r in rel),
                            top1_next_tee_acc=_wavg([(r["top1_next_tee_acc"], r["n"]) for r in rel]),
                            n_with_path=sum(r["n_with_path"] for r in rel),
                            top1_acc_when_path=_wavg([(r["top1_acc_when_path"], r["n_with_path"]) for r in rel
                                                      if r.get("top1_acc_when_path") is not None]))
    ch = [e["clubhouse"]["error_m"] for e in evs if (e.get("clubhouse") or {}).get("eligible") and e["clubhouse"].get("error_m") is not None]
    out["clubhouse"] = dict(courses=len(ch), median_error_m=_med(ch), within_50m=_frac(ch, 50), within_150m=_frac(ch, 150))
    dr = [e["driving_range"] for e in evs if (e.get("driving_range") or {}).get("eligible")]
    fp = [e["driving_range"] for e in evs if not (e.get("driving_range") or {}).get("eligible")]
    out["driving_range"] = dict(courses_with_osm_range=len(dr), hit=sum(bool(d.get("hit")) for d in dr),
                                predicted_where_none_mapped=sum(bool(d.get("predicted")) for d in fp), courses_without=len(fp))
    fa = [e["fairway_axis"] for e in evs if e.get("fairway_axis", {}).get("n")]
    out["fairway_axis"] = dict(n=sum(f["n"] for f in fa),
                               median_err_deg=_wmed([(f["median_err_deg"], f["n"]) for f in fa]),
                               within_20deg=_wavg([(f["within_20deg"], f["n"]) for f in fa]),
                               stripe_strong_n=sum(f.get("stripe_strong_n") or 0 for f in fa),
                               stripe_strong_within_20deg=_wavg([(f.get("stripe_strong_within_20deg"), f.get("stripe_strong_n") or 0)
                                                                 for f in fa if f.get("stripe_strong_within_20deg") is not None]))
    return out


def _wavg(pairs):
    pairs = [(v, w) for v, w in pairs if v is not None and w]
    if not pairs:
        return None
    return round(sum(v * w for v, w in pairs) / sum(w for _, w in pairs), 3)


def _wmed(pairs):
    pairs = [(v, w) for v, w in pairs if v is not None and w]
    if not pairs:
        return None
    v = np.repeat([p[0] for p in pairs], [int(p[1]) for p in pairs])
    return round(float(np.median(v)), 1)


def _med(v):
    return round(float(np.median(v)), 1) if v else None


def _frac(v, t):
    return round(float(np.mean(np.array(v) <= t)), 3) if v else None


def _f(x, pct=True):
    if x is None:
        return "-"
    return f"{100 * x:.0f}%" if pct else f"{x}"


def write(evs, models, path_md, path_json):
    tr = [e for e in evs if split_of(e.get("state")) == "train"]
    te = [e for e in evs if split_of(e.get("state")) == "test"]
    P = dict(train=pool(tr), test=pool(te), all=pool(evs))
    L = ["# Course perception: per-element accuracy vs OSM", "",
         f"Generated by `course_data/perception/report.py` ({time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}) from "
         f"`perceive.py` runs on GitHub Actions (`perception.yml`). Blind mode: the detectors read only NAIP + 3DEP lidar "
         f"for the course bbox; OSM is the reference. Geographic hold-out: **test states {', '.join(TEST_STATES)}** "
         f"({len(te)} courses) were never used to train or tune; train states: {len(tr)} courses.",
         f"Detections made with: `{', '.join(sorted({str(e.get('models')) for e in evs}))}` "
         f"(object models trained on the train states of an earlier run; `rules-v1` = no trained model).", "",
         "Only courses whose OSM mapping of an element is complete enough are scored for it (column `courses`).", "",
         "## Objects (held-out test states | train states)", "",
         "| element | test courses | test precision | test recall | train courses | train precision | train recall |",
         "|---|---|---|---|---|---|---|"]
    names = dict(greens_hole="hole greens (practice excluded)", greens_any="any green", tee_complexes="tee complexes (recall @ hole starts, 30 m)",
                 tee_boxes="tee boxes (8 m)", fairways="fairways (30 % overlap)", bunkers="bunkers (30 % overlap)",
                 water="water (30 % overlap)", buildings="buildings", parking="parking lots")
    for k in ("greens_hole", "greens_any", "tee_complexes", "tee_boxes", "fairways", "bunkers", "water", "buildings", "parking"):
        a, b = P["test"][k], P["train"][k]
        L.append(f"| {names[k]} | {a['courses']} | {_f(a['precision'])} | {_f(a['recall'])} | {b['courses']} | "
                 f"{_f(b['precision'])} | {_f(b['recall'])} |")
    a, b = P["test"]["tee_complexes_precision_eligible"], P["train"]["tee_complexes_precision_eligible"]
    L.append(f"| tee complexes, precision where OSM tees complete | {a['courses']} | {_f(a['precision'])} | | {b['courses']} | {_f(b['precision'])} | |")
    L += ["", "## Practice greens (hole-green courses)", "", "| split | practice true | called hole | called practice | hole greens called practice | hole greens uncertain |",
          "|---|---|---|---|---|---|"]
    for s in ("test", "train"):
        g = P[s]["greens_practice"]
        L.append(f"| {s} | {g['practice_true']} | {g['practice_called_hole']} | {g['practice_called_practice']} | "
                 f"{g['hole_called_practice']} | {g['hole_uncertain']} |")
    L += ["", "## Cart paths, ordering evidence, clubhouse, range", "",
          "| metric | test | train |", "|---|---|---|"]
    for lab, k, sub, pct in (("cart-path courses (OSM paths dense)", "cart_paths", "courses", False),
                             ("length precision (4 m)", "cart_paths", "length_precision", True),
                             ("length recall (4 m)", "cart_paths", "length_recall", True),
                             ("connectivity acc (OSM-connected hole transitions also connected)", "cart_paths", "connectivity_acc", True),
                             ("transitions scored", "cart_paths", "transitions", False),
                             ("green->next tee top-1 (edge accuracy)", "relations", "top1_next_tee_acc", True),
                             ("  same, when a cart-path route exists", "relations", "top1_acc_when_path", True),
                             ("greens scored for edges", "relations", "n", False),
                             ("clubhouse courses", "clubhouse", "courses", False),
                             ("clubhouse median error (m)", "clubhouse", "median_error_m", False),
                             ("clubhouse within 50 m", "clubhouse", "within_50m", True),
                             ("clubhouse within 150 m", "clubhouse", "within_150m", True),
                             ("driving range hit / OSM ranges", "driving_range", None, False),
                             ("fairway axis within 20 deg of the hole line", "fairway_axis", "within_20deg", True),
                             ("fairway axis median error (deg)", "fairway_axis", "median_err_deg", False),
                             ("mowing stripes (strong) within 20 deg of the hole line", "fairway_axis", "stripe_strong_within_20deg", True)):
        if sub is None:
            vals = [f"{P[s][k]['hit']} / {P[s][k]['courses_with_osm_range']}" for s in ("test", "train")]
        else:
            vals = [_f(P[s][k].get(sub), pct) for s in ("test", "train")]
        L.append(f"| {lab} | {vals[0]} | {vals[1]} |")
    if models:
        L += ["", "## Object models trained in this run (applied from the next run; held-out test states)", "",
              "| model | train rows | test rows | test AUC | test precision | test recall |", "|---|---|---|---|---|---|"]
        for k, v in (models.get("objects") or {}).items():
            if "skipped" in v:
                L.append(f"| {k} | skipped: {v['skipped']} | | | | |")
                continue
            t = v.get("test") or {}
            L.append(f"| {k} | {v['n_train']} | {v['n_test']} | {t.get('auc_pos', '-')} | {_f(t.get('precision_pos'))} | {_f(t.get('recall_pos'))} |")
        pp = models.get("path_px") or {}
        if "test" in pp:
            L.append(f"| path_px (pixels) | {pp['n_train']} | {pp['test'].get('n')} | {pp['test'].get('auc_pos', '-')} | "
                     f"{_f(pp['test'].get('precision_pos'))} | {_f(pp['test'].get('recall_pos'))} |")
    L += ["", "## Per course", "", "| course | st | split | lidar | hole greens P/R | tee cx R | paths P/R | conn | clubhouse err m | range |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for e in sorted(evs, key=lambda e: (split_of(e.get("state")), e.get("state") or "", e["slug"])):
        g, t, c = e.get("greens_hole", {}), e.get("tee_complexes", {}), e.get("cart_paths", {})
        L.append(f"| {e['slug']} | {e.get('state')} | {split_of(e.get('state'))} | {'y' if e.get('lidar') else 'n'} | "
                 f"{_f(g.get('precision'))}/{_f(g.get('recall'))}{'' if g.get('eligible') else '*'} | {_f(t.get('recall'))} | "
                 f"{_f(c.get('length_precision'))}/{_f(c.get('length_recall'))}{'' if c.get('eligible') else '*'} | "
                 f"{_f(c.get('connectivity_acc'))} | {(e.get('clubhouse') or {}).get('error_m', '-')} | "
                 f"{(e.get('driving_range') or {}).get('hit')} |")
    L += ["", "`*` = OSM mapping of that element not complete enough on this course: shown, not pooled.", "",
          "## Definitions", "",
          "* **hole greens**: perceived greens with `kind == hole` vs OSM greens a golf=hole way ends on (18 m). A green "
          "matches when its centroid is within 6 m of the OSM polygon. Practice greens (OSM greens no hole ends on) called "
          "`hole` count as false positives; perceived `practice` / `uncertain` greens are not in the hole set.",
          "* **tee complexes**: recall = share of OSM hole-way starts with a box of a perceived complex (p >= 0.5) within 30 m; "
          "precision = share of perceived complexes with a box within 25 m of an OSM tee box or hole start, on courses whose "
          "OSM tees number >= 1.5 per hole.",
          "* **fairways / bunkers / water / buildings / parking**: a perceived object is correct when >= 30 % of its pixels "
          "fall in the OSM class; an OSM object is found when >= 30 % of it is covered by perceived objects (course boundary + 40 m).",
          "* **cart paths**: length within 4 m of an OSM cart path / footpath / in-course service way (and vice versa), inside "
          "the course + 40 m, on courses with >= 1.5 km of OSM paths per 18 holes. **Connectivity**: for each consecutive "
          "hole pair whose green-end -> next-tee is connected by OSM paths (attach 45 m), the perceived graph connects them "
          "too with a route <= 2 x the OSM route + 60 m.",
          "* **edge accuracy** (ordering evidence): for each OSM hole n with hole n+1 mapped and its green perceived, the "
          "perceived tee complex with the highest `p_next` from that green is within 30 m of hole n+1's start.",
          "* **clubhouse**: distance from the perceived clubhouse point to the OSM golf=clubhouse / building=clubhouse "
          "(or a building named club house / pro shop)."]
    open(path_md, "w").write("\n".join(L) + "\n")
    json.dump(dict(built_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), test_states=list(TEST_STATES),
                   models=(models or {}).get("id"), pooled=P, courses={e["slug"]: e for e in evs}),
              open(path_json, "w"), indent=1, default=float)
    return P


def compress_scenes(d):
    """scene.json -> scene.json.gz (committed); scene.geojson dropped (scene.to_geojson rebuilds it)."""
    for p in glob.glob(os.path.join(d, "*", "scene.json")):
        with open(p, "rb") as f, gzip.open(p + ".gz", "wb", compresslevel=9) as g:
            g.write(f.read())
        os.remove(p)
    for p in glob.glob(os.path.join(d, "*", "scene.geojson")):
        os.remove(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", default=os.path.join(HERE, "scenes"))
    ap.add_argument("--tables")
    ap.add_argument("--models", default=os.path.join(HERE, "models", "models.json"))
    a = ap.parse_args()
    evs = _load(a.scenes)
    models = json.load(open(a.models)) if os.path.exists(a.models) else None
    P = write(evs, models, os.path.join(HERE, "REPORT.md"), os.path.join(HERE, "eval.json"))
    compress_scenes(a.scenes)
    print(json.dumps(P["test"], indent=1)[:4000])


if __name__ == "__main__":
    main()
