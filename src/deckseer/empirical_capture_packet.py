from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from deckseer.data_loader import DeckseerData
from deckseer.empirical_capture_guide import REQUIRED_VALUES, SOURCE_TARGET
from deckseer.empirical_worksheet import (
    build_empirical_worksheet_report,
    build_empirical_worksheet_report_from_payload,
    find_worksheet_entry,
    load_worksheet_payload,
)
from deckseer.models import DataError, ValidationError


PACKET_TYPE = "empirical_capture_packet"
PACKET_REQUIRED_FIELDS = ("entry_id", "card_id") + REQUIRED_VALUES


def build_empirical_capture_packet(path: Path) -> dict[str, Any]:
    worksheet_report = build_empirical_worksheet_report(path)
    entries = [
        {field: None for field in PACKET_REQUIRED_FIELDS}
        for _ in worksheet_report["entries"]
    ]
    for packet_entry, worksheet_entry in zip(entries, worksheet_report["entries"]):
        packet_entry["entry_id"] = worksheet_entry["id"]
        packet_entry["card_id"] = worksheet_entry["card_id"]
    return {
        "packet_type": PACKET_TYPE,
        "source_target": SOURCE_TARGET,
        "worksheet_path": str(path),
        "required_fields": list(PACKET_REQUIRED_FIELDS),
        "entries": entries,
        "caveats": [
            "Fill this packet manually from reviewed STS2.fun values.",
            "Do not use blank, guessed, or synthetic values.",
            "Applying a packet previews changes unless --write is provided.",
        ],
    }


def build_empirical_capture_packet_apply_report(
    data: DeckseerData,
    packet_path: Path,
    *,
    worksheet_path: Path,
    write: bool = False,
) -> dict[str, Any]:
    packet = load_empirical_capture_packet(packet_path)
    worksheet = load_worksheet_payload(worksheet_path)
    payload = deepcopy(worksheet)
    updated_rows: list[dict[str, Any]] = []
    for packet_entry in packet["entries"]:
        entry_id = packet_entry["entry_id"]
        target = find_worksheet_entry(payload["entries"], entry_id, worksheet_path)
        if target.get("card_id") != packet_entry["card_id"]:
            raise ValidationError(f"{packet_path.name}.{entry_id}.card_id does not match worksheet card_id")
        card_id = packet_entry["card_id"]
        if card_id not in data.cards_by_id:
            raise DataError(f"Missing card data for packet entry {entry_id}: {card_id}")
        updated_fields = _apply_packet_entry(target, packet_entry)
        updated_rows.append({"entry_id": entry_id, "card_id": card_id, "updated_fields": updated_fields})

    worksheet_report = build_empirical_worksheet_report_from_payload(payload, path=worksheet_path)
    if write:
        worksheet_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return {
        "packet_type": "empirical_capture_packet_apply",
        "status": worksheet_report["status"],
        "packet_path": str(packet_path),
        "worksheet_path": str(worksheet_path),
        "write_requested": write,
        "wrote_file": write,
        "updated_rows": updated_rows,
        "payload": payload,
        "worksheet_report": worksheet_report,
        "caveats": [
            "Packet apply does not promote or activate empirical data.",
            "Preview mode does not write changes; use --write to update the worksheet file.",
            "Run empirical-draft-check only after the worksheet is ready for draft check.",
        ],
    }


def load_empirical_capture_packet(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except FileNotFoundError as exc:
        raise DataError(f"Empirical capture packet file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path} is not valid JSON: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValidationError(f"{path} must contain an empirical capture packet object")
    if raw.get("packet_type") != PACKET_TYPE:
        raise ValidationError(f"{path}.packet_type must be {PACKET_TYPE}")
    entries = raw.get("entries")
    if not isinstance(entries, list):
        raise ValidationError(f"{path}.entries must be a list")
    for index, entry in enumerate(entries):
        _validate_packet_entry(entry, f"{path.name}.entries[{index}]")
    return raw


def validate_empirical_capture_packet_entry(entry: Any, source_label: str) -> None:
    _validate_packet_entry(entry, source_label)


def apply_empirical_capture_packet_entry(target: dict[str, Any], packet_entry: dict[str, Any]) -> list[str]:
    return _apply_packet_entry(target, packet_entry)


def _validate_packet_entry(entry: Any, source_label: str) -> None:
    if not isinstance(entry, dict):
        raise ValidationError(f"{source_label} must be an object")
    for field in PACKET_REQUIRED_FIELDS:
        if field not in entry:
            raise ValidationError(f"{source_label}.{field} is required for empirical capture packets")
        if entry[field] is None:
            raise ValidationError(f"{source_label}.{field} is required for empirical capture packets and must not be null")


def _apply_packet_entry(target: dict[str, Any], packet_entry: dict[str, Any]) -> list[str]:
    updated_fields: list[str] = []
    for field in REQUIRED_VALUES:
        target[field] = packet_entry[field]
        updated_fields.append(field)
    return updated_fields
