from __future__ import annotations

import json
from pathlib import Path

from deckseer.cli import main
from deckseer.data_loader import DeckseerData
from deckseer.empirical_draft import build_empirical_draft_report, load_empirical_draft
from deckseer.models import ValidationError
from deckseer.qa import discover_empirical_stats


FIXTURES = Path("tests/fixtures/empirical")
NECROBINDER_WORKSHEET = Path("data/empirical/drafts/necrobinder_sts2fun_capture_template.json")
CURRENT_PATCH_WORKSHEET = Path("data/empirical/drafts/necrobinder_sts2fun_current_patch_triage_batch.json")


def test_valid_traceable_draft_loads() -> None:
    entries = load_empirical_draft(FIXTURES / "valid_traceable_draft.json")

    assert len(entries) == 1
    assert entries[0].id == "silent_adrenaline_sts2fun_2026_05_23"
    assert entries[0].stat.card_id == "adrenaline"
    assert entries[0].stat.source_url == "https://sts2.fun/"
    assert entries[0].stat.review_status == "accepted"


def test_draft_rejects_missing_provenance(tmp_path) -> None:
    draft_path = tmp_path / "missing_provenance.json"
    payload = _draft_payload()
    del payload["entries"][0]["source_url"]
    draft_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_empirical_draft(draft_path)
    except ValidationError as exc:
        assert "source_url is required" in str(exc)
    else:
        raise AssertionError("Expected missing provenance to fail validation")


def test_draft_rejects_missing_numeric_stat(tmp_path) -> None:
    draft_path = tmp_path / "missing_numeric.json"
    payload = _draft_payload()
    del payload["entries"][0]["sample_size"]
    draft_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_empirical_draft(draft_path)
    except ValidationError as exc:
        assert "sample_size is required" in str(exc)
    else:
        raise AssertionError("Expected missing numeric field to fail validation")


def test_draft_rejects_null_required_field(tmp_path) -> None:
    draft_path = tmp_path / "null_card_id.json"
    payload = _draft_payload()
    payload["entries"][0]["card_id"] = None
    draft_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_empirical_draft(draft_path)
    except ValidationError as exc:
        assert "card_id is required for empirical draft rows and must not be null" in str(exc)
    else:
        raise AssertionError("Expected null required field to fail validation")


def test_draft_rejects_invalid_review_status(tmp_path) -> None:
    draft_path = tmp_path / "bad_review_status.json"
    payload = _draft_payload()
    payload["entries"][0]["review_status"] = "seed"
    draft_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_empirical_draft(draft_path)
    except ValidationError as exc:
        assert "review_status must be one of" in str(exc)
    else:
        raise AssertionError("Expected invalid review_status to fail validation")


def test_draft_rejects_duplicate_ids(tmp_path) -> None:
    draft_path = tmp_path / "duplicate_ids.json"
    payload = _draft_payload()
    duplicate = dict(payload["entries"][0])
    duplicate["card_id"] = "glacier"
    duplicate["character"] = "defect"
    duplicate["patch"] = "v0.102.0"
    payload["entries"].append(duplicate)
    draft_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_empirical_draft(draft_path)
    except ValidationError as exc:
        assert "duplicate empirical draft ids" in str(exc)
    else:
        raise AssertionError("Expected duplicate draft ids to fail validation")


def test_draft_rejects_duplicate_card_patch_source_rows(tmp_path) -> None:
    draft_path = tmp_path / "duplicate_card_source.json"
    payload = _draft_payload()
    duplicate = dict(payload["entries"][0])
    duplicate["id"] = "duplicate_source_row"
    payload["entries"].append(duplicate)
    draft_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_empirical_draft(draft_path)
    except ValidationError as exc:
        assert "duplicate empirical draft card/patch/source rows" in str(exc)
    else:
        raise AssertionError("Expected duplicate card/source rows to fail validation")


def test_clean_draft_report_is_promotion_ready() -> None:
    data = DeckseerData.load(Path("data"))

    report = build_empirical_draft_report(data, FIXTURES / "valid_traceable_draft.json")

    assert report["draft_type"] == "empirical_stat_draft"
    assert report["status"] == "pass"
    assert report["summary"]["promotion_ready"] is True
    assert report["summary"]["audit_flags"] == 0
    assert report["summary"]["rows_by_character"] == {"silent": 1}


def test_draft_with_audit_flags_reports_review_needed() -> None:
    data = DeckseerData.load(Path("data"))

    report = build_empirical_draft_report(data, FIXTURES / "review_flag_traceable_draft.json")

    assert report["status"] == "review"
    assert report["summary"]["promotion_ready"] is False
    assert report["summary"]["audit_flags"] == 1
    assert report["audit_preview"]["summary"]["flags_by_code"] == {"low_prior_strong_empirical": 1}


def test_draft_files_are_not_discovered_as_active_empirical_stats() -> None:
    assert all("drafts" not in path.parts for path in discover_empirical_stats(Path("data")))


def test_necrobinder_capture_worksheet_exists_and_is_valid_json() -> None:
    payload = json.loads(NECROBINDER_WORKSHEET.read_text(encoding="utf-8"))

    assert payload["draft_type"] == "empirical_stat_draft"
    assert payload["entries"][0]["id"] == "necrobinder_sts2fun_first_capture"
    assert payload["entries"][0]["character"] == "necrobinder"
    assert payload["entries"][0]["card_id"] is None
    assert payload["entries"][0]["sample_size"] is None
    assert payload["entries"][0]["pick_rate"] is None
    assert payload["entries"][0]["win_rate"] is None
    assert payload["entries"][0]["impact"] is None


def test_necrobinder_capture_worksheet_fails_with_clear_null_guidance(capsys) -> None:
    status = main(["empirical-draft-check", str(NECROBINDER_WORKSHEET), "--format", "text"])

    captured = capsys.readouterr()

    assert status == 2
    assert "card_id is required for empirical draft rows and must not be null" in captured.err


def test_current_patch_worksheet_strict_draft_check_reports_review_flags(capsys) -> None:
    status = main(["empirical-draft-check", str(CURRENT_PATCH_WORKSHEET), "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Empirical Draft: REVIEW" in captured.out
    assert "Entries: 3 | Audit flags: 2 | Promotion ready: no" in captured.out
    assert "patch_mismatch" in captured.out


def test_empirical_draft_cli_text_shows_promotion_readiness(capsys) -> None:
    status = main(["empirical-draft-check", "tests/fixtures/empirical/valid_traceable_draft.json", "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Empirical Draft: PASS" in captured.out
    assert "Promotion ready: yes" in captured.out
    assert "Rows by character: silent=1" in captured.out


def test_empirical_draft_cli_json_includes_audit_preview(capsys) -> None:
    status = main(["empirical-draft-check", "tests/fixtures/empirical/valid_traceable_draft.json", "--format", "json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["summary"]["promotion_ready"] is True
    assert payload["audit_preview"]["summary"]["flags"] == 0
    assert payload["caveats"]


def test_empirical_draft_cli_fail_on_review_returns_failure(capsys) -> None:
    status = main(["empirical-draft-check", "tests/fixtures/empirical/review_flag_traceable_draft.json", "--fail-on-review"])

    captured = capsys.readouterr()

    assert status == 1
    assert "Empirical Draft: REVIEW" in captured.out
    assert "low_prior_strong_empirical" in captured.out


def test_project_qa_reports_review_with_active_empirical_flags(capsys) -> None:
    status = main(["qa", "--check-recommendation-baseline", "--check-accuracy"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Project QA: REVIEW" in captured.out
    assert "Empirical audits: 6 | Flags: 14" in captured.out


def _draft_payload() -> dict:
    return {
        "draft_type": "empirical_stat_draft",
        "entries": [
            {
                "id": "silent_adrenaline_sts2fun_2026_05_23",
                "card_id": "adrenaline",
                "character": "silent",
                "patch": "v0.102.0",
                "source": "STS2.fun manual capture test fixture",
                "source_url": "https://sts2.fun/",
                "captured_at": "2026-05-23",
                "stat_definition": "Test fixture impact value for draft validation.",
                "reviewer_notes": "Traceable test row.",
                "sample_size": 1400,
                "pick_rate": 0.54,
                "win_rate": 0.66,
                "impact": 0.11,
                "act": "all",
                "ascension": "all",
                "review_status": "accepted",
            }
        ],
    }
