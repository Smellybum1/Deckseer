from __future__ import annotations

from pathlib import Path

import pytest

from deckseer.card_lookup import resolve_card_id, suggest_card_ids
from deckseer.data_loader import DeckseerData
from deckseer.models import DataError


def _data() -> DeckseerData:
    return DeckseerData.load(Path("data"))


def test_suggest_card_ids_matches_display_name_and_spacing() -> None:
    data = _data()

    assert suggest_card_ids("Shrug It Off", data.cards_by_id) == ["shrug_it_off"]
    assert suggest_card_ids("pommel strike", data.cards_by_id) == ["pommel_strike"]


def test_resolve_card_id_only_returns_exact_normalized_aliases() -> None:
    data = _data()

    assert resolve_card_id("Shrug It Off", data.cards_by_id) == "shrug_it_off"
    assert resolve_card_id("defragmant", data.cards_by_id) is None


def test_suggest_card_ids_handles_close_typos() -> None:
    suggestions = suggest_card_ids("defragmant", _data().cards_by_id)

    assert suggestions[0] == "defragment"


def test_missing_reward_card_error_includes_suggestions() -> None:
    data = _data()

    with pytest.raises(DataError, match="Shrug It Off -> shrug_it_off"):
        data.cards_for_choices(("Shrug It Off",))
