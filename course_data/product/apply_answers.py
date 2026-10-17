"""Apply the golfer's review answers (the review page's "Copy answers" JSON) to the course package, then re-plan
only the holes whose geometry changed.

  python3 course_data/product/apply_answers.py answers.json            # or '-' for stdin, or the JSON itself
      [--review course_data/packages/<slug>/out/review/review.json]    # default: from the answers' slug
      [--package-out <path>]  (default: the package in place)  [--no-replan]  [--plan-out <dir>]

What each answer does (items and frames come from review.json, so the page never needs geometry):
  tee     confirm  tees[set].verified = "golfer", confidence 1.0
          moved    tees[set].tee_ll moved dx yds right / dy yds forward in the review's frame for that hole
                   (aim_ll re-derived by platform/tee_line.py), method "golfer", confidence 1.0; hole-level tee_ll
                   too when it is the package's tee set
  hazard  confirm  the group's zones_ll get verified = "golfer", p = 1.0 (verify.py stops asking)
          absent   the group's zones_ll are deleted
          moved    the group is translated `shift` yds toward the fairway (sideways, or along the line for a
                   hazard across it), then verified
  fairway confirm  the hole's fairway zones get verified; moved: that side's edge moved `shift` yds toward the
                   centre (+ = narrower; verify.fairway_moved, the same transform the review tested)
  cut     present  the tested first-cut polygons are added (src golfer:cut); confirm: verification.no_cut = true
  gap     present  a "recovery" polygon over the tested strip is added (src golfer:gap)
          confirm  hole.verification.open_<side> = true (verify.py stops asking)
  check   playable / not_playable is recorded in hole.verification (the plan's guard still prints the CHECK)
Every answer is also recorded under hole["verification"][item id] and package["verification"]. Zone indices
are checked against review.json's fingerprints (first vertex); a mismatch (package rebuilt since the review)
skips that item with a warning.

Re-plan: decide.quick_hole (the quick plan, N = 8000, same seeds) for the changed holes only; their entries in
<plan out>/decision.json and plan.json picks are replaced and <plan out>/replan.json lists before -> after.
The book PDFs and the wind page are not rebuilt here (commit a plan request for that).

Corrections survive a package rebuild: every applied answer is also stored, with the resolved geometry (the tee's
new lon/lat, the polygons removed / before and after a move / added), in packages/<slug>/corrections.json.
reapply(package, corrections) matches stored polygons to the rebuilt package's zones by lie and overlap
(IoU >= 0.5) and redoes each correction; platform/package.py write() calls it when that file exists.
"""
import argparse
import copy
import datetime as dt
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import verify as V                                  # noqa: E402
import render as R                                  # noqa: E402

PK = V.PK

GEOM = ("moved", "absent", "present")


def _read_answers(arg):
    if arg == "-":
        return json.load(sys.stdin)
    if os.path.exists(arg):
        return json.load(open(arg))
    return json.loads(arg)


def _to_yd(fr, poly):
    q = fr.ll_to_yds(np.array(poly, float)[:, :2])
    return np.c_[q[:, 0], -q[:, 1]]


def _to_ll(fr, xa):
    xa = np.asarray(xa, float)
    return fr.yds_to_ll(np.c_[xa[:, 0], -xa[:, 1]]).tolist()


def _fp_ok(z, fp):
    p = z.get("poly") or []
    return bool(p) and abs(float(p[0][0]) - fp[0]) < 1e-6 and abs(float(p[0][1]) - fp[1]) < 1e-6


def apply(pkg, review, answers, log=print, corrections_out=None):
    """-> (new package dict, {hole ref: [item ids that changed geometry]}, warnings). corrections_out (a list)
    receives the resolved corrections for store_corrections()."""
    pkg = copy.deepcopy(pkg)
    tee_set = review["tee_set"]
    items = {it["id"]: it for it in review["items"]}
    changed, warn = {}, []
    removals = {}
    corr = []
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    for a in answers.get("answers", []):
        it = items.get(a.get("id"))
        if it is None:
            warn.append(f"{a.get('id')}: not in this review")
            continue
        ref = it["hole"]
        h = pkg["holes"].get(ref)
        hv = review["holes"].get(ref) or {}
        if h is None:
            warn.append(f"{a['id']}: hole {ref} not in the package")
            continue
        ans = a.get("answer")
        rec = dict(a, at=answers.get("answered") or now, review_built=review.get("built"))
        h.setdefault("verification", {})[it["id"]] = rec
        fr = R.Frame.from_json(hv["frame"]) if hv.get("frame") else None
        if it["type"] == "tee":
            ent = _tee(h, tee_set)
            if ent is None:
                warn.append(f"{a['id']}: no {tee_set} tee entry")
                continue
            if ans == "moved" and fr is not None and (abs(a.get("dx", 0)) > 0.5 or abs(a.get("dy", 0)) > 0.5):
                new = fr.yds_to_ll([[float(a.get("dx", 0)), -float(a.get("dy", 0))]])[0].tolist()
                aim, _ = PK._tee_line_mod().aim_point(new, h.get("hole_line_ll"), PK._ll(h.get("green_ll")),
                                                      float(ent.get("card_yards") or h.get("length") or 0) or None,
                                                      int(h.get("par") or 4))
                ent.update(tee_ll=new, aim_ll=aim, method="golfer", confidence=1.0, verified="golfer",
                           moved_yds=[a.get("dx", 0), a.get("dy", 0)])
                if ent.get("measured_yards") is not None:
                    ent["measured_yards"] = round(float(ent["measured_yards"]) - float(a.get("dy", 0)), 1)
                if str(pkg.get("tee_set", "")).lower() == tee_set.lower():
                    h["tee_ll"], h["aim_ll"] = new, aim
                changed.setdefault(ref, []).append(it["id"])
            else:
                ent.update(confidence=1.0, verified="golfer")
            corr.append(dict(kind="tee", hole=ref, tee_set=tee_set, answer=ans, tee_ll=ent.get("tee_ll"), id=it["id"]))
        elif it["type"] in ("hazard", "fairway"):
            zl = h.get("zones_ll") or []
            idx = it.get("zone_idx", [])
            fps = it.get("zone_fp", [])
            if any(i >= len(zl) or not _fp_ok(zl[i], fp) for i, fp in zip(idx, fps)):
                warn.append(f"{a['id']}: zones changed since the review (package rebuilt?): skipped")
                continue
            lie = zl[idx[0]].get("lie") if idx else None
            before = [copy.deepcopy(zl[i]["poly"]) for i in idx]
            if ans == "absent" and it["type"] == "hazard":
                removals.setdefault(ref, set()).update(idx)
                changed.setdefault(ref, []).append(it["id"])
                corr.append(dict(kind="zones", hole=ref, answer="absent", lie=lie, polys=before, id=it["id"]))
            elif ans == "moved" and abs(float(a.get("shift", 0))) >= 0.5 and fr is not None:
                if it["type"] == "fairway":
                    moved = V.fairway_moved(h, fr, idx, it["side"], float(a["shift"]), float(hv["base"]["aim"]))
                    for i in idx:
                        zl[i]["poly"] = moved[i]["poly"]
                else:
                    vec = np.array(it["toward"], float) * float(a["shift"])
                    for i in idx:
                        zl[i]["poly"] = _to_ll(fr, _to_yd(fr, zl[i]["poly"]) + vec)
                for i in idx:
                    zl[i].update(verified="golfer", p=1.0, moved_yds=float(a["shift"]))
                changed.setdefault(ref, []).append(it["id"])
                corr.append(dict(kind="zones", hole=ref, answer="moved", lie=lie, polys=before,
                                 after=[zl[i]["poly"] for i in idx], id=it["id"]))
            else:
                for i in idx:
                    zl[i].update(verified="golfer", p=1.0)
                corr.append(dict(kind="zones", hole=ref, answer="confirm", lie=lie, polys=before, id=it["id"]))
        elif it["type"] in ("gap", "cut"):
            if ans == "present" and fr is not None:
                lie = "recovery" if it["type"] == "gap" else "first_cut"
                polys = [_to_ll(fr, it["strip_xa"])] if it["type"] == "gap" else [_to_ll(fr, c) for c in it["cut_xa"]]
                for poly in polys:
                    h.setdefault("zones_ll", []).append(dict(lie=lie, poly=poly, src=f"golfer:{it['type']}", p=1.0,
                                                             verified="golfer"))
                changed.setdefault(ref, []).append(it["id"])
                corr.append(dict(kind="add", hole=ref, lie=lie, polys=polys, id=it["id"]))
            else:
                flag = f"open_{it['side']}" if it["type"] == "gap" else "no_cut"
                h["verification"][flag] = True
                corr.append(dict(kind="flag", hole=ref, flag=flag, id=it["id"]))
        # check: recorded only
    for ref, idx in removals.items():
        zl = pkg["holes"][ref]["zones_ll"]
        pkg["holes"][ref]["zones_ll"] = [z for i, z in enumerate(zl) if i not in idx]
    pkg.setdefault("verification", {}).setdefault("rounds", []).append(
        dict(review_built=review.get("built"), applied=now, answers=len(answers.get("answers", [])),
             changed_holes=sorted(changed)))
    _reframe(pkg, warn)
    for c in corr:
        c["at"] = answers.get("answered") or now
    pkg["verification"]["rounds"][-1]["corrections"] = len(corr)
    if corrections_out is not None:
        corrections_out.extend(corr)
    return pkg, changed, warn


# ----------------------------------------------------------------------------- corrections that survive a rebuild
def _xy(poly, lat0):
    k = np.cos(np.radians(lat0))
    return [(float(p[0]) * k * 111320.0, float(p[1]) * 111320.0) for p in poly]


def _iou(a, b, lat0):
    try:
        pa, pb = V.shapely_poly(_xy(a, lat0)), V.shapely_poly(_xy(b, lat0))
        u = pa.union(pb).area
        return pa.intersection(pb).area / u if u > 0 else 0.0
    except Exception:                                        # noqa: BLE001
        return 0.0


def _match(zl, lie, polys, lat0, thr=0.5):
    """Indices of zones of `lie` that overlap any stored polygon with IoU >= thr."""
    out = []
    for i, z in enumerate(zl):
        if not isinstance(z, dict) or z.get("lie") != lie or len(z.get("poly") or []) < 3:
            continue
        if any(_iou(z["poly"], p, lat0) >= thr for p in polys):
            out.append(i)
    return out


def store_corrections(slug_dir, corr, review_built=None):
    path = os.path.join(slug_dir, "corrections.json")
    doc = json.load(open(path)) if os.path.exists(path) else {"schema": "corrections/1", "items": []}
    keep = {c["id"]: c for c in doc["items"]}
    for c in corr:
        keep[c["id"]] = dict(c, review_built=review_built)          # a later answer to the same item wins
    doc["items"] = list(keep.values())
    with open(path, "w") as fh:
        json.dump(doc, fh, indent=1)
    return path


def reapply(pkg, corrections, reframe=None, log=print):
    """Redo stored corrections on a (rebuilt) package, in place. -> {applied, skipped}."""
    items = corrections.get("items", corrections) if isinstance(corrections, dict) else corrections
    done, skipped = 0, []
    for c in items:
        h = (pkg.get("holes") or {}).get(c.get("hole"))
        if h is None:
            skipped.append(c.get("id"))
            continue
        lat0 = float((h.get("green_ll") or h.get("tee_ll") or [0, 40])[1])
        zl = h.setdefault("zones_ll", [])
        h.setdefault("verification", {})[c["id"]] = dict(answer=c.get("answer", c["kind"]), reapplied=True, at=c.get("at"))
        if c["kind"] == "tee":
            ent = _tee(h, c["tee_set"])
            if ent is None or not c.get("tee_ll"):
                skipped.append(c["id"])
                continue
            ent.update(tee_ll=c["tee_ll"], method="golfer" if c["answer"] == "moved" else ent.get("method"),
                       confidence=1.0, verified="golfer")
            aim, _ = PK._tee_line_mod().aim_point(c["tee_ll"], h.get("hole_line_ll"), PK._ll(h.get("green_ll")),
                                                  float(ent.get("card_yards") or h.get("length") or 0) or None,
                                                  int(h.get("par") or 4))
            ent["aim_ll"] = aim
            if str(pkg.get("tee_set", "")).lower() == c["tee_set"].lower():
                h["tee_ll"], h["aim_ll"] = c["tee_ll"], aim
        elif c["kind"] == "zones":
            idx = _match(zl, c["lie"], c["polys"], lat0)
            if not idx:
                skipped.append(c["id"])
                continue
            if c["answer"] == "absent":
                h["zones_ll"] = [z for i, z in enumerate(zl) if i not in set(idx)]
            elif c["answer"] == "moved":
                src = zl[idx[0]].get("src")
                h["zones_ll"] = [z for i, z in enumerate(zl) if i not in set(idx)] + \
                    [dict(lie=c["lie"], poly=p, src=f"golfer:{src}", p=1.0, verified="golfer") for p in c["after"]]
            else:
                for i in idx:
                    zl[i].update(verified="golfer", p=1.0)
        elif c["kind"] == "add":
            for p in c["polys"]:
                if not _match(zl, c["lie"], [p], lat0, thr=0.8):
                    zl.append(dict(lie=c["lie"], poly=p, src="golfer:added", p=1.0, verified="golfer"))
        elif c["kind"] == "flag":
            h["verification"][c["flag"]] = True
        done += 1
    if reframe is not None and done:
        try:
            reframe(pkg)
        except Exception as e:                               # noqa: BLE001
            log(f"  ! reapply: reframe failed ({type(e).__name__}: {e})")
    pkg.setdefault("verification", {})["reapplied"] = dict(applied=done, skipped=skipped)
    log(f"  golfer corrections re-applied: {done}, skipped (no matching zone / hole): {len(skipped)}")
    return dict(applied=done, skipped=skipped)


def _tee(h, tee_set):
    for k, v in (h.get("tees") or {}).items():
        if k.lower() == tee_set.lower():
            return v
    return None


def _reframe(pkg, warn):
    """Refresh the package's yard-frame zones (platform.package.reframe), if the platform module imports."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("cdp_platform_package", os.path.join(CD, "platform", "package.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.reframe(pkg)
    except Exception as e:                                   # noqa: BLE001
        warn.append(f"reframe skipped ({type(e).__name__}: {e}); zones_ll is authoritative")


def replan(pkg_path, tee_set, refs, workers=1, n=8000, log=print):
    """Quick plan (decide.quick_hole) for the given holes of the package at pkg_path -> {ref: result}."""
    import decide
    C = PK.load(pkg_path, tee_set)
    keys = [k for k in C.holes if str(k) in {str(r) for r in refs}]
    if not keys:
        return {}
    decide.bind(C.holes)
    res = {}
    if workers > 1 and len(keys) > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(min(workers, len(keys))) as pool:
            for k, r in pool.imap_unordered(decide._work, [("quick", k, dict(n=n)) for k in keys]):
                res[str(k)] = r
    else:
        for k in keys:
            res[str(k)] = decide._work(("quick", k, dict(n=n)))[1]
    for k, r in res.items():
        log(f"  re-planned {k}: {r['pick']} aim {r['aim']:+.1f} margin {r['margin']:.3f}")
    return res


def write_plan(plan_out, results, tee_set):
    """Replace the re-planned holes in <plan_out>/decision.json and plan.json picks; write replan.json."""
    os.makedirs(plan_out, exist_ok=True)
    dp, pp = os.path.join(plan_out, "decision.json"), os.path.join(plan_out, "plan.json")
    dec = json.load(open(dp)) if os.path.exists(dp) else {}
    before = {k: (dict(pick=dec[k]["pick"], aim=dec[k]["aim"]) if k in dec else None) for k in results}
    for k, r in results.items():
        dec[k] = r
    with open(dp, "w") as fh:
        json.dump(dec, fh, indent=1, default=float)
    if os.path.exists(pp):
        plan = json.load(open(pp))
        for k, r in results.items():
            plan.setdefault("picks", {})[k] = dict(club=r["pick"], aim=r["aim"], zone=r["zone"], margin=round(r["margin"], 4),
                                                   tie=r["tie"], conf=r.get("conf"), check=r.get("check") or [],
                                                   status="CHECK" if r.get("check") else "PLAY", replanned="golfer answers")
        with open(pp, "w") as fh:
            json.dump(plan, fh, indent=1, default=float)
    rp = dict(tee_set=tee_set, at=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
              holes={k: dict(before=before[k], after=dict(pick=r["pick"], aim=r["aim"], tie=r["tie"]))
                     for k, r in results.items()})
    with open(os.path.join(plan_out, "replan.json"), "w") as fh:
        json.dump(rp, fh, indent=1)
    return rp


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("answers", help="answers JSON file, '-' for stdin, or the JSON text")
    ap.add_argument("--review")
    ap.add_argument("--package-out")
    ap.add_argument("--plan-out")
    ap.add_argument("--no-replan", action="store_true")
    ap.add_argument("--no-store", action="store_true", help="do not record the corrections for rebuilds")
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args(argv)
    ans = _read_answers(a.answers)
    review_path = a.review or os.path.join(CD, "packages", ans["slug"], "out", "review", "review.json")
    review = json.load(open(review_path))
    if ans.get("review_built") and ans["review_built"] != review.get("built"):
        print(f"! answers are for the review built {ans['review_built']}, this review is {review.get('built')}")
    pkg_path = os.path.join(ROOT, review["package"])
    pkg = json.load(open(pkg_path))
    corr = []
    new, changed, warn = apply(pkg, review, ans, corrections_out=corr)
    out_pkg = a.package_out or pkg_path
    with open(out_pkg, "w") as fh:
        json.dump(new, fh, separators=(",", ":"))
    if not a.no_store:
        cp = store_corrections(os.path.dirname(pkg_path), corr, review.get("built"))
        print(f"  corrections stored in {os.path.relpath(cp, ROOT)} (re-applied on the next package rebuild)")
    print(f"applied {len(ans.get('answers', []))} answers -> {os.path.relpath(out_pkg, ROOT)}; "
          f"geometry changed on holes {sorted(changed) or 'none'}")
    for w in warn:
        print("  !", w)
    if changed and not a.no_replan:
        res = replan(out_pkg, review["tee_set"], list(changed), workers=a.workers)
        plan_out = a.plan_out or os.path.join(os.path.dirname(pkg_path), "out")
        rp = write_plan(plan_out, res, review["tee_set"])
        for k, v in rp["holes"].items():
            b = v["before"] or {}
            print(f"  hole {k}: {b.get('pick', '-')} {b.get('aim', 0):+.0f} -> {v['after']['pick']} {v['after']['aim']:+.0f}")
    return new, changed


if __name__ == "__main__":
    main()
