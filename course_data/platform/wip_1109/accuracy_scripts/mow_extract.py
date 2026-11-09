"""Corridor grids (1 yd) of raster features + truth native for the mowing-line work.
python3 mow_extract.py AUTO_V1 AUTO_V2 OUTDIR [courses]"""
import json, os, sys, pickle, warnings
warnings.filterwarnings("ignore")
import numpy as np
WT = "/home/user/my_golf_data_science"; CD = os.path.join(WT, "course_data")
for p in (os.path.join(CD, "platform"), os.path.join(CD, "mapper"), os.path.join(CD, "product")):
    sys.path.insert(0, p)
import error_budget as E
import common as M
import native_auto as NA
import native_confirm as NC
import shapely
from shapely.geometry import Polygon, shape, LineString
from shapely.ops import unary_union
from pyproj import Transformer

A1, A2, OUT = sys.argv[1:4]
cfgs = {c["slug"]: (c, "v1") for c in E.SETS["v1"]()}
cfgs.update({c["slug"]: (c, "v2") for c in E.SETS["v2"]()})
COURSES = sys.argv[4].split(",") if len(sys.argv) > 4 else ["gateway_national", "coldwater", "spirit_hollow", "sand_creek_station",
          "prairie_dunes", "buffalo_dunes", "mariah_hills", "annbriar", "eagle_bend", "ellis"]
XS = np.arange(-75, 75.01, 1.0); AS = np.arange(130, 400.01, 1.0)
os.makedirs(OUT, exist_ok=True)
for slug in COURSES:
    cfg, sv = cfgs[slug]
    S = cfg["tees"]
    pkg = M.rj(os.path.join(A1 if sv == "v1" else A2, slug, "package.json"))
    base = E.prepare(pkg, S)
    truth = E.truth_holes(cfg)
    st = M.tee_set_of(pkg, S) if any(k.lower() == S.lower() for k in pkg.get("tee_sets") or {}) else M.tee_set_of(pkg)
    frames = M.make_frames(pkg, st)
    rs = NA.course_rasters(slug)
    tr = Transformer.from_crs("EPSG:4326", rs["crs"], always_xy=True)
    P = E.PK()
    # cart paths
    osm = None
    for d in (os.path.join(CD, "packages", slug, "raw", "osm.geojson"), os.path.join(CD, "library", slug, "raw", "osm.geojson")):
        if os.path.exists(d): osm = json.load(open(d)); break
    paths = []
    if osm:
        for f in osm["features"]:
            p = f["properties"]
            if f["geometry"]["type"] == "LineString" and (p.get("golf") == "cartpath" or p.get("highway") in ("path", "service", "track", "footway")):
                paths.append(f["geometry"]["coordinates"])
    holes = {}
    for ref, fj in frames.items():
        h = pkg["holes"].get(ref); td = truth.get(ref)
        if h is None: continue
        XX, YY = np.meshgrid(XS, AS)
        xy = np.c_[XX.ravel(), YY.ravel()]
        ll = M.xy_to_ll(fj, xy)
        g = dict(shape=XX.shape)
        if td is not None and td.get("hand"):
            hb = base["holes"][ref]
            ent = E.tee_entry(hb, S, base.get("tee_set"))
            ast = E.auto_stack(base, hb, P._ll(ent.get("tee_ll")) or td["tee_ll"])
            tst = E.truth_stack(ast, td)
            et = E.effective(tst)
            foot = Polygon(td["hand"]["footprint"])
            g["foot"] = shapely.contains_xy(foot, ll[:, 0], ll[:, 1])
            for lie in ("native", "fairway", "recovery", "water", "sand"):
                g["t_" + lie] = shapely.contains_xy(et[lie], ll[:, 0], ll[:, 1]) if lie in et else np.zeros(len(xy), bool)
            g["truth_tee_xy"] = M.ll_to_xy(fj, [td["tee_ll"]])[0]
        mown = NC.mown_xy(fj, h)
        g["d"] = (shapely.distance(mown, shapely.points(xy)) if mown is not None and not mown.is_empty else np.abs(xy[:, 0]) - 15.0).astype(np.float32)
        g["has_fw"] = mown is not None and not mown.is_empty
        allmown, haz = NA._union(fj, pkg, NA.MOWN_LIES), NA._union(fj, pkg, NA.HAZ_LIES)
        g["othermown"] = shapely.contains_xy(allmown, xy[:, 0], xy[:, 1]) if allmown is not None else np.zeros(len(xy), bool)
        g["haz"] = shapely.contains_xy(haz, xy[:, 0], xy[:, 1]) if haz is not None else np.zeros(len(xy), bool)
        nat = NC.native_xy(fj, h)
        g["a_nat"] = shapely.contains_xy(nat, xy[:, 0], xy[:, 1]) if nat is not None and not nat.is_empty else np.zeros(len(xy), bool)
        Eg, Ng = tr.transform(ll[:, 0], ll[:, 1])
        g["hag"] = NA._sample(rs["hag"], Eg, Ng).astype(np.float32)
        if "chm" in rs: g["chm"] = NA._sample(rs["chm"], Eg, Ng).astype(np.float32)
        if "s2" in rs: g["s2"] = NA._sample(rs["s2"], Eg, Ng).astype(np.float32)
        for i, nd in enumerate(rs["naip"]):
            for k in NA.NAIP_KEYS:
                g[f"y{i}_{k}"] = NA._sample((nd[k], nd["t"]), Eg, Ng).astype(np.float32)
        if paths:
            ls = []
            for c in paths:
                q = M.ll_to_xy(fj, c)
                if q[:, 1].max() > 100 and q[:, 1].min() < 430 and np.abs(q[:, 0]).min() < 110:
                    ls.append(LineString(q))
            g["dpath"] = shapely.distance(unary_union(ls), shapely.points(xy)).astype(np.float32) if ls else np.full(len(xy), 999, np.float32)
        else:
            g["dpath"] = np.full(len(xy), 999, np.float32)
        holes[ref] = g
    pickle.dump(dict(slug=slug, holes=holes, years=[nd["year"] for nd in rs["naip"]], has_s2="s2" in rs), open(os.path.join(OUT, slug + ".pkl"), "wb"), protocol=4)
    print(slug, len(holes), flush=True)
