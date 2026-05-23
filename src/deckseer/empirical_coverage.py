from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from deckseer.audit.card_priors import audit_card_priors, load_empirical_card_stats
from deckseer.data_loader import DeckseerData
from deckseer.models import DeckseerError, ValidationError


def build_empirical_coverage_report(
    data: DeckseerData,
    *,
    empirical_stats_paths: tuple[Path, ...],
    min_rows_per_character: int = 1,
    min_sample_size: int = 300,
) -> dict[str, Any]:
    if min_rows_per_character < 0:
        raise ValidationError("min_rows_per_character must be a non-negative integer")
    if min_sample_size < 0:
        raise ValidationError("min_sample_size must be a non-negative integer")

    audits: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    rows_by_character: Counter[str] = Counter()
    rows_by_patch: Counter[str] = Counter()
    rows_by_review_status: Counter[str] = Counter()
    missing_source_url_by_character: Counter[str] = Counter()
    missing_captured_at_by_character: Counter[str] = Counter()
    missing_stat_definition_by_character: Counter[str] = Counter()
    missing_reviewer_notes_by_character: Counter[str] = Counter()
    traceable_rows_by_character: Counter[str] = Counter()
    covered_card_ids: set[str] = set()

    for stats_path in empirical_stats_paths:
        try:
            stats = load_empirical_card_stats(stats_path)
            audit = audit_card_priors(data, stats, empirical_source=str(stats_path), min_sample_size=min_sample_size)
        except (DeckseerError, OSError) as exc:
            errors.append({"path": str(stats_path), "message": str(exc)})
            continue

        audits.append(audit.to_dict())
        for stat in stats:
            rows_by_character[stat.character] += 1
            rows_by_patch[stat.patch] += 1
            rows_by_review_status[stat.review_status] += 1
            if stat.source_url is None:
                missing_source_url_by_character[stat.character] += 1
            if stat.captured_at is None:
                missing_captured_at_by_character[stat.character] += 1
            if stat.stat_definition is None:
                missing_stat_definition_by_character[stat.character] += 1
            if stat.reviewer_notes is None:
                missing_reviewer_notes_by_character[stat.character] += 1
            if _is_traceable(stat):
                traceable_rows_by_character[stat.character] += 1
            covered_card_ids.add(stat.card_id)

    summary = _summarize_audits(audits, files=len(empirical_stats_paths), errors=len(errors))
    catalog_characters = sorted({card.character for card in data.cards_by_id.values() if card.character != "neutral"})
    characters_below_minimum = {
        character: rows_by_character.get(character, 0)
        for character in catalog_characters
        if rows_by_character.get(character, 0) < min_rows_per_character
    }
    coverage = {
        "min_rows_per_character": min_rows_per_character,
        "catalog_characters": catalog_characters,
        "covered_characters": sorted(character for character in rows_by_character if rows_by_character[character] > 0),
        "missing_catalog_characters": sorted(
            character for character in catalog_characters if rows_by_character.get(character, 0) == 0
        ),
        "characters_below_minimum": dict(sorted(characters_below_minimum.items())),
        "rows_by_character": _sort_counts(rows_by_character),
        "rows_by_patch": _sort_counts(rows_by_patch),
        "rows_by_review_status": _sort_counts(rows_by_review_status),
        "provenance_gaps": {
            "missing_source_url": sum(missing_source_url_by_character.values()),
            "missing_captured_at": sum(missing_captured_at_by_character.values()),
            "missing_stat_definition": sum(missing_stat_definition_by_character.values()),
            "missing_reviewer_notes": sum(missing_reviewer_notes_by_character.values()),
        },
        "provenance_gaps_by_character": {
            "missing_source_url": _sort_counts(missing_source_url_by_character),
            "missing_captured_at": _sort_counts(missing_captured_at_by_character),
            "missing_stat_definition": _sort_counts(missing_stat_definition_by_character),
            "missing_reviewer_notes": _sort_counts(missing_reviewer_notes_by_character),
        },
        "traceable_rows_by_character": _sort_counts(traceable_rows_by_character),
        "missing_traceable_catalog_characters": sorted(
            character for character in catalog_characters if traceable_rows_by_character.get(character, 0) == 0
        ),
        "covered_card_ids": sorted(covered_card_ids),
    }
    caveats = _coverage_caveats(summary=summary, coverage=coverage, errors=errors)
    status = _coverage_status(summary=summary, coverage=coverage, errors=errors)
    return {
        "coverage_type": "empirical_coverage",
        "status": status,
        "summary": summary,
        "coverage": coverage,
        "audits": audits,
        "errors": errors,
        "caveats": caveats,
    }


def _summarize_audits(audits: list[dict[str, Any]], *, files: int, errors: int) -> dict[str, Any]:
    flags_by_code: Counter[str] = Counter()
    flags_by_severity: Counter[str] = Counter()
    rows = 0
    clean_rows = 0
    flagged_rows = 0
    flags = 0
    for audit in audits:
        audit_summary = audit["summary"]
        rows += audit_summary["rows"]
        clean_rows += audit_summary["clean_rows"]
        flagged_rows += audit_summary["flagged_rows"]
        flags += audit_summary["flags"]
        flags_by_code.update(audit_summary["flags_by_code"])
        flags_by_severity.update(audit_summary["flags_by_severity"])
    return {
        "files": files,
        "loaded_files": len(audits),
        "failed_files": errors,
        "rows": rows,
        "clean_rows": clean_rows,
        "flagged_rows": flagged_rows,
        "flags": flags,
        "flags_by_code": _sort_counts(flags_by_code),
        "flags_by_severity": _sort_counts(flags_by_severity),
    }


def _coverage_status(*, summary: dict[str, Any], coverage: dict[str, Any], errors: list[dict[str, str]]) -> str:
    if errors:
        return "fail"
    if summary["flags"] or coverage["characters_below_minimum"] or any(coverage["provenance_gaps"].values()):
        return "review"
    return "pass"


def _coverage_caveats(*, summary: dict[str, Any], coverage: dict[str, Any], errors: list[dict[str, str]]) -> list[str]:
    caveats = [
        "Empirical coverage is review evidence only; it does not automatically change card priors or scoring.",
    ]
    if errors:
        caveats.append("One or more empirical files could not be loaded or validated.")
    if summary["flags"]:
        caveats.append("Active empirical audit flags need review before this coverage should be treated as clean.")
    if coverage["characters_below_minimum"]:
        missing = ", ".join(coverage["characters_below_minimum"])
        caveats.append(f"Empirical coverage is below the configured character target for: {missing}.")
    if any(coverage["provenance_gaps"].values()):
        caveats.append("Some active empirical rows are missing provenance fields needed for future review.")
    if summary["rows"] == 0:
        caveats.append("No active empirical rows were found.")
    return caveats


def _is_traceable(stat: Any) -> bool:
    return all((stat.source_url, stat.captured_at, stat.stat_definition, stat.reviewer_notes))


def _sort_counts(counts: Counter[str]) -> dict[str, int]:
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
