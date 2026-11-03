"""Back-tee evidence sheets for hand-checking a truth / auto tee (the far-cap check, platform/ERROR_BUDGET.md "Far cap").

    python3 course_data/tees/back_tee_sheets.py OUTDIR AUTO_V1 AUTO_V2 CAP_V1 CAP_V2 slug:hole ...
AUTO_* / CAP_* = rebuild_tees_trees.py --out dirs (v1 / v2 truth sets) for the two variants compared.
Writes OUTDIR/<slug>_<hole>.png (+ _zoom.png) and summary.json (positions in the truth tee's frame, yds).
Panels: package NAIP + marks, other NAIP years, DEM hillshade + lidar pads, lidar HAG.
Marks: T truth tee (white), A auto cap off (red), C auto cap 45 (yellow); cyan = OSM tee boxes,
magenta = lidar pads (tees/lidar_pads.detect_pads). Frame: truth tee -> green, along 0 = truth tee."""
import json, os, sys
import numpy as np
OUT, A1, A2, C1, C2 = sys.argv[1:6]
CD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (os.path.join(CD, "mapper"), os.path.join(CD, "truth"), os.path.join(CD, "tees"), os.path.join(CD, "platform"),
          os.path.join(CD, "product"), os.path.join(CD, "imagery")):
    sys.path.insert(0, p)
import common as M
import corridor as C
import render_inputs as RI
import error_budget as E
import lidar_pads as LP
import cv2

os.makedirs(OUT, exist_ok=True)
cfgs = {c["slug"]: (c, "v1") for c in E.SETS["v1"]()}
cfgs.update({c["slug"]: (c, "v2") for c in E.SETS["v2"]()})


def tee_of(pkg, ref, st):
    h = (pkg or {}).get("holes", {}).get(ref) or {}
    t = h.get("tees") or {}
    k = next((k for k in t if k.lower() == st.lower()), None)
    return (t[k].get("tee_ll"), t[k].get("method"), t[k].get("measured_yards")) if k else (None, None, None)


summary = {}
for arg in sys.argv[6:]:
    slug, ref = arg.split(":")[:2]
    cfg, sv = cfgs[slug]
    st = cfg["tees"]
    T = E.truth_holes(cfg)[ref]
    ad, cd = (A1, C1) if sv == "v1" else (A2, C2)
    pa = M.rj(os.path.join(ad, slug, "package.json"))
    pc = M.rj(os.path.join(cd, slug, "package.json"))
    tee = T["tee_ll"]
    green = T.get("green_ll") or pa["holes"][ref]["green_ll"]
    fr1 = C.corridor_frame(tee, green, 1.0, a0=-100, a1=600, lat=100)

    fj = dict(frame=fr1.to_json())
    pts = {"T": tee}
    a_ll, a_m, a_meas = tee_of(pa, ref, st)
    c_ll, c_m, c_meas = tee_of(pc, ref, st)
    if a_ll:
        pts["A"] = a_ll
    if c_ll:
        pts["C"] = c_ll
    P = {k: M.ll_to_xy(fj, [v])[0] for k, v in pts.items()}
    boxes = RI.osm_tees(slug)
    bx = []
    for r in boxes:
        q = M.ll_to_xy(fj, r)
        if q[:, 1].max() > -80 and q[:, 1].min() < 160 and np.abs(q[:, 0]).min() < 60:
            bx.append(q)
    S = M.sources(slug)
    dem = None
    for d in (os.path.join(CD, "packages", slug, "imagery", "dem.tif"), os.path.join(CD, "vision_any", slug, "raw", "dtm.tif")):
        if os.path.exists(d):
            dem = d
            break
    if "dem" not in S and dem:
        S["dem"] = C.Raster(dem, label="DTM")
    pads = []
    if dem:
        try:
            for p in LP.detect_pads(dem):
                q = M.ll_to_xy(fj, [[lo, la] for la, lo in p["coords"]])
                if q[:, 1].max() > -80 and q[:, 1].min() < 160 and np.abs(q[:, 0]).min() < 60:
                    pads.append(q)
        except Exception as e:  # noqa
            print("pads", e)
    al = [p[1] for p in P.values()] + [q[:, 1].min() for q in bx if np.abs(q[:, 0]).min() < 30]
    a0 = min(min(al), 0) - 35.0
    a1 = min(max(al) + 30.0, a0 + 170)
    lat = 45.0
    ppy = 4.0
    fr = C.corridor_frame(tee, green, ppy, a0=a0, a1=a1, lat=lat)

    def px(q):
        q = np.asarray(q, float).reshape(-1, 2)
        return np.c_[(q[:, 0] + lat) * ppy, (a1 - q[:, 1]) * ppy]

    def overlay(img, marks=True):
        for q in bx:
            cv2.polylines(img, [np.round(px(q) * 8).astype(np.int32)], True, (0, 255, 255), 1, shift=3)
        for q in pads:
            cv2.polylines(img, [np.round(px(q) * 8).astype(np.int32)], True, (255, 0, 255), 1, shift=3)
        img = C.grid(img, fr, a0=a0, a1=a1, lat=lat, step=10, label_every=20, font=0.33)
        if marks:
            for k, col in (("T", (255, 255, 255)), ("A", (255, 60, 60)), ("C", (255, 220, 0))):
                if k in P:
                    RI.mark(img, px([P[k]])[0], k, col)
        return img
    panels = [C.title(overlay(C._u8(S["photo"].warp(fr)[..., :3]) if "photo" in S else np.zeros((int((a1-a0)*ppy), int(2*lat*ppy), 3), np.uint8)),
                      f"{slug} {ref} {st} card {(T.get('yards') or {}).get(st)}: T truth A auto C cap45", 0.38)]
    ys = sorted([k for k in S if k.startswith("naip_")], reverse=True)[:2]
    for k in ys:
        panels.append(C.title(overlay(C._u8(S[k].warp(fr)[..., :3]), False), S[k].label, 0.38))
    if "dem" in S:
        panels.append(C.title(overlay(RI.hillshade(S["dem"], fr)), "DEM hillshade; magenta lidar pads", 0.38))
    if "hag" in S:
        panels.append(C.title(overlay(C.hag_rgb(C.hag_m(S, fr)), False), "lidar HAG", 0.38))
    C.save(os.path.join(OUT, f"{slug}_{ref}.png"), C.stack(panels, len(panels)))
    # zoom on the truth tee (+-22 yds lateral, -25..+30 along) at 8 px / yd
    za0, za1, zl, zp = -25.0, 30.0, 22.0, 8.0
    zf = C.corridor_frame(tee, green, zp, a0=za0, a1=za1, lat=zl)
    def zpx(q):
        q = np.asarray(q, float).reshape(-1, 2)
        return np.c_[(q[:, 0] + zl) * zp, (za1 - q[:, 1]) * zp]
    zps = []
    for k in (["photo"] + ys)[:3]:
        if k not in S:
            continue
        im = C._u8(S[k].warp(zf)[..., :3]).copy()
        for q in pads:
            cv2.polylines(im, [np.round(zpx(q) * 8).astype(np.int32)], True, (255, 0, 255), 1, shift=3)
        im = C.grid(im, zf, a0=za0, a1=za1, lat=zl, step=5, label_every=10, font=0.33)
        if k == "photo":
            RI.mark(im, zpx([P["T"]])[0], "T", (255, 255, 255))
        zps.append(C.title(im, f"zoom {S[k].label}", 0.38))
    if "dem" in S:
        zps.append(C.title(C.grid(RI.hillshade(S["dem"], zf), zf, a0=za0, a1=za1, lat=zl, step=5, label_every=10, font=0.33), "zoom DEM", 0.38))
    C.save(os.path.join(OUT, f"{slug}_{ref}_zoom.png"), C.stack(zps, len(zps)))
    summary[arg] = dict(truth_method=T.get("tee_method"), truth_along=0.0,
                        auto=(a_m, a_meas, [round(float(v), 1) for v in P.get("A", [np.nan, np.nan])]),
                        cap=(c_m, c_meas, [round(float(v), 1) for v in P.get("C", [np.nan, np.nan])]),
                        boxes=[[round(float(q[:, 0].mean()), 1), round(float(q[:, 1].min()), 1), round(float(q[:, 1].max()), 1)] for q in bx if np.abs(q[:, 0]).min() < 30],
                        pads=[[round(float(q[:, 0].mean()), 1), round(float(q[:, 1].min()), 1), round(float(q[:, 1].max()), 1)] for q in pads if np.abs(q[:, 0]).min() < 30])
    print(arg, json.dumps(summary[arg]))
json.dump(summary, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
