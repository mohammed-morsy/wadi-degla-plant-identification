# Wadi Degla Image Dataset

## Overview

This directory contains the reproducibility and methodological records for the Wadi Degla image dataset used in the plant-identification study.

The model dataset contains 32 target plant species and one non-target `others` class, giving 33 model classes and 22,564 images in total.

The 32 target species comprise 22,064 field images. The `others` class contains 500 PlantNet-300K-derived images.

## Train/Validation Split

The complete model dataset contains:

- 17,364 training images
- 5,200 validation images

For the 32 target plant species:

- 22 species were split using date-separated Train/Validation subsets.
- 9 species were split using image-level random splitting.
- 1 species was split using site-separated Train/Validation subsets.

Image-level random splitting used `seed = 42`.

The `others` class was split programmatically into 400 training images and 100 validation images using `seed = 42`.

## Repository Contents

### `notebooks/`

The notebooks are preserved as historical execution and methodological evidence.

They document the original dataset-construction and preparation workflow and retain their stored outputs. They are not intended to serve as one-click Run-All reconstruction pipelines.

### `metadata/`

Contains the primary machine-readable records describing:

- per-species Train/Validation composition and split strategy;
- overall split methodology;
- historical model-class indices and names together with accepted botanical names.

Historical model-class names and indices are preserved exactly for reproducibility.

### `validation/`

Contains compact verification records for:

- the final `others` Train/Validation composition and cross-split duplicate-content check;
- the exact species-name overlap audit between the Wadi Degla target species and PlantNet species records.

## Relationship to Stage 1

Fieldwork and botanical-identification metadata already documented under `fieldwork_botany/` remain authoritative and are not duplicated here.

In particular:

- `../fieldwork_botany/metadata/species_summary.csv`
- `../fieldwork_botany/metadata/field_visits.csv`

Stage 2 adds dataset-construction, splitting, class-identity, and validation records specific to the image-dataset stage.

## Non-target `others` Class

The `others` class is part of the experimental model dataset.

The 500 PlantNet-300K-derived images used for this class will not be redistributed in the public Wadi Degla dataset package.

## Public Image Dataset

The Wadi Degla image files themselves are not stored in this GitHub repository.

The planned public image release is `WadiDegla v1.0`, using resized copies hosted in a dedicated data repository.

The final repository platform, resize dimensions, license, metadata schema, and DOI arrangements remain publication dependencies.
