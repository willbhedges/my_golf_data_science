"""Run plan.py for request files (what .github/workflows/plan_course.yml calls on Actions).

  python3 course_data/product/run_requests.py course_data/product/requests/spirit_hollow.json [...]

Request file (course_data/product/requests/<slug>.json, or ARCHITECTURE 9.4's course_data/requests/plan_*.json):
  {"package": "course_data/packages/<slug>/package.json",   # or "course": "<name>" for an offline stand-in
   "tees": "Black", "mode": "quick" | "full",
   "draws": 64, "days": "2026-10-17,2026-10-18", "out": "<dir>"}       # optional
Each run's log goes to <out>/plan_log.txt; files over 50 MB are deleted (never committed). The output
directories are listed in $GITHUB_OUTPUT as `dirs` (space separated) for the commit step.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MAX_BYTES = 50 * 1024 * 1024


def args_for(req):
    a = []
    if req.get("package"):
        a += ["--package", req["package"]]
    elif req.get("course"):
        a += ["--course", req["course"]]
    else:
        raise ValueError("request needs 'package' (path to package.json) or 'course'")
    if req.get("tees") or req.get("tee_set"):
        a += ["--tees", req.get("tees") or req.get("tee_set")]
    a += ["--mode", "full" if str(req.get("mode", "quick")).lower() == "full" else "quick"]
    for k in ("draws", "days", "out", "forecast", "workers"):
        if req.get(k) is not None:
            a += [f"--{k}", str(req[k])]
    return a


def main(paths):
    dirs, failed = [], []
    for p in paths:
        if not p.endswith(".json") or not os.path.exists(p):
            continue
        req = json.load(open(p))
        if req.get("kind") not in (None, "plan"):
            continue
        print(f"::group::plan {p}", flush=True)
        try:
            cmd = [sys.executable, os.path.join(HERE, "plan.py")] + args_for(req)
        except ValueError as e:
            print(f"::error file={p}::{e}")
            failed.append(p)
            continue
        print(" ".join(cmd), flush=True)
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        print(proc.stdout[-20000:])
        print(proc.stderr[-20000:], file=sys.stderr)
        out = None
        for line in proc.stdout.splitlines():
            if "done in" in line and "->" in line:
                out = line.split("->")[-1].strip()
        if out is None:                       # plan.py failed before the manifest: guess the slug
            slug = os.path.splitext(os.path.basename(p))[0]
            slug = slug[5:] if slug.startswith("plan_") else slug
            if len(slug) > 3 and slug[2] == "_" and slug[:2].isalpha() and req.get("state", "").lower() == slug[:2]:
                slug = slug[3:]
            out = req.get("out") or os.path.join("course_data", "packages", slug, "out")
        od = os.path.join(ROOT, out)
        os.makedirs(od, exist_ok=True)
        with open(os.path.join(od, "plan_log.txt"), "w") as fh:
            fh.write(f"request: {p}\n$ {' '.join(cmd)}\nexit {proc.returncode}\n\n{proc.stdout}\n{proc.stderr[-20000:]}")
        for dp, _, fs in os.walk(od):
            for f in fs:
                fp = os.path.join(dp, f)
                if os.path.getsize(fp) > MAX_BYTES:
                    print(f"::warning::{fp} is {os.path.getsize(fp) / 1e6:.0f} MB: not committed")
                    os.remove(fp)
        dirs.append(out)
        if proc.returncode != 0:
            print(f"::error file={p}::plan.py exited {proc.returncode}")
            failed.append(p)
        print("::endgroup::", flush=True)
    gh = os.environ.get("GITHUB_OUTPUT")
    if gh:
        with open(gh, "a") as fh:
            fh.write("dirs=" + " ".join(dirs) + "\n")
    print("output dirs:", dirs, "failed:", failed)
    return 1 if failed and not dirs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
