from __future__ import annotations

import json
from pathlib import Path

from deckseer.cli import main
from deckseer.data_loader import DeckseerData
from deckseer.models import RunState
from deckseer.scoring.card_reward import recommend_card_reward


def _data() -> DeckseerData:
    return DeckseerData.load(Path("data"))


def _run(overrides: dict | None = None) -> RunState:
    raw = {
        "character": "ironclad",
        "act": 1,
        "floor": 3,
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


def _silent_run(overrides: dict | None = None) -> RunState:
    raw = {
        "character": "silent",
        "act": 1,
        "floor": 4,
        "hp": {"current": 62, "max": 70},
        "deck": [
            {"id": "strike", "upgraded": False, "count": 5},
            {"id": "defend", "upgraded": False, "count": 5},
            {"id": "neutralize", "upgraded": False, "count": 1},
            {"id": "survivor", "upgraded": False, "count": 1},
        ],
        "relics": [],
        "potions": [],
        "card_reward": ["dagger_throw", "backflip", "footwork"],
    }
    if overrides:
        raw.update(overrides)
    return RunState.from_dict(raw)


def _defect_run(overrides: dict | None = None) -> RunState:
    raw = {
        "character": "defect",
        "act": 1,
        "floor": 4,
        "hp": {"current": 68, "max": 75},
        "deck": [
            {"id": "strike", "upgraded": False, "count": 4},
            {"id": "defend", "upgraded": False, "count": 4},
            {"id": "zap", "upgraded": False, "count": 1},
            {"id": "dualcast", "upgraded": False, "count": 1},
        ],
        "relics": [],
        "potions": [],
        "card_reward": ["cold_snap", "glacier", "defragment"],
    }
    if overrides:
        raw.update(overrides)
    return RunState.from_dict(raw)


def _necrobinder_run(overrides: dict | None = None) -> RunState:
    raw = {
        "character": "necrobinder",
        "act": 1,
        "floor": 4,
        "hp": {"current": 66, "max": 75},
        "deck": [
            {"id": "strike", "upgraded": False, "count": 4},
            {"id": "defend", "upgraded": False, "count": 4},
            {"id": "sic_em", "upgraded": False, "count": 1},
            {"id": "calcify", "upgraded": False, "count": 1},
        ],
        "relics": [],
        "potions": [],
        "card_reward": ["unleash", "bodyguard", "forbidden_grimoire"],
    }
    if overrides:
        raw.update(overrides)
    return RunState.from_dict(raw)


def _regent_run(overrides: dict | None = None) -> RunState:
    raw = {
        "character": "regent",
        "act": 1,
        "floor": 4,
        "hp": {"current": 66, "max": 75},
        "deck": [
            {"id": "strike", "upgraded": False, "count": 4},
            {"id": "defend", "upgraded": False, "count": 4},
            {"id": "shining_strike", "upgraded": False, "count": 1},
            {"id": "parry", "upgraded": False, "count": 1},
        ],
        "relics": [],
        "potions": [],
        "card_reward": ["astral_pulse", "bulwark", "spectrum_shift"],
    }
    if overrides:
        raw.update(overrides)
    return RunState.from_dict(raw)


def test_early_deck_lacking_damage_prefers_efficient_attack() -> None:
    result = recommend_card_reward(_run(), _data())

    assert result.ranked_choices[0].choice == "pommel_strike"
    assert result.ranked_choices[0].score > result.ranked_choices[-1].score


def test_defensive_light_deck_prefers_block_card() -> None:
    run = _run(
        {
            "hp": {"current": 34, "max": 80},
            "deck": [
                {"id": "strike", "upgraded": False, "count": 5},
                {"id": "bash", "upgraded": False, "count": 1},
            ],
            "card_reward": ["pommel_strike", "shrug_it_off", "anger"],
        }
    )

    result = recommend_card_reward(run, _data())

    assert result.ranked_choices[0].choice == "shrug_it_off"
    assert any("defense" in reason for reason in result.ranked_choices[0].reasoning)


def test_act_two_deck_without_scaling_favors_scaling_plan() -> None:
    run = _run(
        {
            "act": 2,
            "floor": 22,
            "deck": [
                {"id": "strike", "upgraded": False, "count": 5},
                {"id": "defend", "upgraded": False, "count": 4},
                {"id": "bash", "upgraded": False, "count": 1},
            ],
            "card_reward": ["pommel_strike", "inflame", "clothesline"],
        }
    )

    result = recommend_card_reward(run, _data())

    assert result.ranked_choices[0].choice == "inflame"
    assert any("scaling" in reason for reason in result.ranked_choices[0].reasoning)


def test_underdocks_context_pushes_block_for_elite_prep() -> None:
    run = _run(
        {
            "run_context": {
                "act_region": "underdocks",
                "upcoming_elites": ["skulking_colony", "terror_eel"],
                "path_pressure": "elite_soon",
            },
            "card_reward": ["pommel_strike", "shrug_it_off", "anger"],
        }
    )

    result = recommend_card_reward(run, _data())

    assert result.ranked_choices[0].choice == "shrug_it_off"
    assert any("Underdocks" in reason for reason in result.ranked_choices[0].reasoning)


def test_overgrowth_context_pushes_damage_for_elite_prep() -> None:
    run = _run(
        {
            "run_context": {
                "act_region": "overgrowth",
                "upcoming_elites": ["berdonis", "bygone_effigy"],
                "path_pressure": "elite_soon",
            },
            "card_reward": ["pommel_strike", "shrug_it_off", "inflame"],
        }
    )

    result = recommend_card_reward(run, _data())

    assert result.ranked_choices[0].choice == "pommel_strike"
    assert any("Overgrowth" in reason for reason in result.ranked_choices[0].reasoning)


def test_bloated_deck_can_rank_skip_first() -> None:
    run = _run(
        {
            "deck": [
                {"id": "strike", "upgraded": False, "count": 13},
                {"id": "defend", "upgraded": False, "count": 12},
                {"id": "bash", "upgraded": False, "count": 2},
            ],
            "card_reward": ["anger", "clothesline", "inflame"],
        }
    )

    result = recommend_card_reward(run, _data())

    assert result.ranked_choices[0].choice == "skip"


def test_output_ranking_is_stable_and_deterministic() -> None:
    run = _run()
    first = recommend_card_reward(run, _data()).to_dict()
    second = recommend_card_reward(run, _data()).to_dict()

    assert first == second


def test_unknown_deck_card_metadata_lowers_confidence_without_blocking_scoring() -> None:
    run = _run(
        {
            "deck": [
                {"id": "strike", "upgraded": False, "count": 2},
                {"id": "defend", "upgraded": False, "count": 4},
                {"id": "unknown_deck_card", "upgraded": False, "count": 1},
            ],
        }
    )

    result = recommend_card_reward(run, _data())

    assert result.ranked_choices
    assert {choice.confidence for choice in result.ranked_choices} == {"low"}


def test_explanations_prioritize_run_need_over_generic_quality() -> None:
    result = recommend_card_reward(_run(), _data())
    top = result.ranked_choices[0]

    assert top.choice == "pommel_strike"
    assert any("frontload" in reason for reason in top.reasoning)
    assert not any("baseline quality" in reason for reason in top.reasoning)
    assert not any("card prior" in reason.lower() for reason in top.reasoning)


def test_strong_prior_helps_close_fit_decisions() -> None:
    run = _run(
        {
            "run_context": {
                "act_region": "overgrowth",
                "upcoming_elites": ["berdonis"],
                "path_pressure": "elite_soon",
            },
            "card_reward": ["pommel_strike", "anger"],
        }
    )

    result = recommend_card_reward(run, _data())

    assert result.ranked_choices[0].choice == "pommel_strike"
    assert result.ranked_choices[0].score > result.ranked_choices[1].score


def test_premium_draw_energy_card_scores_as_consistency_solution() -> None:
    run = _run(
        {
            "act": 2,
            "floor": 21,
            "deck": [
                {"id": "strike", "upgraded": False, "count": 5},
                {"id": "defend", "upgraded": False, "count": 4},
                {"id": "bash", "upgraded": False, "count": 1},
                {"id": "clothesline", "upgraded": False, "count": 2},
                {"id": "bludgeon", "upgraded": False, "count": 1},
            ],
            "card_reward": ["offering", "anger", "body_slam"],
        }
    )

    result = recommend_card_reward(run, _data())

    assert result.ranked_choices[0].choice == "offering"
    assert any("consistency" in reason for reason in result.ranked_choices[0].reasoning)


def test_low_prior_niche_card_loses_without_matching_plan() -> None:
    run = _run(
        {
            "act": 2,
            "floor": 21,
            "deck": [
                {"id": "strike", "upgraded": False, "count": 5},
                {"id": "defend", "upgraded": False, "count": 4},
                {"id": "bash", "upgraded": False, "count": 1},
            ],
            "card_reward": ["body_slam", "pommel_strike", "impervious"],
        }
    )

    result = recommend_card_reward(run, _data())
    body_slam = next(choice for choice in result.ranked_choices if choice.choice == "body_slam")

    assert result.ranked_choices[0].choice == "pommel_strike"
    assert body_slam.rank > 1
    assert any("Niche payoff" in risk for risk in body_slam.risks)


def test_premium_bad_fit_does_not_override_urgent_context() -> None:
    run = _run(
        {
            "run_context": {
                "act_region": "underdocks",
                "upcoming_elites": ["skulking_colony", "terror_eel"],
                "path_pressure": "elite_soon",
            },
            "card_reward": ["pommel_strike", "shrug_it_off"],
        }
    )

    result = recommend_card_reward(run, _data())
    pommel = next(choice for choice in result.ranked_choices if choice.choice == "pommel_strike")

    assert result.ranked_choices[0].choice == "shrug_it_off"
    assert any("Strong card prior" in risk for risk in pommel.risks)


def test_cli_smoke_json_output(capsys) -> None:
    status = main(["recommend-card", "examples/card_reward_basic.json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["recommendation_type"] == "card_reward"
    assert payload["ranked_choices"]
    assert {choice["choice"] for choice in payload["ranked_choices"]} >= {"skip", "pommel_strike"}


def test_cli_json_output_can_include_diagnosis(capsys) -> None:
    status = main(["recommend-card", "examples/card_reward_basic.json", "--include-diagnosis"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["diagnosis"]["diagnosis_type"] == "card_reward_run_needs"
    assert payload["recommendation"]["recommendation_type"] == "card_reward"
    assert payload["diagnosis"]["prioritized_needs"]


def test_cli_markdown_output_can_include_diagnosis(capsys) -> None:
    status = main(["recommend-card", "examples/card_reward_basic.json", "--format", "markdown", "--include-diagnosis"])

    captured = capsys.readouterr()

    assert status == 0
    assert "## Run Diagnosis" in captured.out
    assert "## Card Reward Recommendation" in captured.out
    assert "| Rank | Choice | Score | Confidence |" in captured.out
    assert "Pommel Strike (`pommel_strike`)" in captured.out


def test_silent_basic_reward_can_be_scored() -> None:
    result = recommend_card_reward(_silent_run(), _data())

    assert result.recommendation_type == "card_reward"
    assert {choice.choice for choice in result.ranked_choices} >= {"dagger_throw", "backflip", "footwork", "skip"}


def test_silent_early_low_damage_prefers_frontload() -> None:
    run = _silent_run(
        {
            "deck": [
                {"id": "strike", "upgraded": False, "count": 2},
                {"id": "defend", "upgraded": False, "count": 5},
                {"id": "neutralize", "upgraded": False, "count": 1},
                {"id": "survivor", "upgraded": False, "count": 1},
            ],
            "card_reward": ["dagger_throw", "footwork", "prepared"],
        }
    )

    result = recommend_card_reward(run, _data())

    assert result.ranked_choices[0].choice == "dagger_throw"
    assert any("frontload" in reason for reason in result.ranked_choices[0].reasoning)


def test_silent_low_hp_low_block_prefers_defense() -> None:
    run = _silent_run(
        {
            "hp": {"current": 24, "max": 70},
            "deck": [
                {"id": "strike", "upgraded": False, "count": 5},
                {"id": "neutralize", "upgraded": False, "count": 1},
            ],
            "card_reward": ["dagger_throw", "backflip", "slice"],
        }
    )

    result = recommend_card_reward(run, _data())

    assert result.ranked_choices[0].choice == "backflip"
    assert any("defense" in reason for reason in result.ranked_choices[0].reasoning)


def test_silent_example_cli_smoke(capsys) -> None:
    status = main(["recommend-card", "examples/silent_card_reward_basic.json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["recommendation_type"] == "card_reward"
    assert {choice["choice"] for choice in payload["ranked_choices"]} >= {"dagger_throw", "backflip", "footwork", "skip"}


def test_defect_basic_reward_can_be_scored() -> None:
    result = recommend_card_reward(_defect_run(), _data())

    assert result.recommendation_type == "card_reward"
    assert {choice.choice for choice in result.ranked_choices} >= {"cold_snap", "glacier", "defragment", "skip"}


def test_defect_early_low_damage_prefers_frontload_orb_card() -> None:
    run = _defect_run(
        {
            "deck": [
                {"id": "strike", "upgraded": False, "count": 2},
                {"id": "defend", "upgraded": False, "count": 4},
                {"id": "zap", "upgraded": False, "count": 1},
                {"id": "dualcast", "upgraded": False, "count": 1},
            ],
            "card_reward": ["cold_snap", "defragment", "skim"],
        }
    )

    result = recommend_card_reward(run, _data())

    assert result.ranked_choices[0].choice == "cold_snap"
    assert any("frontload" in reason for reason in result.ranked_choices[0].reasoning)


def test_defect_low_hp_low_block_prefers_glacier() -> None:
    run = _defect_run(
        {
            "hp": {"current": 25, "max": 75},
            "deck": [
                {"id": "strike", "upgraded": False, "count": 4},
                {"id": "zap", "upgraded": False, "count": 1},
                {"id": "dualcast", "upgraded": False, "count": 1},
            ],
            "card_reward": ["compile_driver", "glacier", "ball_lightning"],
        }
    )

    result = recommend_card_reward(run, _data())

    assert result.ranked_choices[0].choice == "glacier"
    assert any("defense" in reason for reason in result.ranked_choices[0].reasoning)


def test_defect_act_two_no_scaling_prefers_defragment() -> None:
    run = _defect_run(
        {
            "act": 2,
            "floor": 22,
            "deck": [
                {"id": "strike", "upgraded": False, "count": 4},
                {"id": "defend", "upgraded": False, "count": 4},
                {"id": "zap", "upgraded": False, "count": 1},
                {"id": "dualcast", "upgraded": False, "count": 1},
                {"id": "cold_snap", "upgraded": False, "count": 1},
            ],
            "card_reward": ["defragment", "cold_snap", "compile_driver"],
        }
    )

    result = recommend_card_reward(run, _data())

    assert result.ranked_choices[0].choice == "defragment"
    assert any("scaling" in reason for reason in result.ranked_choices[0].reasoning)


def test_defect_example_cli_smoke(capsys) -> None:
    status = main(["recommend-card", "examples/defect_card_reward_basic.json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["recommendation_type"] == "card_reward"
    assert {choice["choice"] for choice in payload["ranked_choices"]} >= {"cold_snap", "glacier", "defragment", "skip"}


def test_necrobinder_basic_reward_can_be_scored() -> None:
    result = recommend_card_reward(_necrobinder_run(), _data())

    assert result.recommendation_type == "card_reward"
    assert {choice.choice for choice in result.ranked_choices} >= {"unleash", "bodyguard", "forbidden_grimoire", "skip"}


def test_necrobinder_early_low_damage_prefers_unleash() -> None:
    run = _necrobinder_run(
        {
            "deck": [
                {"id": "strike", "upgraded": False, "count": 2},
                {"id": "defend", "upgraded": False, "count": 4},
                {"id": "calcify", "upgraded": False, "count": 1},
            ],
            "card_reward": ["unleash", "forbidden_grimoire", "friendship"],
        }
    )

    result = recommend_card_reward(run, _data())

    assert result.ranked_choices[0].choice == "unleash"
    assert any("frontload" in reason for reason in result.ranked_choices[0].reasoning)


def test_necrobinder_low_hp_low_block_prefers_bodyguard() -> None:
    run = _necrobinder_run(
        {
            "hp": {"current": 26, "max": 75},
            "deck": [
                {"id": "strike", "upgraded": False, "count": 4},
                {"id": "sic_em", "upgraded": False, "count": 1},
            ],
            "card_reward": ["unleash", "bodyguard", "lethality"],
        }
    )

    result = recommend_card_reward(run, _data())

    assert result.ranked_choices[0].choice == "bodyguard"
    assert any("defense" in reason for reason in result.ranked_choices[0].reasoning)


def test_necrobinder_act_two_no_scaling_prefers_deathbringer() -> None:
    run = _necrobinder_run(
        {
            "act": 2,
            "floor": 22,
            "deck": [
                {"id": "strike", "upgraded": False, "count": 4},
                {"id": "defend", "upgraded": False, "count": 4},
                {"id": "sic_em", "upgraded": False, "count": 1},
                {"id": "calcify", "upgraded": False, "count": 1},
                {"id": "unleash", "upgraded": False, "count": 1},
            ],
            "card_reward": ["deathbringer", "unleash", "forbidden_grimoire"],
        }
    )

    result = recommend_card_reward(run, _data())

    assert result.ranked_choices[0].choice == "deathbringer"
    assert any("scaling" in reason for reason in result.ranked_choices[0].reasoning)


def test_necrobinder_example_cli_smoke(capsys) -> None:
    status = main(["recommend-card", "examples/necrobinder_card_reward_basic.json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["recommendation_type"] == "card_reward"
    assert {choice["choice"] for choice in payload["ranked_choices"]} >= {"unleash", "bodyguard", "forbidden_grimoire", "skip"}


def test_regent_basic_reward_can_be_scored() -> None:
    result = recommend_card_reward(_regent_run(), _data())

    assert result.recommendation_type == "card_reward"
    assert {choice.choice for choice in result.ranked_choices} >= {"astral_pulse", "bulwark", "spectrum_shift", "skip"}


def test_regent_early_low_damage_prefers_overstatted_frontload() -> None:
    run = _regent_run(
        {
            "deck": [
                {"id": "strike", "upgraded": False, "count": 2},
                {"id": "defend", "upgraded": False, "count": 4},
                {"id": "parry", "upgraded": False, "count": 1},
            ],
            "card_reward": ["astral_pulse", "spectrum_shift", "glow"],
        }
    )

    result = recommend_card_reward(run, _data())

    assert result.ranked_choices[0].choice == "astral_pulse"
    assert any("frontload" in reason for reason in result.ranked_choices[0].reasoning)


def test_regent_low_hp_low_block_prefers_bulwark() -> None:
    run = _regent_run(
        {
            "hp": {"current": 24, "max": 75},
            "deck": [
                {"id": "strike", "upgraded": False, "count": 4},
                {"id": "shining_strike", "upgraded": False, "count": 1},
            ],
            "card_reward": ["astral_pulse", "bulwark", "tyranny"],
        }
    )

    result = recommend_card_reward(run, _data())

    assert result.ranked_choices[0].choice == "bulwark"
    assert any("defense" in reason for reason in result.ranked_choices[0].reasoning)


def test_regent_act_two_no_scaling_prefers_spectrum_shift() -> None:
    run = _regent_run(
        {
            "act": 2,
            "floor": 22,
            "deck": [
                {"id": "strike", "upgraded": False, "count": 4},
                {"id": "defend", "upgraded": False, "count": 4},
                {"id": "shining_strike", "upgraded": False, "count": 1},
                {"id": "parry", "upgraded": False, "count": 1},
                {"id": "astral_pulse", "upgraded": False, "count": 1},
            ],
            "card_reward": ["spectrum_shift", "astral_pulse", "particle_wall"],
        }
    )

    result = recommend_card_reward(run, _data())

    assert result.ranked_choices[0].choice == "spectrum_shift"
    assert any("scaling" in reason for reason in result.ranked_choices[0].reasoning)


def test_regent_example_cli_smoke(capsys) -> None:
    status = main(["recommend-card", "examples/regent_card_reward_basic.json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["recommendation_type"] == "card_reward"
    assert {choice["choice"] for choice in payload["ranked_choices"]} >= {"astral_pulse", "bulwark", "spectrum_shift", "skip"}
