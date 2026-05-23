from __future__ import annotations

from pathlib import Path
from typing import Any

from deckseer.card_lookup import missing_card_suggestions
from deckseer.data_loader import DeckseerData
from deckseer.models import DeckseerError, RunState
from deckseer.scoring.rules import DeckProfile, RunNeed, build_deck_profile, diagnose_run_needs


def diagnose_run_state(run: RunState, data: DeckseerData) -> dict[str, Any]:
    profile = build_deck_profile(run, data.cards_by_id)
    needs = diagnose_run_needs(run, profile)
    return {
        "diagnosis_type": "card_reward_run_needs",
        "character": run.character,
        "act": run.act,
        "floor": run.floor,
        "hp": {
            "current": run.hp.current,
            "max": run.hp.max,
            "ratio": round(profile.hp_ratio, 3),
        },
        "data_coverage": _coverage_to_dict(profile),
        "deck_profile": _profile_to_dict(profile),
        "prioritized_needs": [_need_to_dict(need) for need in needs],
        "caveats": _caveats_for(profile),
    }


def check_run_data_coverage(run: RunState, data: DeckseerData) -> dict[str, Any]:
    deck_missing = sorted({deck_card.id for deck_card in run.deck if deck_card.id not in data.cards_by_id})
    reward_missing = sorted(choice for choice in run.card_reward if choice not in data.cards_by_id)
    deck_total = sum(deck_card.count for deck_card in run.deck)
    deck_missing_count = sum(deck_card.count for deck_card in run.deck if deck_card.id in deck_missing)
    deck_known_count = deck_total - deck_missing_count
    deck_coverage_ratio = deck_known_count / deck_total if deck_total else 1.0
    return {
        "check_type": "run_data_coverage",
        "character": run.character,
        "scoring_ready": not reward_missing,
        "deck": {
            "total_cards": deck_total,
            "known_cards": deck_known_count,
            "unknown_cards": deck_missing_count,
            "coverage_ratio": round(deck_coverage_ratio, 3),
            "missing_card_ids": deck_missing,
            "suggestions": missing_card_suggestions(deck_missing, data.cards_by_id),
        },
        "card_reward": {
            "total_choices": len(run.card_reward),
            "known_choices": len(run.card_reward) - len(reward_missing),
            "missing_choices": len(reward_missing),
            "missing_card_ids": reward_missing,
            "suggestions": missing_card_suggestions(reward_missing, data.cards_by_id),
        },
        "caveats": _coverage_caveats(deck_missing, reward_missing),
    }


def check_run_file_data_coverage(path: Path, data: DeckseerData) -> dict[str, Any]:
    try:
        run = RunState.from_json_file(path)
    except (DeckseerError, OSError) as exc:
        return {
            "path": str(path),
            "valid": False,
            "scoring_ready": False,
            "error": str(exc),
        }

    coverage = check_run_data_coverage(run, data)
    return {
        "path": str(path),
        "valid": True,
        **coverage,
    }


def check_run_files_data_coverage(paths: list[Path], data: DeckseerData) -> dict[str, Any]:
    runs = [check_run_file_data_coverage(path, data) for path in paths]
    valid_runs = [run for run in runs if run["valid"]]
    return {
        "check_type": "run_file_data_coverage_batch",
        "summary": {
            "total_files": len(runs),
            "valid_files": len(valid_runs),
            "invalid_files": len(runs) - len(valid_runs),
            "scoring_ready_files": sum(1 for run in valid_runs if run["scoring_ready"]),
            "blocked_files": sum(1 for run in runs if not run["scoring_ready"]),
            "files_with_deck_metadata_gaps": sum(
                1 for run in valid_runs if run["deck"]["unknown_cards"] > 0
            ),
        },
        "runs": runs,
    }


def _coverage_to_dict(profile: DeckProfile) -> dict[str, Any]:
    coverage_ratio = profile.known_cards / profile.size if profile.size else 1.0
    return {
        "known_deck_cards": profile.known_cards,
        "unknown_deck_cards": profile.unknown_cards,
        "coverage_ratio": round(coverage_ratio, 3),
        "unknown_card_ids": list(profile.unknown_card_ids),
    }


def _profile_to_dict(profile: DeckProfile) -> dict[str, Any]:
    return {
        "size": profile.size,
        "known_cards": profile.known_cards,
        "unknown_cards": profile.unknown_cards,
        "phase": profile.phase,
        "average_cost": round(profile.average_cost, 2),
        "counts": {
            "damage": profile.damage_cards,
            "block": profile.block_cards,
            "draw": profile.draw_cards,
            "energy": profile.energy_cards,
            "scaling": profile.scaling_cards,
        },
        "densities": {
            "damage": round(profile.damage_density, 3),
            "block": round(profile.block_density, 3),
            "draw": round(profile.draw_density, 3),
            "scaling": round(profile.scaling_density, 3),
        },
        "tags": sorted(profile.tags),
        "roles": sorted(profile.roles),
    }


def _need_to_dict(need: RunNeed) -> dict[str, Any]:
    return {
        "name": need.name,
        "priority": round(need.priority, 1),
        "reason": need.reason,
        "unresolved_risk": need.unresolved_risk,
    }


def _caveats_for(profile: DeckProfile) -> list[str]:
    if profile.unknown_cards == 0:
        return []
    labels = ", ".join(profile.unknown_card_ids)
    return [f"Deck contains unmodeled card metadata ({labels}); diagnosis and confidence are limited."]


def _coverage_caveats(deck_missing: list[str], reward_missing: list[str]) -> list[str]:
    caveats: list[str] = []
    if reward_missing:
        labels = ", ".join(reward_missing)
        caveats.append(f"Cannot score this reward until offered card metadata is added: {labels}.")
    if deck_missing:
        labels = ", ".join(deck_missing)
        caveats.append(f"Existing deck has unmodeled cards; recommendations can run but confidence is limited: {labels}.")
    return caveats
