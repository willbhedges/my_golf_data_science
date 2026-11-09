"""Blind loop driver: build courses of the fixed list (platform/blind20/blind20.json, loop order) on the fast path and
write one contact sheet each.   python3 loop.py 2        |  python3 loop.py 1 2 3   (re-run: cached fetches)
-> cache/packages/b20_<slug>/ + cache/contact/<order>_<slug>.jpg + one status line per course
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fast  # noqa: E402

LIST = os.path.join(os.path.dirname(HERE), "blind20", "blind20.json")
SHEETS = os.path.join(os.path.dirname(HERE), "blind20", "blind20_sheets.py")


def one(c):
    t0 = time.time()
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            r = fast.build(None, slug=c["slug"], row=c, log=lambda *a: None)
    except BaseException as e:                                       # noqa: BLE001
        import traceback
        r = dict(status="failed", stage="crash", why=f"{type(e).__name__}: {e}"[:300], trace=traceback.format_exc()[-1200:])
    r["wall"] = round(time.time() - t0, 1)
    if isinstance((r.get("timing") or {}).get("card"), str):          # phase 2: the card arrived after the first answer
        t1 = time.time()
        if fast.wait_card(90):
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                r2 = fast.build(None, slug=c["slug"], row=c, log=lambda *a: None)
            r2["wall"] = r["wall"]
            r2["phase2"] = f"card search finished {round(time.time() - t1, 1)} s after the first answer; rebuilt with it"
            r = r2
    d = os.path.join(fast.pc.PACKAGES, c["slug"])
    sheet = os.path.join(fast.CACHE, "contact", f"{c['order']:02d}_{c['slug']}.jpg")
    if r.get("status") in ("ok", "blocked") and os.path.exists(os.path.join(d, "imagery", "naip_rgb.tif")):
        subprocess.run([sys.executable, SHEETS, "--course-dir", d, "--img", os.path.join(d, "imagery"), "--contact", sheet],
                       capture_output=True)
        r["sheet"] = sheet
    pkg = json.load(open(os.path.join(d, "package.json"))) if os.path.exists(os.path.join(d, "package.json")) and r.get("status") in ("ok", "blocked") else {}
    st = pkg.get("stages") or {}
    print(f"{c['order']} {c['tier']} {c['name']} ({c['city']}, {c['state']}): {r.get('status')} {r.get('stage') or ''} "
          f"{r.get('wall')} s | holes {r.get('holes')} | {r.get('why') or ''}")
    if pkg:
        dec = (json.load(open(os.path.join(d, "decision.json"))) if os.path.exists(os.path.join(d, "decision.json")) else {}).get("holes", {})
        print("   timing", {k: v for k, v in (r.get("timing") or {}).items() if k not in ("fetch (card || imagery)",)})
        print("   card", (pkg.get("sources", {}).get("scorecard") or {}).get("kind"), "| set", pkg.get("tee_set"), "| holes method",
              (pkg.get("pipeline", {}).get("holes") or {}).get("method"), "| pars", sum(h.get("par") or 0 for h in pkg["holes"].values()))
        for k in ("routing", "tees", "green_auto", "fairway_fill", "green_visibility", "trees_meta", "elevation"):
            if st.get(k):
                print(f"   {k}: {str(st[k])[:150]}")
        if r.get("phase2"):
            print("   phase 2:", r["phase2"])
        print("   warnings", len(pkg.get("warnings") or []), [w[:110] for w in (pkg.get("warnings") or [])[:6]])
        print("   picks", {k: f"{v['pick']} {v['aim']:+.0f}" for k, v in dec.items()})
        print("   sheet", r.get("sheet"))
    elif r.get("trace"):
        print(r["trace"])
    return r


if __name__ == "__main__":
    cs = {c["order"]: c for c in json.load(open(LIST))["courses"]}
    for n in sys.argv[1:]:
        one(cs[int(n)])
