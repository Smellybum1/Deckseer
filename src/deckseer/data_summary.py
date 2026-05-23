from __future__ import annotations

from collections.abc import Iterable
from collections import Counter, defaultdict
from typing import Any

from deckseer.data_loader import DeckseerData
from deckseer.models import CardData, DataError


BLOCKING_HEALTH_REVIEW_FLAGS = (
    "uncategorized_cards_with_neutral_quality_prior",
    "attack_skill_cards_with_empty_direct_effects",
    "power_cards_with_empty_direct_effects",
)


def build_data_summary(data: DeckseerData, *, character: str | None = None) -> dict[str, Any]:
    cards = _filtered_cards(data, character=character)
    cards_by_character = _cards_by_character(cards)
    return {
        "summary_type": "data_summary",
        "filters": {
            "character": character,
        },
        "totals": {
            "cards": len(cards),
            "characters": len(cards_by_character),
            "relics": len(data.relics_by_id),
            "potions": len(data.potions_by_id),
        },
        "cards_by_character": cards_by_character,
        "metadata_gaps": _metadata_gaps(cards),
        "review_flags": _review_flags(cards),
        "card_types": _sort_counts(Counter(card.type for card in cards)),
        "rarities": _sort_counts(Counter(card.rarity for card in cards)),
        "source_patches": _source_patch_counts(cards),
        "roles": _sort_counts(_count_many(card.roles for card in cards)),
        "tags": _sort_counts(_count_many(card.tags for card in cards)),
        "caveats": [
            "Card metadata is hand-curated and simplified; it is not full combat rules text.",
            "Quality priors and source patches are review aids, not direct scoring overrides.",
        ],
    }


def build_data_health(data: DeckseerData, *, character: str | None = None) -> dict[str, Any]:
    summary = build_data_summary(data, character=character)
    metadata_failures = {
        gap_name: gap for gap_name, gap in summary["metadata_gaps"].items() if gap["count"] > 0
    }
    blocking_review_flags = {
        flag_name: summary["review_flags"][flag_name]
        for flag_name in BLOCKING_HEALTH_REVIEW_FLAGS
        if summary["review_flags"][flag_name]["count"] > 0
    }
    ignored_review_flags = {
        flag_name: flag
        for flag_name, flag in summary["review_flags"].items()
        if flag_name not in BLOCKING_HEALTH_REVIEW_FLAGS and flag["count"] > 0
    }
    failures: dict[str, Any] = {}
    if metadata_failures:
        failures["metadata_gaps"] = metadata_failures
    if blocking_review_flags:
        failures["blocking_review_flags"] = blocking_review_flags
    if character is not None and summary["totals"]["cards"] == 0:
        failures["empty_character_filter"] = {"count": 1, "ids": [character]}

    failure_count = _count_failures(failures)
    return {
        "health_type": "data_health",
        "status": "pass" if failure_count == 0 else "fail",
        "filters": {
            "character": character,
        },
        "failure_count": failure_count,
        "failures": failures,
        "ignored_review_flags": ignored_review_flags,
        "caveats": [
            "Starter, modest, niche, and seed-only neutral quality priors are review context, not health failures.",
            "This gate checks catalog hygiene only; it does not validate gameplay scoring quality.",
        ],
    }


def build_data_review(data: DeckseerData, *, character: str | None = None, flag: str | None = None) -> dict[str, Any]:
    cards = _filtered_cards(data, character=character)
    cards_by_id = {card.id: card for card in cards}
    review_flags = _review_flags(cards)
    if flag is not None and flag not in review_flags:
        known_flags = ", ".join(sorted(review_flags))
        raise DataError(f"Unknown review flag: {flag}. Known flags: {known_flags}")

    selected_flags = {flag: review_flags[flag]} if flag is not None else review_flags
    review_items = {
        flag_name: [_card_review_item(cards_by_id[card_id]) for card_id in flag_data["ids"]]
        for flag_name, flag_data in selected_flags.items()
    }
    return {
        "review_type": "data_review",
        "filters": {
            "character": character,
            "flag": flag,
        },
        "totals": {
            "flags": len(review_items),
            "cards": sum(len(items) for items in review_items.values()),
        },
        "review_flags": review_items,
        "caveats": [
            "Review flags identify data cleanup targets; they do not necessarily indicate scoring bugs.",
            "Card metadata is hand-curated and simplified, so review against current patch data before changing priors.",
        ],
    }


def _filtered_cards(data: DeckseerData, *, character: str | None) -> list[CardData]:
    cards = sorted(data.cards_by_id.values(), key=lambda card: (card.character, card.name, card.id))
    if character is not None:
        character_key = _normalize_filter(character)
        cards = [card for card in cards if _normalize_filter(card.character) == character_key]
    return cards


def _card_review_item(card: CardData) -> dict[str, Any]:
    return {
        "id": card.id,
        "name": card.name,
        "character": card.character,
        "type": card.type,
        "rarity": card.rarity,
        "cost": card.cost,
        "quality_prior": card.quality_prior,
        "source_patch": card.source_patch,
        "roles": sorted(card.roles),
        "tags": sorted(card.tags),
        "source_notes": list(card.source_notes),
    }


def _cards_by_character(cards: list[CardData]) -> dict[str, int]:
    counts = defaultdict(int)
    for card in cards:
        counts[card.character] += 1
    return dict(sorted(counts.items()))


def _source_patch_counts(cards: list[CardData]) -> dict[str, int]:
    counts = Counter(card.source_patch or "unspecified" for card in cards)
    return _sort_counts(counts)


def _metadata_gaps(cards: list[CardData]) -> dict[str, Any]:
    cards_without_roles = [card.id for card in cards if not card.roles]
    cards_without_tags = [card.id for card in cards if not card.tags]
    cards_without_source_patch = [card.id for card in cards if card.character != "neutral" and card.source_patch is None]
    cards_without_source_notes = [card.id for card in cards if card.character != "neutral" and not card.source_notes]
    return {
        "cards_without_roles": {"count": len(cards_without_roles), "ids": cards_without_roles},
        "cards_without_tags": {"count": len(cards_without_tags), "ids": cards_without_tags},
        "cards_without_source_patch": {"count": len(cards_without_source_patch), "ids": cards_without_source_patch},
        "cards_without_source_notes": {"count": len(cards_without_source_notes), "ids": cards_without_source_notes},
    }


def _review_flags(cards: list[CardData]) -> dict[str, Any]:
    neutral_quality_prior_cards = [card for card in cards if card.quality_prior == 0]
    starter_cards_with_neutral_quality_prior = [
        card.id for card in neutral_quality_prior_cards if card.rarity == "starter"
    ]
    modest_cards_with_neutral_quality_prior = [
        card.id for card in neutral_quality_prior_cards if card.rarity != "starter" and _has_modest_neutral_prior_note(card)
    ]
    niche_cards_with_neutral_quality_prior = [
        card.id for card in neutral_quality_prior_cards if card.rarity != "starter" and _has_niche_neutral_prior_note(card)
    ]
    seed_only_cards_with_neutral_quality_prior = [
        card.id
        for card in neutral_quality_prior_cards
        if card.rarity != "starter"
        and not _has_modest_neutral_prior_note(card)
        and not _has_niche_neutral_prior_note(card)
        and _has_seed_only_neutral_prior_note(card)
    ]
    uncategorized_cards_with_neutral_quality_prior = [
        card.id
        for card in neutral_quality_prior_cards
        if card.rarity != "starter"
        and not _has_modest_neutral_prior_note(card)
        and not _has_niche_neutral_prior_note(card)
        and not _has_seed_only_neutral_prior_note(card)
    ]
    cards_with_empty_direct_effects = [card for card in cards if _has_empty_direct_effects(card)]
    attack_skill_cards_with_empty_direct_effects = [
        card.id for card in cards_with_empty_direct_effects if card.type in {"attack", "skill"}
    ]
    power_cards_with_empty_direct_effects = [
        card.id for card in cards_with_empty_direct_effects if card.type == "power"
    ]
    return {
        "starter_cards_with_neutral_quality_prior": {
            "count": len(starter_cards_with_neutral_quality_prior),
            "ids": starter_cards_with_neutral_quality_prior,
        },
        "modest_cards_with_neutral_quality_prior": {
            "count": len(modest_cards_with_neutral_quality_prior),
            "ids": modest_cards_with_neutral_quality_prior,
        },
        "niche_cards_with_neutral_quality_prior": {
            "count": len(niche_cards_with_neutral_quality_prior),
            "ids": niche_cards_with_neutral_quality_prior,
        },
        "seed_only_cards_with_neutral_quality_prior": {
            "count": len(seed_only_cards_with_neutral_quality_prior),
            "ids": seed_only_cards_with_neutral_quality_prior,
        },
        "uncategorized_cards_with_neutral_quality_prior": {
            "count": len(uncategorized_cards_with_neutral_quality_prior),
            "ids": uncategorized_cards_with_neutral_quality_prior,
        },
        "attack_skill_cards_with_empty_direct_effects": {
            "count": len(attack_skill_cards_with_empty_direct_effects),
            "ids": attack_skill_cards_with_empty_direct_effects,
        },
        "power_cards_with_empty_direct_effects": {
            "count": len(power_cards_with_empty_direct_effects),
            "ids": power_cards_with_empty_direct_effects,
        },
    }


def _has_modest_neutral_prior_note(card: CardData) -> bool:
    notes = _source_notes_text(card)
    return "c tier" in notes or "mediocre" in notes or "preferably skip" in notes


def _has_niche_neutral_prior_note(card: CardData) -> bool:
    return "niche" in _source_notes_text(card)


def _has_seed_only_neutral_prior_note(card: CardData) -> bool:
    notes = _source_notes_text(card)
    return "seed" in notes or "not present in provided" in notes


def _source_notes_text(card: CardData) -> str:
    return " ".join(card.source_notes).lower()


def _has_empty_direct_effects(card: CardData) -> bool:
    return (
        card.effects.damage == 0
        and card.effects.block == 0
        and card.effects.draw == 0
        and card.effects.energy == 0
        and not any(value != 0 for value in card.effects.extra.values())
    )


def _count_many(values: Iterable[Iterable[str]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for value_set in values:
        counter.update(value_set)
    return counter


def _sort_counts(counts: Counter[str]) -> dict[str, int]:
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _count_failures(failures: dict[str, Any]) -> int:
    total = 0
    for failure in failures.values():
        if isinstance(failure, dict) and "count" in failure:
            total += failure["count"]
            continue
        total += sum(item["count"] for item in failure.values())
    return total


def _normalize_filter(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")
