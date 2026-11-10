from pathlib import Path
from collections import OrderedDict
import numpy as np
import nibabel as nib
import torch
from torch.utils.data import Dataset

MODALITIES = ("t1n", "t1c", "t2w", "t2f")
LABEL_NAME_TO_ID = {"NETC": 1, "SNFH": 2, "ET": 3, "RC": 4}

def discover_cases(data_root):
    """Find cases by locating each *-t1n.nii or *-t1n.nii.gz file."""
    root = Path(data_root)
    candidates = list(root.rglob("*-t1n.nii")) + list(root.rglob("*-t1n.nii.gz"))
    cases = {}
    for t1n_path in candidates:
        name = t1n_path.name
        suffix = "-t1n.nii.gz" if name.endswith("-t1n.nii.gz") else "-t1n.nii"
        case_id = name[:-len(suffix)]
        case_dir = t1n_path.parent
        files = {}
        for modality in MODALITIES:
            expected = [
                case_dir / f"{case_id}-{modality}.nii",
                case_dir / f"{case_id}-{modality}.nii.gz",
            ]
            matches = [p for p in expected if p.exists()]
            if len(matches) != 1:
                raise FileNotFoundError(
                    f"Expected exactly one file for {case_id}, modality {modality}; found {matches}"
                )
            files[modality] = matches[0]
        seg_candidates = [
            case_dir / f"{case_id}-seg.nii",
            case_dir / f"{case_id}-seg.nii.gz",
        ]
        seg_matches = [p for p in seg_candidates if p.exists()]
        if len(seg_matches) != 1:
            raise FileNotFoundError(
                f"Expected exactly one segmentation for {case_id}; found {seg_matches}"
            )
        files["seg"] = seg_matches[0]
        cases[case_id] = files
    if not cases:
        raise FileNotFoundError(
            f"No '*-t1n.nii[.gz]' files found under {root}. Check DATA_ROOT."
        )
    return dict(sorted(cases.items()))

def load_case(case_files, canonical=True):
    """
    Load four MRI modalities and the segmentation.
    Returns image [4, X, Y, Z] float32 and label [X, Y, Z] int16.
    No resampling is performed; spatial alignment is checked.
    """
    arrays, affines = [], []
    reference_shape = None
    reference_affine = None

    for modality in MODALITIES:
        nii = nib.load(str(case_files[modality]))
        if canonical:
            nii = nib.as_closest_canonical(nii)
        arr = np.asarray(nii.dataobj, dtype=np.float32)

        if reference_shape is None:
            reference_shape = arr.shape
            reference_affine = nii.affine
        else:
            if arr.shape != reference_shape:
                raise ValueError(
                    f"Shape mismatch for {modality}: {arr.shape} vs {reference_shape}"
                )
            if not np.allclose(nii.affine, reference_affine, atol=1e-4):
                raise ValueError(f"Affine mismatch for modality {modality}")

        arrays.append(arr)

    seg_nii = nib.load(str(case_files["seg"]))
    if canonical:
        seg_nii = nib.as_closest_canonical(seg_nii)
    label = np.asarray(seg_nii.dataobj, dtype=np.float32)

    if label.shape != reference_shape:
        raise ValueError(f"Segmentation shape mismatch: {label.shape} vs {reference_shape}")
    if not np.allclose(seg_nii.affine, reference_affine, atol=1e-4):
        raise ValueError("Segmentation affine does not match MRI modalities")

    # Labels are categorical integers, not continuous intensities.
    label = np.rint(label).astype(np.int16)
    observed = set(np.unique(label).tolist())
    allowed = {0, 1, 2, 3, 4}
    if not observed.issubset(allowed):
        raise ValueError(f"Unexpected segmentation labels: {sorted(observed - allowed)}")

    image = np.stack(arrays, axis=0).astype(np.float32)
    return image, label

def normalize_modalities(image, eps=1e-8):
    """
    Per-volume, per-modality z-score normalization over non-zero voxels.
    Background remains zero. Input/output shape: [4, X, Y, Z].
    """
    image = np.asarray(image, dtype=np.float32)
    normalized = np.zeros_like(image, dtype=np.float32)

    for channel in range(image.shape[0]):
        volume = image[channel]
        valid = np.isfinite(volume) & (np.abs(volume) > eps)
        if not np.any(valid):
            continue

        values = volume[valid]
        mean = values.mean(dtype=np.float64)
        std = values.std(dtype=np.float64)
        if std < eps:
            std = 1.0

        normalized_channel = np.zeros_like(volume, dtype=np.float32)
        normalized_channel[valid] = (volume[valid] - mean) / std
        normalized[channel] = normalized_channel

    # Replace any numerical issues defensively.
    np.nan_to_num(normalized, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
    return normalized

def _crop_with_padding(array, center, patch_size):
    """Crop a [C,X,Y,Z] or [X,Y,Z] array around center; pad if needed."""
    spatial_shape = array.shape[-3:]
    starts = [int(center[i]) - patch_size[i] // 2 for i in range(3)]
    ends = [starts[i] + patch_size[i] for i in range(3)]

    src_starts = [max(0, starts[i]) for i in range(3)]
    src_ends = [min(spatial_shape[i], ends[i]) for i in range(3)]
    pad_before = [max(0, -starts[i]) for i in range(3)]
    pad_after = [max(0, ends[i] - spatial_shape[i]) for i in range(3)]

    slices = tuple(slice(src_starts[i], src_ends[i]) for i in range(3))
    if array.ndim == 4:
        cropped = array[(slice(None),) + slices]
        pad_width = [(0, 0)] + list(zip(pad_before, pad_after))
    else:
        cropped = array[slices]
        pad_width = list(zip(pad_before, pad_after))

    return np.pad(cropped, pad_width, mode="constant", constant_values=0)

def extract_patch(image, label, patch_size=(64, 64, 64),
                  positive_probability=0.7, rng=None):
    """
    Extract a patch from image [C,X,Y,Z] and label [X,Y,Z].
    With probability positive_probability, center on a non-background voxel.
    Otherwise choose a random spatial center.
    """
    if rng is None:
        rng = np.random.default_rng()

    patch_size = tuple(int(v) for v in patch_size)
    if len(patch_size) != 3 or any(v <= 0 for v in patch_size):
        raise ValueError("patch_size must contain three positive integers")

    spatial_shape = label.shape
    positive_coords = np.argwhere(label > 0)

    choose_positive = len(positive_coords) > 0 and rng.random() < positive_probability
    if choose_positive:
        center = positive_coords[rng.integers(0, len(positive_coords))]
    else:
        center = np.array([
            rng.integers(0, spatial_shape[axis]) for axis in range(3)
        ])

    image_patch = _crop_with_padding(image, center, patch_size)
    label_patch = _crop_with_padding(label, center, patch_size)

    return image_patch.astype(np.float32), label_patch.astype(np.int64)

class BraTS3DPatchDataset(Dataset):
    """
    Lazy-loading patch dataset.
    One index corresponds to one sampled patch; cases can be repeated
    using patches_per_case. Each item returns:
      image: float32 [4, D, H, W]
      label: int64   [D, H, W]
    """
    def __init__(self, case_ids, case_files, patch_size=(64, 64, 64),
                 patches_per_case=1, positive_probability=0.7,
                 training=True, seed=42, canonical=True):
        self.case_ids = list(case_ids)
        self.case_files = case_files
        self.patch_size = tuple(patch_size)
        self.patches_per_case = int(patches_per_case)
        self.positive_probability = float(positive_probability)
        self.training = bool(training)
        self.seed = int(seed)
        self.canonical = bool(canonical)

        if not self.case_ids:
            raise ValueError("case_ids cannot be empty")
        if self.patches_per_case < 1:
            raise ValueError("patches_per_case must be >= 1")

    def __len__(self):
        return len(self.case_ids) * self.patches_per_case

    def __getitem__(self, index):
        case_index = index % len(self.case_ids)
        case_id = self.case_ids[case_index]

        image, label = load_case(self.case_files[case_id], canonical=self.canonical)
        image = normalize_modalities(image)

        # Deterministic sampling for inspection when training=False.
        if self.training:
            rng = np.random.default_rng()
        else:
            rng = np.random.default_rng(self.seed + index)

        image_patch, label_patch = extract_patch(
            image,
            label,
            patch_size=self.patch_size,
            positive_probability=self.positive_probability,
            rng=rng,
        )

        image_tensor = torch.from_numpy(np.ascontiguousarray(image_patch))
        label_tensor = torch.from_numpy(np.ascontiguousarray(label_patch)).long()

        return image_tensor, label_tensor
