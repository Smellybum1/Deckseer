from __future__ import annotations

import json
from pathlib import Path
import shutil

from deckseer.cli import main
from deckseer.data_loader import DeckseerData
from deckseer.empirical_cross_class_packet import (
    build_empirical_cross_class_apply_packet_report,
    build_empirical_cross_class_capture_packet,
)


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


def test_cross_class_capture_packet_json_includes_four_groups_and_twelve_rows(capsys) -> None:
    status = main(["empirical-cross-class-capture-packet", "--format", "json"])

    captured = capsys.readouterr()
    packet = json.loads(captured.out)

    assert status == 0
    assert packet["packet_type"] == "empirical_cross_class_capture_packet"
    assert packet["summary"] == {"groups": 4, "entries": 12}
    assert [group["character"] for group in packet["groups"]] == ["ironclad", "silent", "defect", "regent"]
    for group in packet["groups"]:
        assert [entry["card_id"] for entry in group["entries"]] == CLASS_CARDS[group["character"]]
        assert group["worksheet_path"] == str(CLASS_WORKSHEETS[group["character"]])
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


def test_cross_class_capture_packet_text_lists_worksheets_and_representative_entries(capsys) -> None:
    status = main(["empirical-cross-class-capture-packet", "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Empirical Cross-Class Capture Packet" in captured.out
    for worksheet in CLASS_WORKSHEETS.values():
        assert str(worksheet) in captured.out
    assert "ironclad_shrug_it_off_sts2fun_current_patch_capture: shrug_it_off" in captured.out
    assert "silent_dagger_throw_sts2fun_current_patch_capture: dagger_throw" in captured.out
    assert "defect_cold_snap_sts2fun_current_patch_capture: cold_snap" in captured.out
    assert "regent_astral_pulse_sts2fun_current_patch_capture: astral_pulse" in captured.out


def test_cross_class_capture_packet_generation_does_not_modify_worksheets() -> None:
    before = {character: path.read_text(encoding="utf-8") for character, path in CLASS_WORKSHEETS.items()}

    packet = build_empirical_cross_class_capture_packet(Path("data"))

    after = {character: path.read_text(encoding="utf-8") for character, path in CLASS_WORKSHEETS.items()}
    assert after == before
    assert packet["summary"]["entries"] == 12


def test_cross_class_apply_packet_preview_updates_payload_without_writing(tmp_path) -> None:
    data_dir = _copy_cross_class_data_dir(tmp_path)
    packet = _filled_packet(build_empirical_cross_class_capture_packet(data_dir))
    packet_path = _write_packet(tmp_path, packet)
    original = _read_worksheets(data_dir)

    status = main(["empirical-cross-class-apply-packet", str(packet_path), "--format", "json"])

    assert status == 0
    assert _read_worksheets(data_dir) == original


def test_cross_class_apply_packet_write_updates_all_matching_rows(tmp_path) -> None:
    data_dir = _copy_cross_class_data_dir(tmp_path)
    packet = _filled_packet(build_empirical_cross_class_capture_packet(data_dir))
    packet_path = _write_packet(tmp_path, packet)

    status = main(["empirical-cross-class-apply-packet", str(packet_path), "--write"])
    written = _load_worksheets(data_dir)

    assert status == 0
    for character, payload in written.items():
        assert [entry["card_id"] for entry in payload["entries"]] == CLASS_CARDS[character]
        assert all(entry["patch"] == "v0.103.0" for entry in payload["entries"])
        assert all(entry["sample_size"] == 1200 for entry in payload["entries"])


def test_cross_class_apply_packet_missing_required_field_returns_validation_error(tmp_path, capsys) -> None:
    data_dir = _copy_cross_class_data_dir(tmp_path)
    packet = _filled_packet(build_empirical_cross_class_capture_packet(data_dir))
    del packet["groups"][0]["entries"][0]["sample_size"]
    packet_path = _write_packet(tmp_path, packet)

    status = main(["empirical-cross-class-apply-packet", str(packet_path)])

    captured = capsys.readouterr()
    assert status == 2
    assert "sample_size is required" in captured.err


def test_cross_class_apply_packet_unknown_entry_id_returns_validation_error(tmp_path, capsys) -> None:
    data_dir = _copy_cross_class_data_dir(tmp_path)
    packet = _filled_packet(build_empirical_cross_class_capture_packet(data_dir))
    packet["groups"][0]["entries"][0]["entry_id"] = "not_a_real_entry"
    packet_path = _write_packet(tmp_path, packet)

    status = main(["empirical-cross-class-apply-packet", str(packet_path)])

    captured = capsys.readouterr()
    assert status == 2
    assert "does not contain worksheet entry id" in captured.err


def test_cross_class_apply_packet_mismatched_card_id_returns_validation_error(tmp_path, capsys) -> None:
    data_dir = _copy_cross_class_data_dir(tmp_path)
    packet = _filled_packet(build_empirical_cross_class_capture_packet(data_dir))
    packet["groups"][0]["entries"][0]["card_id"] = "pommel_strike"
    packet_path = _write_packet(tmp_path, packet)

    status = main(["empirical-cross-class-apply-packet", str(packet_path)])

    captured = capsys.readouterr()
    assert status == 2
    assert "card_id does not match worksheet card_id" in captured.err


def test_cross_class_apply_packet_unknown_local_card_id_returns_validation_error(tmp_path, capsys) -> None:
    data_dir = _copy_cross_class_data_dir(tmp_path)
    worksheet_path = data_dir / "empirical" / "drafts" / CLASS_WORKSHEETS["ironclad"].name
    worksheet = json.loads(worksheet_path.read_text(encoding="utf-8"))
    worksheet["entries"][0]["card_id"] = "not_a_real_card"
    worksheet_path.write_text(json.dumps(worksheet), encoding="utf-8")
    packet = _filled_packet(build_empirical_cross_class_capture_packet(data_dir))
    packet["groups"][0]["entries"][0]["card_id"] = "not_a_real_card"
    packet_path = _write_packet(tmp_path, packet)

    status = main(["empirical-cross-class-apply-packet", str(packet_path)])

    captured = capsys.readouterr()
    assert status == 2
    assert "Missing card data for packet entry" in captured.err


def test_cross_class_apply_full_packet_makes_all_temp_worksheets_ready_for_draft_check(tmp_path) -> None:
    data_dir = _copy_cross_class_data_dir(tmp_path)
    packet = _filled_packet(build_empirical_cross_class_capture_packet(data_dir))
    packet_path = _write_packet(tmp_path, packet)

    report = build_empirical_cross_class_apply_packet_report(
        DeckseerData.load(Path("data")),
        packet_path,
        write=False,
    )

    assert report["status"] == "pass"
    assert report["summary"]["ready_groups"] == 4
    assert report["summary"]["remaining_null_fields"] == 0
    assert report["summary"]["remaining_missing_fields"] == 0


def _copy_cross_class_data_dir(tmp_path: Path) -> Path:
    data_dir = tmp_path / "data"
    drafts_dir = data_dir / "empirical" / "drafts"
    drafts_dir.mkdir(parents=True)
    for worksheet in CLASS_WORKSHEETS.values():
        shutil.copyfile(worksheet, drafts_dir / worksheet.name)
    return data_dir


def _read_worksheets(data_dir: Path) -> dict[str, str]:
    drafts_dir = data_dir / "empirical" / "drafts"
    return {
        character: (drafts_dir / worksheet.name).read_text(encoding="utf-8")
        for character, worksheet in CLASS_WORKSHEETS.items()
    }


def _load_worksheets(data_dir: Path) -> dict[str, dict]:
    drafts_dir = data_dir / "empirical" / "drafts"
    return {
        character: json.loads((drafts_dir / worksheet.name).read_text(encoding="utf-8"))
        for character, worksheet in CLASS_WORKSHEETS.items()
    }


def _write_packet(tmp_path: Path, packet: dict) -> Path:
    packet_path = tmp_path / "cross_class_packet.json"
    packet_path.write_text(json.dumps(packet), encoding="utf-8")
    return packet_path


def _filled_packet(packet: dict) -> dict:
    for group in packet["groups"]:
        for entry in group["entries"]:
            entry.update(
                {
                    "source_url": "https://sts2.fun/cards",
                    "patch": "v0.103.0",
                    "sample_size": 1200,
                    "pick_rate": 0.42,
                    "win_rate": 0.58,
                    "impact": 0.08,
                    "stat_definition": "Manual current-patch all-run STS2.fun fixture values.",
                    "captured_at": "2026-05-23",
                    "reviewer_notes": "Traceable cross-class packet test row.",
                }
            )
    return packet
