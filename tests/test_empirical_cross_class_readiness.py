from __future__ import annotations

import json
from pathlib import Path
import shutil

from deckseer.cli import main
from deckseer.data_loader import DeckseerData
from deckseer.empirical_cross_class_packet import build_empirical_cross_class_capture_packet
from deckseer.empirical_cross_class_readiness import build_empirical_cross_class_readiness_report


CLASS_WORKSHEETS = {
    "ironclad": Path("data/empirical/drafts/ironclad_sts2fun_current_patch_capture_batch.json"),
    "silent": Path("data/empirical/drafts/silent_sts2fun_current_patch_capture_batch.json"),
    "defect": Path("data/empirical/drafts/defect_sts2fun_current_patch_capture_batch.json"),
    "regent": Path("data/empirical/drafts/regent_sts2fun_current_patch_capture_batch.json"),
}


def test_cross_class_readiness_current_completed_worksheets_report_review(capsys) -> None:
    status = main(["empirical-cross-class-readiness", "--format", "json"])

    captured = capsys.readouterr()
    report = json.loads(captured.out)

    assert status == 0
    assert report["report_type"] == "empirical_cross_class_readiness"
    assert report["status"] == "review"
    assert report["summary"]["worksheets"] == 4
    assert report["summary"]["complete_worksheets"] == 4
    assert report["summary"]["incomplete_worksheets"] == 0
    assert report["summary"]["ready_for_draft_check"] == 4
    assert report["summary"]["audit_flags"] == 9
    assert report["summary"]["remaining_null_fields"] == 0
    assert report["summary"]["remaining_missing_fields"] == 0
    assert [row["character"] for row in report["worksheets"]] == ["ironclad", "silent", "defect", "regent"]
    assert all(row["audit_preview"] is not None for row in report["worksheets"])
    assert "empirical-draft-check" in report["worksheets"][0]["next_command"]


def test_cross_class_readiness_text_names_all_classes(capsys) -> None:
    status = main(["empirical-cross-class-readiness", "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Empirical Cross-Class Readiness: REVIEW" in captured.out
    assert "Worksheets: 4 | Complete: 4 | Incomplete: 0 | Audit flags: 9" in captured.out
    assert "ironclad: REVIEW | null fields: 0" in captured.out
    assert "silent: REVIEW | null fields: 0" in captured.out
    assert "defect: REVIEW | null fields: 0" in captured.out
    assert "regent: REVIEW | null fields: 0" in captured.out


def test_cross_class_readiness_json_includes_next_commands(capsys) -> None:
    status = main(["empirical-cross-class-readiness", "--format", "json"])

    captured = capsys.readouterr()
    report = json.loads(captured.out)

    assert status == 0
    for worksheet in report["worksheets"]:
        assert worksheet["next_command"] == worksheet["next_commands"][0]
        assert any("empirical-draft-check" in command for command in worksheet["next_commands"])


def test_cross_class_readiness_complete_temp_worksheets_report_pass(tmp_path) -> None:
    data_dir = _copy_project_data(tmp_path)
    _fill_worksheets(data_dir, use_card_source_patch=True, impact=0.0)

    report = build_empirical_cross_class_readiness_report(
        DeckseerData.load(data_dir),
        data_dir=data_dir,
        min_sample_size=300,
    )

    assert report["status"] == "pass"
    assert report["summary"]["complete_worksheets"] == 4
    assert report["summary"]["incomplete_worksheets"] == 0
    assert report["summary"]["audit_flags"] == 0
    assert report["summary"]["remaining_null_fields"] == 0
    assert all(worksheet["audit_preview"] is not None for worksheet in report["worksheets"])
    assert all("empirical-promote-draft" in worksheet["next_commands"][1] for worksheet in report["worksheets"])


def test_cross_class_readiness_complete_temp_worksheet_with_audit_flags_reports_review(tmp_path) -> None:
    data_dir = _copy_project_data(tmp_path)
    _fill_worksheets(data_dir, use_card_source_patch=False, impact=0.0)

    report = build_empirical_cross_class_readiness_report(
        DeckseerData.load(data_dir),
        data_dir=data_dir,
        min_sample_size=300,
    )

    assert report["status"] == "review"
    assert report["summary"]["complete_worksheets"] == 4
    assert report["summary"]["audit_flags"] > 0
    assert any("--allow-review-flags" in command for worksheet in report["worksheets"] for command in worksheet["next_commands"])


def test_cross_class_readiness_invalid_worksheet_shape_returns_validation_error(tmp_path, capsys) -> None:
    data_dir = _copy_project_data(tmp_path)
    bad_path = data_dir / "empirical" / "drafts" / CLASS_WORKSHEETS["ironclad"].name
    bad_path.write_text(json.dumps({"draft_type": "empirical_stat_draft", "entries": {}}), encoding="utf-8")

    status = main(["empirical-cross-class-readiness", "--data-dir", str(data_dir)])

    captured = capsys.readouterr()

    assert status == 2
    assert "entries must be a list" in captured.err


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
    packet = build_empirical_cross_class_capture_packet(data_dir)
    for group in packet["groups"]:
        worksheet_path = Path(group["worksheet_path"])
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
            entry["reviewer_notes"] = "Traceable readiness test row."
        worksheet_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
