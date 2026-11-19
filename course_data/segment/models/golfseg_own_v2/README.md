# golfseg_own_v2: our NAIP golf-feature U-Net, national fine-tune

* Source: GitHub Actions run 44417856467 (`.github/workflows/golfseg_v2_train.yml`, CPU runners, two chained jobs:
  steps 0-3783 in 316.2 min; steps 3783-6353 in 96.1 min), artifact `golfseg-v2-model`; copied by `.github/workflows/import_golfseg_v2.yml`.
* File: `model.safetensors`, 48946068 bytes, sha256 `d0ed0fc16645a1a511415da4b7a446f9932ab25c664d334f74d36a394aaa3ffe`.
* Architecture and input: unchanged from `../golfseg_own` (segmentation_models_pytorch Unet, ResNet-34, 4 bands
  R, G, B, NIR NAIP 0.6 m uint8, 6 classes background / green / tee / fairway / bunker / water, the same
  image_mean / image_std in `preprocessor_config.json`), so `fastc/perception/unet.py` runs it as is.
* Initialisation: `../golfseg_own` (our v1, run 38987845450). Training: `course_data/segment/train/train_v2.py`,
  6353 of 6353 planned steps (320 px crops, batch 8, AdamW lr 0.0002 warm-up + cosine),
  class-balanced crop centres [0.2, 0.3, 0.1, 0.15, 0.25] (green, tee, fairway, bunker, water), cross-entropy weights
  [0.176, 1.38, 1.842, 0.433, 1.717, 1.025] + 0.5 x soft Dice. Exported: step 3783
  (best mean validation IoU).
* Training data: NAIP (USDA, public domain, via Microsoft Planetary Computer) with OpenStreetMap golf polygons
  as labels (ODbL 1.0): 1329 training courses in 49 states
  (1383 built of 1500 drawn, `course_data/segment/train/dataset_index_v2.json`; drawn by
  `pick_v2.py` with every validation-set, blind20 / TEST-40, perception pool and TRAIN-BIG course and a 1.5 km
  buffer around them excluded).
* Validation (54 held-out courses of the same draw, 512 px tiles), IoU: init (v1) green 0.6473, tee 0.3306, fairway 0.6312, bunker 0.4933, water 0.6023, mean 0.5409;
  exported green 0.6887, tee 0.3517, fairway 0.6874, bunker 0.5262, water 0.7466, mean 0.6001.
* Licence: ours (trained by this project; encoder start ImageNet ResNet-34 via v1, torchvision BSD-3). The
  ariadgolf/golf-course-segmentation weights are a different model and are not in this repository.
* Used by: `course_data/platform/fastpath/fastscene.py` (FASTSCENE_UNET_MODEL) through
  `course_data/platform/fastc/perception/unet.py`.
