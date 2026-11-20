"""smoke_scenes.py REF_DIR RUN_DIR: rebuilt bench scenes (RUN_DIR/big/scenes) vs the committed ones (REF_DIR/big/scenes)
per course: hole greens and tee complexes, and the share of the reference's hole greens with a rebuilt hole green within
10 m (and the other way). Informational."""
import gzip, json, math, os, sys


def load(d, s):
    return json.load(gzip.open(os.path.join(d, "big", "scenes", s + ".json.gz"), "rt"))


def hole(sc):
    return [g["centroid"] for g in sc.get("greens") or [] if g.get("kind") == "hole"]


def near(a, bs, m=10.0):
    k = math.cos(math.radians(a[1]))
    return any(math.hypot((a[0] - b[0]) * k, a[1] - b[1]) * 111320.0 <= m for b in bs)


ref, run = sys.argv[1:3]
for f in sorted(os.listdir(os.path.join(run, "big", "scenes"))):
    s = f[:-len(".json.gz")]
    a, b = load(ref, s), load(run, s)
    ga, gb = hole(a), hole(b)
    print("%-30s years ref %s run %s | hole greens %d / %d, matched %d / %d | tee complexes %d / %d" % (
        s, (a.get("route_bench") or {}).get("years"), (b.get("route_bench") or {}).get("years"), len(ga), len(gb),
        sum(near(g, gb) for g in ga), sum(near(g, ga) for g in gb), len(a.get("tee_complexes") or []),
        len(b.get("tee_complexes") or [])))
