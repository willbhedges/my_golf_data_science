"""End-to-end check: package -> product/plan.py -> book PDF + aim sheets + wind page, for any course.

  python3 course_data/qa/e2e.py --package course_data/packages/<slug>/package.json --tees White
  python3 course_data/qa/e2e.py --all            # every package on disk (its own tee set)

Runs plan.py --quick into a scratch dir (never into another team's folder), then checks the deliverables:
  * plan.py exits 0 within the time limit
  * <Name>_Strategy.pdf and _Aim_Sheets.pdf exist, open, and have >= one page per hole
  * wind_page/index.html exists, is self-contained (no http(s) script src outside the allowed CDNs), and
    embeds a wind grid for every tee shot
  * decision.json has a club + aim for every par-4/5 hole of the package; aims inside +/-60 and not on the bound
  * plan.json lists its data gaps
Writes course_data/qa/e2e.json (results only; the PDFs stay in the scratch dir, path recorded).
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
import time

QA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QA)
import packages as P                                     # noqa: E402

PLAN = os.path.join(P.CD, "product", "plan.py")
SCRATCH = os.environ.get("QA_SCRATCH") or os.path.join(tempfile.gettempdir(), "qa_e2e")


def pdf_pages(path):
    try:
        from pypdf import PdfReader
        return len(PdfReader(path).pages)
    except ImportError:
        pass
    try:
        out = subprocess.run(["pdfinfo", path], capture_output=True, text=True).stdout
        m = re.search(r"Pages:\s+(\d+)", out)
        return int(m.group(1)) if m else None
    except FileNotFoundError:
        data = open(path, "rb").read()
        return len(re.findall(rb"/Type\s*/Page[^s]", data))


def run(pkg_path, tees, timeout=1800, extra=(), check_only=False):
    pk = next((p for p in P.find_packages() if os.path.abspath(p.path) == os.path.abspath(pkg_path)), None)
    slug = pk.slug if pk else os.path.basename(os.path.dirname(pkg_path))
    out = os.path.join(SCRATCH, slug + ("_" + tees if tees else ""))
    os.makedirs(out, exist_ok=True)
    cmd = [sys.executable, PLAN, "--package", pkg_path, "--quick", "--out", out] + (["--tees", tees] if tees else []) + list(extra)
    t0 = time.time()
    r = dict(package=os.path.relpath(pkg_path, P.ROOT), tees=tees, out=out, cmd=" ".join(cmd), checks={}, problems=[])
    prev = (json.load(open(os.path.join(QA, "e2e.json"))) if os.path.exists(os.path.join(QA, "e2e.json")) else {}).get(
        f"{os.path.relpath(pkg_path, P.ROOT)}|{tees}", {})
    if check_only:
        r["exit"], r["seconds"], r["log_tail"] = prev.get("exit", 0), prev.get("seconds"), prev.get("log_tail")
    else:
        try:
            p = subprocess.run(cmd, cwd=P.ROOT, capture_output=True, text=True, timeout=timeout)
            r["exit"] = p.returncode
            r["log_tail"] = (p.stdout + p.stderr)[-3000:]
        except subprocess.TimeoutExpired:
            r["exit"] = "timeout"
        r["seconds"] = round(time.time() - t0)
    r["checks"]["plan_exit_0"] = r["exit"] == 0
    n_holes = len(pk.holes) if pk else None
    tee_holes = [k for k, q in (pk.holes.items() if pk else []) if (q.par or 4) > 3]
    pdfs = sorted(glob.glob(os.path.join(out, "*_Strategy.pdf")))
    aims = sorted(glob.glob(os.path.join(out, "*_Aim_Sheets.pdf")))
    r["checks"]["book_pdf"] = bool(pdfs)
    r["checks"]["aim_sheets_pdf"] = bool(aims)
    if pdfs:
        n = pdf_pages(pdfs[0])
        r["book_pages"] = n
        r["book_mb"] = round(os.path.getsize(pdfs[0]) / 1e6, 1)
        r["checks"]["book_pages_ge_holes"] = bool(n and n_holes and n >= n_holes)
    if aims:
        r["aim_pages"] = pdf_pages(aims[0])
    wp = os.path.join(out, "wind_page", "index.html")
    r["checks"]["wind_page"] = os.path.exists(wp)
    if os.path.exists(wp):
        html = open(wp).read()
        r["wind_page_kb"] = round(len(html) / 1e3)
        ext = re.findall(r'<script[^>]+src="(https?://[^"]+)"', html)
        bad = [u for u in ext if not re.match(r"https://(cdnjs\.cloudflare\.com|cdn\.jsdelivr\.net/npm/|unpkg\.com)", u)]
        r["checks"]["wind_page_self_contained"] = not bad
        if bad:
            r["problems"].append(f"wind page loads {bad}")
        missing = [k for k in tee_holes if not re.search(r'["\']%s[BF]?["\']\s*:|"key"\s*:\s*"?%s[BF]?["\s,}]'
                                                       % (re.escape(k), re.escape(k)), html)]
        r["checks"]["wind_page_all_tee_holes"] = not missing
        if missing:
            r["problems"].append(f"wind page has no entry for holes {missing}")
    dj = os.path.join(out, "decision.json")
    if os.path.exists(dj):
        d = json.load(open(dj))
        d = d.get("holes", d)
        r["decision"] = {k: dict(club=v.get("pick") or v.get("club"), aim=v.get("aim")) for k, v in d.items()
                         if isinstance(v, dict)}
        got = {k.rstrip("BF") for k in r["decision"]}
        miss = [k for k in tee_holes if k not in got]
        r["checks"]["decision_all_tee_holes"] = not miss
        if miss:
            r["problems"].append(f"no decision for holes {miss}")
        edge = [k for k, v in r["decision"].items() if v["aim"] is not None and abs(float(v["aim"])) >= 59.9]
        r["checks"]["no_aim_on_bound"] = not edge
        if edge:
            r["problems"].append(f"aim on the +/-60 search bound: {edge}")
    else:
        r["checks"]["decision_all_tee_holes"] = False
    pj = os.path.join(out, "plan.json")
    if os.path.exists(pj):
        pl = json.load(open(pj))
        r["data_gaps"] = pl.get("gaps") or pl.get("data_gaps")
    r["ok"] = all(r["checks"].values())
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", action="append")
    ap.add_argument("--tees")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--check-only", action="store_true", help="re-check an existing output dir, don't run plan.py")
    a = ap.parse_args()
    jobs = []
    if a.all:
        for pk in P.find_packages():
            if pk.kind == "package.json":
                jobs.append((pk.path, a.tees or pk.tee_set))
    for p in a.package or []:
        jobs.append((p, a.tees))
    resf = os.path.join(QA, "e2e.json")
    res = json.load(open(resf)) if os.path.exists(resf) else {}
    for path, tees in jobs:
        print("e2e:", path, tees, flush=True)
        r = run(path, tees, a.timeout, check_only=a.check_only)
        res[f"{os.path.relpath(path, P.ROOT)}|{tees}"] = r
        print(json.dumps({k: v for k, v in r.items() if k not in ("log_tail", "decision")}, indent=1), flush=True)
        with open(resf, "w") as fh:
            json.dump(res, fh, indent=1)


if __name__ == "__main__":
    main()
