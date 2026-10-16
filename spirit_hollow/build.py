"""Build the Spirit Hollow strategy book and aim sheets.

  python3 spirit_hollow/build.py           -> output/Spirit_Hollow_Strategy.pdf + _Aim_Sheets.pdf
  python3 spirit_hollow/build.py --stats   -> also re-runs the confidence numbers first (~15 min)

Uses the same model and book builder as mozingo/.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "mozingo"))
sys.path.insert(0, HERE)

import course                     # noqa: E402
import stats                      # noqa: E402
import yardage_book as yb         # noqa: E402


def setup():
    yb.use_course("Spirit Hollow GC", HERE, "Spirit_Hollow", course.HOLES, course.PAR3,
                  course.NOTES, course.AIM_AT, course.ORDER, course.LABELS)


if __name__ == "__main__":
    setup()
    if "--stats" in sys.argv:
        stats.main(out=os.path.join(HERE, "output", "stats_report.md"), title="Spirit Hollow", deep=None)
    yb.build()
