from __future__ import annotations

import argparse
import json
from pathlib import Path

from deckseer.data_loader import DeckseerData
from deckseer.diagnostics import diagnose_run_state
from deckseer.importers.sts2_save import load_sts2_run
from deckseer.rendering import render_recommendation
from deckseer.scoring.card_reward import recommend_card_reward


def handle_save_command(args: argparse.Namespace) -> int | None:
    if args.command == "inspect-save":
        imported = load_sts2_run(Path(args.save_json), player_index=args.player_index)
        print(json.dumps(imported.to_summary_dict(), indent=2))
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
    return None


def register_save_inspection_commands(subparsers: argparse._SubParsersAction) -> None:
    inspect_save = subparsers.add_parser("inspect-save", help="Summarize a plain JSON Slay the Spire 2 run-history save.")
    inspect_save.add_argument("save_json", help="Path to a Slay the Spire 2 .run JSON file.")
    inspect_save.add_argument("--player-index", type=int, default=0, help="Player index for multi-player run files. Defaults to 0.")


def register_save_recommendation_commands(subparsers: argparse._SubParsersAction) -> None:
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
