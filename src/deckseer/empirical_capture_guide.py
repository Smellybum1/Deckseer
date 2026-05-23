from __future__ import annotations

from pathlib import Path
from typing import Any

from deckseer.empirical_worksheet import build_empirical_worksheet_report
from deckseer.models import ValidationError


GUIDE_TYPE = "empirical_capture_guide"
SOURCE_TARGET = "STS2.fun current patch, all runs"
DEFAULT_WORKSHEETS = {
    "ironclad": "ironclad_sts2fun_current_patch_capture_batch.json",
    "silent": "silent_sts2fun_current_patch_capture_batch.json",
    "defect": "defect_sts2fun_current_patch_capture_batch.json",
    "necrobinder": "necrobinder_sts2fun_capture_batch.json",
    "regent": "regent_sts2fun_current_patch_capture_batch.json",
}
REQUIRED_VALUES = (
    "source_url",
    "patch",
    "sample_size",
    "pick_rate",
    "win_rate",
    "impact",
    "stat_definition",
    "captured_at",
    "reviewer_notes",
)
SAFETY_FLOW = (
    "empirical-worksheet-check",
    "empirical-worksheet-fill preview",
    "empirical-worksheet-fill --write",
    "empirical-draft-check",
    "empirical-promote-draft preview",
    "empirical-promote-draft --write after review",
)


def build_empirical_capture_guide(
    character: str,
    *,
    data_dir: Path,
    worksheet_path: Path | None = None,
) -> dict[str, Any]:
    normalized_character = character.lower()
    if normalized_character not in DEFAULT_WORKSHEETS:
        supported = ", ".join(sorted(DEFAULT_WORKSHEETS))
        raise ValidationError(f"empirical capture guide currently supports only: {supported}")

    if worksheet_path is None:
        worksheet_path = data_dir / "empirical" / "drafts" / DEFAULT_WORKSHEETS[normalized_character]
    worksheet_report = build_empirical_worksheet_report(worksheet_path)
    rows = [_build_row(row, worksheet_path) for row in worksheet_report["entries"]]
    return {
        "guide_type": GUIDE_TYPE,
        "status": worksheet_report["status"],
        "character": normalized_character,
        "worksheet_path": str(worksheet_path),
        "source_target": SOURCE_TARGET,
        "required_values": list(REQUIRED_VALUES),
        "safety_flow": list(SAFETY_FLOW),
        "rows": rows,
        "worksheet_summary": worksheet_report["summary"],
        "caveats": [
            "This guide does not scrape STS2.fun, write worksheet files, promote empirical data, or change scoring.",
            "Copy values manually from the reviewed source and run the preview command before using --write.",
        ],
    }


def _build_row(row: dict[str, Any], worksheet_path: Path) -> dict[str, Any]:
    entry_id = row["id"]
    card_id = row["card_id"]
    return {
        "entry_id": entry_id,
        "card_id": card_id,
        "missing_fields": row["missing_fields"],
        "null_fields": row["null_fields"],
        "is_complete": row["is_complete"],
        "preview_command": _fill_command(worksheet_path, entry_id, write=False),
        "write_command": _fill_command(worksheet_path, entry_id, write=True),
    }


def _fill_command(worksheet_path: Path, entry_id: str, *, write: bool) -> str:
    parts = [
        "deckseer",
        "empirical-worksheet-fill",
        str(worksheet_path),
        "--entry-id",
        entry_id,
        "--source-url",
        '"<source_url>"',
        "--patch",
        '"<patch>"',
        "--sample-size",
        "<sample_size>",
        "--pick-rate",
        "<pick_rate>",
        "--win-rate",
        "<win_rate>",
        "--impact",
        "<impact>",
        "--captured-at",
        "<YYYY-MM-DD>",
        "--stat-definition",
        '"<STS2.fun metric and filters>"',
        "--reviewer-notes",
        '"<review notes>"',
        "--format",
        "text",
    ]
    if write:
        parts.append("--write")
    return " ".join(parts)
