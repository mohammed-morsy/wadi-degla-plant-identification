# Wadi Degla Fieldwork and Botanical Identification

## Scope

This directory documents the fieldwork and botanical-identification component of the Wadi Degla plant-identification study. It contains metadata describing field visits, target plant species, sampling locations, herbarium records, and the relationship between historical model-class names and currently accepted scientific names.

## Field Survey Design

Fieldwork covered a 12-km study route within Wadi Degla Protected Area. The sampling framework comprised 24 predefined sampling locations distributed at 0.5-km intervals along the study route.

The field GPS record contains 24 coordinate records organized under codes K1-K12, with two coordinate records associated with each code.

Routine field visits aimed to cover about 12 of the 24 sampling locations. Site coverage remained flexible during individual visits so that fieldwork could continue along the study route when a planned location was unsuitable for photographing or collecting the target vegetation.

## Field Visits

Ten field visits were conducted between December 2023 and February 2025.

Most visits followed the routine field-survey workflow. The visits conducted on 20 April 2024 and 7 February 2025 were targeted collection visits designed to address specific field-collection needs.

Visit-level information, including collection date, visit type, number of species photographed, and number of images retained, is provided in `metadata/field_visits.csv`.

## Image Acquisition

Image acquisition followed a flexible field protocol designed to capture visual diversity under natural conditions.

Plants were photographed from different distances and viewpoints, including whole-plant views and available plant organs such as leaves, flowers, fruits, and other visible structures.

This strategy increased variation in scale, viewpoint, organ representation, background, illumination, growth stage, and other naturally occurring visual conditions within the field image collection.

Images were acquired using multiple mobile devices.

## Botanical Identification and Verification

Plant identification began in the field with preliminary identification by botanical experts. Reference specimens representing the target species were collected during the fieldwork program and used together with expert review to confirm botanical identity.

Field images associated with the identified plants were subsequently organized under the confirmed species identity.

During botanical verification and dataset curation, 300 field images were excluded because their botanical identity could not be established with sufficient confidence.

The WadiDegla field dataset contains 22,064 images representing 32 target plant species.

## Herbarium Documentation

Reference specimens representing the 32 target plant species were documented in the herbarium record associated with the study.

The machine-readable herbarium metadata are provided in `metadata/herbarium_specimens.csv` and include family, recorded binomial name, recorded synonym where applicable, and collection-location code.

The specimens are associated with the Herbarium of the Faculty of Science, Al-Azhar University.

## Taxonomic Nomenclature

Botanical reporting uses the currently accepted scientific names adopted for the study, while historical model-class names and class indices are preserved for computational reproducibility.

The relationship between these two naming layers is documented in `metadata/class_taxonomy_crosswalk.csv`.

For example, the historical model class `Salsola imbricata Forssk.` is linked to the accepted scientific name `Caroxylon imbricatum (Forssk.) Moq.`.

## Files in This Directory

### `metadata/field_visits.csv`

Visit-level metadata for the ten field visits, including dates, visit type, species photographed, and retained field-image counts.

### `metadata/species_summary.csv`

Species-level summary for the 32 target plant species and their representation within the WadiDegla field dataset.

### `metadata/class_taxonomy_crosswalk.csv`

Mapping between historical model class indices/names and the scientific names used for current botanical reporting.

### `metadata/herbarium_specimens.csv`

Machine-readable representation of the herbarium specimen record.

### `metadata/sampling_locations.csv`

Coordinate records for the 24 predefined sampling locations used during fieldwork.

### `documentation/fieldwork_notes.md`

Additional methodological documentation relevant to the fieldwork and botanical-identification stage.

### `figures/study_area_map/`

Files associated with the study-area and sampling-location map.

## Documentation Notes

Field metadata were organized primarily at the species and collection-date levels. Accordingly, image counts represent numbers of photographs and should not be interpreted as counts of independent plant individuals or independent biological observations.

The coordinate reference system/datum associated with the field GPS record will be confirmed before production of the final study-area map.

Detailed permit metadata will be incorporated after retrieval of the original permit record.

## Related Dataset Stage

This directory documents the fieldwork and botanical-identification component of the project.

WadiDegla model dataset construction, model training, validation, external web-image data, and subsequent experimental stages are documented separately.
