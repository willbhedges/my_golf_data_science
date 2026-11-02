"""Apply a mapper agent's layers to a course package, layer by layer, recorded in provenance.

  python3 course_data/mapper/apply.py <slug> [--package P] [--agent-dir D] [--out OUT.json]
  from apply import apply; pkg2, report = apply(pkg, "course_data/mapper/<slug>")

Inputs in the agent folder (course_data/mapper/<slug>/, written by write_layers.py from the agent's edits.json):
  agent_zones.geojson  FeatureCollection, WGS84. One feature per edit, applied in file order to the hole it names:
                         op "erase": every zone of the listed lies (properties.lies, default [lie]) loses the polygon
                         op "add":   a new zone of properties.lie (src "agent:mapper")
                         op "grow":  the zones of properties.lie grown by properties.by yds (negative = shrunk),
                                     only inside the feature polygon (a tree edge that is a few yds short / long)
  agent_tees.json      {"holes": {ref: {set: {"action": "move" | "keep", "tee_ll": [lon, lat], ...}}}}: moved tees
                         get the new point (method "agent"), their aim / bearing (tee_line rule), measured length and
                         elevation profile are re-derived; "keep" records that the auto tee was checked.
Every package zone keeps its src; agent zones are src "agent:mapper", clipped zones get "agent_clipped": true.
After the edits the yard frame is re-derived (platform/package.reframe), then:
  package["agent_layers"]   {dir, files {name: sha1}, mapper, made, ops, tees_moved, tees_checked, holes, skipped}
  package["stages"]["agent_layers"]   one-line summary
  holes[ref]["provenance"]["agent"]   what changed on that hole
Lie precedence is the package's (platform/package.LIE_ORDER, later wins: native < recovery < ob < first_cut <
fairway < green < water < sand), so long grass drawn generously never covers a fairway.
"""
import argparse
import copy
import datetime as dt
import importlib.util
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
YD = 0.9144
SRC = "agent:mapper"
ZONE_FILE, TEE_FILE = "agent_zones.geojson", "agent_tees.json"
MIN_AREA_YD2 = 4.0
_PK = None


def platform_package():
    """platform/package.py under its own name (product/package.py is also 'package')."""
    global _PK
    if _PK is None:
        spec = importlib.util.spec_from_file_location("mapper_platform_package", os.path.join(CD, "platform", "package.py"))
        _PK = importlib.util.module_from_spec(spec)
        sys.modules["mapper_platform_package"] = _PK
        spec.loader.exec_module(_PK)
    return _PK


def _rj(p):
    with open(p) as fh:
        return json.load(fh)


def _sha1(p):
    import hashlib
    with open(p, "rb") as fh:
        return hashlib.sha1(fh.read()).hexdigest()[:16]


class Local:
    """Equirectangular yards around a point (error < 0.1 % over a hole): shapely works in yards here."""

    def __init__(self, lon0, lat0):
        self.lon0, self.lat0 = lon0, lat0
        self.kx = 111320.0 * math.cos(math.radians(lat0)) / YD
        self.ky = 110574.0 / YD

    def fwd(self, ring):
        r = np.asarray(ring, float)[:, :2]
        return np.c_[(r[:, 0] - self.lon0) * self.kx, (r[:, 1] - self.lat0) * self.ky]

    def inv(self, xy):
        xy = np.asarray(xy, float)
        return np.c_[xy[:, 0] / self.kx + self.lon0, xy[:, 1] / self.ky + self.lat0]


def _ring(poly):
    if isinstance(poly, dict):
        c = poly.get("coordinates") or []
        return (c[0] if c else []) if poly.get("type") == "Polygon" else (c[0][0] if c and c[0] else [])
    return poly or []


def _geom(L, ring):
    from shapely.geometry import Polygon
    g = Polygon(L.fwd(ring))
    return g if g.is_valid else g.buffer(0)


def _polys(g):
    if g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g] if g.area >= MIN_AREA_YD2 else []
    return [p for p in getattr(g, "geoms", []) if p.geom_type == "Polygon" and p.area >= MIN_AREA_YD2]


def _to_ring(L, p):
    ll = L.inv(np.asarray(p.exterior.coords)[:-1])
    return [[round(float(x), 7), round(float(y), 7)] for x, y in ll]


def _feature_geom(L, geometry):
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    if geometry["type"] == "Polygon":
        rings = [geometry["coordinates"]]
    elif geometry["type"] == "MultiPolygon":
        rings = geometry["coordinates"]
    else:
        raise ValueError(f"geometry {geometry['type']} (Polygon / MultiPolygon only)")
    gs = []
    for poly in rings:
        g = Polygon(L.fwd(poly[0]), [L.fwd(h) for h in poly[1:]])
        gs.append(g if g.is_valid else g.buffer(0))
    return unary_union(gs)


def zone_ops(h, feats):
    """Apply the hole's features (in order) to h["zones_ll"] in place -> list of op summaries."""
    from shapely.ops import unary_union
    t = h.get("tee_ll") or (h.get("green_ll"))
    if not t:
        z0 = next((z for z in h.get("zones_ll") or [] if len(_ring(z.get("poly"))) >= 3), None)
        if z0 is None and not feats:
            return []
        t = (_ring(z0["poly"])[0] if z0 else feats[0]["geometry"]["coordinates"][0][0])
    L = Local(float(t[0]), float(t[1]))
    zones = list(h.get("zones_ll") or [])
    done = []
    for f in feats:
        p = f.get("properties") or {}
        op, lie = p.get("op"), p.get("lie")
        g = _feature_geom(L, f["geometry"])
        extra = {k: p[k] for k in ("note", "confidence", "evidence", "edit") if p.get(k) not in (None, "")}
        if op == "add":
            n = 0
            for q in _polys(g):
                zones.append(dict(lie=lie, poly=_to_ring(L, q), src=SRC, **extra))
                n += 1
            done.append(dict(op="add", lie=lie, zones=n, yd2=round(g.area)))
        elif op == "erase":
            lies = set(p.get("lies") or [lie])
            out, cut = [], 0.0
            for z in zones:
                r = _ring(z.get("poly"))
                if z.get("lie") not in lies or len(r) < 3:
                    out.append(z)
                    continue
                zg = _geom(L, r)
                if not zg.intersects(g):
                    out.append(z)
                    continue
                rest = zg.difference(g)
                cut += zg.area - rest.area
                for q in _polys(rest):
                    out.append(dict(z, poly=_to_ring(L, q), agent_clipped=True))
            zones = out
            done.append(dict(op="erase", lie=",".join(sorted(lies)), yd2=round(cut)))
        elif op == "grow":
            by = float(p.get("by") or 0.0)
            mine = [_geom(L, _ring(z["poly"])) for z in zones if z.get("lie") == lie and len(_ring(z.get("poly"))) >= 3]
            if not mine or by == 0:
                done.append(dict(op="grow", lie=lie, by=by, yd2=0))
                continue
            u = unary_union(mine)
            if by > 0:
                new = u.buffer(by, join_style=2).intersection(g).difference(u)
                for q in _polys(new):
                    zones.append(dict(lie=lie, poly=_to_ring(L, q), src=SRC, **extra))
                done.append(dict(op="grow", lie=lie, by=by, yd2=round(new.area)))
            else:
                keep = u.buffer(by, join_style=2)
                lose = u.intersection(g).difference(keep)
                out = []
                for z in zones:
                    r = _ring(z.get("poly"))
                    if z.get("lie") != lie or len(r) < 3:
                        out.append(z)
                        continue
                    zg = _geom(L, r)
                    if not zg.intersects(lose):
                        out.append(z)
                        continue
                    for q in _polys(zg.difference(lose)):
                        out.append(dict(z, poly=_to_ring(L, q), agent_clipped=True))
                zones = out
                done.append(dict(op="grow", lie=lie, by=by, yd2=-round(lose.area)))
        else:
            raise ValueError(f"unknown op {op!r}")
    h["zones_ll"] = zones
    return done


def _measure(h, lon, lat):
    sys.path.insert(0, os.path.join(CD, "tees"))
    import place_tee as pt
    line = [(c[1], c[0]) for c in h["hole_line_ll"]]
    fr, lop = pt._hole_frame(line, (h["green_ll"][1], h["green_ll"][0]))
    return int(round(lop.dist_to_green(fr.fwd(lat, lon))))


def tee_ops(pkg, h, ref, entries, PK, sample):
    """Move / check the hole's tees -> list of summaries. entries {set: {action, tee_ll, ...}}."""
    done, moved = [], False
    for s, e in entries.items():
        t = (h.get("tees") or {}).get(s)
        if t is None:
            done.append(dict(set=s, action="skipped", why="set not on this package hole"))
            continue
        if e.get("action") != "move":
            t["agent_checked"] = dict(action="keep", confidence=e.get("confidence"), evidence=e.get("evidence"))
            done.append(dict(set=s, action="keep"))
            continue
        new = [round(float(e["tee_ll"][0]), 7), round(float(e["tee_ll"][1]), 7)]
        old = list(t["tee_ll"])
        d = math.hypot((new[0] - old[0]) * 111320.0 * math.cos(math.radians(old[1])), (new[1] - old[1]) * 110574.0) / YD
        t["tee_ll"] = new
        try:
            t["measured_yards"] = _measure(h, new[0], new[1])
        except Exception:                                          # noqa: BLE001
            pass
        t["agent_checked"] = dict(action="move", from_ll=old, moved_yd=round(d, 1), confidence=e.get("confidence"),
                                  evidence=e.get("evidence"), auto_method=t.get("method"))
        t["method"] = "agent"
        t["tee_source"] = "agent"
        t["tee_choice"] = f"tee stage: {s} agent (mapper moved the auto tee {d:.0f} yds)"
        done.append(dict(set=s, action="move", moved_yd=round(d, 1)))
        moved = True
    if moved:
        PK.apply_tee_line(h)
        if sample is not None:
            for s, t in h["tees"].items():
                if (t.get("agent_checked") or {}).get("action") != "move":
                    continue
                fr = PK._frame(t["tee_ll"], t["aim_ll"])
                gy = fr.ll_to_yds(np.array([h["green_ll"]]))[0]
                hh = dict(ref=ref, par=h["par"], length=t.get("card_yards") or t.get("measured_yards"),
                          measured_length=t.get("measured_yards"), green=[float(gy[0]), float(gy[1])],
                          bearing_deg=t["bearing_deg"])
                try:
                    t["elevation"] = PK.elevation_for_hole(hh, sample, fr.yds_to_ll)
                except Exception:                                  # noqa: BLE001
                    t["elevation"] = None
    return done


def _summary(ops, tees):
    parts = []
    for o in ops:
        if o["op"] == "grow":
            parts.append(f"grow {o['lie']} {o['by']:+g} yd ({o['yd2']:+d} yd2)")
        else:
            parts.append(f"{o['op']} {o['lie']} {o['yd2']} yd2")
    for t in tees:
        if t["action"] == "move":
            parts.append(f"tee {t['set']} moved {t['moved_yd']:.0f} yd")
    return "; ".join(parts) or "checked, no change"


def apply(pkg, agent_dir, pk=None, made_by=None):
    """(package with the agent's layers, report). The input is not modified. pk = platform/package module
    (default: loaded by path); its reframe() re-derives the yard frame."""
    PK = pk or platform_package()
    agent_dir = os.path.join(ROOT, agent_dir) if not os.path.isabs(agent_dir) else agent_dir
    zp, tp = os.path.join(agent_dir, ZONE_FILE), os.path.join(agent_dir, TEE_FILE)
    if not os.path.exists(zp) and not os.path.exists(tp):
        raise FileNotFoundError(f"no {ZONE_FILE} / {TEE_FILE} in {agent_dir}")
    fc = _rj(zp) if os.path.exists(zp) else dict(type="FeatureCollection", features=[], properties={})
    tj = _rj(tp) if os.path.exists(tp) else dict(holes={})
    p = copy.deepcopy(pkg)
    by_hole = {}
    for f in fc.get("features") or []:
        by_hole.setdefault(str((f.get("properties") or {}).get("hole")), []).append(f)
    skipped, holes = [], {}
    for ref, feats in by_hole.items():
        h = p["holes"].get(ref)
        if h is None:
            skipped.append(f"hole {ref}: not in the package ({len(feats)} zone edits)")
            continue
        holes.setdefault(ref, dict(ops=[], tees=[]))["ops"] = zone_ops(h, feats)
    sample = None
    if any(e.get("action") == "move" for es in (tj.get("holes") or {}).values() for e in es.values()) and p.get("elevation"):
        try:
            sample = PK.dem_sampler(os.path.join(ROOT, p["elevation"]["file"]))
        except Exception:                                          # noqa: BLE001
            sample = None
    for ref, es in (tj.get("holes") or {}).items():
        h = p["holes"].get(str(ref))
        if h is None:
            skipped.append(f"hole {ref}: not in the package (tee checks)")
            continue
        holes.setdefault(str(ref), dict(ops=[], tees=[]))["tees"] = tee_ops(p, h, str(ref), es, PK, sample)
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        out = PK.reframe(p)
    n_ops = sum(len(v["ops"]) for v in holes.values())
    moved = sum(1 for v in holes.values() for t in v["tees"] if t["action"] == "move")
    checked = sum(1 for v in holes.values() for t in v["tees"] if t["action"] in ("move", "keep"))
    meta = (fc.get("properties") or {})
    files = {n: _sha1(os.path.join(agent_dir, n)) for n in (ZONE_FILE, TEE_FILE) if os.path.exists(os.path.join(agent_dir, n))}
    rel = os.path.relpath(agent_dir, ROOT)
    rep = dict(dir=rel, files=files, mapper=meta.get("mapper") or tj.get("mapper"), edits_made=meta.get("made"),
               base_package=meta.get("base_package"), corridor_set=meta.get("corridor_set"),
               applied=made_by or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               ops=n_ops, tees_moved=moved, tees_checked=checked,
               holes={k: dict(v, summary=_summary(v["ops"], v["tees"])) for k, v in sorted(holes.items())},
               skipped=skipped)
    for ref, v in rep["holes"].items():
        if ref in out["holes"]:
            out["holes"][ref].setdefault("provenance", {})["agent"] = v["summary"]
    out["agent_layers"] = rep
    out.setdefault("stages", {})["agent_layers"] = (
        f"ok: {rel} ({n_ops} zone edits on {sum(1 for v in holes.values() if v['ops'])} holes, {moved} tee(s) moved, "
        f"{checked} checked" + (f"; skipped: {'; '.join(skipped)}" if skipped else "") + ")")
    return out, rep


def main():
    sys.path.insert(0, HERE)
    import common as M
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    ap.add_argument("--package", help="package.json to apply to (default: the mapper's base package)")
    ap.add_argument("--agent-dir", help="default course_data/mapper/<slug>")
    ap.add_argument("--out", help="default course_data/mapper/<slug>/out/package.json")
    a = ap.parse_args()
    pkg = M.rj(a.package) if a.package else M.load_base(a.slug)
    out, rep = apply(pkg, a.agent_dir or M.mdir(a.slug))
    dst = a.out or M.mdir(a.slug, "out", "package.json")
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    with open(dst, "w") as fh:
        json.dump(out, fh)
    print(out["stages"]["agent_layers"])
    for ref, v in rep["holes"].items():
        print(f"  {ref}: {v['summary']}")
    print("->", os.path.relpath(dst, ROOT))


if __name__ == "__main__":
    main()
