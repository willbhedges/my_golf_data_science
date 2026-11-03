"""course_page.py: a failed finish says why in status.json; an all-par-3 card still gets a wind grid."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import course_page as cp  # noqa: E402

# the tail of the gamble_sands finish job in course-page run 41346643978 (Actions log timestamps kept)
GAMBLE_LOG = """\
2026-11-02T02:20:36.2261698Z $ /opt/hostedtoolcache/Python/3.11.17/x64/bin/python3 /home/runner/work/r/r/course_data/courses/v2_course.py merge /tmp/merge_gamble_sands_auto --which auto --slug gamble_sands
2026-11-02T02:20:38.2419734Z Traceback (most recent call last):
2026-11-02T02:20:38.2421545Z   File "/home/runner/work/r/r/course_data/courses/v2_course.py", line 546, in <module>
2026-11-02T02:20:38.2427813Z     grid = json.load(open(os.path.join(v2dir, "wind_grid.json")))
2026-11-02T02:20:38.2429341Z FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/r/r/course_data/library/gamble_sands/auto/v2/wind_grid.json'
2026-11-02T02:20:38.4043085Z Traceback (most recent call last):
2026-11-02T02:20:38.4053981Z   File "/home/runner/work/r/r/course_data/library/course_page.py", line 105, in vc
2026-11-02T02:20:38.4061475Z     raise CalledProcessError(retcode, process.args,
2026-11-02T02:20:38.4064083Z subprocess.CalledProcessError: Command '['/opt/hostedtoolcache/Python/3.11.17/x64/bin/python3', '/home/runner/work/r/r/course_data/courses/v2_course.py', 'page']' returned non-zero exit status 1.
"""


def test_error_lines_keep_the_exceptions_repo_relative():
    e = cp.error_lines(GAMBLE_LOG)
    assert len(e) == 2
    assert e[0] == ("FileNotFoundError: [Errno 2] No such file or directory: "
                    "'course_data/library/gamble_sands/auto/v2/wind_grid.json'")
    assert e[1].startswith("subprocess.CalledProcessError: Command '['python3', 'course_data/courses/v2_course.py'")
    assert "/home/runner" not in " ".join(e) and "hostedtoolcache" not in " ".join(e)


def test_error_lines_without_a_traceback_and_long_lines():
    assert cp.error_lines("step 1\n\nstep 2\nsomething went wrong\n", k=2) == ["step 2", "something went wrong"]
    assert cp.error_lines("") == []
    long = cp.error_lines("ValueError: " + "x" * 1000)[0]
    assert len(long) == 300 and long.endswith("...")
    # the same exception printed twice (a retry) is one reason; only the last k distinct ones are kept
    assert cp.error_lines("KeyError: 'a'\nKeyError: 'a'\nValueError: b\nRuntimeError: c\nOSError: d", k=3) == \
        ["ValueError: b", "RuntimeError: c", "OSError: d"]


def _q(tmp_path):
    return dict(slug="zz_test", name="ZZ Test", state="WA", city="X", group="library", path="r.json",
                out=str(tmp_path / "zz_test"))


def test_failed_records_the_log_errors(tmp_path):
    log = tmp_path / "finish.log"
    log.write_text(GAMBLE_LOG)
    q = _q(tmp_path)
    cp.failed(q, "finish", "merge / page / checks failed", log=str(log))
    st = json.load(open(tmp_path / "zz_test" / "status.json"))
    assert st["status"] == "failed"
    assert st["reasons"][0] == "finish: merge / page / checks failed"
    assert st["reasons"][1].startswith("finish error: FileNotFoundError:") and "wind_grid.json" in st["reasons"][1]
    assert st["reasons"][2].startswith("finish error: subprocess.CalledProcessError:")
    assert "wind_grid.json" in (tmp_path / "zz_test" / "qa_report.md").read_text()
    # no log (the package stage) -> the one reason, as before
    cp.failed(q, "package", "no prepared course", log=str(tmp_path / "missing.log"))
    assert json.load(open(tmp_path / "zz_test" / "status.json"))["reasons"] == ["package: no prepared course"]


def test_cli_failed_takes_log_before_the_positionals(tmp_path, monkeypatch):
    got = {}
    monkeypatch.setattr(cp, "request", lambda p: _q(tmp_path))
    monkeypatch.setattr(cp, "failed", lambda q, stage, msg, log=None: got.update(stage=stage, msg=msg, log=log))
    monkeypatch.setattr(sys, "argv", ["course_page.py", "failed", "--log", "/tmp/f.log", "req.json", "finish",
                                      "merge / page / checks failed"])
    cp.main()
    assert got == dict(stage="finish", msg="merge / page / checks failed", log="/tmp/f.log")


def test_wind_groups_all_par3_card_still_runs_once():
    # Quicksands at Gamble Sands: 14 par 3s, no tee-shot holes -> one process (it writes the par-3 plays-like
    # tables); before, zero processes ran, no wind_grid.json was written and the page step crashed
    assert cp.wind_groups([], 4) == [[]]
    assert cp.wind_groups(["1", "2", "3"], 2) == [["1", "3"], ["2"]]
    assert cp.wind_groups(["1"], 4) == [["1"]]


def test_requested_set_matches_one_part_of_a_slash_name():
    """colbert_hills (qa_rebuild.md): request "Black", OpenGolfAPI card "Black/Blue" (7525) + "Web" (7505): the
    page must solve Black/Blue, not substitute the longest non-combination set."""
    pkg = {"tee_set": "Black/Blue", "tee_sets": {
        "Black/Blue": {"total": 7525, "yards": [434] * 18}, "Web": {"total": 7505, "yards": [414] * 18},
        "Silver": {"total": 7049, "yards": [390] * 18}, "White": {"total": 5883, "yards": [330] * 18}}}
    bases, _, _ = cp.choose_bases(pkg, ["Black", "Silver"])
    assert bases == ["Black/Blue", "Silver"]
    assert cp.choose_bases(pkg, ["Black/Blue", "Silver"])[0] == ["Black/Blue", "Silver"]
    assert cp.choose_bases(pkg, ["Silver"])[0] == ["Silver", "Web"]        # unchanged without a slash match


def test_native_source_needs_agent_layers_and_the_three_mapper_files(tmp_path):
    q = _q(tmp_path)
    assert cp.native_source(q) == (None, "no agent_layers in the request")
    m = tmp_path / "mapper_zz"
    m.mkdir()
    q["agent_layers"] = str(m)
    path, why = cp.native_source(q)
    assert path is None and "frames.json" in why and "agent_zones.geojson" in why
    for f in cp.NATIVE_FILES:
        (m / f).write_text("{}")
    assert cp.native_source(q) == (str(m), None)
    q["native"] = False
    assert cp.native_source(q)[0] is None
    # the committed mapper outputs of eagle_bend (round 4) qualify, by repo-relative path
    assert cp.native_source(dict(agent_layers="course_data/mapper/eagle_bend/"))[0]


def test_native_stage_never_fails_the_build(tmp_path):
    q = _q(tmp_path)
    os.makedirs(q["out"])
    r = cp.native(q)                                    # no agent_layers: noted, no items
    assert r["items"] == [] and r["note"].startswith("not asked")
    m = tmp_path / "mapper_zz"
    m.mkdir()
    for f in cp.NATIVE_FILES:
        (m / f).write_text("{}")
    q["agent_layers"] = str(m)
    r = cp.native(q)                                    # no package / config yet: skipped, recorded
    assert r["items"] == [] and r["note"].startswith("skipped")
    assert json.load(open(tmp_path / "zz_test" / "native.json"))["schema"] == "lib_native/1"
    assert cp.native_summary(q)["holes"] == []


# ---- a failed re-run must not overwrite a good page's entry (tournament_club_iowa, 2026-11-02: an Overpass timeout
# on a later rebuild turned a published "needs confirm" page into "failed", page null, while page.html was still there)
def _good(q, page_bytes=1234):
    os.makedirs(q["out"], exist_ok=True)
    page = os.path.join(q["out"], "page.html")
    open(page, "w").write("x" * page_bytes)
    st = dict(slug=q["slug"], name=q["name"], city=q["city"], state=q["state"], group="library",
              status="needs confirm", reasons=["OSM greens 17 of 18 holes"], check_holes=[7], tee_sets=[{"name": "Blue"}],
              solved_sets=["Blue"], page=os.path.relpath(page, cp.ROOT), page_bytes=page_bytes,
              qa_report=os.path.relpath(os.path.join(q["out"], "qa_report.md"), cp.ROOT), built="2026-10-30T12:33Z")
    cp.wj(os.path.join(q["out"], "status.json"), st)
    open(os.path.join(q["out"], "qa_report.md"), "w").write("# good report\n")
    return st


def test_failed_rerun_keeps_the_last_good_entry(tmp_path):
    q = _q(tmp_path)
    good = _good(q)
    cp.failed(q, "package", "overpass failed: ReadTimeout")
    st = json.load(open(tmp_path / "zz_test" / "status.json"))
    for k in ("status", "page", "page_bytes", "reasons", "check_holes", "tee_sets", "solved_sets", "built", "qa_report"):
        assert st[k] == good[k], k
    la = st["last_attempt"]
    assert la["status"] == "failed" and la["stage"] == "package"
    assert la["error"] == ["package: overpass failed: ReadTimeout"] and la["when"]
    # the good report stays; the failure is in status.json last_attempt
    assert (tmp_path / "zz_test" / "qa_report.md").read_text() == "# good report\n"
    # a second failure replaces last_attempt, never the good record
    cp.failed(q, "finish", "merge / page / checks failed")
    st2 = json.load(open(tmp_path / "zz_test" / "status.json"))
    assert st2["status"] == "needs confirm" and st2["page"] == good["page"]
    assert st2["last_attempt"]["stage"] == "finish"
    # the index lists the page, with the failure beside it
    row = cp.index_row(st2)
    assert row["status"] == "needs confirm" and row["page"] == good["page"] and row["group"] == "library"
    assert row["last_attempt"]["stage"] == "finish"


def test_failed_without_a_page_on_disk_is_a_failure(tmp_path):
    q = _q(tmp_path)
    _good(q)
    os.remove(tmp_path / "zz_test" / "page.html")       # the record says page.html, but it is gone: nothing to keep
    cp.failed(q, "package", "overpass failed")
    st = json.load(open(tmp_path / "zz_test" / "status.json"))
    assert st["status"] == "failed" and st["page"] is None and "last_attempt" not in st
    assert "last_attempt" not in cp.index_row(st)


def test_failed_after_a_failure_stays_failed(tmp_path):
    q = _q(tmp_path)
    cp.failed(q, "package", "a")
    cp.failed(q, "package", "b")
    st = json.load(open(tmp_path / "zz_test" / "status.json"))
    assert st["status"] == "failed" and st["reasons"] == ["package: b"]


# ---- imagery outside NAIP (Anchorage, AK: the package fell back to 10 m Sentinel-2 and the page shipped gray holes)
NAIP_PKG = {"imagery": {"source": "USDA NAIP via Microsoft Planetary Computer (collection 'naip')", "year": 2023,
                        "resolution_m": 0.6}}
S2_PKG = {"imagery": {"source": "Sentinel-2 L2A via Planetary Computer", "year": None, "resolution_m": 10,
                      "acquired": "2026-08-26"}}


def test_imagery_problem_names_non_naip_sources():
    assert cp.imagery_problem(NAIP_PKG) is None
    assert "Sentinel-2" in cp.imagery_problem(S2_PKG) and "NAIP" in cp.imagery_problem(S2_PKG)
    assert cp.imagery_problem({}) is not None
    assert cp.imagery_problem({"imagery": {"source": "USDA NAIP", "resolution_m": 0.6, "present": False}}) is not None


def test_unsupported_imagery_stops_the_build_and_delists_the_page(tmp_path):
    q = _q(tmp_path)
    _good(q)                                  # an earlier build shipped gray pictures: it must not stay listed
    try:
        cp.check_imagery(q, S2_PKG)
        raise AssertionError("check_imagery should stop the build")
    except SystemExit as e:
        assert "Sentinel-2" in str(e.code)
    st = json.load(open(tmp_path / "zz_test" / "status.json"))
    assert st["status"] == "unsupported" and st["page"] is None
    assert any("NAIP" in r for r in st["reasons"])
    assert "unsupported" in (tmp_path / "zz_test" / "qa_report.md").read_text()
    row = cp.index_row(st)
    assert row["status"] == "unsupported" and row["page"] is None
    cp.check_imagery(q, NAIP_PKG)             # NAIP: nothing happens


# ---- wide-aim CHECK on the page (library QA 2026-11-02: Gustin Gold 6 4-wood -60 printed with no CHECK)
def _tee(key, pick, aim, temps=(45.0, 55.0)):
    cell = {pick: [aim, 4.0, aim - 1, aim + 1, 250, 270, 60, 0.0], "Mid iron": [0.0, 4.5, -1, 1, 180, 190, 36, 0.0]}
    return dict(kind="tee", key=key, bearing=0.0, calm=dict(pick=pick, aim=aim, temp=50.0),
                grids={"0": {f"{T:g}": {"0_0": cell, **{f"5_{d}": cell for d in range(0, 360, 30)}} for T in temps}})


def _data():
    return dict(base_set="Black", temps=[45.0, 55.0], speeds=[0, 5], days=["2026-11-07"], forecast=[],
                holes=[_tee("6", "4-wood", -40.0), _tee("7", "Driver", 5.0)],
                alt={"Gold": [_tee("6", "4-wood", -60.0), _tee("7", "Driver", 5.0)]})


def test_wide_aim_is_a_check_on_its_own_set():
    checks = {"auto": dict(set="Black", course=dict(pars_ok=True), holes={"6": dict(status="PASS", reasons=[], checks={}),
                                               "7": dict(status="PASS", reasons=[], checks={})}),
              "auto_b": dict(set="Gold", course=dict(pars_ok=True), holes={"6": dict(status="PASS", reasons=[], checks={}),
                                                "7": dict(status="PASS", reasons=[], checks={})})}
    cp.wide_aim_checks(checks, _data())
    assert [r["status"] for r in checks["auto"]["holes"].values()] == ["PASS", "PASS"]      # -40 is on the bound
    g6 = checks["auto_b"]["holes"]["6"]
    assert g6["status"] == "CHECK" and g6["reasons"] == [
        "wide_aim: 4-wood aim -60 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): "
        "confirm the line on the map"]
    assert checks["auto_b"]["holes"]["7"]["status"] == "PASS"
    pkg = dict(pipeline=dict(holes=dict(method="osm"), profile=dict(osm_greens=18, card=True)),
               holes={str(k): {} for k in range(1, 19)},
               scorecard=dict(kind="web"), stages=dict(vision="ok: vision_any/2"))
    status, reasons, check_holes, _ = cp.course_gate(pkg, checks, {}, {})
    assert status == "needs confirm" and check_holes == [6]


# ---- native cards on the page's own pick (Osage National 15, 2026-11-02: card "now Driver, 60 yds right")
def _item(hole, plans, regret=None):
    regret = regret or {}
    opts = []
    for a in ("L", "R", "both", "none"):
        c, x = plans[a].rsplit(" ", 1)
        opts.append(dict(answer=a, label=a, text="planner text", outcome=dict(pick=c, aim=float(x), regret=regret.get(a, 0.0))))
    return dict(id=f"native_{hole}", hole=hole, plans=plans, options=opts)


def test_native_card_whose_plan_the_page_does_not_play_is_dropped():
    holes = [_tee("15", "Long iron", -1.0), _tee("5", "Driver", -18.5), _tee("11", "Driver", -7.0)]
    rec = dict(items=[
        _item("5", {"current": "Driver -18", "L": "4-wood -5", "R": "Driver -18", "both": "4-wood -5", "none": "Driver -18"},
              {"L": 0.168, "both": 0.168}),
        _item("15", {"current": "Driver +60", "L": "Driver +60", "R": "4-wood +2", "both": "4-wood +5", "none": "Driver +60"},
              {"R": 0.265, "both": 0.245}),
        _item("11", {"current": "Driver -8", "L": "Driver +2", "R": "Driver -8", "both": "4-wood -2", "none": "Driver -8"},
              {"L": 0.047, "both": 0.048})])
    cp.native_reconcile(rec, holes, cap=4)
    assert [it["hole"] for it in rec["items"]] == ["5", "11"]
    assert rec["dropped"][0]["hole"] == "15" and "Long iron -1.0" in rec["dropped"][0]["why"]
    c5 = rec["items"][0]
    assert c5["plans"]["current"] == "Driver -18" and c5["plans"]["planner"] == "Driver -18"
    t = {o["answer"]: o["text"] for o in c5["options"]}
    assert t["L"].startswith("Re-planned: 4-wood, 5 yds left (now Driver, 18 yds left).") and t["R"] == "No change to the plan."
    # every card's "no answer" plan is the page's pick
    for it in rec["items"]:
        h = next(h for h in holes if h["key"] == it["hole"])
        none = next(o for o in it["options"] if o["answer"] == "none")["outcome"]
        assert (none["pick"], none["aim"]) == (h["calm"]["pick"], h["calm"]["aim"])
    c11 = rec["items"][1]                                   # L: Driver +2 is 9 yds from the page's -7: no change
    assert next(o for o in c11["options"] if o["answer"] == "L")["text"] == "No change to the plan."


def test_native_card_with_a_replan_past_the_page_bound_or_no_change_is_dropped():
    holes = [_tee("6", "Driver", -5.5), _tee("2", "Driver", 0.0)]
    rec = dict(items=[
        _item("6", {"current": "Driver -8", "L": "4-wood +20", "R": "Driver -32", "both": "Driver -110", "none": "Driver -18"}),
        _item("2", {"current": "Driver +2", "L": "Driver +4", "R": "Driver -3", "both": "Driver +1", "none": "Driver +2"})])
    cp.native_reconcile(rec, holes, cap=4)
    assert rec["items"] == [] and [d["hole"] for d in rec["dropped"]] == ["6", "2"]


def test_native_cards_capped_after_reconcile():
    holes = [_tee(str(k), "Driver", 0.0) for k in range(1, 7)]
    plans = {"current": "Driver +0", "L": "4-wood +0", "R": "Driver +0", "both": "4-wood +0", "none": "Driver +0"}
    rec = dict(items=[_item(str(k), dict(plans)) for k in range(1, 7)])
    cp.native_reconcile(rec, holes, cap=4)
    assert [it["hole"] for it in rec["items"]] == ["1", "2", "3", "4"] and len(rec["dropped"]) == 2


def test_finish_records_a_lost_package_job():
    """Troon North, run 41539188571: the package runner was shut down mid-job (exit 143), so no lib-<slug>-pkg
    artifact; finish then saw the checkout's OLD status.json, skipped `failed` and committed nothing. The finish
    step must key on whether this run's package artifact arrived, not on a status.json existing."""
    import yaml
    wf = yaml.safe_load(open(os.path.join(HERE, "..", "..", ".github", "workflows", "course_page_one.yml")))
    steps = wf["jobs"]["finish"]["steps"]
    pkg = [s for s in steps if (s.get("with") or {}).get("name") == "lib-${{ inputs.slug }}-pkg"]
    assert len(pkg) == 1 and pkg[0].get("id"), "the package artifact download needs an id"
    merge = next(s for s in steps if s.get("name") == "Merge, page, checks, report")
    assert f"steps.{pkg[0]['id']}.outcome" in merge["run"]
    assert "needs.package.result" in merge["run"]
