from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from deckseer.current_state import CurrentState
from deckseer.models import DataError, ValidationError


@dataclass(frozen=True)
class ExportedState:
    source_type: str
    screen_type: str
    metadata: dict[str, Any]
    current_state: CurrentState

    def to_summary_dict(self) -> dict[str, Any]:
        payload = self.current_state.to_recommendation_input()
        return {
            "source_type": self.source_type,
            "screen_type": self.screen_type,
            "source": self.metadata.get("source"),
            "exporter_version": self.metadata.get("exporter_version"),
            "game_patch": self.metadata.get("game_patch"),
            "game_build": self.metadata.get("game_build"),
            "exported_at": self.metadata.get("exported_at"),
            "requires_user_confirmation": self.metadata.get("requires_user_confirmation", False),
            "valid": True,
            "character": payload["character"],
            "card_reward": list(payload["card_reward"]),
            "caveats": list(self.current_state.caveats),
        }


@dataclass(frozen=True)
class InspectedExport:
    source_type: str
    screen_type: str
    metadata: dict[str, Any]
    status: str | None = None
    current_state: CurrentState | None = None

    def to_summary_dict(self) -> dict[str, Any]:
        payload = self.current_state.to_recommendation_input() if self.current_state is not None else None
        summary = {
            "source_type": self.source_type,
            "screen_type": self.screen_type,
            "source": self.metadata.get("source"),
            "exporter_version": self.metadata.get("exporter_version"),
            "game_patch": self.metadata.get("game_patch"),
            "game_build": self.metadata.get("game_build"),
            "exported_at": self.metadata.get("exported_at"),
            "requires_user_confirmation": self.metadata.get("requires_user_confirmation", False),
            "valid": True,
            "caveats": _metadata_caveats(self.metadata),
        }
        if self.status is not None:
            summary["status"] = self.status
        if payload is not None:
            summary["character"] = payload["character"]
            summary["card_reward"] = list(payload["card_reward"])
            summary["caveats"] = list(self.current_state.caveats)
        return summary


def inspect_exporter_state(path: Path) -> InspectedExport:
    raw = _read_json(path)
    data = _require_mapping(raw, "exporter state")
    game = _require_str(data.get("game", "slay_the_spire_2"), "game")
    if game != "slay_the_spire_2":
        raise ValidationError(f"unsupported exporter game: {game}")
    screen_type = _require_str(data.get("screen_type"), "screen_type")
    metadata = _copy_optional_mapping(data.get("export_metadata"), "export_metadata")
    source_type = _require_str(metadata.get("source", "deckseer_exporter_mod"), "export_metadata.source")
    if screen_type == "card_reward":
        exported = _load_card_reward_export(data, metadata, source_type)
        return InspectedExport(
            source_type=exported.source_type,
            screen_type=exported.screen_type,
            metadata=exported.metadata,
            current_state=exported.current_state,
        )
    if screen_type == "exporter_status":
        return InspectedExport(
            source_type=source_type,
            screen_type=screen_type,
            metadata=metadata,
            status=_require_str(data.get("status"), "status"),
        )
    raise ValidationError(f"unsupported exporter screen_type: {screen_type}")


def load_exporter_state(path: Path) -> ExportedState:
    raw = _read_json(path)
    data = _require_mapping(raw, "exporter state")
    game = _require_str(data.get("game", "slay_the_spire_2"), "game")
    if game != "slay_the_spire_2":
        raise ValidationError(f"unsupported exporter game: {game}")
    screen_type = _require_str(data.get("screen_type"), "screen_type")
    if screen_type != "card_reward":
        raise ValidationError(f"recommend-export only supports card_reward exports; got {screen_type}")

    metadata = _copy_optional_mapping(data.get("export_metadata"), "export_metadata")
    source_type = _require_str(metadata.get("source", "deckseer_exporter_mod"), "export_metadata.source")
    return _load_card_reward_export(data, metadata, source_type)


def _load_card_reward_export(data: dict[str, Any], metadata: dict[str, Any], source_type: str) -> ExportedState:
    caveats = _metadata_caveats(metadata)
    if metadata.get("requires_user_confirmation") is True:
        caveats.append("Exporter state requires user confirmation before recommendation.")

    payload = _canonical_payload(data)
    state = CurrentState(source_type=source_type, payload=payload, caveats=tuple(caveats))
    state.to_run_state()
    return ExportedState(
        source_type=source_type,
        screen_type="card_reward",
        metadata=metadata,
        current_state=state,
    )


def _canonical_payload(data: dict[str, Any]) -> dict[str, Any]:
    payload = dict(data)
    payload.pop("screen_type", None)
    payload.pop("export_metadata", None)
    return _copy_json_object(payload)


def _metadata_caveats(metadata: dict[str, Any]) -> list[str]:
    raw_caveats = metadata.get("caveats", [])
    caveats = _require_list(raw_caveats, "export_metadata.caveats")
    return [_require_str(caveat, f"export_metadata.caveats[{index}]") for index, caveat in enumerate(caveats)]


def _copy_optional_mapping(value: Any, label: str) -> dict[str, Any]:
    if value is None:
        return {}
    return _copy_json_object(_require_mapping(value, label))


def _copy_json_object(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError("exporter payload must be an object")
    return json.loads(json.dumps(value))


def _read_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except UnicodeDecodeError as exc:
        raise DataError(f"{path} is not a plain JSON exporter state file") from exc
    except FileNotFoundError as exc:
        raise DataError(f"Exporter state file not found: {path}") from exc
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
