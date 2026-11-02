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


def write_summary(slug, pkg, FJ, S):
    st = next(iter(FJ.values()))["set"] if FJ else pkg.get("tee_set")
    ys, py = other_years(S)
    L = [f"# Mapper inputs: {pkg['course']['name']} ({pkg['course'].get('town')}, {pkg['course'].get('state')})", "",
         f"Base package: `{os.path.relpath(M.base_package_path(slug), M.ROOT)}` (built {pkg.get('built')}; "
         f"{(pkg.get('stages') or {}).get('mapper_base', '')}). Corridor set **{st}**. Sets: {', '.join(pkg.get('tee_sets') or {})}.",
         f"Photo NAIP {py}; other years: {', '.join(S[k].label for k in ys) or 'none'}; lidar canopy: "
         f"{'yes' if 'hag' in S else 'NO (trees can only be checked on the photo)'}; CIR: {'yes' if 'nir' in S else 'no'}.", "",
         "Auto layer sources: " + "; ".join(f"{k}: {str(v)[:110]}" for k, v in (pkg.get("stages") or {}).items()
                                           if k in ("vision", "ob", "segment", "tees")), "",
         "| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) |",
         "|---|---|---|---|---|---|"]
    for ref, fj in FJ.items():
        h = pkg["holes"][ref]
        t = (h.get("tees") or {}).get(st) or {}
        ar = landing_areas(fj, h)
        sets = ", ".join(f"{s} {tt.get('card_yards')}" for s, tt in (h.get("tees") or {}).items())
        L.append(f"| {ref} | {fj['par']} | {fj.get('yards')} | {t.get('method')}, {t.get('confidence')} | "
                 f"{sets} | "
                 f"{', '.join(f'{k} {v}' for k, v in sorted(ar.items())) or 'all rough'} |")
    L += ["", "Par 3s are not corridors (their tees are still checked in edits.json `tees`)."]
    open(M.mdir(slug, "inputs.md"), "w").write("\n".join(L) + "\n")


def template(slug, pkg, FJ):
    holes, tees = {}, {}
    for ref, h in sorted(pkg["holes"].items(), key=lambda kv: M.hole_key(kv[0])):
        if ref in FJ:
            holes[ref] = dict(reviewed=[], confidence="", note="", edits=[])
        tees[ref] = {s: dict(action="", confidence="", evidence="") for s in (h.get("tees") or {})}
    st = next(iter(FJ.values()))["set"] if FJ else pkg.get("tee_set")
    d = dict(schema="mapper_edits/1", slug=slug, corridor_set=st, mapper="", started="", minutes=None,
             doc="Fill in, save as edits.json, then: python3 course_data/mapper/write_layers.py " + slug +
                 ". See course_data/mapper/BRIEF.md for ops, shapes and rules.",
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


def run(slug, st=None, holes=None, rebuild="auto", course_map=True, fresh=False):
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
    S = C.sources(slug)
    dem = os.path.join(M.CD, "packages", slug, "imagery", "dem.tif")
    if os.path.exists(dem):
        S["dem"] = C.Raster(dem, label="3DEP DEM")
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
        n += tee_sheet(slug, ref, fj, h, S, boxes, out)
        M.log(f"  {ref}: {n} panels")
    write_summary(slug, pkg, FJ, S)
    if not os.path.exists(M.mdir(slug, "edits.json")):
        template(slug, pkg, FJ)
    M.log(f"-> {os.path.relpath(M.mdir(slug), M.ROOT)}/ (inputs.md, frames.json, edits.template.json, render/)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    ap.add_argument("--set", help="corridor tee set (default: the package's tee_set)")
    ap.add_argument("--holes")
    ap.add_argument("--rebuild", default="auto", help="auto | none | tees,trees (base package layers re-made offline)")
    ap.add_argument("--no-map", action="store_true")
    ap.add_argument("--fresh", action="store_true", help="re-make base/package.json even if it exists")
    a = ap.parse_args()
    run(a.slug, a.set, set(a.holes.split(",")) if a.holes else None, a.rebuild, not a.no_map, a.fresh)


if __name__ == "__main__":
    main()
