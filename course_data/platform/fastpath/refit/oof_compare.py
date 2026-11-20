"""oof_compare.py A.json [B.json] [--identity]: route_bench eval outputs (a refit's out-of-fold bench, oof.json) per
split (all = train+big, choice = not in never_used.txt, never-used; never test):
  one file:  holes right, forward-tee metric (hole_ok_fwd), all-right courses, card error (median over courses of the
             median |routed - card| yd) and courses with errors.
  two files: both tables, then B against A on the courses in both: net holes, better / worse / same, flips of 5+
             holes, and the card guardrail (card error median B - A, courses whose card error median rose > 10 yd).
  --identity: exit 1 unless every course's per-hole result and routed lines are identical (determinism check)."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
NEW = set(open(os.path.join(HERE, "never_used.txt")).read().strip().split(","))


def load(p):
    return {r["slug"]: r for r in json.load(open(p))["courses"]}


def cerr(r):
    v = [abs(x) for x in (r.get("card_resid") or {}).values() if x is not None]
    return float(np.median(v)) if v else None


def splits(slugs):
    return (("all", sorted(slugs)), ("choice", sorted(s for s in slugs if s not in NEW)),
            ("never-used", sorted(s for s in slugs if s in NEW)))


def table(name, R):
    print("== %s" % name)
    for nm, ss in splits(R):
        rs = [R[s] for s in ss]
        H = sum(r.get("n_true", 0) for r in rs) or 1
        ok = sum(sum((r.get("hole_ok") or {}).values()) for r in rs)
        fw = sum(sum((r.get("hole_ok_fwd") or {}).values()) for r in rs)
        al = sum(bool((r.get("score") or {}).get("all_correct")) for r in rs)
        ce = [c for c in (cerr(r) for r in rs) if c is not None]
        print("  %-10s %3d courses %5d holes | right %.2f %% (%d) | fwd %.2f %% | all-right %d | card err med %.1f yd | errors %d"
              % (nm, len(rs), H, 100 * ok / H, ok, 100 * fw / H, al, np.median(ce) if ce else float("nan"),
                 sum(bool(r.get("error")) for r in rs)))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    A = load(args[0])
    table(os.path.basename(args[0]), A)
    if len(args) < 2:
        return
    B = load(args[1])
    table(os.path.basename(args[1]), B)
    both = set(A) & set(B)
    print("== B (%s) against A (%s) on the %d courses in both (A only %d, B only %d)"
          % (os.path.basename(args[1]), os.path.basename(args[0]), len(both), len(set(A) - both), len(set(B) - both)))
    diff_ok = diff_lines = 0
    for nm, ss in splits(both):
        d = [(sum((B[s].get("hole_ok") or {}).values()) - sum((A[s].get("hole_ok") or {}).values()), s) for s in ss]
        df = sum(sum((B[s].get("hole_ok_fwd") or {}).values()) - sum((A[s].get("hole_ok_fwd") or {}).values()) for s in ss)
        ca = [cerr(A[s]) for s in ss]
        cb = [cerr(B[s]) for s in ss]
        pr = [(a, b) for a, b in zip(ca, cb) if a is not None and b is not None]
        up10 = sum(b - a > 10 for a, b in pr)
        print("  %-10s net %+d holes (fwd %+d) | better %d (+%d) worse %d (%d) same %d | card err med A %.1f B %.1f yd, rose > 10 yd on %d"
              % (nm, sum(x for x, _ in d), df, sum(x > 0 for x, _ in d), sum(x for x, _ in d if x > 0),
                 sum(x < 0 for x, _ in d), sum(x for x, _ in d if x < 0), sum(x == 0 for x, _ in d),
                 np.median([a for a, _ in pr]) if pr else float("nan"), np.median([b for _, b in pr]) if pr else float("nan"), up10))
        print("             flips >= 5 up %s" % sorted([(s, x) for x, s in d if x >= 5], key=lambda t: -t[1])[:12])
        print("             flips >= 5 down %s" % sorted([(s, x) for x, s in d if x <= -5], key=lambda t: t[1])[:12])
    for s in sorted(both):
        diff_ok += A[s].get("hole_ok") != B[s].get("hole_ok")
        diff_lines += A[s].get("lines") != B[s].get("lines")
    print("identity: per-hole results differ on %d courses, routed lines on %d (of %d)" % (diff_ok, diff_lines, len(both)))
    if "--identity" in sys.argv:
        ok = not diff_ok and not diff_lines and set(A) == set(B)
        print("IDENTICAL" if ok else "NOT IDENTICAL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
