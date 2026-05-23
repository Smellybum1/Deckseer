from __future__ import annotations

import json
from pathlib import Path

from deckseer.catalog import list_cards
from deckseer.cli import main
from deckseer.data_loader import DeckseerData


def _data() -> DeckseerData:
    return DeckseerData.load(Path("data"))


def test_list_cards_filters_by_character() -> None:
    catalog = list_cards(_data(), character="silent")

    assert catalog["catalog_type"] == "cards"
    assert catalog["count"] >= 25
    assert {card["character"] for card in catalog["cards"]} == {"silent"}
    assert "backflip" in {card["id"] for card in catalog["cards"]}


def test_list_cards_searches_names_ids_roles_and_tags() -> None:
    catalog = list_cards(_data(), query="scaling")

    ids = {card["id"] for card in catalog["cards"]}

    assert "inflame" in ids
    assert "defragment" in ids
    assert "spectrum_shift" in ids


def test_list_cards_cli_json_smoke(capsys) -> None:
    status = main(["list-cards", "--character", "defect", "--query", "frost"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["catalog_type"] == "cards"
    assert payload["filters"] == {"character": "defect", "query": "frost"}
    assert {card["id"] for card in payload["cards"]} >= {"cold_snap", "glacier"}


def test_list_cards_cli_text_smoke(capsys) -> None:
    status = main(["list-cards", "--query", "backflip", "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Cards (1)" in captured.out
    assert "backflip - Backflip" in captured.out
