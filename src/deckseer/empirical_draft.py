from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from deckseer.audit.card_priors import EmpiricalCardStat, audit_card_priors
from deckseer.data_loader import DeckseerData
from deckseer.models import DataError, ValidationError


DRAFT_TYPE = "empirical_stat_draft"
DRAFT_REVIEW_STATUSES = frozenset({"proposed", "accepted", "rejected"})
DRAFT_REQUIRED_FIELDS = (
    "card_id",
    "character",
    "patch",
    "source",
    "sample_size",
    "pick_rate",
    "win_rate",
    "impact",
    "source_url",
    "captured_at",
    "stat_definition",
    "reviewer_notes",
    "review_status",
)


@dataclass(frozen=True)
class EmpiricalDraftEntry:
    id: str
    stat: EmpiricalCardStat

    @classmethod
    def from_dict(cls, raw: Any, source_label: str) -> "EmpiricalDraftEntry":
        if not isinstance(raw, dict):
            raise ValidationError(f"{source_label} must be an object")
        entry_id = _require_str(raw.get("id"), f"{source_label}.id")
        _require_complete_provenance(raw, source_label)
        review_status = raw.get("review_status")
        if review_status not in DRAFT_REVIEW_STATUSES:
            allowed = ", ".join(sorted(DRAFT_REVIEW_STATUSES))
            raise ValidationError(f"{source_label}.review_status must be one of: {allowed}")
        return cls(id=entry_id, stat=EmpiricalCardStat.from_dict(raw, source_label))

    def to_dict(self) -> dict[str, Any]:
        data = {"id": self.id}
        data.update(self.stat.to_dict())
        return data


def load_empirical_draft(path: Path) -> tuple[EmpiricalDraftEntry, ...]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except FileNotFoundError as exc:
        raise DataError(f"Empirical draft file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path} is not valid JSON: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValidationError(f"{path} must contain an empirical draft object")
    if raw.get("draft_type") != DRAFT_TYPE:
        raise ValidationError(f"{path}.draft_type must be {DRAFT_TYPE}")
    entries = raw.get("entries")
    if not isinstance(entries, list):
        raise ValidationError(f"{path}.entries must be a list")
    loaded = tuple(EmpiricalDraftEntry.from_dict(entry, f"{path.name}.entries[{index}]") for index, entry in enumerate(entries))
    _validate_unique_entries(loaded, str(path))
    return loaded


def build_empirical_draft_report(data: DeckseerData, path: Path, *, min_sample_size: int = 300) -> dict[str, Any]:
    entries = load_empirical_draft(path)
    stats = tuple(entry.stat for entry in entries)
    audit = audit_card_priors(data, stats, empirical_source=str(path), min_sample_size=min_sample_size).to_dict()
    flags = audit["summary"]["flags"]
    rows_by_character = Counter(entry.stat.character for entry in entries)
    rows_by_review_status = Counter(entry.stat.review_status for entry in entries)
    rejected_rows = rows_by_review_status.get("rejected", 0)
    promotion_ready = flags == 0 and rejected_rows == 0
    status = "pass" if promotion_ready else "review"
    caveats = [
        "Draft rows are validation previews only; this command does not promote or write active empirical data.",
    ]
    if flags:
        caveats.append("One or more draft rows would produce audit flags if promoted.")
    if rejected_rows:
        caveats.append("Rejected draft rows are not promotion-ready.")
    if not entries:
        caveats.append("Draft contains no empirical rows.")
    return {
        "draft_type": DRAFT_TYPE,
        "status": status,
        "path": str(path),
        "summary": {
            "entries": len(entries),
            "promotion_ready": promotion_ready,
            "audit_flags": flags,
            "rows_by_character": _sort_counts(rows_by_character),
            "rows_by_review_status": _sort_counts(rows_by_review_status),
        },
        "entries": [entry.to_dict() for entry in entries],
        "audit_preview": audit,
        "caveats": caveats,
    }


def _validate_unique_entries(entries: tuple[EmpiricalDraftEntry, ...], source: str) -> None:
    seen_ids: set[str] = set()
    duplicate_ids: set[str] = set()
    seen_keys: set[tuple[str, str, str, str]] = set()
    duplicate_keys: set[tuple[str, str, str, str]] = set()
    for entry in entries:
        if entry.id in seen_ids:
            duplicate_ids.add(entry.id)
        seen_ids.add(entry.id)

        stat = entry.stat
        key = (stat.card_id, stat.patch, stat.source, stat.source_url or "")
        if key in seen_keys:
            duplicate_keys.add(key)
        seen_keys.add(key)
    if duplicate_ids:
        ids = ", ".join(sorted(duplicate_ids))
        raise ValidationError(f"{source} contains duplicate empirical draft ids: {ids}")
    if duplicate_keys:
        keys = ", ".join("/".join(key) for key in sorted(duplicate_keys))
        raise ValidationError(f"{source} contains duplicate empirical draft card/patch/source rows: {keys}")


def _require_complete_provenance(raw: dict[str, Any], source_label: str) -> None:
    for field in DRAFT_REQUIRED_FIELDS:
        if field not in raw:
            raise ValidationError(f"{source_label}.{field} is required for empirical draft rows")
        if raw[field] is None:
            raise ValidationError(f"{source_label}.{field} is required for empirical draft rows and must not be null")


def _require_str(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{label} must be a non-empty string")
    return value


def _sort_counts(counts: Counter[str]) -> dict[str, int]:
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
