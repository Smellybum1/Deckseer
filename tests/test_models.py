from __future__ import annotations

import json
from pathlib import Path

import pytest

from deckseer.data_loader import DeckseerData
from deckseer.models import CardData, DataError, RunState, TaggedData, ValidationError


def test_run_state_loads_fixture() -> None:
    with open("tests/fixtures/card_reward_basic.json", "r", encoding="utf-8") as handle:
        run = RunState.from_dict(json.load(handle))

    assert run.character == "ironclad"
    assert run.hp.current == 52
    assert run.deck[0].id == "strike"
    assert run.card_reward == ("pommel_strike", "shrug_it_off", "anger")


def test_run_state_requires_card_reward() -> None:
    raw = {
        "character": "ironclad",
        "act": 1,
        "floor": 1,
        "hp": {"current": 70, "max": 80},
        "deck": [],
        "relics": [],
        "potions": [],
    }

    with pytest.raises(ValidationError, match="card_reward"):
        RunState.from_dict(raw)


def test_run_state_rejects_explicit_skip_reward() -> None:
    raw = {
        "character": "ironclad",
        "act": 1,
        "floor": 1,
        "hp": {"current": 70, "max": 80},
        "deck": [],
        "relics": [],
        "potions": [],
        "card_reward": ["skip"],
    }

    with pytest.raises(ValidationError, match="adds it automatically"):
        RunState.from_dict(raw)


def test_run_context_v02_optional_fields_load() -> None:
    raw = {
        "character": "ironclad",
        "act": 1,
        "floor": 6,
        "hp": {"current": 62, "max": 80},
        "deck": [],
        "relics": [],
        "potions": [],
        "card_reward": ["pommel_strike"],
        "run_context": {
            "act_region": "underdocks",
            "upcoming_elites": ["skulking_colony", "terror_eel"],
            "fought_elites": ["phantasmal_gardener"],
            "next_nodes": ["combat", "fire", "elite"],
            "fire_before_elite": True,
            "shop_before_elite": False,
            "path_pressure": "elite_soon",
        },
    }

    run = RunState.from_dict(raw)

    assert run.run_context.act_region == "underdocks"
    assert run.run_context.upcoming_elites == ("skulking_colony", "terror_eel")
    assert run.run_context.fought_elites == ("phantasmal_gardener",)
    assert run.run_context.next_nodes == ("combat", "fire", "elite")
    assert run.run_context.fire_before_elite is True
    assert run.run_context.shop_before_elite is False
    assert run.run_context.path_pressure == "elite_soon"


def test_data_loader_reports_unknown_reward_card() -> None:
    data = DeckseerData.load(data_dir=Path("data"))

    with pytest.raises(DataError, match="missing_card"):
        data.cards_for_choices(("missing_card",))


def test_expanded_ironclad_cards_load_with_priors_and_roles() -> None:
    data = DeckseerData.load(data_dir=Path("data"))

    assert len([card for card in data.cards_by_id.values() if card.character == "ironclad"]) >= 20
    assert data.cards_by_id["offering"].quality_prior == 5.0
    assert {"draw", "energy", "burst"}.issubset(data.cards_by_id["offering"].roles)
    assert data.cards_by_id["barricade"].quality_prior < 0
    assert "niche" in data.cards_by_id["body_slam"].roles


def test_silent_cards_load_with_priors_and_roles() -> None:
    data = DeckseerData.load(data_dir=Path("data"))

    silent_cards = [card for card in data.cards_by_id.values() if card.character == "silent"]

    assert len(silent_cards) >= 25
    assert {"neutralize", "survivor", "backflip", "dagger_throw", "footwork"}.issubset(data.cards_by_id)
    assert data.cards_by_id["backflip"].quality_prior == 5.0
    assert {"block", "draw", "consistency"}.issubset(data.cards_by_id["backflip"].roles)
    assert data.cards_by_id["poisoned_stab"].quality_prior < 0


def test_defect_cards_load_with_priors_and_roles() -> None:
    data = DeckseerData.load(data_dir=Path("data"))

    defect_cards = [card for card in data.cards_by_id.values() if card.character == "defect"]

    assert len(defect_cards) >= 30
    assert {"zap", "dualcast", "cold_snap", "glacier", "defragment"}.issubset(data.cards_by_id)
    assert data.cards_by_id["cold_snap"].quality_prior == 2.0
    assert data.cards_by_id["cold_snap"].source_patch == "main_v0.103_current"
    assert "Current-patch STS2.fun review" in data.cards_by_id["cold_snap"].source_notes[1]
    assert data.cards_by_id["defragment"].quality_prior == 5.0
    assert {"scaling", "orb", "power"}.issubset(data.cards_by_id["defragment"].roles)
    assert data.cards_by_id["claw"].quality_prior < 0


def test_necrobinder_cards_load_with_priors_and_roles() -> None:
    data = DeckseerData.load(data_dir=Path("data"))

    necrobinder_cards = [card for card in data.cards_by_id.values() if card.character == "necrobinder"]

    assert len(necrobinder_cards) >= 35
    assert {"unleash", "bodyguard", "deathbringer", "forbidden_grimoire"}.issubset(data.cards_by_id)
    assert data.cards_by_id["deathbringer"].quality_prior == 5.0
    assert {"scaling", "summon", "power"}.issubset(data.cards_by_id["deathbringer"].roles)
    assert data.cards_by_id["forbidden_grimoire"].quality_prior == 1.0
    assert data.cards_by_id["forbidden_grimoire"].source_patch == "main_v0.103_current"
    assert "Current-patch STS2.fun review" in data.cards_by_id["forbidden_grimoire"].source_notes[0]
    assert data.cards_by_id["misery"].quality_prior < 0


def test_regent_cards_load_with_priors_and_roles() -> None:
    data = DeckseerData.load(data_dir=Path("data"))

    regent_cards = [card for card in data.cards_by_id.values() if card.character == "regent"]

    assert len(regent_cards) >= 35
    assert {"astral_pulse", "bulwark", "spectrum_shift", "child_of_the_stars"}.issubset(data.cards_by_id)
    assert data.cards_by_id["astral_pulse"].quality_prior == 2.0
    assert data.cards_by_id["astral_pulse"].source_patch == "main_v0.103_current"
    assert "Current-patch STS2.fun review" in data.cards_by_id["astral_pulse"].source_notes[1]
    assert data.cards_by_id["bulwark"].quality_prior == 2.0
    assert data.cards_by_id["bulwark"].source_patch == "main_v0.103_current"
    assert "Current-patch STS2.fun review" in data.cards_by_id["bulwark"].source_notes[1]
    assert {"frontload", "burst"}.issubset(data.cards_by_id["astral_pulse"].roles)
    assert {"block", "scaling", "power"}.issubset(data.cards_by_id["child_of_the_stars"].roles)
    assert data.cards_by_id["shining_strike"].quality_prior < 0


def test_card_roles_are_optional_for_backward_compatibility() -> None:
    card = CardData.from_dict(
        {
            "id": "old_card",
            "name": "Old Card",
            "character": "ironclad",
            "type": "attack",
            "rarity": "common",
            "cost": 1,
            "tags": ["damage"],
            "effects": {"damage": 7, "block": 0, "draw": 0, "energy": 0},
        },
        "test_card",
    )

    assert card.roles == frozenset()
    assert card.quality_prior == 0
    assert card.pick_context == frozenset()
    assert card.source_patch is None
    assert card.source_notes == ()


def test_card_prior_metadata_loads_when_present() -> None:
    card = CardData.from_dict(
        {
            "id": "prior_card",
            "name": "Prior Card",
            "character": "ironclad",
            "type": "skill",
            "rarity": "rare",
            "cost": 1,
            "tags": ["block"],
            "roles": ["block"],
            "quality_prior": 4.5,
            "pick_context": ["defense", "elite_prep"],
            "source_patch": "v0.102.0",
            "source_notes": ["Local tier list: S tier."],
            "effects": {"damage": 0, "block": 12, "draw": 0, "energy": 0},
        },
        "test_card",
    )

    assert card.quality_prior == 4.5
    assert card.pick_context == frozenset({"defense", "elite_prep"})
    assert card.source_patch == "v0.102.0"
    assert card.source_notes == ("Local tier list: S tier.",)


def test_card_effects_support_extra_numeric_metadata() -> None:
    card = CardData.from_dict(
        {
            "id": "extra_effect_card",
            "name": "Extra Effect Card",
            "character": "silent",
            "type": "skill",
            "rarity": "common",
            "cost": 1,
            "tags": ["poison"],
            "effects": {
                "damage": 0,
                "block": 0,
                "draw": 0,
                "energy": 0,
                "extra": {
                    "poison": 5,
                },
            },
        },
        "test_card",
    )

    assert card.effects.extra == {"poison": 5.0}


def test_tagged_data_supports_relic_choice_metadata() -> None:
    relic = TaggedData.from_dict(
        {
            "id": "test_relic",
            "name": "Test Relic",
            "tags": ["damage"],
            "roles": ["frontload"],
            "quality_prior": 3.5,
            "pick_context": ["elite_prep"],
            "source_patch": "deckseer_relic_seed_v1",
            "source_notes": ["Reviewed seed note."],
        },
        "test_relic",
    )

    assert relic.roles == frozenset({"frontload"})
    assert relic.quality_prior == 3.5
    assert relic.pick_context == frozenset({"elite_prep"})
    assert relic.source_patch == "deckseer_relic_seed_v1"
    assert relic.source_notes == ("Reviewed seed note.",)


def test_relic_seed_metadata_loads_for_relic_choice_v1() -> None:
    data = DeckseerData.load(data_dir=Path("data"))

    assert data.relics_by_id["burning_blood"].roles == frozenset({"sustain"})
    assert data.relics_by_id["akabeko"].quality_prior == 4.0
    assert {"early", "elite_prep", "attack_dense"}.issubset(data.relics_by_id["akabeko"].pick_context)
    assert {"defense", "scaling"}.issubset(data.relics_by_id["kunai"].roles)
    assert data.relics_by_id["kunai"].source_patch == "deckseer_relic_seed_v1"
