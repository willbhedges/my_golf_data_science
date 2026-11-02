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
