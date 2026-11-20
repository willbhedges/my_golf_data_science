"""inputs_check.py ARTS_DIR: the bench_inputs stage's summary from the meta-<job>/<slug>.json records (refit/bench_inputs.py).
Main jobs: courses built / failed (with errors), the package-year pin kept, U-Net implementations and CPUs.
Twin jobs (a sample rebuilt again, possibly with another FASTPERC_IMPL): per course and job against the main build,
whether the NAIP item ids, the imagery / DEM / canopy bytes, the U-Net probabilities and the scene counts are
identical, with the CPU of each job - imagery moving = the served imagery; same imagery, other probabilities = the
arithmetic (CPU / implementation)."""
import glob, json, os, sys
from collections import Counter, defaultdict

arts = sys.argv[1]
recs = defaultdict(dict)               # job -> slug -> rec
for p in glob.glob(os.path.join(arts, "meta-*", "*.json")):
    job = os.path.basename(os.path.dirname(p))[5:]
    r = json.load(open(p))
    recs[job][r["slug"]] = r
main = {s: r for j, rs in recs.items() if j.startswith("main") for s, r in rs.items()}
bad = {s: r for s, r in main.items() if "error" in r}
print("main build: %d courses, %d ok, %d failed (TRAIN-BIG %d, validation %d)" % (
    len(main), len(main) - len(bad), len(bad), sum(s.startswith("tb_") for s in main), sum(not s.startswith("tb_") for s in main)))
for s, r in sorted(bad.items()):
    print("  failed %s: %s" % (s, r["error"][:200]))
ok = [r for r in main.values() if "error" not in r]
print("package-year pin kept on %d of %d; extra years dropped on %d" % (
    sum(r["fetch"]["pkg_pin_kept"] for r in ok), len(ok), sum(bool(r["fetch"].get("extra_dropped")) for r in ok)))
print("U-Net implementations:", dict(Counter(",".join(r.get("unet_impl") or []) for r in ok)))
print("CPUs (main jobs):", dict(Counter("%s amx=%s" % (r["cpu"]["model"], r["cpu"]["amx"]) for r in main.values())))
print("thread / impl pins:", json.dumps(next(iter(main.values()))["env"]) if main else "-")


def key(r):
    im = r.get("imagery") or {}
    return dict(items={y: v.get("items") for y, v in im.items()}, img={y: v.get("sha") for y, v in im.items()},
                files=r.get("files"), probs=r.get("probs_sha"),
                scene=(r.get("greens_hole"), r.get("greens"), r.get("tee_complexes")), years=r.get("unet_years"))


twins = sorted(j for j in recs if j.startswith("twin"))
if twins:
    print("\ntwin rebuilds against the main build (same = identical; items / imagery bytes / dem+canopy / probs / scene counts)")
    tally = defaultdict(Counter)
    for j in twins:
        cpu = next(iter(recs[j].values()))["cpu"] if recs[j] else {}
        print("  %s on %s amx=%s" % (j, cpu.get("model"), cpu.get("amx")))
        for s, r in sorted(recs[j].items()):
            m = main.get(s)
            if m is None or "error" in m or "error" in r:
                print("    %-34s missing / failed" % s)
                continue
            a, b = key(m), key(r)
            flags = {k: a[k] == b[k] for k in ("items", "img", "files", "probs", "scene")}
            for k, v in flags.items():
                tally[j][k] += v
            tally[j]["n"] += 1
            print("    %-34s %s | main cpu %s | impl %s vs %s | scene %s vs %s" % (
                s, " ".join("%s=%s" % (k, "same" if v else "DIFF") for k, v in flags.items()), m["cpu"]["model"][:28],
                ",".join(m.get("unet_impl") or []), ",".join(r.get("unet_impl") or []), a["scene"], b["scene"]))
    print("\ntwin tally (courses identical / compared):")
    for j in twins:
        t = tally[j]
        print("  %-14s %s" % (j, " ".join("%s %d/%d" % (k, t[k], t["n"]) for k in ("items", "img", "files", "probs", "scene"))))
    print("\ntwin jobs of the same implementation against each other (probs / scene identical):")
    for i, j in enumerate(twins):
        for k in twins[i + 1:]:
            if j.rsplit("-", 1)[0] != k.rsplit("-", 1)[0]:
                continue
            cs = [s for s in recs[j] if s in recs[k] and "error" not in recs[j][s] and "error" not in recs[k][s]]
            cj, ck = (next(iter(recs[x].values()))["cpu"] for x in (j, k))
            print("  %s (%s amx=%s) vs %s (%s amx=%s): img same %d, probs same %d, scene same %d of %d" % (
                j, cj["model"][:30], cj["amx"], k, ck["model"][:30], ck["amx"],
                sum(key(recs[j][s])["img"] == key(recs[k][s])["img"] for s in cs),
                sum(key(recs[j][s])["probs"] == key(recs[k][s])["probs"] for s in cs),
                sum(key(recs[j][s])["scene"] == key(recs[k][s])["scene"] for s in cs), len(cs)))
