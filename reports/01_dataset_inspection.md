# Notebook 01 --- Dataset Inspection

**Project:** NeuroSeg --- Brain MRI Segmentation\
**Dataset:** 2024 BraTS Glioma (Kaggle)\
**Notebook:** `01_dataset_inspection.ipynb`\
**Status:** Completed --- initial inspection of one patient

## Objective

Inspect the BraTS dataset structure, read NIfTI metadata, verify
alignment between MRI modalities, and examine the segmentation-label
distribution for one patient.

## Dataset structure

Each inspected patient folder contains five NIfTI files:

  File suffix   Description
  ------------- ----------------------
  `t1n`         T1
  `t1c`         Contrast-enhanced T1
  `t2w`         T2
  `t2f`         FLAIR
  `seg`         Segmentation mask

Dataset root used in Kaggle:

``` text
/kaggle/input/datasets/i212385nomanarif/2024-brats-glioma
```

## Inspection results

Inspected patient: `BraTS-GLI-02547-101`

  Property                        Observed result
  ------------------------------- ----------------------
  Volume shape (all five files)   `(182, 218, 182)`
  Voxel spacing                   `(1.0, 1.0, 1.0)` mm
  Data type                       `float32`
  Approx. file size per volume    `27.55 MB`

All four MRI modalities had matching volume dimensions and matching
affine matrices in this patient.

The voxel spacing is isotropic: the spacing is 1 mm along each of the
three spatial axes. The affine matrix maps voxel indices to
physical/world coordinates.

## Segmentation-label distribution

Observed proportions in this patient's segmentation file:

    Label value   Percentage of voxels
  ------------- ----------------------
              0               99.7808%
              1                0.0007%
              2                0.1787%
              3                0.0347%
              4                0.0051%

This sample shows strong class imbalance, with background voxels making
up the vast majority of the volume.

**Important:** These percentages describe one patient only; they are not
dataset-wide statistics. The meaning of each non-zero label must be
confirmed against the official BraTS 2024 dataset documentation before
label remapping or metric calculation.

## Conclusion

The dataset is accessible and its NIfTI files can be inspected with
NiBabel. The selected patient's four MRI modalities have matching shapes
and affine matrices, supporting voxel-wise multimodal analysis for this
case.

## Next step

Proceed to `02_volume_visualization.ipynb` to load and visualize the MRI
volume in axial, coronal, and sagittal planes.
