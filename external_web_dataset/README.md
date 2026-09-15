# External Web Dataset

This directory documents the external web-image collection used in the Wadi Degla plant-identification project.

## Overview

The external web dataset contains **5,815 plant images** representing the same 32 target plant species used in the study.

Images were obtained from three documented online biodiversity sources:

- **Plants of the World Online (POWO)** — 191 images
- **Global Biodiversity Information Facility (GBIF)** — 4,893 images
- **Pl@ntNet** — 731 images

The images were manually searched, reviewed, selected, and downloaded individually. Before downloading an image, its availability under an open Creative Commons license was checked.

No automated collection script or bulk-download pipeline was used.

The externally sourced image files themselves are **not redistributed** in this repository.

## Public Metadata

### `metadata/external_web_image_composition_by_source.csv`

This CSV provides the public species-level composition of the external web dataset by documented source.

For each of the 32 target species, it reports the number of images obtained from:

- POWO
- GBIF
- Pl@ntNet

together with the per-species total.

The table was derived directly from the retained project summary record. Repeated rows for the same species and source were aggregated, source combinations absent from the retained count table were represented as zero counts, and per-species totals were calculated directly from the three source-count columns.

The final dataset composition is:

- **32 target species**
- **POWO:** 191 images
- **GBIF:** 4,893 images
- **Pl@ntNet:** 731 images
- **Total:** 5,815 images

## Source-Label Standardization

In the retained historical summary, the POWO source is labeled **`Kew`**.

In the public metadata, this source is reported as **POWO**, consistent with the terminology used in the manuscript.

This standardization changes only the source label; the numerical values remain unchanged.

## Scientific Names

The public metadata uses the accepted full scientific names adopted for current botanical reporting.

Historical source and model-class names remain preserved in the internal project records for reproducibility.

For example, the historical label:

`Salsola imbricata Forssk.`

is reported publicly under the accepted scientific name:

`Caroxylon imbricatum (Forssk.) Moq.`

## Rights and Redistribution

During the original manual collection workflow, images were selected only after checking that they were available under an open Creative Commons license.

The detailed Creative Commons subtype for each individual image was not retained in the surviving project summary record.

Only documentation and aggregate metadata are published in this repository.

The external web images themselves are **not redistributed**.
