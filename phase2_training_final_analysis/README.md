# Phase 2 Training and Final Analysis

This directory contains the compact public reproducibility package for Stage 6 of the Wadi Degla plant-identification study: Phase 2 web-assisted fine-tuning and the subsequent final analysis.

## Scope

Stage 6 covers:

1. the retained Phase 2 training histories for the Top-30 and Bottom-30 adaptation branches;
2. cross-domain evaluation of Phase 1 checkpoints 121–130 on the External Web Dataset and retention of checkpoint 127;
3. performance-based stratification of the External Web Dataset;
4. construction and verification of Common Web and complementary evaluation sets;
5. final comparison of the seven retained Phase 2 candidate checkpoints;
6. selection of Top-30 checkpoint 215 for the Final Analysis;
7. species-level final analysis; and
8. the final confusion-matrix comparison.

No training or inference was rerun merely to create this GitHub package. The package contains retained scientific outputs and a compact subset of the evidence used in the final analysis.

## Dataset terminology

The following terms are used in public-facing documentation:

- **WadiDegla field dataset**: 22,064 original field images representing 32 target plant species.
- **WadiDegla model dataset**: the WadiDegla field dataset plus 500 external plant images in the non-target `others` class, for a total of 22,564 images and 33 model classes.
- **WadiDegla model dataset training set**: 17,364 images.
- **WadiDegla model dataset validation set**: 5,200 images.
- **External Web Dataset**: 5,815 image records representing the 32 target species.

Historical filenames, notebook variables, and stored outputs may retain older labels when changing them would rewrite the computational record.

## Phase 2 initialization and training branches

Both Phase 2 branches were initialized from Phase 1 checkpoint 127.

- **Top-30 branch**: 1,199 Top-30 web images were added to the 17,364-image WadiDegla model dataset training set, producing 18,563 training records.
- **Bottom-30 branch**: 1,202 Bottom-30 web images were added, producing 18,566 training records.

Both branches used strong augmentation during epochs 128–180 and then returned to the default Phase-1-style augmentation from epoch 181 onward.

The historical base learning rate was `1e-5`. The Bottom-30 branch also contains a final refinement in which checkpoint 215 was reloaded, a new AdamW optimizer was initialized at `5e-6`, class-weight multipliers were recalculated from checkpoint-215 validation Recall, and epoch labels 216–220 were restarted. These epoch labels therefore do not represent a simple uninterrupted continuation of the superseded historical Bottom-30 216–220 trajectory.

The retained candidate checkpoints carried into the final comparison were:

- Top-30: 199, 215, 220
- Bottom-30: 196, 215, 216, 220

## Selection of Phase 1 checkpoint 127

Phase 1 checkpoints 121–130 were evaluated on the same 5,815-image External Web Dataset.

Checkpoint 127 was retained to initialize Phase 2 because it achieved the highest **Accuracy**, **Macro Recall**, and **Macro F1** within checkpoints 121–130:

- Accuracy: 26.66%
- Macro Recall: 22.68%
- Macro F1: 23.47%

Checkpoint 130 had the highest Macro Precision (34.53%), so checkpoint 127 should not be described as the highest-performing checkpoint on every metric.

## Performance-based Web stratification

The External Web Dataset was stratified after evaluation by Phase 1 checkpoints 121–130.

- **Correctly classified**: 1,815 images classified correctly by at least one checkpoint.
- **Top-30**: 1,199 never-correct images in the upper stored performance bands.
- **Middle-40**: 1,599 never-correct images in the middle stored performance bands.
- **Bottom-30**: 1,202 never-correct images in the lower stored performance bands.

The four groups sum to 5,815 image records. The three never-correct strata sum to 4,000 records.

Historical source files may retain labels such as `Middle-30-70` or `Lowest-30`. The publication-facing terminology is **Top-30**, **Middle-40**, and **Bottom-30**.

## Common Web and complementary evaluation

For direct cross-candidate comparison, the final analysis used:

- **Common Web** = Correctly classified + Middle-40 = 3,414 image records.
- **Top-30 opposite-only** = 1,199 records, used for evaluation of Bottom-trained candidates on the opposite difficult stratum.
- **Bottom-30 opposite-only** = 1,202 records, used for evaluation of Top-trained candidates on the opposite difficult stratum.
- **Top-30 complementary union** = Common Web + Bottom-30 = 4,616 records.
- **Bottom-30 complementary union** = Common Web + Top-30 = 4,613 records.

Common Web is the shared basis for direct comparison of Baseline 127 and all seven Phase 2 candidates. The complementary evaluations provide branch-specific supporting context.

These Web-derived evaluation sets are part of the development/model-selection workflow and are **not** presented as a newly collected independent final test set.

## Final Phase 2 model selection

The seven Phase 2 candidate checkpoints were ranked on Common Web using:

1. Macro F1, descending;
2. Macro Recall, descending;
3. Accuracy, descending; and
4. `candidate_id` as a final tie-breaker.

This ranking rule belongs to the Final Analysis and should not be described as a prespecified pre-training criterion.

The selected Final Analysis model was **Top-30 checkpoint 215**:

- Accuracy: 73.02%
- Macro Precision: 65.11%
- Macro Recall: 65.24%
- Macro F1: 64.04%

Top-30 checkpoint 220 achieved slightly higher Accuracy (73.08%) but lower Macro Recall (64.81%) and Macro F1 (63.91%), and therefore ranked second under the documented rule.

Relative to Baseline 127 on Common Web, Top-30/215 improved Accuracy by 27.62 percentage points and Macro F1 by 26.42 percentage points. The saved paired comparison gives a net gain of 943 correct image classifications.

## Species-level analysis

The public species-level tables preserve accepted scientific names for reporting.

For Top-30/215 relative to Baseline 127:

- on Common Web, Recall increased for 31 of 32 target species and decreased for one species;
- on the WadiDegla model dataset validation set, Recall increased for 19 target species, was unchanged for 6, and decreased for 7.

Examples on the WadiDegla model dataset validation set include:

- *Trichodesma africanum* (L.) Sm.: 52.10% → 75.45%;
- *Farsetia aegyptia* Turra: 60.54% → 77.84%.

These values are development/validation comparisons and are not presented as independent final-test estimates.

## Confusion matrices

The final comparison figure contains four row-normalized confusion matrices:

1. Common Web — Baseline 127;
2. Common Web — Top-30/215;
3. WadiDegla model dataset validation set — Baseline 127; and
4. WadiDegla model dataset validation set — Top-30/215.

The count sources retained in this package are:

- `phase2_common_confusion_counts.csv`
- `wadidegla_validation_mobilenet_127_confusion_counts.csv`
- `wadidegla_validation_top_30_215_confusion_counts.csv`

The final publication-facing raster is:

- `phase2_final_confusion_matrix_comparison_2x2.png`

## Exact-hash audit and interpretation

The External Web Dataset contains 5,815 file records corresponding to 5,579 unique SHA-256 values. Exact duplicate-content hashes remained within the same species and performance stratum; no exact hash crossed the Correctly classified, Top-30, Middle-40, and Bottom-30 strata.

Common Web contains 3,414 file records and 3,258 unique SHA-256 values.

The reported metrics remain file-level metrics. No deduplicated/unique-hash sensitivity reanalysis is claimed.

## Directory contents

```text
phase2_training_final_analysis/
├── README.md
├── notebooks/
│   └── Phase 2 training.ipynb
├── outputs/
│   ├── training/
│   │   ├── phase2_checkpoint_candidates.csv
│   │   ├── phase2_history_source_runs.csv
│   │   └── phase2_history_retained.csv
│   ├── checkpoint_selection/
│   │   ├── phase1_web_checkpoint_selection_121_130.csv
│   │   └── web_metrics_121_130.csv
│   ├── web_stratification/
│   │   ├── web_group_summary_121_130.csv
│   │   └── web_species_distribution_wide_121_130.csv
│   ├── evaluation/
│   │   └── phase2_evaluation_baseline_comparison.csv
│   ├── model_selection/
│   │   └── phase2_model_selection_evidence.csv
│   ├── species_analysis/
│   │   ├── phase2_common_species_recall_publication.csv
│   │   └── phase2_wadidegla_species_recall_publication.csv
│   └── confusion_matrices/
│       ├── phase2_common_confusion_counts.csv
│       ├── wadidegla_validation_mobilenet_127_confusion_counts.csv
│       └── wadidegla_validation_top_30_215_confusion_counts.csv
└── figures/
    ├── phase2_wadidegla_combined_metrics_top_vs_bottom_30.png
    ├── phase2_wadidegla_combined_loss_top_vs_bottom_30.png
    └── phase2_final_confusion_matrix_comparison_2x2.png
```

## Files intentionally not included

The compact public package does not include:

- large checkpoint/model-weight bundles;
- `training_states_*.pkl` or similar optimizer/training-state archives;
- raw prediction-level CSVs and image-level audit exports that are already summarized by the retained public outputs;
- internal manifests and supporting paired/error analyses not designated as GitHub core;
- externally sourced Web images;
- publication SVG masters retained as source graphics;
- internal manuscript/governance DOCX files; or
- application deployment artifacts.

The externally sourced Web images are not redistributed through this repository.

## Historical notebook and rerunning

`Phase 2 training.ipynb` is retained as historical execution and methodological evidence. Historical paths, variables, labels, branching, restarts, and stored outputs should not be rewritten merely to make the workflow appear more linear than it was.

The notebook should not be interpreted as a guaranteed cross-platform one-click reproduction pipeline. Environment configuration, local paths, historical checkpoints, and retained artifacts may require adaptation before rerunning elsewhere.

## Application model

Top-30 checkpoint 215 is the model selected by the Stage 6 Final Analysis.

This repository section does **not** claim that the current Web application actually deploys Top-30/215. The exact deployed checkpoint must be confirmed separately from the application code before a deployment statement is made.

## Relationship to earlier repository stages

This directory builds on the earlier public components:

- `fieldwork_botany/`
- `wadi_model_dataset/`
- `external_web_dataset/`
- `architecture_screening/`
- `phase1_training/`

Shared authoritative metadata from earlier stages is referenced rather than duplicated here.

## Data and release status

The repository is a compact reproducibility record and is not the public image-data repository.

The WadiDegla field-image public-release platform, final image license, dataset DOI timing, and any optional archival DOI for a later GitHub release remain separate publication/release decisions. Do not add a DOI or release badge until those actions actually occur.
