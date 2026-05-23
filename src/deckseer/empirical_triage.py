from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from deckseer.audit.card_priors import audit_card_priors, load_empirical_card_stats
from deckseer.data_loader import DeckseerData
from deckseer.models import DataError, DeckseerError, ValidationError


TRIAGE_TYPE = "empirical_flag_triage"
TRIAGE_REPORT_TYPE = "empirical_triage_report"
TRIAGE_STATUSES = frozenset({"open", "needs_current_patch", "needs_scenario", "resolved_no_change", "resolved_change_planned"})
OPEN_TRIAGE_STATUSES = frozenset({"open"})
RESOLVED_TRIAGE_STATUSES = frozenset({"resolved_no_change"})


@dataclass(frozen=True)
class EmpiricalTriageEntry:
    id: str
    empirical_file: str
    card_id: str
    flag_code: str
    status: str
    decision: str
    next_action: str
    reviewer_notes: str
    reviewed_at: str

    @classmethod
    def from_dict(cls, raw: Any, source_label: str) -> "EmpiricalTriageEntry":
        if not isinstance(raw, dict):
            raise ValidationError(f"{source_label} must be an object")
        status = _require_str(raw.get("status"), f"{source_label}.status")
        if status not in TRIAGE_STATUSES:
            allowed = ", ".join(sorted(TRIAGE_STATUSES))
            raise ValidationError(f"{source_label}.status must be one of: {allowed}")
        return cls(
            id=_require_str(raw.get("id"), f"{source_label}.id"),
            empirical_file=_normalize_path(_require_str(raw.get("empirical_file"), f"{source_label}.empirical_file")),
            card_id=_require_str(raw.get("card_id"), f"{source_label}.card_id"),
            flag_code=_require_str(raw.get("flag_code"), f"{source_label}.flag_code"),
            status=status,
            decision=_require_str(raw.get("decision"), f"{source_label}.decision"),
            next_action=_require_str(raw.get("next_action"), f"{source_label}.next_action"),
            reviewer_notes=_require_str(raw.get("reviewer_notes"), f"{source_label}.reviewer_notes"),
            reviewed_at=_require_str(raw.get("reviewed_at"), f"{source_label}.reviewed_at"),
        )

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.empirical_file, self.card_id, self.flag_code)

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "empirical_file": self.empirical_file,
            "card_id": self.card_id,
            "flag_code": self.flag_code,
            "status": self.status,
            "decision": self.decision,
            "next_action": self.next_action,
            "reviewer_notes": self.reviewer_notes,
            "reviewed_at": self.reviewed_at,
        }


def load_empirical_triage(path: Path) -> tuple[EmpiricalTriageEntry, ...]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except FileNotFoundError as exc:
        raise DataError(f"Empirical triage manifest not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path} is not valid JSON: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValidationError(f"{path} must contain an empirical triage object")
    if raw.get("triage_type") != TRIAGE_TYPE:
        raise ValidationError(f"{path}.triage_type must be {TRIAGE_TYPE}")
    entries = raw.get("entries")
    if not isinstance(entries, list):
        raise ValidationError(f"{path}.entries must be a list")
    loaded = tuple(EmpiricalTriageEntry.from_dict(entry, f"{path.name}.entries[{index}]") for index, entry in enumerate(entries))
    _validate_unique_entries(loaded, str(path))
    return loaded


def build_empirical_triage_report(
    data: DeckseerData,
    *,
    empirical_stats_paths: tuple[Path, ...],
    triage_manifest_path: Path,
    min_sample_size: int = 300,
) -> dict[str, Any]:
    triage_entries = load_empirical_triage(triage_manifest_path)
    active_flags, audit_errors = _active_empirical_flags(data, empirical_stats_paths, min_sample_size=min_sample_size)

    triage_by_key = {entry.key: entry for entry in triage_entries}
    active_keys = {flag["key"] for flag in active_flags}
    matched = []
    missing = []
    for flag in active_flags:
        triage = triage_by_key.get(flag["key"])
        if triage is None:
            missing.append({key: value for key, value in flag.items() if key != "key"})
            continue
        matched.append(
            {
                **{key: value for key, value in flag.items() if key != "key"},
                "triage": triage.to_dict(),
            }
        )

    stale = [entry.to_dict() for entry in triage_entries if entry.key not in active_keys]
    open_entries = [entry.to_dict() for entry in triage_entries if entry.key in active_keys and entry.status in OPEN_TRIAGE_STATUSES]
    summary = _summary(active_flags, matched, missing, stale, open_entries, triage_entries, audit_errors)
    status = _status(summary)
    return {
        "report_type": TRIAGE_REPORT_TYPE,
        "status": status,
        "manifest_path": str(triage_manifest_path),
        "summary": summary,
        "matched_flags": matched,
        "missing_triage": missing,
        "stale_triage": stale,
        "open_triage": open_entries,
        "audit_errors": audit_errors,
        "caveats": _caveats(summary),
    }


def _active_empirical_flags(
    data: DeckseerData,
    empirical_stats_paths: tuple[Path, ...],
    *,
    min_sample_size: int,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    flags: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for stats_path in empirical_stats_paths:
        try:
            stats = load_empirical_card_stats(stats_path)
            audit = audit_card_priors(data, stats, empirical_source=str(stats_path), min_sample_size=min_sample_size).to_dict()
        except (DeckseerError, OSError) as exc:
            errors.append({"path": str(stats_path), "message": str(exc)})
            continue
        empirical_file = _normalize_path(str(stats_path))
        for row in audit["rows"]:
            for flag in row["flags"]:
                key = (empirical_file, row["card_id"], flag["code"])
                flags.append(
                    {
                        "key": key,
                        "empirical_file": empirical_file,
                        "card_id": row["card_id"],
                        "card_name": row["name"],
                        "character": row["character"],
                        "flag_code": flag["code"],
                        "severity": flag["severity"],
                        "message": flag["message"],
                        "patch": row["patch"],
                        "quality_prior": row["quality_prior"],
                        "empirical_impact": row["empirical_impact"],
                        "sample_size": row["sample_size"],
                    }
                )
    return sorted(flags, key=lambda flag: flag["key"]), errors


def _summary(
    active_flags: list[dict[str, Any]],
    matched: list[dict[str, Any]],
    missing: list[dict[str, Any]],
    stale: list[dict[str, str]],
    open_entries: list[dict[str, str]],
    triage_entries: tuple[EmpiricalTriageEntry, ...],
    audit_errors: list[dict[str, str]],
) -> dict[str, Any]:
    statuses = Counter(entry.status for entry in triage_entries)
    active_statuses = Counter(row["triage"]["status"] for row in matched)
    unresolved_statuses = Counter(
        row["triage"]["status"]
        for row in matched
        if row["triage"]["status"] not in RESOLVED_TRIAGE_STATUSES
    )
    if missing:
        unresolved_statuses["missing_triage"] += len(missing)
    resolved_active_flags = sum(
        1 for row in matched if row["triage"]["status"] in RESOLVED_TRIAGE_STATUSES
    )
    unresolved_active_flags = len(active_flags) - resolved_active_flags
    codes = Counter(flag["flag_code"] for flag in active_flags)
    cards = Counter(flag["card_id"] for flag in active_flags)
    next_actions = Counter(row["triage"]["next_action"] for row in matched)
    return {
        "active_flags": len(active_flags),
        "triaged_flags": len(matched),
        "resolved_active_flags": resolved_active_flags,
        "unresolved_active_flags": unresolved_active_flags,
        "missing_triage_entries": len(missing),
        "stale_triage_entries": len(stale),
        "open_triage_entries": len(open_entries),
        "audit_errors": len(audit_errors),
        "triage_entries": len(triage_entries),
        "statuses_by_triage_entry": _sort_counts(statuses),
        "statuses_by_active_flag": _sort_counts(active_statuses),
        "unresolved_statuses_by_active_flag": _sort_counts(unresolved_statuses),
        "flags_by_code": _sort_counts(codes),
        "flags_by_card": _sort_counts(cards),
        "next_actions": _sort_counts(next_actions),
    }


def _status(summary: dict[str, Any]) -> str:
    if summary["audit_errors"]:
        return "fail"
    if (
        summary["missing_triage_entries"]
        or summary["stale_triage_entries"]
        or summary["open_triage_entries"]
        or summary["unresolved_active_flags"]
    ):
        return "review"
    return "pass"


def _caveats(summary: dict[str, Any]) -> list[str]:
    caveats = [
        "Empirical triage records are review notes only; they do not change scoring or card priors.",
    ]
    if summary["audit_errors"]:
        caveats.append("One or more active empirical files could not be audited.")
    if summary["missing_triage_entries"]:
        caveats.append("Some active empirical audit flags do not have triage entries yet.")
    if summary["stale_triage_entries"]:
        caveats.append("Some triage entries no longer match active empirical audit flags.")
    if summary["open_triage_entries"]:
        caveats.append("Some active empirical audit flags are still marked open.")
    if summary["unresolved_active_flags"]:
        caveats.append("Active empirical flags remain review work until resolved by current-patch evidence, scenarios, or documented no-change decisions.")
    elif summary["active_flags"]:
        caveats.append("All active empirical flags are triaged as resolved_no_change and are treated as reviewed, non-blocking context.")
    return caveats


def _validate_unique_entries(entries: tuple[EmpiricalTriageEntry, ...], source: str) -> None:
    seen_ids: set[str] = set()
    duplicate_ids: set[str] = set()
    seen_keys: set[tuple[str, str, str]] = set()
    duplicate_keys: set[tuple[str, str, str]] = set()
    for entry in entries:
        if entry.id in seen_ids:
            duplicate_ids.add(entry.id)
        seen_ids.add(entry.id)
        if entry.key in seen_keys:
            duplicate_keys.add(entry.key)
        seen_keys.add(entry.key)
    if duplicate_ids:
        ids = ", ".join(sorted(duplicate_ids))
        raise ValidationError(f"{source} contains duplicate empirical triage ids: {ids}")
    if duplicate_keys:
        keys = ", ".join("/".join(key) for key in sorted(duplicate_keys))
        raise ValidationError(f"{source} contains duplicate empirical triage flag keys: {keys}")


def _require_str(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{label} must be a non-empty string")
    return value


def _normalize_path(value: str) -> str:
    return value.replace("\\", "/")


def _sort_counts(counts: Counter[str]) -> dict[str, int]:
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
