from __future__ import annotations

import json
from pathlib import Path

from deckseer.cli import main
from deckseer.data_loader import DeckseerData
from deckseer.empirical_draft import load_empirical_draft
from deckseer.empirical_worksheet import build_empirical_worksheet_fill_report


BATCH_WORKSHEET = Path("data/empirical/drafts/necrobinder_sts2fun_capture_batch.json")


def test_worksheet_fill_preview_updates_payload_without_writing(tmp_path) -> None:
    worksheet_path = _copy_batch(tmp_path)
    original = worksheet_path.read_text(encoding="utf-8")
    data = DeckseerData.load(Path("data"))

    report = build_empirical_worksheet_fill_report(
        data,
        worksheet_path,
        entry_id="necrobinder_unleash_sts2fun_capture",
        updates={"patch": "v0.103.0", "sample_size": 1234},
    )

    assert report["write_requested"] is False
    assert report["wrote_file"] is False
    assert worksheet_path.read_text(encoding="utf-8") == original
    assert report["payload"]["entries"][0]["patch"] == "v0.103.0"
    assert report["payload"]["entries"][0]["sample_size"] == 1234
    assert report["worksheet_report"]["summary"]["total_null_fields"] == 33


def test_worksheet_fill_write_updates_exactly_one_entry(tmp_path) -> None:
    worksheet_path = _copy_batch(tmp_path)
    data = DeckseerData.load(Path("data"))

    report = build_empirical_worksheet_fill_report(
        data,
        worksheet_path,
        entry_id="necrobinder_bodyguard_sts2fun_capture",
        updates={"patch": "v0.103.0", "captured_at": "2026-05-23"},
        write=True,
    )
    written = json.loads(worksheet_path.read_text(encoding="utf-8"))

    assert report["wrote_file"] is True
    assert written["entries"][0]["patch"] is None
    assert written["entries"][1]["patch"] == "v0.103.0"
    assert written["entries"][1]["captured_at"] == "2026-05-23"
    assert written["entries"][2]["captured_at"] is None


def test_worksheet_fill_omitted_flags_preserve_existing_values(tmp_path) -> None:
    worksheet_path = _copy_batch(tmp_path)
    data = DeckseerData.load(Path("data"))

    report = build_empirical_worksheet_fill_report(
        data,
        worksheet_path,
        entry_id="necrobinder_unleash_sts2fun_capture",
        updates={"patch": "v0.103.0", "source_url": None, "reviewer_notes": None},
    )

    entry = report["payload"]["entries"][0]
    assert entry["patch"] == "v0.103.0"
    assert entry["source_url"] == "https://sts2.fun/"
    assert entry["reviewer_notes"].startswith("Capture exact STS2.fun")


def test_worksheet_fill_unknown_entry_id_returns_validation_error(tmp_path, capsys) -> None:
    worksheet_path = _copy_batch(tmp_path)

    status = main(["empirical-worksheet-fill", str(worksheet_path), "--entry-id", "not_a_real_entry", "--patch", "v0.103.0"])

    captured = capsys.readouterr()

    assert status == 2
    assert "does not contain worksheet entry id" in captured.err


def test_worksheet_fill_missing_entry_id_returns_validation_error(tmp_path, capsys) -> None:
    worksheet_path = _copy_batch(tmp_path)

    status = main(["empirical-worksheet-fill", str(worksheet_path), "--patch", "v0.103.0"])

    captured = capsys.readouterr()

    assert status == 2
    assert "requires --entry-id" in captured.err


def test_worksheet_fill_unknown_local_card_id_returns_validation_error(tmp_path, capsys) -> None:
    worksheet_path = _copy_batch(tmp_path)
    payload = json.loads(worksheet_path.read_text(encoding="utf-8"))
    payload["entries"][0]["card_id"] = "not_a_real_card"
    worksheet_path.write_text(json.dumps(payload), encoding="utf-8")

    status = main(["empirical-worksheet-fill", str(worksheet_path), "--entry-id", "necrobinder_unleash_sts2fun_capture", "--patch", "v0.103.0"])

    captured = capsys.readouterr()

    assert status == 2
    assert "Missing card data for worksheet entry" in captured.err


def test_worksheet_fill_cli_text_shows_updated_fields_and_remaining_blanks(tmp_path, capsys) -> None:
    worksheet_path = _copy_batch(tmp_path)

    status = main(
        [
            "empirical-worksheet-fill",
            str(worksheet_path),
            "--entry-id",
            "necrobinder_unleash_sts2fun_capture",
            "--patch",
            "v0.103.0",
            "--sample-size",
            "1200",
            "--format",
            "text",
        ]
    )

    captured = capsys.readouterr()

    assert status == 0
    assert "Empirical Worksheet Fill: REVIEW" in captured.out
    assert "Mode: preview | Wrote file: no" in captured.out
    assert "Updated fields: patch, sample_size" in captured.out
    assert "Remaining null fields: 33" in captured.out
    assert "Entry null fields: pick_rate, win_rate, impact, captured_at, stat_definition" in captured.out


def test_worksheet_fill_cli_json_includes_payload_and_report(tmp_path, capsys) -> None:
    worksheet_path = _copy_batch(tmp_path)

    status = main(
        [
            "empirical-worksheet-fill",
            str(worksheet_path),
            "--entry-id",
            "necrobinder_unleash_sts2fun_capture",
            "--patch",
            "v0.103.0",
            "--format",
            "json",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["updated_entry_id"] == "necrobinder_unleash_sts2fun_capture"
    assert payload["updated_fields"] == ["patch"]
    assert payload["payload"]["entries"][0]["patch"] == "v0.103.0"
    assert payload["worksheet_report"]["summary"]["ready_for_draft_check"] is False


def test_worksheet_fill_can_make_single_entry_ready_for_strict_draft_check(tmp_path) -> None:
    worksheet_path = tmp_path / "single_entry.json"
    payload = json.loads(BATCH_WORKSHEET.read_text(encoding="utf-8"))
    payload["entries"] = [payload["entries"][0]]
    worksheet_path.write_text(json.dumps(payload), encoding="utf-8")
    data = DeckseerData.load(Path("data"))

    report = build_empirical_worksheet_fill_report(
        data,
        worksheet_path,
        entry_id="necrobinder_unleash_sts2fun_capture",
        updates={
            "patch": "v0.103.0",
            "sample_size": 1200,
            "pick_rate": 0.42,
            "win_rate": 0.58,
            "impact": 0.08,
            "captured_at": "2026-05-23",
            "stat_definition": "Manual test fixture values for worksheet fill validation.",
        },
        write=True,
    )

    entries = load_empirical_draft(worksheet_path)

    assert report["worksheet_report"]["summary"]["ready_for_draft_check"] is True
    assert len(entries) == 1
    assert entries[0].stat.card_id == "unleash"


def _copy_batch(tmp_path: Path) -> Path:
    worksheet_path = tmp_path / "worksheet.json"
    worksheet_path.write_text(BATCH_WORKSHEET.read_text(encoding="utf-8"), encoding="utf-8")
    return worksheet_path
