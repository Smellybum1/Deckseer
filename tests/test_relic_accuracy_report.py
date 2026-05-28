from __future__ import annotations

import json
from pathlib import Path

import pytest

from deckseer.cli import main
from deckseer.data_loader import DeckseerData
from deckseer.models import ValidationError
from deckseer.relic_accuracy import build_relic_accuracy_report, load_relic_accuracy_scenarios


def _data() -> DeckseerData:
    return DeckseerData.load(Path("data"))


def _write_manifest(path: Path, scenarios: list[dict]) -> None:
    path.write_text(
        json.dumps(
            {
                "manifest_type": "relic_accuracy_scenarios",
                "scenarios": scenarios,
            }
        ),
        encoding="utf-8",
    )


def _scenario(**overrides) -> dict:
    scenario = {
        "id": "test_relic_scenario",
        "path": "tests/fixtures/relic_choice/elite_frontload.json",
        "expected_top_choice": "akabeko",
        "expected_reason_keywords": ["frontload"],
        "source": "test fixture",
        "review_status": "accepted",
    }
    scenario.update(overrides)
    return scenario


def test_relic_accuracy_manifest_loads_reviewed_scenarios() -> None:
    scenarios = load_relic_accuracy_scenarios(Path("data/relic_accuracy/scenarios.json"))

    assert len(scenarios) == 6
    assert scenarios[0].id == "elite_frontload"
    assert scenarios[0].expected_top_choice == "akabeko"
    assert scenarios[0].expected_reason_keywords == ("frontload", "elite_prep")
    assert scenarios[-3].id == "early_consistency_ring"
    assert scenarios[-2].id == "colorless_deck_quality"
    assert scenarios[-1].id == "skill_dense_letter_opener"


def test_relic_accuracy_report_scores_all_scenarios() -> None:
    report = build_relic_accuracy_report(_data(), manifest_path=Path("data/relic_accuracy/scenarios.json"))

    assert report["report_type"] == "relic_accuracy_report"
    assert report["status"] == "pass"
    assert report["summary"]["scenarios"] == 6
    assert report["summary"]["passed"] == 6
    assert report["summary"]["failed"] == 0
    assert report["summary"]["failed_scenario_ids"] == []
    assert report["summary"]["review_status_counts"] == {"accepted": 6}
    assert report["summary"]["passed_by_review_status"] == {"accepted": 6}
    assert report["summary"]["failed_by_review_status"] == {}
    assert report["scenarios"][0]["actual_top_choice"] == "akabeko"
    assert report["scenarios"][0]["matched_reason_keywords"] == ["frontload", "elite_prep"]
    assert report["scenarios"][-3]["actual_top_choice"] == "ring_of_the_snake"
    assert report["scenarios"][-2]["actual_top_choice"] == "lead_paperweight"
    assert report["scenarios"][-1]["actual_top_choice"] == "letter_opener"


def test_relic_accuracy_report_cli_text_smoke(capsys) -> None:
    status = main(["relic-accuracy-report", "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Relic Accuracy Report: PASS" in captured.out
    assert "Scenarios: 6 | Passed: 6 | Failed: 0" in captured.out
    assert "Review statuses: accepted=6" in captured.out
    assert "PASS elite_frontload: expected akabeko, got akabeko" in captured.out
    assert "PASS early_consistency_ring: expected ring_of_the_snake, got ring_of_the_snake" in captured.out
    assert "PASS skill_dense_letter_opener: expected letter_opener, got letter_opener" in captured.out


def test_relic_accuracy_report_cli_json_smoke(capsys) -> None:
    status = main(["relic-accuracy-report", "--format", "json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["report_type"] == "relic_accuracy_report"
    assert payload["summary"]["scenarios"] == 6
    assert payload["summary"]["failed"] == 0
    assert payload["summary"]["review_status_counts"] == {"accepted": 6}
    assert payload["scenarios"][0]["expected_reason_keywords"] == ["frontload", "elite_prep"]


def test_relic_accuracy_report_cli_can_fail_on_mismatch(tmp_path, capsys) -> None:
    manifest_path = tmp_path / "bad_relic_accuracy_manifest.json"
    _write_manifest(manifest_path, [_scenario(expected_top_choice="kunai")])

    status = main(["relic-accuracy-report", "--manifest", str(manifest_path), "--fail-on-mismatch"])

    captured = capsys.readouterr()

    assert status == 1
    assert "Relic Accuracy Report: FAIL" in captured.out
    assert "FAIL test_relic_scenario: expected kunai, got akabeko" in captured.out


def test_relic_accuracy_manifest_rejects_duplicate_ids(tmp_path) -> None:
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(manifest_path, [_scenario(), _scenario()])

    with pytest.raises(ValidationError, match="duplicate scenario id"):
        load_relic_accuracy_scenarios(manifest_path)


def test_relic_accuracy_manifest_rejects_empty_reason_keywords(tmp_path) -> None:
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(manifest_path, [_scenario(expected_reason_keywords=[])])

    with pytest.raises(ValidationError, match="at least one keyword"):
        load_relic_accuracy_scenarios(manifest_path)


def test_relic_accuracy_manifest_rejects_unsupported_review_status(tmp_path) -> None:
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(manifest_path, [_scenario(review_status="maybe")])

    with pytest.raises(ValidationError, match="review_status must be one of"):
        load_relic_accuracy_scenarios(manifest_path)
