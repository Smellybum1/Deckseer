from __future__ import annotations

import json
from pathlib import Path
import shutil

from deckseer.cli import main
from deckseer.data_loader import DeckseerData
from deckseer.empirical_cross_class_promotion import build_empirical_cross_class_promotion_preview_report


CLASS_WORKSHEETS = {
    "ironclad": Path("data/empirical/drafts/ironclad_sts2fun_current_patch_capture_batch.json"),
    "silent": Path("data/empirical/drafts/silent_sts2fun_current_patch_capture_batch.json"),
    "defect": Path("data/empirical/drafts/defect_sts2fun_current_patch_capture_batch.json"),
    "regent": Path("data/empirical/drafts/regent_sts2fun_current_patch_capture_batch.json"),
}


def test_cross_class_promotion_preview_current_promoted_outputs_are_blocked_for_review(capsys) -> None:
    status = main(["empirical-cross-class-promotion-preview", "--format", "json"])

    captured = capsys.readouterr()
    report = json.loads(captured.out)

    assert status == 0
    assert report["report_type"] == "empirical_cross_class_promotion_preview"
    assert report["status"] == "review"
    assert report["summary"] == {
        "worksheets": 4,
        "blocked_worksheets": 4,
        "promotion_ready": 0,
        "review_needed": 0,
            "audit_flags": 9,
    }
    assert [preview["character"] for preview in report["previews"]] == ["ironclad", "silent", "defect", "regent"]
    assert all(preview["status"] == "blocked" for preview in report["previews"])
    assert all(preview["remaining_null_fields"] == 0 for preview in report["previews"])
    assert all(preview["output_exists"] is True for preview in report["previews"])


def test_cross_class_promotion_preview_text_lists_outputs(capsys) -> None:
    status = main(["empirical-cross-class-promotion-preview", "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Empirical Cross-Class Promotion Preview: REVIEW" in captured.out
    assert "Worksheets: 4 | Blocked: 4 | Promotion ready: 0 | Review needed: 0 | Audit flags: 9" in captured.out
    assert "ironclad: BLOCKED | null fields: 0 | output: data\\empirical\\ironclad_sts2fun_current_patch_reviewed.json" in captured.out
    assert "silent_sts2fun_current_patch_reviewed.json" in captured.out
    assert "defect_sts2fun_current_patch_reviewed.json" in captured.out
    assert "regent_sts2fun_current_patch_reviewed.json" in captured.out


def test_cross_class_promotion_preview_complete_temp_worksheets_report_pass(tmp_path) -> None:
    data_dir = _copy_project_data(tmp_path)
    _fill_worksheets(data_dir, use_card_source_patch=True, impact=0.0)

    report = build_empirical_cross_class_promotion_preview_report(
        DeckseerData.load(data_dir),
        data_dir=data_dir,
        min_sample_size=300,
    )

    assert report["status"] == "pass"
    assert report["summary"] == {
        "worksheets": 4,
        "blocked_worksheets": 0,
        "promotion_ready": 4,
        "review_needed": 0,
        "audit_flags": 0,
    }
    assert all(preview["promotion_preview"] is not None for preview in report["previews"])
    assert all(preview["promotion_preview"]["wrote_file"] is False for preview in report["previews"])
    assert all("empirical-promote-draft" in preview["next_command"] for preview in report["previews"])


def test_cross_class_promotion_preview_complete_temp_worksheets_with_audit_flags_report_review(tmp_path) -> None:
    data_dir = _copy_project_data(tmp_path)
    _fill_worksheets(data_dir, use_card_source_patch=False, impact=0.0)

    report = build_empirical_cross_class_promotion_preview_report(
        DeckseerData.load(data_dir),
        data_dir=data_dir,
        min_sample_size=300,
    )

    assert report["status"] == "review"
    assert report["summary"]["blocked_worksheets"] == 0
    assert report["summary"]["promotion_ready"] == 0
    assert report["summary"]["review_needed"] == 4
    assert report["summary"]["audit_flags"] > 0
    assert all(preview["allow_review_flags_needed"] is True for preview in report["previews"])
    assert all("--allow-review-flags" in preview["next_command"] for preview in report["previews"])


def test_cross_class_promotion_preview_existing_output_file_is_review_blocker(tmp_path) -> None:
    data_dir = _copy_project_data(tmp_path)
    _fill_worksheets(data_dir, use_card_source_patch=True, impact=0.0)
    existing_output = data_dir / "empirical" / "ironclad_sts2fun_current_patch_reviewed.json"
    existing_output.parent.mkdir(parents=True, exist_ok=True)
    existing_output.write_text("[]\n", encoding="utf-8")

    report = build_empirical_cross_class_promotion_preview_report(
        DeckseerData.load(data_dir),
        data_dir=data_dir,
        min_sample_size=300,
    )

    ironclad = report["previews"][0]
    assert report["status"] == "review"
    assert report["summary"]["blocked_worksheets"] == 1
    assert report["summary"]["promotion_ready"] == 3
    assert ironclad["status"] == "blocked"
    assert ironclad["output_exists"] is True
    assert "Review existing output before replacing" in ironclad["next_command"]


def test_cross_class_promotion_preview_invalid_worksheet_shape_returns_validation_error(tmp_path, capsys) -> None:
    data_dir = _copy_project_data(tmp_path)
    bad_path = data_dir / "empirical" / "drafts" / CLASS_WORKSHEETS["ironclad"].name
    bad_path.write_text(json.dumps({"draft_type": "empirical_stat_draft", "entries": {}}), encoding="utf-8")

    status = main(["empirical-cross-class-promotion-preview", "--data-dir", str(data_dir)])

    captured = capsys.readouterr()
    assert status == 2
    assert "entries must be a list" in captured.err


def test_cross_class_promotion_preview_json_includes_caveats_and_next_commands(capsys) -> None:
    status = main(["empirical-cross-class-promotion-preview", "--format", "json"])

    captured = capsys.readouterr()
    report = json.loads(captured.out)

    assert status == 0
    assert report["caveats"]
    for preview in report["previews"]:
        assert preview["next_command"]
        assert preview["output_path"].endswith(f"{preview['character']}_sts2fun_current_patch_reviewed.json")


def _copy_project_data(tmp_path: Path) -> Path:
    data_dir = tmp_path / "data"
    shutil.copytree(Path("data/cards"), data_dir / "cards")
    shutil.copytree(Path("data/relics"), data_dir / "relics")
    shutil.copytree(Path("data/potions"), data_dir / "potions")
    drafts_dir = data_dir / "empirical" / "drafts"
    drafts_dir.mkdir(parents=True)
    for worksheet in CLASS_WORKSHEETS.values():
        shutil.copyfile(worksheet, drafts_dir / worksheet.name)
    return data_dir


def _fill_worksheets(data_dir: Path, *, use_card_source_patch: bool, impact: float) -> None:
    deckseer_data = DeckseerData.load(data_dir)
    drafts_dir = data_dir / "empirical" / "drafts"
    for worksheet_name in [path.name for path in CLASS_WORKSHEETS.values()]:
        worksheet_path = drafts_dir / worksheet_name
        payload = json.loads(worksheet_path.read_text(encoding="utf-8"))
        for entry in payload["entries"]:
            card = deckseer_data.cards_by_id[entry["card_id"]]
            entry["source_url"] = f"https://sts2.fun/cards?character={entry['character'].upper()}"
            entry["patch"] = card.source_patch if use_card_source_patch else "main_v0.999_test"
            entry["sample_size"] = 1200
            entry["pick_rate"] = 0.42
            entry["win_rate"] = 0.58
            entry["impact"] = impact
            entry["stat_definition"] = "Manual current-patch all-run STS2.fun fixture values."
            entry["captured_at"] = "2026-05-23"
            entry["reviewer_notes"] = "Traceable promotion preview test row."
        worksheet_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
