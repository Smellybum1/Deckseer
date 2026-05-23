from __future__ import annotations

import json
from pathlib import Path

import pytest

from deckseer.cli import main
from deckseer.importers.exporter_state import load_exporter_state
from deckseer.models import ValidationError


FIXTURE = Path("tests/fixtures/exporter_card_reward_state.json")


def test_exporter_state_loads_through_current_state_adapter() -> None:
    exported = load_exporter_state(FIXTURE)
    run = exported.current_state.to_run_state()

    assert exported.source_type == "deckseer_exporter_mod"
    assert exported.screen_type == "card_reward"
    assert run.character == "ironclad"
    assert run.card_reward == ("pommel_strike", "shrug_it_off", "anger")


def test_exporter_state_drops_metadata_from_recommendation_input() -> None:
    exported = load_exporter_state(FIXTURE)
    payload = exported.current_state.to_recommendation_input()

    assert "screen_type" not in payload
    assert "export_metadata" not in payload
    assert payload["game"] == "slay_the_spire_2"


def test_exporter_state_preserves_metadata_caveats_outside_scorer() -> None:
    exported = load_exporter_state(FIXTURE)

    assert "User should confirm visible card reward before using this state." in exported.current_state.caveats
    assert "Exporter state requires user confirmation before recommendation." in exported.current_state.caveats


def test_exporter_state_rejects_unsupported_screen_type(tmp_path: Path) -> None:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    raw["screen_type"] = "shop"
    path = tmp_path / "shop_export.json"
    path.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(ValidationError, match="unsupported exporter screen_type: shop"):
        load_exporter_state(path)


def test_inspect_export_cli_smoke(capsys) -> None:
    status = main(["inspect-export", str(FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["source_type"] == "deckseer_exporter_mod"
    assert payload["screen_type"] == "card_reward"
    assert payload["valid"] is True
    assert payload["card_reward"] == ["pommel_strike", "shrug_it_off", "anger"]


def test_recommend_export_cli_smoke_json(capsys) -> None:
    status = main(["recommend-export", str(FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["recommendation_type"] == "card_reward"
    assert {choice["choice"] for choice in payload["ranked_choices"]} >= {"pommel_strike", "shrug_it_off", "anger", "skip"}


def test_recommend_export_cli_smoke_text(capsys) -> None:
    status = main(["recommend-export", str(FIXTURE), "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Card Reward" in captured.out
    assert "Skip" in captured.out
