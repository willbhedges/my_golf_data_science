# golfseg_own: our own NAIP golf-feature U-Net

* Source: GitHub Actions run 38987845450 (`.github/workflows/segment_train.yml`, 2026-10-17, 4 h 58 min on a CPU
  runner), artifact `golfseg-own-model`; copied by `.github/workflows/import_golfseg_own.yml`.
* File: `model.safetensors`, 48946068 bytes, sha256 `c6607d8c3b9eb4b853ae47ef63c40e3b44093dac3fef4baca66d60d32041f3fc`.
* Architecture: segmentation_models_pytorch Unet, ResNet-34 encoder (ImageNet start), 4 bands R, G, B, NIR (NAIP
  0.6 m, uint8), 6 classes background / green / tee / fairway / bunker / water; normalisation and tile size in
  `preprocessor_config.json` / `train_log.json` (mean / std of the training tiles).
* Training data: NAIP (USDA, via Microsoft Planetary Computer) with OpenStreetMap golf polygons as labels
  (ODbL 1.0), well-mapped Iowa / Missouri courses (`course_data/segment/train/dataset_index.json`); 320 px crops,
  batch 8, 6407 steps.
* Validation (held-out courses of the same states): IoU green 0.717, tee 0.426, fairway 0.774, bunker 0.551, water 0.793.
* Licence: ours (trained by this project). The ariadgolf/golf-course-segmentation weights are a different model
  and are not in this repository (no licence grant).
* Used by: `course_data/platform/fastc/perception/unet.py` (forward pass without torch) through
  `course_data/platform/fastpath/fastscene.py`.
