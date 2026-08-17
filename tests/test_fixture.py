from __future__ import annotations

import pytest

from stroke_signal.fixture import fixture_digest, generate_fixture


def test_fixture_is_deterministic_and_contains_positive_and_negative_slices() -> None:
    first = generate_fixture(15, 2, 48, 7)
    second = generate_fixture(15, 2, 48, 7)
    assert fixture_digest(first) == fixture_digest(second)
    assert len(first) == 30
    assert any(sample.mask.any() for sample in first)
    assert any(not sample.mask.any() for sample in first)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"patient_count": 14}, "patient_count"),
        ({"slices_per_patient": 1}, "slices_per_patient"),
        ({"image_size": 47}, "image_size"),
    ],
)
def test_fixture_rejects_invalid_shape(kwargs: dict, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        generate_fixture(**kwargs)
