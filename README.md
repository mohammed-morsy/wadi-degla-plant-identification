# wadi-degla-plant-identification
Research code, metadata, analyses, figures, and reproducibility materials for image-based identification of selected plant species from Wadi Degla Protected Area.

## Phase 2 Training and Final Analysis

The `phase2_training_final_analysis/` directory documents Stage 6 of the study: Phase 2 Web-Assisted Fine-Tuning and the subsequent Final Analysis.

The package includes the retained Top-30 and Bottom-30 Phase 2 training histories, evaluation of Phase 1 checkpoints 121–130 on the External Web Dataset, performance-based Web-image stratification, Common Web/complementary evaluation summaries, final candidate-ranking evidence, publication-ready species-level Recall tables, and the final confusion-matrix comparison.

The Final Analysis selected **Top-30 checkpoint 215** using the documented Common Web ranking rule (Macro F1, then Macro Recall, then Accuracy, then candidate ID). Common Web contains 3,414 image records from the 32 target species and is part of the development/model-selection workflow; it is not presented as an independent final test set.

See [`phase2_training_final_analysis/README.md`](phase2_training_final_analysis/README.md) for the complete Stage 6 documentation and file map.

### Stage 6 package structure

```text
phase2_training_final_analysis/
├── README.md
├── notebooks/
├── outputs/
│   ├── training/
│   ├── checkpoint_selection/
│   ├── web_stratification/
│   ├── evaluation/
│   ├── model_selection/
│   ├── species_analysis/
│   └── confusion_matrices/
└── figures/
```
