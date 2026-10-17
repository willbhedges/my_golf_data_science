"""Green close-ups for the page: NAIP 2023 around each green, turned so the approach plays up the image,
with every polygon of output/approach.json re-projected into that image.

  python3 spirit_hollow/approach/views.py    -> output/green_views.json

Most greens sit outside the wind page's tee-shot crop (and several are above the screenshot's top edge),
so a page that wants to draw the target boxes needs its own green image. Per hole:
  img (JPEG data URI), w, h, ypp (yards per image px), the view's `from` point (where the approach is
  played from: the median tee ball on par 4s, the lay-up target on par 5s), and, in image px:
  green, boxes[lie][wind] (shape + aim), go_boxes (par 5), sg_best, go_target / layup targets if in view.
"""
import base64
import io
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "..", "course_data", "imagery")]

import render as R                              # noqa: E402

SRC = os.path.join(HERE, "output", "approach.json")
OUT = os.path.join(HERE, "output", "green_views.json")
NAIP = os.path.join(HERE, "..", "..", "course_data", "imagery", "spirit_hollow")
HALF = 45.0          # yds shown each side of the green centre
PPY = 4.0            # image px per yd


def view(hole_rec, img):
    centre = np.array(hole_rec["green"]["centre"]["ll"][0])
    frm = np.array(hole_rec["box_from"]["ll"][0])
    size = int(2 * HALF * PPY)
    # a Frame whose "tee" is the approach start and whose aim is the green centre: forward = up
    probe = R.Frame(frm, centre, ppy=PPY, tee_px=(0, 0), size=(size, size))
    dist = float(-probe.ll_to_yds(centre[None])[0, 1])
    fr = R.Frame(frm, centre, ppy=PPY, tee_px=(size / 2, size / 2 + dist * PPY), size=(size, size))
    rgb, info = R.render(fr, img)
    from PIL import Image
    im = Image.fromarray(np.asarray(rgb)[..., :3].astype(np.uint8))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=80, optimize=True)
    uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

    def px(geo):
        return [[round(float(a), 1), round(float(b), 1)] for a, b in fr.ll_to_px(np.array(geo["ll"]))]

    out = dict(img=uri, w=size, h=size, ypp=1 / PPY, from_dist=round(dist, 1), green=px(hole_rec["green"]["osm"]),
               imagery=dict(date=info.get("imagery_date"), source=info.get("imagery_source")))
    for name in ("boxes", "go_boxes"):
        if name in hole_rec:
            out[name] = {lie: {w: dict(shape=px(b["shape"]), aim=px(b["aim"])[0], play=b["play"], lo=b["lo"], hi=b["hi"])
                               for w, b in by_w.items()} for lie, by_w in hole_rec[name].items()}
    sg = hole_rec.get("sg_check")
    if sg:
        out["sg_best"] = px(sg["best"])[0]
        out["recommend"] = sg["recommend"]
        if sg.get("sg_box"):
            out["sg_box"] = px(sg["sg_box"])
    for name in ("go_target", "layup"):
        if name in hole_rec:
            p = px(hole_rec[name]["target"])[0]
            if 0 <= p[0] <= size and 0 <= p[1] <= size:
                out[name] = dict(target=p, zone=px(hole_rec[name]["zone"]))
    return out


def main():
    data = json.load(open(SRC))
    img = R.Imagery(NAIP)
    views = {k: view(h, img) for k, h in data["holes"].items()}
    with open(OUT, "w") as f:
        json.dump(dict(doc=__doc__.strip().splitlines()[0], half_yd=HALF, ppy=PPY, holes=views), f,
                  separators=(",", ":"))
    print("wrote", OUT, f"{os.path.getsize(OUT) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
