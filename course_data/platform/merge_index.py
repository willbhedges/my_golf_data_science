"""Three-way merge of packages/_index.json for commit_packages.sh (parallel course-package jobs all write it).

  python course_data/platform/merge_index.py <base sha> <tip sha> <path>   -> merged JSON on stdout

Start from the origin tip's index and apply this run's own edits (working file vs the run's base commit): an
entry the run added / changed replaces the tip's, an entry the run removed is dropped unless the tip changed it.
Entries other jobs wrote meanwhile are kept. Exit 1 (caller skips the file) when a side is not a JSON object.
"""
import json
import subprocess
import sys


def at(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else {}


def merge(base, tip, mine):
    out = dict(tip)
    for k, v in mine.items():
        if base.get(k) != v:
            out[k] = v
    for k in base:
        if k not in mine and k in out and out[k] == base[k]:
            del out[k]
    return out


def main(base_rev, tip_rev, path):
    base, tip = at(base_rev, path), at(tip_rev, path)
    with open(path) as fh:
        mine = json.load(fh)
    if not all(isinstance(x, dict) for x in (base, tip, mine)):
        return 1
    json.dump(merge(base, tip, mine), sys.stdout, indent=1)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
