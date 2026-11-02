"""Render everything a mapper agent looks at, from a course package (no truth file is read).

  python3 course_data/mapper/render_inputs.py <slug> [--set Blue] [--holes 4,7] [--rebuild auto|none|tees,trees]

Writes course_data/mapper/<slug>/:
  base/package.json     the package the agent reviews (the committed package; --rebuild auto also re-makes the
                        vision_any/2 lidar trees when the build had none but vision_any/<slug>/raw exists, and the
                        tees with the current tee rule: what a build with the lidar stack gives, as
                        platform/rebuild_tees_trees.py). Committed with the edits: it is the "auto" side of eval_mapper.
  frames.json           every par-4/5 tee shot's corridor frame (corridor set tee -> package aim point); all edits
                        are (x, along) yds in these frames
  edits.template.json   the edits.json skeleton: every corridor hole, every tee set, nothing reviewed yet
  inputs.md             per hole: card, auto tees (method / confidence), auto layers in the landing zone
  render/ (not committed; re-made by this script)
    map/map.jpg                 whole course: NAIP + OSM greens (G), tees (T), hole lines, package holes (P<n>)
    hNN_overview.png            tee -> green, every set's tee, the corridor box
    hNN_corridor_a.png          [photo + AUTO layers (filled, numbered)] [bare photo] [second NAIP year]
    hNN_corridor_b.png          [lidar canopy + AUTO tree outlines] [CIR + lidar edge] [third NAIP year | DEM hillshade]
    hNN_tees.png                tee complex: [photo + every set's auto tee + OSM tee boxes] [DEM hillshade] [2nd year]
    hNN_corridor_s2.png         Sentinel-2 native suggestion: [S2 native P (10 m) over the photo, 0.5 contour, AUTO
                                fairway outline] [photo + "S2 suggested native" candidates, ids] [same on 2nd year]
S2 (course_data/mapper/s2_suggest.py, vision_any/s2/native_model.py): LOCO-safe native P (a course in the S2
training set gets the fold model trained without it, a new course the full model); its P >= 0.5 clusters outside
the package fairway / first cut / green / water / sand / trees are written per hole and side into
edits.template.json `s2_suggested` with an empty `decision` the agent fills in (accept / reject / replace).
Grids: 10-yd lines, labels every 20 yds; x = yds right of the tee line (magenta 0 line), along = yds from the tee
(yellow every 50). Zone colours: fairway green, first cut light green, trees dark green, long grass gold, water blue,
sand cream, OB red.
"""
import argparse
import contextlib
import io
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as M  # noqa: E402
import s2_suggest as S2S  # noqa: E402
import corridor as C  # noqa: E402  (course_data/truth/corridor.py: rasters, grid, drawing; nothing of a truth set)

PPY = 3.0
DRAW_LIES = ("fairway", "first_cut", "recovery", "native", "water", "sand", "ob")


# ----------------------------------------------------------------------------- base package
def prepare(slug, rebuild="auto", fresh=False):
    """The base package: kept as it is once made (frames.json and every edit are relative to its tees), unless
    fresh=True (then re-check the edits: write_layers.py warns when the base changed after the renders)."""
    bp = M.mdir(slug, "base", "package.json")
    if os.path.exists(bp) and not fresh:
        pkg = M.rj(bp)
        M.log(f"[{slug}] base package kept: {os.path.relpath(bp, M.ROOT)} ({pkg['stages'].get('mapper_base')}; --fresh remakes it)")
        return pkg
    pkg = M.rj(M.committed_package_path(slug))
    if pkg is None:
        raise SystemExit(f"{slug}: no course_data/packages/{slug}/package.json; push course_data/requests/package_{slug}.json")
    notes = []
    raw = os.path.join(M.CD, "vision_any", slug, "raw")
    vis = str((pkg.get("stages") or {}).get("vision", ""))
    want = set() if rebuild == "none" else ({"tees", "trees"} if rebuild == "auto" else set(rebuild.split(",")))
    if rebuild == "auto" and not (vis.startswith("missing") and os.path.isdir(raw)):
        want.discard("trees")
    if want:
        sys.path.insert(0, os.path.join(M.CD, "platform"))
        import importlib.util
        spec = importlib.util.spec_from_file_location("mapper_rtt", os.path.join(M.CD, "platform", "rebuild_tees_trees.py"))
        RT = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(RT)
        if "tees" in want:
            with contextlib.redirect_stdout(io.StringIO()):
                pkg, n = RT.retee(pkg, os.path.dirname(M.committed_package_path(slug)), slug)
            notes.append(n)
        if "trees" in want:
            k = M.rj(os.path.join(M.CD, "vision_any", "model_v2", "model.json"))["settings"]["trees"]["k_m"]
            pkg, n = RT.retree(pkg, slug, k)
            notes.append(n)
    pkg.setdefault("stages", {})["mapper_base"] = ("committed package" + (": " + "; ".join(notes) if notes else ""))
    M.wj(M.mdir(slug, "base", "package.json"), pkg, indent=None)
    M.log(f"[{slug}] base package: {pkg['stages']['mapper_base']}")
    return pkg


# ----------------------------------------------------------------------------- drawing helpers
def zones_for_draw(fj, h):
    return [dict(lie=z["lie"], xy=z["xy"]) for z in M.auto_zones_xy(fj, h, DRAW_LIES)]


def frame(fj, ppy, a0, a1, lat):
    f = fj["frame"]
    return C.corridor_frame(f["tee_ll"], f["aim_ll"], ppy, a0=a0, a1=a1, lat=lat)


def gridw(img, fr, a0, a1, lat, step=10, every=20, font=0.33):
    return C.grid(img, fr, a0=a0, a1=a1, lat=lat, step=step, label_every=every, font=font)


def draw(img, fr, zones, a1, lat, fill=True, labels=False, width=1):
    return C.draw_zones(img, fr, zones, fill=fill, width=width, labels=labels, a1=a1, lat=lat)


def hillshade(S_dem, fr):
    """DEM (m) in the frame -> grey hillshade (sun from the NW), tee pads and bunkers stand out."""
    z = S_dem.warp(fr)[..., 0].astype(float)
    if not np.isfinite(z).any():
        return np.zeros(z.shape + (3,), np.uint8)
    z = np.where(np.isfinite(z), z, np.nanmedian(z))
    px_m = M.YD / fr.ppy
    gy, gx = np.gradient(z, px_m)
    slope = np.arctan(np.hypot(gx, gy) * 2.0)
    aspect = np.arctan2(-gx, gy)
    az, alt = np.radians(315.0), np.radians(45.0)
    hs = np.sin(alt) * np.cos(slope) + np.cos(alt) * np.sin(slope) * np.cos(az - aspect)
    g = np.clip(255 * hs, 0, 255).astype(np.uint8)
    return np.dstack([g, g, g])


def other_years(S):
    py = None
    try:
        py = str(json.load(open(os.path.join(os.path.dirname(S["photo"].path), "georef.json")))["imagery"]["year"])
    except Exception:                                              # noqa: BLE001
        pass
    ks = sorted([k for k in S if k.startswith("naip_") and k[5:9] != py], reverse=True)
    return ks, py


def mark(img, p, text, col):
    import cv2
    p = (int(round(p[0])), int(round(p[1])))
    cv2.circle(img, p, 5, (0, 0, 0), -1)
    cv2.circle(img, p, 4, col, -1)
    cv2.putText(img, text, (p[0] + 6, p[1] + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 0), 3)
    cv2.putText(img, text, (p[0] + 6, p[1] + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.42, col, 1)


SET_COL = [(255, 60, 60), (60, 160, 255), (255, 255, 255), (255, 210, 0), (255, 120, 255), (120, 255, 120)]


# ----------------------------------------------------------------------------- per-hole sheets
def corridor_sheets(slug, ref, fj, h, S, out):
    a0, a1, lat = M.WIN["a0"], M.WIN["a1"], M.WIN["lat"]
    fr = frame(fj, PPY, a0, a1, lat)
    zones = zones_for_draw(fj, h)
    rgb = S["photo"].warp(fr)
    photo = C._u8(rgb)
    ys, py = other_years(S)
    head = f"{slug} {ref} par {fj['par']} {fj['set']} {fj.get('yards')} yds"
    P = [C.title(gridw(draw(photo, fr, zones, a1, lat, labels=True), fr, a0, a1, lat), f"{head}: AUTO layers on NAIP {py}", 0.4),
         C.title(gridw(photo, fr, a0, a1, lat), f"bare photo NAIP {py} (0.3-0.6 m)", 0.4)]
    if ys:
        P.append(C.title(gridw(C._u8(S[ys[0]].warp(fr)[..., :3]), fr, a0, a1, lat), f"2nd year: {S[ys[0]].label}", 0.4))
    C.save(os.path.join(out, f"h{int(ref):02d}_corridor_a.png"), C.stack(P, len(P)))
    Q = []
    tz = [z for z in zones if z["lie"] == "recovery"]
    if "hag" in S:
        Q.append(C.title(gridw(draw(C.hag_rgb(C.hag_m(S, fr)), fr, tz, a1, lat, fill=False), fr, a0, a1, lat),
                         "lidar HAG (grey<0.5 yel<2.5 grn<8 dk>8 m) + AUTO trees", 0.4))
    if "nir" in S:
        Q.append(C.title(gridw(C.lidar_contour(C.cir(S, fr, rgb), S, fr), fr, a0, a1, lat),
                         "CIR (NIR,R,G) + lidar canopy edge 2.5 m (cyan)", 0.4))
    if len(ys) > 1:
        Q.append(C.title(gridw(C._u8(S[ys[1]].warp(fr)[..., :3]), fr, a0, a1, lat), f"3rd year: {S[ys[1]].label}", 0.4))
    elif "dem" in S:
        Q.append(C.title(gridw(hillshade(S["dem"], fr), fr, a0, a1, lat), "DEM hillshade (sun NW)", 0.4))
    if Q:
        C.save(os.path.join(out, f"h{int(ref):02d}_corridor_b.png"), C.stack(Q, len(Q)))
    return len(P) + len(Q)


S2_COL = (255, 120, 0)


def p_heat(photo, P, thr=S2S.THR):
    """Blend the S2 native P over the photo: < 0.3 clear, 0.3-thr blue -> cyan, >= thr yellow -> red; nan grey."""
    import cv2
    out = photo.astype(np.float32).copy()
    p = np.nan_to_num(P, nan=-1.0)
    col = np.zeros_like(out)
    lo = (p >= 0.3) & (p < thr)
    hi = p >= thr
    t = np.clip((p - thr) / (1 - thr), 0, 1)
    col[lo] = (40, 140, 255)
    col[hi] = np.c_[np.full(hi.sum(), 255.0), 230 * (1 - t[hi]), np.zeros(hi.sum())]
    a = np.where(hi, 0.45, np.where(lo, 0.3, 0.0))[..., None]
    out = out * (1 - a) + col * a
    out[p < -0.5] = out[p < -0.5] * 0.5 + 60
    out = out.astype(np.uint8)
    m = (p >= thr).astype(np.uint8)
    cs, _ = cv2.findContours(m, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(out, cs, -1, (0, 0, 0), 3)
    cv2.drawContours(out, cs, -1, (255, 40, 40), 1)
    return out


def draw_cands(img, fr, cands, a1, lat):
    import cv2
    out = img.copy()
    for c in cands:
        q = C.yd_to_px(fr, c["shape"]["poly"], a1, lat)
        pi = np.round(q * 8).astype(np.int32)
        cv2.polylines(out, [pi], True, (0, 0, 0), 4, shift=3)
        cv2.polylines(out, [pi], True, S2_COL, 2, shift=3)
        m = q.mean(0).astype(int)
        t = c["id"].split("-")[-1]
        cv2.putText(out, t, (int(m[0]) - 8, int(m[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)
        cv2.putText(out, t, (int(m[0]) - 8, int(m[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, S2_COL, 1)
    return out


def s2_sheet(slug, ref, fj, h, S, pg, cands, out):
    a0, a1, lat = M.WIN["a0"], M.WIN["a1"], M.WIN["lat"]
    fr = frame(fj, PPY, a0, a1, lat)
    photo = C._u8(S["photo"].warp(fr))
    P = S2S.p_frame(pg, fj, a0, a1, lat, PPY)
    fw = [z for z in zones_for_draw(fj, h) if z["lie"] in ("fairway", "first_cut", "green")]
    ys, py = other_years(S)
    src = "LOCO fold" if pg["source"] == "loco" else "full model"
    P1 = [C.title(gridw(draw(p_heat(photo, P), fr, fw, a1, lat, fill=False), fr, a0, a1, lat),
                  f"{ref}: S2 native P ({src}) blue .3-.5, yel-red >.5", 0.4),
          C.title(gridw(draw_cands(photo, fr, cands, a1, lat), fr, a0, a1, lat),
                  f"S2 suggested native (orange, ids L1/R1..) on NAIP {py}", 0.4)]
    if ys:
        P1.append(C.title(gridw(draw_cands(C._u8(S[ys[0]].warp(fr)[..., :3]), fr, cands, a1, lat), fr, a0, a1, lat),
                          f"same on {S[ys[0]].label}: accept only if unmown in both years", 0.4))
    C.save(os.path.join(out, f"h{int(ref):02d}_corridor_s2.png"), C.stack(P1, len(P1)))
    return len(P1)


def s2_load(slug):
    """The course's S2 native P grid (LOCO-safe) or None, never fatal: the mapper works without it."""
    try:
        pg = S2S.load(slug)
    except Exception as e:                                         # noqa: BLE001
        M.log(f"  ! S2 native P not available ({type(e).__name__}: {str(e)[:160]})")
        return None
    if pg is None:
        M.log(f"  ! no S2 stack (course_data/vision_any/s2/{slug}/s2_stack.npz): no S2 suggestions; coordinator: "
              f"push course_data/requests/s2_stack_<name>.json")
    else:
        M.log(f"  S2 native P: {pg['source']} ({pg['note']})")
    return pg


def osm_tees(slug):
    p = os.path.join(M.CD, "packages", slug, "raw", "osm.geojson")
    fc = M.rj(p) or {}
    out = []
    for f in fc.get("features", []):
        if (f.get("properties") or {}).get("golf") != "tee":
            continue
        g = f["geometry"]
        rings = [g["coordinates"][0]] if g["type"] == "Polygon" else [q[0] for q in g["coordinates"]] if g["type"] == "MultiPolygon" else []
        out += [np.asarray(r, float)[:, :2] for r in rings]
    return out


def tee_sheet(slug, ref, fj, h, S, boxes, out):
    import cv2
    pts = {}
    for s, t in (h.get("tees") or {}).items():
        if t.get("tee_ll"):
            pts[s] = M.ll_to_xy(fj, [t["tee_ll"]])[0]
    if not pts:
        return 0
    al = [p[1] for p in pts.values()]
    xs = [abs(p[0]) for p in pts.values()]
    a0, a1 = min(al) - 45.0, max(al) + 30.0
    lat = float(np.ceil((max(xs) + 35.0) / 10.0) * 10.0)
    ppy = 4.0 if (a1 - a0) < 200 else 3.0
    fr = frame(fj, ppy, a0, a1, lat)
    photo = C._u8(S["photo"].warp(fr))
    img = photo.copy()

    def px(xy):
        xy = np.asarray(xy, float).reshape(-1, 2)
        return np.c_[(xy[:, 0] + lat) * ppy, (a1 - xy[:, 1]) * ppy]
    for r in boxes:
        q = M.ll_to_xy(fj, r)
        if q[:, 1].max() < a0 or q[:, 1].min() > a1 or np.abs(q[:, 0]).min() > lat:
            continue
        cv2.polylines(img, [np.round(px(q) * 8).astype(np.int32)], True, (0, 255, 255), 1, shift=3)
    img = gridw(img, fr, a0, a1, lat, step=10, every=20)
    for i, (s, p) in enumerate(sorted(pts.items(), key=lambda kv: -kv[1][1] * 0 + kv[1][1])):
        t = h["tees"][s]
        mark(img, px([p])[0], f"{s} {t.get('card_yards') or '?'} ({t.get('method')})", SET_COL[i % len(SET_COL)])
    P = [C.title(img, f"{slug} {ref}: auto tee per set (card yds, method) + OSM tee boxes (cyan)", 0.4)]
    if "dem" in S:
        P.append(C.title(gridw(hillshade(S["dem"], fr), fr, a0, a1, lat), "DEM hillshade: raised flat pads = tee boxes", 0.4))
    ys, _ = other_years(S)
    if ys:
        P.append(C.title(gridw(C._u8(S[ys[0]].warp(fr)[..., :3]), fr, a0, a1, lat), f"{S[ys[0]].label}", 0.4))
    C.save(os.path.join(out, f"h{int(ref):02d}_tees.png"), C.stack(P, len(P)))
    return len(P)


# ----------------------------------------------------------------------------- summary files
def landing_areas(fj, h):
    """sq yds per lie of the AUTO map in the landing zone (180-330 yds, +/-50), visible lie (later wins)."""
    from shapely.geometry import box
    from shapely.ops import unary_union
    order = ["native", "recovery", "ob", "first_cut", "fairway", "green", "water", "sand"]
    zs = sorted(M.auto_zones_xy(fj, h), key=lambda z: order.index(z["lie"]) if z["lie"] in order else -1)
    lz = box(-50, 180, 50, 330)
    seen, out = None, {}
    for z in reversed(zs):
        g = M._poly(z["xy"]).intersection(lz)
        if seen is not None:
            g = g.difference(seen)
        if g.is_empty:
            continue
        seen = g if seen is None else unary_union([seen, g])
        out[z["lie"]] = out.get(z["lie"], 0) + g.area
    return {k: int(round(v)) for k, v in out.items() if v >= 1}


def write_summary(slug, pkg, FJ, S, pg=None, CANDS=None):
    st = next(iter(FJ.values()))["set"] if FJ else pkg.get("tee_set")
    ys, py = other_years(S)
    L = [f"# Mapper inputs: {pkg['course']['name']} ({pkg['course'].get('town')}, {pkg['course'].get('state')})", "",
         f"Base package: `{os.path.relpath(M.base_package_path(slug), M.ROOT)}` (built {pkg.get('built')}; "
         f"{(pkg.get('stages') or {}).get('mapper_base', '')}). Corridor set **{st}**. Sets: {', '.join(pkg.get('tee_sets') or {})}.",
         f"Photo NAIP {py}; other years: {', '.join(S[k].label for k in ys) or 'none'}; lidar canopy: "
         f"{'yes' if 'hag' in S else 'NO (trees can only be checked on the photo)'}; CIR: {'yes' if 'nir' in S else 'no'}.", "",
         "Auto layer sources: " + "; ".join(f"{k}: {str(v)[:110]}" for k, v in (pkg.get("stages") or {}).items()
                                           if k in ("vision", "ob", "segment", "tees")), "",
         (f"S2 native suggestion: **{pg['source']}** ({pg['note']}); P >= {S2S.THR:g} clusters outside the package "
          f"fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json "
          f"`s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions')."
          if pg is not None else "S2 native suggestion: **none** (no S2 stack for this course): long grass from the photos only."), "",
         "| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |",
         "|---|---|---|---|---|---|---|"]
    for ref, fj in FJ.items():
        h = pkg["holes"][ref]
        t = (h.get("tees") or {}).get(st) or {}
        ar = landing_areas(fj, h)
        sets = ", ".join(f"{s} {tt.get('card_yards')}" for s, tt in (h.get("tees") or {}).items())
        L.append(f"| {ref} | {fj['par']} | {fj.get('yards')} | {t.get('method')}, {t.get('confidence')} | "
                 f"{sets} | "
                 f"{', '.join(f'{k} {v}' for k, v in sorted(ar.items())) or 'all rough'} | "
                 f"{s2_cell(CANDS, ref, pg)} |")
    L += ["", "Par 3s are not corridors (their tees are still checked in edits.json `tees`)."]
    open(M.mdir(slug, "inputs.md"), "w").write("\n".join(L) + "\n")


def s2_cell(CANDS, ref, pg):
    if pg is None:
        return "no S2"
    cs = (CANDS or {}).get(ref) or []
    return ", ".join(f"{c['id'].split('-')[-1]}: {c['area_yd2']}, {c['gap_yd']}" for c in cs) or "none"


def template(slug, pkg, FJ, CANDS=None):
    holes, tees = {}, {}
    for ref, h in sorted(pkg["holes"].items(), key=lambda kv: M.hole_key(kv[0])):
        if ref in FJ:
            holes[ref] = dict(reviewed=[], confidence="", note="", long_grass={"L": "", "R": ""}, edits=[])
            if CANDS is not None:
                holes[ref]["s2_suggested"] = S2S.template_entry(CANDS.get(ref) or [])
        tees[ref] = {s: dict(action="", confidence="", evidence="") for s in (h.get("tees") or {})}
    st = next(iter(FJ.values()))["set"] if FJ else pkg.get("tee_set")
    d = dict(schema="mapper_edits/1", slug=slug, corridor_set=st, mapper="", started="", minutes=None,
             doc="Fill in, save as edits.json, then: python3 course_data/mapper/write_layers.py " + slug +
                 ". See course_data/mapper/BRIEF.md for ops, shapes and rules. long_grass: a verdict per side on "
                 "every hole, 'native: <edits>' or 'none: <what both years show>' (S2 silence is not a verdict)." +
                 (" s2_suggested: Sentinel-2 native candidates (hint, not a layer): per hole and side set every "
                  "candidate's decision to accept (its shape becomes add native with your confidence + evidence; the "
                  "10-yd keep-out applies), reject (evidence = why) or replace (you drew your own native edit in "
                  "`edits`, e.g. the traced edge); undecided ones are listed in review.md." if CANDS is not None else ""),
             holes=holes, tees=tees)
    M.wj(M.mdir(slug, "edits.template.json"), d)


# ----------------------------------------------------------------------------- main
def tee_frames(pkg, st, FJ):
    """Every hole's tee-sheet frame: the corridor frame (par 4 / 5) or the corridor-set tee -> green (par 3)."""
    out = {}
    for ref, h in sorted(pkg["holes"].items(), key=lambda kv: M.hole_key(kv[0])):
        if ref in FJ:
            out[ref] = dict(ref=ref, par=FJ[ref]["par"], set=st, frame=FJ[ref]["frame"])
            continue
        t = (h.get("tees") or {}).get(st) or {}
        tee = t.get("tee_ll") or h.get("tee_ll")
        if tee and h.get("green_ll"):
            out[ref] = dict(ref=ref, par=h.get("par"), set=st, frame=M.corridor_frame(tee, h["green_ll"], 1.0).to_json())
    return out


def run(slug, st=None, holes=None, rebuild="auto", course_map=True, fresh=False, s2=True):
    pkg = prepare(slug, rebuild, fresh)
    st = M.tee_set_of(pkg, st)
    FJ = M.make_frames(pkg, st)
    TF = tee_frames(pkg, st, FJ)
    M.wj(M.mdir(slug, "frames.json"), dict(
        slug=slug, set=st, window=M.WIN, base_package=os.path.relpath(M.mdir(slug, "base", "package.json"), M.ROOT),
        base_built=pkg.get("built"), doc="(x, along) yds: x right of the tee line, along from the corridor-set tee "
                                         "towards the package aim point (render.Frame UTM, 1 px = 1 yd); tee_frames: "
                                         "the frame of every hole's tee sheet (par 3s: tee -> green)", holes=FJ,
        tee_frames=TF))
    S = M.sources(slug)
    if "photo" not in S:
        raise SystemExit(f"{slug}: no course_data/packages/{slug}/imagery/naip_rgb.tif (the package request must "
                         f"commit imagery)")
    out = M.mdir(slug, "render")
    os.makedirs(out, exist_ok=True)
    M.log(f"[{slug}] set {st}; sources: " + ", ".join(f"{k}={v.label}" for k, v in S.items()))
    if course_map:
        r = subprocess.run([sys.executable, os.path.join(M.CD, "truth", "course_map.py"), "--slug", slug,
                            "--out", os.path.join(out, "map")], capture_output=True, text=True)
        M.log("  course map: " + (r.stdout.strip()[-200:] or r.stderr.strip()[-300:]))
    boxes = osm_tees(slug)
    pg = s2_load(slug) if s2 else None
    CANDS = {ref: S2S.candidates(pg, fj, pkg["holes"][ref], ref) for ref, fj in FJ.items()} if pg is not None else None
    for ref, h in sorted(pkg["holes"].items(), key=lambda kv: M.hole_key(kv[0])):
        if holes and ref not in holes:
            continue
        fj = FJ.get(ref) or TF.get(ref)
        if fj is None:
            continue
        n = 0
        if ref in FJ:
            C.save(os.path.join(out, f"h{int(ref):02d}_overview.png"), C.overview(S, fj, h))
            n += corridor_sheets(slug, ref, fj, h, S, out)
            if pg is not None:
                n += s2_sheet(slug, ref, fj, h, S, pg, CANDS[ref], out)
        n += tee_sheet(slug, ref, fj, h, S, boxes, out)
        M.log(f"  {ref}: {n} panels")
    write_summary(slug, pkg, FJ, S, pg, CANDS)
    if not os.path.exists(M.mdir(slug, "edits.json")):
        template(slug, pkg, FJ, CANDS)
    M.log(f"-> {os.path.relpath(M.mdir(slug), M.ROOT)}/ (inputs.md, frames.json, edits.template.json, render/)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    ap.add_argument("--set", help="corridor tee set (default: the package's tee_set)")
    ap.add_argument("--holes")
    ap.add_argument("--rebuild", default="auto", help="auto | none | tees,trees (base package layers re-made offline)")
    ap.add_argument("--no-map", action="store_true")
    ap.add_argument("--fresh", action="store_true", help="re-make base/package.json even if it exists")
    ap.add_argument("--no-s2", action="store_true", help="no Sentinel-2 native suggestions")
    a = ap.parse_args()
    run(a.slug, a.set, set(a.holes.split(",")) if a.holes else None, a.rebuild, not a.no_map, a.fresh, not a.no_s2)


if __name__ == "__main__":
    main()
