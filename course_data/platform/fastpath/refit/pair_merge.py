"""pair_merge.py PAIR.jsonl...: the detector_pair tables per split (choice = not in never_used.txt, never-used):
holes right A / B, courses better / worse / same for B, net change, courses flipping by >= 5 holes each way, the
forward-tee metric, card error and the scenes' green / tee recall against the truth. Writes the merged rows as
pair_all.jsonl next to the first input when PAIR_OUT is set."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
new = set(open(os.path.join(HERE, "never_used.txt")).read().strip().split(","))
rows = [json.loads(l) for p in sys.argv[1:] for l in open(p) if l.strip()]
if os.environ.get("PAIR_OUT"):
    with open(os.environ["PAIR_OUT"], "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
ok = [r for r in rows if "error" not in r and "right" in (r.get("A") or {}) and "right" in (r.get("B") or {})]
bad = [r["slug"] for r in rows if r not in ok]
print("courses: %d, complete pairs: %d, failed: %d %s" % (len(rows), len(ok), len(bad), bad[:12]))
if ok:
    r0 = ok[0]
    print("A = %s + %s | B = %s + %s | B imagery %s" % (r0["unet"]["A"], r0["objects"]["A"], r0["unet"]["B"], r0["objects"]["B"],
                                                         "refetched" if r0.get("refetch_b") else "shared with A"))
for nm, sub in (("choice", [r for r in ok if r["slug"] not in new]), ("never-used", [r for r in ok if r["slug"] in new]),
                ("all", ok)):
    if not sub:
        continue
    H = sum(r["A"]["n_true"] for r in sub)
    a, b = sum(r["A"]["right"] for r in sub), sum(r["B"]["right"] for r in sub)
    fa, fb = sum(r["A"]["right_fwd"] for r in sub), sum(r["B"]["right_fwd"] for r in sub)
    d = [(r["B"]["right"] - r["A"]["right"], r["slug"]) for r in sub]
    ce = lambda k: np.median([r[k]["card_err_med"] for r in sub if r[k].get("card_err_med") is not None])  # noqa: E731
    print("\n== %s: %d courses, %d holes" % (nm, len(sub), H))
    print("  holes right   A %.2f %% (%d)   B %.2f %% (%d)   net %+d holes" % (100 * a / H, a, 100 * b / H, b, b - a))
    print("  fwd metric    A %.2f %%   B %.2f %%" % (100 * fa / H, 100 * fb / H))
    print("  B vs A        better %d (+%d)   worse %d (%d)   same %d" % (
        sum(x > 0 for x, _ in d), sum(x for x, _ in d if x > 0), sum(x < 0 for x, _ in d), sum(x for x, _ in d if x < 0),
        sum(x == 0 for x, _ in d)))
    print("  flips >= 5    up %d %s" % (sum(x >= 5 for x, _ in d), sorted([(s, x) for x, s in d if x >= 5], key=lambda t: -t[1])[:15]))
    print("                down %d %s" % (sum(x <= -5 for x, _ in d), sorted([(s, x) for x, s in d if x <= -5], key=lambda t: t[1])[:15]))
    print("  all-right     A %d   B %d" % (sum(r["A"]["right"] == r["A"]["n_true"] for r in sub), sum(r["B"]["right"] == r["B"]["n_true"] for r in sub)))
    print("  card err med  A %.1f   B %.1f yd (median of course medians)" % (ce("A"), ce("B")))
    print("  green recall  A %.2f %%   B %.2f %%" % tuple(100 * sum(r[k]["green_recall"] for r in sub) / H for k in "AB"))
    print("  tee recall    A %.2f %%   B %.2f %%" % tuple(100 * sum(r[k]["tee_recall"] for r in sub) / H for k in "AB"))
    print("  scene hole greens A %d   B %d   tee complexes A %d   B %d" % tuple(
        sum(r[k][f] for r in sub) for f in ("greens_hole", "tee_complexes") for k in "AB"))
