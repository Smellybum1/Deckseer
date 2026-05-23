from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from deckseer.card_lookup import missing_card_suggestions
from deckseer.models import CardData, DataError, TaggedData, ValidationError


class DeckseerData:
    def __init__(
        self,
        *,
        cards_by_id: dict[str, CardData],
        relics_by_id: dict[str, TaggedData],
        potions_by_id: dict[str, TaggedData],
    ) -> None:
        self.cards_by_id = cards_by_id
        self.relics_by_id = relics_by_id
        self.potions_by_id = potions_by_id

    @classmethod
    def load(cls, data_dir: Path) -> "DeckseerData":
        return cls(
            cards_by_id=_load_cards(data_dir / "cards"),
            relics_by_id=_load_tagged(data_dir / "relics" / "relics.json", "relic"),
            potions_by_id=_load_tagged(data_dir / "potions" / "potions.json", "potion"),
        )

    def cards_for_choices(self, choices: tuple[str, ...]) -> dict[str, CardData]:
        missing = sorted(choice for choice in choices if choice not in self.cards_by_id)
        if missing:
            raise DataError(_missing_card_message(missing, self.cards_by_id))
        return {choice: self.cards_by_id[choice] for choice in choices}


def _read_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise DataError(f"Data file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path} is not valid JSON: {exc}") from exc


def _load_cards(cards_dir: Path) -> dict[str, CardData]:
    if not cards_dir.exists():
        raise DataError(f"Cards data directory not found: {cards_dir}")

    cards: dict[str, CardData] = {}
    for path in sorted(cards_dir.glob("*.json")):
        raw_cards = _read_json(path)
        if not isinstance(raw_cards, list):
            raise ValidationError(f"{path} must contain a list of card records")
        for index, raw_card in enumerate(raw_cards):
            card = CardData.from_dict(raw_card, f"{path.name}[{index}]")
            if card.id in cards:
                raise ValidationError(f"Duplicate card id in data files: {card.id}")
            cards[card.id] = card
    if not cards:
        raise DataError(f"No card data found in {cards_dir}")
    return cards


def _load_tagged(path: Path, label: str) -> dict[str, TaggedData]:
    raw_items = _read_json(path)
    if not isinstance(raw_items, list):
        raise ValidationError(f"{path} must contain a list of {label} records")

    items: dict[str, TaggedData] = {}
    for index, raw_item in enumerate(raw_items):
        item = TaggedData.from_dict(raw_item, f"{label} in {path.name}[{index}]")
        if item.id in items:
            raise ValidationError(f"Duplicate {label} id in data files: {item.id}")
        items[item.id] = item
    return items


def _missing_card_message(missing: list[str], cards_by_id: dict[str, CardData]) -> str:
    message = f"Missing card data for: {', '.join(missing)}"
    suggestions = missing_card_suggestions(missing, cards_by_id)
    if not suggestions:
        return message
    suggestion_parts = [
        f"{card_id} -> {', '.join(card_suggestions)}"
        for card_id, card_suggestions in suggestions.items()
    ]
    return f"{message}. Suggestions: {'; '.join(suggestion_parts)}"
