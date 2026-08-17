from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
V1_PATH = ROOT / "benchmarks/results/baseline.json"
V2_PATH = ROOT / "benchmarks/publication/stroke-signal-v2.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def git_blob(commit: str, path: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{commit}:{path}"],
        capture_output=True,
        check=False,
    )
    require(completed.returncode == 0, f"source commit lacks {path}")
    return completed.stdout


def main() -> None:
    manifest = (ROOT / "project.yaml").read_text(encoding="utf-8")
    published = re.search(r"(?m)^status:\s*published\s*$", manifest) is not None
    if not V2_PATH.is_file():
        require(not published, "published project requires V2 evidence")
        print("publication_evidence=not-applicable")
        return
    v1 = json.loads(V1_PATH.read_text(encoding="utf-8"))
    v2 = json.loads(V2_PATH.read_text(encoding="utf-8"))
    schema = json.loads(
        (ROOT / ".portfolio/contracts/benchmark-result-v2.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(v2)
    require(v2["project"] == "stroke-signal-demo", "unexpected V2 project")
    require(v2["execution"]["repeat"] == 3, "publication requires three runs")
    primary = [metric for metric in v2["metrics"] if metric["name"] == "segmentation_dice"]
    require(len(primary) == 1, "V2 must contain one primary metric")
    require(primary[0]["value"] == v1["value"], "V1/V2 primary metric mismatch")
    require(primary[0]["samples"] == v1["samples"], "V1/V2 samples mismatch")
    require(all(metric["failures"] == 0 for metric in v2["metrics"]), "V2 contains failures")
    require(v2["environment"]["split_unit"] == "patient", "V2 split unit mismatch")
    require(v2["environment"]["test_used_for_selection"] is False, "V2 test leakage")

    commit = v2["provenance"]["source_commit"]
    require(re.fullmatch(r"[0-9a-f]{40}", commit) is not None, "invalid source commit")
    require(
        v2["workload"]["fixture_digest"]
        == digest(git_blob(commit, "data/clinical-fixture-manifest.json")),
        "fixture manifest digest mismatch",
    )
    require(
        v2["workload"]["config_digest"] == digest(git_blob(commit, "benchmarks/workload.json")),
        "workload digest mismatch",
    )
    require(
        v2["provenance"]["dependency_lock_digest"]
        == digest(git_blob(commit, "constraints.lock")),
        "dependency lock digest mismatch",
    )
    for field in ("image_digest", "artifact_digest"):
        require(
            re.fullmatch(r"sha256:[0-9a-f]{64}", v2["provenance"][field]) is not None,
            f"invalid {field}",
        )
    require(
        "result_path: benchmarks/publication/stroke-signal-v2.json" in manifest,
        "project manifest does not point to V2 evidence",
    )
    serialized = json.dumps({"v1": v1, "v2": v2})
    for forbidden in ("C:\\Users\\", "github" + "_pat_", "gh" + "p_"):
        require(forbidden not in serialized, f"forbidden value in evidence: {forbidden}")
    print("publication_evidence=passed")


if __name__ == "__main__":
    main()
