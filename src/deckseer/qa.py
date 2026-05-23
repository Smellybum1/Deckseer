from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any

from deckseer.accuracy import build_accuracy_report
from deckseer.audit.card_priors import audit_card_priors, load_empirical_card_stats
from deckseer.data_loader import DeckseerData
from deckseer.data_summary import build_data_health
from deckseer.diagnostics import check_run_files_data_coverage
from deckseer.empirical_coverage import build_empirical_coverage_report
from deckseer.empirical_triage import build_empirical_triage_report
from deckseer.models import DataError, DeckseerError, RunState, ValidationError
from deckseer.scoring.card_reward import recommend_card_reward


def build_project_qa(
    data: DeckseerData,
    *,
    empirical_stats_paths: tuple[Path, ...],
    run_paths: tuple[Path, ...] = (),
    recommendation_baseline_path: Path | None = None,
    accuracy_manifest_path: Path | None = None,
    empirical_coverage_min_rows_per_character: int | None = None,
    empirical_triage_manifest_path: Path | None = None,
    min_sample_size: int = 300,
    audit_flags_are_failures: bool = False,
) -> dict[str, Any]:
    data_health = build_data_health(data)
    run_coverage = check_run_files_data_coverage(list(run_paths), data)
    recommendation_smoke = _recommendation_smoke(run_paths, data)
    recommendation_baseline = _compare_recommendation_baseline(recommendation_smoke, recommendation_baseline_path)
    accuracy_report = build_accuracy_report(data, manifest_path=accuracy_manifest_path) if accuracy_manifest_path else None
    empirical_coverage = (
        build_empirical_coverage_report(
            data,
            empirical_stats_paths=empirical_stats_paths,
            min_rows_per_character=empirical_coverage_min_rows_per_character,
            min_sample_size=min_sample_size,
        )
        if empirical_coverage_min_rows_per_character is not None
        else None
    )
    empirical_triage = (
        build_empirical_triage_report(
            data,
            empirical_stats_paths=empirical_stats_paths,
            triage_manifest_path=empirical_triage_manifest_path,
            min_sample_size=min_sample_size,
        )
        if empirical_triage_manifest_path is not None
        else None
    )
    empirical_audits = []
    for stats_path in empirical_stats_paths:
        stats = load_empirical_card_stats(stats_path)
        audit = audit_card_priors(data, stats, empirical_source=str(stats_path), min_sample_size=min_sample_size)
        empirical_audits.append(audit.to_dict())

    empirical_flags = sum(audit["summary"]["flags"] for audit in empirical_audits)
    empirical_flags_by_code = _sum_audit_counts(empirical_audits, "flags_by_code")
    empirical_flags_by_severity = _sum_audit_counts(empirical_audits, "flags_by_severity")
    blocked_run_files = run_coverage["summary"]["blocked_files"]
    recommendation_smoke_failures = recommendation_smoke["summary"]["failed_files"]
    recommendation_baseline_mismatches = recommendation_baseline["summary"]["mismatches"]
    accuracy_failures = accuracy_report["summary"]["failed"] if accuracy_report else 0
    empirical_coverage_status = empirical_coverage["status"] if empirical_coverage else None
    empirical_triage_status = empirical_triage["status"] if empirical_triage else None
    status = "pass"
    if data_health["status"] != "pass":
        status = "fail"
    elif blocked_run_files:
        status = "fail"
    elif recommendation_smoke_failures:
        status = "fail"
    elif recommendation_baseline_mismatches:
        status = "fail"
    elif accuracy_failures:
        status = "fail"
    elif empirical_coverage_status == "fail":
        status = "fail"
    elif empirical_triage_status == "fail":
        status = "fail"
    elif empirical_flags and audit_flags_are_failures:
        status = "fail"
    elif empirical_coverage_status == "review":
        status = "review"
    elif empirical_triage_status == "review":
        status = "review"
    elif empirical_flags and empirical_triage_status != "pass":
        status = "review"

    return {
        "qa_type": "project_qa",
        "status": status,
        "summary": {
            "data_health_status": data_health["status"],
            "data_health_failures": data_health["failure_count"],
            "run_files": run_coverage["summary"]["total_files"],
            "run_blocked_files": blocked_run_files,
            "run_files_with_deck_metadata_gaps": run_coverage["summary"]["files_with_deck_metadata_gaps"],
            "recommendation_smoke_passed": recommendation_smoke["summary"]["passed_files"],
            "recommendation_smoke_failed": recommendation_smoke_failures,
            "recommendation_baseline_checked": recommendation_baseline["checked"],
            "recommendation_baseline_mismatches": recommendation_baseline_mismatches,
            "accuracy_checked": accuracy_report is not None,
            "accuracy_passed": accuracy_report["summary"]["passed"] if accuracy_report else 0,
            "accuracy_failed": accuracy_failures,
            "empirical_coverage_checked": empirical_coverage is not None,
            "empirical_coverage_status": empirical_coverage_status,
            "empirical_coverage_rows": empirical_coverage["summary"]["rows"] if empirical_coverage else 0,
            "empirical_coverage_missing_characters": (
                len(empirical_coverage["coverage"]["missing_catalog_characters"]) if empirical_coverage else 0
            ),
            "empirical_triage_checked": empirical_triage is not None,
            "empirical_triage_status": empirical_triage_status,
            "empirical_triage_active_flags": empirical_triage["summary"]["active_flags"] if empirical_triage else 0,
            "empirical_triage_triaged_flags": empirical_triage["summary"]["triaged_flags"] if empirical_triage else 0,
            "empirical_triage_missing_entries": empirical_triage["summary"]["missing_triage_entries"] if empirical_triage else 0,
            "empirical_triage_stale_entries": empirical_triage["summary"]["stale_triage_entries"] if empirical_triage else 0,
            "empirical_triage_open_entries": empirical_triage["summary"]["open_triage_entries"] if empirical_triage else 0,
            "empirical_audits": len(empirical_audits),
            "empirical_flags": empirical_flags,
            "empirical_flags_by_code": empirical_flags_by_code,
            "empirical_flags_by_severity": empirical_flags_by_severity,
            "empirical_flags_are_failures": audit_flags_are_failures,
        },
        "data_health": data_health,
        "run_coverage": run_coverage,
        "recommendation_smoke": recommendation_smoke,
        "recommendation_baseline": recommendation_baseline,
        "accuracy_report": accuracy_report,
        "empirical_coverage": empirical_coverage,
        "empirical_triage": empirical_triage,
        "empirical_audits": empirical_audits,
        "caveats": _project_qa_caveats(
            audit_flags_are_failures=audit_flags_are_failures,
            empirical_coverage=empirical_coverage,
            empirical_triage=empirical_triage,
        ),
    }


def discover_empirical_stats(data_dir: Path) -> tuple[Path, ...]:
    empirical_dir = data_dir / "empirical"
    if not empirical_dir.exists():
        return ()
    excluded = {"intake_queue.json", "triage.json"}
    return tuple(sorted(path for path in empirical_dir.glob("*.json") if path.name not in excluded))


def _sum_audit_counts(empirical_audits: list[dict[str, Any]], summary_key: str) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for audit in empirical_audits:
        counts.update(audit["summary"][summary_key])
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _project_qa_caveats(
    *,
    audit_flags_are_failures: bool,
    empirical_coverage: dict[str, Any] | None,
    empirical_triage: dict[str, Any] | None,
) -> list[str]:
    if audit_flags_are_failures:
        caveats = [
            "Empirical audit flags are configured as failures for this QA run.",
            "Empirical audit flags are still review prompts, not automatic scoring changes.",
        ]
    else:
        caveats = [
            "Empirical audit flags are review prompts, not automatic scoring changes.",
            "Use --fail-on-audit-flags when you want empirical review flags to fail the command.",
        ]
    if empirical_coverage is not None:
        caveats.extend(empirical_coverage["caveats"])
    if empirical_triage is not None:
        caveats.extend(empirical_triage["caveats"])
    return caveats


def discover_example_runs(examples_dir: Path) -> tuple[Path, ...]:
    if not examples_dir.exists():
        return ()
    return tuple(sorted(examples_dir.glob("*.json")))


def build_recommendation_smoke_baseline(data: DeckseerData, *, run_paths: tuple[Path, ...]) -> dict[str, Any]:
    recommendation_smoke = _recommendation_smoke(run_paths, data)
    failed = [check for check in recommendation_smoke["checks"] if not check["passed"]]
    if failed:
        paths = ", ".join(check["path"] for check in failed)
        raise DataError(f"Cannot build recommendation baseline because smoke scoring failed for: {paths}")
    return {
        "baseline_type": "recommendation_smoke_baseline",
        "entries": [
            {
                "path": _normalize_path_for_baseline(check["path"]),
                "top_choice": check["top_choice"],
            }
            for check in recommendation_smoke["checks"]
        ],
    }


def write_recommendation_smoke_baseline(baseline: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8")


def _recommendation_smoke(paths: tuple[Path, ...], data: DeckseerData) -> dict[str, Any]:
    checks = []
    for path in paths:
        try:
            run = RunState.from_json_file(path)
            result = recommend_card_reward(run, data)
        except (DeckseerError, OSError) as exc:
            checks.append(
                {
                    "path": str(path),
                    "passed": False,
                    "error": str(exc),
                }
            )
            continue
        checks.append(
            {
                "path": str(path),
                "passed": True,
                "top_choice": result.ranked_choices[0].choice,
                "top_score": round(result.ranked_choices[0].score, 1),
                "confidence": result.ranked_choices[0].confidence,
            }
        )
    return {
        "check_type": "recommendation_smoke",
        "summary": {
            "total_files": len(checks),
            "passed_files": sum(1 for check in checks if check["passed"]),
            "failed_files": sum(1 for check in checks if not check["passed"]),
        },
        "checks": checks,
    }


def _compare_recommendation_baseline(recommendation_smoke: dict[str, Any], baseline_path: Path | None) -> dict[str, Any]:
    if baseline_path is None:
        return {
            "checked": False,
            "path": None,
            "summary": {
                "expected_entries": 0,
                "checked_entries": 0,
                "mismatches": 0,
            },
            "mismatches": [],
        }

    baseline = _load_recommendation_baseline(baseline_path)
    current_by_path = {
        _normalize_path_for_baseline(check["path"]): check
        for check in recommendation_smoke["checks"]
        if check["passed"]
    }
    mismatches = []
    for entry in baseline["entries"]:
        path = entry["path"]
        expected_choice = entry["top_choice"]
        current = current_by_path.get(path)
        if current is None:
            mismatches.append(
                {
                    "path": path,
                    "expected_top_choice": expected_choice,
                    "actual_top_choice": None,
                    "reason": "missing_smoke_result",
                }
            )
            continue
        actual_choice = current["top_choice"]
        if actual_choice != expected_choice:
            mismatches.append(
                {
                    "path": path,
                    "expected_top_choice": expected_choice,
                    "actual_top_choice": actual_choice,
                    "reason": "top_choice_changed",
                }
            )

    return {
        "checked": True,
        "path": str(baseline_path),
        "summary": {
            "expected_entries": len(baseline["entries"]),
            "checked_entries": len(baseline["entries"]) - len(mismatches),
            "mismatches": len(mismatches),
        },
        "mismatches": mismatches,
    }


def _load_recommendation_baseline(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except FileNotFoundError as exc:
        raise DataError(f"Recommendation baseline file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValidationError(f"{path} must contain a recommendation smoke baseline object")
    if raw.get("baseline_type") != "recommendation_smoke_baseline":
        raise ValidationError(f"{path}.baseline_type must be recommendation_smoke_baseline")
    entries = raw.get("entries")
    if not isinstance(entries, list):
        raise ValidationError(f"{path}.entries must be a list")
    normalized_entries = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValidationError(f"{path}.entries[{index}] must be an object")
        entry_path = entry.get("path")
        top_choice = entry.get("top_choice")
        if not isinstance(entry_path, str) or not entry_path:
            raise ValidationError(f"{path}.entries[{index}].path must be a non-empty string")
        if not isinstance(top_choice, str) or not top_choice:
            raise ValidationError(f"{path}.entries[{index}].top_choice must be a non-empty string")
        normalized_entries.append(
            {
                "path": _normalize_path_for_baseline(entry_path),
                "top_choice": top_choice,
            }
        )
    return {
        "baseline_type": "recommendation_smoke_baseline",
        "entries": normalized_entries,
    }


def _normalize_path_for_baseline(path: str) -> str:
    return path.replace("\\", "/")
