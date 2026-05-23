from __future__ import annotations

import json
from pathlib import Path

from deckseer.cli import main
from deckseer.empirical_worksheet import build_empirical_worksheet_report
from deckseer.qa import discover_empirical_stats


BATCH_WORKSHEET = Path("data/empirical/drafts/necrobinder_sts2fun_capture_batch.json")
CURRENT_PATCH_WORKSHEET = Path("data/empirical/drafts/necrobinder_sts2fun_current_patch_triage_batch.json")
VALID_DRAFT = Path("tests/fixtures/empirical/valid_traceable_draft.json")
CLASS_WORKSHEETS = {
    "ironclad": (
        Path("data/empirical/drafts/ironclad_sts2fun_current_patch_capture_batch.json"),
        ["shrug_it_off", "pommel_strike", "anger"],
    ),
    "silent": (
        Path("data/empirical/drafts/silent_sts2fun_current_patch_capture_batch.json"),
        ["dagger_throw", "backflip", "footwork"],
    ),
    "defect": (
        Path("data/empirical/drafts/defect_sts2fun_current_patch_capture_batch.json"),
        ["cold_snap", "glacier", "defragment"],
    ),
    "regent": (
        Path("data/empirical/drafts/regent_sts2fun_current_patch_capture_batch.json"),
        ["astral_pulse", "bulwark", "spectrum_shift"],
    ),
}


def test_batch_worksheet_exists_and_is_valid_json() -> None:
    payload = json.loads(BATCH_WORKSHEET.read_text(encoding="utf-8"))
    card_ids = [entry["card_id"] for entry in payload["entries"]]

    assert payload["draft_type"] == "empirical_stat_draft"
    assert card_ids == ["unleash", "bodyguard", "forbidden_grimoire", "sleight_of_flesh", "defy"]
    assert all(entry["character"] == "necrobinder" for entry in payload["entries"])
    assert all(entry["sample_size"] is None for entry in payload["entries"])


def test_batch_worksheet_is_not_discovered_as_active_empirical_data() -> None:
    assert all("drafts" not in path.parts for path in discover_empirical_stats(Path("data")))


def test_current_patch_worksheet_exists_and_is_valid_json() -> None:
    payload = json.loads(CURRENT_PATCH_WORKSHEET.read_text(encoding="utf-8"))
    card_ids = [entry["card_id"] for entry in payload["entries"]]

    assert payload["draft_type"] == "empirical_stat_draft"
    assert card_ids == ["forbidden_grimoire", "defy", "sleight_of_flesh"]
    assert all(entry["source_url"] == "https://sts2.fun/cards?character=NECROBINDER" for entry in payload["entries"])
    assert all(entry["patch"] == "main_v0.103_current" for entry in payload["entries"])
    assert all(entry["review_status"] == "accepted" for entry in payload["entries"])
    assert all("not All Patches" in entry["reviewer_notes"] for entry in payload["entries"])
    assert [entry["sample_size"] for entry in payload["entries"]] == [2023, 44804, 16568]


def test_current_patch_worksheet_is_not_discovered_as_active_empirical_data() -> None:
    active_paths = discover_empirical_stats(Path("data"))

    assert CURRENT_PATCH_WORKSHEET not in active_paths
    assert all("drafts" not in path.parts for path in active_paths)


def test_cross_class_current_patch_worksheets_exist_and_are_valid_json() -> None:
    for character, (worksheet, expected_card_ids) in CLASS_WORKSHEETS.items():
        payload = json.loads(worksheet.read_text(encoding="utf-8"))
        card_ids = [entry["card_id"] for entry in payload["entries"]]

        assert payload["draft_type"] == "empirical_stat_draft"
        assert card_ids == expected_card_ids
        assert all(entry["character"] == character for entry in payload["entries"])
        assert all(entry["source_url"] == f"https://sts2.fun/cards?character={character.upper()}" for entry in payload["entries"])
        assert all(entry["patch"] == "main_v0.103_current" for entry in payload["entries"])
        assert all(entry["sample_size"] is not None for entry in payload["entries"])
        assert all(entry["review_status"] == "accepted" for entry in payload["entries"])
        assert all("user-provided STS2.fun current v0.103 screenshot" in entry["reviewer_notes"] for entry in payload["entries"])


def test_cross_class_current_patch_worksheets_are_not_active_empirical_data() -> None:
    active_paths = discover_empirical_stats(Path("data"))

    for worksheet, _expected_card_ids in CLASS_WORKSHEETS.values():
        assert worksheet not in active_paths
    assert all("drafts" not in path.parts for path in active_paths)


def test_cross_class_worksheet_reports_completed_rows() -> None:
    worksheet, _expected_card_ids = CLASS_WORKSHEETS["ironclad"]

    report = build_empirical_worksheet_report(worksheet)

    assert report["status"] == "pass"
    assert report["summary"]["entries"] == 3
    assert report["summary"]["complete_entries"] == 3
    assert report["summary"]["incomplete_entries"] == 0
    assert report["summary"]["total_null_fields"] == 0
    assert report["summary"]["rows_by_character"] == {"ironclad": 3}
    assert report["entries"][0]["null_fields"] == []


def test_worksheet_report_lists_all_null_fields() -> None:
    report = build_empirical_worksheet_report(BATCH_WORKSHEET)

    assert report["worksheet_type"] == "empirical_stat_worksheet"
    assert report["status"] == "review"
    assert report["summary"]["entries"] == 5
    assert report["summary"]["complete_entries"] == 0
    assert report["summary"]["incomplete_entries"] == 5
    assert report["summary"]["total_null_fields"] == 35
    assert report["summary"]["ready_for_draft_check"] is False
    assert report["summary"]["rows_by_character"] == {"necrobinder": 5}
    assert report["entries"][0]["null_fields"] == [
        "patch",
        "sample_size",
        "pick_rate",
        "win_rate",
        "impact",
        "captured_at",
        "stat_definition",
    ]


def test_worksheet_report_lists_missing_and_null_fields(tmp_path) -> None:
    worksheet_path = tmp_path / "missing_and_null.json"
    payload = json.loads(BATCH_WORKSHEET.read_text(encoding="utf-8"))
    del payload["entries"][0]["source_url"]
    del payload["entries"][0]["review_status"]
    worksheet_path.write_text(json.dumps(payload), encoding="utf-8")

    report = build_empirical_worksheet_report(worksheet_path)

    assert report["summary"]["total_missing_fields"] == 2
    assert report["entries"][0]["missing_fields"] == ["source_url", "review_status"]
    assert "patch" in report["entries"][0]["null_fields"]


def test_worksheet_cli_text_reports_incomplete_entries(capsys) -> None:
    status = main(["empirical-worksheet-check", str(BATCH_WORKSHEET), "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Empirical Worksheet: REVIEW" in captured.out
    assert "Entries: 5 | Complete: 0 | Incomplete: 5 | Ready for draft check: no" in captured.out
    assert "Null fields: patch, sample_size, pick_rate, win_rate, impact, captured_at, stat_definition" in captured.out
    assert "necrobinder_forbidden_grimoire_sts2fun_capture: forbidden_grimoire" in captured.out


def test_worksheet_cli_json_includes_summary_and_entries(capsys) -> None:
    status = main(["empirical-worksheet-check", str(BATCH_WORKSHEET), "--format", "json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["summary"]["incomplete_entries"] == 5
    assert payload["summary"]["total_null_fields"] == 35
    assert payload["entries"][3]["card_id"] == "sleight_of_flesh"
    assert "patch" in payload["entries"][3]["null_fields"]


def test_worksheet_cli_fail_on_incomplete_returns_failure(capsys) -> None:
    status = main(["empirical-worksheet-check", str(BATCH_WORKSHEET), "--fail-on-incomplete"])

    captured = capsys.readouterr()

    assert status == 1
    assert "Empirical Worksheet: REVIEW" in captured.out


def test_worksheet_cli_invalid_shape_returns_validation_error(tmp_path, capsys) -> None:
    worksheet_path = tmp_path / "bad_shape.json"
    worksheet_path.write_text(json.dumps({"draft_type": "empirical_stat_draft", "entries": {}}), encoding="utf-8")

    status = main(["empirical-worksheet-check", str(worksheet_path)])

    captured = capsys.readouterr()

    assert status == 2
    assert "entries must be a list" in captured.err


def test_strict_draft_check_still_rejects_incomplete_batch(capsys) -> None:
    status = main(["empirical-draft-check", str(BATCH_WORKSHEET), "--format", "text"])

    captured = capsys.readouterr()

    assert status == 2
    assert "patch is required for empirical draft rows and must not be null" in captured.err


def test_strict_draft_check_reviews_completed_cross_class_worksheet(capsys) -> None:
    worksheet, _expected_card_ids = CLASS_WORKSHEETS["silent"]

    status = main(["empirical-draft-check", str(worksheet), "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Empirical Draft: REVIEW" in captured.out
    assert "Entries: 3 | Audit flags: 3 | Promotion ready: no" in captured.out


def test_filled_worksheet_reports_ready_for_draft_check(tmp_path) -> None:
    worksheet_path = tmp_path / "filled_worksheet.json"
    worksheet_path.write_text(VALID_DRAFT.read_text(encoding="utf-8"), encoding="utf-8")

    report = build_empirical_worksheet_report(worksheet_path)

    assert report["status"] == "pass"
    assert report["summary"]["complete_entries"] == 1
    assert report["summary"]["incomplete_entries"] == 0
    assert report["summary"]["total_null_fields"] == 0
    assert report["summary"]["ready_for_draft_check"] is True
