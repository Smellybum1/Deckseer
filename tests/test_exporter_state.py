from __future__ import annotations

import json
from pathlib import Path

import pytest

from deckseer.cli import main
from deckseer.importers.exporter_state import inspect_exporter_state, load_exporter_recommendation_state, load_exporter_state
from deckseer.models import ValidationError


FIXTURE = Path("tests/fixtures/exporter_card_reward_state.json")
LIVE_V030_FIXTURE = Path("tests/fixtures/exporter_card_reward_live_v030_state.json")
LIVE_V039_MIXED_REWARD_FIXTURE = Path("tests/fixtures/exporter_card_reward_live_v039_mixed_reward_state.json")
LIVE_V047_MIXED_REWARD_MAPPED_FIXTURE = Path(
    "tests/fixtures/exporter_card_reward_live_v047_mixed_reward_mapped_state.json"
)
LIVE_RELIC_V040_FIXTURE = Path("tests/fixtures/exporter_relic_reward_live_v040_state.json")
LIVE_RELIC_V045_TREASURE_FIXTURE = Path("tests/fixtures/exporter_relic_reward_live_v045_treasure_state.json")
LIVE_RELIC_V046_TREASURE_MAPPED_FIXTURE = Path(
    "tests/fixtures/exporter_relic_reward_live_v046_treasure_mapped_state.json"
)
UNKNOWN_ID_FIXTURE = Path("tests/fixtures/exporter_card_reward_unknown_id_state.json")
UPGRADED_DECK_FIXTURE = Path("tests/fixtures/exporter_card_reward_upgraded_deck_state.json")
UPGRADED_REWARD_OBJECT_FIXTURE = Path("tests/fixtures/exporter_card_reward_upgraded_reward_object_state.json")
STATUS_FIXTURE = Path("tests/fixtures/exporter_status_state.json")
STATUS_V021_FIXTURE = Path("tests/fixtures/exporter_status_v021_state.json")
STATUS_V022_SCREEN_FIXTURE = Path("tests/fixtures/exporter_status_v022_screen_observation_state.json")
STATUS_V023_CARD_CHOICE_SCREEN_FIXTURE = Path("tests/fixtures/exporter_status_v023_card_choice_screen_state.json")
STATUS_V024_CARD_CHOICE_CLOSED_FIXTURE = Path("tests/fixtures/exporter_status_v024_card_choice_closed_state.json")
STATUS_V025_CARD_IDENTITY_PROBE_FIXTURE = Path("tests/fixtures/exporter_status_v025_card_identity_probe_state.json")
STATUS_V026_CARD_IDENTITY_RUNTIME_FIXTURE = Path("tests/fixtures/exporter_status_v026_card_identity_runtime_state.json")
STATUS_V027_CARD_IDENTITY_RUNTIME_VISIBLE_FIXTURE = Path("tests/fixtures/exporter_status_v027_card_identity_runtime_visible_state.json")
STATUS_V028_REWARD_SCREEN_IDENTITY_RUNTIME_FIXTURE = Path("tests/fixtures/exporter_status_v028_reward_screen_identity_runtime_state.json")
STATUS_V029_CARD_IDENTITY_REVIEW_FIXTURE = Path("tests/fixtures/exporter_status_v029_card_identity_review_state.json")
STATUS_V0210_RUN_STATE_COMPILE_FIXTURE = Path("tests/fixtures/exporter_status_v0210_run_state_compile_state.json")
STATUS_V0211_RUN_STATE_RUNTIME_FIXTURE = Path("tests/fixtures/exporter_status_v0211_run_state_runtime_state.json")
STATUS_V0212_DECK_IDENTITY_REVIEW_FIXTURE = Path("tests/fixtures/exporter_status_v0212_deck_identity_review_state.json")
STATUS_V0213_DECK_IDENTITY_ALIAS_FIXTURE = Path("tests/fixtures/exporter_status_v0213_deck_identity_alias_state.json")
STATUS_V0214_DRAMATIC_ENTRANCE_FIXTURE = Path("tests/fixtures/exporter_status_v0214_dramatic_entrance_state.json")
STATUS_V0215_LIVE_EXPORT_CANDIDATE_REFUSAL_FIXTURE = Path(
    "tests/fixtures/exporter_status_v0215_live_export_candidate_refusal_state.json"
)
STATUS_V0216_RELIC_POTION_IDENTITY_REVIEW_FIXTURE = Path(
    "tests/fixtures/exporter_status_v0216_relic_potion_identity_review_state.json"
)
STATUS_V032_POST_PICKUP_FRESHNESS_FIXTURE = Path(
    "tests/fixtures/exporter_status_v032_post_pickup_freshness_state.json"
)
STATUS_V033_REWARD_COLLECTED_FRESHNESS_FIXTURE = Path(
    "tests/fixtures/exporter_status_v033_reward_collected_freshness_state.json"
)
STATUS_V034_MIXED_REWARD_READINESS_FIXTURE = Path(
    "tests/fixtures/exporter_status_v034_mixed_reward_readiness_state.json"
)
STATUS_V035_REWARD_COLLECTED_POTION_IDENTITY_FIXTURE = Path(
    "tests/fixtures/exporter_status_v035_reward_collected_potion_identity_state.json"
)
STATUS_V036_COLORLESS_POTION_MAPPING_FIXTURE = Path(
    "tests/fixtures/exporter_status_v036_colorless_potion_mapping_state.json"
)
STATUS_V037_REWARD_COLLECTED_VISIBLE_PLAYER_FIXTURE = Path(
    "tests/fixtures/exporter_status_v037_reward_collected_visible_player_state.json"
)
STATUS_V038_REWARD_COLLECTED_RUN_STATE_CONTEXT_FIXTURE = Path(
    "tests/fixtures/exporter_status_v038_reward_collected_run_state_context_state.json"
)
STATUS_V0310_CARD_REWARD_SELECTION_CLOSED_FIXTURE = Path(
    "tests/fixtures/exporter_status_v0310_card_reward_selection_closed_state.json"
)
STATUS_V047_CARD_REWARD_SELECTION_CLOSED_FIXTURE = Path(
    "tests/fixtures/exporter_status_v047_card_reward_selection_closed_state.json"
)
STATUS_V047_EVENT_SPECIAL_ROUTE_STARTUP_FIXTURE = Path(
    "tests/fixtures/exporter_status_v047_event_special_route_startup_state.json"
)
STATUS_V047_EVENT_SPECIAL_ROUTE_MAP_CLEAR_STARTUP_FIXTURE = Path(
    "tests/fixtures/exporter_status_v047_event_special_route_map_clear_startup_state.json"
)
STATUS_V047_EVENT_SPECIAL_ROUTE_MAP_CLEARED_FIXTURE = Path(
    "tests/fixtures/exporter_status_v047_event_special_route_map_cleared_state.json"
)
STATUS_V047_EVENT_SPECIAL_ROUTE_OVERLAY_STARTUP_FIXTURE = Path(
    "tests/fixtures/exporter_status_v047_event_special_route_overlay_startup_state.json"
)
STATUS_V047_EVENT_SPECIAL_ROUTE_BUNDLE_ACTIVE_FIXTURE = Path(
    "tests/fixtures/exporter_status_v047_event_special_route_bundle_active_state.json"
)
STATUS_V047_EVENT_SPECIAL_ROUTE_RANWID_RELIC_ACTIVE_FIXTURE = Path(
    "tests/fixtures/exporter_status_v047_event_special_route_ranwid_relic_active_state.json"
)
STATUS_V047_EVENT_SPECIAL_ROUTE_DOLL_ROOM_RELIC_OPTIONS_FIXTURE = Path(
    "tests/fixtures/exporter_status_v047_event_special_route_doll_room_relic_options_state.json"
)
STATUS_V047_EVENT_SPECIAL_ROUTE_VAKUU_RELIC_OPTIONS_FIXTURE = Path(
    "tests/fixtures/exporter_status_v047_event_special_route_vakuu_relic_options_state.json"
)
STATUS_V047_EVENT_SPECIAL_ROUTE_ZEN_WEAVER_ACTIVE_FIXTURE = Path(
    "tests/fixtures/exporter_status_v047_event_special_route_zen_weaver_active_state.json"
)
STATUS_V047_EVENT_SPECIAL_ROUTE_SELF_HELP_BOOK_ACTIVE_FIXTURE = Path(
    "tests/fixtures/exporter_status_v047_event_special_route_self_help_book_active_state.json"
)
STATUS_V047_EVENT_SPECIAL_ROUTE_SELF_HELP_BOOK_CARD_SELECT_FIXTURE = Path(
    "tests/fixtures/exporter_status_v047_event_special_route_self_help_book_card_select_state.json"
)
STATUS_V047_EVENT_SPECIAL_ROUTE_DECK_ENCHANT_ACTIVE_FIXTURE = Path(
    "tests/fixtures/exporter_status_v047_event_special_route_deck_enchant_active_state.json"
)
STATUS_V047_EVENT_SPECIAL_ROUTE_WOOD_CARVINGS_DECK_ENCHANT_FIXTURE = Path(
    "tests/fixtures/exporter_status_v047_event_special_route_wood_carvings_deck_enchant_state.json"
)
STATUS_V047_EVENT_SPECIAL_ROUTE_LOOT_CARD_STATUS_FIXTURE = Path(
    "tests/fixtures/exporter_status_v047_event_special_route_loot_card_status_state.json"
)
STATUS_V047_EVENT_SPECIAL_ROUTE_BRAIN_LEECH_ACTIVE_FIXTURE = Path(
    "tests/fixtures/exporter_status_v047_event_special_route_brain_leech_active_state.json"
)
STATUS_V047_EVENT_SPECIAL_ROUTE_BRAIN_LEECH_MAP_CLEARED_FIXTURE = Path(
    "tests/fixtures/exporter_status_v047_event_special_route_brain_leech_map_cleared_state.json"
)
STATUS_V047_EVENT_SPECIAL_ROUTE_EVENT_ROOM_CLOSED_FIXTURE = Path(
    "tests/fixtures/exporter_status_v047_event_special_route_event_room_closed_state.json"
)
STATUS_V047_EVENT_SPECIAL_ROUTE_ANCIENT_ACTIVE_FIXTURE = Path(
    "tests/fixtures/exporter_status_v047_event_special_route_ancient_active_state.json"
)
STATUS_V047_EVENT_SPECIAL_ROUTE_ANCIENT_POST_CHOICE_FIXTURE = Path(
    "tests/fixtures/exporter_status_v047_event_special_route_ancient_post_choice_state.json"
)
STATUS_V047_EVENT_SPECIAL_ROUTE_FIXTURES = (
    STATUS_V047_EVENT_SPECIAL_ROUTE_STARTUP_FIXTURE,
    STATUS_V047_EVENT_SPECIAL_ROUTE_MAP_CLEAR_STARTUP_FIXTURE,
    STATUS_V047_EVENT_SPECIAL_ROUTE_MAP_CLEARED_FIXTURE,
    STATUS_V047_EVENT_SPECIAL_ROUTE_OVERLAY_STARTUP_FIXTURE,
    STATUS_V047_EVENT_SPECIAL_ROUTE_BUNDLE_ACTIVE_FIXTURE,
    STATUS_V047_EVENT_SPECIAL_ROUTE_RANWID_RELIC_ACTIVE_FIXTURE,
    STATUS_V047_EVENT_SPECIAL_ROUTE_DOLL_ROOM_RELIC_OPTIONS_FIXTURE,
    STATUS_V047_EVENT_SPECIAL_ROUTE_VAKUU_RELIC_OPTIONS_FIXTURE,
    STATUS_V047_EVENT_SPECIAL_ROUTE_ZEN_WEAVER_ACTIVE_FIXTURE,
    STATUS_V047_EVENT_SPECIAL_ROUTE_SELF_HELP_BOOK_ACTIVE_FIXTURE,
    STATUS_V047_EVENT_SPECIAL_ROUTE_SELF_HELP_BOOK_CARD_SELECT_FIXTURE,
    STATUS_V047_EVENT_SPECIAL_ROUTE_DECK_ENCHANT_ACTIVE_FIXTURE,
    STATUS_V047_EVENT_SPECIAL_ROUTE_WOOD_CARVINGS_DECK_ENCHANT_FIXTURE,
    STATUS_V047_EVENT_SPECIAL_ROUTE_LOOT_CARD_STATUS_FIXTURE,
    STATUS_V047_EVENT_SPECIAL_ROUTE_BRAIN_LEECH_ACTIVE_FIXTURE,
    STATUS_V047_EVENT_SPECIAL_ROUTE_BRAIN_LEECH_MAP_CLEARED_FIXTURE,
    STATUS_V047_EVENT_SPECIAL_ROUTE_EVENT_ROOM_CLOSED_FIXTURE,
    STATUS_V047_EVENT_SPECIAL_ROUTE_ANCIENT_ACTIVE_FIXTURE,
    STATUS_V047_EVENT_SPECIAL_ROUTE_ANCIENT_POST_CHOICE_FIXTURE,
)
STATUS_V040_RELIC_REWARD_CLOSED_FIXTURE = Path(
    "tests/fixtures/exporter_status_v040_relic_reward_closed_state.json"
)
STATUS_V041_TREASURE_RELIC_ROUTE_FIXTURE = Path(
    "tests/fixtures/exporter_status_v041_treasure_relic_route_state.json"
)
STATUS_V042_TREASURE_RELIC_IDENTITY_FIXTURE = Path(
    "tests/fixtures/exporter_status_v042_treasure_relic_identity_state.json"
)
STATUS_V043_TREASURE_RELIC_MODEL_ID_FIXTURE = Path(
    "tests/fixtures/exporter_status_v043_treasure_relic_model_id_state.json"
)
STATUS_V044_TREASURE_RELIC_LETTER_OPENER_FIXTURE = Path(
    "tests/fixtures/exporter_status_v044_treasure_relic_letter_opener_state.json"
)
STATUS_V045_TREASURE_RELIC_PICKED_FIXTURE = Path(
    "tests/fixtures/exporter_status_v045_treasure_relic_picked_state.json"
)
STATUS_V046_TREASURE_RELIC_PICKED_FIXTURE = Path(
    "tests/fixtures/exporter_status_v046_treasure_relic_picked_state.json"
)
RELIC_FIXTURE = Path("tests/fixtures/exporter_relic_reward_state.json")


def _find_forbidden_keys(value: object, forbidden: set[str], path: str = "$") -> list[str]:
    if isinstance(value, dict):
        found: list[str] = []
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in forbidden:
                found.append(child_path)
            found.extend(_find_forbidden_keys(child, forbidden, child_path))
        return found
    if isinstance(value, list):
        found = []
        for index, child in enumerate(value):
            found.extend(_find_forbidden_keys(child, forbidden, f"{path}[{index}]"))
        return found
    return []


def test_exporter_state_loads_through_current_state_adapter() -> None:
    exported = load_exporter_state(FIXTURE)
    run = exported.current_state.to_run_state()

    assert exported.source_type == "deckseer_exporter_mod"
    assert exported.screen_type == "card_reward"
    assert run.character == "ironclad"
    assert run.card_reward == ("pommel_strike", "shrug_it_off", "anger")


def test_exporter_state_drops_metadata_from_recommendation_input() -> None:
    exported = load_exporter_state(FIXTURE)
    payload = exported.current_state.to_recommendation_input()

    assert "screen_type" not in payload
    assert "export_metadata" not in payload
    assert payload["game"] == "slay_the_spire_2"


def test_exporter_state_preserves_upgraded_deck_cards() -> None:
    exported = load_exporter_state(UPGRADED_DECK_FIXTURE)
    run = exported.current_state.to_run_state()
    cards = {(card.id, card.upgraded): card.count for card in run.deck}

    assert cards[("defend", True)] == 1
    assert cards[("bash", True)] == 1
    assert run.card_reward == ("pommel_strike", "shrug_it_off")


def test_exporter_state_preserves_metadata_caveats_outside_scorer() -> None:
    exported = load_exporter_state(FIXTURE)

    assert "User should confirm visible card reward before using this state." in exported.current_state.caveats
    assert "Exporter state requires user confirmation before recommendation." in exported.current_state.caveats


def test_exporter_state_accepts_live_v030_card_reward_contract() -> None:
    exported = load_exporter_state(LIVE_V030_FIXTURE)
    run = exported.current_state.to_run_state()

    assert exported.source_type == "deckseer_exporter_mod"
    assert exported.screen_type == "card_reward"
    assert exported.metadata["exporter_version"] == "0.3.0"
    assert exported.metadata["requires_user_confirmation"] is True
    assert run.character == "silent"
    assert run.relics == ("lead_paperweight", "ring_of_the_snake")
    assert run.card_reward == ("cloak_and_dagger", "bouncing_flask", "infinite_blades")
    assert "Live exporter map/path context is unknown/defaulted." in exported.current_state.caveats


def test_exporter_state_preserves_contract_caveats_for_upgraded_deck_fixture() -> None:
    exported = load_exporter_state(UPGRADED_DECK_FIXTURE)

    assert "Fixture preserves upgraded deck cards while reward upgrade export remains unimplemented." in exported.current_state.caveats
    assert "Exporter state requires user confirmation before recommendation." in exported.current_state.caveats


def test_exporter_state_rejects_object_shaped_upgraded_reward_until_contract_exists() -> None:
    with pytest.raises(ValidationError, match=r"card_reward\[0\] must be a non-empty string"):
        inspect_exporter_state(UPGRADED_REWARD_OBJECT_FIXTURE)


def test_exporter_state_rejects_unsupported_screen_type(tmp_path: Path) -> None:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    raw["screen_type"] = "shop"
    path = tmp_path / "shop_export.json"
    path.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(ValidationError, match="unsupported exporter screen_type: shop"):
        inspect_exporter_state(path)


def test_recommend_export_rejects_status_export() -> None:
    with pytest.raises(ValidationError, match="recommend-export only supports card_reward exports; got exporter_status"):
        load_exporter_state(STATUS_FIXTURE)


def test_inspect_export_cli_smoke(capsys) -> None:
    status = main(["inspect-export", str(FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["source_type"] == "deckseer_exporter_mod"
    assert payload["screen_type"] == "card_reward"
    assert payload["valid"] is True
    assert payload["card_reward"] == ["pommel_strike", "shrug_it_off", "anger"]


def test_inspect_export_accepts_status_fixture(capsys) -> None:
    status = main(["inspect-export", str(STATUS_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["source_type"] == "deckseer_exporter_mod"
    assert payload["screen_type"] == "exporter_status"
    assert payload["status"] == "ok"
    assert payload["valid"] is True
    assert payload["requires_user_confirmation"] is False
    assert payload["caveats"] == ["Static exporter status only; no live run state is present."]


def test_inspect_export_accepts_status_fixture_with_diagnostics(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V021_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["source_type"] == "deckseer_exporter_mod"
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.2.1"
    assert payload["status"] == "ok"
    assert payload["valid"] is True
    assert payload["requires_user_confirmation"] is False
    assert "Card reward API probe compiled against public STS2 reward/run-state symbols, but no live reward data is exported." in payload["caveats"]


def test_status_export_preserves_diagnostics_as_metadata() -> None:
    inspected = inspect_exporter_state(STATUS_V021_FIXTURE)

    diagnostics = inspected.metadata["diagnostics"]

    assert diagnostics["card_reward_api_probe"] == "compiled"
    assert "RewardsSet.Rewards" in diagnostics["verified_symbols"]
    assert diagnostics["hook_model_compile_probe"] == "compiled_not_registered"
    assert "ModelDb.Singleton" in diagnostics["hook_model_verified_symbols"]


def test_status_export_preserves_screen_observation_diagnostics_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V022_SCREEN_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V022_SCREEN_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.2.2"
    assert "card_reward" not in payload
    assert "character" not in payload
    assert diagnostics["screen_observation_probe"] == "registered"
    assert diagnostics["visible_reward_probe_status"] == "card_reward_model_seen"
    assert diagnostics["visible_card_reward_option_count"] == 3
    assert "CardReward.Cards" in diagnostics["screen_observation_verified_symbols"]


def test_status_export_preserves_card_choice_screen_diagnostics_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V023_CARD_CHOICE_SCREEN_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V023_CARD_CHOICE_SCREEN_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.2.3"
    assert "card_reward" not in payload
    assert "character" not in payload
    assert diagnostics["screen_observation_probe"] == "registered"
    assert diagnostics["visible_reward_probe_status"] == "card_choice_screen_seen"
    assert diagnostics["visible_card_reward_option_count"] == 2
    assert diagnostics["visible_card_choice_option_count"] == 2
    assert diagnostics["visible_card_choice_can_skip"] is True
    assert "NChooseACardSelectionScreen.ShowScreen" in diagnostics["screen_observation_verified_symbols"]


def test_status_export_preserves_card_choice_closed_diagnostics_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V024_CARD_CHOICE_CLOSED_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V024_CARD_CHOICE_CLOSED_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.2.4"
    assert "card_reward" not in payload
    assert "character" not in payload
    assert diagnostics["screen_observation_probe"] == "registered"
    assert diagnostics["visible_reward_probe_status"] == "reward_screen_completed"
    assert diagnostics["visible_reward_probe_last_event"] == "choose_card_screen_closed"
    assert diagnostics["visible_card_reward_option_count"] == 0
    assert diagnostics["visible_card_choice_option_count"] == 0
    assert diagnostics["visible_card_choice_can_skip"] is None
    assert "NChooseACardSelectionScreen._ExitTree" in diagnostics["screen_observation_verified_symbols"]


def test_status_export_preserves_card_identity_probe_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V025_CARD_IDENTITY_PROBE_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V025_CARD_IDENTITY_PROBE_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.2.5"
    assert "card_reward" not in payload
    assert "character" not in payload
    assert diagnostics["card_identity_mapping_probe"] == "compiled_not_exported"
    assert diagnostics["card_identity_mapping_verified_symbol_count"] == 7
    assert "CardModel.Id" in diagnostics["card_identity_mapping_verified_symbols"]
    assert "CardModel.CurrentUpgradeLevel" in diagnostics["card_identity_mapping_verified_symbols"]
    assert "SerializableCard.Id" in diagnostics["card_identity_mapping_verified_symbols"]


def test_status_export_preserves_card_identity_runtime_diagnostics_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V026_CARD_IDENTITY_RUNTIME_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V026_CARD_IDENTITY_RUNTIME_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.2.6"
    assert "card_reward" not in payload
    assert "character" not in payload
    assert diagnostics["card_identity_runtime_probe"] == "mapping_incomplete"
    assert diagnostics["visible_card_identity_read_count"] == 2
    assert diagnostics["visible_card_identity_mapping_known_count"] == 1
    assert diagnostics["visible_card_identity_mapping_unknown_count"] == 1
    assert diagnostics["visible_card_identity_upgraded_count"] == 1
    assert "visible_card_identity_ids" not in diagnostics
    assert "visible_card_identity_names" not in diagnostics


def test_status_export_preserves_card_identity_runtime_visible_counts_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V027_CARD_IDENTITY_RUNTIME_VISIBLE_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V027_CARD_IDENTITY_RUNTIME_VISIBLE_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.2.7"
    assert "card_reward" not in payload
    assert "character" not in payload
    assert diagnostics["visible_reward_probe_status"] == "card_choice_screen_seen"
    assert diagnostics["visible_card_reward_option_count"] == 3
    assert diagnostics["visible_card_choice_option_count"] == 3
    assert diagnostics["card_identity_runtime_probe"] == "mapping_incomplete"
    assert diagnostics["visible_card_identity_read_count"] == 3
    assert diagnostics["visible_card_identity_direct_id_count"] == 3
    assert diagnostics["visible_card_identity_mapping_known_count"] == 2
    assert diagnostics["visible_card_identity_mapping_unknown_count"] == 1
    assert diagnostics["visible_card_identity_upgraded_count"] == 0
    assert "NRewardsScreen.RewardCollectedFrom" not in diagnostics["screen_observation_verified_symbols"]
    assert "visible_card_identity_ids" not in diagnostics
    assert "visible_card_identity_names" not in diagnostics


def test_status_export_preserves_reward_screen_identity_runtime_counts_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V028_REWARD_SCREEN_IDENTITY_RUNTIME_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V028_REWARD_SCREEN_IDENTITY_RUNTIME_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.2.8"
    assert "card_reward" not in payload
    assert "character" not in payload
    assert diagnostics["visible_reward_probe_status"] == "card_reward_model_seen"
    assert diagnostics["visible_reward_probe_last_event"] == "rewards_screen_shown"
    assert diagnostics["visible_card_reward_option_count"] == 3
    assert diagnostics["visible_card_choice_option_count"] == 0
    assert diagnostics["card_identity_runtime_probe"] == "card_choice_ids_seen"
    assert diagnostics["card_identity_runtime_last_event"] == "rewards_screen_shown"
    assert diagnostics["visible_card_identity_read_count"] == 3
    assert diagnostics["visible_card_identity_mapping_known_count"] == 3
    assert diagnostics["visible_card_identity_mapping_unknown_count"] == 0
    assert "visible_card_identity_ids" not in diagnostics
    assert "visible_card_identity_names" not in diagnostics


def test_status_export_preserves_card_identity_review_items_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V029_CARD_IDENTITY_REVIEW_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V029_CARD_IDENTITY_REVIEW_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.2.9"
    assert "card_reward" not in payload
    assert "character" not in payload
    assert diagnostics["card_identity_review_probe"] == "ids_revealed_for_review"
    assert diagnostics["card_identity_review_option_count"] == 3
    assert [item["position"] for item in diagnostics["card_identity_review_items"]] == [0, 1, 2]
    assert [item["deckseer_id"] for item in diagnostics["card_identity_review_items"]] == [
        "cloak_and_dagger",
        "bouncing_flask",
        "infinite_blades",
    ]
    assert all(item["deckseer_mapping_status"] == "known" for item in diagnostics["card_identity_review_items"])
    assert "selected_card" not in diagnostics
    assert "deck" not in diagnostics


def test_status_export_preserves_live_card_reward_run_state_compile_probe_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V0210_RUN_STATE_COMPILE_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V0210_RUN_STATE_COMPILE_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.2.10"
    assert "card_reward" not in payload
    assert "character" not in payload
    assert diagnostics["card_reward_live_export_probe"] == "run_state_symbols_compiled_not_exported"
    assert diagnostics["card_reward_live_export_required_field_count"] == 12
    assert diagnostics["card_reward_live_export_writes_recommendation_state"] is False
    assert "character" in diagnostics["card_reward_live_export_required_fields"]
    assert "hp.current" in diagnostics["card_reward_live_export_required_fields"]
    assert "deck.upgraded" in diagnostics["card_reward_live_export_required_fields"]
    assert any(symbol.endswith("SerializablePlayer.CurrentHp") for symbol in diagnostics["card_reward_live_export_verified_symbols"])
    assert any(symbol.endswith("SerializablePlayer.Deck") for symbol in diagnostics["card_reward_live_export_verified_symbols"])
    assert diagnostics["card_identity_review_items"] == []


def test_status_export_preserves_run_state_runtime_readiness_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V0211_RUN_STATE_RUNTIME_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V0211_RUN_STATE_RUNTIME_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.2.11"
    assert "card_reward" not in payload
    assert "character" not in payload
    assert diagnostics["card_reward_run_state_runtime_probe"] == "run_state_seen"
    assert diagnostics["card_reward_run_state_run_in_progress"] is True
    assert diagnostics["card_reward_run_state_player_count"] == 1
    assert diagnostics["card_reward_run_state_single_player_available"] is True
    assert diagnostics["card_reward_run_state_character_present"] is True
    assert diagnostics["card_reward_run_state_hp_present"] is True
    assert diagnostics["card_reward_run_state_deck_card_count"] == 7
    assert diagnostics["card_reward_run_state_deck_card_mapping_unknown_count"] == 0
    assert diagnostics["card_reward_run_state_visible_reward_player_present"] is True
    assert diagnostics["card_reward_run_state_writes_recommendation_state"] is False
    assert "character_id" not in diagnostics
    assert "hp_current" not in diagnostics
    assert "gold" not in diagnostics
    assert "deck_card_ids" not in diagnostics


def test_status_export_preserves_deck_identity_review_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V0212_DECK_IDENTITY_REVIEW_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V0212_DECK_IDENTITY_REVIEW_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.2.12"
    assert "card_reward" not in payload
    assert "deck" not in payload
    assert "character" not in payload
    assert diagnostics["deck_identity_review_probe"] == "ids_revealed_for_review"
    assert diagnostics["deck_identity_review_card_count"] == 4
    assert diagnostics["deck_identity_review_unique_card_count"] == 3
    assert diagnostics["deck_identity_review_mapping_known_count"] == 2
    assert diagnostics["deck_identity_review_mapping_unknown_count"] == 2
    assert diagnostics["card_reward_run_state_writes_recommendation_state"] is False
    assert diagnostics["deck_identity_review_error"] is None
    assert diagnostics["deck_identity_review_items"][0]["public_model_id"] == "CLOAK_AND_DAGGER"
    assert diagnostics["deck_identity_review_items"][0]["deckseer_id"] == "cloak_and_dagger"
    assert diagnostics["deck_identity_review_items"][1]["deckseer_mapping_status"] == "unknown"
    assert diagnostics["deck_identity_review_items"][1]["upgraded"] is True
    assert diagnostics["deck_identity_review_items"][2]["deckseer_mapping_status"] == "unknown"
    assert "hp_current" not in diagnostics
    assert "gold" not in diagnostics
    assert "relic_ids" not in diagnostics
    assert "potion_ids" not in diagnostics


def test_status_export_preserves_reviewed_deck_identity_aliases_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V0213_DECK_IDENTITY_ALIAS_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V0213_DECK_IDENTITY_ALIAS_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]
    items_by_public_id = {item["public_model_id"]: item for item in diagnostics["deck_identity_review_items"]}

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.2.13"
    assert "card_reward" not in payload
    assert "deck" not in payload
    assert "character" not in payload
    assert diagnostics["deck_identity_review_mapping_known_count"] == 13
    assert diagnostics["deck_identity_review_mapping_unknown_count"] == 1
    assert diagnostics["card_reward_run_state_deck_card_mapping_known_count"] == 13
    assert diagnostics["card_reward_run_state_deck_card_mapping_unknown_count"] == 1
    assert items_by_public_id["STRIKE_SILENT"]["normalized_candidate_id"] == "strike_silent"
    assert items_by_public_id["STRIKE_SILENT"]["deckseer_mapping_status"] == "known"
    assert items_by_public_id["STRIKE_SILENT"]["deckseer_id"] == "strike"
    assert items_by_public_id["DEFEND_SILENT"]["normalized_candidate_id"] == "defend_silent"
    assert items_by_public_id["DEFEND_SILENT"]["deckseer_mapping_status"] == "known"
    assert items_by_public_id["DEFEND_SILENT"]["deckseer_id"] == "defend"
    assert items_by_public_id["DRAMATIC_ENTRANCE"]["deckseer_mapping_status"] == "unknown"
    assert items_by_public_id["DRAMATIC_ENTRANCE"]["deckseer_id"] is None
    assert diagnostics["card_reward_run_state_writes_recommendation_state"] is False
    assert "hp_current" not in diagnostics
    assert "gold" not in diagnostics
    assert "relic_ids" not in diagnostics
    assert "potion_ids" not in diagnostics


def test_status_export_preserves_reviewed_dramatic_entrance_mapping_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V0214_DRAMATIC_ENTRANCE_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V0214_DRAMATIC_ENTRANCE_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]
    item = diagnostics["deck_identity_review_items"][0]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.2.14"
    assert "card_reward" not in payload
    assert "deck" not in payload
    assert "character" not in payload
    assert diagnostics["deck_identity_review_mapping_known_count"] == 1
    assert diagnostics["deck_identity_review_mapping_unknown_count"] == 0
    assert diagnostics["card_reward_run_state_deck_card_mapping_known_count"] == 1
    assert diagnostics["card_reward_run_state_deck_card_mapping_unknown_count"] == 0
    assert item["public_model_id"] == "DRAMATIC_ENTRANCE"
    assert item["normalized_candidate_id"] == "dramatic_entrance"
    assert item["deckseer_mapping_status"] == "known"
    assert item["deckseer_id"] == "dramatic_entrance"
    assert diagnostics["card_reward_run_state_writes_recommendation_state"] is False


def test_status_export_preserves_live_export_candidate_refusal_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V0215_LIVE_EXPORT_CANDIDATE_REFUSAL_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V0215_LIVE_EXPORT_CANDIDATE_REFUSAL_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.2.15"
    assert "card_reward" not in payload
    assert "deck" not in payload
    assert "character" not in payload
    assert diagnostics["card_reward_live_export_candidate"] == "refused"
    assert diagnostics["card_reward_live_export_refusal_reasons"] == ["unmapped_relic"]
    assert diagnostics["card_reward_live_export_missing_fields"] == []
    assert diagnostics["card_reward_live_export_unmapped_reward_count"] == 0
    assert diagnostics["card_reward_live_export_unmapped_deck_count"] == 0
    assert diagnostics["card_reward_live_export_unmapped_relic_count"] == 2
    assert diagnostics["card_reward_live_export_unmapped_potion_count"] == 0
    assert diagnostics["card_reward_live_export_writes_recommendation_state"] is False
    assert diagnostics["card_reward_live_export_candidate_writes_recommendation_state"] is False
    assert "hp_current" not in diagnostics
    assert "gold" not in diagnostics
    assert "relic_ids" not in diagnostics
    assert "potion_ids" not in diagnostics


def test_status_export_preserves_relic_potion_identity_review_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V0216_RELIC_POTION_IDENTITY_REVIEW_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V0216_RELIC_POTION_IDENTITY_REVIEW_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.2.16"
    assert "card_reward" not in payload
    assert "deck" not in payload
    assert "character" not in payload
    assert diagnostics["relic_potion_identity_review_probe"] == "ids_revealed_for_review"
    assert diagnostics["relic_identity_review_count"] == 2
    assert diagnostics["relic_identity_review_mapping_known_count"] == 1
    assert diagnostics["relic_identity_review_mapping_unknown_count"] == 1
    assert diagnostics["potion_identity_review_count"] == 1
    assert diagnostics["potion_identity_review_mapping_known_count"] == 1
    assert diagnostics["potion_identity_review_mapping_unknown_count"] == 0
    assert diagnostics["relic_identity_review_items"][0]["public_model_id"] == "AKABEKO"
    assert diagnostics["relic_identity_review_items"][0]["deckseer_id"] == "akabeko"
    assert diagnostics["relic_identity_review_items"][1]["deckseer_mapping_status"] == "unknown"
    assert diagnostics["potion_identity_review_items"][0]["deckseer_id"] == "fire_potion"
    assert diagnostics["card_reward_live_export_refusal_reasons"] == ["unmapped_relic"]
    assert diagnostics["card_reward_live_export_unmapped_relic_count"] == 1
    assert diagnostics["card_reward_live_export_unmapped_potion_count"] == 0
    assert diagnostics["card_reward_live_export_candidate_writes_recommendation_state"] is False
    assert "hp_current" not in diagnostics
    assert "gold" not in diagnostics
    assert "relics" not in payload
    assert "potions" not in payload


def test_status_export_preserves_post_pickup_freshness_probe_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V032_POST_PICKUP_FRESHNESS_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V032_POST_PICKUP_FRESHNESS_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.3.2"
    assert "card_reward" not in payload
    assert "deck" not in payload
    assert "character" not in payload
    assert "gold" not in payload
    assert "hp" not in payload
    assert "potions" not in payload
    assert diagnostics["visible_reward_probe_status"] == "card_choice_screen_seen"
    assert diagnostics["visible_card_choice_option_count"] == 3
    assert diagnostics["card_reward_run_state_runtime_probe"] == "serializable_run_seen"
    assert diagnostics["card_reward_run_state_available"] is False
    assert diagnostics["card_reward_run_state_serializable_run_available"] is True
    assert diagnostics["card_reward_run_state_gold_present"] is True
    assert diagnostics["card_reward_run_state_potions_present"] is True
    assert diagnostics["card_reward_run_state_potion_count"] == 1
    assert diagnostics["card_reward_live_export_candidate"] == "refused"
    assert diagnostics["card_reward_live_export_refusal_reasons"] == [
        "no_visible_reward",
        "missing_required_run_state_field",
    ]
    assert diagnostics["card_reward_live_export_candidate_writes_recommendation_state"] is False
    assert "gold_value" not in diagnostics
    assert "hp_current" not in diagnostics
    assert "potion_ids" not in diagnostics


def test_status_export_preserves_reward_collected_freshness_probe_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V033_REWARD_COLLECTED_FRESHNESS_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V033_REWARD_COLLECTED_FRESHNESS_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.3.3"
    assert "card_reward" not in payload
    assert "gold" not in payload
    assert "hp" not in payload
    assert "potions" not in payload
    assert any(
        symbol.endswith("NRewardsScreen.RewardCollectedFrom")
        for symbol in diagnostics["screen_observation_verified_symbols"]
    )
    assert diagnostics["visible_reward_probe_status"] == "card_reward_model_seen"
    assert diagnostics["visible_reward_probe_last_event"] == "reward_collected"
    assert diagnostics["card_reward_run_state_runtime_probe"] == "serializable_run_seen"
    assert diagnostics["card_reward_run_state_available"] is False
    assert diagnostics["card_reward_run_state_serializable_run_available"] is True
    assert diagnostics["card_reward_run_state_potion_count"] == 1
    assert diagnostics["card_reward_live_export_candidate"] == "refused"
    assert diagnostics["card_reward_live_export_refusal_reasons"] == [
        "mixed_reward_screen_state_may_change",
        "missing_required_run_state_field",
        "unmapped_potion",
    ]
    assert diagnostics["card_reward_live_export_candidate_writes_recommendation_state"] is False
    assert "gold_value" not in diagnostics
    assert "hp_current" not in diagnostics
    assert "potion_ids" not in diagnostics


def test_status_export_preserves_mixed_reward_readiness_contract_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V034_MIXED_REWARD_READINESS_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V034_MIXED_REWARD_READINESS_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.3.4"
    assert "card_reward" not in payload
    assert "gold" not in payload
    assert "hp" not in payload
    assert "potions" not in payload
    assert diagnostics["visible_reward_probe_last_event"] == "reward_collected"
    assert diagnostics["card_reward_run_state_runtime_probe"] == "serializable_run_seen"
    assert diagnostics["card_reward_run_state_serializable_run_available"] is True
    assert diagnostics["card_reward_live_export_mixed_reward_freshness_status"] == (
        "reward_collected_serializable_counts_seen"
    )
    assert diagnostics["card_reward_live_export_mixed_reward_freshness_blockers"] == [
        "run_state_not_aligned",
        "visible_reward_player_not_aligned",
        "potion_identity_not_mapped_after_refresh",
        "mixed_reward_live_export_not_approved",
    ]
    assert diagnostics["card_reward_live_export_mixed_reward_freshness_writes_recommendation_state"] is False
    assert diagnostics["card_reward_live_export_candidate"] == "refused"
    assert diagnostics["card_reward_live_export_candidate_writes_recommendation_state"] is False
    assert "gold_value" not in diagnostics
    assert "hp_current" not in diagnostics
    assert "potion_ids" not in diagnostics


def test_status_export_preserves_reward_collected_potion_identity_review_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V035_REWARD_COLLECTED_POTION_IDENTITY_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V035_REWARD_COLLECTED_POTION_IDENTITY_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.3.5"
    assert "card_reward" not in payload
    assert "gold" not in payload
    assert "hp" not in payload
    assert "potions" not in payload
    assert diagnostics["visible_reward_probe_last_event"] == "reward_collected"
    assert diagnostics["relic_potion_identity_review_probe"] == "ids_revealed_for_review"
    assert diagnostics["relic_potion_identity_review_last_event"] == "reward_collected"
    assert diagnostics["potion_identity_review_count"] == 1
    assert diagnostics["potion_identity_review_mapping_unknown_count"] == 1
    assert diagnostics["potion_identity_review_items"][0]["public_model_id"] == "COLORLESS_POTION"
    assert diagnostics["potion_identity_review_items"][0]["normalized_candidate_id"] == "colorless_potion"
    assert diagnostics["potion_identity_review_items"][0]["deckseer_mapping_status"] == "unknown"
    assert diagnostics["potion_identity_review_items"][0]["deckseer_id"] is None
    assert diagnostics["card_reward_live_export_unmapped_potion_count"] == 1
    assert diagnostics["card_reward_live_export_mixed_reward_freshness_blockers"] == [
        "run_state_not_aligned",
        "visible_reward_player_not_aligned",
        "potion_identity_not_mapped_after_refresh",
        "mixed_reward_live_export_not_approved",
    ]
    assert diagnostics["card_reward_live_export_candidate_writes_recommendation_state"] is False
    assert "gold_value" not in diagnostics
    assert "hp_current" not in diagnostics
    assert "potion_ids" not in diagnostics


def test_status_export_preserves_reviewed_colorless_potion_mapping_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V036_COLORLESS_POTION_MAPPING_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V036_COLORLESS_POTION_MAPPING_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.3.6"
    assert "card_reward" not in payload
    assert "gold" not in payload
    assert "hp" not in payload
    assert "potions" not in payload
    assert diagnostics["visible_reward_probe_last_event"] == "reward_collected"
    assert diagnostics["potion_identity_review_count"] == 1
    assert diagnostics["potion_identity_review_mapping_known_count"] == 1
    assert diagnostics["potion_identity_review_mapping_unknown_count"] == 0
    assert diagnostics["potion_identity_review_items"][0]["public_model_id"] == "COLORLESS_POTION"
    assert diagnostics["potion_identity_review_items"][0]["normalized_candidate_id"] == "colorless_potion"
    assert diagnostics["potion_identity_review_items"][0]["deckseer_mapping_status"] == "known"
    assert diagnostics["potion_identity_review_items"][0]["deckseer_id"] == "colorless_potion"
    assert diagnostics["card_reward_live_export_refusal_reasons"] == [
        "mixed_reward_screen_state_may_change",
        "missing_required_run_state_field",
    ]
    assert diagnostics["card_reward_live_export_unmapped_potion_count"] == 0
    assert diagnostics["card_reward_live_export_mixed_reward_freshness_blockers"] == [
        "run_state_not_aligned",
        "visible_reward_player_not_aligned",
        "mixed_reward_live_export_not_approved",
    ]
    assert diagnostics["card_reward_live_export_candidate_writes_recommendation_state"] is False
    assert "gold_value" not in diagnostics
    assert "hp_current" not in diagnostics
    assert "potion_ids" not in diagnostics


def test_status_export_preserves_reward_collected_visible_player_alignment_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V037_REWARD_COLLECTED_VISIBLE_PLAYER_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V037_REWARD_COLLECTED_VISIBLE_PLAYER_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.3.7"
    assert "card_reward" not in payload
    assert "gold" not in payload
    assert "hp" not in payload
    assert "potions" not in payload
    assert diagnostics["visible_reward_probe_last_event"] == "reward_collected"
    assert diagnostics["card_reward_run_state_runtime_probe"] == "serializable_run_seen"
    assert diagnostics["card_reward_run_state_available"] is False
    assert diagnostics["card_reward_run_state_visible_reward_player_present"] is True
    assert diagnostics["card_reward_live_export_missing_fields"] == ["run_state"]
    assert diagnostics["card_reward_live_export_mixed_reward_freshness_blockers"] == [
        "run_state_not_aligned",
        "mixed_reward_live_export_not_approved",
    ]
    assert diagnostics["card_reward_live_export_unmapped_potion_count"] == 0
    assert diagnostics["card_reward_live_export_candidate_writes_recommendation_state"] is False
    assert "visible_reward_player_id" not in diagnostics
    assert "gold_value" not in diagnostics
    assert "hp_current" not in diagnostics
    assert "potion_ids" not in diagnostics


def test_status_export_preserves_reward_collected_run_state_context_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V038_REWARD_COLLECTED_RUN_STATE_CONTEXT_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V038_REWARD_COLLECTED_RUN_STATE_CONTEXT_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.3.8"
    assert "card_reward" not in payload
    assert "gold" not in payload
    assert "hp" not in payload
    assert "potions" not in payload
    assert diagnostics["visible_reward_probe_last_event"] == "reward_collected"
    assert diagnostics["card_reward_run_state_runtime_probe"] == "run_state_seen"
    assert diagnostics["card_reward_run_state_available"] is True
    assert diagnostics["card_reward_run_state_serializable_run_available"] is True
    assert diagnostics["card_reward_run_state_visible_reward_player_present"] is True
    assert diagnostics["card_reward_live_export_refusal_reasons"] == ["mixed_reward_screen_state_may_change"]
    assert diagnostics["card_reward_live_export_missing_fields"] == []
    assert diagnostics["card_reward_live_export_mixed_reward_freshness_blockers"] == [
        "mixed_reward_live_export_not_approved"
    ]
    assert diagnostics["card_reward_live_export_unmapped_potion_count"] == 0
    assert diagnostics["card_reward_live_export_candidate_writes_recommendation_state"] is False
    assert "visible_reward_player_id" not in diagnostics
    assert "gold_value" not in diagnostics
    assert "hp_current" not in diagnostics
    assert "potion_ids" not in diagnostics


def test_status_export_clears_card_reward_selection_screen_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V0310_CARD_REWARD_SELECTION_CLOSED_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V0310_CARD_REWARD_SELECTION_CLOSED_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.3.10"
    assert "card_reward" not in payload
    assert "gold" not in payload
    assert "hp" not in payload
    assert "potions" not in payload
    assert diagnostics["visible_reward_probe_status"] == "reward_screen_completed"
    assert diagnostics["visible_reward_probe_last_event"] == "card_reward_selection_screen_closed"
    assert diagnostics["visible_card_reward_option_count"] == 0
    assert diagnostics["card_identity_review_items"] == []
    assert diagnostics["deck_identity_review_items"] == []
    assert diagnostics["relic_identity_review_items"] == []
    assert diagnostics["potion_identity_review_items"] == []
    assert diagnostics["card_reward_run_state_runtime_probe"] == "cleared"
    assert diagnostics["card_reward_live_export_candidate"] == "refused"
    assert diagnostics["card_reward_live_export_refusal_reasons"] == [
        "stale_reward_screen",
        "missing_required_run_state_field",
    ]
    assert diagnostics["card_reward_live_export_mixed_reward_freshness_status"] == "not_applicable"
    assert diagnostics["card_reward_live_export_candidate_writes_recommendation_state"] is False


def test_recommend_export_rejects_closed_card_reward_selection_status_even_when_confirmed(capsys) -> None:
    status = main(
        [
            "recommend-export",
            str(STATUS_V0310_CARD_REWARD_SELECTION_CLOSED_FIXTURE),
            "--confirmed",
            "--format",
            "text",
        ]
    )

    captured = capsys.readouterr()

    assert status == 2
    assert captured.out == ""
    assert "recommend-export only supports card_reward or relic_reward exports" in captured.err
    assert "got exporter_status" in captured.err


def test_status_export_clears_v047_card_reward_selection_screen_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V047_CARD_REWARD_SELECTION_CLOSED_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V047_CARD_REWARD_SELECTION_CLOSED_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.7"
    assert "card_reward" not in payload
    assert "gold" not in payload
    assert "hp" not in payload
    assert "potions" not in payload
    assert diagnostics["visible_reward_probe_status"] == "reward_screen_completed"
    assert diagnostics["visible_reward_probe_last_event"] == "card_reward_selection_screen_closed"
    assert diagnostics["visible_card_reward_option_count"] == 0
    assert diagnostics["card_identity_review_probe"] == "cleared"
    assert diagnostics["card_identity_review_items"] == []
    assert diagnostics["deck_identity_review_items"] == []
    assert diagnostics["relic_identity_review_items"] == []
    assert diagnostics["potion_identity_review_items"] == []
    assert diagnostics["card_reward_run_state_runtime_probe"] == "cleared"
    assert diagnostics["card_reward_live_export_candidate"] == "refused"
    assert diagnostics["card_reward_live_export_refusal_reasons"] == [
        "stale_reward_screen",
        "missing_required_run_state_field",
    ]
    assert diagnostics["card_reward_live_export_mixed_reward_freshness_status"] == "not_applicable"
    assert diagnostics["card_reward_live_export_candidate_writes_recommendation_state"] is False


def test_recommend_export_rejects_v047_card_reward_selection_closed_status_even_when_confirmed(capsys) -> None:
    status = main(
        [
            "recommend-export",
            str(STATUS_V047_CARD_REWARD_SELECTION_CLOSED_FIXTURE),
            "--confirmed",
            "--format",
            "text",
        ]
    )

    captured = capsys.readouterr()

    assert status == 2
    assert captured.out == ""
    assert "recommend-export only supports card_reward or relic_reward exports" in captured.err
    assert "got exporter_status" in captured.err


def test_status_export_clears_relic_reward_screen_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V040_RELIC_REWARD_CLOSED_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V040_RELIC_REWARD_CLOSED_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.0"
    assert "relic_reward" not in payload
    assert "gold" not in payload
    assert "hp" not in payload
    assert "potions" not in payload
    assert diagnostics["visible_reward_probe_status"] == "reward_screen_completed"
    assert diagnostics["visible_reward_probe_last_event"] == "reward_collected"
    assert diagnostics["visible_relic_reward_option_count"] == 0
    assert diagnostics["relic_reward_identity_review_items"] == []
    assert diagnostics["deck_identity_review_items"] == []
    assert diagnostics["relic_identity_review_items"] == []
    assert diagnostics["potion_identity_review_items"] == []
    assert diagnostics["card_reward_run_state_runtime_probe"] == "cleared"
    assert diagnostics["relic_reward_live_export_candidate"] == "refused"
    assert diagnostics["relic_reward_live_export_refusal_reasons"] == [
        "stale_reward_screen",
        "missing_required_run_state_field",
    ]
    assert diagnostics["relic_reward_live_export_candidate_writes_recommendation_state"] is False


def test_recommend_export_rejects_closed_relic_reward_status_even_when_confirmed(capsys) -> None:
    status = main(
        [
            "recommend-export",
            str(STATUS_V040_RELIC_REWARD_CLOSED_FIXTURE),
            "--confirmed",
            "--format",
            "text",
        ]
    )

    captured = capsys.readouterr()

    assert status == 2
    assert captured.out == ""
    assert "recommend-export only supports card_reward or relic_reward exports" in captured.err
    assert "got exporter_status" in captured.err


def test_status_export_reports_treasure_relic_route_as_status_only(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V041_TREASURE_RELIC_ROUTE_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V041_TREASURE_RELIC_ROUTE_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.1"
    assert "relic_reward" not in payload
    assert diagnostics["visible_reward_probe_status"] == "treasure_relic_model_seen"
    assert diagnostics["visible_reward_probe_last_event"] == "treasure_relic_holder_initialized"
    assert diagnostics["visible_relic_reward_option_count"] == 1
    assert diagnostics["relic_reward_live_export_candidate"] == "refused"
    assert diagnostics["relic_reward_live_export_refusal_reasons"] == [
        "treasure_relic_route_status_only"
    ]
    assert diagnostics["relic_reward_live_export_candidate_writes_recommendation_state"] is False
    assert diagnostics["relic_reward_identity_review_option_count"] == 1
    assert diagnostics["relic_reward_identity_review_mapping_known_count"] == 1
    assert diagnostics["relic_reward_identity_review_items"][0]["deckseer_id"] == "akabeko"


def test_recommend_export_rejects_treasure_relic_status_even_when_confirmed(capsys) -> None:
    status = main(
        [
            "recommend-export",
            str(STATUS_V041_TREASURE_RELIC_ROUTE_FIXTURE),
            "--confirmed",
            "--format",
            "text",
        ]
    )

    captured = capsys.readouterr()

    assert status == 2
    assert captured.out == ""
    assert "recommend-export only supports card_reward or relic_reward exports" in captured.err
    assert "got exporter_status" in captured.err


def test_status_export_reports_treasure_relic_identity_after_canonical_fix(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V042_TREASURE_RELIC_IDENTITY_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V042_TREASURE_RELIC_IDENTITY_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.2"
    assert "MegaCrit.Sts2.Core.Models.RelicModel.CanonicalInstance" in diagnostics["screen_observation_verified_symbols"]
    assert diagnostics["visible_reward_probe_status"] == "treasure_relic_model_seen"
    assert diagnostics["relic_reward_live_export_refusal_reasons"] == [
        "treasure_relic_route_status_only"
    ]
    assert diagnostics["relic_reward_identity_review_probe"] == "ids_revealed_for_review"
    assert diagnostics["relic_reward_identity_review_error"] is None
    assert diagnostics["relic_reward_identity_review_items"][0]["deckseer_id"] == "akabeko"


def test_status_export_reports_treasure_relic_identity_from_model_id(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V043_TREASURE_RELIC_MODEL_ID_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V043_TREASURE_RELIC_MODEL_ID_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.3"
    assert "MegaCrit.Sts2.Core.Models.RelicModel.Id" in diagnostics["screen_observation_verified_symbols"]
    assert diagnostics["visible_reward_probe_status"] == "treasure_relic_model_seen"
    assert diagnostics["relic_reward_live_export_refusal_reasons"] == [
        "treasure_relic_route_status_only"
    ]
    assert diagnostics["relic_reward_live_export_candidate_writes_recommendation_state"] is False
    assert diagnostics["relic_reward_identity_review_probe"] == "ids_revealed_for_review"
    assert diagnostics["relic_reward_identity_review_mapping_known_count"] == 1
    assert diagnostics["relic_reward_identity_review_items"][0]["public_model_id"] == "AKABEKO"
    assert diagnostics["relic_reward_identity_review_items"][0]["deckseer_id"] == "akabeko"


def test_status_export_maps_reviewed_letter_opener_treasure_relic(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V044_TREASURE_RELIC_LETTER_OPENER_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V044_TREASURE_RELIC_LETTER_OPENER_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.4"
    assert diagnostics["visible_reward_probe_status"] == "treasure_relic_model_seen"
    assert diagnostics["relic_reward_live_export_refusal_reasons"] == [
        "treasure_relic_route_status_only"
    ]
    assert diagnostics["relic_reward_live_export_candidate_writes_recommendation_state"] is False
    assert diagnostics["relic_reward_identity_review_probe"] == "ids_revealed_for_review"
    assert diagnostics["relic_reward_identity_review_mapping_known_count"] == 1
    assert diagnostics["relic_reward_identity_review_mapping_unknown_count"] == 0
    assert diagnostics["relic_reward_identity_review_items"][0]["public_model_id"] == "LETTER_OPENER"
    assert diagnostics["relic_reward_identity_review_items"][0]["deckseer_id"] == "letter_opener"


def test_inspect_export_accepts_live_v045_treasure_relic_fixture(capsys) -> None:
    status = main(["inspect-export", str(LIVE_RELIC_V045_TREASURE_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["source_type"] == "deckseer_exporter_mod"
    assert payload["screen_type"] == "relic_reward"
    assert payload["exporter_version"] == "0.4.5"
    assert payload["requires_user_confirmation"] is True
    assert payload["character"] == "silent"
    assert payload["relic_reward"] == ["letter_opener"]
    assert payload["valid"] is True


def test_recommend_export_requires_confirmation_for_live_v045_treasure_relic_fixture(capsys) -> None:
    status = main(["recommend-export", str(LIVE_RELIC_V045_TREASURE_FIXTURE)])

    captured = capsys.readouterr()

    assert status == 2
    assert captured.out == ""
    assert "run inspect-export, verify the visible state" in captured.err
    assert "--confirmed" in captured.err


def test_recommend_export_cli_scores_live_v045_treasure_relic_fixture_when_confirmed(capsys) -> None:
    status = main(["recommend-export", str(LIVE_RELIC_V045_TREASURE_FIXTURE), "--confirmed"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["recommendation_type"] == "relic_choice"
    assert payload["ranked_choices"][0]["choice"] == "letter_opener"


def test_recommend_export_cli_scores_live_v046_mapped_treasure_fixture_when_confirmed(capsys) -> None:
    inspect_status = main(["inspect-export", str(LIVE_RELIC_V046_TREASURE_MAPPED_FIXTURE)])
    captured = capsys.readouterr()
    inspected = json.loads(captured.out)

    assert inspect_status == 0
    assert inspected["screen_type"] == "relic_reward"
    assert inspected["exporter_version"] == "0.4.6"
    assert inspected["requires_user_confirmation"] is True
    assert inspected["valid"] is True

    unconfirmed_status = main(["recommend-export", str(LIVE_RELIC_V046_TREASURE_MAPPED_FIXTURE)])
    captured = capsys.readouterr()

    assert unconfirmed_status == 2
    assert captured.out == ""
    assert "--confirmed" in captured.err

    status = main(["recommend-export", str(LIVE_RELIC_V046_TREASURE_MAPPED_FIXTURE), "--confirmed"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["recommendation_type"] == "relic_choice"
    assert payload["ranked_choices"][0]["choice"] == "letter_opener"


def test_recommend_export_cli_scores_live_v047_mapped_card_reward_fixture_when_confirmed(capsys) -> None:
    inspect_status = main(["inspect-export", str(LIVE_V047_MIXED_REWARD_MAPPED_FIXTURE)])
    captured = capsys.readouterr()
    inspected = json.loads(captured.out)

    assert inspect_status == 0
    assert inspected["screen_type"] == "card_reward"
    assert inspected["exporter_version"] == "0.4.7"
    assert inspected["requires_user_confirmation"] is True
    assert inspected["valid"] is True
    assert inspected["character"] == "silent"
    assert inspected["card_reward"] == ["envenom", "predator", "memento_mori"]

    unconfirmed_status = main(["recommend-export", str(LIVE_V047_MIXED_REWARD_MAPPED_FIXTURE)])
    captured = capsys.readouterr()

    assert unconfirmed_status == 2
    assert captured.out == ""
    assert "--confirmed" in captured.err

    status = main(["recommend-export", str(LIVE_V047_MIXED_REWARD_MAPPED_FIXTURE), "--confirmed"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["recommendation_type"] == "card_reward"
    assert payload["ranked_choices"][0]["choice"] == "envenom"
    assert payload["ranked_choices"][1]["choice"] == "skip"
    assert payload["ranked_choices"][2]["choice"] == "predator"


@pytest.mark.parametrize("fixture", STATUS_V047_EVENT_SPECIAL_ROUTE_FIXTURES)
def test_v047_event_special_route_fixtures_remain_status_only(fixture: Path, capsys) -> None:
    status = main(["inspect-export", str(fixture)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(fixture)
    diagnostics = inspected.metadata["diagnostics"]
    route = diagnostics["event_special_route"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert inspected.metadata["requires_user_confirmation"] is False
    assert diagnostics["event_special_route_writes_recommendation_state"] is False
    assert route["exports_recommendation_state"] is False

    forbidden_top_level = {
        "character",
        "act",
        "floor",
        "ascension",
        "gold",
        "hp",
        "deck",
        "relics",
        "potions",
        "card_reward",
        "relic_reward",
    }
    assert forbidden_top_level.isdisjoint(payload)

    forbidden_route_identity_keys = {
        "option_ids",
        "option_names",
        "option_titles",
        "option_descriptions",
        "option_text",
        "selected_option",
        "selected_outcome",
        "selected_card",
        "selected_relic",
        "enchantment_id",
        "enchantment_name",
        "prompt_text",
    }
    assert _find_forbidden_keys(route, forbidden_route_identity_keys) == []

    recommendation_status = main(["recommend-export", str(fixture), "--confirmed", "--format", "text"])
    recommendation_output = capsys.readouterr()

    assert recommendation_status == 2
    assert recommendation_output.out == ""
    assert "got exporter_status" in recommendation_output.err


def test_status_export_preserves_v047_event_special_route_startup_diagnostics(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V047_EVENT_SPECIAL_ROUTE_STARTUP_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V047_EVENT_SPECIAL_ROUTE_STARTUP_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]
    route = diagnostics["event_special_route"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.7"
    assert "card_reward" not in payload
    assert "relic_reward" not in payload
    assert "character" not in payload
    assert diagnostics["event_special_route_compile_probe"] == "compiled_not_registered"
    assert diagnostics["event_special_route_verified_symbol_count"] == 25
    assert diagnostics["screen_observation_verified_symbol_count"] == 25
    assert "MegaCrit.Sts2.Core.Nodes.Rooms.NEventRoom.Create" in diagnostics["event_special_route_verified_symbols"]
    assert "MegaCrit.Sts2.Core.Nodes.Events.NEventLayout.AddOptions" in diagnostics["screen_observation_verified_symbols"]
    assert route == {
        "probe_status": "not_observed",
        "last_event": "startup",
        "active": False,
        "route_family": None,
        "route_label": None,
        "observation_source": "public_event_route_classifier",
        "visible_option_count": 0,
        "clear_state": "cleared",
        "exports_recommendation_state": False,
        "blockers": [],
        "error": None,
    }
    assert "option_ids" not in route
    assert "option_names" not in route
    assert "selected_option" not in route


def test_recommend_export_rejects_v047_event_special_route_status_even_when_confirmed(capsys) -> None:
    status = main(
        [
            "recommend-export",
            str(STATUS_V047_EVENT_SPECIAL_ROUTE_STARTUP_FIXTURE),
            "--confirmed",
            "--format",
            "text",
        ]
    )

    captured = capsys.readouterr()

    assert status == 2
    assert captured.out == ""
    assert "recommend-export only supports card_reward or relic_reward exports" in captured.err
    assert "got exporter_status" in captured.err


def test_status_export_preserves_v047_event_special_route_map_clear_startup_diagnostics(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V047_EVENT_SPECIAL_ROUTE_MAP_CLEAR_STARTUP_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V047_EVENT_SPECIAL_ROUTE_MAP_CLEAR_STARTUP_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]
    route = diagnostics["event_special_route"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.7"
    assert "card_reward" not in payload
    assert "relic_reward" not in payload
    assert "character" not in payload
    assert diagnostics["event_special_route_compile_probe"] == "compiled_not_registered"
    assert diagnostics["event_special_route_verified_symbol_count"] == 26
    assert diagnostics["screen_observation_verified_symbol_count"] == 26
    assert (
        "MegaCrit.Sts2.Core.Nodes.Screens.Map.NMapScreen.Open"
        in diagnostics["event_special_route_verified_symbols"]
    )
    assert (
        "MegaCrit.Sts2.Core.Nodes.Screens.Map.NMapScreen.Open"
        in diagnostics["screen_observation_verified_symbols"]
    )
    assert route == {
        "probe_status": "not_observed",
        "last_event": "startup",
        "active": False,
        "route_family": None,
        "route_label": None,
        "observation_source": "public_event_route_classifier",
        "visible_option_count": 0,
        "clear_state": "cleared",
        "exports_recommendation_state": False,
        "blockers": [],
        "error": None,
    }
    assert "option_ids" not in route
    assert "option_names" not in route
    assert "selected_option" not in route


def test_status_export_preserves_v047_event_special_route_map_cleared_diagnostics(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V047_EVENT_SPECIAL_ROUTE_MAP_CLEARED_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V047_EVENT_SPECIAL_ROUTE_MAP_CLEARED_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]
    route = diagnostics["event_special_route"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.7"
    assert "card_reward" not in payload
    assert "relic_reward" not in payload
    assert "character" not in payload
    assert diagnostics["event_special_route_compile_probe"] == "compiled_not_registered"
    assert diagnostics["event_special_route_verified_symbol_count"] == 26
    assert diagnostics["screen_observation_verified_symbol_count"] == 26
    assert route == {
        "probe_status": "cleared",
        "last_event": "map_screen_opened",
        "active": False,
        "route_family": None,
        "route_label": None,
        "observation_source": "public_event_route_classifier",
        "visible_option_count": 0,
        "clear_state": "cleared",
        "exports_recommendation_state": False,
        "blockers": [],
        "error": None,
    }
    assert "option_ids" not in route
    assert "option_names" not in route
    assert "selected_option" not in route


def test_status_export_preserves_v047_event_special_route_overlay_startup_diagnostics(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V047_EVENT_SPECIAL_ROUTE_OVERLAY_STARTUP_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V047_EVENT_SPECIAL_ROUTE_OVERLAY_STARTUP_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]
    route = diagnostics["event_special_route"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.7"
    assert "card_reward" not in payload
    assert "relic_reward" not in payload
    assert "character" not in payload
    assert diagnostics["event_special_route_compile_probe"] == "compiled_not_registered"
    assert diagnostics["event_special_route_verified_symbol_count"] == 30
    assert diagnostics["screen_observation_verified_symbol_count"] == 30
    assert (
        "MegaCrit.Sts2.Core.Nodes.Screens.NChooseARelicSelection.ShowScreen"
        in diagnostics["event_special_route_verified_symbols"]
    )
    assert (
        "MegaCrit.Sts2.Core.Nodes.Screens.NChooseARelicSelection._ExitTree"
        in diagnostics["event_special_route_verified_symbols"]
    )
    assert (
        "MegaCrit.Sts2.Core.Nodes.Screens.CardSelection.NChooseABundleSelectionScreen.ShowScreen"
        in diagnostics["screen_observation_verified_symbols"]
    )
    assert (
        "MegaCrit.Sts2.Core.Nodes.Screens.CardSelection.NChooseABundleSelectionScreen._ExitTree"
        in diagnostics["screen_observation_verified_symbols"]
    )
    assert route == {
        "probe_status": "not_observed",
        "last_event": "startup",
        "active": False,
        "route_family": None,
        "route_label": None,
        "observation_source": "public_event_route_classifier",
        "visible_option_count": 0,
        "clear_state": "cleared",
        "exports_recommendation_state": False,
        "blockers": [],
        "error": None,
    }
    assert "option_ids" not in route
    assert "option_names" not in route
    assert "selected_option" not in route


def test_status_export_preserves_v047_event_special_route_bundle_active_diagnostics(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V047_EVENT_SPECIAL_ROUTE_BUNDLE_ACTIVE_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V047_EVENT_SPECIAL_ROUTE_BUNDLE_ACTIVE_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]
    route = diagnostics["event_special_route"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.7"
    assert "card_reward" not in payload
    assert "relic_reward" not in payload
    assert "character" not in payload
    assert diagnostics["event_special_route_verified_symbol_count"] == 30
    assert diagnostics["screen_observation_verified_symbol_count"] == 30
    assert route == {
        "probe_status": "event_special_route_seen",
        "last_event": "choose_bundle_selection_screen_shown",
        "active": True,
        "route_family": "event_special_choice",
        "route_label": None,
        "observation_source": "public_choose_bundle_selection_screen",
        "visible_option_count": 2,
        "clear_state": "active",
        "exports_recommendation_state": False,
        "blockers": ["event_special_route_status_only"],
        "error": None,
    }
    assert diagnostics["visible_reward_probe_status"] == "reward_screen_completed"
    assert diagnostics["card_reward_live_export_candidate"] == "refused"
    assert diagnostics["card_reward_live_export_candidate_writes_recommendation_state"] is False
    assert "option_ids" not in route
    assert "option_names" not in route
    assert "selected_option" not in route


def test_status_export_preserves_v047_event_special_route_ranwid_relic_active_diagnostics(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V047_EVENT_SPECIAL_ROUTE_RANWID_RELIC_ACTIVE_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V047_EVENT_SPECIAL_ROUTE_RANWID_RELIC_ACTIVE_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]
    route = diagnostics["event_special_route"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.7"
    assert "card_reward" not in payload
    assert "relic_reward" not in payload
    assert "character" not in payload
    assert diagnostics["event_special_route_verified_symbol_count"] == 30
    assert diagnostics["screen_observation_verified_symbol_count"] == 30
    assert route == {
        "probe_status": "event_special_route_seen",
        "last_event": "event_layout_options_added",
        "active": True,
        "route_family": "event_special_choice",
        "route_label": None,
        "observation_source": "public_event_layout_options",
        "visible_option_count": 3,
        "clear_state": "active",
        "exports_recommendation_state": False,
        "blockers": ["event_special_route_status_only"],
        "error": None,
    }
    assert diagnostics["visible_reward_probe_status"] == "reward_screen_completed"
    assert diagnostics["relic_reward_live_export_candidate"] == "refused"
    assert diagnostics["relic_reward_live_export_candidate_writes_recommendation_state"] is False
    assert "option_ids" not in route
    assert "option_names" not in route
    assert "selected_option" not in route


def test_status_export_preserves_v047_event_special_route_doll_room_relic_options_diagnostics(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V047_EVENT_SPECIAL_ROUTE_DOLL_ROOM_RELIC_OPTIONS_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V047_EVENT_SPECIAL_ROUTE_DOLL_ROOM_RELIC_OPTIONS_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]
    route = diagnostics["event_special_route"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.7"
    assert "card_reward" not in payload
    assert "relic_reward" not in payload
    assert "character" not in payload
    assert diagnostics["event_special_route_verified_symbol_count"] == 30
    assert diagnostics["screen_observation_verified_symbol_count"] == 30
    assert route == {
        "probe_status": "event_special_route_seen",
        "last_event": "event_layout_options_added",
        "active": True,
        "route_family": "event_special_choice",
        "route_label": None,
        "observation_source": "public_event_layout_options",
        "visible_option_count": 2,
        "clear_state": "active",
        "exports_recommendation_state": False,
        "blockers": ["event_special_route_status_only"],
        "error": None,
    }
    assert diagnostics["visible_reward_probe_status"] == "reward_screen_completed"
    assert diagnostics["relic_reward_live_export_candidate"] == "refused"
    assert diagnostics["relic_reward_live_export_candidate_writes_recommendation_state"] is False
    assert "option_ids" not in route
    assert "option_names" not in route
    assert "selected_option" not in route


def test_status_export_preserves_v047_event_special_route_vakuu_relic_options_diagnostics(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V047_EVENT_SPECIAL_ROUTE_VAKUU_RELIC_OPTIONS_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V047_EVENT_SPECIAL_ROUTE_VAKUU_RELIC_OPTIONS_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]
    route = diagnostics["event_special_route"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.7"
    assert "card_reward" not in payload
    assert "relic_reward" not in payload
    assert "character" not in payload
    assert diagnostics["event_special_route_verified_symbol_count"] == 30
    assert diagnostics["screen_observation_verified_symbol_count"] == 30
    assert route == {
        "probe_status": "event_special_route_seen",
        "last_event": "event_layout_options_added",
        "active": True,
        "route_family": "event_special_choice",
        "route_label": None,
        "observation_source": "public_event_layout_options",
        "visible_option_count": 3,
        "clear_state": "active",
        "exports_recommendation_state": False,
        "blockers": ["event_special_route_status_only"],
        "error": None,
    }
    assert diagnostics["visible_reward_probe_status"] == "reward_screen_completed"
    assert diagnostics["relic_reward_live_export_candidate"] == "refused"
    assert diagnostics["relic_reward_live_export_candidate_writes_recommendation_state"] is False
    assert "option_ids" not in route
    assert "option_names" not in route
    assert "selected_option" not in route


def test_status_export_preserves_v047_event_special_route_zen_weaver_active_diagnostics(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V047_EVENT_SPECIAL_ROUTE_ZEN_WEAVER_ACTIVE_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V047_EVENT_SPECIAL_ROUTE_ZEN_WEAVER_ACTIVE_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]
    route = diagnostics["event_special_route"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.7"
    assert "card_reward" not in payload
    assert "relic_reward" not in payload
    assert "character" not in payload
    assert diagnostics["event_special_route_verified_symbol_count"] == 30
    assert diagnostics["screen_observation_verified_symbol_count"] == 30
    assert route == {
        "probe_status": "event_special_route_seen",
        "last_event": "event_layout_options_added",
        "active": True,
        "route_family": "event_special_choice",
        "route_label": None,
        "observation_source": "public_event_layout_options",
        "visible_option_count": 3,
        "clear_state": "active",
        "exports_recommendation_state": False,
        "blockers": ["event_special_route_status_only"],
        "error": None,
    }
    assert diagnostics["visible_reward_probe_status"] == "reward_screen_completed"
    assert diagnostics["card_reward_live_export_candidate"] == "refused"
    assert diagnostics["card_reward_live_export_candidate_writes_recommendation_state"] is False
    assert "option_ids" not in route
    assert "option_names" not in route
    assert "selected_option" not in route


def test_status_export_preserves_v047_event_special_route_self_help_book_active_diagnostics(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V047_EVENT_SPECIAL_ROUTE_SELF_HELP_BOOK_ACTIVE_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V047_EVENT_SPECIAL_ROUTE_SELF_HELP_BOOK_ACTIVE_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]
    route = diagnostics["event_special_route"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.7"
    assert "card_reward" not in payload
    assert "relic_reward" not in payload
    assert "character" not in payload
    assert diagnostics["event_special_route_verified_symbol_count"] == 30
    assert diagnostics["screen_observation_verified_symbol_count"] == 30
    assert route == {
        "probe_status": "event_special_route_seen",
        "last_event": "event_layout_options_added",
        "active": True,
        "route_family": "event_special_choice",
        "route_label": None,
        "observation_source": "public_event_layout_options",
        "visible_option_count": 3,
        "clear_state": "active",
        "exports_recommendation_state": False,
        "blockers": ["event_special_route_status_only"],
        "error": None,
    }
    assert diagnostics["visible_reward_probe_status"] == "reward_screen_completed"
    assert diagnostics["card_reward_live_export_candidate"] == "refused"
    assert diagnostics["card_reward_live_export_candidate_writes_recommendation_state"] is False
    assert "option_ids" not in route
    assert "option_names" not in route
    assert "selected_option" not in route


def test_status_export_preserves_v047_event_special_route_self_help_book_card_select_diagnostics(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V047_EVENT_SPECIAL_ROUTE_SELF_HELP_BOOK_CARD_SELECT_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V047_EVENT_SPECIAL_ROUTE_SELF_HELP_BOOK_CARD_SELECT_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]
    route = diagnostics["event_special_route"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.7"
    assert "card_reward" not in payload
    assert "relic_reward" not in payload
    assert "character" not in payload
    assert diagnostics["event_special_route_verified_symbol_count"] == 30
    assert diagnostics["screen_observation_verified_symbol_count"] == 30
    assert route == {
        "probe_status": "event_special_options_cleared",
        "last_event": "event_layout_options_cleared",
        "active": True,
        "route_family": "event_special_choice",
        "route_label": None,
        "observation_source": "public_event_layout_options",
        "visible_option_count": 0,
        "clear_state": "unknown",
        "exports_recommendation_state": False,
        "blockers": ["event_special_route_status_only"],
        "error": None,
    }
    assert diagnostics["visible_reward_probe_status"] == "reward_screen_completed"
    assert diagnostics["visible_card_choice_option_count"] == 0
    assert diagnostics["card_identity_review_option_count"] == 0
    assert diagnostics["card_reward_live_export_candidate"] == "refused"
    assert diagnostics["card_reward_live_export_candidate_writes_recommendation_state"] is False
    assert "option_ids" not in route
    assert "option_names" not in route
    assert "selected_option" not in route


def test_status_export_preserves_v047_event_special_route_deck_enchant_active_diagnostics(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V047_EVENT_SPECIAL_ROUTE_DECK_ENCHANT_ACTIVE_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V047_EVENT_SPECIAL_ROUTE_DECK_ENCHANT_ACTIVE_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]
    route = diagnostics["event_special_route"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.7"
    assert "card_reward" not in payload
    assert "relic_reward" not in payload
    assert "character" not in payload
    assert diagnostics["event_special_route_verified_symbol_count"] == 33
    assert diagnostics["screen_observation_verified_symbol_count"] == 33
    assert (
        "MegaCrit.Sts2.Core.Nodes.Screens.CardSelection.NDeckEnchantSelectScreen.ShowScreen"
        in diagnostics["event_special_route_verified_symbols"]
    )
    assert (
        "MegaCrit.Sts2.Core.Nodes.Screens.CardSelection.NDeckEnchantSelectScreen.ShowScreen"
        in diagnostics["screen_observation_verified_symbols"]
    )
    assert route == {
        "probe_status": "event_special_route_seen",
        "last_event": "deck_enchant_selection_screen_shown",
        "active": True,
        "route_family": "post_event_card_choice",
        "route_label": "deck_enchant_card_select",
        "observation_source": "public_deck_enchant_selection_screen",
        "visible_option_count": 19,
        "clear_state": "active",
        "exports_recommendation_state": False,
        "blockers": ["event_special_route_status_only"],
        "error": None,
    }
    assert diagnostics["visible_card_choice_option_count"] == 0
    assert diagnostics["card_identity_review_option_count"] == 0
    assert diagnostics["card_reward_live_export_candidate"] == "refused"
    assert diagnostics["card_reward_live_export_candidate_writes_recommendation_state"] is False
    assert "option_ids" not in route
    assert "option_names" not in route
    assert "selected_option" not in route
    assert "card_ids" not in route
    assert "card_names" not in route
    assert "enchantment_id" not in route
    assert "enchantment_name" not in route


def test_status_export_preserves_v047_wood_carvings_deck_enchant_diagnostics(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V047_EVENT_SPECIAL_ROUTE_WOOD_CARVINGS_DECK_ENCHANT_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V047_EVENT_SPECIAL_ROUTE_WOOD_CARVINGS_DECK_ENCHANT_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]
    route = diagnostics["event_special_route"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.7"
    assert "card_reward" not in payload
    assert "relic_reward" not in payload
    assert "character" not in payload
    assert route == {
        "probe_status": "event_special_route_seen",
        "last_event": "deck_enchant_selection_screen_shown",
        "active": True,
        "route_family": "post_event_card_choice",
        "route_label": "deck_enchant_card_select",
        "observation_source": "public_deck_enchant_selection_screen",
        "visible_option_count": 12,
        "clear_state": "active",
        "exports_recommendation_state": False,
        "blockers": ["event_special_route_status_only"],
        "error": None,
    }
    assert diagnostics["visible_card_choice_option_count"] == 0
    assert diagnostics["card_identity_review_option_count"] == 0
    assert diagnostics["card_reward_live_export_candidate"] == "refused"
    assert diagnostics["card_reward_live_export_candidate_writes_recommendation_state"] is False
    assert "option_ids" not in route
    assert "option_names" not in route
    assert "selected_option" not in route
    assert "card_ids" not in route
    assert "card_names" not in route
    assert "enchantment_id" not in route
    assert "enchantment_name" not in route


def test_status_export_preserves_v047_event_special_route_loot_card_status_diagnostics(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V047_EVENT_SPECIAL_ROUTE_LOOT_CARD_STATUS_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V047_EVENT_SPECIAL_ROUTE_LOOT_CARD_STATUS_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]
    route = diagnostics["event_special_route"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.7"
    assert "card_reward" not in payload
    assert "relic_reward" not in payload
    assert "character" not in payload
    assert diagnostics["event_special_route_verified_symbol_count"] == 30
    assert diagnostics["screen_observation_verified_symbol_count"] == 30
    assert route == {
        "probe_status": "event_special_options_cleared",
        "last_event": "event_layout_options_cleared",
        "active": True,
        "route_family": "event_special_choice",
        "route_label": None,
        "observation_source": "public_event_layout_options",
        "visible_option_count": 0,
        "clear_state": "unknown",
        "exports_recommendation_state": False,
        "blockers": ["event_special_route_status_only"],
        "error": None,
    }
    assert diagnostics["visible_reward_probe_status"] == "card_reward_model_seen"
    assert diagnostics["visible_reward_count"] == 2
    assert diagnostics["visible_card_reward_count"] == 2
    assert diagnostics["visible_card_reward_option_count"] == 6
    assert diagnostics["card_identity_review_option_count"] == 6
    assert diagnostics["card_reward_live_export_candidate"] == "refused"
    assert diagnostics["card_reward_live_export_candidate_writes_recommendation_state"] is False
    assert diagnostics["card_reward_live_export_refusal_reasons"] == [
        "unknown_reward_card",
        "unknown_deck_card",
        "unmapped_relic",
    ]
    assert "option_ids" not in route
    assert "option_names" not in route
    assert "selected_option" not in route


def test_status_export_preserves_v047_event_special_route_brain_leech_active_diagnostics(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V047_EVENT_SPECIAL_ROUTE_BRAIN_LEECH_ACTIVE_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V047_EVENT_SPECIAL_ROUTE_BRAIN_LEECH_ACTIVE_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]
    route = diagnostics["event_special_route"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.7"
    assert "card_reward" not in payload
    assert "relic_reward" not in payload
    assert "character" not in payload
    assert diagnostics["event_special_route_verified_symbol_count"] == 30
    assert diagnostics["screen_observation_verified_symbol_count"] == 30
    assert route == {
        "probe_status": "event_special_route_seen",
        "last_event": "event_layout_options_added",
        "active": True,
        "route_family": "event_special_choice",
        "route_label": None,
        "observation_source": "public_event_layout_options",
        "visible_option_count": 2,
        "clear_state": "active",
        "exports_recommendation_state": False,
        "blockers": ["event_special_route_status_only"],
        "error": None,
    }
    assert diagnostics["visible_reward_probe_status"] == "reward_screen_completed"
    assert diagnostics["card_reward_live_export_candidate"] == "refused"
    assert diagnostics["card_reward_live_export_candidate_writes_recommendation_state"] is False
    assert diagnostics["card_reward_live_export_refusal_reasons"] == [
        "stale_reward_screen",
        "missing_required_run_state_field",
    ]
    assert "option_ids" not in route
    assert "option_names" not in route
    assert "selected_option" not in route


def test_status_export_preserves_v047_event_special_route_brain_leech_map_cleared_diagnostics(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V047_EVENT_SPECIAL_ROUTE_BRAIN_LEECH_MAP_CLEARED_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V047_EVENT_SPECIAL_ROUTE_BRAIN_LEECH_MAP_CLEARED_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]
    route = diagnostics["event_special_route"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.7"
    assert "card_reward" not in payload
    assert "relic_reward" not in payload
    assert "character" not in payload
    assert diagnostics["event_special_route_verified_symbol_count"] == 30
    assert diagnostics["screen_observation_verified_symbol_count"] == 30
    assert route == {
        "probe_status": "cleared",
        "last_event": "map_screen_opened",
        "active": False,
        "route_family": None,
        "route_label": None,
        "observation_source": "public_event_route_classifier",
        "visible_option_count": 0,
        "clear_state": "cleared",
        "exports_recommendation_state": False,
        "blockers": [],
        "error": None,
    }
    assert diagnostics["visible_reward_probe_status"] == "reward_screen_completed"
    assert diagnostics["card_reward_live_export_candidate"] == "refused"
    assert diagnostics["card_reward_live_export_candidate_writes_recommendation_state"] is False
    assert "option_ids" not in route
    assert "option_names" not in route
    assert "selected_option" not in route


def test_status_export_preserves_v047_event_special_route_event_room_closed_diagnostics(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V047_EVENT_SPECIAL_ROUTE_EVENT_ROOM_CLOSED_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V047_EVENT_SPECIAL_ROUTE_EVENT_ROOM_CLOSED_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]
    route = diagnostics["event_special_route"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.7"
    assert "card_reward" not in payload
    assert "relic_reward" not in payload
    assert "character" not in payload
    assert diagnostics["event_special_route_verified_symbol_count"] == 33
    assert diagnostics["screen_observation_verified_symbol_count"] == 33
    assert route == {
        "probe_status": "cleared",
        "last_event": "event_room_closed",
        "active": False,
        "route_family": None,
        "route_label": None,
        "observation_source": "public_event_route_classifier",
        "visible_option_count": 0,
        "clear_state": "cleared",
        "exports_recommendation_state": False,
        "blockers": [],
        "error": None,
    }
    assert diagnostics["card_reward_live_export_candidate"] == "refused"
    assert diagnostics["card_reward_live_export_candidate_writes_recommendation_state"] is False
    assert diagnostics["relic_reward_live_export_candidate"] == "refused"
    assert diagnostics["visible_reward_probe_status"] == "reward_screen_completed"
    assert diagnostics["visible_reward_probe_last_event"] == "card_reward_selection_screen_closed"
    assert diagnostics["visible_card_reward_option_count"] == 0
    assert diagnostics["visible_relic_reward_option_count"] == 0
    assert "option_ids" not in route
    assert "option_names" not in route
    assert "selected_option" not in route


def test_export_alert_is_idle_for_v047_event_room_closed_clear_state(capsys) -> None:
    status = main(["export-alert", str(STATUS_V047_EVENT_SPECIAL_ROUTE_EVENT_ROOM_CLOSED_FIXTURE), "--once", "--quiet"])

    captured = capsys.readouterr()

    assert status == 0
    assert "no important state detected" in captured.out
    assert "Codex attention: no" in captured.out
    assert captured.err == ""


def test_export_alert_is_idle_for_proven_deck_enchant_status_only_route(capsys) -> None:
    status = main(
        [
            "export-alert",
            str(STATUS_V047_EVENT_SPECIAL_ROUTE_WOOD_CARVINGS_DECK_ENCHANT_FIXTURE),
            "--once",
            "--quiet",
        ]
    )

    captured = capsys.readouterr()

    assert status == 0
    assert "no important state detected" in captured.out
    assert "Codex attention: no" in captured.out
    assert "special_overlay_seen" not in captured.out
    assert captured.err == ""


def test_export_alert_flags_choose_relic_overlay(tmp_path: Path, capsys) -> None:
    raw = json.loads(STATUS_V047_EVENT_SPECIAL_ROUTE_EVENT_ROOM_CLOSED_FIXTURE.read_text(encoding="utf-8"))
    route = raw["export_metadata"]["diagnostics"]["event_special_route"]
    route.update(
        {
            "probe_status": "event_special_route_seen",
            "last_event": "choose_relic_selection_screen_shown",
            "active": True,
            "route_family": "event_special_choice",
            "observation_source": "public_choose_relic_selection_screen",
            "visible_option_count": 3,
            "clear_state": "active",
            "blockers": ["event_special_route_status_only"],
        }
    )
    fixture = tmp_path / "choose_relic_overlay.json"
    fixture.write_text(json.dumps(raw), encoding="utf-8")

    status = main(["export-alert", str(fixture), "--once", "--quiet"])

    captured = capsys.readouterr()

    assert status == 10
    assert "IMPORTANT DECKSEER EXPORTER STATE" in captured.out
    assert "choose_relic_overlay_seen" in captured.out
    assert "Codex attention: yes" in captured.out
    assert "public_choose_relic_selection_screen" in captured.out
    assert captured.err == ""


def test_export_alert_is_idle_for_pre_collection_mixed_reward_status(tmp_path: Path, capsys) -> None:
    raw = json.loads(STATUS_V047_EVENT_SPECIAL_ROUTE_LOOT_CARD_STATUS_FIXTURE.read_text(encoding="utf-8"))
    diagnostics = raw["export_metadata"]["diagnostics"]
    diagnostics["card_reward_live_export_refusal_reasons"] = [
        "unknown_reward_card",
        "unknown_deck_card",
        "unmapped_relic",
        "mixed_reward_screen_state_may_change",
    ]
    diagnostics["card_reward_live_export_mixed_reward_freshness_status"] = "awaiting_reward_collected"
    diagnostics["card_reward_live_export_mixed_reward_freshness_blockers"] = ["reward_collection_not_observed"]
    fixture = tmp_path / "pre_collection_mixed_reward_status.json"
    fixture.write_text(json.dumps(raw), encoding="utf-8")

    status = main(["export-alert", str(fixture), "--once", "--quiet"])

    captured = capsys.readouterr()

    assert status == 0
    assert "no important state detected" in captured.out
    assert "Codex attention: no" in captured.out
    assert "card_reward_export_blocked" not in captured.out
    assert captured.err == ""


def test_export_alert_is_idle_for_mapping_gap_already_in_local_catalog(tmp_path: Path, capsys) -> None:
    raw = json.loads(STATUS_V047_EVENT_SPECIAL_ROUTE_EVENT_ROOM_CLOSED_FIXTURE.read_text(encoding="utf-8"))
    diagnostics = raw["export_metadata"]["diagnostics"]
    diagnostics["card_reward_live_export_refusal_reasons"] = [
        "unknown_reward_card",
        "unknown_deck_card",
        "unmapped_relic",
        "unmapped_potion",
    ]
    diagnostics["card_reward_live_export_unmapped_reward_count"] = 1
    diagnostics["card_reward_live_export_unmapped_deck_count"] = 1
    diagnostics["card_reward_live_export_unmapped_relic_count"] = 1
    diagnostics["card_reward_live_export_unmapped_potion_count"] = 1
    diagnostics["card_identity_review_items"] = [
        {
            "normalized_candidate_id": "anger",
            "deckseer_mapping_status": "unknown",
            "deckseer_id": None,
        }
    ]
    diagnostics["deck_identity_review_items"] = [
        {
            "normalized_candidate_id": "armaments",
            "deckseer_mapping_status": "unknown",
            "deckseer_id": None,
        }
    ]
    diagnostics["relic_identity_review_items"] = [
        {
            "normalized_candidate_id": "lost_coffer",
            "deckseer_mapping_status": "unknown",
            "deckseer_id": None,
        }
    ]
    diagnostics["potion_identity_review_items"] = [
        {
            "normalized_candidate_id": "attack_potion",
            "deckseer_mapping_status": "unknown",
            "deckseer_id": None,
        }
    ]
    fixture = tmp_path / "local_catalog_known_mapping_status.json"
    fixture.write_text(json.dumps(raw), encoding="utf-8")

    status = main(["export-alert", str(fixture), "--once", "--quiet"])

    captured = capsys.readouterr()

    assert status == 0
    assert "no important state detected" in captured.out
    assert "Codex attention: no" in captured.out
    assert "card_reward_export_blocked" not in captured.out
    assert captured.err == ""


def test_export_alert_flags_mapping_gap_status(capsys) -> None:
    status = main(["export-alert", str(STATUS_V047_EVENT_SPECIAL_ROUTE_LOOT_CARD_STATUS_FIXTURE), "--once", "--quiet"])

    captured = capsys.readouterr()

    assert status == 10
    assert "card_reward_export_blocked" in captured.out
    assert "unknown_reward_card" in captured.out
    assert "unmapped_relic" in captured.out
    assert "Codex attention: yes" in captured.out
    assert "review ids: cleanse, kaleidoscope" in captured.out
    assert captured.err == ""


def test_export_alert_flags_recommendation_ready_without_codex_attention(capsys) -> None:
    status = main(["export-alert", str(FIXTURE), "--once", "--quiet"])

    captured = capsys.readouterr()

    assert status == 10
    assert "card_reward_ready" in captured.out
    assert "Codex attention: no" in captured.out
    assert "recommend-export --confirmed" in captured.out
    assert captured.err == ""


def test_status_export_preserves_v047_event_special_route_active_diagnostics(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V047_EVENT_SPECIAL_ROUTE_ANCIENT_ACTIVE_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V047_EVENT_SPECIAL_ROUTE_ANCIENT_ACTIVE_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]
    route = diagnostics["event_special_route"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.7"
    assert "card_reward" not in payload
    assert "relic_reward" not in payload
    assert "character" not in payload
    assert diagnostics["event_special_route_compile_probe"] == "compiled_not_registered"
    assert diagnostics["screen_observation_probe"] == "registered"
    assert diagnostics["screen_observation_verified_symbol_count"] == 25
    assert route == {
        "probe_status": "event_special_route_seen",
        "last_event": "event_layout_options_added",
        "active": True,
        "route_family": "event_special_choice",
        "route_label": None,
        "observation_source": "public_event_layout_options",
        "visible_option_count": 3,
        "clear_state": "active",
        "exports_recommendation_state": False,
        "blockers": ["event_special_route_status_only"],
        "error": None,
    }
    assert "option_ids" not in route
    assert "option_names" not in route
    assert "selected_option" not in route


def test_recommend_export_rejects_v047_event_special_route_active_status_even_when_confirmed(capsys) -> None:
    status = main(
        [
            "recommend-export",
            str(STATUS_V047_EVENT_SPECIAL_ROUTE_ANCIENT_ACTIVE_FIXTURE),
            "--confirmed",
            "--format",
            "text",
        ]
    )

    captured = capsys.readouterr()

    assert status == 2
    assert captured.out == ""
    assert "recommend-export only supports card_reward or relic_reward exports" in captured.err
    assert "got exporter_status" in captured.err


def test_status_export_preserves_v047_event_special_route_post_choice_diagnostics(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V047_EVENT_SPECIAL_ROUTE_ANCIENT_POST_CHOICE_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V047_EVENT_SPECIAL_ROUTE_ANCIENT_POST_CHOICE_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]
    route = diagnostics["event_special_route"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.7"
    assert "card_reward" not in payload
    assert "relic_reward" not in payload
    assert diagnostics["event_special_route_compile_probe"] == "compiled_not_registered"
    assert route["probe_status"] == "event_special_route_seen"
    assert route["last_event"] == "event_layout_options_added"
    assert route["active"] is True
    assert route["route_family"] == "event_special_choice"
    assert route["visible_option_count"] == 1
    assert route["clear_state"] == "active"
    assert route["exports_recommendation_state"] is False
    assert route["blockers"] == ["event_special_route_status_only"]
    assert "option_ids" not in route
    assert "option_names" not in route
    assert "selected_option" not in route


def test_status_export_clears_v045_treasure_relic_pick_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V045_TREASURE_RELIC_PICKED_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V045_TREASURE_RELIC_PICKED_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.5"
    assert "relic_reward" not in payload
    assert diagnostics["visible_reward_probe_status"] == "reward_screen_completed"
    assert diagnostics["visible_reward_probe_last_event"] == "treasure_relic_picked"
    assert diagnostics["visible_relic_reward_option_count"] == 0
    assert diagnostics["relic_reward_live_export_refusal_reasons"] == [
        "stale_reward_screen",
        "missing_required_run_state_field",
    ]
    assert diagnostics["relic_reward_identity_review_probe"] == "cleared"
    assert diagnostics["relic_reward_identity_review_items"] == []
    assert diagnostics["deck_identity_review_items"] == []
    assert diagnostics["relic_identity_review_items"] == []
    assert diagnostics["potion_identity_review_items"] == []


def test_recommend_export_rejects_v045_treasure_relic_picked_status_even_when_confirmed(capsys) -> None:
    status = main(
        [
            "recommend-export",
            str(STATUS_V045_TREASURE_RELIC_PICKED_FIXTURE),
            "--confirmed",
            "--format",
            "text",
        ]
    )

    captured = capsys.readouterr()

    assert status == 2
    assert captured.out == ""
    assert "recommend-export only supports card_reward or relic_reward exports" in captured.err
    assert "got exporter_status" in captured.err


def test_status_export_clears_v046_treasure_relic_pick_as_metadata(capsys) -> None:
    status = main(["inspect-export", str(STATUS_V046_TREASURE_RELIC_PICKED_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    inspected = inspect_exporter_state(STATUS_V046_TREASURE_RELIC_PICKED_FIXTURE)
    diagnostics = inspected.metadata["diagnostics"]

    assert status == 0
    assert payload["screen_type"] == "exporter_status"
    assert payload["exporter_version"] == "0.4.6"
    assert "relic_reward" not in payload
    assert diagnostics["visible_reward_probe_status"] == "reward_screen_completed"
    assert diagnostics["visible_reward_probe_last_event"] == "treasure_relic_picked"
    assert diagnostics["visible_relic_reward_option_count"] == 0
    assert diagnostics["relic_reward_live_export_refusal_reasons"] == [
        "stale_reward_screen",
        "missing_required_run_state_field",
    ]
    assert diagnostics["relic_reward_identity_review_probe"] == "cleared"
    assert diagnostics["relic_reward_identity_review_items"] == []
    assert diagnostics["deck_identity_review_items"] == []
    assert diagnostics["relic_identity_review_items"] == []
    assert diagnostics["potion_identity_review_items"] == []


def test_recommend_export_rejects_v046_treasure_relic_picked_status_even_when_confirmed(capsys) -> None:
    status = main(
        [
            "recommend-export",
            str(STATUS_V046_TREASURE_RELIC_PICKED_FIXTURE),
            "--confirmed",
            "--format",
            "text",
        ]
    )

    captured = capsys.readouterr()

    assert status == 2
    assert captured.out == ""
    assert "recommend-export only supports card_reward or relic_reward exports" in captured.err
    assert "got exporter_status" in captured.err


def test_inspect_export_accepts_relic_reward_fixture(capsys) -> None:
    status = main(["inspect-export", str(RELIC_FIXTURE)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["source_type"] == "deckseer_exporter_mod"
    assert payload["screen_type"] == "relic_reward"
    assert payload["character"] == "ironclad"
    assert payload["relic_reward"] == ["akabeko", "kunai"]
    assert payload["valid"] is True
    assert "User should confirm visible relic reward before using this state." in payload["caveats"]
    assert "Exporter state requires user confirmation before recommendation." in payload["caveats"]


def test_recommend_export_cli_rejects_status_fixture(capsys) -> None:
    status = main(["recommend-export", str(STATUS_FIXTURE)])

    captured = capsys.readouterr()

    assert status == 2
    assert captured.out == ""
    assert "recommend-export only supports card_reward or relic_reward exports" in captured.err


def test_exporter_recommendation_state_loads_relic_fixture() -> None:
    exported = load_exporter_recommendation_state(RELIC_FIXTURE)

    assert exported.screen_type == "relic_reward"
    assert exported.relic_state.relic_reward == ("akabeko", "kunai")


def test_recommend_export_requires_confirmation_for_relic_fixture(capsys) -> None:
    status = main(["recommend-export", str(RELIC_FIXTURE)])

    captured = capsys.readouterr()

    assert status == 2
    assert captured.out == ""
    assert "run inspect-export, verify the visible state" in captured.err
    assert "--confirmed" in captured.err


def test_recommend_export_cli_scores_relic_fixture_when_confirmed(capsys) -> None:
    status = main(["recommend-export", str(RELIC_FIXTURE), "--confirmed"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["recommendation_type"] == "relic_choice"
    assert payload["ranked_choices"][0]["choice"] == "akabeko"


def test_recommend_export_cli_scores_relic_fixture_as_text_when_confirmed(capsys) -> None:
    status = main(["recommend-export", str(RELIC_FIXTURE), "--confirmed", "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Relic Choice" in captured.out
    assert "1. Akabeko (akabeko)" in captured.out


def test_recommend_export_requires_confirmation_for_live_v040_relic_fixture(capsys) -> None:
    status = main(["recommend-export", str(LIVE_RELIC_V040_FIXTURE)])

    captured = capsys.readouterr()

    assert status == 2
    assert captured.out == ""
    assert "run inspect-export, verify the visible state" in captured.err
    assert "--confirmed" in captured.err


def test_recommend_export_cli_scores_live_v040_relic_fixture_when_confirmed(capsys) -> None:
    inspect_status = main(["inspect-export", str(LIVE_RELIC_V040_FIXTURE)])
    captured = capsys.readouterr()
    inspected = json.loads(captured.out)

    assert inspect_status == 0
    assert inspected["screen_type"] == "relic_reward"
    assert inspected["exporter_version"] == "0.4.0"
    assert inspected["requires_user_confirmation"] is True
    assert inspected["valid"] is True

    status = main(["recommend-export", str(LIVE_RELIC_V040_FIXTURE), "--confirmed"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["recommendation_type"] == "relic_choice"
    assert payload["ranked_choices"][0]["choice"] == "akabeko"
    assert {choice["choice"] for choice in payload["ranked_choices"]} >= {"akabeko", "kunai"}


def test_recommend_export_requires_confirmation(capsys) -> None:
    status = main(["recommend-export", str(FIXTURE)])

    captured = capsys.readouterr()

    assert status == 2
    assert captured.out == ""
    assert "run inspect-export, verify the visible state" in captured.err
    assert "--confirmed" in captured.err


def test_recommend_export_requires_confirmation_for_live_v030_fixture(capsys) -> None:
    status = main(["recommend-export", str(LIVE_V030_FIXTURE)])

    captured = capsys.readouterr()

    assert status == 2
    assert captured.out == ""
    assert "run inspect-export, verify the visible state" in captured.err
    assert "--confirmed" in captured.err


def test_recommend_export_cli_scores_live_v030_fixture_when_confirmed(capsys) -> None:
    status = main(["recommend-export", str(LIVE_V030_FIXTURE), "--confirmed"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["recommendation_type"] == "card_reward"
    assert {choice["choice"] for choice in payload["ranked_choices"]} >= {
        "cloak_and_dagger",
        "bouncing_flask",
        "infinite_blades",
        "skip",
    }


def test_recommend_export_requires_confirmation_for_live_v039_mixed_reward_fixture(capsys) -> None:
    status = main(["recommend-export", str(LIVE_V039_MIXED_REWARD_FIXTURE)])

    captured = capsys.readouterr()

    assert status == 2
    assert captured.out == ""
    assert "run inspect-export, verify the visible state" in captured.err
    assert "--confirmed" in captured.err


def test_recommend_export_cli_scores_live_v039_mixed_reward_fixture_when_confirmed(capsys) -> None:
    inspect_status = main(["inspect-export", str(LIVE_V039_MIXED_REWARD_FIXTURE)])
    captured = capsys.readouterr()
    inspected = json.loads(captured.out)

    assert inspect_status == 0
    assert inspected["screen_type"] == "card_reward"
    assert inspected["exporter_version"] == "0.3.9"
    assert inspected["requires_user_confirmation"] is True
    assert inspected["valid"] is True

    status = main(["recommend-export", str(LIVE_V039_MIXED_REWARD_FIXTURE), "--confirmed"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["recommendation_type"] == "card_reward"
    assert {choice["choice"] for choice in payload["ranked_choices"]} >= {
        "cloak_and_dagger",
        "bouncing_flask",
        "infinite_blades",
        "skip",
    }


def test_recommend_export_requires_confirmation_before_unknown_id_validation(capsys) -> None:
    status = main(["recommend-export", str(UNKNOWN_ID_FIXTURE)])

    captured = capsys.readouterr()

    assert status == 2
    assert captured.out == ""
    assert "run inspect-export, verify the visible state" in captured.err
    assert "--confirmed" in captured.err


def test_recommend_export_confirmed_unknown_reward_id_reports_missing_data(capsys) -> None:
    status = main(["recommend-export", str(UNKNOWN_ID_FIXTURE), "--confirmed"])

    captured = capsys.readouterr()

    assert status == 2
    assert captured.out == ""
    assert "Missing card data for: unknown_exported_card" in captured.err


def test_recommend_export_cli_smoke_json_with_confirmation(capsys) -> None:
    status = main(["recommend-export", str(FIXTURE), "--confirmed"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["recommendation_type"] == "card_reward"
    assert {choice["choice"] for choice in payload["ranked_choices"]} >= {"pommel_strike", "shrug_it_off", "anger", "skip"}


def test_recommend_export_cli_smoke_text(capsys) -> None:
    status = main(["recommend-export", str(FIXTURE), "--confirmed", "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Card Reward" in captured.out
    assert "Skip" in captured.out


def test_recommend_export_allows_unconfirmed_when_confirmation_not_required(tmp_path: Path, capsys) -> None:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    raw["export_metadata"]["requires_user_confirmation"] = False
    path = tmp_path / "already_confirmed_export.json"
    path.write_text(json.dumps(raw), encoding="utf-8")

    status = main(["recommend-export", str(path)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["recommendation_type"] == "card_reward"
