"""run_requests.py phases (requests first, then the sharded offline rebuild), build hash, chunk commits;
merge_index.py; commit_run.sh / commit_packages.sh against a throwaway origin."""
import json
import os
import shutil
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import merge_index  # noqa: E402
import platform_common as pc  # noqa: E402
import run_requests as rr  # noqa: E402


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A fake repo root: course_data/platform/{a,test_a}.py, requests a (new) / b, c (fetched)."""
    cd = tmp_path / "course_data"
    (cd / "platform").mkdir(parents=True)
    (cd / "platform" / "a.py").write_text("x = 1\n")
    (cd / "platform" / "test_a.py").write_text("t = 1\n")
    (cd / "requests").mkdir()
    for s in ("a", "b", "c"):
        (cd / "requests" / f"package_{s}.json").write_text(json.dumps(dict(course=s.upper())))
    (cd / "requests" / "survey_x.json").write_text("{}")
    for s in ("b", "c"):
        (cd / "packages" / s / "raw").mkdir(parents=True)
        (cd / "packages" / s / "raw" / "osm.geojson").write_text("{}")
    monkeypatch.setattr(pc, "ROOT", str(tmp_path))
    monkeypatch.setattr(pc, "PACKAGES", str(cd / "packages"))
    monkeypatch.setattr(pc, "REQUESTS", str(cd / "requests"))
    monkeypatch.setattr(rr, "DEPS", [])
    monkeypatch.setattr(rr, "DATA", [])
    return tmp_path


def actions(changed, **kw):
    return {os.path.basename(p): a for p, a in rr.plan(changed, **kw)}


def test_requests_phase_never_rebuilds(repo):
    a = actions(["course_data/platform/a.py"], phase="requests")
    assert a == {"package_a.json": "fetch", "package_b.json": "skip", "package_c.json": "skip", "survey_x.json": "skip"}
    a = actions(["course_data/requests/package_b.json", "course_data/requests/survey_x.json"], phase="requests")
    assert a["package_b.json"] == "fetch" and a["survey_x.json"] == "survey" and a["package_c.json"] == "skip"
    # the old single step still rebuilds on a code change
    assert actions(["course_data/platform/a.py"])["package_c.json"] == "build"


def test_rebuild_phase_follows_the_build_hash(repo):
    req = lambda s: str(repo / "course_data" / "requests" / f"package_{s}.json")    # noqa: E731
    # nothing recorded: every fetched package is stale, whatever the push touched; unfetched ones are not built
    assert actions([], phase="rebuild") == {"package_a.json": "skip", "package_b.json": "build",
                                            "package_c.json": "build", "survey_x.json": "skip"}
    rec = rr.record_build("b", req("b"), files=[])
    assert rec["files"] == ["course_data/platform/a.py"] and "test_a.py" not in json.dumps(rec)
    rr.record_build("c", req("c"), files=[])
    assert set(actions([], phase="rebuild").values()) == {"skip"}
    # a test-only change keeps them current; a code change or a new module makes them stale
    (repo / "course_data" / "platform" / "test_a.py").write_text("t = 2\n")
    assert "build" not in actions([], phase="rebuild").values()
    (repo / "course_data" / "platform" / "a.py").write_text("x = 2\n")
    assert actions([], phase="rebuild")["package_b.json"] == "build"
    rr.record_build("b", req("b"), files=[])
    rr.record_build("c", req("c"), files=[])
    (repo / "course_data" / "platform" / "new.py").write_text("")
    assert actions([], phase="rebuild")["package_c.json"] == "build"
    os.remove(repo / "course_data" / "platform" / "new.py")
    # a recorded imported module (outside platform/) counts; so does the request file
    (repo / "course_data" / "tees").mkdir()
    (repo / "course_data" / "tees" / "t.py").write_text("y = 1\n")
    rr.record_build("c", req("c"), files=["course_data/tees/t.py"])
    assert actions([], phase="rebuild")["package_c.json"] == "skip"
    (repo / "course_data" / "tees" / "t.py").write_text("y = 2\n")
    assert actions([], phase="rebuild")["package_c.json"] == "build"
    rr.record_build("c", req("c"), files=["course_data/tees/t.py"])
    open(req("c"), "w").write(json.dumps(dict(course="C", tees="White")))
    assert actions([], phase="rebuild")["package_c.json"] == "build"
    # requests handled by the requests phase are left alone
    assert actions(["course_data/requests/package_c.json"], phase="rebuild")["package_c.json"] == "skip"


def test_rebuild_shards_partition_the_packages(repo):
    for s in "defghijk":
        (repo / "course_data" / "requests" / f"package_{s}.json").write_text("{}")
        (repo / "course_data" / "packages" / s / "raw").mkdir(parents=True)
        (repo / "course_data" / "packages" / s / "raw" / "osm.geojson").write_text("{}")
    every = {p for p, a in actions([], phase="rebuild").items() if a == "build"}
    parts = [{p for p, a in actions([], phase="rebuild", shard=(k, 3)).items() if a == "build"} for k in range(3)]
    assert set().union(*parts) == every and sum(map(len, parts)) == len(every) == 10


def test_loaded_code_files_sees_path_loaded_modules():
    files = rr.loaded_code_files()
    assert "course_data/platform/run_requests.py" in files and not any("/test_" in f for f in files)


def test_plan_json_and_args(repo, tmp_path):
    out = tmp_path / "plan.json"
    obj = rr.write_plan(["course_data/requests/package_c.json"], str(out))
    assert obj == dict(requests=["course_data/requests/package_a.json", "course_data/requests/package_c.json"],
                       rebuild=1)                                    # b (c is the requests phase's)
    assert json.load(open(out)) == obj
    a = rr.parse_args(["--phase", "rebuild", "--shard", "1/2", "--commit-every", "4", "x.json"])
    assert a.shard == (1, 2) and a.commit_every == 4 and a.changed == ["x.json"]
    with pytest.raises(SystemExit):
        rr.parse_args(["--shard", "2/2"])


def test_main_commits_every_n(repo, monkeypatch, tmp_path):
    """--commit-every: COMMIT_CMD gets the slugs after every N builds and the rest at the end."""
    import package as pk
    built = []

    def fake_build(p, render=False):
        slug = os.path.basename(p)[len("package_"):-5]
        built.append(slug)
        s = dict(holes_built=18, holes_mapped=18, greens_found=18, tee_boxes=1,
                 holes_with_trees_or_long_grass_in_landing_zone=1, of_par4_5=14, mean_landing_osm_share=0.5,
                 mean_confidence=0.5, osm_score=0.5)
        return dict(slug=slug, stages=dict(vision="ok: vision_any/2"), coverage=dict(summary=s),
                    course=dict(name=slug), tee_set="White", built="now")
    monkeypatch.setattr(pk, "build_request", fake_build)
    for s in "def":
        (repo / "course_data" / "requests" / f"package_{s}.json").write_text("{}")
        (repo / "course_data" / "packages" / s / "raw").mkdir(parents=True)
        (repo / "course_data" / "packages" / s / "raw" / "osm.geojson").write_text("{}")
    log = tmp_path / "calls.txt"
    monkeypatch.setenv("COMMIT_CMD", f"sh -c 'echo \"$*\" >> {log}' commit")
    monkeypatch.setenv("VISION_GATE", str(tmp_path / "gate.txt"))
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
    assert rr.main([], phase="rebuild", commit_every=2) == 0
    assert built == ["b", "c", "d", "e", "f"]
    assert log.read_text().split("\n")[:-1] == ["b c", "d e", "f"]
    assert all(os.path.exists(rr.inputs_path(s)) for s in built)
    assert sorted(json.load(open(os.path.join(pc.PACKAGES, "_index.json")))) == built
    built.clear()
    assert rr.main([], phase="rebuild", commit_every=2) == 0 and built == []        # all current now
    # --only: one request in the requests phase (fetch stubbed)
    import fetch_package as fp
    monkeypatch.setattr(fp, "fetch", lambda p: ("a", "ok"))
    assert rr.main(["course_data/requests/package_a.json", "course_data/requests/package_c.json"],
                   phase="requests", only=["course_data/requests/package_a.json"]) == 0
    assert built == ["a"]


def test_merge_index():
    base = dict(a=1, b=1, c=1)
    tip = dict(a=1, b=2, c=1, d=9)                                     # another job changed b, added d
    mine = dict(a=5, b=1, e=3)                                         # this job: a changed, c removed, e added
    assert merge_index.merge(base, tip, mine) == dict(a=5, b=2, d=9, e=3)


def git(cwd, *a):
    return subprocess.run(["git", "-C", str(cwd), *a], check=True, capture_output=True, text=True).stdout.strip()


@pytest.mark.skipif(not shutil.which("git"), reason="git")
def test_commit_run_parallel_jobs_keep_each_others_index(tmp_path):
    """Two jobs from the same base publish different packages; the second merges _index.json, and a chunk
    commit with slugs publishes only those packages."""
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    seed = tmp_path / "seed"
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    for k, v in (("user.name", "t"), ("user.email", "t@t")):
        git(seed, "config", k, v)
    (seed / "course_data" / "platform").mkdir(parents=True)
    for f in ("commit_run.sh", "commit_packages.sh", "merge_index.py"):
        shutil.copy(os.path.join(HERE, f), seed / "course_data" / "platform" / f)
    pk = seed / "course_data" / "packages"
    (pk / "x").mkdir(parents=True)
    (pk / "x" / "package.json").write_text("{}")
    (pk / "_index.json").write_text(json.dumps(dict(x=dict(status="ok"))))
    git(seed, "add", "-A")
    git(seed, "commit", "-qm", "seed")
    git(seed, "remote", "add", "origin", str(origin))
    git(seed, "push", "-q", "origin", "main")
    base = git(seed, "rev-parse", "HEAD")
    jobs = []
    for name in ("j1", "j2"):
        d = tmp_path / name
        subprocess.run(["git", "clone", "-q", str(origin), str(d)], check=True)
        for k, v in (("user.name", "t"), ("user.email", "t@t")):
            git(d, "config", k, v)
        jobs.append(d)
    msg = tmp_path / "msg.txt"
    msg.write_text("test\n\nBuilt from: x\n")

    def build(d, slug):
        (d / "course_data" / "packages" / slug).mkdir()
        (d / "course_data" / "packages" / slug / "package.json").write_text(json.dumps(dict(slug=slug)))
        ix = d / "course_data" / "packages" / "_index.json"
        idx = json.loads(ix.read_text())
        idx[slug] = dict(status="ok")
        ix.write_text(json.dumps(idx))

    run = lambda d, *slugs: subprocess.run(                            # noqa: E731
        ["bash", "course_data/platform/commit_run.sh", "main", base, str(msg), *slugs], cwd=d,
        capture_output=True, text=True)
    build(jobs[0], "p1")
    build(jobs[0], "p2")
    r = run(jobs[0], "p1")
    assert r.returncode == 0, r.stdout + r.stderr
    build(jobs[1], "q1")
    r = run(jobs[1])
    assert r.returncode == 0, r.stdout + r.stderr
    r = run(jobs[0], "p2")                                              # the next chunk of job 1
    assert r.returncode == 0, r.stdout + r.stderr
    check = tmp_path / "check"
    subprocess.run(["git", "clone", "-q", str(origin), str(check)], check=True)
    idx = json.loads((check / "course_data" / "packages" / "_index.json").read_text())
    assert sorted(idx) == ["p1", "p2", "q1", "x"]
    for s in ("p1", "p2", "q1"):
        assert (check / "course_data" / "packages" / s / "package.json").exists()
    assert git(check, "log", "--format=%s").split("\n") == ["test", "test", "test", "seed"]
