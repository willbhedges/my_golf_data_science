#!/bin/bash
# Commit the packages a course-package run built WITHOUT clobbering newer work on the branch.
#
#   course_data/platform/commit_packages.sh <branch> <base sha> <message file> [paths...]
#
# <base sha> is the commit the run checked out. Every path the run changed (vs base) is published, EXCEPT:
#   * a package directory (course_data/packages/<slug>/) where anything changed on origin since base
#     (another run / workflow rebuilt that package meanwhile): the whole directory is skipped
#   * any other file (packages/_index.json, qa/golden_tees.*) changed on origin since base
# The commit is built on top of the current origin tip in a private index (git read-tree + update-index +
# commit-tree), so no rebase, no -X theirs, and nothing outside the run's own changed paths is touched.
# A rejected push (the branch moved again) re-fetches and re-checks, up to 8 times.
set -u
BR="$1"; BASE="$2"; MSG="$3"; shift 3
PATHS=("$@")
[ ${#PATHS[@]} -gt 0 ] || PATHS=(course_data/packages)
git add -A -- "${PATHS[@]}" 2>/dev/null
CHANGES=$(git diff --cached --name-status "$BASE" -- "${PATHS[@]}")
if [ -z "$CHANGES" ]; then
  echo "No package changes to commit"; exit 0
fi
unit() {  # the unit a path is skipped with: its package directory, else the file itself
  case "$1" in
    course_data/packages/_*) echo "$1" ;;
    course_data/packages/*/*) echo "$1" | cut -d/ -f1-3 ;;
    *) echo "$1" ;;
  esac
}
for i in 1 2 3 4 5 6 7 8; do
  git fetch -q origin "$BR" || { sleep $((i * 10)); continue; }
  TIP=$(git rev-parse FETCH_HEAD)
  MOVED=$(git diff --name-only "$BASE" "$TIP" -- "${PATHS[@]}" | while read -r p; do unit "$p"; done | sort -u)
  export GIT_INDEX_FILE=$(mktemp)
  git read-tree "$TIP"
  n=0; skipped=""
  while IFS=$'\t' read -r st p p2; do
    [ -n "$p" ] || continue
    case "$st" in R*|C*) old="$p"; p="$p2" ;; *) old="" ;; esac
    u=$(unit "$p")
    if printf '%s\n' "$MOVED" | grep -qxF "$u"; then
      skipped="$skipped $u"; continue
    fi
    if [ -n "$old" ] && [ "$st" != "${st#R}" ]; then git update-index --force-remove -- "$old"; fi
    if [ "$st" = "D" ]; then
      git update-index --force-remove -- "$p"
    else
      git update-index --add -- "$p"
    fi
    n=$((n + 1))
  done <<< "$CHANGES"
  [ -n "$skipped" ] && echo "skipped (changed on origin since $BASE):$(printf '%s\n' $skipped | sort -u | tr '\n' ' ')"
  TREE=$(git write-tree)
  rm -f "$GIT_INDEX_FILE"; unset GIT_INDEX_FILE
  if [ "$n" = 0 ] || [ "$TREE" = "$(git rev-parse "$TIP^{tree}")" ]; then
    echo "nothing left to publish"; exit 0
  fi
  C=$(git commit-tree "$TREE" -p "$TIP" -F "$MSG")
  if git push origin "$C:refs/heads/$BR"; then
    echo "published $n path(s) as $C"; exit 0
  fi
  echo "push attempt $i rejected; re-checking"; sleep $((i * 10))
done
exit 1
