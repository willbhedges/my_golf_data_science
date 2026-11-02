# Shared rules for parallel agents (golf pipeline)

Repo: /home/user/my_golf_data_science, branch claude/mozingo-lake-tee-strategy-ef54wl.

- Work in your OWN sparse worktree under the scratchpad (not the main checkout):
    git -C /home/user/my_golf_data_science worktree add --no-checkout <scratch>/wt-<name> origin/claude/mozingo-lake-tee-strategy-ef54wl
    cd <scratch>/wt-<name> && git sparse-checkout set --no-cone <paths you need> && git checkout
  Remove it when done (git worktree remove --force). Keep it small (disk is shared).
- Stage files by explicit path only. Commit messages end with:
    Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
    Claude-Session: https://claude.ai/code/session_011rKvZuUcU769YfPfktPsds
  Never put a model name/ID anywhere else in the repo.
- Push loop: for i in 1..5: git pull --rebase origin <branch> && git push origin HEAD:<branch> && break; sleep.
- Run the relevant tests before every push (don't pipe pytest through tail in a way that hides failures).
- GitHub Actions only via request files under course_data/requests/ (workflow_dispatch is 403). web_fetch.yml now
  fetches every webfetch_*.json changed by your push. Do NOT push course_page_* / course_batch_* request files unless
  your brief says so (they start long builds that share 20 runners); hand them to the coordinator instead.
- Off limits: course_data/courses/* (tournament pages), spirit_hollow/ (read-only), course_data/app/ (unless your
  brief is the app). No publishing artifacts.
- Sandbox can't reach OSM/Overpass/imagery hosts directly; use cached data in the repo or a web_fetch request.
- Set OMP_NUM_THREADS=1 for tree-model fits on the shared box.
- Final report: short, honest numbers (say what was NOT verified), files and commits.

- Scoring (error_budget.py, eval_mapper.py, eval_native_confirm.py, any planner numbers you report) must run in the FULL checkout or a full worktree. A sparse checkout missing course_data/elevation, library, vision_any/s2 or spirit_hollow/ silently changes planner scores (found 2026-11-02). Blind mapper worktrees stay sparse; the coordinator scores them in the full checkout.
