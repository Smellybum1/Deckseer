from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from deckseer.accuracy import build_accuracy_report
from deckseer.cli_data import handle_data_command, register_data_commands
from deckseer.cli_exporter import (
    handle_exporter_command,
    register_exporter_inspection_commands,
    register_exporter_recommendation_commands,
)
from deckseer.cli_run_state import (
    handle_run_state_command,
    register_run_state_commands,
    register_run_state_normalize_command,
)
from deckseer.cli_save import handle_save_command, register_save_inspection_commands, register_save_recommendation_commands
from deckseer.data_loader import DeckseerData
from deckseer.diagnostics import check_run_files_data_coverage
from deckseer.empirical_coverage import build_empirical_coverage_report
from deckseer.empirical_capture_guide import build_empirical_capture_guide
from deckseer.empirical_capture_packet import build_empirical_capture_packet, build_empirical_capture_packet_apply_report
from deckseer.empirical_current_patch import build_empirical_current_patch_review
from deckseer.empirical_cross_class_packet import (
    build_empirical_cross_class_apply_packet_report,
    build_empirical_cross_class_capture_packet,
)
from deckseer.empirical_cross_class_promotion import build_empirical_cross_class_promotion_preview_report
from deckseer.empirical_cross_class_readiness import build_empirical_cross_class_readiness_report
from deckseer.empirical_draft import build_empirical_draft_report
from deckseer.empirical_intake import build_empirical_intake_report
from deckseer.empirical_promotion import build_empirical_promotion_report
from deckseer.empirical_triage import build_empirical_triage_report
from deckseer.empirical_worksheet import build_empirical_worksheet_fill_report, build_empirical_worksheet_report
from deckseer.models import DeckseerError
from deckseer.audit.card_priors import audit_card_priors, load_empirical_card_stats
from deckseer.qa import (
    build_project_qa,
    build_recommendation_smoke_baseline,
    discover_empirical_stats,
    discover_example_runs,
    write_recommendation_smoke_baseline,
)
from deckseer.rendering import (
    render_accuracy_report,
    render_card_prior_audit,
    render_empirical_capture_guide,
    render_empirical_capture_packet,
    render_empirical_capture_packet_apply,
    render_empirical_coverage,
    render_empirical_current_patch_review,
    render_empirical_cross_class_capture_packet,
    render_empirical_cross_class_capture_packet_apply,
    render_empirical_cross_class_promotion_preview,
    render_empirical_cross_class_readiness,
    render_empirical_draft,
    render_empirical_intake,
    render_empirical_promotion,
    render_empirical_triage,
    render_empirical_worksheet,
    render_empirical_worksheet_fill,
    render_project_qa,
)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
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
        if args.command == "accuracy-report":
            data = DeckseerData.load(Path(args.data_dir))
            report = build_accuracy_report(data, manifest_path=Path(args.manifest))
            print(render_accuracy_report(report, args.format))
            if args.fail_on_mismatch and report["summary"]["failed"] > 0:
                return 1
            return 0
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
        if args.command == "empirical-capture-guide":
            worksheet_path = Path(args.worksheet) if args.worksheet else None
            report = build_empirical_capture_guide(args.character, data_dir=Path(args.data_dir), worksheet_path=worksheet_path)
            print(render_empirical_capture_guide(report, args.format))
            return 0
        if args.command == "empirical-capture-packet":
            report = build_empirical_capture_packet(Path(args.worksheet_json))
            print(render_empirical_capture_packet(report, args.format))
            return 0
        if args.command == "empirical-cross-class-capture-packet":
            report = build_empirical_cross_class_capture_packet(Path(args.data_dir))
            print(render_empirical_cross_class_capture_packet(report, args.format))
            return 0
        if args.command == "empirical-cross-class-apply-packet":
            data = DeckseerData.load(Path(args.data_dir))
            report = build_empirical_cross_class_apply_packet_report(
                data,
                Path(args.packet_json),
                write=args.write,
            )
            print(render_empirical_cross_class_capture_packet_apply(report, args.format))
            return 0
        if args.command == "empirical-cross-class-readiness":
            data_dir = Path(args.data_dir)
            data = DeckseerData.load(data_dir)
            report = build_empirical_cross_class_readiness_report(
                data,
                data_dir=data_dir,
                min_sample_size=args.min_sample_size,
            )
            print(render_empirical_cross_class_readiness(report, args.format))
            return 0 if report["status"] != "fail" else 1
        if args.command == "empirical-cross-class-promotion-preview":
            data_dir = Path(args.data_dir)
            data = DeckseerData.load(data_dir)
            report = build_empirical_cross_class_promotion_preview_report(
                data,
                data_dir=data_dir,
                min_sample_size=args.min_sample_size,
            )
            print(render_empirical_cross_class_promotion_preview(report, args.format))
            return 0 if report["status"] != "fail" else 1
        if args.command == "empirical-worksheet-apply-packet":
            data = DeckseerData.load(Path(args.data_dir))
            report = build_empirical_capture_packet_apply_report(
                data,
                Path(args.packet_json),
                worksheet_path=Path(args.worksheet),
                write=args.write,
            )
            print(render_empirical_capture_packet_apply(report, args.format))
            return 0
        if args.command == "empirical-draft-check":
            data = DeckseerData.load(Path(args.data_dir))
            report = build_empirical_draft_report(data, Path(args.draft_json), min_sample_size=args.min_sample_size)
            print(render_empirical_draft(report, args.format))
            if args.fail_on_review and report["status"] == "review":
                return 1
            return 0
        if args.command == "empirical-worksheet-check":
            report = build_empirical_worksheet_report(Path(args.worksheet_json))
            print(render_empirical_worksheet(report, args.format))
            if args.fail_on_incomplete and not report["summary"]["ready_for_draft_check"]:
                return 1
            return 0
        if args.command == "empirical-worksheet-fill":
            data = DeckseerData.load(Path(args.data_dir))
            updates = {
                "patch": args.patch,
                "sample_size": args.sample_size,
                "pick_rate": args.pick_rate,
                "win_rate": args.win_rate,
                "impact": args.impact,
                "captured_at": args.captured_at,
                "stat_definition": args.stat_definition,
                "reviewer_notes": args.reviewer_notes,
                "source_url": args.source_url,
                "act": args.act,
                "ascension": args.ascension,
                "review_status": args.review_status,
            }
            report = build_empirical_worksheet_fill_report(
                data,
                Path(args.worksheet_json),
                entry_id=args.entry_id,
                updates=updates,
                write=args.write,
            )
            print(render_empirical_worksheet_fill(report, args.format))
            return 0
        if args.command == "empirical-promote-draft":
            data_dir = Path(args.data_dir)
            data = DeckseerData.load(data_dir)
            report = build_empirical_promotion_report(
                data,
                Path(args.draft_json),
                output_path=Path(args.output),
                data_dir=data_dir,
                write=args.write,
                replace=args.replace,
                allow_review_flags=args.allow_review_flags,
                min_sample_size=args.min_sample_size,
            )
            print(render_empirical_promotion(report, args.format))
            if report["status"] == "review" and not report["wrote_file"]:
                return 1
            return 0
        if args.command == "check-runs":
            data = DeckseerData.load(Path(args.data_dir))
            paths = _expand_run_paths([Path(path) for path in args.paths])
            print(json.dumps(check_run_files_data_coverage(paths, data), indent=2))
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
        data_status = handle_data_command(args)
        if data_status is not None:
            return data_status
        save_status = handle_save_command(args)
        if save_status is not None:
            return save_status
        run_state_status = handle_run_state_command(args)
        if run_state_status is not None:
            return run_state_status
        exporter_status = handle_exporter_command(args)
        if exporter_status is not None:
            return exporter_status
        parser.error("missing command")
    except DeckseerError as exc:
        print(f"deckseer: {exc}", file=sys.stderr)
        return 2

    return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="deckseer", description="Local decision-support coach for Slay the Spire 2.")
    subparsers = parser.add_subparsers(dest="command")

    register_data_commands(subparsers)

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

    accuracy_report = subparsers.add_parser("accuracy-report", help="Score reviewed accuracy scenarios and report recommendation drift.")
    accuracy_report.add_argument("--manifest", default="data/accuracy/scenarios.json", help="Accuracy scenario manifest. Defaults to data/accuracy/scenarios.json.")
    accuracy_report.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    accuracy_report.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")
    accuracy_report.add_argument("--fail-on-mismatch", action="store_true", help="Exit with status 1 when any scenario mismatches.")

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

    empirical_capture_guide = subparsers.add_parser("empirical-capture-guide", help="Print manual empirical capture instructions for a worksheet batch.")
    empirical_capture_guide.add_argument("--character", required=True, help="Character guide to show. Currently supports necrobinder.")
    empirical_capture_guide.add_argument("--worksheet", help="Optional empirical worksheet JSON file. Defaults to the Necrobinder capture batch.")
    empirical_capture_guide.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    empirical_capture_guide.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")

    empirical_capture_packet = subparsers.add_parser("empirical-capture-packet", help="Generate a manual fill-in packet from an empirical worksheet.")
    empirical_capture_packet.add_argument("worksheet_json", help="Path to an empirical_stat_draft worksheet JSON file.")
    empirical_capture_packet.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")

    empirical_cross_capture_packet = subparsers.add_parser(
        "empirical-cross-class-capture-packet",
        help="Generate one manual fill-in packet for Ironclad, Silent, Defect, and Regent worksheets.",
    )
    empirical_cross_capture_packet.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    empirical_cross_capture_packet.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")

    empirical_cross_apply_packet = subparsers.add_parser(
        "empirical-cross-class-apply-packet",
        help="Preview or write a filled cross-class empirical capture packet into its worksheets.",
    )
    empirical_cross_apply_packet.add_argument("packet_json", help="Path to an empirical_cross_class_capture_packet JSON file.")
    empirical_cross_apply_packet.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    empirical_cross_apply_packet.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")
    empirical_cross_apply_packet.add_argument("--write", action="store_true", help="Write updated worksheets. Defaults to preview only.")

    empirical_cross_readiness = subparsers.add_parser(
        "empirical-cross-class-readiness",
        help="Review cross-class empirical worksheets before strict draft checks or promotion.",
    )
    empirical_cross_readiness.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    empirical_cross_readiness.add_argument("--min-sample-size", type=int, default=300, help="Minimum sample size before empirical conflict flags are trusted.")
    empirical_cross_readiness.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")

    empirical_cross_promotion_preview = subparsers.add_parser(
        "empirical-cross-class-promotion-preview",
        help="Preview active empirical promotion outputs for cross-class worksheets without writing files.",
    )
    empirical_cross_promotion_preview.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    empirical_cross_promotion_preview.add_argument("--min-sample-size", type=int, default=300, help="Minimum sample size before empirical conflict flags are trusted.")
    empirical_cross_promotion_preview.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")

    empirical_apply_packet = subparsers.add_parser(
        "empirical-worksheet-apply-packet",
        help="Preview or write a filled empirical capture packet into a worksheet.",
    )
    empirical_apply_packet.add_argument("packet_json", help="Path to an empirical_capture_packet JSON file.")
    empirical_apply_packet.add_argument("--worksheet", required=True, help="Target empirical worksheet JSON file.")
    empirical_apply_packet.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    empirical_apply_packet.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")
    empirical_apply_packet.add_argument("--write", action="store_true", help="Write the updated worksheet. Defaults to preview only.")

    empirical_draft = subparsers.add_parser("empirical-draft-check", help="Validate manually captured empirical stat drafts before promotion.")
    empirical_draft.add_argument("draft_json", help="Path to an empirical_stat_draft JSON file.")
    empirical_draft.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    empirical_draft.add_argument("--min-sample-size", type=int, default=300, help="Minimum sample size before empirical conflict flags are trusted.")
    empirical_draft.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")
    empirical_draft.add_argument("--fail-on-review", action="store_true", help="Exit with status 1 when the draft is valid but needs review.")

    empirical_worksheet = subparsers.add_parser(
        "empirical-worksheet-check",
        help="Review incomplete empirical capture worksheets without promoting them.",
    )
    empirical_worksheet.add_argument("worksheet_json", help="Path to an empirical_stat_draft worksheet JSON file.")
    empirical_worksheet.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")
    empirical_worksheet.add_argument("--fail-on-incomplete", action="store_true", help="Exit with status 1 when worksheet entries still have null or missing fields.")

    empirical_worksheet_fill = subparsers.add_parser(
        "empirical-worksheet-fill",
        help="Preview or write field updates for one empirical capture worksheet row.",
    )
    empirical_worksheet_fill.add_argument("worksheet_json", help="Path to an empirical_stat_draft worksheet JSON file.")
    empirical_worksheet_fill.add_argument("--entry-id", help="Worksheet entry id to update.")
    empirical_worksheet_fill.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    empirical_worksheet_fill.add_argument("--patch", help="Observed game patch for the empirical row.")
    empirical_worksheet_fill.add_argument("--sample-size", type=int, help="Exact observed sample size.")
    empirical_worksheet_fill.add_argument("--pick-rate", type=float, help="Exact observed pick rate.")
    empirical_worksheet_fill.add_argument("--win-rate", type=float, help="Exact observed win rate.")
    empirical_worksheet_fill.add_argument("--impact", type=float, help="Exact observed impact value.")
    empirical_worksheet_fill.add_argument("--captured-at", help="Capture date, for example 2026-05-23.")
    empirical_worksheet_fill.add_argument("--stat-definition", help="Definition of the copied empirical metric and filters.")
    empirical_worksheet_fill.add_argument("--reviewer-notes", help="Reviewer notes, filters, page context, or caveats.")
    empirical_worksheet_fill.add_argument("--source-url", help="Specific source URL for the copied row.")
    empirical_worksheet_fill.add_argument("--act", help="Act filter used by the source, or all.")
    empirical_worksheet_fill.add_argument("--ascension", help="Ascension filter used by the source, or all.")
    empirical_worksheet_fill.add_argument("--review-status", choices=("proposed", "accepted", "rejected"), help="Review status for the draft row.")
    empirical_worksheet_fill.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")
    empirical_worksheet_fill.add_argument("--write", action="store_true", help="Write the updated worksheet. Defaults to preview only.")

    empirical_promote = subparsers.add_parser(
        "empirical-promote-draft",
        help="Preview or explicitly write active empirical stats from a promotion-ready draft.",
    )
    empirical_promote.add_argument("draft_json", help="Path to an empirical_stat_draft JSON file.")
    empirical_promote.add_argument("--output", required=True, help="Output path under data/empirical for the active empirical JSON file.")
    empirical_promote.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    empirical_promote.add_argument("--min-sample-size", type=int, default=300, help="Minimum sample size before empirical conflict flags are trusted.")
    empirical_promote.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")
    empirical_promote.add_argument("--write", action="store_true", help="Write the promoted empirical JSON file. Defaults to preview only.")
    empirical_promote.add_argument("--replace", action="store_true", help="Allow --write to replace an existing empirical JSON file.")
    empirical_promote.add_argument("--allow-review-flags", action="store_true", help="Allow --write to activate reviewed rows that produce audit review flags.")

    register_run_state_commands(subparsers)

    check_runs = subparsers.add_parser("check-runs", help="Batch-check run-state JSON files or directories for data coverage.")
    check_runs.add_argument("paths", nargs="+", help="Run-state JSON files or directories containing *.json files.")
    check_runs.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")

    register_run_state_normalize_command(subparsers)

    audit_card_priors_parser = subparsers.add_parser(
        "audit-card-priors",
        help="Read-only review of Deckseer card priors against empirical-style card stats.",
    )
    audit_card_priors_parser.add_argument("empirical_stats", help="Path to empirical card stats JSON.")
    audit_card_priors_parser.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    audit_card_priors_parser.add_argument("--min-sample-size", type=int, default=300, help="Minimum sample size before conflict flags are trusted.")
    audit_card_priors_parser.add_argument("--format", choices=("json", "text"), default="json", help="Output format. Defaults to json.")
    audit_card_priors_parser.add_argument("--fail-on-flags", action="store_true", help="Exit with status 1 when the audit reports any flags.")

    register_save_inspection_commands(subparsers)
    register_exporter_inspection_commands(subparsers)

    register_save_recommendation_commands(subparsers)
    register_exporter_recommendation_commands(subparsers)
    return parser


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


if __name__ == "__main__":
    raise SystemExit(main())
