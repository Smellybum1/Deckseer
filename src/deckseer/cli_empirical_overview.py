from __future__ import annotations

import argparse
from pathlib import Path

from deckseer.data_loader import DeckseerData
from deckseer.empirical_coverage import build_empirical_coverage_report
from deckseer.empirical_current_patch import build_empirical_current_patch_review
from deckseer.empirical_intake import build_empirical_intake_report
from deckseer.empirical_triage import build_empirical_triage_report
from deckseer.qa import discover_empirical_stats
from deckseer.rendering import (
    render_empirical_coverage,
    render_empirical_current_patch_review,
    render_empirical_intake,
    render_empirical_triage,
)


def handle_empirical_overview_command(args: argparse.Namespace) -> int | None:
    if args.command == "empirical-coverage":
        data_dir = Path(args.data_dir)
        data = DeckseerData.load(data_dir)
        report = build_empirical_coverage_report(
            data,
            empirical_stats_paths=discover_empirical_stats(data_dir),
            min_rows_per_character=args.min_rows_per_character,
            min_sample_size=args.min_sample_size,
        )
        print(render_empirical_coverage(report, args.format))
        if args.fail_on_review and report["status"] in {"fail", "review"}:
            return 1
        if report["status"] == "fail":
            return 1
        return 0
    if args.command == "empirical-intake":
        report = build_empirical_intake_report(Path(args.manifest))
        print(render_empirical_intake(report, args.format))
        return 0
    if args.command == "empirical-triage-report":
        data_dir = Path(args.data_dir)
        data = DeckseerData.load(data_dir)
        report = build_empirical_triage_report(
            data,
            empirical_stats_paths=discover_empirical_stats(data_dir),
            triage_manifest_path=Path(args.manifest),
            min_sample_size=args.min_sample_size,
        )
        print(render_empirical_triage(report, args.format))
        if report["status"] == "fail":
            return 1
        if args.fail_on_open and (
            report["summary"]["missing_triage_entries"] or report["summary"]["open_triage_entries"]
        ):
            return 1
        return 0
    if args.command == "empirical-current-patch-review":
        data = DeckseerData.load(Path(args.data_dir))
        report = build_empirical_current_patch_review(
            data,
            Path(args.worksheet_json),
            triage_manifest_path=Path(args.triage_manifest),
            min_sample_size=args.min_sample_size,
        )
        print(render_empirical_current_patch_review(report, args.format))
        return 1 if report["status"] == "fail" else 0
    return None


def register_empirical_overview_commands(subparsers: argparse._SubParsersAction) -> None:
    empirical_coverage = subparsers.add_parser("empirical-coverage", help="Summarize active empirical review coverage by character and patch.")
    empirical_coverage.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    empirical_coverage.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")
    empirical_coverage.add_argument("--min-rows-per-character", type=int, default=1, help="Minimum rows per catalog character. Defaults to 1.")
    empirical_coverage.add_argument("--min-sample-size", type=int, default=300, help="Minimum sample size before empirical conflict flags are trusted.")
    empirical_coverage.add_argument("--fail-on-review", action="store_true", help="Exit with status 1 when coverage status is review or fail.")

    empirical_intake = subparsers.add_parser("empirical-intake", help="Summarize pending empirical intake notes without activating them.")
    empirical_intake.add_argument("--manifest", default="data/empirical/intake_queue.json", help="Empirical intake manifest. Defaults to data/empirical/intake_queue.json.")
    empirical_intake.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")

    empirical_triage = subparsers.add_parser("empirical-triage-report", help="Cross-check active empirical audit flags against the triage manifest.")
    empirical_triage.add_argument("--manifest", default="data/empirical/triage.json", help="Empirical triage manifest. Defaults to data/empirical/triage.json.")
    empirical_triage.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    empirical_triage.add_argument("--min-sample-size", type=int, default=300, help="Minimum sample size before empirical conflict flags are trusted.")
    empirical_triage.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")
    empirical_triage.add_argument("--fail-on-open", action="store_true", help="Exit with status 1 when active flags are missing triage or still open.")

    empirical_current_patch = subparsers.add_parser(
        "empirical-current-patch-review",
        help="Review whether a current-patch empirical worksheet is ready to resolve active triage items.",
    )
    empirical_current_patch.add_argument("worksheet_json", help="Path to an empirical_stat_draft worksheet JSON file.")
    empirical_current_patch.add_argument("--triage-manifest", default="data/empirical/triage.json", help="Empirical triage manifest. Defaults to data/empirical/triage.json.")
    empirical_current_patch.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    empirical_current_patch.add_argument("--min-sample-size", type=int, default=300, help="Minimum sample size before empirical conflict flags are trusted.")
    empirical_current_patch.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")
