from __future__ import annotations

import json
from pathlib import Path

from deckseer.cli import main
from deckseer.data_loader import DeckseerData
from deckseer.empirical_capture_packet import build_empirical_capture_packet, build_empirical_capture_packet_apply_report


BATCH_WORKSHEET = Path("data/empirical/drafts/necrobinder_sts2fun_capture_batch.json")
CURRENT_PATCH_WORKSHEET = Path("data/empirical/drafts/necrobinder_sts2fun_current_patch_triage_batch.json")


def test_capture_packet_text_lists_necrobinder_rows(capsys) -> None:
    status = main(["empirical-capture-packet", str(BATCH_WORKSHEET), "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Empirical Capture Packet" in captured.out
    assert "necrobinder_unleash_sts2fun_capture: unleash" in captured.out
    assert "necrobinder_bodyguard_sts2fun_capture: bodyguard" in captured.out
    assert "necrobinder_forbidden_grimoire_sts2fun_capture: forbidden_grimoire" in captured.out
    assert "necrobinder_sleight_of_flesh_sts2fun_capture: sleight_of_flesh" in captured.out
    assert "necrobinder_defy_sts2fun_capture: defy" in captured.out


def test_capture_packet_json_includes_required_fill_fields(capsys) -> None:
    status = main(["empirical-capture-packet", str(BATCH_WORKSHEET), "--format", "json"])

    captured = capsys.readouterr()
    packet = json.loads(captured.out)

    assert status == 0
    assert packet["packet_type"] == "empirical_capture_packet"
    assert packet["source_target"] == "STS2.fun current patch, all runs"
    assert packet["required_fields"] == [
        "entry_id",
        "card_id",
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
    assert packet["entries"][0]["entry_id"] == "necrobinder_unleash_sts2fun_capture"
    assert packet["entries"][0]["sample_size"] is None


def test_capture_packet_current_patch_worksheet_lists_three_triage_targets() -> None:
    packet = build_empirical_capture_packet(CURRENT_PATCH_WORKSHEET)

    assert packet["worksheet_path"] == str(CURRENT_PATCH_WORKSHEET)
    assert [entry["card_id"] for entry in packet["entries"]] == [
        "forbidden_grimoire",
        "defy",
        "sleight_of_flesh",
    ]
    assert all(entry["source_url"] is None for entry in packet["entries"])


def test_capture_packet_invalid_worksheet_shape_returns_validation_error(tmp_path, capsys) -> None:
    worksheet_path = tmp_path / "bad_worksheet.json"
    worksheet_path.write_text(json.dumps({"draft_type": "empirical_stat_draft", "entries": {}}), encoding="utf-8")

    status = main(["empirical-capture-packet", str(worksheet_path)])

    captured = capsys.readouterr()

    assert status == 2
    assert "entries must be a list" in captured.err


def test_capture_packet_generation_does_not_modify_worksheet() -> None:
    before = BATCH_WORKSHEET.read_text(encoding="utf-8")

    packet = build_empirical_capture_packet(BATCH_WORKSHEET)

    after = BATCH_WORKSHEET.read_text(encoding="utf-8")
    assert before == after
    assert len(packet["entries"]) == 5


def test_apply_packet_preview_updates_payload_without_writing(tmp_path) -> None:
    worksheet_path = _copy_batch(tmp_path)
    packet_path = _write_packet(tmp_path, entries=[_filled_entry("necrobinder_unleash_sts2fun_capture", "unleash")])
    original = worksheet_path.read_text(encoding="utf-8")

    status = main(["empirical-worksheet-apply-packet", str(packet_path), "--worksheet", str(worksheet_path), "--format", "json"])

    written = worksheet_path.read_text(encoding="utf-8")
    assert status == 0
    assert written == original


def test_apply_packet_write_updates_matching_rows(tmp_path) -> None:
    worksheet_path = _copy_batch(tmp_path)
    packet_path = _write_packet(
        tmp_path,
        entries=[
            _filled_entry("necrobinder_unleash_sts2fun_capture", "unleash"),
            _filled_entry("necrobinder_bodyguard_sts2fun_capture", "bodyguard"),
        ],
    )

    status = main(["empirical-worksheet-apply-packet", str(packet_path), "--worksheet", str(worksheet_path), "--write"])
    payload = json.loads(worksheet_path.read_text(encoding="utf-8"))

    assert status == 0
    assert payload["entries"][0]["patch"] == "v0.103.0"
    assert payload["entries"][1]["patch"] == "v0.103.0"
    assert payload["entries"][2]["patch"] is None


def test_apply_packet_unknown_entry_id_returns_validation_error(tmp_path, capsys) -> None:
    worksheet_path = _copy_batch(tmp_path)
    packet_path = _write_packet(tmp_path, entries=[_filled_entry("not_a_real_entry", "unleash")])

    status = main(["empirical-worksheet-apply-packet", str(packet_path), "--worksheet", str(worksheet_path)])

    captured = capsys.readouterr()
    assert status == 2
    assert "does not contain worksheet entry id" in captured.err


def test_apply_packet_mismatched_card_id_returns_validation_error(tmp_path, capsys) -> None:
    worksheet_path = _copy_batch(tmp_path)
    packet_path = _write_packet(tmp_path, entries=[_filled_entry("necrobinder_unleash_sts2fun_capture", "bodyguard")])

    status = main(["empirical-worksheet-apply-packet", str(packet_path), "--worksheet", str(worksheet_path)])

    captured = capsys.readouterr()
    assert status == 2
    assert "card_id does not match worksheet card_id" in captured.err


def test_apply_packet_missing_required_field_returns_validation_error(tmp_path, capsys) -> None:
    worksheet_path = _copy_batch(tmp_path)
    entry = _filled_entry("necrobinder_unleash_sts2fun_capture", "unleash")
    del entry["impact"]
    packet_path = _write_packet(tmp_path, entries=[entry])

    status = main(["empirical-worksheet-apply-packet", str(packet_path), "--worksheet", str(worksheet_path)])

    captured = capsys.readouterr()
    assert status == 2
    assert "impact is required" in captured.err


def test_apply_packet_unknown_local_card_id_returns_validation_error(tmp_path, capsys) -> None:
    worksheet_path = _copy_batch(tmp_path)
    worksheet = json.loads(worksheet_path.read_text(encoding="utf-8"))
    worksheet["entries"][0]["card_id"] = "not_a_real_card"
    worksheet_path.write_text(json.dumps(worksheet), encoding="utf-8")
    packet_path = _write_packet(tmp_path, entries=[_filled_entry("necrobinder_unleash_sts2fun_capture", "not_a_real_card")])

    status = main(["empirical-worksheet-apply-packet", str(packet_path), "--worksheet", str(worksheet_path)])

    captured = capsys.readouterr()
    assert status == 2
    assert "Missing card data for packet entry" in captured.err


def test_apply_full_packet_makes_temp_worksheet_ready_for_draft_check(tmp_path) -> None:
    worksheet_path = _copy_batch(tmp_path)
    packet_path = _write_packet(
        tmp_path,
        entries=[
            _filled_entry("necrobinder_unleash_sts2fun_capture", "unleash"),
            _filled_entry("necrobinder_bodyguard_sts2fun_capture", "bodyguard"),
            _filled_entry("necrobinder_forbidden_grimoire_sts2fun_capture", "forbidden_grimoire"),
            _filled_entry("necrobinder_sleight_of_flesh_sts2fun_capture", "sleight_of_flesh"),
            _filled_entry("necrobinder_defy_sts2fun_capture", "defy"),
        ],
    )

    report = build_empirical_capture_packet_apply_report(
        DeckseerData.load(Path("data")),
        packet_path,
        worksheet_path=worksheet_path,
        write=False,
    )

    assert report["worksheet_report"]["summary"]["ready_for_draft_check"] is True
    assert report["worksheet_report"]["summary"]["total_null_fields"] == 0


def _copy_batch(tmp_path: Path) -> Path:
    worksheet_path = tmp_path / "worksheet.json"
    worksheet_path.write_text(BATCH_WORKSHEET.read_text(encoding="utf-8"), encoding="utf-8")
    return worksheet_path


def _write_packet(tmp_path: Path, *, entries: list[dict]) -> Path:
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(
        json.dumps(
            {
                "packet_type": "empirical_capture_packet",
                "source_target": "STS2.fun current patch, all runs",
                "entries": entries,
            }
        ),
        encoding="utf-8",
    )
    return packet_path


def _filled_entry(entry_id: str, card_id: str) -> dict:
    return {
        "entry_id": entry_id,
        "card_id": card_id,
        "source_url": "https://sts2.fun/",
        "patch": "v0.103.0",
        "sample_size": 1200,
        "pick_rate": 0.42,
        "win_rate": 0.58,
        "impact": 0.08,
        "stat_definition": "Manual test fixture values for packet validation.",
        "captured_at": "2026-05-23",
        "reviewer_notes": "Traceable packet test row.",
    }
