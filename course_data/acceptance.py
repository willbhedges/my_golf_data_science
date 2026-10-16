"""Acceptance test: auto-built Spirit Hollow vs the hand-reviewed spirit_hollow/course.py.

  python3 course_data/acceptance.py                 # oracle tees: auto build with the traced lengths
  python3 course_data/acceptance.py --holes course_data/spirit_hollow/holes.json   # a pipeline build as is
  python3 course_data/acceptance.py --fast          # 4,000 swings per sim instead of 20,000

For each traced tee shot (1, 2B, 2F, 4, 5, 6, 8, 9B, 9F, 10, 11, 13, 14, 16, 17, 18) and par 3 (7, 12, 15):

  registration  traced screenshot px -> the auto hole's yard frame. Preferred: the imagery team's
                NAIP registration (course_data/imagery/spirit_hollow/traced_registration.json, ECC on
                gradient images: a true georeference, independent of both maps). Fallback: a rigid fit
                (rotation, shift, scale 0.95-1.05) of the traced lie raster onto the auto lie raster on
                fairway/water/sand, which never looks at the tee or green.
  tee, green    position error in yds after registration.
  length        auto length - traced length (frame-free).
  IoU           per lie class on the landing-zone grid (220-340 yds along, +/-45 yds, 5-yd step) laid
                out in the traced frame; "own-frame" IoU also reported (same along/lat in each map's own
                frame = what the model sees for a given aim).
  club          argmin over Driver / 2-wood / 4-wood of tee_strategy.best_aim EV, on each map.

Bar (ARCHITECTURE.md section 7): tee and green <= 10 yds, |length| <= 5 yds, landing-zone IoU > 0.6 for
water / OB / trees where either map has the class, same club on >= 80% of tee shots.
Writes course_data/spirit_hollow/acceptance.json and acceptance.md.
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(ROOT, "spirit_hollow"), os.path.join(ROOT, "mozingo")]
import pipeline as P                                      # noqa: E402
import tee_strategy as t                                  # noqa: E402
import course                                             # noqa: E402

CDIR = os.path.join(HERE, "spirit_hollow")
REG = os.path.join(HERE, "imagery", "spirit_hollow", "traced_registration.json")
WOODS = ["Driver", "2-wood", "4-wood"]
CLASSES = ["fairway", "rough", "recovery", "native", "water", "sand", "ob"]
BAR = dict(tee=10.0, green=10.0, length=5.0, iou=0.6, iou_classes=("water", "ob", "recovery"), club=0.8)
MIN_ECC = 0.3
SCALES = (1.0,)          # both maps are in yards; a free scale lets wide traced fairways shrink onto OSM's


def ref_of(k):
    return str(k).rstrip("BF")


# ----------------------------------------------------------------------------- auto builds
def oracle_builds():
    """Two pipeline builds with the traced lengths as the card (B tees, then F tees), keyed like course.py."""
    out = {}
    for variant in ("B", "F"):
        lens = {}
        for k, h in course.HOLES.items():
            if str(k)[-1:] in "BF" and str(k)[-1] != variant:
                continue
            lens[ref_of(k)] = float(h["length"])
        for k, p in course.PAR3.items():
            lens[str(k)] = float(p["center"])
        m = P.build_course("Spirit Hollow", "white", lens, render=False, tee_stage=False, vision=False, layers=False)
        for k in list(course.HOLES) + list(course.PAR3):
            if str(k)[-1:] in "BF" and str(k)[-1] != variant:
                continue
            if ref_of(k) in m["holes"] and k not in out:
                out[k] = m["holes"][ref_of(k)]
    return out


LOHO = os.path.join(HERE, "imagery", "spirit_hollow", "gapfill_loho")


def loho_builds():
    """Oracle tees + the imagery gap-fill from the leave-one-hole-out model that never saw hole k
    (ARCHITECTURE.md section 7, circularity rule a). One geometry build per traced hole."""
    fc = json.load(open(os.path.join(CDIR, "osm.geojson")))
    out = {}
    for k, h in course.HOLES.items():
        f = os.path.join(LOHO, f"{k}.geojson")
        if not os.path.exists(f):
            print(f"  {k}: no LOHO gap-fill file; OSM only")
        extra, _ = P.vision_layers(None, [f] if os.path.exists(f) else [])
        holes, how, _ = P.build_holes(fc, "white", {ref_of(k): float(h["length"])}, extra, None)
        a = holes[ref_of(k)]
        a["vision"] = os.path.relpath(f, ROOT) if os.path.exists(f) else None
        out[k] = a
    for k, p in course.PAR3.items():
        holes, _, _ = P.build_holes(fc, "white", {str(k): float(p["center"])}, [], None)
        out[k] = holes[str(k)]
    return out


def from_model(path):
    """holes.json (course_model/1) or a platform package.json (course_package/1: yard-frame zones)."""
    m = json.load(open(path))
    out = {}
    for k in list(course.HOLES) + list(course.PAR3):
        h = m["holes"].get(ref_of(k))
        if h is None:
            continue
        h = dict(h)
        if "zones" in h and h["zones"] and isinstance(h["zones"][0], dict):      # [{lie, poly}] variant
            h["zones"] = [(z["lie"], z["poly"]) for z in h["zones"]]
        out[k] = h
    return out


def as_model_hole(h):
    """holes.json hole -> the dict tee_strategy wants (tuples, aim range)."""
    d = dict(h)
    d["tee"], d["dot270"], d["green"] = tuple(h["tee"]), tuple(h["dot270"]), tuple(h["green"])
    d["zones"] = [(n, [tuple(p) for p in poly]) for n, poly in P.model_zones(h["zones"])]
    d.setdefault("aim_min", -60)   # as course_auto.py
    d.setdefault("aim_max", 60)
    return d


# ----------------------------------------------------------------------------- frames
def px_to_yds(h, px):
    tee, f, r, ppy = P.yard_frame(h)
    d = (np.atleast_2d(px) - tee) / ppy
    return np.c_[d @ r, -(d @ f)]                         # (x right, y = -along)


def yds_to_px(h, xy):
    tee, f, r, ppy = P.yard_frame(h)
    xy = np.atleast_2d(xy)
    return tee + (xy[:, :1] * r - xy[:, 1:2] * f) * ppy


def lies_yds(h, xy):
    return t.lie_at(h, yds_to_px(h, xy))


_RENDER = None


def auto_frame(a, ref):
    """The auto hole's georeferenced Frame (imagery/render.py), or None."""
    global _RENDER
    if _RENDER is None:
        _RENDER = P.load_module(os.path.join(HERE, "imagery", "render.py"), "cd_imagery_render") or False
    if not _RENDER:
        return None
    if "tee_ll" in a and "aim_ll" in a:                      # geometry's frame: UTM yards, tee_ll -> aim_ll
        ppy = float(np.hypot(*np.subtract(a["dot270"], a["tee"]))) / 270.0   # works for pixel and yard frames
        return _RENDER.Frame(a["tee_ll"], a["aim_ll"], ppy=ppy, tee_px=a["tee"], proj="utm")
    lines = _RENDER._osm_holes(CDIR)
    if "lonlat_tee" not in a or ref not in lines:
        return None
    return _RENDER.Frame(a["lonlat_tee"], _RENDER.aim_point(a["lonlat_tee"], lines[ref], proj="utm"),
                         ppy=a["px_per_yd"], tee_px=a["tee"], proj="utm")


def georef_transform(k, a, regs):
    """traced px -> auto yard frame via the NAIP registration, or None."""
    reg = regs.get(str(k))
    if not reg or not (reg.get("ecc") or 0) >= MIN_ECC:
        return None, None
    fa = auto_frame(a, ref_of(k))
    if fa is None:
        return None, None
    fr = _RENDER.Frame.from_json(reg["frame"])
    W2 = np.array(reg["warp"])

    def T(px):
        q = np.atleast_2d(np.asarray(px, float)) @ W2[:, :2].T + W2[:, 2]
        return px_to_yds(a, fa.ll_to_px(fr.px_to_ll(q)))
    return T, dict(method="naip_registration", ecc=round(reg["ecc"], 3), scale=reg.get("scale"),
                   rot_deg=reg.get("rot_deg"))


def raster_transform(h, a):
    """Rigid (+scale) fit of the traced lie raster onto the auto lie raster (fairway, water, sand)."""
    # auto raster, 2-yd cells, yard frame
    xs, ys = np.arange(-160, 161, 2.0), np.arange(-520, 61, 2.0)
    gx, gy = np.meshgrid(xs, ys)
    alie = lies_yds(a, np.c_[gx.ravel(), gy.ravel()]).reshape(gx.shape)
    # traced sample points: visible part of the screenshot, 80-430 yds along, in traced yards
    ax_, lx_ = np.meshgrid(np.arange(80, 431, 4.0), np.arange(-110, 111, 4.0))
    al, la = ax_.ravel(), lx_.ravel()
    px = P.to_px(h, al, la)
    vis = (px[:, 0] >= 0) & (px[:, 0] <= 920) & (px[:, 1] >= 540) & (px[:, 1] <= 2000)
    tl = t.lie_at(h, px[vis])
    txy = np.c_[la[vis], -al[vis]]
    cls = [c for c in ("fairway", "water", "sand") if (tl == c).any() and (alie == c).any()]
    if not cls:
        return None, None
    masks = {c: tl == c for c in cls}

    def score(th, dx, dy, s):
        c, si = np.cos(th), np.sin(th)
        q = s * (txy @ np.array([[c, si], [-si, c]])) + [dx, dy]
        ix = np.clip(((q[:, 0] - xs[0]) / 2).round().astype(int), 0, len(xs) - 1)
        iy = np.clip(((q[:, 1] - ys[0]) / 2).round().astype(int), 0, len(ys) - 1)
        lab = alie[iy, ix]
        tot = 0.0
        for c_ in cls:
            A, B = masks[c_], lab == c_
            tot += 2 * np.sum(A & B) / max(A.sum() + B.sum(), 1)
        return tot / len(cls)

    best = (-1, 0, 0, 0, 1)
    for th in np.radians(np.arange(-15, 15.1, 1.5)):
        for s in SCALES:
            for dx in range(-40, 41, 5):
                for dy in range(-40, 41, 5):
                    v = score(th, dx, dy, s)
                    if v > best[0]:
                        best = (v, th, dx, dy, s)
    for step_th, step_d, step_s in ((np.radians(0.5), 2, 0.01), (np.radians(0.2), 1, 0.005)):
        v0, th0, dx0, dy0, s0 = best
        for th in th0 + step_th * np.arange(-2, 3):
            for s in ([s0] if len(SCALES) == 1 else s0 + step_s * np.arange(-2, 3)):
                for dx in dx0 + step_d * np.arange(-2, 3):
                    for dy in dy0 + step_d * np.arange(-2, 3):
                        v = score(th, dx, dy, s)
                        if v > best[0]:
                            best = (v, th, dx, dy, s)
    v, th, dx, dy, s = best
    c, si = np.cos(th), np.sin(th)

    def T(pxs):
        q = px_to_yds(h, pxs)
        return s * (q @ np.array([[c, si], [-si, c]])) + [dx, dy]
    return T, dict(method="lie_raster_fit", dice=round(float(v), 3), classes=cls, rot_deg=round(float(np.degrees(th)), 2),
                   shift=[float(dx), float(dy)], scale=round(float(s), 3))


# ----------------------------------------------------------------------------- metrics
def iou_table(tl, al):
    out = {}
    for c in CLASSES:
        A, B = tl == c, al == c
        u = np.sum(A | B)
        if u:
            out[c] = round(float(np.sum(A & B) / u), 3)
    return out


def best_club(hmap, k, z):
    saved = t.HOLES
    t.HOLES = hmap
    try:
        res = {c: t.best_aim(k, c, z=z) for c in WOODS}
    finally:
        t.HOLES = saved
    b = min(res, key=lambda c: res[c]["ev"])
    return b, {c: round(float(r["ev"]), 4) for c, r in res.items()}, float(res[b]["aim"])


def green_uncertainty(k):
    """Spread of the traced green (yds) when the app's three Center numbers move by their +/-0.5-yd
    rounding: the trilateration is ill-conditioned laterally for far greens."""
    if k not in course.APP or course.GREEN_SIDE.get(k, 0) == 0:
        return None
    d = np.array(course.APP[k], float)
    side = course.GREEN_SIDE[k]
    pts = []
    for e in np.array(np.meshgrid(*[[-0.5, 0, 0.5]] * 3)).reshape(3, -1).T:
        al, lat = course.green_from_app(*(d + e), side)
        pts.append((al, lat))
    pts = np.array(pts)
    return dict(along=round(float(np.ptp(pts[:, 0]) / 2), 1), lat=round(float(np.ptp(pts[:, 1]) / 2), 1))


def tee_hole(k, h, a, regs, z):
    am = as_model_hole(a)
    T, reg = georef_transform(k, am, regs)
    if T is None:
        T, reg = raster_transform(h, am)
    row = dict(hole=str(k), par=h["par"], traced_len=h["length"], auto_len=a["length"],
               length_err=a["length"] - h["length"], tee_choice=a.get("tee_choice"),
               confidence=(a.get("auto") or {}).get("score"))
    a_green = px_to_yds(am, am["green"])[0]
    if T is not None:
        row["registration"] = reg
        row["tee_err"] = round(float(np.linalg.norm(T(h["tee"])[0])), 1)
        row["green_err"] = round(float(np.linalg.norm(T(h["green"])[0] - a_green)), 1)
        row["green_unc"] = green_uncertainty(k)
    else:
        row["registration"] = dict(method="none")
    if reg and reg.get("method") == "naip_registration":         # independent cross-check of the georeference
        T2, reg2 = raster_transform(h, am)
        if T2 is not None:
            reg2["tee_err"] = round(float(np.linalg.norm(T2(h["tee"])[0])), 1)
            reg2["green_err"] = round(float(np.linalg.norm(T2(h["green"])[0] - a_green)), 1)
            row["registration_check"] = reg2
    al, la = P.landing_grid()
    tpx = P.to_px(h, al, la)
    tl = t.lie_at(h, tpx)
    own = lies_yds(am, np.c_[la, -al])
    row["iou_own_frame"] = iou_table(tl, own)
    if T is not None:
        row["iou"] = iou_table(tl, lies_yds(am, T(tpx)))
    else:
        row["iou"] = row["iou_own_frame"]
    tc, tev, taim = best_club(course.HOLES, k, z)
    ac, aev, aaim = best_club({k: am}, k, z)
    row.update(club_traced=tc, club_auto=ac, same_club=tc == ac, ev_traced=tev, ev_auto=aev,
               aim_traced=taim, aim_auto=aaim)
    return row


def par3_hole(k, p, a):
    row = dict(hole=str(k), par=3, traced_center=p["center"], auto_center=(a.get("par3") or {}).get("center", a["length"]),
               tee_choice=a.get("tee_choice"))
    row["length_err"] = row["auto_center"] - p["center"]
    if a.get("par3"):
        row["haz_traced"], row["haz_auto"] = p["haz"], a["par3"]["haz"]
        row["front_back_traced"] = (p["front"], p["back"])
        row["front_back_auto"] = (a["par3"]["front"], a["par3"]["back"])
    return row


def passes(r):
    checks = {}
    if "tee_err" in r:
        checks["tee"] = r["tee_err"] <= BAR["tee"]
        u = r.get("green_unc") or {}
        checks["green"] = r["green_err"] <= max(BAR["green"], np.hypot(u.get("along", 0), u.get("lat", 0)))
    checks["length"] = abs(r["length_err"]) <= BAR["length"]
    for c in BAR["iou_classes"]:
        if c in r.get("iou", {}):
            checks[f"iou_{c}"] = r["iou"][c] > BAR["iou"]
    if "same_club" in r:
        checks["club"] = r["same_club"]
    return checks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--holes", help="evaluate this holes.json as built (default: oracle-tee builds)")
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--only", help="comma-separated traced keys")
    ap.add_argument("--vision", choices=["none", "loho"], default="none",
                    help="loho: add the imagery gap-fill from the model that did not see the hole")
    a = ap.parse_args()
    t0 = time.time()
    if a.holes:
        auto = from_model(a.holes)
    elif a.vision == "loho":
        auto = loho_builds()
    else:
        auto = oracle_builds()
    regs = json.load(open(REG)) if os.path.exists(REG) else {}
    regs = regs.get("holes", regs)
    n = 4000 if a.fast else t.N_SHOTS
    rng = np.random.default_rng(11)
    z = np.vstack([rng.standard_normal((2, n)), rng.random((2, n))])
    only = set(a.only.split(",")) if a.only else None
    rows, p3 = [], []
    for k, h in course.HOLES.items():
        if only and str(k) not in only:
            continue
        if k not in auto:
            rows.append(dict(hole=str(k), missing=True))
            continue
        r = tee_hole(k, h, auto[k], regs, z)
        r["checks"] = passes(r)
        rows.append(r)
        print(f"{str(k):>3} len {r['length_err']:+4d}  tee {r.get('tee_err', '-'):>5}  green {r.get('green_err', '-'):>5}  "
              f"[{r['registration']['method']}]  club {r['club_traced']:>6} / {r['club_auto']:<6}  "
              f"IoU {r['iou']}", flush=True)
    for k, p in course.PAR3.items():
        if (only and str(k) not in only) or k not in auto:
            continue
        r = par3_hole(k, p, auto[k])
        r["checks"] = dict(length=abs(r["length_err"]) <= BAR["length"])
        p3.append(r)
    ok = [r for r in rows if not r.get("missing")]
    summary = dict(
        mode=(f"{os.path.basename(a.holes)} as built" if a.holes else "oracle tees (traced lengths as the card)"
              + (", + LOHO imagery gap-fill" if a.vision == "loho" and not a.holes else ", OSM zones only")),
        n_tee_shots=len(ok), missing=[r["hole"] for r in rows if r.get("missing")],
        same_club=round(float(np.mean([r["same_club"] for r in ok])), 3) if ok else None,
        tee_within=round(float(np.mean([r["tee_err"] <= BAR["tee"] for r in ok if "tee_err" in r] or [np.nan])), 3),
        green_within=round(float(np.mean([r["checks"]["green"] for r in ok if "green" in r["checks"]] or [np.nan])), 3),
        length_within=round(float(np.mean([abs(r["length_err"]) <= BAR["length"] for r in ok])), 3) if ok else None,
        median_tee_err=float(np.median([r["tee_err"] for r in ok if "tee_err" in r])) if ok else None,
        median_green_err=float(np.median([r["green_err"] for r in ok if "green_err" in r])) if ok else None,
        mean_iou={c: round(float(np.mean([r["iou"][c] for r in ok if c in r["iou"]])), 3)
                  for c in CLASSES if any(c in r["iou"] for r in ok)},
        holes_passing=[r["hole"] for r in ok if all(r["checks"].values())],
        par3_length_within=[r["hole"] for r in p3 if r["checks"]["length"]],
        bar=BAR, seconds=round(time.time() - t0))
    summary["club_bar_met"] = bool(summary["same_club"] is not None and summary["same_club"] >= BAR["club"])
    out = dict(summary=summary, tee_shots=rows, par3=p3)
    tag = ("" if not a.holes else "_" + os.path.splitext(os.path.basename(a.holes))[0]) + \
        ("_loho" if a.vision == "loho" and not a.holes else "")
    with open(os.path.join(CDIR, f"acceptance{tag}.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    write_md(out, os.path.join(CDIR, f"acceptance{tag}.md"))
    print(json.dumps(summary, indent=1, default=float))


def write_md(out, path):
    s = out["summary"]
    L = [f"# Auto-course acceptance: Spirit Hollow ({s['mode']})", "",
         f"Same club (Driver / 2-wood / 4-wood) on **{s['same_club']:.0%}** of {s['n_tee_shots']} tee shots "
         f"(bar {BAR['club']:.0%}). Tee within {BAR['tee']:.0f} yds: {s['tee_within']:.0%}; green within "
         f"{BAR['green']:.0f} (or the traced green's own rounding spread): {s['green_within']:.0%}; length within {BAR['length']:.0f}: {s['length_within']:.0%}. "
         f"Median tee error {s['median_tee_err']} yds, green {s['median_green_err']} yds.", "",
         "Mean landing-zone IoU by class: " + ", ".join(f"{c} {v:.2f}" for c, v in s["mean_iou"].items()), "",
         f"Holes passing every check: {', '.join(s['holes_passing']) or 'none'}", "",
         "| hole | len err | tee err | green err (traced +/-) | registration | club traced / auto | IoU water | IoU ob | IoU trees | IoU fairway | failed |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in out["tee_shots"]:
        if r.get("missing"):
            L.append(f"| {r['hole']} | missing in the auto build |||||||||| ")
            continue
        reg = r["registration"]
        rs = reg["method"] + (f" (ecc {reg['ecc']})" if "ecc" in reg else (f" (dice {reg['dice']})" if "dice" in reg else ""))
        iou = r["iou"]
        fail = [k for k, v in r["checks"].items() if not v]
        u = r.get("green_unc")
        unc = f" (+/-{u['along']:.0f} along, +/-{u['lat']:.0f} lat)" if u else ""
        L.append(f"| {r['hole']} | {r['length_err']:+d} | {r.get('tee_err', '-')} | {r.get('green_err', '-')}{unc} | {rs} | "
                 f"{r['club_traced']} / {r['club_auto']} | {iou.get('water', '-')} | {iou.get('ob', '-')} | "
                 f"{iou.get('recovery', '-')} | {iou.get('fairway', '-')} | {', '.join(fail)} |")
    L += ["", "Par 3s (centre distance):", "", "| hole | traced | auto | err | hazards traced | hazards auto |", "|---|---|---|---|---|---|"]
    for r in out["par3"]:
        L.append(f"| {r['hole']} | {r['traced_center']} | {r['auto_center']} | {r['length_err']:+d} | "
                 f"{r.get('haz_traced', '-')} | {r.get('haz_auto', '-')} |")
    L += ["", "IoU is on the landing-zone grid (220-340 yds, +/-45) in the traced frame after registration; classes "
          "absent from both maps are omitted. Trees are traced at the trunks by hand and are unmapped in OSM, "
          "so `recovery` IoU is expected to be the weakest until the imagery gap-fill lands."]
    with open(path, "w") as fh:
        fh.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
