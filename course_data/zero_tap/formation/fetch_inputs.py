"""Inputs for the formation study, built on GitHub Actions (zt_formation.yml, stage "inputs").

    python course_data/zero_tap/formation/fetch_inputs.py slugs                 -> JSON list of every study course
    python course_data/zero_tap/formation/fetch_inputs.py run --chunk 0 --of 6 [--stacks /home/runner/stacks] --out out

Per course (structure/sets.json courses + generalize/courses):
  aux.npz         aux_build.py layers (U-Net fairway / tee / green, lidar DTM + canopy, mowing stripes), 5 m
  scene.json.gz   a blind perception scene (perception/perceive.py with the committed models, no OSM golf input)
                  for courses that have none committed in course_data/perception/scenes
  scorecard.json  web cards (platform/fetch_package.fetch_scorecards with NO OSM lengths, so nothing of the truth
                  steers which card is kept) for courses without one in generalize/courses
The stack is restored from the perception workflow's combined cache when present, else built (fetch_stack.py).
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import shutil
import subprocess
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(os.path.dirname(HERE))
ROOT = os.path.dirname(CD)


def study_courses():
    out = []
    sets = json.load(open(os.path.join(CD, "structure", "sets.json")))
    for c in sets["courses"]:
        cj = os.path.join(CD, "structure", "data", c["slug"], "course.json")
        if os.path.exists(cj):
            out.append(dict(slug=c["slug"], course=cj, src="structure", split=c["split"], state=c["state"]))
    gdir = os.path.join(CD, "generalize", "courses")
    for s in sorted(os.listdir(gdir)):
        cj = os.path.join(gdir, s, "course.json")
        if os.path.exists(cj):
            out.append(dict(slug=s, course=cj, src="generalize", split="dev", state=s.rsplit("_", 1)[-1].upper()))
    return out


def run(cmd, timeout):
    print("$", " ".join(cmd), flush=True)
    try:
        r = subprocess.run(cmd, timeout=timeout)
        return r.returncode == 0
    except subprocess.TimeoutExpired:
        print("timeout", flush=True)
        return False


def one(c, stacks, out, work):
    slug = c["slug"]
    od = os.path.join(out, slug)
    os.makedirs(od, exist_ok=True)
    log = dict(slug=slug, t0=time.time())
    # 1. scorecards (structure courses: none committed)
    if c["src"] == "structure":
        try:
            sys.path[:0] = [os.path.join(CD, "platform"), CD]
            import fetch_package as fp
            course = json.load(open(c["course"]))
            req = dict(schema="request/1", kind="package", course=course.get("name"), state=course.get("state"),
                       osm=None, tees="back", allow_substitute=True, slug=slug)
            raw = os.path.join(work, slug + "_raw")
            os.makedirs(raw, exist_ok=True)
            sw = fp.fetch_scorecards(req, course, {}, raw)
            import scorecard as scm
            cards = [dict(source=k["source"], url=k.get("url"), card=scm.normalise(k["card"])) for k in sw.get("cards", [])]
            pick = scm.choose_card([(k["source"], k["card"], k.get("url")) for k in cards]) if cards else None
            json.dump(dict(cards=cards, chosen=pick[0] if pick else None, tried=sw.get("tried"),
                           note="fetched without OSM hole lengths (zero_tap/formation)"),
                      open(os.path.join(od, "scorecard.json"), "w"), indent=1)
            log["cards"] = [k["source"] for k in cards]
        except Exception as e:                                       # noqa: BLE001
            traceback.print_exc()
            log["card_error"] = repr(e)[:300]
    # 2. stack
    sd = os.path.join(stacks, slug) if stacks else None
    if not (sd and os.path.exists(os.path.join(sd, "stack.npz"))):
        sd = os.path.join(work, slug)
        ok = run([sys.executable, "-u", os.path.join(CD, "perception", "fetch_stack.py"), slug, "--course", c["course"],
                  "--out", sd], 2400)
        shutil.rmtree(os.path.join(sd, "raw"), ignore_errors=True)
        log["stack_built"] = ok
    if not os.path.exists(os.path.join(sd, "stack.npz")):
        log["error"] = "no stack"
        return log
    # 3. aux layers
    log["aux"] = run([sys.executable, "-u", os.path.join(HERE, "aux_build.py"), sd, "--out", os.path.join(od, "aux.npz")], 900)
    # 4. blind scene when none is committed
    if not os.path.exists(os.path.join(CD, "perception", "scenes", slug, "scene.json.gz")):
        tmp = os.path.join(work, slug + "_scene")
        ok = run([sys.executable, "-u", os.path.join(CD, "perception", "perceive.py"), sd, "--out", tmp], 1800)
        if ok and os.path.exists(os.path.join(tmp, "scene.json")):
            with open(os.path.join(tmp, "scene.json"), "rb") as fi, gzip.open(os.path.join(od, "scene.json.gz"), "wb") as fo:
                fo.write(fi.read())
            if os.path.exists(os.path.join(tmp, "eval.json")):
                shutil.copy(os.path.join(tmp, "eval.json"), os.path.join(od, "perception_eval.json"))
        log["scene"] = ok
    if sd.startswith(work):
        shutil.rmtree(sd, ignore_errors=True)
    log["seconds"] = round(time.time() - log.pop("t0"), 1)
    return log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["slugs", "run"])
    ap.add_argument("--chunk", type=int, default=0)
    ap.add_argument("--of", type=int, default=1)
    ap.add_argument("--stacks", default="")
    ap.add_argument("--out", default="out")
    ap.add_argument("--work", default="work_formation")
    ap.add_argument("--only", default="", help="comma-separated slugs")
    a = ap.parse_args()
    cs = study_courses()
    if a.cmd == "slugs":
        print(json.dumps([c["slug"] for c in cs]))
        return
    if a.only:
        keep = set(a.only.split(","))
        cs = [c for c in cs if c["slug"] in keep]
    cs = cs[a.chunk::a.of]
    os.makedirs(a.out, exist_ok=True)
    os.makedirs(a.work, exist_ok=True)
    logs = []
    for i, c in enumerate(cs):
        print(f"=== [{i + 1}/{len(cs)}] {c['slug']}", flush=True)
        try:
            logs.append(one(c, a.stacks, a.out, a.work))
        except Exception as e:                                       # noqa: BLE001
            traceback.print_exc()
            logs.append(dict(slug=c["slug"], error=repr(e)[:300]))
        print(json.dumps(logs[-1]), flush=True)
        json.dump(logs, open(os.path.join(a.out, f"_log_{a.chunk}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
