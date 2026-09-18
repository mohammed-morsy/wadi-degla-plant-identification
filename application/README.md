# Wadi Degla AI Plant Identifier

This folder contains the reviewed Stage 7 application package for the Wadi Degla plant-identification study.

## Current application model

The application uses the selected MobileNetV2 Top-30 checkpoint 215 (`model_top_30_215.pkl`).

The model has 33 output classes:
- 32 target Wadi Degla plant species
- 1 non-target `others` class

The historical model-class mapping is preserved for reproducibility. User-facing botanical reporting uses accepted names where required; the historical model class `Salsola imbricata Forssk.` is reported as `Caroxylon imbricatum (Forssk.) Moq.`.

Model selection was performed during the documented development/final-analysis workflow. Common Web was used for model selection and is not an independent final test set.

## Included files

- `wadi_degla_hosting_ready_v6_top30_215_species_json_confusion.py` — current Dash application source.
- `model_top_30_215.pkl` — selected application model.
- `phase2_selected_model.json` — selected-model provenance and evaluation-preprocessing record.
- `idx_to_class_data.pkl` — historical 33-class index mapping.
- `requirements_wadi_degla.txt` — Python package requirements.
- `assets/` — 32 species metadata JSON files, POWO links, Wadi image, and source logos.
- `App screenshots/A.png` — current Figure 7 panel (a): upload and identification result.
- `App screenshots/B.png` — current Figure 7 panel (b): Species and User Guide with Model Confusion Insights.

## Input preprocessing

Uploaded images are converted to RGB and evaluated using Resize(256), CenterCrop(224), tensor conversion/scaling, and ImageNet normalization with mean `[0.485, 0.456, 0.406]` and standard deviation `[0.229, 0.224, 0.225]`.

## Model Score

The interface displays a softmax-derived Model Score for the uploaded image. It is a model output and is not presented as a calibrated probability.

## `others` class

`others` is an ordinary model class. No separate confidence threshold forces prediction of `others`; it is returned when it has the highest model output.

## Top Alternative Prediction

Top Alternative Prediction is image-specific. It is the second-ranked class from the current uploaded image and is displayed only when its score reaches the 5% display threshold.

## Likely Confused Species

Likely Confused Species is not an additional prediction for the current image.

For each target species, the corresponding species metadata JSON stores:

`confusion.likely_confused_species`

These names summarize the target species most often misclassified as the displayed class by the selected Top-30/215 model on the WadiDegla model dataset validation set. Only species names needed by the interface are retained in the per-species JSON files; confusion counts are not used by the application.

## Supported uploads

The reviewed application accepts JPEG/JPG, PNG, and WebP images with a maximum upload size of 20 MB.

## Runtime device selection

The application uses CUDA when available, otherwise Apple Metal Performance Shaders (MPS) when available, otherwise CPU. The reviewed local run used MPS on an Apple M1 system.

## Run locally

```bash
python3 -m pip install -r requirements_wadi_degla.txt
python3 wadi_degla_hosting_ready_v6_top30_215_species_json_confusion.py
