from __future__ import annotations

import json
from pathlib import Path

from deckseer.cli import main
from deckseer.data_loader import DeckseerData
from deckseer.empirical_current_patch import build_empirical_current_patch_review


CURRENT_PATCH_WORKSHEET = Path("data/empirical/drafts/necrobinder_sts2fun_current_patch_triage_batch.json")
TRIAGE = Path("data/empirical/triage.json")


def test_current_patch_review_reports_completed_rows_and_triage_coverage() -> None:
    data = DeckseerData.load(Path("data"))

    report = build_empirical_current_patch_review(data, CURRENT_PATCH_WORKSHEET, triage_manifest_path=TRIAGE)

    assert report["review_type"] == "empirical_current_patch_review"
    assert report["status"] == "pass"
    assert report["summary"]["entries"] == 3
    assert report["summary"]["complete_entries"] == 3
    assert report["summary"]["triage_matches"] == 5
    assert report["summary"]["total_null_fields"] == 0
    assert report["summary"]["triage_cards_covered"] == ["defy", "forbidden_grimoire", "sleight_of_flesh"]
    assert report["summary"]["forbidden_grimoire_blocked"] is False
    assert report["summary"]["audit_preview_ran"] is True
    assert report["summary"]["audit_flags"] == 2
    assert report["audit_preview"]["summary"]["flags_by_code"] == {"patch_mismatch": 2}


def test_all_patches_rows_are_insufficient_for_current_patch_resolution(tmp_path) -> None:
    data = DeckseerData.load(Path("data"))
    worksheet = tmp_path / "all_patches_current_review.json"
    payload = _filled_current_patch_payload(patch="all_patches")
    worksheet.write_text(json.dumps(payload), encoding="utf-8")

    report = build_empirical_current_patch_review(data, worksheet, triage_manifest_path=TRIAGE)

    assert report["status"] == "review"
    assert report["summary"]["blocked_all_patches_rows"] == 3
    assert report["summary"]["audit_preview_ran"] is False
    assert report["rows"][0]["resolution_status"] == "blocked_all_patches"
    assert any("All Patches rows are insufficient" in caveat for caveat in report["caveats"])


def test_complete_current_patch_review_runs_strict_audit_preview(tmp_path) -> None:
    data = DeckseerData.load(Path("data"))
    worksheet = tmp_path / "current_patch_review.json"
    worksheet.write_text(json.dumps(_filled_current_patch_payload(patch="main_v0.103_current")), encoding="utf-8")

    report = build_empirical_current_patch_review(data, worksheet, triage_manifest_path=TRIAGE)

    assert report["status"] == "pass"
    assert report["summary"]["ready_for_draft_check"] is True
    assert report["summary"]["audit_preview_ran"] is True
    assert report["audit_preview"]["summary"]["rows"] == 3
    assert report["summary"]["forbidden_grimoire_blocked"] is False


def test_current_patch_review_cli_text_names_forbidden_grimoire_and_blocker(capsys) -> None:
    status = main(["empirical-current-patch-review", str(CURRENT_PATCH_WORKSHEET), "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Empirical Current-Patch Review: PASS" in captured.out
    assert "forbidden_grimoire" in captured.out
    assert "Forbidden Grimoire prior-change status: ready for promotion review" in captured.out
    assert "Null fields: 0" in captured.out
    assert "Audit preview: ran | Flags: 2" in captured.out


def test_current_patch_review_cli_json_includes_summary_rows_and_caveats(capsys) -> None:
    status = main(["empirical-current-patch-review", str(CURRENT_PATCH_WORKSHEET), "--format", "json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["review_type"] == "empirical_current_patch_review"
    assert payload["summary"]["total_null_fields"] == 0
    assert len(payload["rows"]) == 3
    assert len(payload["triage_matches"]) == 5
    assert payload["caveats"]


def test_current_patch_review_invalid_json_returns_validation_error(tmp_path, capsys) -> None:
    worksheet = tmp_path / "bad.json"
    worksheet.write_text("{", encoding="utf-8")

    status = main(["empirical-current-patch-review", str(worksheet)])

    captured = capsys.readouterr()

    assert status == 2
    assert "is not valid JSON" in captured.err


def test_current_patch_review_invalid_shape_returns_validation_error(tmp_path, capsys) -> None:
    worksheet = tmp_path / "bad_shape.json"
    worksheet.write_text(json.dumps({"draft_type": "empirical_stat_draft", "entries": {}}), encoding="utf-8")

    status = main(["empirical-current-patch-review", str(worksheet)])

    captured = capsys.readouterr()

    assert status == 2
    assert "entries must be a list" in captured.err


def _filled_current_patch_payload(*, patch: str) -> dict:
    return {
        "draft_type": "empirical_stat_draft",
        "entries": [
            _entry("necrobinder_forbidden_grimoire_sts2fun_current_patch_capture", "forbidden_grimoire", patch, -0.031),
            _entry("necrobinder_defy_sts2fun_current_patch_capture", "defy", patch, -0.01),
            _entry("necrobinder_sleight_of_flesh_sts2fun_current_patch_capture", "sleight_of_flesh", patch, 0.015),
        ],
    }


def _entry(entry_id: str, card_id: str, patch: str, impact: float) -> dict:
    return {
        "id": entry_id,
        "card_id": card_id,
        "character": "necrobinder",
        "patch": patch,
        "source": "STS2.fun manual capture test fixture",
        "source_url": "https://sts2.fun/cards?character=NECROBINDER",
        "captured_at": "2026-05-23",
        "stat_definition": "Test fixture current-patch all-run reward-pick stats.",
        "reviewer_notes": "Filled test fixture for current-patch review command.",
        "sample_size": 1200,
        "pick_rate": 0.42,
        "win_rate": 0.5,
        "impact": impact,
        "act": "all",
        "ascension": "all",
        "review_status": "accepted",
    }
