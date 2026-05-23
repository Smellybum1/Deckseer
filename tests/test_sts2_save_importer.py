from __future__ import annotations

import json
from pathlib import Path

from deckseer.cli import main
from deckseer.importers.sts2_save import load_sts2_run, normalize_game_id


FIXTURE = Path("tests/fixtures/sts2_run_history_sanitized.run")


def test_normalize_game_id_removes_prefixes_and_class_suffixes() -> None:
    assert normalize_game_id("CARD.STRIKE_IRONCLAD") == "strike"
    assert normalize_game_id("RELIC.BURNING_BLOOD") == "burning_blood"
    assert normalize_game_id("CHARACTER.SILENT") == "silent"


def test_load_sts2_run_history_summary() -> None:
    imported = load_sts2_run(FIXTURE)

    assert imported.summary.character == "ironclad"
    assert imported.summary.ascension == 8
    assert imported.summary.deck_size == 5
    assert imported.summary.unique_cards == 4
    assert imported.summary.relic_count == 1
    assert imported.relics == ("burning_blood",)
    assert imported.potions == ("fire_potion",)


def test_imported_run_builds_recommendation_input() -> None:
    imported = load_sts2_run(FIXTURE)
    payload = imported.to_recommendation_input(
        card_reward=("pommel_strike", "shrug_it_off", "anger"),
        hp_current=52,
        hp_max=80,
        act=1,
        floor=7,
    )

    assert payload["character"] == "ironclad"
    assert payload["hp"] == {"current": 52, "max": 80}
    assert payload["card_reward"] == ["pommel_strike", "shrug_it_off", "anger"]
    assert {"id": "bash", "upgraded": True, "count": 1} in payload["deck"]


def test_inspect_save_cli_smoke(capsys) -> None:
    status = main(["inspect-save", str(FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["source_type"] == "sts2_run_history"
    assert payload["character"] == "ironclad"
    assert payload["deck_size"] == 5


def test_import_run_cli_smoke(capsys) -> None:
    status = main(
        [
            "import-run",
            str(FIXTURE),
            "--card-reward",
            "pommel_strike",
            "shrug_it_off",
            "anger",
            "--hp-current",
            "52",
            "--hp-max",
            "80",
            "--act",
            "1",
            "--floor",
            "7",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["character"] == "ironclad"
    assert payload["card_reward"] == ["pommel_strike", "shrug_it_off", "anger"]


def test_recommend_save_cli_smoke_json(capsys) -> None:
    status = main(
        [
            "recommend-save",
            str(FIXTURE),
            "--card-reward",
            "pommel_strike",
            "shrug_it_off",
            "anger",
            "--hp-current",
            "52",
            "--hp-max",
            "80",
            "--act",
            "1",
            "--floor",
            "7",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["recommendation_type"] == "card_reward"
    assert {choice["choice"] for choice in payload["ranked_choices"]} >= {"pommel_strike", "shrug_it_off", "anger", "skip"}


def test_recommend_save_cli_smoke_text(capsys) -> None:
    status = main(
        [
            "recommend-save",
            str(FIXTURE),
            "--card-reward",
            "pommel_strike",
            "shrug_it_off",
            "anger",
            "--hp-current",
            "52",
            "--hp-max",
            "80",
            "--act",
            "1",
            "--floor",
            "7",
            "--format",
            "text",
        ]
    )

    captured = capsys.readouterr()

    assert status == 0
    assert "Card Reward" in captured.out
    assert "Skip" in captured.out


def test_recommend_save_can_include_text_diagnosis(capsys) -> None:
    status = main(
        [
            "recommend-save",
            str(FIXTURE),
            "--card-reward",
            "pommel_strike",
            "shrug_it_off",
            "anger",
            "--hp-current",
            "52",
            "--hp-max",
            "80",
            "--act",
            "1",
            "--floor",
            "7",
            "--format",
            "text",
            "--include-diagnosis",
        ]
    )

    captured = capsys.readouterr()

    assert status == 0
    assert "Run Diagnosis" in captured.out
    assert "Top needs:" in captured.out
    assert "Card Reward" in captured.out


def test_recommend_save_cli_smoke_markdown(capsys) -> None:
    status = main(
        [
            "recommend-save",
            str(FIXTURE),
            "--card-reward",
            "pommel_strike",
            "shrug_it_off",
            "anger",
            "--hp-current",
            "52",
            "--hp-max",
            "80",
            "--act",
            "1",
            "--floor",
            "7",
            "--format",
            "markdown",
        ]
    )

    captured = capsys.readouterr()

    assert status == 0
    assert "## Card Reward Recommendation" in captured.out
    assert "| Rank | Choice | Score | Confidence |" in captured.out
    assert "Skip (`skip`)" in captured.out
