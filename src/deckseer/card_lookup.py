from __future__ import annotations

from difflib import get_close_matches

from deckseer.models import CardData


def resolve_card_id(raw: str, cards_by_id: dict[str, CardData]) -> str | None:
    aliases = _card_aliases(cards_by_id)
    return aliases.get(normalize_card_query(raw))


def suggest_card_ids(raw: str, cards_by_id: dict[str, CardData], *, limit: int = 3) -> list[str]:
    aliases = _card_aliases(cards_by_id)
    query = normalize_card_query(raw)
    if query in aliases:
        return [aliases[query]]

    matches = get_close_matches(query, aliases.keys(), n=limit * 3, cutoff=0.72)
    suggestions: list[str] = []
    for match in matches:
        card_id = aliases[match]
        if card_id not in suggestions:
            suggestions.append(card_id)
        if len(suggestions) >= limit:
            break
    return suggestions


def missing_card_suggestions(missing: list[str], cards_by_id: dict[str, CardData]) -> dict[str, list[str]]:
    return {
        card_id: suggestions
        for card_id in missing
        if (suggestions := suggest_card_ids(card_id, cards_by_id))
    }


def normalize_card_query(value: str) -> str:
    normalized = value.strip().lower()
    chars = [character if character.isalnum() else "_" for character in normalized]
    return "_".join("".join(chars).split("_"))


def _card_aliases(cards_by_id: dict[str, CardData]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for card in cards_by_id.values():
        aliases.setdefault(normalize_card_query(card.id), card.id)
        aliases.setdefault(normalize_card_query(card.name), card.id)
    return aliases
