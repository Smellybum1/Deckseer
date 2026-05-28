from __future__ import annotations

import json
from pathlib import Path

from deckseer.accuracy import build_accuracy_report, load_accuracy_scenarios
from deckseer.cli import main
from deckseer.data_loader import DeckseerData
from deckseer.models import ValidationError

import pytest


def _data() -> DeckseerData:
    return DeckseerData.load(Path("data"))


def _write_manifest(path: Path, scenarios: list[dict]) -> None:
    path.write_text(
        json.dumps(
            {
                "manifest_type": "accuracy_scenarios",
                "scenarios": scenarios,
            }
        ),
        encoding="utf-8",
    )


def _scenario(**overrides) -> dict:
    scenario = {
        "id": "test_scenario",
        "path": "tests/fixtures/scenarios/early_act1_low_frontload.json",
        "expected_top_choice": "pommel_strike",
        "expected_reason_keywords": ["frontload"],
        "source": "test fixture",
        "review_status": "accepted",
    }
    scenario.update(overrides)
    return scenario


def test_accuracy_manifest_loads_reviewed_scenarios() -> None:
    scenarios = load_accuracy_scenarios(Path("data/accuracy/scenarios.json"))

    assert len(scenarios) == 10
    assert scenarios[0].id == "early_act1_low_frontload"
    assert scenarios[0].expected_top_choice == "pommel_strike"
    assert scenarios[0].expected_reason_keywords == ("frontload",)


def test_accuracy_report_scores_all_scenarios() -> None:
    report = build_accuracy_report(_data(), manifest_path=Path("data/accuracy/scenarios.json"))

    assert report["report_type"] == "accuracy_report"
    assert report["status"] == "pass"
    assert report["summary"]["scenarios"] == 10
    assert report["summary"]["passed"] == 10
    assert report["summary"]["failed"] == 0
    assert report["summary"]["failed_scenario_ids"] == []
    assert report["summary"]["review_status_counts"] == {"accepted": 10}
    assert report["summary"]["passed_by_review_status"] == {"accepted": 10}
    assert report["summary"]["failed_by_review_status"] == {}
    assert report["scenarios"][0]["actual_top_choice"] == "pommel_strike"
    assert report["scenarios"][0]["matched_reason_keywords"] == ["frontload"]


def test_accuracy_report_cli_text_smoke(capsys) -> None:
    status = main(["accuracy-report", "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Accuracy Report: PASS" in captured.out
    assert "Scenarios: 10 | Passed: 10 | Failed: 0" in captured.out
    assert "Review statuses: accepted=10" in captured.out
    assert "PASS early_act1_low_frontload: expected pommel_strike, got pommel_strike" in captured.out
    assert "PASS necrobinder_forbidden_grimoire_frontload_guard: expected unleash, got unleash" in captured.out


def test_accuracy_report_cli_json_smoke(capsys) -> None:
    status = main(["accuracy-report", "--format", "json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["report_type"] == "accuracy_report"
    assert payload["summary"]["scenarios"] == 10
    assert payload["summary"]["failed"] == 0
    assert payload["summary"]["review_status_counts"] == {"accepted": 10}
    assert payload["scenarios"][0]["expected_reason_keywords"] == ["frontload"]


def test_accuracy_report_cli_can_fail_on_mismatch(tmp_path, capsys) -> None:
    manifest_path = tmp_path / "bad_accuracy_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "manifest_type": "accuracy_scenarios",
                "scenarios": [
                    {
                        "id": "bad_expected_choice",
                        "path": "tests/fixtures/scenarios/early_act1_low_frontload.json",
                        "expected_top_choice": "inflame",
                        "expected_reason_keywords": ["frontload"],
                        "source": "test fixture",
                        "review_status": "accepted",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    status = main(["accuracy-report", "--manifest", str(manifest_path), "--fail-on-mismatch"])

    captured = capsys.readouterr()

    assert status == 1
    assert "Accuracy Report: FAIL" in captured.out
    assert "FAIL bad_expected_choice: expected inflame, got pommel_strike" in captured.out


def test_accuracy_manifest_rejects_duplicate_ids(tmp_path) -> None:
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(manifest_path, [_scenario(), _scenario()])

    with pytest.raises(ValidationError, match="duplicate scenario id"):
        load_accuracy_scenarios(manifest_path)


def test_accuracy_manifest_rejects_empty_reason_keywords(tmp_path) -> None:
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(manifest_path, [_scenario(expected_reason_keywords=[])])

    with pytest.raises(ValidationError, match="at least one keyword"):
        load_accuracy_scenarios(manifest_path)


def test_accuracy_manifest_rejects_unsupported_review_status(tmp_path) -> None:
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(manifest_path, [_scenario(review_status="maybe")])

    with pytest.raises(ValidationError, match="review_status must be one of"):
        load_accuracy_scenarios(manifest_path)
