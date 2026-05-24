from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from deckseer.accuracy import build_accuracy_report
from deckseer.catalog import list_cards
from deckseer.current_state import load_manual_card_reward_state
from deckseer.data_loader import DeckseerData
from deckseer.data_summary import build_data_health, build_data_review, build_data_summary
from deckseer.diagnostics import check_run_data_coverage, check_run_files_data_coverage, diagnose_run_state
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
from deckseer.exporter_toolchain import build_exporter_toolchain_preflight
from deckseer.models import DeckseerError, ValidationError
from deckseer.audit.card_priors import audit_card_priors, load_empirical_card_stats
from deckseer.importers.exporter_state import inspect_exporter_state, load_exporter_state
from deckseer.importers.sts2_save import load_sts2_run
from deckseer.normalization import normalize_run_file, write_normalized_payload
from deckseer.qa import (
    build_project_qa,
    build_recommendation_smoke_baseline,
    discover_empirical_stats,
    discover_example_runs,
    write_recommendation_smoke_baseline,
)
from deckseer.rendering import (
    render_accuracy_report,
    render_card_catalog,
    render_card_prior_audit,
    render_data_health,
    render_data_review,
    render_data_summary,
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
    render_exporter_toolchain_preflight,
    render_project_qa,
    render_recommendation,
)
from deckseer.scoring.card_reward import recommend_card_reward


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "list-cards":
            data = DeckseerData.load(Path(args.data_dir))
            catalog = list_cards(data, character=args.character, query=args.query)
            print(render_card_catalog(catalog, args.format))
            return 0
        if args.command == "data-summary":
            data = DeckseerData.load(Path(args.data_dir))
            print(
                render_data_summary(
                    build_data_summary(data, character=args.character),
                    args.format,
                    show_gap_ids=args.show_gap_ids,
                    max_gap_ids=args.max_gap_ids,
                )
            )
            return 0
        if args.command == "data-review":
            data = DeckseerData.load(Path(args.data_dir))
            print(render_data_review(build_data_review(data, character=args.character, flag=args.flag), args.format))
            return 0
        if args.command == "data-health":
            data = DeckseerData.load(Path(args.data_dir))
            health = build_data_health(data, character=args.character)
            print(render_data_health(health, args.format))
            return 0 if health["status"] == "pass" else 1
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
        if args.command == "recommend-card":
            run = load_manual_card_reward_state(Path(args.input_json)).to_run_state()
            data = DeckseerData.load(Path(args.data_dir))
            result = recommend_card_reward(run, data)
            diagnosis = diagnose_run_state(run, data) if args.include_diagnosis else None
            print(render_recommendation(result, args.format, diagnosis=diagnosis))
            return 0
        if args.command == "diagnose-run":
            run = load_manual_card_reward_state(Path(args.input_json)).to_run_state()
            data = DeckseerData.load(Path(args.data_dir))
            print(json.dumps(diagnose_run_state(run, data), indent=2))
            return 0
        if args.command == "check-run-data":
            run = load_manual_card_reward_state(Path(args.input_json)).to_run_state()
            data = DeckseerData.load(Path(args.data_dir))
            print(json.dumps(check_run_data_coverage(run, data), indent=2))
            return 0
        if args.command == "check-runs":
            data = DeckseerData.load(Path(args.data_dir))
            paths = _expand_run_paths([Path(path) for path in args.paths])
            print(json.dumps(check_run_files_data_coverage(paths, data), indent=2))
            return 0
        if args.command == "normalize-run":
            data = DeckseerData.load(Path(args.data_dir))
            report = normalize_run_file(Path(args.input_json), data)
            if args.output:
                write_normalized_payload(report, Path(args.output))
            print(json.dumps(report, indent=2))
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
        if args.command == "inspect-save":
            imported = load_sts2_run(Path(args.save_json), player_index=args.player_index)
            print(json.dumps(imported.to_summary_dict(), indent=2))
            return 0
        if args.command == "inspect-export":
            exported = inspect_exporter_state(Path(args.export_json))
            print(json.dumps(exported.to_summary_dict(), indent=2))
            return 0
        if args.command == "exporter-toolchain-preflight":
            report = build_exporter_toolchain_preflight(
                sts2_install_path=Path(args.sts2_install),
                steam_manifest_path=Path(args.steam_manifest),
                export_dir=Path(args.export_dir) if args.export_dir else None,
            )
            print(render_exporter_toolchain_preflight(report, args.format))
            return 0
        if args.command == "import-run":
            imported = load_sts2_run(Path(args.save_json), player_index=args.player_index)
            payload = imported.to_recommendation_input(
                card_reward=tuple(args.card_reward),
                hp_current=args.hp_current,
                hp_max=args.hp_max,
                act=args.act,
                floor=args.floor,
            )
            output = json.dumps(payload, indent=2)
            if args.output:
                Path(args.output).write_text(output + "\n", encoding="utf-8")
            else:
                print(output)
            return 0
        if args.command == "recommend-save":
            imported = load_sts2_run(Path(args.save_json), player_index=args.player_index)
            run = imported.to_current_state(
                card_reward=tuple(args.card_reward),
                hp_current=args.hp_current,
                hp_max=args.hp_max,
                act=args.act,
                floor=args.floor,
            ).to_run_state()
            data = DeckseerData.load(Path(args.data_dir))
            result = recommend_card_reward(run, data)
            diagnosis = diagnose_run_state(run, data) if args.include_diagnosis else None
            print(render_recommendation(result, args.format, diagnosis=diagnosis))
            return 0
        if args.command == "recommend-export":
            exported = load_exporter_state(Path(args.export_json))
            if exported.metadata.get("requires_user_confirmation") is True and not args.confirmed:
                raise ValidationError(
                    "exporter state requires user confirmation; run inspect-export, verify the visible state, "
                    "then rerun recommend-export with --confirmed"
                )
            run = exported.current_state.to_run_state()
            data = DeckseerData.load(Path(args.data_dir))
            result = recommend_card_reward(run, data)
            diagnosis = diagnose_run_state(run, data) if args.include_diagnosis else None
            print(render_recommendation(result, args.format, diagnosis=diagnosis))
            return 0
        parser.error("missing command")
    except DeckseerError as exc:
        print(f"deckseer: {exc}", file=sys.stderr)
        return 2

    return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="deckseer", description="Local decision-support coach for Slay the Spire 2.")
    subparsers = parser.add_subparsers(dest="command")

    list_cards_parser = subparsers.add_parser("list-cards", help="Search Deckseer's local card catalog and show exact card IDs.")
    list_cards_parser.add_argument("--character", help="Optional character filter, such as ironclad, silent, defect, necrobinder, or regent.")
    list_cards_parser.add_argument("--query", help="Optional search across card id, name, roles, and tags.")
    list_cards_parser.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    list_cards_parser.add_argument("--format", choices=("json", "text"), default="json", help="Output format. Defaults to json.")

    data_summary = subparsers.add_parser("data-summary", help="Summarize local card/relic/potion data coverage and metadata gaps.")
    data_summary.add_argument("--character", help="Optional character filter, such as ironclad, silent, defect, necrobinder, or regent.")
    data_summary.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    data_summary.add_argument("--format", choices=("json", "text"), default="json", help="Output format. Defaults to json.")
    data_summary.add_argument("--show-gap-ids", action="store_true", help="In text output, show example card IDs for metadata gaps.")
    data_summary.add_argument("--max-gap-ids", type=int, default=12, help="Maximum IDs to show per metadata gap in text output. Defaults to 12.")

    data_review = subparsers.add_parser("data-review", help="List cards behind data review flags with source metadata.")
    data_review.add_argument("--character", help="Optional character filter, such as ironclad, silent, defect, necrobinder, or regent.")
    data_review.add_argument("--flag", help="Optional review flag filter, such as attack_skill_cards_with_empty_direct_effects.")
    data_review.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    data_review.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")

    data_health = subparsers.add_parser("data-health", help="Pass/fail gate for catalog metadata and blocking review flags.")
    data_health.add_argument("--character", help="Optional character filter, such as ironclad, silent, defect, necrobinder, or regent.")
    data_health.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    data_health.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")

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

    recommend_card = subparsers.add_parser("recommend-card", help="Rank the current card reward choices, including Skip.")
    recommend_card.add_argument("input_json", help="Path to a structured run-state JSON file.")
    recommend_card.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    recommend_card.add_argument("--format", choices=("json", "text", "markdown"), default="json", help="Output format. Defaults to json.")
    recommend_card.add_argument("--include-diagnosis", action="store_true", help="Include deck profile and prioritized run needs with the recommendation.")

    diagnose_run = subparsers.add_parser("diagnose-run", help="Show deck profile and prioritized run needs for a run-state JSON file.")
    diagnose_run.add_argument("input_json", help="Path to a structured run-state JSON file.")
    diagnose_run.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")

    check_run_data = subparsers.add_parser("check-run-data", help="Report missing deck or reward card metadata for a run-state JSON file.")
    check_run_data.add_argument("input_json", help="Path to a structured run-state JSON file.")
    check_run_data.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")

    check_runs = subparsers.add_parser("check-runs", help="Batch-check run-state JSON files or directories for data coverage.")
    check_runs.add_argument("paths", nargs="+", help="Run-state JSON files or directories containing *.json files.")
    check_runs.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")

    normalize_run = subparsers.add_parser("normalize-run", help="Normalize exact card display names in a run JSON to Deckseer card IDs.")
    normalize_run.add_argument("input_json", help="Path to a structured run-state JSON file.")
    normalize_run.add_argument("--output", help="Optional path for the normalized run-state payload.")
    normalize_run.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")

    audit_card_priors_parser = subparsers.add_parser(
        "audit-card-priors",
        help="Read-only review of Deckseer card priors against empirical-style card stats.",
    )
    audit_card_priors_parser.add_argument("empirical_stats", help="Path to empirical card stats JSON.")
    audit_card_priors_parser.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    audit_card_priors_parser.add_argument("--min-sample-size", type=int, default=300, help="Minimum sample size before conflict flags are trusted.")
    audit_card_priors_parser.add_argument("--format", choices=("json", "text"), default="json", help="Output format. Defaults to json.")
    audit_card_priors_parser.add_argument("--fail-on-flags", action="store_true", help="Exit with status 1 when the audit reports any flags.")

    inspect_save = subparsers.add_parser("inspect-save", help="Summarize a plain JSON Slay the Spire 2 run-history save.")
    inspect_save.add_argument("save_json", help="Path to a Slay the Spire 2 .run JSON file.")
    inspect_save.add_argument("--player-index", type=int, default=0, help="Player index for multi-player run files. Defaults to 0.")

    inspect_export = subparsers.add_parser("inspect-export", help="Summarize a Deckseer Exporter JSON state file.")
    inspect_export.add_argument("export_json", help="Path to a Deckseer Exporter latest_state.json file.")

    exporter_preflight = subparsers.add_parser(
        "exporter-toolchain-preflight",
        help="Read-only readiness report for the future static Deckseer Exporter mod spike.",
    )
    exporter_preflight.add_argument("--format", choices=("json", "text"), default="text", help="Output format. Defaults to text.")
    exporter_preflight.add_argument(
        "--sts2-install",
        default=r"D:\Games\Steam\steamapps\common\Slay the Spire 2",
        help="Slay the Spire 2 install path. Defaults to the documented local Steam install path.",
    )
    exporter_preflight.add_argument(
        "--steam-manifest",
        default=r"D:\Games\Steam\steamapps\appmanifest_2868840.acf",
        help="Steam app manifest path. Defaults to the documented local STS2 manifest path.",
    )
    exporter_preflight.add_argument(
        "--export-dir",
        help="Expected Deckseer exporter output directory. Defaults to %%LOCALAPPDATA%%\\Deckseer\\exports.",
    )

    import_run = subparsers.add_parser("import-run", help="Create a Deckseer recommendation JSON draft from a run-history save.")
    import_run.add_argument("save_json", help="Path to a Slay the Spire 2 .run JSON file.")
    import_run.add_argument("--player-index", type=int, default=0, help="Player index for multi-player run files. Defaults to 0.")
    import_run.add_argument("--card-reward", nargs="+", required=True, help="Current visible card reward IDs in Deckseer format.")
    import_run.add_argument("--hp-current", type=int, required=True, help="Current HP to place in the Deckseer input.")
    import_run.add_argument("--hp-max", type=int, required=True, help="Maximum HP to place in the Deckseer input.")
    import_run.add_argument("--act", type=int, required=True, help="Current act to place in the Deckseer input.")
    import_run.add_argument("--floor", type=int, required=True, help="Current floor to place in the Deckseer input.")
    import_run.add_argument("--output", help="Optional output path. Defaults to printing JSON.")

    recommend_save = subparsers.add_parser("recommend-save", help="Rank card rewards directly from a run-history save plus manual live state.")
    recommend_save.add_argument("save_json", help="Path to a Slay the Spire 2 .run JSON file.")
    recommend_save.add_argument("--player-index", type=int, default=0, help="Player index for multi-player run files. Defaults to 0.")
    recommend_save.add_argument("--card-reward", nargs="+", required=True, help="Current visible card reward IDs in Deckseer format.")
    recommend_save.add_argument("--hp-current", type=int, required=True, help="Current HP to place in the Deckseer input.")
    recommend_save.add_argument("--hp-max", type=int, required=True, help="Maximum HP to place in the Deckseer input.")
    recommend_save.add_argument("--act", type=int, required=True, help="Current act to place in the Deckseer input.")
    recommend_save.add_argument("--floor", type=int, required=True, help="Current floor to place in the Deckseer input.")
    recommend_save.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    recommend_save.add_argument("--format", choices=("json", "text", "markdown"), default="json", help="Output format. Defaults to json.")
    recommend_save.add_argument("--include-diagnosis", action="store_true", help="Include deck profile and prioritized run needs with the recommendation.")

    recommend_export = subparsers.add_parser("recommend-export", help="Rank card rewards from a Deckseer Exporter JSON state file.")
    recommend_export.add_argument("export_json", help="Path to a Deckseer Exporter latest_state.json file.")
    recommend_export.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    recommend_export.add_argument("--format", choices=("json", "text", "markdown"), default="json", help="Output format. Defaults to json.")
    recommend_export.add_argument("--include-diagnosis", action="store_true", help="Include deck profile and prioritized run needs with the recommendation.")
    recommend_export.add_argument("--confirmed", action="store_true", help="Confirm that you reviewed the exported visible state before recommendation.")
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
