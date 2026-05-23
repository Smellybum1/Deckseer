from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from deckseer.card_lookup import resolve_card_id, suggest_card_ids
from deckseer.data_loader import DeckseerData
from deckseer.current_state import load_manual_card_reward_state
from deckseer.models import ValidationError


def normalize_run_file(path: Path, data: DeckseerData) -> dict[str, Any]:
    state = load_manual_card_reward_state(path)
    return normalize_run_payload(state.to_recommendation_input(), data)


def normalize_run_payload(payload: dict[str, Any], data: DeckseerData) -> dict[str, Any]:
    normalized = _copy_json_object(payload)
    changes: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []

    for index, card in enumerate(normalized["deck"]):
        original = card["id"]
        replacement = resolve_card_id(original, data.cards_by_id)
        field = f"deck[{index}].id"
        if replacement is None:
            if original not in data.cards_by_id:
                unresolved.append(_unresolved_entry(field, original, data))
            continue
        if replacement != original:
            card["id"] = replacement
            changes.append({"field": field, "from": original, "to": replacement})

    for index, original in enumerate(normalized["card_reward"]):
        replacement = resolve_card_id(original, data.cards_by_id)
        field = f"card_reward[{index}]"
        if replacement is None:
            if original not in data.cards_by_id:
                unresolved.append(_unresolved_entry(field, original, data))
            continue
        if replacement != original:
            normalized["card_reward"][index] = replacement
            changes.append({"field": field, "from": original, "to": replacement})

    return {
        "normalization_type": "run_card_ids",
        "changed": bool(changes),
        "changes": changes,
        "unresolved": unresolved,
        "payload": normalized,
    }


def write_normalized_payload(report: dict[str, Any], output_path: Path) -> None:
    output_path.write_text(json.dumps(report["payload"], indent=2) + "\n", encoding="utf-8")


def _unresolved_entry(field: str, value: str, data: DeckseerData) -> dict[str, Any]:
    return {
        "field": field,
        "value": value,
        "suggestions": suggest_card_ids(value, data.cards_by_id),
    }


def _copy_json_object(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError("run payload must be an object")
    return json.loads(json.dumps(value))
