---
library_name: segmentation-models-pytorch
pipeline_tag: image-segmentation
language:
- en
tags:
- golf
- aerial-imagery
- remote-sensing
- semantic-segmentation
- unet
- resnet34
- naip
- multispectral
- pytorch
- safetensors
---

# Ariad Golf Course Segmentation

A six-class semantic segmentation model for golf-course features in four-band aerial imagery. This is Ariad's **v4** U-Net with a ResNet-34 encoder, exported from the archived Supabase checkpoint into native Hugging Face / Segmentation Models PyTorch format.

The model predicts background, putting greens, tees, fairways, bunkers, and water. It is strongest on greens; water predictions are unreliable. This repository contains the model and inference utilities, not the imagery or training dataset.

## Model details

| Property | Value |
|---|---|
| Architecture | U-Net, ResNet-34 encoder |
| Input | Four bands, **red, green, blue, near-infrared**, in that order |
| Tile size | 512 × 512 pixels |
| Imagery scale | 0.6 ground metres per pixel |
| Raw values | uint8, 0–255 |
| Outputs | Six unnormalized logits per pixel |
| Stored weights | FP16 Safetensors; converted to FP32 for the CPU usage below |
| Training | 4,665 tiles from 790 courses; 573 validation tiles |
| Training run | v4, 14 scheduled epochs; selected checkpoint is epoch 13 (one-based) |

| Class ID | Label |
|---|---|
| 0 | background |
| 1 | green |
| 2 | tee |
| 3 | fairway |
| 4 | bunker |
| 5 | water |

## Load and run

Install `requirements.txt` from this repository for the exact environment used to verify this export. The model loads through the library's standard Hub integration and does not require `trust_remote_code`.

```python
import json
import numpy as np
import rasterio
import segmentation_models_pytorch as smp
import torch
from huggingface_hub import hf_hub_download

repo_id = "ariadgolf/golf-course-segmentation"
model = smp.from_pretrained(repo_id).float().eval()
with open(hf_hub_download(repo_id, "preprocessor_config.json")) as handle:
    config = json.load(handle)

with rasterio.open("tile.tif") as source:
    image = source.read()
assert image.shape == (4, 512, 512) and image.dtype == np.uint8
mean = np.asarray(config["image_mean"], dtype=np.float32)[:, None, None]
std = np.asarray(config["image_std"], dtype=np.float32)[:, None, None]
x = torch.from_numpy((image.astype(np.float32) - mean) / std).unsqueeze(0)
with torch.inference_mode():
    probabilities = model(x).softmax(dim=1)
    mask = probabilities.argmax(dim=1)[0].numpy().astype(np.uint8)
```

Normalization is `(raw_pixel - mean) / std`, using means `[108.314, 118.389, 97.68, 158.925]` and standard deviations `[42.693, 38.205, 33.022, 51.632]`. **Do not divide by 255 first.** Ordinary RGB images are insufficient: the fourth band must be near-infrared, not alpha. Do not substitute standard ImageNet normalization.

The included CLI averages identity, horizontal-flip, and vertical-flip probabilities by default, preserves the input georeferencing, and writes a single-band class raster with nodata value 255:

```bash
python inference.py tile.tif mask.tif
python inference.py tile.tif mask.tif --device mps
```

Use `--model /path/to/downloaded/model` for an offline local snapshot, `--revision COMMIT_SHA` to pin a Hub revision, and `--no-tta` for a single forward pass. Inputs must be four-band uint8 512 × 512 tiles at the expected ground resolution. Larger rasters need overlapping tiling and probability blending before polygonization. Ground resolution must account for projection distortion; map-coordinate metres are not always ground metres.

## Recorded evaluation

These are historical results for the original v4 checkpoint, **not a new evaluation of the exported FP16 model**. The export preserves all tensor values from the stored checkpoint. Most evaluation references are OpenStreetMap outlines, so the scores measure OSM agreement, not surveyed accuracy. Object metrics include the original tiling, augmentation, stitching, and polygon-filtering pipeline; the simple argmax usage above does not reproduce that entire pipeline.

| Green-object evaluation | Courses | Reference greens | Recall at IoU ≥ 0.5 | Precision at IoU ≥ 0.5 | Mean IoU over references |
|---|---:|---:|---:|---:|---:|
| Matched held-out courses | 99 | 1,552 | 88.27% | 79.24% | 0.7283 |
| Held-out states | 40 | 805 | 90.31% | 83.47% | 0.7616 |
| OSM validation | 27 | 528 | 87.88% | 86.41% | 0.7303 |

On 148 negative tiles, the original pipeline returned two green candidates, or 0.14 candidates/km². At the selected checkpoint, recorded validation pixel IoUs were green 0.693, tee 0.331, fairway 0.636, bunker 0.563, and water 0.034. These pixel metrics use a different evaluation procedure from the green-object metrics.

A reviewed set contains 175 scorable greens. Model mean IoU was 0.8469 versus 0.9335 for OSM. The references reuse OSM geometry for 136 of those greens, giving OSM perfect agreement on that subset by construction. This is not a fully independent benchmark. The historical review-parity criterion was not met. Full aggregate records are in `evaluation.json`.

## Training data and limitations

Training used USDA NAIP aerial imagery retrieved through USGS The National Map, paired with OpenStreetMap golf-feature labels. Training splits were course-based, with additional geographic and deployment-matched holdouts. The source runbook describes state-level holdouts in AZ, CO, GA, IA, and OR and exclusion of the NYC metro area from training. Counts above come from the saved v4 configuration and evaluations.

OSM labels can be missing or inaccurate, especially tees and water. The training objective includes partial-label cross-entropy and multiclass Dice with class-dependent label trust. Appearance shifts from imagery vintage, shadows, dormant turf, trees, and geography can reduce accuracy. Water output should not be used as authoritative hazard geometry. Predictions require imagery review before mapping or navigation use; the network supplies no hole numbering, routing, tee ratings, or surveyed boundaries.

## Provenance and licensing

`provenance.json` records the source checkpoint hash and export metadata. Weights were copied without retraining or changes to their stored tensor values. The original Supabase artifacts remain intact.

Imagery source: [USDA NAIP / USGS The National Map](https://www.usgs.gov/programs/national-geospatial-program/national-map). Labels: © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), under ODbL 1.0. Library: [Segmentation Models PyTorch](https://github.com/qubvel/segmentation_models.pytorch).

No additional license grant for the model weights is specified in this release. Public download availability does not by itself assign a model license; upstream imagery, label, and software terms remain separate.
