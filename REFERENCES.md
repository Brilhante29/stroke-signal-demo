# References And Reuse

| Reference | Used for | Reuse boundary |
|---|---|---|
| [Divisible Cell-Segmentation, IJCNN 2023](https://doi.org/10.1109/IJCNN54540.2023.10191320) | Paper identity, clinical task, reported metrics, automatic initialization and segmentation stages | Methodology reference; no paper code, weights, or images copied |
| [UFC doctoral thesis](https://repositorio.ufc.br/handle/riufc/72342) | Dataset description, quadrant initialization, R50-FPN configuration, metrics and limitations | Public document consulted; the 25-exam dataset is not redistributed |
| [PhysioNet CT-ICH](https://physionet.org/content/ct-ich/1.3.1/) | Candidate external-validation dataset and patient-level split rationale | Not downloaded or used; current access requires a data-use agreement |
| [NumPy](https://numpy.org/doc/stable/) | Deterministic fixture and array operations | BSD-3-Clause dependency |
| [SciPy ndimage](https://docs.scipy.org/doc/scipy/reference/ndimage.html) | Labeling, morphology, and connected components | BSD-3-Clause dependency |

All implementation, tests, manifests, and benchmark harness code in this repository are project-specific. The synthetic fixture contains no DICOM file, patient record, expert annotation, or image copied from the paper or another dataset.
