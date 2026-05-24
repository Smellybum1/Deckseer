from __future__ import annotations

import argparse
import json
from pathlib import Path

from deckseer.data_loader import DeckseerData
from deckseer.diagnostics import check_run_files_data_coverage
from deckseer.qa import (
    build_project_qa,
    build_recommendation_smoke_baseline,
    discover_empirical_stats,
    discover_example_runs,
    write_recommendation_smoke_baseline,
)
from deckseer.rendering import render_project_qa


def handle_qa_command(args: argparse.Namespace) -> int | None:
    if args.command == "qa":
        data_dir = Path(args.data_dir)
        data = DeckseerData.load(data_dir)
        empirical_stats_paths = tuple(Path(path) for path in args.empirical_stats) if args.empirical_stats else discover_empirical_stats(data_dir)
        run_paths = (
            tuple(_expand_run_paths([Path(path) for path in args.run_paths]))
            if args.run_paths is not None
            else discover_example_runs(Path(args.examples_dir))
        )
        recommendation_baseline_path = _resolve_recommendation_baseline_path(
            data_dir,
            explicit_path=args.recommendation_baseline,
            use_default=args.check_recommendation_baseline or args.strict,
        )
        accuracy_manifest_path = data_dir / "accuracy" / "scenarios.json" if args.check_accuracy else None
        report = build_project_qa(
            data,
            empirical_stats_paths=empirical_stats_paths,
            run_paths=run_paths,
            recommendation_baseline_path=recommendation_baseline_path,
            accuracy_manifest_path=accuracy_manifest_path,
            empirical_coverage_min_rows_per_character=(
                args.min_empirical_rows_per_character if args.check_empirical_coverage else None
            ),
            empirical_triage_manifest_path=(data_dir / "empirical" / "triage.json" if args.check_empirical_triage else None),
            min_sample_size=args.min_sample_size,
            audit_flags_are_failures=args.fail_on_audit_flags or args.strict,
        )
        print(render_project_qa(report, args.format))
        if report["status"] == "fail":
            return 1
        return 0
    if args.command == "qa-baseline":
        data = DeckseerData.load(Path(args.data_dir))
        run_paths = (
            tuple(_expand_run_paths([Path(path) for path in args.run_paths]))
            if args.run_paths is not None
            else discover_example_runs(Path(args.examples_dir))
        )
        baseline = build_recommendation_smoke_baseline(data, run_paths=run_paths)
        if args.output:
            write_recommendation_smoke_baseline(baseline, Path(args.output))
        print(json.dumps(baseline, indent=2))
        return 0
    if args.command == "check-runs":
        data = DeckseerData.load(Path(args.data_dir))
        paths = _expand_run_paths([Path(path) for path in args.paths])
        print(json.dumps(check_run_files_data_coverage(paths, data), indent=2))
        return 0
    return None


def register_qa_commands(subparsers: argparse._SubParsersAction) -> None:
    qa = subparsers.add_parser("qa", help="Run project-native data health and empirical audit checks.")
    qa.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    qa.add_argument("--examples-dir", default="examples", help="Directory of example run-state JSON files to check when --run-paths is omitted.")
    qa.add_argument("--run-paths", nargs="*", help="Run-state JSON files or directories to check. Defaults to examples/*.json.")
    qa.add_argument("--empirical-stats", nargs="*", help="Empirical stats JSON files. Defaults to all JSON files under data/empirical.")
    qa.add_argument("--recommendation-baseline", help="Optional recommendation smoke baseline JSON file for top-choice drift checks.")
    qa.add_argument(
        "--check-recommendation-baseline",
        action="store_true",
        help="Check the default recommendation baseline under data/qa/recommendation_smoke_baseline.json.",
    )
    qa.add_argument("--min-sample-size", type=int, default=300, help="Minimum sample size before empirical conflict flags are trusted.")
    qa.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")
    qa.add_argument("--fail-on-audit-flags", action="store_true", help="Exit with status 1 when empirical audits report any flags.")
    qa.add_argument("--check-accuracy", action="store_true", help="Check the default accuracy scenario manifest under data/accuracy/scenarios.json.")
    qa.add_argument("--check-empirical-coverage", action="store_true", help="Check active empirical coverage against catalog characters.")
    qa.add_argument("--check-empirical-triage", action="store_true", help="Check active empirical audit flags against data/empirical/triage.json.")
    qa.add_argument(
        "--min-empirical-rows-per-character",
        type=int,
        default=1,
        help="Minimum active empirical rows per catalog character when --check-empirical-coverage is used.",
    )
    qa.add_argument(
        "--strict",
        action="store_true",
        help="Check the default recommendation baseline and fail on empirical audit flags.",
    )

    qa_baseline = subparsers.add_parser("qa-baseline", help="Generate a recommendation smoke baseline from run-state JSON files.")
    qa_baseline.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    qa_baseline.add_argument("--examples-dir", default="examples", help="Directory of example run-state JSON files to use when --run-paths is omitted.")
    qa_baseline.add_argument("--run-paths", nargs="*", help="Run-state JSON files or directories to baseline. Defaults to examples/*.json.")
    qa_baseline.add_argument("--output", help="Optional output path for the baseline JSON. Defaults to printing only.")


def register_check_runs_command(subparsers: argparse._SubParsersAction) -> None:
    check_runs = subparsers.add_parser("check-runs", help="Batch-check run-state JSON files or directories for data coverage.")
    check_runs.add_argument("paths", nargs="+", help="Run-state JSON files or directories containing *.json files.")
    check_runs.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")


def _expand_run_paths(paths: list[Path]) -> list[Path]:
    expanded: list[Path] = []
    for path in paths:
        if path.is_dir():
            expanded.extend(sorted(path.glob("*.json")))
        else:
            expanded.append(path)
    return expanded


def _resolve_recommendation_baseline_path(
    data_dir: Path,
    *,
    explicit_path: str | None,
    use_default: bool,
) -> Path | None:
    if explicit_path:
        return Path(explicit_path)
    if use_default:
        return data_dir / "qa" / "recommendation_smoke_baseline.json"
    return None
