# NeuroSeg --- Project Log

*Last updated: 3 November 2026*

## 1. Project overview

**NeuroSeg** is a research-oriented brain MRI segmentation project
focused on understanding and evaluating established 3D medical-image
segmentation methods for glioma/tumour regions.

The project has a strict **60-hour scope**. The priority is not to
invent a new architecture or build a large software platform. The
priority is to:

-   Understand the medical-imaging domain and the BraTS dataset.
-   Study established segmentation architectures and their design
    choices.
-   Run pretrained-model inference where suitable weights and compatible
    preprocessing are available.
-   Evaluate predictions quantitatively and perform visual/error
    analysis.
-   Build only a lightweight demonstration interface/backend if time
    permits.

The intended audience includes professors and research institutes
considering the project as evidence of preparation for a
computer-vision/medical-imaging research internship.

## 2. Intended deliverable

A user should be able to provide a supported brain MRI volume and
receive:

-   A predicted tumour segmentation mask.
-   Visual overlays of the prediction on MRI slices.
-   Volumes for the relevant tumour regions.
-   Quantitative evaluation metrics when a ground-truth mask is
    available.

This is an experimental research/demo tool, **not a clinically validated
diagnostic system**.

## 3. Dataset

### Current dataset choice

Using the Kaggle dataset **`2024_BraTS_Glioma`**, described on its
Kaggle page as the BraTS 2024 Adult Glioma Segmentation Task dataset
from Synapse.

-   Reported dataset size: approximately 700 3D scans.
-   Four MRI modalities per case and one segmentation mask.
-   NIfTI files (`.nii`).
-   Dataset is attached to a Kaggle notebook; the data is read-only
    under `/kaggle/input`.

Current Kaggle dataset root observed in the notebook:

``` text
/kaggle/input/datasets/i212385nomanarif/2024-brats-glioma
```

Example patient:

``` text
BraTS-GLI-02547-101/
├── BraTS-GLI-02547-101-seg.nii
├── BraTS-GLI-02547-101-t1c.nii
├── BraTS-GLI-02547-101-t1n.nii
├── BraTS-GLI-02547-101-t2f.nii
└── BraTS-GLI-02547-101-t2w.nii
```

Modality suffixes:

  Suffix   Modality
  -------- -----------------------------
  `t1n`    T1
  `t1c`    T1ce / contrast-enhanced T1
  `t2w`    T2
  `t2f`    FLAIR
  `seg`    Segmentation annotation

**Important:** Do not assume BraTS 2021 label conventions apply
unchanged. The inspected BraTS 2024 mask contains values
`0, 1, 2, 3, 4`. Confirm the exact label definitions from the dataset's
official documentation/metadata before writing label remapping, region
definitions, loss functions, or evaluation code.

## 4. Research questions and domain concepts to explore

1.  How do 3D CNNs exploit volumetric context compared with 2D
    slice-based models?
2.  How do the four MRI modalities contribute complementary information?
3.  How do CNN-based and Transformer-based architectures differ in local
    and global context modelling?
4.  Which tumour subregions are most difficult to segment?
5.  How do Dice, IoU, HD95 and sensitivity describe different aspects of
    segmentation quality?
6.  How robust is performance to removal of one or more MRI modalities?
7.  What kinds of errors occur across patients, and what limitations
    remain?

Potential experiments should be kept small and reproducible. For
example, compare full four-modality input with selected modality
subsets, provided the chosen model supports such inputs and the
experiment can be completed within the time budget.

## 5. Model exploration plan

Models discussed as candidates:

  -----------------------------------------------------------------------
  Model                               Role in exploration
  ----------------------------------- -----------------------------------
  3D U-Net                            Understand the foundational
                                      volumetric CNN encoder-decoder

  nnU-Net                             Study a strong self-configuring
                                      medical segmentation framework and
                                      use a compatible pretrained model
                                      if available

  UNETR                               Explore a Transformer encoder with
                                      a U-shaped decoder

  Swin UNETR                          Explore hierarchical/windowed
                                      Transformer representations for 3D
                                      segmentation
  -----------------------------------------------------------------------

These are **candidates for study/comparison, not a promise to train all
four**. Given the 60-hour limit, prioritize reliable inference with one
suitable pretrained model and only add comparisons if compatible
checkpoints, compute and time are available. Record model version,
checkpoint source, preprocessing, input shape, and inference settings.

## 6. Evaluation plan

Primary metrics to investigate:

-   **Dice coefficient:** overlap between predicted and reference
    regions.
-   **IoU:** intersection divided by union.
-   **HD95:** robust boundary-distance measure based on the 95th
    percentile.
-   **Sensitivity/recall:** fraction of reference tumour voxels
    detected.

Evaluate the relevant BraTS tumour regions only after confirming the
dataset's label mapping and region definitions. Report per-region
results rather than relying on a single aggregate score. Include
qualitative overlays and examples of failure cases.

## 7. Scope and time budget

Total planned effort: **60 hours**.

  Workstream                                              Hours
  ---------------------------------------------------- --------
  Medical-imaging fundamentals and BraTS exploration         10
  Architecture and paper study                               12
  Pretrained inference and experiments                       15
  Quantitative evaluation and error analysis                 13
  Minimal application and documentation                      10
  **Total**                                              **60**

Backend/frontend should remain minimal. A simple Streamlit interface
with a small inference layer may be enough; avoid unnecessary
authentication, databases, complex deployment, or elaborate frontend
work.

## 8. Notebook plan

  ---------------------------------------------------------------------------------------
  Notebook                                Objective               Status
  --------------------------------------- ----------------------- -----------------------
  `01_dataset_inspection.ipynb`           Inspect folders, files, **Completed for one
                                          NIfTI metadata,         patient**
                                          alignment and label     
                                          distribution            

  `02_volume_visualization.ipynb`         Load and visualize MRI  Not started
                                          volumes in axial,       
                                          coronal and sagittal    
                                          planes                  

  `03_multimodal_visualization.ipynb`     Compare T1n, T1c, T2w   Not started
                                          and T2f for the same    
                                          patient/slices          

  `04_segmentation_visualization.ipynb`   Visualize ground-truth  Not started
                                          labels over MRI slices  

  `05_dataset_statistics.ipynb`           Analyse label           Not started
                                          frequencies,            
                                          tumour-region volumes   
                                          and patient-level       
                                          variation               
  ---------------------------------------------------------------------------------------

## 9. Current progress --- 3 November 2026

### Environment and data access

-   Kaggle notebook created and dataset attached.
-   Kaggle session successfully started.
-   `nibabel` is available in the notebook environment.
-   Dataset files are accessible in read-only `/kaggle/input`.

### Notebook 01 completed

Inspected patient `BraTS-GLI-02547-101`.

Observed for the five files:

-   Shape: `(182, 218, 182)`.
-   Voxel spacing: `(1.0, 1.0, 1.0)` mm.
-   Data type: `float32`.
-   Each file size: approximately `27.55 MB`.
-   All four MRI modalities have matching shapes.
-   All four MRI modalities have matching affine matrices.
-   The displayed segmentation file has the same shape and voxel
    spacing.

Observed segmentation label proportions for this patient:

    Label value   Percentage of voxels
  ------------- ----------------------
              0               99.7808%
              1                0.0007%
              2                0.1787%
              3                0.0347%
              4                0.0051%

These are observations from **one patient only**, not dataset-wide
statistics. They illustrate strong background/foreground imbalance.
Confirm label semantics before interpreting the nonzero values
biologically.

### Current status

-   Dataset access: complete.
-   Initial patient/file inspection: complete.
-   NIfTI metadata inspection: complete.
-   Modality shape and affine consistency check: complete.
-   Initial segmentation-label distribution: complete for one patient.
-   MRI visualization: not started.
-   Model selection/checkpoint validation: not started.
-   Inference and quantitative evaluation: not started.
-   Application/backend: not started.

## 10. Immediate next steps

1.  Create `02_volume_visualization.ipynb`.
2.  Load one modality with NiBabel and inspect its NumPy array shape,
    intensity range and representative slices.
3.  Visualize axial, coronal and sagittal planes, being careful to use
    the affine/orientation information rather than assuming array axes
    correspond directly to anatomical directions.
4.  In the next notebook, compare all four modalities at matching
    anatomical locations.
5.  Visualize the segmentation mask and verify the official label
    mapping.
6.  Only then begin model/checkpoint selection and preprocessing design.

## 11. Working principles

-   Understand each preprocessing step; do not blindly run a pipeline.
-   Keep experiments reproducible and record dataset/model/checkpoint
    versions.
-   Do not claim clinical validity.
-   Do not claim a model comparison unless the models were actually
    evaluated under comparable conditions.
-   Prefer a small number of well-explained experiments over many
    superficial ones.
-   Keep the research analysis and quantitative evaluation more
    substantial than the software wrapper.

------------------------------------------------------------------------
