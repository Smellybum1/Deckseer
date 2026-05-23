from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

from deckseer.current_state import CurrentState, build_card_reward_state
from deckseer.models import DataError, ValidationError


@dataclass(frozen=True)
class SaveDeckCard:
    id: str
    upgraded: bool
    count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "upgraded": self.upgraded,
            "count": self.count,
        }


@dataclass(frozen=True)
class ImportedRunSummary:
    source_type: str
    character: str
    ascension: int
    deck_size: int
    unique_cards: int
    relic_count: int
    potion_count: int
    win: bool | None
    run_time: int | None
    seed: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_type": self.source_type,
            "character": self.character,
            "ascension": self.ascension,
            "deck_size": self.deck_size,
            "unique_cards": self.unique_cards,
            "relic_count": self.relic_count,
            "potion_count": self.potion_count,
            "win": self.win,
            "run_time": self.run_time,
            "seed": self.seed,
        }


@dataclass(frozen=True)
class ImportedRun:
    summary: ImportedRunSummary
    deck: tuple[SaveDeckCard, ...]
    relics: tuple[str, ...]
    potions: tuple[str, ...]

    def to_summary_dict(self) -> dict[str, Any]:
        payload = self.summary.to_dict()
        payload["deck_preview"] = [card.to_dict() for card in self.deck[:10]]
        payload["relics"] = list(self.relics)
        payload["potions"] = list(self.potions)
        return payload

    def to_recommendation_input(
        self,
        *,
        card_reward: tuple[str, ...],
        hp_current: int,
        hp_max: int,
        act: int,
        floor: int,
        run_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.to_current_state(
            card_reward=card_reward,
            hp_current=hp_current,
            hp_max=hp_max,
            act=act,
            floor=floor,
            run_context=run_context,
        ).to_recommendation_input()

    def to_current_state(
        self,
        *,
        card_reward: tuple[str, ...],
        hp_current: int,
        hp_max: int,
        act: int,
        floor: int,
        run_context: dict[str, Any] | None = None,
    ) -> CurrentState:
        caveat = "Imported from Slay the Spire 2 run history; verify HP, floor, and current reward manually."
        context = run_context or {
            "recent_damage": None,
            "next_node_type": "unknown",
            "boss": None,
            "notes": [caveat],
        }
        return build_card_reward_state(
            source_type=self.summary.source_type,
            character=self.summary.character,
            act=act,
            floor=floor,
            ascension=self.summary.ascension,
            gold=0,
            hp_current=hp_current,
            hp_max=hp_max,
            deck=self.deck,
            relics=self.relics,
            potions=self.potions,
            card_reward=card_reward,
            run_context=context,
            caveats=(caveat,),
        )


def load_sts2_run(path: Path, *, player_index: int = 0) -> ImportedRun:
    raw = _read_json(path)
    data = _require_mapping(raw, "save file")
    if "players" not in data:
        raise DataError("Save file does not look like a Slay the Spire 2 run-history JSON file; expected top-level players")
    players = _require_list(data.get("players"), "players")
    if player_index < 0 or player_index >= len(players):
        raise ValidationError(f"player_index {player_index} is out of range for {len(players)} players")
    player = _require_mapping(players[player_index], f"players[{player_index}]")

    deck = _load_deck(player.get("deck"))
    relics = _load_id_list(player.get("relics"), "relics")
    potions = _load_id_list(player.get("potions", []), "potions")
    summary = ImportedRunSummary(
        source_type="sts2_run_history",
        character=normalize_game_id(_require_str(player.get("character"), "player.character")),
        ascension=_optional_int(data.get("ascension"), "ascension", default=0),
        deck_size=sum(card.count for card in deck),
        unique_cards=len(deck),
        relic_count=len(relics),
        potion_count=len(potions),
        win=_optional_bool(data.get("win"), "win"),
        run_time=_optional_int(data.get("run_time"), "run_time", default=None),
        seed=_optional_str(data.get("seed"), "seed"),
    )
    return ImportedRun(summary=summary, deck=deck, relics=relics, potions=potions)


def normalize_game_id(raw_id: str) -> str:
    value = raw_id.split(".")[-1].lower()
    value = re.sub(r"[^a-z0-9]+", "_", value).strip("_")
    for suffix in ("_ironclad", "_silent", "_defect", "_necrobinder", "_regent"):
        if value.endswith(suffix):
            value = value[: -len(suffix)]
    return value


def _load_deck(raw_deck: Any) -> tuple[SaveDeckCard, ...]:
    counts: dict[tuple[str, bool], int] = defaultdict(int)
    for index, raw_card in enumerate(_require_list(raw_deck, "deck")):
        card = _require_mapping(raw_card, f"deck[{index}]")
        card_id = normalize_game_id(_require_str(card.get("id"), f"deck[{index}].id"))
        upgraded = _optional_int(card.get("current_upgrade_level"), f"deck[{index}].current_upgrade_level", default=0) > 0
        counts[(card_id, upgraded)] += 1
    return tuple(
        SaveDeckCard(id=card_id, upgraded=upgraded, count=count)
        for (card_id, upgraded), count in sorted(counts.items())
    )


def _load_id_list(raw_items: Any, label: str) -> tuple[str, ...]:
    normalized: list[str] = []
    for index, raw_item in enumerate(_require_list(raw_items, label)):
        if isinstance(raw_item, str):
            normalized.append(normalize_game_id(raw_item))
            continue
        item = _require_mapping(raw_item, f"{label}[{index}]")
        normalized.append(normalize_game_id(_require_str(item.get("id"), f"{label}[{index}].id")))
    return tuple(normalized)


def _read_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except UnicodeDecodeError as exc:
        raise DataError(f"{path} is not a plain JSON save file") from exc
    except FileNotFoundError as exc:
        raise DataError(f"Save file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path} is not valid JSON: {exc}") from exc


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


def _optional_int(value: Any, label: str, *, default: int | None) -> int | None:
    if value is None:
        return default
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValidationError(f"{label} must be an integer")
    return value


def _optional_bool(value: Any, label: str) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ValidationError(f"{label} must be a boolean")
    return value
