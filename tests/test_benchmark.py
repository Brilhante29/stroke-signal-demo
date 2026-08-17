from __future__ import annotations

import json
from pathlib import Path

from stroke_signal.benchmark import METHOD_SCOPE, PAPER_DOI, load_workload, run_benchmark
from stroke_signal.cli import main


def test_benchmark_writes_leakage_safe_result(tmp_path: Path) -> None:
    output = tmp_path / "benchmark.json"
    result = run_benchmark(15, 2, 48, 23, (-3.0, 0.0, 3.0), output)
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert result.value == payload["metrics"]["segmentation_dice"]
    assert payload["split"]["unit"] == "patient"
    assert payload["split"]["overlap_count"] == 0
    assert payload["split"]["test_used_for_selection"] is False
    assert payload["dataset"]["clinical_use"] is False
    assert payload["proof"]["paper_doi"] == PAPER_DOI
    assert payload["proof"]["scope"] == METHOD_SCOPE
    confusion_total = sum(
        payload["metrics"][name]
        for name in ("true_negative", "false_positive", "false_negative", "true_positive")
    )
    assert confusion_total == payload["measured_iterations"] * 48 * 48


def test_cli_demo_and_benchmark(capsys, tmp_path: Path) -> None:
    assert main(
        ["demo", "--patients", "15", "--slices-per-patient", "2", "--image-size", "48"]
    ) == 0
    assert "confusion_matrix=" in capsys.readouterr().out
    output = tmp_path / "cli.json"
    assert main([
        "benchmark",
        "--patients", "15",
        "--slices-per-patient", "2",
        "--image-size", "48",
        "--output", str(output),
    ]) == 0
    assert output.is_file()


def test_load_workload(tmp_path: Path) -> None:
    path = tmp_path / "workload.json"
    path.write_text('{"seed": 42}', encoding="utf-8")
    assert load_workload(path) == {"seed": 42}
