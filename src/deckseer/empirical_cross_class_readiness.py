from __future__ import annotations

from pathlib import Path
from typing import Any

from deckseer.data_loader import DeckseerData
from deckseer.empirical_capture_guide import DEFAULT_WORKSHEETS
from deckseer.empirical_cross_class_packet import CROSS_CLASS_CHARACTERS
from deckseer.empirical_draft import build_empirical_draft_report
from deckseer.empirical_worksheet import build_empirical_worksheet_report


READINESS_TYPE = "empirical_cross_class_readiness"


def build_empirical_cross_class_readiness_report(
    data: DeckseerData,
    *,
    data_dir: Path,
    min_sample_size: int = 300,
) -> dict[str, Any]:
    worksheets = []
    caveats = [
        "Readiness review is read-only; it does not scrape, write worksheets, promote rows, or change scoring.",
        "Draft worksheets remain inactive until strict validation, review, and explicit promotion.",
    ]

    for character in CROSS_CLASS_CHARACTERS:
        path = data_dir / "empirical" / "drafts" / DEFAULT_WORKSHEETS[character]
        worksheet_report = build_empirical_worksheet_report(path)
        worksheet_summary = worksheet_report["summary"]
        ready_for_draft_check = worksheet_summary["ready_for_draft_check"]
        audit_preview = None
        audit_flags = 0
        status = "review"
        next_commands = _incomplete_next_commands(path)

        if ready_for_draft_check:
            draft_report = build_empirical_draft_report(data, path, min_sample_size=min_sample_size)
            audit_preview = draft_report["audit_preview"]
            audit_flags = draft_report["summary"]["audit_flags"]
            if audit_flags:
                next_commands = _review_next_commands(path, character)
            else:
                status = "pass"
                next_commands = _clean_next_commands(path, character)

        worksheets.append(
            {
                "character": character,
                "path": str(path),
                "status": status,
                "ready_for_draft_check": ready_for_draft_check,
                "remaining_null_fields": worksheet_summary["total_null_fields"],
                "remaining_missing_fields": worksheet_summary["total_missing_fields"],
                "audit_flags": audit_flags,
                "audit_preview": audit_preview,
                "next_command": next_commands[0],
                "next_commands": next_commands,
                "worksheet_report": worksheet_report,
            }
        )

    complete_worksheets = sum(1 for worksheet in worksheets if worksheet["ready_for_draft_check"])
    audit_flags = sum(worksheet["audit_flags"] for worksheet in worksheets)
    remaining_null_fields = sum(worksheet["remaining_null_fields"] for worksheet in worksheets)
    remaining_missing_fields = sum(worksheet["remaining_missing_fields"] for worksheet in worksheets)
    incomplete_worksheets = len(worksheets) - complete_worksheets
    status = "pass" if incomplete_worksheets == 0 and audit_flags == 0 else "review"

    if incomplete_worksheets:
        caveats.append("One or more worksheets still have null or missing fields.")
    if audit_flags:
        caveats.append("One or more complete worksheets would produce audit flags if promoted.")

    return {
        "report_type": READINESS_TYPE,
        "status": status,
        "summary": {
            "worksheets": len(worksheets),
            "complete_worksheets": complete_worksheets,
            "incomplete_worksheets": incomplete_worksheets,
            "ready_for_draft_check": complete_worksheets,
            "audit_flags": audit_flags,
            "remaining_null_fields": remaining_null_fields,
            "remaining_missing_fields": remaining_missing_fields,
        },
        "worksheets": worksheets,
        "caveats": caveats,
    }


def _incomplete_next_commands(path: Path) -> list[str]:
    return [
        "deckseer empirical-cross-class-capture-packet --format json",
        "deckseer empirical-cross-class-apply-packet packet.json --format text",
        f"deckseer empirical-worksheet-check {path} --format text",
    ]


def _clean_next_commands(path: Path, character: str) -> list[str]:
    return [
        f"deckseer empirical-draft-check {path} --format text",
        f"deckseer empirical-promote-draft {path} --output data/empirical/{character}_sts2fun_current_patch_reviewed.json",
    ]


def _review_next_commands(path: Path, character: str) -> list[str]:
    return [
        f"deckseer empirical-draft-check {path} --format text",
        (
            f"deckseer empirical-promote-draft {path} "
            f"--output data/empirical/{character}_sts2fun_current_patch_reviewed.json --allow-review-flags"
        ),
        "Review audit flags and add triage records before treating promoted rows as non-blocking.",
    ]
