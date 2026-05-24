from __future__ import annotations

import argparse
import json
from pathlib import Path

from deckseer.data_loader import DeckseerData
from deckseer.diagnostics import diagnose_run_state
from deckseer.exporter_toolchain import build_exporter_toolchain_preflight
from deckseer.importers.exporter_state import inspect_exporter_state, load_exporter_state
from deckseer.models import ValidationError
from deckseer.rendering import render_exporter_toolchain_preflight, render_recommendation
from deckseer.scoring.card_reward import recommend_card_reward


def handle_exporter_command(args: argparse.Namespace) -> int | None:
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
    return None


def register_exporter_inspection_commands(subparsers: argparse._SubParsersAction) -> None:
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


def register_exporter_recommendation_commands(subparsers: argparse._SubParsersAction) -> None:
    recommend_export = subparsers.add_parser("recommend-export", help="Rank card rewards from a Deckseer Exporter JSON state file.")
    recommend_export.add_argument("export_json", help="Path to a Deckseer Exporter latest_state.json file.")
    recommend_export.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    recommend_export.add_argument("--format", choices=("json", "text", "markdown"), default="json", help="Output format. Defaults to json.")
    recommend_export.add_argument("--include-diagnosis", action="store_true", help="Include deck profile and prioritized run needs with the recommendation.")
    recommend_export.add_argument("--confirmed", action="store_true", help="Confirm that you reviewed the exported visible state before recommendation.")
