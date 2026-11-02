#!/bin/bash
# Publish what a course-package job built (commit_packages.sh does the no-clobber commit on the origin tip).
#
#   course_data/platform/commit_run.sh <branch> <base sha> <message file> [slug...]
#
# With slugs: only those packages (course_data/packages/<slug>/), their vision layer files + OB evidence, and
# packages/_index.json (merged with the tip's, merge_index.py) - run_requests.py --commit-every calls it per
# chunk. Without: every package directory, vision layer and OB evidence the job changed. qa/golden_tees.* ride
# along whenever they exist.
set -u
BR="$1"; BASE="$2"; MSG="$3"; shift 3
cd "$(git rev-parse --show-toplevel)"
P=""
if [ $# -gt 0 ]; then
  P="course_data/packages/_index.json"
  for s in "$@"; do [ -d "course_data/packages/$s" ] && P="$P course_data/packages/$s"; done
  DIRS=""
  for s in "$@"; do [ -d "course_data/vision_any/$s" ] && DIRS="$DIRS course_data/vision_any/$s/"; done
else
  [ -d course_data/packages ] || { echo "nothing built"; exit 0; }
  P="course_data/packages"
  DIRS=$(ls -d course_data/vision_any/*/ 2>/dev/null)
  du -sh course_data/packages/* 2>/dev/null | sort -h | tail -5 || true
fi
for f in course_data/qa/golden_tees.json course_data/qa/golden_tees.md; do [ -e "$f" ] && P="$P $f"; done
# the vision layers + OB evidence built this run (build_layers.committed_paths; never raw2/)
for d in $DIRS; do
  s=$(basename "$d")
  for f in raw vision_any.geojson vision_any_v2.geojson vision_any_v1.geojson layers_v2.tif classes_v2.jpg; do
    [ -e "$d$f" ] && P="$P $d$f"
  done
  [ -d "course_data/ob/$s" ] && P="$P course_data/ob/$s"
done
# shellcheck disable=SC2086
exec bash course_data/platform/commit_packages.sh "$BR" "$BASE" "$MSG" $P
