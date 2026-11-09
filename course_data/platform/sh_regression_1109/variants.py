"""Quick-mode diagnostics on SH Black holes: package variants for the native layer."""
import sys, json, os, copy
ROOT = "/home/user/my_golf_data_science"
sys.path.insert(0, os.path.join(ROOT, "course_data", "qa"))
import scoreboard as SB
S = os.environ.get("SH1109_DIR", "/tmp/sh1109")  # needs $S/pk/d06e6acee.json = git show d06e6acee:course_data/packages/spirit_hollow/package.json
base = json.load(open(f"{S}/pk/d06e6acee.json"))
hz = json.load(open(f"{ROOT}/course_data/spirit_hollow/hand_zones_ll.json"))["holes"]
holes = sys.argv[1].split(",")
final = SB.final_truth()
def strip(pkg, ref, sides=("L", "R")):
    h = pkg["holes"][ref]
    h["zones_ll"] = [z for z in h["zones_ll"] if not (z.get("src") == "auto:native_side")]
def variant(name):
    p = copy.deepcopy(base)
    for ref in holes:
        h = p["holes"][ref]
        if name == "head": pass
        elif name == "nonative": strip(p, ref)
        elif name == "handnative":
            strip(p, ref)
            h["zones_ll"].append  # hand native polygons appended (lowest precedence lie, package order rules)
            for z in hz[ref]["zones"]:
                if z["lie"] == "native":
                    h["zones_ll"].append(dict(lie="native", poly=[[ll[1], ll[0]] if abs(ll[0]) < 60 else ll for ll in z["poly_ll"]], src="hand"))
        elif name in ("onlyL", "onlyR"):
            # keep auto native only on one side: classify by the native_sides p/side? use zone order (L first when both)
            pass
    return p
out = {}
for name in sys.argv[2].split(","):
    p = variant(name)
    f = f"{S}/pk/var_{name}.json"; json.dump(p, open(f, "w"))
    cfg = dict(SB.COURSES[0]); cfg["package"] = f
    res, C, s = SB.product_plan(cfg, "Black", keys=set(holes), n=8000)
    for k in holes:
        r = res[k]; tr = final[k]
        print(name, k, r["pick"], round(float(r["aim"]), 1), "margin", round(float(r["margin"]), 3), "truth", tr["pick"],
              "regret", SB.regret(r, tr), {c: round(v["ev"], 3) for c, v in r["clubs"].items()}, flush=True)
