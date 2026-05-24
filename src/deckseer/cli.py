from __future__ import annotations

import argparse
import sys

from deckseer.cli_data import handle_data_command, register_data_commands
from deckseer.cli_empirical_overview import handle_empirical_overview_command, register_empirical_overview_commands
from deckseer.cli_empirical_workflow import handle_empirical_workflow_command, register_empirical_workflow_commands
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
from deckseer.cli_qa import handle_qa_command, register_check_runs_command, register_qa_commands
from deckseer.cli_review import handle_review_command, register_accuracy_report_command, register_card_prior_audit_command
from deckseer.cli_save import handle_save_command, register_save_inspection_commands, register_save_recommendation_commands
from deckseer.models import DeckseerError


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        data_status = handle_data_command(args)
        if data_status is not None:
            return data_status
        qa_status = handle_qa_command(args)
        if qa_status is not None:
            return qa_status
        empirical_overview_status = handle_empirical_overview_command(args)
        if empirical_overview_status is not None:
            return empirical_overview_status
        empirical_workflow_status = handle_empirical_workflow_command(args)
        if empirical_workflow_status is not None:
            return empirical_workflow_status
        review_status = handle_review_command(args)
        if review_status is not None:
            return review_status
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
    register_qa_commands(subparsers)

    register_accuracy_report_command(subparsers)

    register_empirical_overview_commands(subparsers)
    register_empirical_workflow_commands(subparsers)

    register_run_state_commands(subparsers)
    register_check_runs_command(subparsers)

    register_run_state_normalize_command(subparsers)

    register_card_prior_audit_command(subparsers)

    register_save_inspection_commands(subparsers)
    register_exporter_inspection_commands(subparsers)

    register_save_recommendation_commands(subparsers)
    register_exporter_recommendation_commands(subparsers)
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
