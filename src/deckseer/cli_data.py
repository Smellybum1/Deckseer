from __future__ import annotations

import argparse
from pathlib import Path

from deckseer.catalog import list_cards
from deckseer.data_loader import DeckseerData
from deckseer.data_summary import build_data_health, build_data_review, build_data_summary
from deckseer.rendering import render_card_catalog, render_data_health, render_data_review, render_data_summary


def handle_data_command(args: argparse.Namespace) -> int | None:
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
    return None


def register_data_commands(subparsers: argparse._SubParsersAction) -> None:
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
