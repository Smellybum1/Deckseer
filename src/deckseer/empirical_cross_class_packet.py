from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from deckseer.data_loader import DeckseerData
from deckseer.empirical_capture_guide import DEFAULT_WORKSHEETS, SOURCE_TARGET
from deckseer.empirical_capture_packet import (
    PACKET_REQUIRED_FIELDS,
    apply_empirical_capture_packet_entry,
    build_empirical_capture_packet,
    validate_empirical_capture_packet_entry,
)
from deckseer.empirical_worksheet import (
    build_empirical_worksheet_report_from_payload,
    find_worksheet_entry,
    load_worksheet_payload,
)
from deckseer.models import DataError, ValidationError


CROSS_CLASS_PACKET_TYPE = "empirical_cross_class_capture_packet"
CROSS_CLASS_APPLY_TYPE = "empirical_cross_class_capture_packet_apply"
CROSS_CLASS_CHARACTERS = ("ironclad", "silent", "defect", "regent")


def build_empirical_cross_class_capture_packet(data_dir: Path) -> dict[str, Any]:
    groups = []
    total_entries = 0
    for character in CROSS_CLASS_CHARACTERS:
        worksheet_path = data_dir / "empirical" / "drafts" / DEFAULT_WORKSHEETS[character]
        packet = build_empirical_capture_packet(worksheet_path)
        entries = packet["entries"]
        total_entries += len(entries)
        groups.append(
            {
                "character": character,
                "worksheet_path": str(worksheet_path),
                "entries": entries,
            }
        )

    return {
        "packet_type": CROSS_CLASS_PACKET_TYPE,
        "source_target": SOURCE_TARGET,
        "characters": list(CROSS_CLASS_CHARACTERS),
        "required_fields": list(PACKET_REQUIRED_FIELDS),
        "summary": {
            "groups": len(groups),
            "entries": total_entries,
        },
        "groups": groups,
        "caveats": [
            "Fill this packet manually from reviewed STS2.fun current-patch values.",
            "This command does not scrape, write worksheets, promote empirical data, or change scoring.",
            "Apply the filled packet in preview mode first; use --write only after review.",
        ],
    }


def build_empirical_cross_class_apply_packet_report(
    data: DeckseerData,
    packet_path: Path,
    *,
    write: bool = False,
) -> dict[str, Any]:
    packet = load_empirical_cross_class_capture_packet(packet_path)
    groups = []
    total_updated_rows = 0
    ready_groups = 0
    remaining_null_fields = 0
    remaining_missing_fields = 0

    for group in packet["groups"]:
        worksheet_path = Path(group["worksheet_path"])
        worksheet = load_worksheet_payload(worksheet_path)
        payload = deepcopy(worksheet)
        updated_rows = []

        for packet_entry in group["entries"]:
            entry_id = packet_entry["entry_id"]
            target = find_worksheet_entry(payload["entries"], entry_id, worksheet_path)
            if target.get("card_id") != packet_entry["card_id"]:
                raise ValidationError(f"{packet_path.name}.{entry_id}.card_id does not match worksheet card_id")
            card_id = packet_entry["card_id"]
            if card_id not in data.cards_by_id:
                raise DataError(f"Missing card data for packet entry {entry_id}: {card_id}")
            updated_fields = apply_empirical_capture_packet_entry(target, packet_entry)
            updated_rows.append({"entry_id": entry_id, "card_id": card_id, "updated_fields": updated_fields})

        worksheet_report = build_empirical_worksheet_report_from_payload(payload, path=worksheet_path)
        worksheet_summary = worksheet_report["summary"]
        total_updated_rows += len(updated_rows)
        remaining_null_fields += worksheet_summary["total_null_fields"]
        remaining_missing_fields += worksheet_summary["total_missing_fields"]
        if worksheet_summary["ready_for_draft_check"]:
            ready_groups += 1
        if write:
            worksheet_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

        groups.append(
            {
                "character": group["character"],
                "worksheet_path": str(worksheet_path),
                "updated_rows": updated_rows,
                "payload": payload,
                "worksheet_report": worksheet_report,
            }
        )

    incomplete_groups = len(groups) - ready_groups
    status = "pass" if incomplete_groups == 0 else "review"
    return {
        "packet_type": CROSS_CLASS_APPLY_TYPE,
        "status": status,
        "packet_path": str(packet_path),
        "write_requested": write,
        "wrote_files": write,
        "summary": {
            "groups": len(groups),
            "entries": sum(len(group["entries"]) for group in packet["groups"]),
            "updated_rows": total_updated_rows,
            "ready_groups": ready_groups,
            "incomplete_groups": incomplete_groups,
            "remaining_null_fields": remaining_null_fields,
            "remaining_missing_fields": remaining_missing_fields,
        },
        "groups": groups,
        "caveats": [
            "Cross-class packet apply does not promote or activate empirical data.",
            "Preview mode does not write changes; use --write to update worksheet files.",
            "Run empirical-draft-check on each worksheet only after it is ready for draft check.",
        ],
    }


def load_empirical_cross_class_capture_packet(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except FileNotFoundError as exc:
        raise DataError(f"Empirical cross-class capture packet file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path} is not valid JSON: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValidationError(f"{path} must contain an empirical cross-class capture packet object")
    if raw.get("packet_type") != CROSS_CLASS_PACKET_TYPE:
        raise ValidationError(f"{path}.packet_type must be {CROSS_CLASS_PACKET_TYPE}")
    groups = raw.get("groups")
    if not isinstance(groups, list):
        raise ValidationError(f"{path}.groups must be a list")
    if not groups:
        raise ValidationError(f"{path}.groups must not be empty")

    seen_characters: set[str] = set()
    for group_index, group in enumerate(groups):
        if not isinstance(group, dict):
            raise ValidationError(f"{path.name}.groups[{group_index}] must be an object")
        character = group.get("character")
        if character not in CROSS_CLASS_CHARACTERS:
            supported = ", ".join(CROSS_CLASS_CHARACTERS)
            raise ValidationError(f"{path.name}.groups[{group_index}].character must be one of: {supported}")
        if character in seen_characters:
            raise ValidationError(f"{path.name}.groups contains duplicate character: {character}")
        seen_characters.add(character)
        worksheet_path = group.get("worksheet_path")
        if not isinstance(worksheet_path, str) or not worksheet_path:
            raise ValidationError(f"{path.name}.groups[{group_index}].worksheet_path must be a non-empty string")
        entries = group.get("entries")
        if not isinstance(entries, list):
            raise ValidationError(f"{path.name}.groups[{group_index}].entries must be a list")
        for entry_index, entry in enumerate(entries):
            validate_empirical_capture_packet_entry(entry, f"{path.name}.groups[{group_index}].entries[{entry_index}]")
    return raw
