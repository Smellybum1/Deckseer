from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from deckseer.data_loader import DeckseerData
from deckseer.empirical_draft import build_empirical_draft_report
from deckseer.empirical_triage import load_empirical_triage
from deckseer.empirical_worksheet import build_empirical_worksheet_report, load_worksheet_payload
from deckseer.models import DeckseerError


REVIEW_TYPE = "empirical_current_patch_review"
CURRENT_PATCH_BLOCKED_VALUES = frozenset({"all_patches", "all patches"})


def build_empirical_current_patch_review(
    data: DeckseerData,
    path: Path,
    *,
    triage_manifest_path: Path,
    min_sample_size: int = 300,
) -> dict[str, Any]:
    worksheet = load_worksheet_payload(path)
    worksheet_report = build_empirical_worksheet_report(path)
    triage_entries = load_empirical_triage(triage_manifest_path)

    rows = _review_rows(worksheet["entries"], worksheet_report["entries"], triage_entries)
    triage_matches = _triage_matches(rows, triage_entries)
    blocked_patch_rows = [row for row in rows if row["patch_is_all_patches"]]
    strict_error = None
    audit_preview = None
    if worksheet_report["summary"]["ready_for_draft_check"] and not blocked_patch_rows:
        try:
            draft_report = build_empirical_draft_report(data, path, min_sample_size=min_sample_size)
            audit_preview = draft_report["audit_preview"]
        except DeckseerError as exc:
            strict_error = str(exc)

    summary = _summary(worksheet_report, rows, triage_matches, blocked_patch_rows, strict_error, audit_preview)
    status = _status(summary)
    return {
        "review_type": REVIEW_TYPE,
        "status": status,
        "path": str(path),
        "triage_manifest_path": str(triage_manifest_path),
        "summary": summary,
        "rows": rows,
        "triage_matches": triage_matches,
        "audit_preview": audit_preview,
        "strict_error": strict_error,
        "caveats": _caveats(summary),
    }


def _review_rows(
    raw_entries: list[dict[str, Any]],
    worksheet_entries: list[dict[str, Any]],
    triage_entries: tuple[Any, ...],
) -> list[dict[str, Any]]:
    triage_by_card = _triage_by_card(triage_entries)
    rows: list[dict[str, Any]] = []
    for raw, reviewed in zip(raw_entries, worksheet_entries):
        card_id = reviewed["card_id"]
        patch = raw.get("patch")
        patch_is_all_patches = isinstance(patch, str) and patch.strip().lower() in CURRENT_PATCH_BLOCKED_VALUES
        triage_for_card = [entry.to_dict() for entry in triage_by_card.get(card_id, [])]
        if not reviewed["is_complete"]:
            resolution_status = "blocked_missing_fields"
        elif patch_is_all_patches:
            resolution_status = "blocked_all_patches"
        elif triage_for_card:
            resolution_status = "ready_for_promotion_review"
        else:
            resolution_status = "no_active_triage_match"
        rows.append(
            {
                "index": reviewed["index"],
                "id": reviewed["id"],
                "card_id": card_id,
                "character": reviewed["character"],
                "patch": patch if isinstance(patch, str) else None,
                "is_complete": reviewed["is_complete"],
                "missing_fields": reviewed["missing_fields"],
                "null_fields": reviewed["null_fields"],
                "patch_is_all_patches": patch_is_all_patches,
                "triage_entry_count": len(triage_for_card),
                "triage_statuses": sorted({entry["status"] for entry in triage_for_card}),
                "resolution_status": resolution_status,
            }
        )
    return rows


def _triage_matches(rows: list[dict[str, Any]], triage_entries: tuple[Any, ...]) -> list[dict[str, Any]]:
    worksheet_card_ids = {row["card_id"] for row in rows if row["card_id"]}
    matches = []
    for entry in triage_entries:
        if entry.card_id not in worksheet_card_ids:
            continue
        matches.append(
            {
                **entry.to_dict(),
                "covered_by_worksheet": True,
                "blocked": entry.status in {"needs_current_patch", "needs_scenario"},
            }
        )
    return matches


def _summary(
    worksheet_report: dict[str, Any],
    rows: list[dict[str, Any]],
    triage_matches: list[dict[str, Any]],
    blocked_patch_rows: list[dict[str, Any]],
    strict_error: str | None,
    audit_preview: dict[str, Any] | None,
) -> dict[str, Any]:
    worksheet_summary = worksheet_report["summary"]
    resolution_statuses = Counter(row["resolution_status"] for row in rows)
    cards = sorted(row["card_id"] for row in rows if row["card_id"])
    forbidden_rows = [row for row in rows if row["card_id"] == "forbidden_grimoire"]
    forbidden_grimoire_blocked = any(row["resolution_status"] != "ready_for_promotion_review" for row in forbidden_rows)
    forbidden_triage = [entry for entry in triage_matches if entry["card_id"] == "forbidden_grimoire"]
    if forbidden_triage and any(entry["status"] in {"needs_current_patch", "needs_scenario"} for entry in forbidden_triage):
        forbidden_grimoire_blocked = True
    return {
        "entries": worksheet_summary["entries"],
        "complete_entries": worksheet_summary["complete_entries"],
        "incomplete_entries": worksheet_summary["incomplete_entries"],
        "total_null_fields": worksheet_summary["total_null_fields"],
        "total_missing_fields": worksheet_summary["total_missing_fields"],
        "ready_for_draft_check": worksheet_summary["ready_for_draft_check"],
        "covered_cards": cards,
        "triage_matches": len(triage_matches),
        "triage_cards_covered": sorted({entry["card_id"] for entry in triage_matches}),
        "blocked_all_patches_rows": len(blocked_patch_rows),
        "resolution_statuses": dict(sorted(resolution_statuses.items())),
        "strict_validation_error": strict_error,
        "audit_preview_ran": audit_preview is not None,
        "audit_flags": None if audit_preview is None else audit_preview["summary"]["flags"],
        "forbidden_grimoire_blocked": forbidden_grimoire_blocked,
    }


def _status(summary: dict[str, Any]) -> str:
    if summary["strict_validation_error"]:
        return "fail"
    if (
        summary["incomplete_entries"]
        or summary["total_missing_fields"]
        or summary["total_null_fields"]
        or summary["blocked_all_patches_rows"]
        or summary["forbidden_grimoire_blocked"]
    ):
        return "review"
    return "pass"


def _caveats(summary: dict[str, Any]) -> list[str]:
    caveats = [
        "Current-patch review is read-only; it does not promote empirical data or change scoring/card priors.",
        "Use empirical-draft-check and empirical-promote-draft after this worksheet is complete and reviewed.",
    ]
    if summary["incomplete_entries"]:
        caveats.append("Worksheet rows still have missing or null fields.")
    if summary["blocked_all_patches_rows"]:
        caveats.append("All Patches rows are insufficient for current-patch triage resolution.")
    if summary["forbidden_grimoire_blocked"]:
        caveats.append("Forbidden Grimoire remains blocked from prior changes until current-patch evidence and scenario review justify a documented decision.")
    if summary["strict_validation_error"]:
        caveats.append("Strict draft validation failed after worksheet completion.")
    return caveats


def _triage_by_card(triage_entries: tuple[Any, ...]) -> dict[str | None, list[Any]]:
    by_card: dict[str | None, list[Any]] = {}
    for entry in triage_entries:
        by_card.setdefault(entry.card_id, []).append(entry)
    return by_card
