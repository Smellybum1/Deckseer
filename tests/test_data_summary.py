from __future__ import annotations

import json
from pathlib import Path

from deckseer.cli import main
from deckseer.data_loader import DeckseerData
from deckseer.data_summary import build_data_health, build_data_review, build_data_summary


def _data() -> DeckseerData:
    return DeckseerData.load(Path("data"))


def test_data_summary_reports_class_coverage() -> None:
    summary = build_data_summary(_data())

    assert summary["summary_type"] == "data_summary"
    assert summary["totals"]["cards"] >= 170
    expected_counts = {
        "defect": 34,
        "ironclad": 30,
        "necrobinder": 40,
        "regent": 42,
        "silent": 43,
    }
    for character, count in expected_counts.items():
        assert summary["cards_by_character"][character] >= count
    assert summary["metadata_gaps"]["cards_without_roles"]["count"] == 0
    assert summary["metadata_gaps"]["cards_without_source_patch"]["count"] == 0
    assert summary["metadata_gaps"]["cards_without_source_notes"]["count"] == 0
    assert "attack_skill_cards_with_empty_direct_effects" not in summary["metadata_gaps"]
    assert summary["review_flags"]["attack_skill_cards_with_empty_direct_effects"]["count"] == 0
    assert summary["review_flags"]["power_cards_with_empty_direct_effects"]["count"] == 0
    assert summary["review_flags"]["starter_cards_with_neutral_quality_prior"]["count"] == 7
    assert summary["review_flags"]["seed_only_cards_with_neutral_quality_prior"]["ids"] == [
        "armaments",
        "clothesline",
        "dominate",
        "perfected_strike",
        "setup_strike",
        "thunderclap",
        "dramatic_entrance",
        "ultimate_defend",
        "accuracy",
        "envenom",
        "fasten",
        "finisher",
        "memento_mori",
        "murder",
        "pinpoint",
        "ricochet",
        "tools_of_the_trade",
    ]
    assert summary["review_flags"]["uncategorized_cards_with_neutral_quality_prior"]["count"] == 0
    assert summary["source_patches"]


def test_data_summary_can_filter_by_character() -> None:
    summary = build_data_summary(_data(), character="silent")

    assert summary["filters"] == {"character": "silent"}
    assert summary["totals"]["cards"] == 43
    assert summary["totals"]["characters"] == 1
    assert summary["cards_by_character"] == {"silent": 43}
    assert "v0.102.0" in summary["source_patches"]
    assert summary["review_flags"]["attack_skill_cards_with_empty_direct_effects"]["count"] == 0
    assert summary["review_flags"]["power_cards_with_empty_direct_effects"]["count"] == 0


def test_data_summary_ironclad_power_effects_are_modeled() -> None:
    summary = build_data_summary(_data(), character="ironclad")

    assert summary["review_flags"]["attack_skill_cards_with_empty_direct_effects"]["count"] == 0
    assert summary["review_flags"]["power_cards_with_empty_direct_effects"]["count"] == 0


def test_data_summary_defect_effects_are_modeled() -> None:
    summary = build_data_summary(_data(), character="defect")

    assert summary["review_flags"]["attack_skill_cards_with_empty_direct_effects"]["count"] == 0
    assert summary["review_flags"]["power_cards_with_empty_direct_effects"]["count"] == 0


def test_data_summary_necrobinder_effects_are_modeled() -> None:
    summary = build_data_summary(_data(), character="necrobinder")

    assert summary["review_flags"]["attack_skill_cards_with_empty_direct_effects"]["count"] == 0
    assert summary["review_flags"]["power_cards_with_empty_direct_effects"]["count"] == 0


def test_data_summary_regent_effects_are_modeled() -> None:
    summary = build_data_summary(_data(), character="regent")

    assert summary["review_flags"]["attack_skill_cards_with_empty_direct_effects"]["count"] == 0
    assert summary["review_flags"]["power_cards_with_empty_direct_effects"]["count"] == 0


def test_data_summary_cli_json_smoke(capsys) -> None:
    status = main(["data-summary", "--character", "defect"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["summary_type"] == "data_summary"
    assert payload["filters"] == {"character": "defect"}
    assert payload["cards_by_character"] == {"defect": 34}
    assert payload["metadata_gaps"]["cards_without_source_patch"]["count"] >= 0
    assert "modest_cards_with_neutral_quality_prior" in payload["review_flags"]


def test_data_summary_cli_text_smoke(capsys) -> None:
    status = main(["data-summary", "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Data Summary" in captured.out
    assert "Cards by character:" in captured.out
    assert "Source patches:" in captured.out
    assert "Metadata gaps:" in captured.out
    assert "Review flags:" in captured.out


def test_data_summary_cli_text_filter_smoke(capsys) -> None:
    status = main(["data-summary", "--character", "ironclad", "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Filter: character=ironclad" in captured.out
    assert "   ironclad: 30" in captured.out


def test_data_summary_cli_text_can_show_limited_gap_ids(capsys) -> None:
    status = main(["data-summary", "--character", "silent", "--format", "text", "--show-gap-ids", "--max-gap-ids", "2"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Review flags:" in captured.out
    assert "attack_skill_cards_with_empty_direct_effects: 0" in captured.out
    assert "power_cards_with_empty_direct_effects: 0" in captured.out


def test_data_health_passes_current_catalog() -> None:
    health = build_data_health(_data())

    assert health["health_type"] == "data_health"
    assert health["status"] == "pass"
    assert health["failure_count"] == 0
    assert health["failures"] == {}
    assert "starter_cards_with_neutral_quality_prior" in health["ignored_review_flags"]
    assert "uncategorized_cards_with_neutral_quality_prior" not in health["ignored_review_flags"]


def test_data_health_cli_text_smoke(capsys) -> None:
    status = main(["data-health"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Data Health: PASS" in captured.out
    assert "Blocking failures: none" in captured.out
    assert "starter_cards_with_neutral_quality_prior" in captured.out


def test_data_health_cli_json_smoke(capsys) -> None:
    status = main(["data-health", "--character", "ironclad", "--format", "json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["health_type"] == "data_health"
    assert payload["status"] == "pass"
    assert payload["filters"] == {"character": "ironclad"}


def test_data_health_empty_character_filter_fails(capsys) -> None:
    status = main(["data-health", "--character", "notaclass"])

    captured = capsys.readouterr()

    assert status == 1
    assert "Data Health: FAIL" in captured.out
    assert "empty_character_filter" in captured.out


def test_data_review_lists_cards_for_selected_flag() -> None:
    review = build_data_review(_data(), flag="seed_only_cards_with_neutral_quality_prior")

    assert review["review_type"] == "data_review"
    assert review["filters"] == {"character": None, "flag": "seed_only_cards_with_neutral_quality_prior"}
    assert review["totals"]["flags"] == 1
    assert [card["id"] for card in review["review_flags"]["seed_only_cards_with_neutral_quality_prior"]] == [
        "armaments",
        "clothesline",
        "dominate",
        "perfected_strike",
        "setup_strike",
        "thunderclap",
        "dramatic_entrance",
        "ultimate_defend",
        "accuracy",
        "envenom",
        "fasten",
        "finisher",
        "memento_mori",
        "murder",
        "pinpoint",
        "ricochet",
        "tools_of_the_trade",
    ]
    clothesline = next(
        card for card in review["review_flags"]["seed_only_cards_with_neutral_quality_prior"] if card["id"] == "clothesline"
    )
    assert clothesline["source_patch"] == "v0.102.0"


def test_data_review_cli_text_smoke(capsys) -> None:
    status = main(["data-review", "--flag", "seed_only_cards_with_neutral_quality_prior"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Data Review" in captured.out
    assert "seed_only_cards_with_neutral_quality_prior" in captured.out
    assert "accuracy - Accuracy" in captured.out
    assert "envenom - Envenom" in captured.out
    assert "fasten - Fasten" in captured.out
    assert "memento_mori - Memento Mori" in captured.out
    assert "finisher - Finisher" in captured.out
    assert "armaments - Armaments" in captured.out
    assert "perfected_strike - Perfected Strike" in captured.out
    assert "setup_strike - Setup Strike" in captured.out
    assert "thunderclap - Thunderclap" in captured.out
    assert "ultimate_defend - Ultimate Defend" in captured.out
    assert "clothesline - Clothesline" in captured.out
    assert "dominate - Dominate" in captured.out
    assert "dramatic_entrance - Dramatic Entrance" in captured.out
    assert "Patch: v0.102.0" in captured.out


def test_data_review_cli_json_smoke(capsys) -> None:
    status = main(["data-review", "--character", "regent", "--flag", "niche_cards_with_neutral_quality_prior", "--format", "json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["review_type"] == "data_review"
    assert payload["filters"] == {"character": "regent", "flag": "niche_cards_with_neutral_quality_prior"}
    assert payload["review_flags"]["niche_cards_with_neutral_quality_prior"]


def test_data_review_unknown_flag_returns_error(capsys) -> None:
    status = main(["data-review", "--flag", "not_a_real_flag"])

    captured = capsys.readouterr()

    assert status == 2
    assert "Unknown review flag" in captured.err
