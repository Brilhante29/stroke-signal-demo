from __future__ import annotations

import dataclasses
import hashlib

import numpy as np


@dataclasses.dataclass(frozen=True)
class CtSlice:
    patient_id: str
    slice_id: str
    image: np.ndarray
    mask: np.ndarray


def _ellipse(
    yy: np.ndarray,
    xx: np.ndarray,
    center_y: float,
    center_x: float,
    radius_y: float,
    radius_x: float,
) -> np.ndarray:
    return ((yy - center_y) / radius_y) ** 2 + ((xx - center_x) / radius_x) ** 2 <= 1


def generate_fixture(
    patient_count: int = 30,
    slices_per_patient: int = 4,
    image_size: int = 96,
    seed: int = 2023,
) -> list[CtSlice]:
    if patient_count < 15:
        raise ValueError("patient_count must be at least 15 for isolated splits")
    if slices_per_patient < 2:
        raise ValueError("slices_per_patient must be at least 2")
    if image_size < 48:
        raise ValueError("image_size must be at least 48")

    yy, xx = np.mgrid[:image_size, :image_size]
    fixture: list[CtSlice] = []
    for patient_index in range(patient_count):
        patient_id = f"patient-{patient_index:03d}"
        patient_rng = np.random.default_rng(seed + patient_index * 7919)
        center_y = image_size / 2 + patient_rng.uniform(-1.5, 1.5)
        center_x = image_size / 2 + patient_rng.uniform(-1.5, 1.5)
        outer = _ellipse(yy, xx, center_y, center_x, image_size * 0.43, image_size * 0.39)
        brain = _ellipse(yy, xx, center_y, center_x, image_size * 0.39, image_size * 0.35)
        skull = outer & ~brain

        for slice_index in range(slices_per_patient):
            rng = np.random.default_rng(seed + patient_index * 1009 + slice_index * 97)
            image = rng.normal(-55.0, 2.0, (image_size, image_size)).astype(np.float32)
            image[brain] = rng.normal(34.0, 6.5, int(brain.sum()))
            image[skull] = rng.normal(96.0, 3.0, int(skull.sum()))

            has_lesion = (patient_index + slice_index) % 5 != 0
            lesion = np.zeros_like(brain)
            if has_lesion:
                direction = -1 if patient_index % 2 else 1
                lesion_x = center_x + direction * image_size * (0.11 + 0.01 * slice_index)
                lesion_y = center_y + rng.uniform(-image_size * 0.11, image_size * 0.11)
                radius_x = rng.uniform(image_size * 0.045, image_size * 0.085)
                radius_y = rng.uniform(image_size * 0.055, image_size * 0.105)
                primary = _ellipse(yy, xx, lesion_y, lesion_x, radius_y, radius_x)
                secondary = _ellipse(
                    yy,
                    xx,
                    lesion_y + rng.uniform(-3.0, 3.0),
                    lesion_x + direction * rng.uniform(2.0, 4.5),
                    radius_y * rng.uniform(0.45, 0.7),
                    radius_x * rng.uniform(0.45, 0.7),
                )
                lesion = (primary | secondary) & brain
                image[lesion] = rng.normal(
                    58.0 + rng.uniform(-5.0, 5.0),
                    9.0,
                    int(lesion.sum()),
                )

            # Small hyperdense artifacts test false-positive control without
            # encoding the target mask into the segmentation implementation.
            if patient_index % 3 == 0:
                artifact_x = int(center_x - image_size * 0.18)
                artifact_y = int(center_y + image_size * 0.15)
                artifact = (xx - artifact_x) ** 2 + (yy - artifact_y) ** 2 <= 4
                image[artifact & brain] = rng.normal(62.0, 4.0, int((artifact & brain).sum()))

            fixture.append(
                CtSlice(
                    patient_id=patient_id,
                    slice_id=f"{patient_id}-slice-{slice_index:02d}",
                    image=image,
                    mask=lesion.astype(bool),
                )
            )
    return fixture


def fixture_digest(samples: list[CtSlice]) -> str:
    digest = hashlib.sha256()
    for sample in sorted(samples, key=lambda item: item.slice_id):
        digest.update(sample.patient_id.encode("ascii"))
        digest.update(b"\0")
        digest.update(sample.slice_id.encode("ascii"))
        digest.update(b"\0")
        digest.update(np.ascontiguousarray(sample.image).tobytes())
        digest.update(np.ascontiguousarray(sample.mask).tobytes())
    return f"sha256:{digest.hexdigest()}"
