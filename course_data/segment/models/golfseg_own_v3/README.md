# golfseg_own_v3: our NAIP golf-feature U-Net, tee-targeted fine-tune of v2

* Source: GitHub Actions run 44731500659 (`.github/workflows/golfseg_v2_train.yml`, request rev 5, CPU runners, two
  chained jobs: steps 0-5041 in 317.2 min; steps 5041-8467 in 126.5 min), artifact `golfseg-v2-model`; copied by `.github/workflows/import_golfseg_v3.yml`.
* File: `model.safetensors`, 48946068 bytes, sha256 `a99d62b938a7823c29e5446d757171bae833726603fafb4fd288c04fcb5f1745`.
* Architecture and input: unchanged from `../golfseg_own` / `../golfseg_own_v2` (same normalisation), so
  `fastc/perception/unet.py` runs it as is.
* Initialisation: `../golfseg_own_v2`. Training: `course_data/segment/train/train_v2.py` with
  `--tee-focus {'small': 2.0, 'wood': 4.0, 'exec': 2.5, 'short': 1.5}` (tee crop centres on small / wooded tees, course picks on par-3 / exec /
  short courses), `--tee-min 1.0`, `--select green,tee`; 8467 of 8467 planned
  steps, lr 0.0001. Exported: step 4500 (best validation IoU of the --select classes).
* Training data: the v2 set (data run 44408172242, `dataset_index_v2.json`) + 1404 new courses built of
  1510 drawn (`pick_v3.py`: v2's draw with v2_courses.json also excluded, 1.5 km buffer;
  `dataset_index_v3.json`, data run 44730428783); 2661 training courses in all. Labels
  OpenStreetMap (ODbL 1.0), imagery USDA NAIP (public domain), tree masks Meta / WRI canopy height (CC BY 4.0).
* Validation (120 held-out courses, 512 px tiles), IoU: init (v2) green 0.7024, tee 0.3603, fairway 0.7074, bunker 0.5121, water 0.7515, mean 0.6067; exported green 0.7188, tee 0.383, fairway 0.7135, bunker 0.5256, water 0.7632, mean 0.6208.
* Licence: ours (trained by this project). The ariadgolf/golf-course-segmentation weights are a different model
  and are not in this repository.
* Used by: `course_data/platform/fastpath/fastscene.py` when FASTSCENE_UNET_MODEL=v3 (opt-in).
