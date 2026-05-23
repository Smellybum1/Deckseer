from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from deckseer.data_loader import DeckseerData
from deckseer.empirical_draft import DRAFT_REQUIRED_FIELDS, DRAFT_TYPE
from deckseer.models import DataError, ValidationError


WORKSHEET_TYPE = "empirical_stat_worksheet"
WORKSHEET_REQUIRED_FIELDS = ("id",) + DRAFT_REQUIRED_FIELDS


def build_empirical_worksheet_report(path: Path) -> dict[str, Any]:
    raw = load_worksheet_payload(path)
    return build_empirical_worksheet_report_from_payload(raw, path=path)


def build_empirical_worksheet_report_from_payload(raw: dict[str, Any], *, path: Path) -> dict[str, Any]:
    entries = raw["entries"]
    reviewed_entries = [_review_entry(entry, index) for index, entry in enumerate(entries)]

    complete_entries = sum(1 for entry in reviewed_entries if entry["is_complete"])
    incomplete_entries = len(reviewed_entries) - complete_entries
    total_null_fields = sum(len(entry["null_fields"]) for entry in reviewed_entries)
    total_missing_fields = sum(len(entry["missing_fields"]) for entry in reviewed_entries)
    ready_for_draft_check = incomplete_entries == 0
    rows_by_character = Counter(entry["character"] for entry in reviewed_entries if entry["character"] is not None)

    caveats = [
        "Worksheet review does not promote or activate empirical data.",
        "Run empirical-draft-check after filling all null and missing fields.",
    ]
    if incomplete_entries:
        caveats.append("Incomplete worksheet entries cannot pass strict draft validation or promotion.")

    return {
        "worksheet_type": WORKSHEET_TYPE,
        "status": "pass" if ready_for_draft_check else "review",
        "path": str(path),
        "summary": {
            "entries": len(reviewed_entries),
            "complete_entries": complete_entries,
            "incomplete_entries": incomplete_entries,
            "total_null_fields": total_null_fields,
            "total_missing_fields": total_missing_fields,
            "ready_for_draft_check": ready_for_draft_check,
            "rows_by_character": _sort_counts(rows_by_character),
        },
        "entries": reviewed_entries,
        "caveats": caveats,
    }


def build_empirical_worksheet_fill_report(
    data: DeckseerData,
    path: Path,
    *,
    entry_id: str | None,
    updates: dict[str, Any],
    write: bool = False,
) -> dict[str, Any]:
    if not entry_id:
        raise ValidationError("empirical worksheet fill requires --entry-id")
    raw = load_worksheet_payload(path)
    before_report = build_empirical_worksheet_report_from_payload(raw, path=path)
    payload = deepcopy(raw)
    entries = payload["entries"]
    target = _find_entry(entries, entry_id, path)
    updated_fields = _apply_updates(target, updates)
    card_id = target.get("card_id")
    if not isinstance(card_id, str) or not card_id:
        raise ValidationError(f"{path.name}.{entry_id}.card_id must be a non-empty string before worksheet fill")
    if card_id not in data.cards_by_id:
        raise DataError(f"Missing card data for worksheet entry {entry_id}: {card_id}")
    worksheet_report = build_empirical_worksheet_report_from_payload(payload, path=path)

    if write:
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return {
        "worksheet_type": "empirical_stat_worksheet_fill",
        "status": worksheet_report["status"],
        "path": str(path),
        "write_requested": write,
        "wrote_file": write,
        "updated_entry_id": entry_id,
        "updated_fields": updated_fields,
        "before_summary": before_report["summary"],
        "payload": payload,
        "worksheet_report": worksheet_report,
        "caveats": [
            "Worksheet fill does not promote or activate empirical data.",
            "Preview mode does not write changes; use --write to update the worksheet file.",
            "Run empirical-draft-check only after the worksheet is ready for draft check.",
        ],
    }


def load_worksheet_payload(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except FileNotFoundError as exc:
        raise DataError(f"Empirical worksheet file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path} is not valid JSON: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValidationError(f"{path} must contain an empirical worksheet object")
    if raw.get("draft_type") != DRAFT_TYPE:
        raise ValidationError(f"{path}.draft_type must be {DRAFT_TYPE}")
    entries = raw.get("entries")
    if not isinstance(entries, list):
        raise ValidationError(f"{path}.entries must be a list")
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValidationError(f"{path.name}.entries[{index}] must be an object")
    return raw


def _find_entry(entries: list[dict[str, Any]], entry_id: str, path: Path) -> dict[str, Any]:
    matches = [entry for entry in entries if entry.get("id") == entry_id]
    if not matches:
        raise ValidationError(f"{path.name} does not contain worksheet entry id: {entry_id}")
    if len(matches) > 1:
        raise ValidationError(f"{path.name} contains duplicate worksheet entry id: {entry_id}")
    return matches[0]


def find_worksheet_entry(entries: list[dict[str, Any]], entry_id: str, path: Path) -> dict[str, Any]:
    return _find_entry(entries, entry_id, path)


def _apply_updates(target: dict[str, Any], updates: dict[str, Any]) -> list[str]:
    updated_fields: list[str] = []
    for field, value in updates.items():
        if value is None:
            continue
        target[field] = value
        updated_fields.append(field)
    return updated_fields


def _review_entry(raw: dict[str, Any], index: int) -> dict[str, Any]:
    missing_fields = [field for field in WORKSHEET_REQUIRED_FIELDS if field not in raw]
    null_fields = [field for field in WORKSHEET_REQUIRED_FIELDS if field in raw and raw[field] is None]
    entry_id = raw.get("id")
    card_id = raw.get("card_id")
    character = raw.get("character")
    return {
        "index": index,
        "id": entry_id if isinstance(entry_id, str) else None,
        "card_id": card_id if isinstance(card_id, str) else None,
        "character": character if isinstance(character, str) else None,
        "missing_fields": missing_fields,
        "null_fields": null_fields,
        "is_complete": not missing_fields and not null_fields,
    }


def _sort_counts(counts: Counter[str]) -> dict[str, int]:
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
