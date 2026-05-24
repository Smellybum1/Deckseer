from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from deckseer.models import DataError, ValidationError


INTAKE_MANIFEST_TYPE = "empirical_intake_queue"
INTAKE_REVIEW_STATUSES = frozenset({"proposed", "rejected"})
INTAKE_NUMERIC_STAT_FIELDS = frozenset({"sample_size", "pick_rate", "win_rate", "impact"})


@dataclass(frozen=True)
class EmpiricalIntakeEntry:
    id: str
    character: str
    topic: str
    review_status: str
    candidate_notes: str
    source_url: str | None = None
    patch: str | None = None
    card_id: str | None = None
    captured_at: str | None = None
    stat_definition: str | None = None

    @classmethod
    def from_dict(cls, raw: Any, source_label: str) -> "EmpiricalIntakeEntry":
        if not isinstance(raw, dict):
            raise ValidationError(f"{source_label} must be an object")
        disallowed = sorted(field for field in INTAKE_NUMERIC_STAT_FIELDS if field in raw)
        if disallowed:
            fields = ", ".join(disallowed)
            raise ValidationError(f"{source_label} must not include numeric empirical stat fields: {fields}")
        return cls(
            id=_require_str(raw.get("id"), f"{source_label}.id"),
            character=_require_str(raw.get("character"), f"{source_label}.character"),
            topic=_require_str(raw.get("topic"), f"{source_label}.topic"),
            review_status=_review_status(raw.get("review_status"), f"{source_label}.review_status"),
            candidate_notes=_require_str(raw.get("candidate_notes"), f"{source_label}.candidate_notes"),
            source_url=_optional_str(raw.get("source_url"), f"{source_label}.source_url"),
            patch=_optional_str(raw.get("patch"), f"{source_label}.patch"),
            card_id=_optional_str(raw.get("card_id"), f"{source_label}.card_id"),
            captured_at=_optional_str(raw.get("captured_at"), f"{source_label}.captured_at"),
            stat_definition=_optional_str(raw.get("stat_definition"), f"{source_label}.stat_definition"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "character": self.character,
            "topic": self.topic,
            "review_status": self.review_status,
            "candidate_notes": self.candidate_notes,
            "source_url": self.source_url,
            "patch": self.patch,
            "card_id": self.card_id,
            "captured_at": self.captured_at,
            "stat_definition": self.stat_definition,
        }


def load_empirical_intake(path: Path) -> tuple[EmpiricalIntakeEntry, ...]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except FileNotFoundError as exc:
        raise DataError(f"Empirical intake file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path} is not valid JSON: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValidationError(f"{path} must contain an empirical intake manifest object")
    manifest_type = raw.get("manifest_type")
    if manifest_type != INTAKE_MANIFEST_TYPE:
        raise ValidationError(f"{path}.manifest_type must be {INTAKE_MANIFEST_TYPE}")
    entries = raw.get("entries")
    if not isinstance(entries, list):
        raise ValidationError(f"{path}.entries must be a list")
    loaded = tuple(EmpiricalIntakeEntry.from_dict(entry, f"{path.name}.entries[{index}]") for index, entry in enumerate(entries))
    _validate_unique_ids(loaded, str(path))
    return loaded


def build_empirical_intake_report(path: Path) -> dict[str, Any]:
    entries = load_empirical_intake(path)
    entries_by_character = Counter(entry.character for entry in entries)
    entries_by_review_status = Counter(entry.review_status for entry in entries)
    proposed = entries_by_review_status.get("proposed", 0)
    rejected = entries_by_review_status.get("rejected", 0)
    return {
        "intake_type": INTAKE_MANIFEST_TYPE,
        "status": "review" if proposed else "pass",
        "path": str(path),
        "summary": {
            "entries": len(entries),
            "proposed": proposed,
            "rejected": rejected,
            "entries_by_character": _sort_counts(entries_by_character),
            "entries_by_review_status": _sort_counts(entries_by_review_status),
        },
        "entries": [entry.to_dict() for entry in entries],
        "caveats": [
            "Intake entries are review notes only; they are not active empirical stats and do not affect scoring.",
            "Promote an entry to data/empirical/*.json only after exact numeric stats and provenance are reviewed.",
        ],
    }


def _validate_unique_ids(entries: tuple[EmpiricalIntakeEntry, ...], source: str) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for entry in entries:
        if entry.id in seen:
            duplicates.add(entry.id)
        seen.add(entry.id)
    if duplicates:
        ids = ", ".join(sorted(duplicates))
        raise ValidationError(f"{source} contains duplicate empirical intake ids: {ids}")


def _require_str(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{label} must be a non-empty string")
    return value


def _optional_str(value: Any, label: str) -> str | None:
    if value is None:
        return None
    return _require_str(value, label)


def _review_status(value: Any, label: str) -> str:
    status = _require_str(value, label)
    if status not in INTAKE_REVIEW_STATUSES:
        allowed = ", ".join(sorted(INTAKE_REVIEW_STATUSES))
        raise ValidationError(f"{label} must be one of: {allowed}")
    return status


def _sort_counts(counts: Counter[str]) -> dict[str, int]:
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
