from __future__ import annotations

import argparse
from pathlib import Path

from deckseer.accuracy import build_accuracy_report
from deckseer.audit.card_priors import audit_card_priors, load_empirical_card_stats
from deckseer.data_loader import DeckseerData
from deckseer.relic_accuracy import build_relic_accuracy_report
from deckseer.rendering import render_accuracy_report, render_card_prior_audit, render_relic_accuracy_report


def handle_review_command(args: argparse.Namespace) -> int | None:
    if args.command == "accuracy-report":
        data = DeckseerData.load(Path(args.data_dir))
        report = build_accuracy_report(data, manifest_path=Path(args.manifest))
        print(render_accuracy_report(report, args.format))
        if args.fail_on_mismatch and report["summary"]["failed"] > 0:
            return 1
        return 0
    if args.command == "relic-accuracy-report":
        data = DeckseerData.load(Path(args.data_dir))
        report = build_relic_accuracy_report(data, manifest_path=Path(args.manifest))
        print(render_relic_accuracy_report(report, args.format))
        if args.fail_on_mismatch and report["summary"]["failed"] > 0:
            return 1
        return 0
    if args.command == "audit-card-priors":
        data = DeckseerData.load(Path(args.data_dir))
        stats_path = Path(args.empirical_stats)
        stats = load_empirical_card_stats(stats_path)
        result = audit_card_priors(data, stats, empirical_source=str(stats_path), min_sample_size=args.min_sample_size)
        print(render_card_prior_audit(result, args.format))
        if args.fail_on_flags and result.to_dict()["summary"]["flags"] > 0:
            return 1
        return 0
    return None


def register_accuracy_report_command(subparsers: argparse._SubParsersAction) -> None:
    accuracy_report = subparsers.add_parser("accuracy-report", help="Score reviewed accuracy scenarios and report recommendation drift.")
    accuracy_report.add_argument("--manifest", default="data/accuracy/scenarios.json", help="Accuracy scenario manifest. Defaults to data/accuracy/scenarios.json.")
    accuracy_report.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    accuracy_report.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")
    accuracy_report.add_argument("--fail-on-mismatch", action="store_true", help="Exit with status 1 when any scenario mismatches.")


def register_relic_accuracy_report_command(subparsers: argparse._SubParsersAction) -> None:
    relic_accuracy_report = subparsers.add_parser("relic-accuracy-report", help="Score reviewed relic choice scenarios and report recommendation drift.")
    relic_accuracy_report.add_argument("--manifest", default="data/relic_accuracy/scenarios.json", help="Relic accuracy scenario manifest. Defaults to data/relic_accuracy/scenarios.json.")
    relic_accuracy_report.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    relic_accuracy_report.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")
    relic_accuracy_report.add_argument("--fail-on-mismatch", action="store_true", help="Exit with status 1 when any scenario mismatches.")


def register_card_prior_audit_command(subparsers: argparse._SubParsersAction) -> None:
    audit_card_priors_parser = subparsers.add_parser(
        "audit-card-priors",
        help="Read-only review of Deckseer card priors against empirical-style card stats.",
    )
    audit_card_priors_parser.add_argument("empirical_stats", help="Path to empirical card stats JSON.")
    audit_card_priors_parser.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    audit_card_priors_parser.add_argument("--min-sample-size", type=int, default=300, help="Minimum sample size before conflict flags are trusted.")
    audit_card_priors_parser.add_argument("--format", choices=("json", "text"), default="json", help="Output format. Defaults to json.")
    audit_card_priors_parser.add_argument("--fail-on-flags", action="store_true", help="Exit with status 1 when the audit reports any flags.")
