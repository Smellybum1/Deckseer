from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any


class DeckseerError(Exception):
    """Base exception for expected Deckseer errors."""


class ValidationError(DeckseerError):
    """Raised when user input or data files fail validation."""


class DataError(DeckseerError):
    """Raised when local game data cannot support a request."""


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{label} must be an object")
    return value


def _require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValidationError(f"{label} must be a list")
    return value


def _require_str(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{label} must be a non-empty string")
    return value


def _optional_str(value: Any, label: str) -> str | None:
    if value is None:
        return None
    return _require_str(value, label)


def _require_int(value: Any, label: str, *, minimum: int | None = None) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValidationError(f"{label} must be an integer")
    if minimum is not None and value < minimum:
        raise ValidationError(f"{label} must be at least {minimum}")
    return value


def _require_number(value: Any, label: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValidationError(f"{label} must be a number")
    return float(value)


def _optional_number(value: Any, label: str, *, default: float = 0.0) -> float:
    if value is None:
        return default
    return _require_number(value, label)


def _optional_number_mapping(value: Any, label: str) -> dict[str, float]:
    if value is None:
        return {}
    data = _require_mapping(value, label)
    return {
        _require_str(key, f"{label} key"): _require_number(item, f"{label}.{key}")
        for key, item in data.items()
    }


def _optional_bool(value: Any, label: str) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ValidationError(f"{label} must be a boolean")
    return value


def _optional_str_tuple(value: Any, label: str) -> tuple[str, ...]:
    return tuple(_require_str(item, f"{label}[{index}]") for index, item in enumerate(_require_list(value, label)))


@dataclass(frozen=True)
class Hp:
    current: int
    max: int

    @classmethod
    def from_dict(cls, raw: Any) -> "Hp":
        data = _require_mapping(raw, "hp")
        current = _require_int(data.get("current"), "hp.current", minimum=0)
        maximum = _require_int(data.get("max"), "hp.max", minimum=1)
        if current > maximum:
            raise ValidationError("hp.current cannot exceed hp.max")
        return cls(current=current, max=maximum)


@dataclass(frozen=True)
class DeckCard:
    id: str
    upgraded: bool = False
    count: int = 1

    @classmethod
    def from_dict(cls, raw: Any, index: int) -> "DeckCard":
        data = _require_mapping(raw, f"deck[{index}]")
        upgraded = data.get("upgraded", False)
        if not isinstance(upgraded, bool):
            raise ValidationError(f"deck[{index}].upgraded must be a boolean")
        return cls(
            id=_require_str(data.get("id"), f"deck[{index}].id"),
            upgraded=upgraded,
            count=_require_int(data.get("count", 1), f"deck[{index}].count", minimum=1),
        )


@dataclass(frozen=True)
class RunContext:
    recent_damage: int | None = None
    next_node_type: str = "unknown"
    boss: str | None = None
    act_region: str | None = None
    upcoming_elites: tuple[str, ...] = ()
    fought_elites: tuple[str, ...] = ()
    next_nodes: tuple[str, ...] = ()
    fire_before_elite: bool | None = None
    shop_before_elite: bool | None = None
    path_pressure: str = "unknown"
    notes: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, raw: Any) -> "RunContext":
        if raw is None:
            return cls()
        data = _require_mapping(raw, "run_context")
        recent_damage_raw = data.get("recent_damage")
        recent_damage = None
        if recent_damage_raw is not None:
            recent_damage = _require_int(recent_damage_raw, "run_context.recent_damage", minimum=0)
        upcoming_elites = _optional_str_tuple(data.get("upcoming_elites", []), "run_context.upcoming_elites")
        fought_elites = _optional_str_tuple(data.get("fought_elites", []), "run_context.fought_elites")
        next_nodes = _optional_str_tuple(data.get("next_nodes", []), "run_context.next_nodes")
        notes_raw = _require_list(data.get("notes", []), "run_context.notes")
        notes = tuple(_require_str(note, f"run_context.notes[{index}]") for index, note in enumerate(notes_raw))
        return cls(
            recent_damage=recent_damage,
            next_node_type=_require_str(data.get("next_node_type", "unknown"), "run_context.next_node_type"),
            boss=_optional_str(data.get("boss"), "run_context.boss"),
            act_region=_optional_str(data.get("act_region"), "run_context.act_region"),
            upcoming_elites=upcoming_elites,
            fought_elites=fought_elites,
            next_nodes=next_nodes,
            fire_before_elite=_optional_bool(data.get("fire_before_elite"), "run_context.fire_before_elite"),
            shop_before_elite=_optional_bool(data.get("shop_before_elite"), "run_context.shop_before_elite"),
            path_pressure=_require_str(data.get("path_pressure", "unknown"), "run_context.path_pressure"),
            notes=notes,
        )


@dataclass(frozen=True)
class RunState:
    character: str
    act: int
    floor: int
    hp: Hp
    deck: tuple[DeckCard, ...]
    relics: tuple[str, ...]
    potions: tuple[str, ...]
    card_reward: tuple[str, ...]
    game: str = "slay_the_spire_2"
    ascension: int = 0
    gold: int = 0
    run_context: RunContext = field(default_factory=RunContext)

    @classmethod
    def from_dict(cls, raw: Any) -> "RunState":
        data = _require_mapping(raw, "run state")
        deck = tuple(DeckCard.from_dict(item, index) for index, item in enumerate(_require_list(data.get("deck"), "deck")))
        relics = tuple(_require_str(item, f"relics[{index}]") for index, item in enumerate(_require_list(data.get("relics"), "relics")))
        potions = tuple(_require_str(item, f"potions[{index}]") for index, item in enumerate(_require_list(data.get("potions"), "potions")))
        card_reward = tuple(
            _require_str(item, f"card_reward[{index}]")
            for index, item in enumerate(_require_list(data.get("card_reward"), "card_reward"))
        )
        if not card_reward:
            raise ValidationError("card_reward must include at least one offered card")
        if any(choice.lower() == "skip" for choice in card_reward):
            raise ValidationError("card_reward should not include Skip; Deckseer adds it automatically")
        return cls(
            game=_require_str(data.get("game", "slay_the_spire_2"), "game"),
            character=_require_str(data.get("character"), "character"),
            act=_require_int(data.get("act"), "act", minimum=1),
            floor=_require_int(data.get("floor"), "floor", minimum=0),
            ascension=_require_int(data.get("ascension", 0), "ascension", minimum=0),
            gold=_require_int(data.get("gold", 0), "gold", minimum=0),
            hp=Hp.from_dict(data.get("hp")),
            deck=deck,
            relics=relics,
            potions=potions,
            card_reward=card_reward,
            run_context=RunContext.from_dict(data.get("run_context")),
        )

    @classmethod
    def from_json_file(cls, path: Path) -> "RunState":
        try:
            with path.open("r", encoding="utf-8") as handle:
                return cls.from_dict(json.load(handle))
        except json.JSONDecodeError as exc:
            raise ValidationError(f"{path} is not valid JSON: {exc}") from exc


@dataclass(frozen=True)
class CardEffects:
    damage: float = 0
    block: float = 0
    draw: float = 0
    energy: float = 0
    extra: dict[str, float] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: Any) -> "CardEffects":
        data = _require_mapping(raw or {}, "card.effects")
        return cls(
            damage=_require_number(data.get("damage", 0), "card.effects.damage"),
            block=_require_number(data.get("block", 0), "card.effects.block"),
            draw=_require_number(data.get("draw", 0), "card.effects.draw"),
            energy=_require_number(data.get("energy", 0), "card.effects.energy"),
            extra=_optional_number_mapping(data.get("extra"), "card.effects.extra"),
        )


@dataclass(frozen=True)
class CardData:
    id: str
    name: str
    character: str
    type: str
    rarity: str
    cost: int
    tags: frozenset[str]
    roles: frozenset[str]
    quality_prior: float
    pick_context: frozenset[str]
    source_patch: str | None
    source_notes: tuple[str, ...]
    upgrades_to: str | None
    effects: CardEffects

    @classmethod
    def from_dict(cls, raw: Any, source: str) -> "CardData":
        data = _require_mapping(raw, f"card in {source}")
        tags = frozenset(_require_str(tag, f"{data.get('id', source)}.tags[{index}]") for index, tag in enumerate(_require_list(data.get("tags", []), "card.tags")))
        roles = frozenset(_require_str(role, f"{data.get('id', source)}.roles[{index}]") for index, role in enumerate(_require_list(data.get("roles", []), "card.roles")))
        pick_context = frozenset(
            _require_str(context, f"{data.get('id', source)}.pick_context[{index}]")
            for index, context in enumerate(_require_list(data.get("pick_context", []), "card.pick_context"))
        )
        source_notes = tuple(
            _require_str(note, f"{data.get('id', source)}.source_notes[{index}]")
            for index, note in enumerate(_require_list(data.get("source_notes", []), "card.source_notes"))
        )
        return cls(
            id=_require_str(data.get("id"), f"{source}.id"),
            name=_require_str(data.get("name"), f"{source}.name"),
            character=_require_str(data.get("character"), f"{source}.character"),
            type=_require_str(data.get("type"), f"{source}.type").lower(),
            rarity=_require_str(data.get("rarity"), f"{source}.rarity").lower(),
            cost=_require_int(data.get("cost"), f"{source}.cost", minimum=0),
            tags=tags,
            roles=roles,
            quality_prior=_optional_number(data.get("quality_prior"), f"{source}.quality_prior"),
            pick_context=pick_context,
            source_patch=_optional_str(data.get("source_patch"), f"{source}.source_patch"),
            source_notes=source_notes,
            upgrades_to=_optional_str(data.get("upgrades_to"), f"{source}.upgrades_to"),
            effects=CardEffects.from_dict(data.get("effects")),
        )


@dataclass(frozen=True)
class TaggedData:
    id: str
    name: str
    tags: frozenset[str]
    roles: frozenset[str] = frozenset()
    quality_prior: float = 0
    pick_context: frozenset[str] = frozenset()
    source_patch: str | None = None
    source_notes: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, raw: Any, source: str) -> "TaggedData":
        data = _require_mapping(raw, source)
        item_id = data.get("id", source)
        roles = frozenset(
            _require_str(role, f"{item_id}.roles[{index}]")
            for index, role in enumerate(_require_list(data.get("roles", []), f"{source}.roles"))
        )
        pick_context = frozenset(
            _require_str(context, f"{item_id}.pick_context[{index}]")
            for index, context in enumerate(_require_list(data.get("pick_context", []), f"{source}.pick_context"))
        )
        source_notes = tuple(
            _require_str(note, f"{item_id}.source_notes[{index}]")
            for index, note in enumerate(_require_list(data.get("source_notes", []), f"{source}.source_notes"))
        )
        return cls(
            id=_require_str(data.get("id"), f"{source}.id"),
            name=_require_str(data.get("name"), f"{source}.name"),
            tags=frozenset(
                _require_str(tag, f"{source}.tags[{index}]")
                for index, tag in enumerate(_require_list(data.get("tags", []), f"{source}.tags"))
            ),
            roles=roles,
            quality_prior=_optional_number(data.get("quality_prior"), f"{source}.quality_prior"),
            pick_context=pick_context,
            source_patch=_optional_str(data.get("source_patch"), f"{source}.source_patch"),
            source_notes=source_notes,
        )


@dataclass(frozen=True)
class ChoiceRecommendation:
    choice: str
    name: str
    rank: int
    score: float
    confidence: str
    reasoning: tuple[str, ...]
    risks: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "choice": self.choice,
            "name": self.name,
            "rank": self.rank,
            "score": round(self.score, 1),
            "confidence": self.confidence,
            "reasoning": list(self.reasoning),
            "risks": list(self.risks),
        }


@dataclass(frozen=True)
class RecommendationResult:
    recommendation_type: str
    ranked_choices: tuple[ChoiceRecommendation, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "recommendation_type": self.recommendation_type,
            "ranked_choices": [choice.to_dict() for choice in self.ranked_choices],
        }
