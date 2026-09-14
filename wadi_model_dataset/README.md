# WadiDegla model dataset

## Overview

This directory contains the reproducibility and methodological records for the WadiDegla model dataset used in the plant-identification study.

The WadiDegla model dataset contains 32 target plant species and one non-target `others` class, giving 33 model classes and 22,564 images in total.

The WadiDegla field dataset contains 22,064 images representing 32 target plant species. The `others` class contains 500 external plant images derived from PlantNet-300K and is included only in the WadiDegla model dataset.

## WadiDegla model dataset training and validation sets

The WadiDegla model dataset contains:

- 17,364 images in the WadiDegla model dataset training set
- 5,200 images in the WadiDegla model dataset validation set

For the 32 target plant species:

- For 22 species, the WadiDegla model dataset training set and WadiDegla model dataset validation set were separated by collection date.
- For 9 species, images were assigned between the WadiDegla model dataset training set and WadiDegla model dataset validation set using image-level random splitting.
- For 1 species, the WadiDegla model dataset training set and WadiDegla model dataset validation set were separated by sampling site.

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

The `others` class is part of the WadiDegla model dataset.

The 500 PlantNet-300K-derived images used for this class are not part of the WadiDegla field dataset and will not be redistributed in the public WadiDegla field dataset package.

## Public WadiDegla field dataset

The images in the WadiDegla field dataset are not stored in this GitHub repository.

The planned public release of the WadiDegla field dataset is `WadiDegla v1.0`, using resized copies hosted in a dedicated data repository.

The final repository platform, resize dimensions, license, metadata schema, and DOI arrangements remain publication dependencies.
