from __future__ import annotations

from pathlib import Path

import pytest

from deckseer.data_loader import DeckseerData
from deckseer.models import RunState
from deckseer.scoring.card_reward import recommend_card_reward


SCENARIOS = Path("tests/fixtures/scenarios")


@pytest.mark.parametrize(
    ("fixture_name", "expected_top_choice", "expected_reason_keyword"),
    [
        ("early_act1_low_frontload.json", "pommel_strike", "frontload"),
        ("underdocks_defense_pressure.json", "shrug_it_off", "Underdocks"),
        ("overgrowth_damage_pressure.json", "pommel_strike", "Overgrowth"),
        ("act2_no_scaling.json", "inflame", "scaling"),
        ("bloated_deck_skip_pressure.json", "skip", "bloat"),
        ("necrobinder_forbidden_grimoire_frontload_guard.json", "unleash", "frontload"),
        ("defect_cold_snap_scaling_guard.json", "defragment", "scaling"),
        ("regent_astral_pulse_scaling_guard.json", "spectrum_shift", "scaling"),
        ("regent_bulwark_frontload_guard.json", "astral_pulse", "frontload"),
    ],
)
def test_accuracy_scenario_top_choice_and_reasoning(
    fixture_name: str,
    expected_top_choice: str,
    expected_reason_keyword: str,
) -> None:
    data = DeckseerData.load(Path("data"))
    run = RunState.from_json_file(SCENARIOS / fixture_name)

    result = recommend_card_reward(run, data)
    top_choice = result.ranked_choices[0]

    assert top_choice.choice == expected_top_choice
    assert any(expected_reason_keyword.lower() in reason.lower() for reason in top_choice.reasoning)
