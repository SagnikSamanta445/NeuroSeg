# Notebook 06 --- Data Preparation

## 1. Purpose

Notebook 06 prepares the BraTS 2024 Adult Glioma MRI dataset for
training and evaluating 3D segmentation models in NeuroSeg.

The notebook focuses on creating a consistent, reusable data pipeline.
It loads and checks the MRI volumes and segmentation masks, examines
image intensities, normalizes the MRI modalities, creates patient-level
dataset splits, extracts 3D patches, and verifies that the data can be
supplied to a PyTorch model.

This notebook is a preparation and validation stage. It does not train a
segmentation model.

## 2. Dataset and input structure

Each patient case contains five NIfTI files:

  File suffix   Description
  ------------- --------------------------
  `-t1n.nii`    T1-weighted MRI
  `-t1c.nii`    T1 contrast-enhanced MRI
  `-t2w.nii`    T2-weighted MRI
  `-t2f.nii`    T2-FLAIR MRI
  `-seg.nii`    Segmentation mask

The four MRI modalities are loaded in the fixed channel order:

1.  T1n
2.  T1c
3.  T2w
4.  T2f

For the inspected example, the MRI volume has dimensions **(4, 182, 218,
182)**: - `4` is the number of MRI channels/modalities. -
`182 × 218 × 182` are the three spatial dimensions of the volume.

The corresponding segmentation mask has dimensions **(182, 218, 182)**.
It contains one integer label for each spatial voxel.

The notebook supports NIfTI files with `.nii` and `.nii.gz` extensions.

## 3. Patient discovery

The notebook scans the dataset directory and groups files by patient
identifier. Each patient is represented by a dictionary containing paths
for the four MRI modalities and the segmentation mask.

The resulting structure is conceptually:

``` text
case_files
 ├── patient_id_1
 │    ├── t1n
 │    ├── t1c
 │    ├── t2w
 │    ├── t2f
 │    └── seg
 ├── patient_id_2
 │    └── ...
 └── ...
```

The discovery step checks that the expected files can be found for each
case. This gives later notebook cells a consistent way to retrieve a
patient's data.

## 4. Loading and validating a patient

The `load_case()` function loads the four MRI volumes and the
segmentation mask for one patient.

The workflow includes:

-   Loading each NIfTI file with NiBabel.
-   Converting volumes to a canonical orientation when requested, so
    that the image files use a consistent orientation convention.
-   Converting MRI image data to `float32`.
-   Checking that all four MRI modalities have matching spatial shapes.
-   Checking that the modalities have matching affine information, which
    describes how voxel coordinates map to physical space.
-   Checking that the segmentation mask has the same spatial shape and
    affine alignment as the MRI modalities.
-   Converting segmentation values to integer labels and checking that
    they belong to the expected label set.

The function returns:

-   `image`: a four-channel MRI array with shape **\[C, X, Y, Z\]**.
-   `label`: a segmentation array with shape **\[X, Y, Z\]**.

Here, `C = 4`. The segmentation does not have a channel dimension at
this stage; it stores one class ID per voxel.

The expected label IDs in this dataset are `0, 1, 2, 3, 4`. Not every
patient is expected to contain every label.

## 5. MRI intensity inspection

Before normalization, the notebook examines the intensity distributions
of the four modalities.

It calculates descriptive statistics such as minimum, maximum, mean,
standard deviation, median, and selected percentiles. It also plots
modality-wise intensity histograms.

Background voxels are excluded from these intensity summaries by
selecting non-zero voxels. This makes the inspection focus on the
non-background portion of the MRI volumes.

The purpose is to understand how intensity values vary across modalities
and to motivate the normalization step. These plots and statistics are
exploratory; results from one patient should not be treated as
dataset-wide conclusions.

## 6. MRI normalization

The notebook applies Z-score normalization separately for each patient
and each MRI modality.

For a given patient, each modality is normalized independently using its
non-zero voxels. Background voxels are kept at zero.

This approach: - prevents the four modalities from being treated as
though they share one intensity scale; - reduces variation in intensity
scale between patient scans; - preserves the zero-valued background; -
produces normalized MRI data suitable for the custom model pipeline.

The normalization is applied to the MRI image channels. It is **not**
applied to the segmentation labels.

The normalized image retains the same shape as the original image:
**\[4, X, Y, Z\]**.

## 7. Segmentation label handling

The segmentation mask is retained as an integer-valued volume with the
original label IDs.

The notebook validates that the labels belong to the expected set:

-   `0`: background
-   `1`, `2`, `3`, `4`: the dataset's annotated tumour-related classes

The notebook does not remap these labels during preparation. Keeping the
original IDs ensures that the model's output classes and the
ground-truth labels can be compared consistently.

A particular patient may contain only a subset of the possible labels.
Missing labels in an individual scan are not automatically an error.

## 8. Patient-level train, validation and test split

The dataset is split at the **patient level**, rather than splitting
individual slices or patches.

The configured split is:

  Split          Approximate proportion
  ------------ ------------------------
  Training                          70%
  Validation                        15%
  Test                              15%

A fixed random seed is used so that the split can be reproduced.

Patient-level splitting is important because slices or patches from the
same 3D scan are highly related. Keeping a patient's data within only
one split helps prevent information leakage between training, validation
and test data.

The saved split information is intended to be reused across the custom
model experiments, so that model comparisons use the same patient
groups.

## 9. 3D patch extraction

Training a 3D segmentation model on every full MRI volume can require
substantial GPU memory. The notebook therefore implements extraction of
smaller 3D patches.

The configured patch size is:

**64 × 64 × 64 voxels**

A patch contains: - four MRI channels with shape **\[4, 64, 64,
64\]**; - one segmentation patch with shape **\[64, 64, 64\]**.

The patch sampler uses a tumour-aware strategy. With the configured
positive-sampling probability of `0.7`, it chooses a centre from a
non-background labelled voxel. Otherwise, it chooses a random spatial
centre.

When a patch extends beyond a volume boundary, the extraction function
pads the missing region with zeros so that the returned patch has the
requested dimensions.

The current `patches_per_case = 1` setting is used as an initial
pipeline smoke test. It verifies that patch extraction works; it is not
a final training sampling schedule.

## 10. Reusable PyTorch Dataset

The notebook defines a reusable `BraTS3DPatchDataset` class in the
`neuroseg_data.py` module.

The Dataset retrieves patient data and extracts patches when samples are
requested. This lazy-loading approach avoids loading every full 3D
patient volume into memory at once.

For a training sample, the Dataset returns:

  Item                 Shape                   Data type
  -------------------- ----------------------- -----------
  MRI image patch      **\[4, 64, 64, 64\]**   `float32`
  Segmentation patch   **\[64, 64, 64\]**      `int64`

The image tensor contains four input channels. The label tensor contains
class IDs and is represented as integer data for use with segmentation
losses such as PyTorch cross-entropy.

The module also contains helper functions for discovering patient files,
loading and validating a case, normalizing modalities, and extracting
patches.

## 11. DataLoader verification

A PyTorch `DataLoader` is created from the Dataset to check that samples
can be batched correctly.

With a batch size of `B`, the expected tensor dimensions are:

  Tensor                Batched shape
  --------------------- --------------------------
  MRI images            **\[B, 4, 64, 64, 64\]**
  Segmentation labels   **\[B, 64, 64, 64\]**

The notebook checks that the Dataset and DataLoader return tensors with
the expected dimensions and data types.

This is a pipeline verification step. Successful loading confirms that
the prepared samples can be passed to a 3D segmentation model, but it
does not establish that the model can train successfully or achieve good
segmentation performance.

## 12. Patch visualization and class inspection

The notebook visualizes sampled patches to inspect the relationship
between the MRI input and the segmentation mask.

It also checks the label distribution in sampled patches. This is useful
because background voxels can occupy a large part of a 3D patch, while
some tumour-related labels may be relatively sparse.

These checks help identify obvious extraction or alignment problems
before model training.

## 13. Saving metadata and configuration

The notebook saves the information needed to reproduce and reuse the
preparation workflow, including the patient split and relevant
configuration.

The saved information records key choices such as: - modality order; -
patch dimensions; - train/validation/test split; - random seed; -
sampling configuration; - dataset-related paths or metadata used by the
notebook.

The reusable `neuroseg_data.py` module should also be retained with the
project source code so that later notebooks can import the same
data-loading and patch-extraction implementation.

## 14. Important scope and limitations

-   Notebook 06 prepares data; it does not train or evaluate a
    segmentation model.
-   The example intensity plots describe the inspected patient only.
-   The initial one-patch-per-case configuration is a smoke test, not a
    complete training strategy.
-   The current patch sampler selects from any non-background label; it
    does not guarantee balanced sampling of every tumour class.
-   Patch-based loading is intended for custom model training. Final
    validation and test evaluation should use full-volume or
    sliding-window inference so that metrics represent complete patient
    volumes.
-   The patient split should remain fixed across custom model
    experiments to support fair comparisons.
-   **nnU-Net is an exception:** it has its own dataset planning and
    preprocessing workflow. The custom normalization and
    patch-extraction pipeline from this notebook should not be forced
    onto nnU-Net's native preprocessing pipeline.

## 15. Final outcome

At the end of Notebook 06, the project has a validated custom
data-preparation workflow that can:

1.  discover patient cases and their five NIfTI files;
2.  load four aligned MRI modalities and the segmentation mask;
3.  validate spatial dimensions, affine alignment and label values;
4.  inspect and normalize MRI intensities;
5.  create reproducible patient-level data splits;
6.  extract fixed-size 3D patches;
7.  provide samples through a reusable PyTorch Dataset and DataLoader;
8.  save preparation metadata and configuration for subsequent
    experiments.

The prepared custom-model input format is **\[B, 4, 64, 64, 64\]**, and
the corresponding segmentation target format is **\[B, 64, 64, 64\]**.

Notebook 06 therefore establishes the data pipeline required before
implementing and training the custom 3D segmentation models in the
subsequent notebooks.
