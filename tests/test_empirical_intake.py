from __future__ import annotations

import json
from pathlib import Path

from deckseer.cli import main
from deckseer.empirical_intake import build_empirical_intake_report, load_empirical_intake
from deckseer.models import ValidationError
from deckseer.qa import discover_empirical_stats


def test_empirical_intake_manifest_loads() -> None:
    entries = load_empirical_intake(Path("data/empirical/intake_queue.json"))

    assert len(entries) == 1
    assert entries[0].id == "necrobinder_initial_sts2_fun_review"
    assert entries[0].character == "necrobinder"
    assert entries[0].review_status == "proposed"


def test_empirical_intake_report_summarizes_proposed_entries() -> None:
    report = build_empirical_intake_report(Path("data/empirical/intake_queue.json"))

    assert report["intake_type"] == "empirical_intake_queue"
    assert report["status"] == "review"
    assert report["summary"]["entries"] == 1
    assert report["summary"]["proposed"] == 1
    assert report["summary"]["entries_by_character"] == {"necrobinder": 1}


def test_empirical_intake_rejects_numeric_stat_fields(tmp_path) -> None:
    manifest = tmp_path / "bad_intake.json"
    manifest.write_text(
        json.dumps(
            {
                "manifest_type": "empirical_intake_queue",
                "entries": [
                    {
                        "id": "bad_numeric_entry",
                        "character": "necrobinder",
                        "topic": "Bad numeric entry",
                        "review_status": "proposed",
                        "candidate_notes": "Should not include numeric evidence yet.",
                        "sample_size": 500,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    try:
        load_empirical_intake(manifest)
    except ValidationError as exc:
        assert "must not include numeric empirical stat fields" in str(exc)
    else:
        raise AssertionError("Expected numeric intake fields to fail validation")


def test_empirical_intake_rejects_duplicate_ids(tmp_path) -> None:
    manifest = tmp_path / "duplicate_intake.json"
    manifest.write_text(
        json.dumps(
            {
                "manifest_type": "empirical_intake_queue",
                "entries": [
                    {
                        "id": "duplicate",
                        "character": "necrobinder",
                        "topic": "One",
                        "review_status": "proposed",
                        "candidate_notes": "First.",
                    },
                    {
                        "id": "duplicate",
                        "character": "silent",
                        "topic": "Two",
                        "review_status": "proposed",
                        "candidate_notes": "Second.",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    try:
        load_empirical_intake(manifest)
    except ValidationError as exc:
        assert "duplicate empirical intake ids" in str(exc)
    else:
        raise AssertionError("Expected duplicate intake ids to fail validation")


def test_empirical_intake_is_not_discovered_as_active_empirical_stats() -> None:
    paths = discover_empirical_stats(Path("data"))

    assert all(path.name != "intake_queue.json" for path in paths)


def test_empirical_intake_cli_text_smoke(capsys) -> None:
    status = main(["empirical-intake", "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Empirical Intake: REVIEW" in captured.out
    assert "Entries by character: necrobinder=1" in captured.out
    assert "necrobinder_initial_sts2_fun_review" in captured.out


def test_empirical_intake_cli_json_smoke(capsys) -> None:
    status = main(["empirical-intake", "--format", "json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["intake_type"] == "empirical_intake_queue"
    assert payload["summary"]["proposed"] == 1
    assert payload["entries"][0]["review_status"] == "proposed"
