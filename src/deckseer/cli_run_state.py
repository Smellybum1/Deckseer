from __future__ import annotations

import argparse
import json
from pathlib import Path

from deckseer.current_state import load_manual_card_reward_state
from deckseer.data_loader import DeckseerData
from deckseer.diagnostics import check_run_data_coverage, diagnose_run_state
from deckseer.normalization import normalize_run_file, write_normalized_payload
from deckseer.rendering import render_recommendation
from deckseer.scoring.card_reward import recommend_card_reward


def handle_run_state_command(args: argparse.Namespace) -> int | None:
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
    if args.command == "normalize-run":
        data = DeckseerData.load(Path(args.data_dir))
        report = normalize_run_file(Path(args.input_json), data)
        if args.output:
            write_normalized_payload(report, Path(args.output))
        print(json.dumps(report, indent=2))
        return 0
    return None


def register_run_state_commands(subparsers: argparse._SubParsersAction) -> None:
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


def register_run_state_normalize_command(subparsers: argparse._SubParsersAction) -> None:
    normalize_run = subparsers.add_parser("normalize-run", help="Normalize exact card display names in a run JSON to Deckseer card IDs.")
    normalize_run.add_argument("input_json", help="Path to a structured run-state JSON file.")
    normalize_run.add_argument("--output", help="Optional path for the normalized run-state payload.")
    normalize_run.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
