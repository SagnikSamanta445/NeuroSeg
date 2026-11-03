# 02 — Volume Visualization

## 1. Objective

Load and visualize 3D brain MRI volumes using NiBabel and Matplotlib.

The notebook explores:

- NIfTI volume loading and intensity inspection.
- Voxel coordinates and physical coordinates.
- Affine transformations and image orientation.
- Canonical RAS+ orientation.
- Axial, coronal and sagittal visualization.
- MRI intensity distribution.

**Dataset:** BraTS 2024 Adult Glioma  
**Patient:** `BraTS-GLI-02547-101`  
**Modality:** T1n

## 2. Volume Information

Loaded the T1n NIfTI file using NiBabel.

Observed properties:

| Property                      | Value             |
| ----------------------------- | ----------------- |
| Volume shape                  | `(182, 218, 182)` |
| Data type after `get_fdata()` | `float64`         |
| Minimum intensity             | `0.0`             |
| Maximum intensity             | `505.92276`       |
| Mean intensity                | `47.59498`        |
| Standard deviation            | `104.11911`       |
| Total voxels                  | `7,221,032`       |

Note: `get_fdata()` returns floating-point data as `float64` by default, although the original stored data type was `float32`.

## 3. Background Voxel Analysis

Inspected the number of zero-intensity voxels.

| Property                     |     Value |
| ---------------------------- | --------: |
| Zero-intensity voxels        | 5,829,451 |
| Total voxels                 | 7,221,032 |
| Percentage of zero voxels    |  80.7288% |
| Percentage of nonzero voxels |  19.2712% |

Approximately 80.73% of the volume contains zero-intensity voxels, indicating substantial background representation.

A sampled voxel at array coordinate `(90, 100, 90)` had an intensity of `304.81595`.

## 4. Spatial Orientation

Inspected the NIfTI affine transformation matrix.

Original affine matrix:

```text
[[-1.  0.  0.  90.]
 [ 0.  1.  0. -126.]
 [ 0.  0.  1. -72.]
 [ 0.  0.  0.   1.]]
```

Original orientation:

```text
('L', 'A', 'S')
```

Converted the volume into canonical RAS+ orientation using:

```python
nib.as_closest_canonical(nii)
```

Canonical orientation:

```text
('R', 'A', 'S')
```

Canonical affine matrix:

```text
[[  1.   0.   0. -91.]
 [  0.   1.   0. -126.]
 [  0.   0.   1. -72.]
 [  0.   0.   0.   1.]]
```

Canonical volume shape:

```text
(182, 218, 182)
```

The first axis was flipped to obtain RAS+ orientation. The volume dimensions remained unchanged.

**Important concepts explored:**

- Voxel coordinates represent positions within the 3D array.
- Physical coordinates represent positions in the spatial reference frame, measured in millimetres.
- The affine matrix maps voxel coordinates to physical coordinates.
- Canonical orientation provides a consistent anatomical reference for visualization.

## 5. Anatomical Visualization

Visualized the MRI volume in three anatomical planes.

| Plane    | Array slicing         | Description              |
| -------- | --------------------- | ------------------------ |
| Axial    | `volume_ras[:, :, z]` | Horizontal cross-section |
| Coronal  | `volume_ras[:, y, :]` | Front/back cross-section |
| Sagittal | `volume_ras[x, :, :]` | Left/right cross-section |

Used middle-slice indices as initial visualization points:

```text
x = 91
y = 109
z = 91
```

Also explored different slice indices to observe anatomical structures at different positions.

## 6. Intensity Distribution

Generated two intensity histograms:

**Histogram 1: All voxels**

- Shows a dominant spike at zero.
- The distribution is heavily influenced by background voxels.

**Histogram 2: Nonzero voxels**

- Most nonzero intensities lie approximately between 30 and 420.
- The distribution contains multiple peaks and is not Gaussian.
- Different tissues and structures contribute to overlapping intensity distributions.

These observations show why intensity values alone cannot reliably distinguish tumour tissue from normal brain tissue.

## 7. Conclusion

Notebook 02 established the basic understanding of 3D MRI volume representation and visualization.

Key takeaways:

- Successfully loaded and inspected a 3D MRI volume.
- Understood voxel coordinates, physical coordinates and affine transformations.
- Converted the original LAS orientation to canonical RAS+.
- Visualized axial, coronal and sagittal slices.
- Examined background voxel proportions and intensity distributions.

No normalization, resizing, resampling or other preprocessing was performed.

**Next:** Notebook 03 — Multimodal Visualization, comparing T1n, T1c, T2w and T2f MRI sequences.
