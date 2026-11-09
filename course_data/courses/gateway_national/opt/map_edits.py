"""Apply trace.py's edited hand bands to hand_zones_ll.json without re-deriving the auto layers (OSM / lidar) of the
other zones (a full `corridor.py build` re-reads the Nov 4 package OSM, which moved a few fairway vertices on 13, 15
and 18 since the Oct 17 build), then rebuild truth/package.json exactly as score_auto.truth_package builds it.

  python3 course_data/courses/gateway_national/opt/map_edits.py <old trace.py> [--holes 3,8,11,13,15,16,18]

For each hole: zones = new EXTRA (trace.py) + the stored zones between the old EXTRA and old LATE + new LATE.
"""
import argparse, importlib.util, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CD = os.path.join(ROOT, "course_data")
sys.path[:0] = [os.path.join(CD, "truth"), os.path.join(CD, "courses")]
import corridor as CO
import score_auto as SA

SLUG = "gateway_national"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("old_trace")
    ap.add_argument("--holes", default="3,8,11,13,15,16,18")
    a = ap.parse_args()
    old = load(a.old_trace, "trace_old")
    new = load(os.path.join(CD, "truth", SLUG, "trace.py"), "trace_new")
    FJ = CO.frames(SLUG)
    p = os.path.join(CD, "truth", SLUG, "hand_zones_ll.json")
    HZ = json.load(open(p))
    rnd = lambda r: [[round(float(x), 8), round(float(y), 8)] for x, y in r]      # noqa: E731
    for ref in a.holes.split(","):
        h = HZ["holes"][ref]
        ne, nl = len(old.EXTRA.get(ref, [])), len(old.LATE.get(ref, []))
        mid = h["zones"][ne:len(h["zones"]) - nl]
        conv = lambda zs: [dict(lie=z["lie"], poly_ll=rnd(CO.ring_ll(FJ[ref], z["xy"])),     # noqa: E731
                                **({"note": z["note"]} if z.get("note") else {})) for z in zs]
        h["zones"] = conv(new.EXTRA.get(ref, [])) + mid + conv(new.LATE.get(ref, []))
        print(ref, "zones", ne + len(mid) + nl, "->", len(h["zones"]))
    json.dump(HZ, open(p, "w"), indent=1)
    auto = json.load(open(os.path.join(CD, "courses", SLUG, "auto", "package.json")))
    pkg, _, _ = SA.truth_package(SLUG, auto, json.load(open(os.path.join(CD, "courses", SLUG, "config.json")))["tees"])
    json.dump(pkg, open(os.path.join(CD, "courses", SLUG, "truth", "package.json"), "w"))
    print("wrote hand_zones_ll.json and truth/package.json")


if __name__ == "__main__":
    main()
