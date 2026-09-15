# Architecture Screening

This directory documents the architecture-screening experiment used to compare three candidate convolutional neural-network architectures on the WadiDegla model dataset:

- VGG16
- ResNet18
- MobileNetV2

The comparison was used to support selection of the architecture carried forward to subsequent model-development stages.

## Repository Contents

### `notebooks/`

Contains the historical execution and analysis notebooks used during architecture screening.

The notebooks preserve the original experimental logic, directory references, and stored historical outputs.

### `outputs/summary_metrics/`

Contains the retained epoch-level training and validation summary CSV files for the three candidate architectures.

### `figures/`

Contains the approved high-resolution visual outputs generated from the retained summary metrics using the analysis notebook.

## Historical Directory Structure

The notebooks retain the original directory structure used during the architecture-screening experiments.

In particular, the historical `Comparison/mobilenetv2/` path contains summary outputs associated with MobileNetV2, ResNet18, and VGG16.

This directory name is preserved for reproducibility and should not be interpreted as indicating that every file under that path belongs exclusively to MobileNetV2.

## Experimental Execution

The three candidate architectures were evaluated using the same experimental configuration and reproducibility settings.

Each architecture was run in a separate execution session.

## Metric Scales

In the retained summary files:

- training macro precision, recall, and F1-score are stored as percentages on a 0–100 scale;
- validation macro precision, recall, and F1-score are stored on a 0–1 scale.

The analysis notebook converts the validation macro metrics to percentages for visualization and reporting.

## Model Size

Model-size values used in the architecture comparison are approximate.

The retained approximate values are:

- VGG16: ~537.6 MB
- ResNet18: ~44.9 MB
- MobileNetV2: ~9.3 MB

## Inference Speed

Inference speed was not benchmarked as a documented experimental measurement during this stage.

Qualitative labels appearing in older comparison material should therefore not be interpreted as measured inference-speed results.

## Figures

The figures in `figures/` are derived visual outputs generated from the retained summary CSV files using `Analysis.ipynb`.

The repository retains the approved high-resolution versions:

- `Training_All_Metrics.png` — 5364 × 2858 px
- `Validation_All_Metrics.png` — 5364 × 2858 px
- `Train & Validation Wadi Degla Loss.png` — 5364 × 1718 px

`Validation_All_Metrics.png` is the main architecture-screening figure used in the manuscript.

`Training_All_Metrics.png` and `Train & Validation Wadi Degla Loss.png` are retained as supplementary outputs.

All three figures can be regenerated from the archived summary files using the analysis notebook.

## Reproducibility Scope

The notebooks preserve the historical execution logic, comparison workflow, and sources of the reported outputs.

They are retained as historical execution and methodological evidence and should not be interpreted as fully cross-platform, one-click reproduction pipelines.

Environment configuration and historical directory paths may require adaptation before rerunning the notebooks on another system.
