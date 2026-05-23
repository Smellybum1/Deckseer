from __future__ import annotations

import json
from pathlib import Path

from deckseer.cli import main
from deckseer.data_loader import DeckseerData
from deckseer.diagnostics import check_run_data_coverage, check_run_files_data_coverage, diagnose_run_state
from deckseer.models import RunState


def _data() -> DeckseerData:
    return DeckseerData.load(Path("data"))


def _run(overrides: dict | None = None) -> RunState:
    raw = {
        "character": "ironclad",
        "act": 1,
        "floor": 4,
        "hp": {"current": 70, "max": 80},
        "deck": [
            {"id": "strike", "upgraded": False, "count": 2},
            {"id": "defend", "upgraded": False, "count": 4},
            {"id": "bash", "upgraded": False, "count": 1},
        ],
        "relics": [],
        "potions": [],
        "card_reward": ["pommel_strike", "shrug_it_off", "inflame"],
    }
    if overrides:
        raw.update(overrides)
    return RunState.from_dict(raw)


def test_diagnose_run_state_reports_profile_and_needs() -> None:
    diagnosis = diagnose_run_state(_run(), _data())

    assert diagnosis["diagnosis_type"] == "card_reward_run_needs"
    assert diagnosis["character"] == "ironclad"
    assert diagnosis["deck_profile"]["size"] == 7
    assert diagnosis["deck_profile"]["phase"] == "early_act_1"
    assert diagnosis["deck_profile"]["counts"]["damage"] == 3
    assert diagnosis["prioritized_needs"]
    assert {need["name"] for need in diagnosis["prioritized_needs"]} >= {"frontload"}


def test_diagnose_run_state_orders_needs_deterministically() -> None:
    run = _run(
        {
            "hp": {"current": 24, "max": 80},
            "deck": [
                {"id": "strike", "upgraded": False, "count": 5},
                {"id": "bash", "upgraded": False, "count": 1},
            ],
        }
    )

    first = diagnose_run_state(run, _data())
    second = diagnose_run_state(run, _data())

    assert first == second
    assert first["prioritized_needs"][0]["name"] == "defense"


def test_diagnose_run_state_reports_unknown_deck_metadata() -> None:
    run = _run(
        {
            "deck": [
                {"id": "strike", "upgraded": False, "count": 2},
                {"id": "mystery_card", "upgraded": False, "count": 3},
            ],
        }
    )

    diagnosis = diagnose_run_state(run, _data())

    assert diagnosis["deck_profile"]["size"] == 5
    assert diagnosis["deck_profile"]["known_cards"] == 2
    assert diagnosis["deck_profile"]["unknown_cards"] == 3
    assert diagnosis["data_coverage"] == {
        "known_deck_cards": 2,
        "unknown_deck_cards": 3,
        "coverage_ratio": 0.4,
        "unknown_card_ids": ["mystery_card"],
    }
    assert "mystery_card" in diagnosis["caveats"][0]


def test_check_run_data_coverage_reports_ready_clean_run() -> None:
    coverage = check_run_data_coverage(_run(), _data())

    assert coverage["check_type"] == "run_data_coverage"
    assert coverage["scoring_ready"] is True
    assert coverage["deck"]["missing_card_ids"] == []
    assert coverage["card_reward"]["missing_card_ids"] == []
    assert coverage["caveats"] == []


def test_check_run_data_coverage_splits_deck_and_reward_gaps() -> None:
    run = _run(
        {
            "deck": [
                {"id": "strike", "upgraded": False, "count": 2},
                {"id": "mystery_deck_card", "upgraded": False, "count": 3},
            ],
            "card_reward": ["pommel_strike", "mystery_reward_card"],
        }
    )

    coverage = check_run_data_coverage(run, _data())

    assert coverage["scoring_ready"] is False
    assert coverage["deck"]["unknown_cards"] == 3
    assert coverage["deck"]["coverage_ratio"] == 0.4
    assert coverage["deck"]["missing_card_ids"] == ["mystery_deck_card"]
    assert coverage["card_reward"]["missing_card_ids"] == ["mystery_reward_card"]
    assert "Cannot score" in coverage["caveats"][0]


def test_check_run_data_coverage_suggests_known_ids_for_name_mismatches() -> None:
    run = _run(
        {
            "deck": [
                {"id": "Strike", "upgraded": False, "count": 2},
                {"id": "defend", "upgraded": False, "count": 4},
            ],
            "card_reward": ["Pommel Strike", "Shrug It Off"],
        }
    )

    coverage = check_run_data_coverage(run, _data())

    assert coverage["scoring_ready"] is False
    assert coverage["deck"]["suggestions"] == {"Strike": ["strike"]}
    assert coverage["card_reward"]["suggestions"] == {
        "Pommel Strike": ["pommel_strike"],
        "Shrug It Off": ["shrug_it_off"],
    }


def test_diagnose_run_cli_smoke(capsys) -> None:
    status = main(["diagnose-run", "examples/card_reward_basic.json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["diagnosis_type"] == "card_reward_run_needs"
    assert payload["deck_profile"]["size"] == 7
    assert payload["prioritized_needs"]


def test_check_run_data_cli_smoke(capsys) -> None:
    status = main(["check-run-data", "examples/card_reward_basic.json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["check_type"] == "run_data_coverage"
    assert payload["scoring_ready"] is True


def test_check_run_files_data_coverage_summarizes_batch(tmp_path: Path) -> None:
    ready_path = tmp_path / "ready.json"
    blocked_path = tmp_path / "blocked.json"
    ready_path.write_text(json.dumps(_run_payload()), encoding="utf-8")
    blocked = _run_payload(
        {
            "deck": [
                {"id": "strike", "upgraded": False, "count": 2},
                {"id": "mystery_deck_card", "upgraded": False, "count": 1},
            ],
            "card_reward": ["pommel_strike", "missing_reward"],
        }
    )
    blocked_path.write_text(json.dumps(blocked), encoding="utf-8")

    report = check_run_files_data_coverage([ready_path, blocked_path], _data())

    assert report["summary"] == {
        "total_files": 2,
        "valid_files": 2,
        "invalid_files": 0,
        "scoring_ready_files": 1,
        "blocked_files": 1,
        "files_with_deck_metadata_gaps": 1,
    }
    assert report["runs"][1]["card_reward"]["missing_card_ids"] == ["missing_reward"]


def test_check_runs_cli_accepts_directory(capsys) -> None:
    status = main(["check-runs", "examples"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["check_type"] == "run_file_data_coverage_batch"
    assert payload["summary"]["total_files"] >= 5
    assert payload["summary"]["blocked_files"] == 0


def _run_payload(overrides: dict | None = None) -> dict:
    payload = {
        "character": "ironclad",
        "act": 1,
        "floor": 4,
        "hp": {"current": 70, "max": 80},
        "deck": [
            {"id": "strike", "upgraded": False, "count": 2},
            {"id": "defend", "upgraded": False, "count": 4},
            {"id": "bash", "upgraded": False, "count": 1},
        ],
        "relics": [],
        "potions": [],
        "card_reward": ["pommel_strike", "shrug_it_off", "inflame"],
    }
    if overrides:
        payload.update(overrides)
    return payload
