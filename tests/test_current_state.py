from __future__ import annotations

from pathlib import Path

import pytest

from deckseer.current_state import build_card_reward_state, load_manual_card_reward_state
from deckseer.importers.sts2_save import load_sts2_run
from deckseer.models import ValidationError


def test_manual_json_loads_through_current_state_adapter() -> None:
    state = load_manual_card_reward_state(Path("tests/fixtures/card_reward_basic.json"))
    run = state.to_run_state()

    assert state.source_type == "manual_json"
    assert run.character == "ironclad"
    assert run.card_reward == ("pommel_strike", "shrug_it_off", "anger")


def test_build_card_reward_state_validates_canonical_shape() -> None:
    state = build_card_reward_state(
        source_type="test_source",
        character="ironclad",
        act=1,
        floor=7,
        hp_current=52,
        hp_max=80,
        deck=[{"id": "strike", "upgraded": False, "count": 4}],
        relics=["burning_blood"],
        potions=[],
        card_reward=["pommel_strike", "shrug_it_off", "anger"],
        caveats=("Confirm visible reward before recommendation.",),
    )

    payload = state.to_recommendation_input()

    assert state.to_run_state().hp.current == 52
    assert payload["deck"] == [{"id": "strike", "upgraded": False, "count": 4}]
    assert "source_type" not in payload
    assert state.caveats == ("Confirm visible reward before recommendation.",)


def test_build_card_reward_state_rejects_invalid_reward() -> None:
    with pytest.raises(ValidationError, match="adds it automatically"):
        build_card_reward_state(
            source_type="test_source",
            character="ironclad",
            act=1,
            floor=7,
            hp_current=52,
            hp_max=80,
            deck=[{"id": "strike", "upgraded": False, "count": 4}],
            relics=[],
            potions=[],
            card_reward=["skip"],
        )


def test_save_importer_uses_current_state_adapter() -> None:
    imported = load_sts2_run(Path("tests/fixtures/sts2_run_history_sanitized.run"))
    state = imported.to_current_state(
        card_reward=("pommel_strike", "shrug_it_off", "anger"),
        hp_current=52,
        hp_max=80,
        act=1,
        floor=7,
    )

    assert state.source_type == "sts2_run_history"
    assert state.to_run_state().character == "ironclad"
    assert "verify HP" in state.caveats[0]
