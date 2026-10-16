"""Probe the ariadgolf/golf-course-segmentation model on the Hugging Face Hub (runs on Actions).

Writes course_data/segment/model_card/: info.json (licence, tags, files, sha), README.md, config files.
Hugging Face is blocked from the sandbox, so this is how we read the card.
    python course_data/segment/probe_model.py [--repo ariadgolf/golf-course-segmentation]
"""
import argparse
import json
import os
import sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_card")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="ariadgolf/golf-course-segmentation")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    from huggingface_hub import HfApi, hf_hub_download
    os.makedirs(a.out, exist_ok=True)
    api = HfApi()
    info = {"repo": a.repo}
    try:
        mi = api.model_info(a.repo, files_metadata=True)
        info.update({
            "sha": mi.sha, "last_modified": str(mi.last_modified), "tags": mi.tags,
            "library": getattr(mi, "library_name", None), "pipeline_tag": getattr(mi, "pipeline_tag", None),
            "card_data": mi.card_data.to_dict() if mi.card_data else None,
            "license": (mi.card_data.to_dict().get("license") if mi.card_data else None),
            "gated": getattr(mi, "gated", None), "downloads": getattr(mi, "downloads", None),
            "files": [{"name": s.rfilename, "size": s.size} for s in (mi.siblings or [])],
        })
    except Exception as e:  # noqa: BLE001
        info["error"] = repr(e)
        print("model_info failed:", e, file=sys.stderr)
    for f in info.get("files", []):
        n = f["name"]
        if n.lower().endswith((".md", ".json", ".yaml", ".yml", ".txt", ".py", ".cfg")) or "licen" in n.lower():
            if (f.get("size") or 0) > 2_000_000:
                continue
            try:
                p = hf_hub_download(a.repo, n)
                dst = os.path.join(a.out, n.replace("/", "__"))
                with open(p, "rb") as src, open(dst, "wb") as d:
                    d.write(src.read())
            except Exception as e:  # noqa: BLE001
                print("download failed", n, e, file=sys.stderr)
    with open(os.path.join(a.out, "info.json"), "w") as fh:
        json.dump(info, fh, indent=1, default=str)
    print(json.dumps(info, indent=1, default=str)[:4000])


if __name__ == "__main__":
    main()
