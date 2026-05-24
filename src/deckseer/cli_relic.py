from __future__ import annotations

import argparse
from pathlib import Path

from deckseer.data_loader import DeckseerData
from deckseer.relic_choice import RelicChoiceState, recommend_relic_choice
from deckseer.rendering import render_recommendation


def handle_relic_command(args: argparse.Namespace) -> int | None:
    if args.command == "recommend-relic":
        state = RelicChoiceState.from_json_file(Path(args.input_json))
        data = DeckseerData.load(Path(args.data_dir))
        result = recommend_relic_choice(state, data)
        print(render_recommendation(result, args.format))
        return 0
    return None


def register_relic_commands(subparsers: argparse._SubParsersAction) -> None:
    recommend_relic = subparsers.add_parser("recommend-relic", help="Rank visible relic reward choices.")
    recommend_relic.add_argument("input_json", help="Path to a structured relic reward JSON file.")
    recommend_relic.add_argument("--data-dir", default="data", help="Path to Deckseer data files. Defaults to ./data.")
    recommend_relic.add_argument("--format", choices=("json", "text", "markdown"), default="json", help="Output format. Defaults to json.")
