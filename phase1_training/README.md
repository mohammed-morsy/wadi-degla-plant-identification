# Phase 1 — WadiDegla model dataset training

This directory preserves the training and analysis evidence for **Stage 5 — Phase 1: WadiDegla model dataset training** in the Wadi Degla Plant Identification project.

## Scope

Phase 1 covers MobileNetV2 training on the **WadiDegla model dataset** through epoch label 130.

The following are **outside this directory's scientific scope** and belong to the next project stage:
- evaluation of Phase 1 checkpoints on the External Web Dataset;
- model-guided web-image stratification;
- Phase 2 web-assisted fine-tuning and later model selection.

## Dataset terminology used in current documentation

- **WadiDegla field dataset**: 22,064 field images representing 32 target plant species.
- **WadiDegla model dataset**: WadiDegla field dataset + 500 external plant images in the non-target `others` class = 22,564 images across 33 model classes.
- **WadiDegla model dataset training set**: 17,364 images.
- **WadiDegla model dataset validation set**: 5,200 images.

Historical notebooks, variable names, file paths, labels, and stored outputs are preserved when needed to document how the work was actually performed. A historical occurrence of a shorter or older WadiDegla label should not be interpreted as a different dataset.

## Repository contents

```text
phase1_training/
├── README.md
├── notebooks/
│   ├── Phase1_MobileNetV2_Training.ipynb
│   └── Phase1_Analysis.ipynb
├── outputs/
│   ├── phase1_training_schedule.csv
│   ├── summary_metrics/
│   │   ├── train_summary.csv
│   │   └── val_summary.csv
│   └── class_weighting_evidence/
│       ├── mobilenetv2_stageD_val_results96_100.csv
│       ├── mobilenetv2_stageE_val_results103_110.csv
│       └── mobilenetv2_stageE_val_results119_120.csv
└── figures/
    ├── Phase1_Training_Validation_Metrics.png
    └── Phase1_Training_Validation_Loss.png
```

## Historical notebooks

### `Phase1_MobileNetV2_Training.ipynb`

This notebook is preserved as the **historical training record** for Phase 1. It should not be interpreted as a single uninterrupted one-click `Run All` pipeline.

The original training history contains checkpoint reloads, rollbacks, overlapping epoch labels, and class-weighting changes. Therefore, notebook cell order and epoch label alone do not uniquely identify the retained model-development lineage.

The important checkpoint transitions are:

`20 -> 39 -> 65 -> 97 -> 108 -> 120 -> 130`

More precisely:
- Stage 2 executed through epoch label 40, but checkpoint 39 was retained for Stage 3.
- Stage 3 executed through epoch label 70, but checkpoint 65 was retained because continuation through 66–70 did not improve validation accuracy beyond checkpoint 65.
- Stage 4 executed through epoch label 100, but Stage 5 was initialized from checkpoint 97.
- During Stage 5, checkpoint 108 was reloaded before epoch label 109 after the weighting formulation was changed. After checkpoint 120, the weighting formulation was changed again and training continued directly through epoch labels 121–130 from checkpoint 120.
- Phase 1 training continued through epoch label 130.

The notebook itself is not rewritten to make this history appear more linear than it actually was.

### `Phase1_Analysis.ipynb`

This is the historical analysis / figure-generation notebook. The original notebook read multiple project-specific intermediate summary files from `train_summary/` and `val_summary/` directories.

Those redundant intermediate CSV files are not published in this compact package. Instead, the repository provides:
- `train_summary.csv`
- `val_summary.csv`
- the retained publication-facing figures generated from the consolidated summaries.

Accordingly, `Phase1_Analysis.ipynb` is preserved as a **historical methodological record** showing how the analysis and figures were produced. It should not be interpreted as a standalone one-click pipeline from only the files in this directory.

If the repository filename is changed from the historical `Phase 1.ipynb` to `Phase1_Analysis.ipynb`, the notebook content should remain unchanged.

## Retained lineage versus complete historical branches

`train_summary.csv` and `val_summary.csv` each contain 130 consolidated epoch-level records and represent the **retained Phase 1 development lineage** used for reporting and plotting.

They should not be interpreted as a complete serialization of every historical branch that occurred in the training notebook. In particular, some epoch labels were executed more than once in different branches after checkpoint reloads.

The historical notebook remains the primary record of the full branch structure, while the consolidated summaries provide the compact reporting lineage.

`phase1_training_schedule.csv` makes the retained transitions and Stage 5 weighting changes machine-readable without rewriting the original notebook.

## Training configuration

The verified Phase 1 configuration includes:
- model: MobileNetV2 initialized with ImageNet-pretrained weights;
- output classes: 33;
- classifier replacement: Kaiming-normal weight initialization with zero bias;
- optimizer: AdamW;
- AdamW betas: `(0.9, 0.999)`;
- weight decay: `1e-4`;
- batch size: `32`;
- no automatic learning-rate scheduler;
- seed: `42` for Python, NumPy, and PyTorch;
- deterministic algorithms enabled;
- seeded `torch.Generator` passed to the data loaders;
- `num_workers = 4`;
- training loader: `shuffle = True`;
- validation loader: `shuffle = False`;
- GPU acceleration: Apple Metal Performance Shaders (MPS);
- mixed precision: not used;
- verified environment: Python 3.12.2, PyTorch 2.5.1, torchvision 0.20.1 on macOS / Apple M1.

## Image preprocessing and augmentation

Training images used a `torchvision.transforms.v2` pipeline:
- random resized crop to 224×224;
- scale range: 0.2–1.0;
- aspect ratio range: 0.75–1.33;
- horizontal flip: `p = 0.5`;
- vertical flip: `p = 0.2`;
- rotation within ±90° inside a random transform applied with `p = 0.5`;
- color jitter with `p = 0.8`:
  - brightness: 0.7–1.3;
  - contrast: 0.85–1.3;
  - saturation: 0.7–1.3;
  - hue: ±0.0278;
- conversion to float32;
- ImageNet normalization:
  - mean = `[0.485, 0.456, 0.406]`;
  - std = `[0.229, 0.224, 0.225]`.

Validation images were resized so that the shorter side was 256 pixels, center-cropped to 224×224, converted to float32, and normalized with the same ImageNet statistics. No random augmentation was applied to validation images.

## Progressive unfreezing and checkpoint history

| Stage / subphase | Historical label | Executed epoch labels | Start / initialization | Transition or endpoint | Trainable scope | Learning rate | Class weighting |
|---|---|---:|---|---:|---|---:|---|
| Stage 1 | A | 1–20 | ImageNet-pretrained MobileNetV2 | 20 | Classifier head only | 1e-3 | Inverse frequency |
| Stage 2 | B | 21–40 | Stage 1 end | 39 | Blocks 17–18 + classifier | 1e-4 | Inverse frequency |
| Stage 3 | C | 40–70 | Checkpoint 39 | 65 | Blocks 15–18 + classifier | 5e-5 | Inverse frequency |
| Stage 4 | D | 66–100 | Checkpoint 65 | 97 | Blocks 13–18 + classifier | 3e-5 | Inverse frequency |
| Stage 5.1 | E | 98–110 | Checkpoint 97 | 108 | Full model | 1e-5 | Adaptive frequency + validation recall |
| Stage 5.2 | E | 109–120 | Checkpoint 108 | 120 | Full model | 1e-5 | Recall-emphasized adaptive weighting |
| Stage 5.3 | E | 121–130 | Checkpoint 120 | 130 | Full model | 1e-5 | Stronger recall-emphasized adaptive weighting |

The overlapping epoch labels are historical and result from checkpoint reloads. They should not be flattened into a fictitious uninterrupted chronology.

## Role of the WadiDegla model dataset validation set

During Phase 1, the WadiDegla model dataset validation set was used to:
- calculate loss and classification metrics after each epoch;
- monitor training progress;
- support checkpoint retention, checkpoint reload, and continuation decisions;
- provide per-class recall values used to update Stage 5 class weights at checkpoints 97, 108, and 120.

For current reporting, results from this set are described as **development-validation results / measurements**.

## Class weighting

### Stages 1–4

Stages 1–4 used inverse-frequency class weights based on the number of training images in each class.

### Stage 5.1 — start from checkpoint 97

Inverse-frequency weights were combined with a validation-recall component derived from per-class recall at checkpoint 97.

The recall-based component was progressively amplified using percentile-based multipliers. The frequency and recall components were standardized before combination; resulting weights were shifted so that the minimum was 1 and then rescaled to a mean of 1.

### Stage 5.2 — checkpoint 108 reloaded before continuing at epoch label 109

Per-class validation recall from checkpoint 108 was converted to a recall penalty:

`recall_penalty = (1 - recall) * 100`

The inverse-frequency and recall-penalty components were standardized across classes. The standardized inverse-frequency component was divided by 2.5 and the standardized recall-penalty component was multiplied by 2.5; the two components were added, and the resulting weights were shifted so that the minimum weight was 1.

### Stage 5.3 — class-weight update at checkpoint 120 followed by continued training

Per-class validation recall from checkpoint 120 was converted to the same recall penalty. The inverse-frequency and recall-penalty components were standardized across classes. The standardized inverse-frequency component was divided by 5 and the standardized recall-penalty component was multiplied by 5; the two components were added, and the resulting weights were shifted so that the minimum weight was 1. Training then continued through epoch labels 121–130.

Here:
## Class-weighting evidence files

The following files are retained because they provide per-class validation evidence used at the Stage 5 weighting transitions and are not redundant with the consolidated epoch summaries:

- `mobilenetv2_stageD_val_results96_100.csv`
- `mobilenetv2_stageE_val_results103_110.csv`
- `mobilenetv2_stageE_val_results119_120.csv`

They should be preserved unchanged as evidence files.

## Metric units

The historical training notebook does not use exactly the same internal numeric scale for every stored metric:
- training macro precision / recall / F1 were stored as percentage-style values on a 0–100 scale;
- validation macro precision / recall / F1 were stored in some raw historical outputs on a 0–1 scale and converted to percentages for reporting / plotting;
- accuracy was historically handled as a percentage-style value.

Publication-facing summaries and figures use consistent percentage units for accuracy, macro precision, macro recall, and macro F1. Historical raw files should not be rewritten merely to normalize their stored units.

## Figures

The publication-facing Phase 1 figures are:
- `Phase1_Training_Validation_Metrics.png` — main Phase 1 metrics figure;
- `Phase1_Training_Validation_Loss.png` — supplementary supporting figure.



The metrics figure shows the retained Phase 1 lineage, not every historical branch in the notebook.

Because the class-weighting formulation changes within Stage 5, loss values across Stage 5 subphases should be interpreted descriptively rather than as values from one fixed objective.

## `phase1_training_schedule.csv`

This compact derived file records the verified stage/subphase structure, checkpoint transitions, learning rates, trainable scopes, and class-weighting strategy.

It is a documentation file derived directly from reviewed Phase 1 sources; it does not introduce a new scientific analysis.

The published CSV was generated from the reviewed Phase 1 sources using a small Python standard-library helper script retained in the project records.

The generator script itself is not part of this compact public package.

## Files intentionally not published in this compact package

The following are excluded by default:
- dozens of intermediate training / validation summary CSV files already represented by `train_summary.csv` and `val_summary.csv`;
- large collections of `training_states_*.pkl` and checkpoint files;
- debugging outputs;
- redundant intermediate exports;
- Phase 2 files;
- External Web Dataset checkpoint evaluation and web-stratification outputs.

A checkpoint or intermediate file should be added later only if it is needed to document a specific part of the historical workflow that is not already clear from the notebooks, compact summaries, schedule, or retained evidence files.

## Publication-facing result context

At epoch 130, the retained Phase 1 lineage reported:
- validation accuracy: 86.52%;
- macro precision: 87.80%;
- macro recall: 89.14%;
- macro F1: 87.97%;
- validation loss: 0.5803;
- training accuracy: 98.59%.

Phase 1 training continued through epoch label 130.

The class-wise observation that *Trichodesma africanum* and *Farsetia aegyptia* had the lowest reported Phase 1 recall values (52% and 61%, respectively) is carried forward in the manuscript as an important bridge to the next stage. The corresponding per-class evidence is reviewed in its proper next-stage context rather than being reinterpreted here.

## Historical record and publication policy

- Historical notebook content is preserved rather than rewritten to create a cleaner story than the actual experimental history.
- Public-facing documentation uses the current WadiDegla dataset terminology.
- Historical class names and class indices used during model training are preserved to document the exact model-class identity used during training.
- Current botanical reporting uses accepted scientific names with botanical authorship.
- No commit, push, release, or upload action is implied by this README. Repository changes should be executed only after explicit project approval.