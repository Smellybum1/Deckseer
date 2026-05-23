from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from deckseer.data_loader import DeckseerData
from deckseer.empirical_draft import build_empirical_draft_report
from deckseer.models import ValidationError


PROMOTION_TYPE = "empirical_draft_promotion"


def build_empirical_promotion_report(
    data: DeckseerData,
    draft_path: Path,
    *,
    output_path: Path,
    data_dir: Path = Path("data"),
    write: bool = False,
    replace: bool = False,
    allow_review_flags: bool = False,
    min_sample_size: int = 300,
) -> dict[str, Any]:
    safe_output_path = _resolve_safe_output_path(output_path, data_dir=data_dir)
    draft_report = build_empirical_draft_report(data, draft_path, min_sample_size=min_sample_size)
    payload = [_active_stat_payload(entry) for entry in draft_report["entries"]]
    promotion_ready = draft_report["summary"]["promotion_ready"]
    rejected_rows = draft_report["summary"]["rows_by_review_status"].get("rejected", 0)
    write_allowed = promotion_ready or (allow_review_flags and rejected_rows == 0)

    if write and not write_allowed:
        return _report(
            draft_report=draft_report,
            output_path=safe_output_path,
            payload=payload,
            write=write,
            replace=replace,
            allow_review_flags=allow_review_flags,
            wrote_file=False,
            status="review",
            caveats=["Draft is not promotion-ready; no active empirical file was written."],
        )

    if write:
        if safe_output_path.exists() and not replace:
            raise ValidationError(f"Refusing to overwrite existing empirical file without --replace: {safe_output_path}")
        safe_output_path.parent.mkdir(parents=True, exist_ok=True)
        safe_output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        wrote_file = True
    else:
        wrote_file = False

    caveats = ["Preview only; no file was written. Re-run with --write to promote this draft."] if not write else []
    return _report(
        draft_report=draft_report,
        output_path=safe_output_path,
        payload=payload,
        write=write,
        replace=replace,
        allow_review_flags=allow_review_flags,
        wrote_file=wrote_file,
        status="pass" if promotion_ready else "review",
        caveats=caveats,
    )


def _active_stat_payload(entry: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in entry.items() if key != "id"}


def _report(
    *,
    draft_report: dict[str, Any],
    output_path: Path,
    payload: list[dict[str, Any]],
    write: bool,
    replace: bool,
    allow_review_flags: bool,
    wrote_file: bool,
    status: str,
    caveats: list[str],
) -> dict[str, Any]:
    draft_caveats = list(draft_report["caveats"])
    if write:
        draft_caveats = [
            caveat
            for caveat in draft_caveats
            if caveat != "Draft rows are validation previews only; this command does not promote or write active empirical data."
        ]
    if allow_review_flags and draft_report["summary"]["audit_flags"]:
        caveats = [
            "Review flags were explicitly allowed for this promotion; promoted rows remain review evidence only.",
            *caveats,
        ]
    return {
        "promotion_type": PROMOTION_TYPE,
        "status": status,
        "draft_path": draft_report["path"],
        "output_path": str(output_path),
        "write_requested": write,
        "replace_requested": replace,
        "allow_review_flags": allow_review_flags,
        "wrote_file": wrote_file,
        "summary": {
            "entries": draft_report["summary"]["entries"],
            "promotion_ready": draft_report["summary"]["promotion_ready"],
            "audit_flags": draft_report["summary"]["audit_flags"],
        },
        "payload": payload,
        "draft_report": draft_report,
        "caveats": [*draft_caveats, *caveats],
    }


def _resolve_safe_output_path(output_path: Path, *, data_dir: Path) -> Path:
    empirical_root = (data_dir / "empirical").resolve(strict=False)
    resolved = output_path.resolve(strict=False)
    try:
        relative = resolved.relative_to(empirical_root)
    except ValueError as exc:
        raise ValidationError(f"Empirical promotion output must be under {empirical_root}") from exc

    if not relative.parts:
        raise ValidationError("Empirical promotion output must be a JSON file, not the empirical directory")
    if relative.parts[0] == "drafts":
        raise ValidationError("Empirical promotion output must not be under data/empirical/drafts")
    if resolved.name == "intake_queue.json":
        raise ValidationError("Empirical promotion output must not overwrite data/empirical/intake_queue.json")
    if resolved.suffix.lower() != ".json":
        raise ValidationError("Empirical promotion output must be a .json file")
    return resolved
