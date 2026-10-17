"""One-shot QA run: contract tests -> contracts.json, golden -> golden.json, REPORT.md; optional review images.

  python3 course_data/qa/run_qa.py              # contracts + golden (+ REPORT.md)
  python3 course_data/qa/run_qa.py --review     # also re-render course_data/qa/review/<slug>/*.jpg
  python3 course_data/qa/run_qa.py --no-golden  # contracts only (light; committed packages only)
The product scoreboard (club agreement, regret, geometry, CHECKs per course) is course_data/qa/scoreboard.py.
"""
import argparse
import collections
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

QA = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(QA))


def contracts(with_work=False):
    xml = os.path.join(QA, ".contracts.xml")
    env = dict(os.environ, QA_SKIP_WORK="0" if with_work else "1")
    subprocess.run([sys.executable, "-m", "pytest", os.path.join(QA, "test_contracts.py"), "-q", "-p", "no:cacheprovider",
                    f"--junitxml={xml}"], cwd=ROOT, stdout=subprocess.DEVNULL, env=env)
    out = collections.OrderedDict()
    for tc in ET.parse(xml).getroot().iter("testcase"):
        name = tc.get("name")
        m = re.match(r"(\w+)\[(.+)\]$", name)
        if not m:
            continue
        test, ident = m.groups()
        parts = ident.split("-")
        pk, hole = parts[0], "-".join(parts[1:]) or None
        v = out.setdefault(pk, dict(passed=0, failed=0, skipped=0, holes=set(), fails=collections.defaultdict(list), msgs=[]))
        if hole:
            v["holes"].add(hole.split("-")[0])
        f = tc.find("failure")
        if f is None:
            f = tc.find("error")
        if f is not None:
            v["failed"] += 1
            v["fails"][test.replace("test_", "")].append(hole or "pkg")
            v["msgs"].append(f"{test} {hole or ''}: {(f.get('message') or '').splitlines()[0][:220]}")
        elif tc.find("skipped") is not None:
            v["skipped"] += 1
        else:
            v["passed"] += 1
    res = {}
    for pk, v in out.items():
        res[pk] = dict(passed=v["passed"], failed=v["failed"], skipped=v["skipped"], holes=len(v["holes"]),
                       fail_summary=[f"{k} ({len(h)}: {','.join(h[:10])})" for k, h in v["fails"].items()],
                       messages=v["msgs"])
    os.remove(xml)
    with open(os.path.join(QA, "contracts.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    for pk, v in res.items():
        print(f"{pk}: {v['passed']} passed, {v['failed']} failed, {v['skipped']} skipped; {v['fail_summary']}")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", action="store_true")
    ap.add_argument("--no-golden", action="store_true")
    ap.add_argument("--with-work", action="store_true", help="also test QA's untracked scratch builds in qa/work/")
    a = ap.parse_args()
    contracts(a.with_work)
    if a.review:
        subprocess.run([sys.executable, os.path.join(QA, "review.py")], cwd=ROOT)
    if not a.no_golden:
        subprocess.run([sys.executable, os.path.join(QA, "golden_spirit_hollow.py")], cwd=ROOT)


if __name__ == "__main__":
    main()
