# 03 — Multimodal Visualization

## 1. Objective

Compare the four MRI modalities of the same patient at matching anatomical locations.

The notebook covers:

- Loading all four MRI modalities.
- Inspecting volume dimensions and intensity ranges.
- Checking spatial consistency against T1n.
- Converting volumes to canonical RAS+ orientation.
- Visualizing axial, coronal and sagittal slices side by side.
- Comparing nonzero intensity distributions across modalities.

**Dataset:** BraTS 2024 Adult Glioma  
**Patient:** `BraTS-GLI-02547-101`

## 2. Modalities

The following four MRI modalities were inspected:

| Suffix | Modality |
|---|---|
| `t1n` | T1-weighted |
| `t1c` | T1-weighted, contrast-enhanced |
| `t2w` | T2-weighted |
| `t2f` | T2-FLAIR |

## 3. Volume Information

All four volumes had the same observed shape and returned data type.

| Property | T1n | T1c | T2w | T2f (FLAIR) |
|---|---:|---:|---:|---:|
| Shape | `(182, 218, 182)` | `(182, 218, 182)` | `(182, 218, 182)` | `(182, 218, 182)` |
| Data type | `float32` | `float32` | `float32` | `float32` |
| Minimum intensity | 0.0 | 0.0 | 0.0 | 0.0 |
| Maximum intensity | 505.92276 | 1253.4319 | 1731.0282 | 443.16007 |

The four modalities were converted to canonical RAS+ orientation before visualization.

## 4. Multimodal Visualization

A 4 × 3 visualization grid was generated:

- Rows: T1n, T1c, T2w and T2f (FLAIR).
- Columns: axial, coronal and sagittal planes.
- Matching slice indices were used across the four modalities.

Percentile-based display limits (1st and 99th percentiles of nonzero slice intensities) were applied independently to each displayed slice. This improves visual contrast but changes display brightness only; it does not modify the stored MRI volumes.

The visualization allowed the same anatomical locations to be inspected across all four MRI sequences.

## 5. Intensity Distribution

Histograms were generated for the nonzero voxels of each modality using 100 bins.

Observed distribution statistics:

| Statistic | T1n | T1c | T2w | T2f (FLAIR) |
|---|---:|---:|---:|---:|
| Mean | 246.97437 | 284.9389 | 506.16083 | 148.68407 |
| Standard deviation | 83.73867 | 101.013916 | 243.04968 | 40.974316 |
| Median | 251.20512 | 283.37213 | 428.13852 | 151.01562 |
| 1st percentile | 55.669838 | 74.716095 | 233.08797 | 20.46959 |
| 99th percentile | 401.5567 | 672.0205 | 1344.6565 | 232.09586 |

These statistics were calculated after excluding zero-intensity voxels.

### Histogram observations

- **T1n:** Broad distribution with multiple concentrations.
- **T1c:** Main concentration around the lower-to-middle part of its range, with a long high-intensity tail.
- **T2w:** Broad, strongly right-skewed distribution with a long high-intensity tail.
- **T2f (FLAIR):** Comparatively concentrated distribution with a narrower intensity range.

The modalities have visibly different intensity distributions. These differences are consistent with their distinct MRI acquisition contrasts. Histogram peaks alone cannot identify specific tissues or tumour components.

## 6. Modality Characteristics Studied

- **T1n:** Provides anatomical contrast and structural context.
- **T1c:** Contrast-enhanced T1 imaging can make regions with contrast enhancement more conspicuous.
- **T2w:** Sensitive to water content and useful for examining fluid-rich or abnormal tissue.
- **T2f (FLAIR):** Suppresses much of the CSF signal while retaining many abnormal T2-like hyperintensities.

The four modalities provide complementary signal information about the same anatomy, which motivates using multimodal input for segmentation.

## 7. Conclusion

Notebook 03 established a visual and statistical comparison of the four MRI modalities for one patient.

Key takeaways:

- Successfully loaded all four modalities.
- Confirmed that all four observed volumes have shape `(182, 218, 182)`.
- Converted the volumes to canonical RAS+ orientation.
- Compared matching anatomical slices in axial, coronal and sagittal planes.
- Examined nonzero intensity histograms and summary statistics.
- Studied the different information each MRI sequence can provide.

The intensity statistics are specific to this patient and should not be treated as dataset-wide reference values. No intensity normalization, resizing, resampling or model preprocessing was performed.

**Next:** Notebook 04 — Segmentation Visualization, to inspect the ground-truth mask over MRI slices and investigate the dataset's label values and their documented meanings.
