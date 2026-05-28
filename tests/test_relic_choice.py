from __future__ import annotations

import json
from pathlib import Path

import pytest

from deckseer.cli import main
from deckseer.data_loader import DeckseerData
from deckseer.models import DataError, ValidationError
from deckseer.relic_choice import RelicChoiceState, recommend_relic_choice


FIXTURE_DIR = Path("tests/fixtures/relic_choice")


def _data() -> DeckseerData:
    return DeckseerData.load(Path("data"))


def _state(name: str) -> RelicChoiceState:
    return RelicChoiceState.from_json_file(FIXTURE_DIR / name)


def _raw_state(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_relic_choice_prefers_akabeko_for_elite_frontload() -> None:
    result = recommend_relic_choice(_state("elite_frontload.json"), _data())

    assert result.recommendation_type == "relic_choice"
    assert result.ranked_choices[0].choice == "akabeko"
    assert any("frontload" in reason for reason in result.ranked_choices[0].reasoning)
    assert result.ranked_choices[0].score > result.ranked_choices[1].score


def test_relic_choice_prefers_burning_blood_when_low_hp_sustain_need() -> None:
    result = recommend_relic_choice(_state("low_hp_sustain.json"), _data())

    assert result.ranked_choices[0].choice == "burning_blood"
    assert any("low_hp" in reason for reason in result.ranked_choices[0].reasoning)
    assert any("tag-based" in risk for risk in result.ranked_choices[0].risks)


def test_relic_choice_prefers_kunai_for_attack_dense_long_fight() -> None:
    result = recommend_relic_choice(_state("long_fight_scaling.json"), _data())

    assert result.ranked_choices[0].choice == "kunai"
    assert any("scaling" in reason for reason in result.ranked_choices[0].reasoning)
    assert any("attack_dense" in reason for reason in result.ranked_choices[0].reasoning)


def test_relic_choice_prefers_ring_for_early_consistency_pressure() -> None:
    result = recommend_relic_choice(_state("early_consistency_ring.json"), _data())

    assert result.ranked_choices[0].choice == "ring_of_the_snake"
    assert any("consistency" in reason for reason in result.ranked_choices[0].reasoning)
    assert any("elite_prep" in reason for reason in result.ranked_choices[0].reasoning)


def test_relic_choice_can_prefer_lead_paperweight_for_healthy_early_quality() -> None:
    result = recommend_relic_choice(_state("colorless_deck_quality.json"), _data())

    assert result.ranked_choices[0].choice == "lead_paperweight"
    assert any("consistency" in reason for reason in result.ranked_choices[0].reasoning)


def test_relic_choice_can_prefer_letter_opener_for_skill_dense_frontload() -> None:
    result = recommend_relic_choice(_state("skill_dense_letter_opener.json"), _data())

    assert result.ranked_choices[0].choice == "letter_opener"
    assert any("frontload" in reason for reason in result.ranked_choices[0].reasoning)
    assert any("skill_dense" in reason for reason in result.ranked_choices[0].reasoning)


def test_relic_choice_rejects_unknown_reward_relic() -> None:
    raw = _raw_state("elite_frontload.json")
    raw["relic_reward"] = ["akabeko", "unknown_relic"]
    state = RelicChoiceState.from_dict(raw)

    with pytest.raises(DataError, match="Missing relic data for reward choices: unknown_relic"):
        recommend_relic_choice(state, _data())


def test_relic_choice_keeps_unknown_owned_relic_as_risk() -> None:
    raw = _raw_state("elite_frontload.json")
    raw["relics"] = ["unknown_owned_relic"]
    state = RelicChoiceState.from_dict(raw)

    result = recommend_relic_choice(state, _data())

    assert result.ranked_choices[0].confidence == "low"
    assert any("unknown_owned_relic" in risk for risk in result.ranked_choices[0].risks)


def test_relic_choice_requires_relic_reward_screen_type() -> None:
    raw = _raw_state("elite_frontload.json")
    raw["screen_type"] = "card_reward"

    with pytest.raises(ValidationError, match="screen_type relic_reward"):
        RelicChoiceState.from_dict(raw)


def test_relic_choice_result_dict_shape_is_stable() -> None:
    result = recommend_relic_choice(_state("elite_frontload.json"), _data()).to_dict()

    assert result["recommendation_type"] == "relic_choice"
    assert result["ranked_choices"][0]["choice"] == "akabeko"
    assert set(result["ranked_choices"][0]) == {
        "choice",
        "name",
        "rank",
        "score",
        "confidence",
        "reasoning",
        "risks",
    }


def test_recommend_relic_cli_text_output(capsys) -> None:
    status = main(["recommend-relic", str(FIXTURE_DIR / "elite_frontload.json"), "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Relic Choice" in captured.out
    assert "1. Akabeko (akabeko)" in captured.out
    assert "Why:" in captured.out


def test_recommend_relic_cli_json_output(capsys) -> None:
    status = main(["recommend-relic", str(FIXTURE_DIR / "low_hp_sustain.json")])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["recommendation_type"] == "relic_choice"
    assert payload["ranked_choices"][0]["choice"] == "burning_blood"


def test_recommend_relic_cli_markdown_output(capsys) -> None:
    status = main(["recommend-relic", str(FIXTURE_DIR / "long_fight_scaling.json"), "--format", "markdown"])

    captured = capsys.readouterr()

    assert status == 0
    assert "## Relic Choice Recommendation" in captured.out
    assert "Kunai (`kunai`)" in captured.out


def test_recommend_relic_cli_unknown_reward_relic_returns_validation_status(tmp_path, capsys) -> None:
    raw = _raw_state("elite_frontload.json")
    raw["relic_reward"] = ["unknown_relic"]
    path = tmp_path / "unknown_reward_relic.json"
    path.write_text(json.dumps(raw), encoding="utf-8")

    status = main(["recommend-relic", str(path)])

    captured = capsys.readouterr()

    assert status == 2
    assert "Missing relic data for reward choices: unknown_relic" in captured.err
