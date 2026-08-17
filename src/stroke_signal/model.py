from __future__ import annotations

import dataclasses
import hashlib
import json
from collections.abc import Iterable, Sequence

import numpy as np
from scipy import ndimage

from stroke_signal.domain import PatientSplit, PixelMetrics
from stroke_signal.fixture import CtSlice


@dataclasses.dataclass(frozen=True)
class SegmentationModel:
    stopping_threshold: float
    minimum_component_pixels: int = 12
    calibration_threshold: float = 0.0

    @property
    def artifact_sha256(self) -> str:
        payload = json.dumps(dataclasses.asdict(self), sort_keys=True, separators=(",", ":"))
        return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def split_patients(samples: Sequence[CtSlice], seed: int) -> PatientSplit:
    patients = sorted({sample.patient_id for sample in samples})
    if len(patients) < 15:
        raise ValueError("at least 15 patients are required")
    shuffled = np.random.default_rng(seed).permutation(patients).tolist()
    train_count = int(len(shuffled) * 0.6)
    validation_count = int(len(shuffled) * 0.2)
    split = PatientSplit(
        train=tuple(sorted(shuffled[:train_count])),
        validation=tuple(sorted(shuffled[train_count : train_count + validation_count])),
        test=tuple(sorted(shuffled[train_count + validation_count :])),
    )
    split.assert_isolated()
    return split


def samples_for_patients(
    samples: Sequence[CtSlice], patient_ids: Iterable[str]
) -> list[CtSlice]:
    selected = set(patient_ids)
    return [sample for sample in samples if sample.patient_id in selected]


def _brain_support(image: np.ndarray) -> np.ndarray:
    soft_tissue = (image > 0) & (image < 85)
    labels, count = ndimage.label(soft_tissue)
    if count == 0:
        return np.zeros_like(image, dtype=bool)
    sizes = ndimage.sum(soft_tissue, labels, index=range(1, count + 1))
    brain = labels == int(np.argmax(sizes) + 1)
    return ndimage.binary_erosion(ndimage.binary_fill_holes(brain), iterations=1)


def fit_calibration_threshold(samples: Sequence[CtSlice]) -> float:
    lesion_values: list[np.ndarray] = []
    background_values: list[np.ndarray] = []
    for sample in samples:
        support = _brain_support(sample.image)
        if sample.mask.any():
            lesion_values.append(sample.image[sample.mask])
        background_values.append(sample.image[support & ~sample.mask])
    if not lesion_values or not background_values:
        raise ValueError("training samples must contain lesion and background pixels")
    lesion_floor = float(np.percentile(np.concatenate(lesion_values), 12.5))
    background_ceiling = float(np.percentile(np.concatenate(background_values), 99.5))
    return (lesion_floor + background_ceiling) / 2.0


def quadrant_seed_search(mask: np.ndarray) -> tuple[int, int] | None:
    if mask.ndim != 2:
        raise ValueError("seed search requires a two-dimensional mask")
    if not mask.any():
        return None

    def search(y0: int, y1: int, x0: int, x1: int) -> tuple[int, int]:
        center_y = (y0 + y1 - 1) // 2
        center_x = (x0 + x1 - 1) // 2
        if mask[center_y, center_x] or (y1 - y0 == 1 and x1 - x0 == 1):
            return center_y, center_x
        middle_y = (y0 + y1) // 2
        middle_x = (x0 + x1) // 2
        quadrants = [
            (y0, middle_y, x0, middle_x),
            (y0, middle_y, middle_x, x1),
            (middle_y, y1, x0, middle_x),
            (middle_y, y1, middle_x, x1),
        ]
        populated = [
            (int(mask[qy0:qy1, qx0:qx1].sum()), index, (qy0, qy1, qx0, qx1))
            for index, (qy0, qy1, qx0, qx1) in enumerate(quadrants)
            if qy1 > qy0 and qx1 > qx0
        ]
        _, _, selected = max(populated, key=lambda item: (item[0], -item[1]))
        return search(*selected)

    seed = search(0, mask.shape[0], 0, mask.shape[1])
    if mask[seed]:
        return seed
    coordinates = np.argwhere(mask)
    nearest = coordinates[np.argmin(np.sum((coordinates - np.asarray(seed)) ** 2, axis=1))]
    return int(nearest[0]), int(nearest[1])


def segment_slice(image: np.ndarray, model: SegmentationModel) -> np.ndarray:
    if image.ndim != 2:
        raise ValueError("segmentation requires a two-dimensional image")
    support = _brain_support(image)
    candidates = support & (image >= model.stopping_threshold)
    coarse = support & (image >= model.stopping_threshold + 3.0)
    seed = quadrant_seed_search(coarse if coarse.any() else candidates)
    if seed is None:
        return np.zeros_like(image, dtype=bool)

    labels, _ = ndimage.label(candidates)
    selected_label = int(labels[seed])
    if selected_label == 0:
        return np.zeros_like(image, dtype=bool)
    prediction = labels == selected_label
    if int(prediction.sum()) < model.minimum_component_pixels:
        return np.zeros_like(image, dtype=bool)
    prediction = ndimage.binary_closing(prediction, iterations=1)
    return ndimage.binary_fill_holes(prediction).astype(bool)


def confusion_counts(samples: Sequence[CtSlice], model: SegmentationModel) -> PixelMetrics:
    true_negative = false_positive = false_negative = true_positive = 0
    for sample in samples:
        prediction = segment_slice(sample.image, model)
        truth = sample.mask
        true_positive += int(np.count_nonzero(prediction & truth))
        true_negative += int(np.count_nonzero(~prediction & ~truth))
        false_positive += int(np.count_nonzero(prediction & ~truth))
        false_negative += int(np.count_nonzero(~prediction & truth))
    return PixelMetrics(true_negative, false_positive, false_negative, true_positive)


def select_model(
    training_samples: Sequence[CtSlice],
    validation_samples: Sequence[CtSlice],
    threshold_offsets: Sequence[float],
) -> SegmentationModel:
    if not threshold_offsets:
        raise ValueError("threshold_offsets cannot be empty")
    calibration = fit_calibration_threshold(training_samples)
    candidates = [
        SegmentationModel(calibration + float(offset), calibration_threshold=calibration)
        for offset in threshold_offsets
    ]
    scored = [(confusion_counts(validation_samples, model).dice, model) for model in candidates]
    return max(scored, key=lambda item: (item[0], -item[1].stopping_threshold))[1]
