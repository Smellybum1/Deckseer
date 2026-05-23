from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Protocol

from deckseer.models import RunState, ValidationError


class DictLikeDeckCard(Protocol):
    def to_dict(self) -> dict[str, Any]:
        ...


@dataclass(frozen=True)
class CurrentState:
    source_type: str
    payload: dict[str, Any]
    caveats: tuple[str, ...] = ()

    def to_run_state(self) -> RunState:
        return RunState.from_dict(self.payload)

    def to_recommendation_input(self) -> dict[str, Any]:
        return _copy_json_object(self.payload)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_type": self.source_type,
            "payload": self.to_recommendation_input(),
            "caveats": list(self.caveats),
        }


def load_manual_card_reward_state(path: Path) -> CurrentState:
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path} is not valid JSON: {exc}") from exc
    state = CurrentState(source_type="manual_json", payload=_copy_json_object(raw))
    state.to_run_state()
    return state


def build_card_reward_state(
    *,
    source_type: str,
    character: str,
    act: int,
    floor: int,
    hp_current: int,
    hp_max: int,
    deck: tuple[dict[str, Any] | DictLikeDeckCard, ...] | list[dict[str, Any] | DictLikeDeckCard],
    relics: tuple[str, ...] | list[str],
    potions: tuple[str, ...] | list[str],
    card_reward: tuple[str, ...] | list[str],
    game: str = "slay_the_spire_2",
    ascension: int = 0,
    gold: int = 0,
    run_context: dict[str, Any] | None = None,
    caveats: tuple[str, ...] = (),
) -> CurrentState:
    payload = {
        "game": game,
        "character": character,
        "act": act,
        "floor": floor,
        "ascension": ascension,
        "gold": gold,
        "hp": {
            "current": hp_current,
            "max": hp_max,
        },
        "deck": [_deck_card_to_dict(card) for card in deck],
        "relics": list(relics),
        "potions": list(potions),
        "card_reward": list(card_reward),
        "run_context": run_context or {},
    }
    state = CurrentState(source_type=source_type, payload=payload, caveats=caveats)
    state.to_run_state()
    return state


def _deck_card_to_dict(card: dict[str, Any] | DictLikeDeckCard) -> dict[str, Any]:
    if hasattr(card, "to_dict"):
        return _copy_json_object(card.to_dict())
    return _copy_json_object(card)


def _copy_json_object(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError("current state payload must be an object")
    return json.loads(json.dumps(value))
