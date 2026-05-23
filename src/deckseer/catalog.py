from __future__ import annotations

from typing import Any

from deckseer.data_loader import DeckseerData
from deckseer.models import CardData


def list_cards(
    data: DeckseerData,
    *,
    character: str | None = None,
    query: str | None = None,
) -> dict[str, Any]:
    cards = sorted(data.cards_by_id.values(), key=lambda card: (card.character, card.name, card.id))
    if character is not None:
        character_key = _normalize_search(character)
        cards = [card for card in cards if _normalize_search(card.character) == character_key]
    if query is not None:
        query_key = _normalize_search(query)
        cards = [
            card
            for card in cards
            if query_key in _normalize_search(card.id)
            or query_key in _normalize_search(card.name)
            or any(query_key in _normalize_search(role) for role in card.roles)
            or any(query_key in _normalize_search(tag) for tag in card.tags)
        ]
    return {
        "catalog_type": "cards",
        "filters": {
            "character": character,
            "query": query,
        },
        "count": len(cards),
        "cards": [_card_to_dict(card) for card in cards],
    }


def _card_to_dict(card: CardData) -> dict[str, Any]:
    return {
        "id": card.id,
        "name": card.name,
        "character": card.character,
        "type": card.type,
        "rarity": card.rarity,
        "cost": card.cost,
        "roles": sorted(card.roles),
        "tags": sorted(card.tags),
        "quality_prior": card.quality_prior,
    }


def _normalize_search(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")
