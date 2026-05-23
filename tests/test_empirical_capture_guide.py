from __future__ import annotations

import json
from pathlib import Path

from deckseer.cli import main
from deckseer.empirical_capture_guide import build_empirical_capture_guide


BATCH_WORKSHEET = Path("data/empirical/drafts/necrobinder_sts2fun_capture_batch.json")
CURRENT_PATCH_WORKSHEET = Path("data/empirical/drafts/necrobinder_sts2fun_current_patch_triage_batch.json")
CLASS_WORKSHEETS = {
    "ironclad": Path("data/empirical/drafts/ironclad_sts2fun_current_patch_capture_batch.json"),
    "silent": Path("data/empirical/drafts/silent_sts2fun_current_patch_capture_batch.json"),
    "defect": Path("data/empirical/drafts/defect_sts2fun_current_patch_capture_batch.json"),
    "regent": Path("data/empirical/drafts/regent_sts2fun_current_patch_capture_batch.json"),
}
CLASS_CARDS = {
    "ironclad": ["shrug_it_off", "pommel_strike", "anger"],
    "silent": ["dagger_throw", "backflip", "footwork"],
    "defect": ["cold_snap", "glacier", "defragment"],
    "regent": ["astral_pulse", "bulwark", "spectrum_shift"],
}


def test_capture_guide_text_lists_necrobinder_rows(capsys) -> None:
    status = main(["empirical-capture-guide", "--character", "necrobinder", "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Empirical Capture Guide: necrobinder [REVIEW]" in captured.out
    assert "Source target: STS2.fun current patch, all runs" in captured.out
    assert "necrobinder_unleash_sts2fun_capture: unleash" in captured.out
    assert "necrobinder_bodyguard_sts2fun_capture: bodyguard" in captured.out
    assert "necrobinder_forbidden_grimoire_sts2fun_capture: forbidden_grimoire" in captured.out
    assert "necrobinder_sleight_of_flesh_sts2fun_capture: sleight_of_flesh" in captured.out
    assert "necrobinder_defy_sts2fun_capture: defy" in captured.out
    assert "deckseer empirical-worksheet-fill" in captured.out
    assert "--write" in captured.out


def test_capture_guide_json_includes_source_required_fields_and_templates(capsys) -> None:
    status = main(["empirical-capture-guide", "--character", "necrobinder", "--format", "json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["guide_type"] == "empirical_capture_guide"
    assert payload["worksheet_path"] == "data\\empirical\\drafts\\necrobinder_sts2fun_capture_batch.json"
    assert payload["source_target"] == "STS2.fun current patch, all runs"
    assert payload["required_values"] == [
        "source_url",
        "patch",
        "sample_size",
        "pick_rate",
        "win_rate",
        "impact",
        "stat_definition",
        "captured_at",
        "reviewer_notes",
    ]
    assert payload["rows"][0]["entry_id"] == "necrobinder_unleash_sts2fun_capture"
    assert "--entry-id necrobinder_unleash_sts2fun_capture" in payload["rows"][0]["preview_command"]
    assert payload["rows"][0]["write_command"].endswith("--write")


def test_capture_guide_supports_cross_class_default_worksheets(capsys) -> None:
    for character, card_ids in CLASS_CARDS.items():
        status = main(["empirical-capture-guide", "--character", character, "--format", "text"])

        captured = capsys.readouterr()

        assert status == 0
        assert f"Empirical Capture Guide: {character} [PASS]" in captured.out
        for card_id in card_ids:
            assert f"{character}_{card_id}_sts2fun_current_patch_capture: {card_id}" in captured.out


def test_capture_guide_cross_class_json_includes_templates(capsys) -> None:
    status = main(["empirical-capture-guide", "--character", "ironclad", "--format", "json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["worksheet_path"] == str(CLASS_WORKSHEETS["ironclad"])
    assert payload["source_target"] == "STS2.fun current patch, all runs"
    assert [row["card_id"] for row in payload["rows"]] == CLASS_CARDS["ironclad"]
    assert "--entry-id ironclad_shrug_it_off_sts2fun_current_patch_capture" in payload["rows"][0]["preview_command"]
    assert payload["rows"][0]["write_command"].endswith("--write")


def test_capture_guide_unsupported_character_returns_validation_error(capsys) -> None:
    status = main(["empirical-capture-guide", "--character", "colorless"])

    captured = capsys.readouterr()

    assert status == 2
    assert "currently supports only: defect, ironclad, necrobinder, regent, silent" in captured.err


def test_capture_guide_can_use_explicit_current_patch_worksheet(capsys) -> None:
    status = main(
        [
            "empirical-capture-guide",
            "--character",
            "necrobinder",
            "--worksheet",
            str(CURRENT_PATCH_WORKSHEET),
            "--format",
            "text",
        ]
    )

    captured = capsys.readouterr()

    assert status == 0
    assert "necrobinder_forbidden_grimoire_sts2fun_current_patch_capture: forbidden_grimoire" in captured.out
    assert "necrobinder_defy_sts2fun_current_patch_capture: defy" in captured.out
    assert "necrobinder_sleight_of_flesh_sts2fun_current_patch_capture: sleight_of_flesh" in captured.out
    assert "necrobinder_unleash_sts2fun_capture" not in captured.out


def test_capture_guide_report_uses_explicit_current_patch_worksheet() -> None:
    report = build_empirical_capture_guide("necrobinder", data_dir=Path("data"), worksheet_path=CURRENT_PATCH_WORKSHEET)

    assert report["worksheet_path"] == str(CURRENT_PATCH_WORKSHEET)
    assert report["worksheet_summary"]["entries"] == 3
    assert [row["card_id"] for row in report["rows"]] == ["forbidden_grimoire", "defy", "sleight_of_flesh"]


def test_capture_guide_does_not_modify_worksheet() -> None:
    before = BATCH_WORKSHEET.read_text(encoding="utf-8")

    report = build_empirical_capture_guide("necrobinder", data_dir=Path("data"))

    after = BATCH_WORKSHEET.read_text(encoding="utf-8")
    assert before == after
    assert report["worksheet_summary"]["total_null_fields"] == 35


def test_cross_class_capture_guide_does_not_modify_worksheet() -> None:
    worksheet = CLASS_WORKSHEETS["silent"]
    before = worksheet.read_text(encoding="utf-8")

    report = build_empirical_capture_guide("silent", data_dir=Path("data"))

    after = worksheet.read_text(encoding="utf-8")
    assert before == after
    assert report["worksheet_summary"]["entries"] == 3
    assert report["worksheet_summary"]["total_null_fields"] == 0
