from __future__ import annotations

from pathlib import Path
from typing import Any

from deckseer.data_loader import DeckseerData
from deckseer.empirical_capture_guide import DEFAULT_WORKSHEETS
from deckseer.empirical_cross_class_packet import CROSS_CLASS_CHARACTERS
from deckseer.empirical_promotion import build_empirical_promotion_report
from deckseer.empirical_worksheet import build_empirical_worksheet_report


PROMOTION_PREVIEW_TYPE = "empirical_cross_class_promotion_preview"


def build_empirical_cross_class_promotion_preview_report(
    data: DeckseerData,
    *,
    data_dir: Path,
    min_sample_size: int = 300,
) -> dict[str, Any]:
    previews = []
    caveats = [
        "Cross-class promotion preview is read-only; it does not write active empirical files.",
        "Use empirical-promote-draft for each class after reviewing this report.",
    ]

    for character in CROSS_CLASS_CHARACTERS:
        worksheet_path = data_dir / "empirical" / "drafts" / DEFAULT_WORKSHEETS[character]
        output_path = data_dir / "empirical" / f"{character}_sts2fun_current_patch_reviewed.json"
        worksheet_report = build_empirical_worksheet_report(worksheet_path)
        worksheet_summary = worksheet_report["summary"]
        remaining_null_fields = worksheet_summary["total_null_fields"]
        remaining_missing_fields = worksheet_summary["total_missing_fields"]
        blocked = not worksheet_summary["ready_for_draft_check"]
        promotion_preview = None
        audit_flags = 0
        allow_review_flags_needed = False
        output_exists = output_path.exists()
        status = "blocked" if blocked else "review"

        if not blocked:
            promotion_preview = build_empirical_promotion_report(
                data,
                worksheet_path,
                output_path=output_path,
                data_dir=data_dir,
                min_sample_size=min_sample_size,
            )
            audit_flags = promotion_preview["summary"]["audit_flags"]
            allow_review_flags_needed = audit_flags > 0
            if promotion_preview["status"] == "pass" and not output_exists:
                status = "pass"
            elif output_exists:
                status = "blocked"

        previews.append(
            {
                "character": character,
                "worksheet_path": str(worksheet_path),
                "output_path": str(output_path),
                "status": status,
                "remaining_null_fields": remaining_null_fields,
                "remaining_missing_fields": remaining_missing_fields,
                "audit_flags": audit_flags,
                "allow_review_flags_needed": allow_review_flags_needed,
                "output_exists": output_exists,
                "promotion_preview": promotion_preview,
                "next_command": _next_command(
                    character=character,
                    worksheet_path=worksheet_path,
                    output_path=output_path,
                    blocked=blocked,
                    audit_flags=audit_flags,
                    output_exists=output_exists,
                ),
                "worksheet_report": worksheet_report,
            }
        )

    blocked_worksheets = sum(1 for preview in previews if preview["status"] == "blocked")
    audit_flags = sum(preview["audit_flags"] for preview in previews)
    review_needed = sum(1 for preview in previews if preview["status"] == "review")
    promotion_ready = sum(1 for preview in previews if preview["status"] == "pass")
    status = "pass" if promotion_ready == len(previews) else "review"

    if blocked_worksheets:
        caveats.append("One or more worksheets are incomplete or have an existing output file that needs explicit review.")
    if review_needed:
        caveats.append("One or more complete worksheets would need review before promotion.")

    return {
        "report_type": PROMOTION_PREVIEW_TYPE,
        "status": status,
        "summary": {
            "worksheets": len(previews),
            "blocked_worksheets": blocked_worksheets,
            "promotion_ready": promotion_ready,
            "review_needed": review_needed,
            "audit_flags": audit_flags,
        },
        "previews": previews,
        "caveats": caveats,
    }


def _next_command(
    *,
    character: str,
    worksheet_path: Path,
    output_path: Path,
    blocked: bool,
    audit_flags: int,
    output_exists: bool,
) -> str:
    if output_exists:
        return f"Review existing output before replacing: {output_path}"
    if blocked:
        return "deckseer empirical-cross-class-capture-packet --format json"

    command = f"deckseer empirical-promote-draft {worksheet_path} --output {output_path}"
    if audit_flags:
        command = f"{command} --allow-review-flags"
    return command
