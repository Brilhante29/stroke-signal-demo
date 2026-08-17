from __future__ import annotations

import numpy as np
import pytest

from stroke_signal.fixture import CtSlice, generate_fixture
from stroke_signal.model import (
    SegmentationModel,
    confusion_counts,
    fit_calibration_threshold,
    quadrant_seed_search,
    samples_for_patients,
    segment_slice,
    select_model,
    split_patients,
)


@pytest.fixture(scope="module")
def fixture():
    return generate_fixture(15, 2, 48, 17)


def test_patient_split_is_deterministic_and_isolated(fixture) -> None:
    first = split_patients(fixture, 17)
    second = split_patients(fixture, 17)
    assert first == second
    assert (len(first.train), len(first.validation), len(first.test)) == (9, 3, 3)
    assert not (set(first.train) & set(first.test))


def test_split_rejects_too_few_patients() -> None:
    sample = CtSlice("one", "one-0", np.zeros((48, 48)), np.zeros((48, 48), bool))
    with pytest.raises(ValueError, match="15 patients"):
        split_patients([sample], 1)


def test_samples_for_patients_filters_by_identity(fixture) -> None:
    selected = samples_for_patients(fixture, [fixture[0].patient_id])
    assert len(selected) == 2
    assert {sample.patient_id for sample in selected} == {fixture[0].patient_id}


def test_quadrant_seed_search_handles_empty_and_rejects_non_image() -> None:
    assert quadrant_seed_search(np.zeros((8, 8), dtype=bool)) is None
    with pytest.raises(ValueError, match="two-dimensional"):
        quadrant_seed_search(np.zeros((2, 2, 2), dtype=bool))


def test_quadrant_seed_is_inside_candidate() -> None:
    mask = np.zeros((16, 16), dtype=bool)
    mask[2:5, 11:14] = True
    seed = quadrant_seed_search(mask)
    assert seed is not None and mask[seed]


def test_model_selection_uses_training_and_validation_only(fixture) -> None:
    split = split_patients(fixture, 17)
    training = samples_for_patients(fixture, split.train)
    validation = samples_for_patients(fixture, split.validation)
    model = select_model(training, validation, (-4.0, 0.0, 4.0))
    assert 40.0 < model.stopping_threshold < 70.0
    assert model.artifact_sha256.startswith("sha256:")
    assert model == select_model(training, validation, (-4.0, 0.0, 4.0))


def test_model_selection_and_calibration_reject_invalid_inputs(fixture) -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        select_model(fixture, fixture, ())
    negative = [sample for sample in fixture if not sample.mask.any()]
    with pytest.raises(ValueError, match="lesion and background"):
        fit_calibration_threshold(negative)


def test_segmentation_and_confusion_are_consistent(fixture) -> None:
    split = split_patients(fixture, 17)
    training = samples_for_patients(fixture, split.train)
    validation = samples_for_patients(fixture, split.validation)
    test = samples_for_patients(fixture, split.test)
    model = select_model(training, validation, (-4.0, 0.0, 4.0))
    prediction = segment_slice(test[0].image, model)
    assert prediction.shape == test[0].mask.shape
    counts = confusion_counts(test, model)
    assert counts.total == sum(sample.mask.size for sample in test)
    assert 0.0 <= counts.dice <= 1.0


def test_segmentation_rejects_non_image_and_small_component() -> None:
    with pytest.raises(ValueError, match="two-dimensional"):
        segment_slice(np.zeros((3, 3, 3)), SegmentationModel(50.0))
    image = np.full((48, 48), -50.0)
    image[5:43, 5:43] = 30.0
    image[20, 20] = 80.0
    assert not segment_slice(image, SegmentationModel(50.0, 12)).any()
