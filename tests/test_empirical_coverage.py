from __future__ import annotations

import json
from pathlib import Path

from deckseer.cli import main
from deckseer.data_loader import DeckseerData
from deckseer.empirical_coverage import build_empirical_coverage_report
from deckseer.qa import discover_empirical_stats


def test_empirical_coverage_current_active_data_summarizes_review_flags() -> None:
    data = DeckseerData.load(Path("data"))

    report = build_empirical_coverage_report(data, empirical_stats_paths=discover_empirical_stats(Path("data")))

    assert report["coverage_type"] == "empirical_coverage"
    assert report["status"] == "review"
    assert report["summary"]["files"] == 6
    assert report["summary"]["rows"] == 18
    assert report["summary"]["flags"] == 14
    assert report["summary"]["flags_by_code"] == {"patch_mismatch": 14}
    assert report["coverage"]["rows_by_review_status"] == {"accepted": 18}
    assert report["coverage"]["provenance_gaps"] == {
        "missing_source_url": 0,
        "missing_captured_at": 0,
        "missing_stat_definition": 0,
        "missing_reviewer_notes": 0,
    }
    assert report["coverage"]["traceable_rows_by_character"] == {
        "defect": 3,
        "ironclad": 3,
        "necrobinder": 6,
        "regent": 3,
        "silent": 3,
    }
    assert report["coverage"]["missing_traceable_catalog_characters"] == []
    assert report["coverage"]["rows_by_character"] == {
        "defect": 3,
        "ironclad": 3,
        "necrobinder": 6,
        "regent": 3,
        "silent": 3,
    }
    assert report["coverage"]["missing_catalog_characters"] == []
    assert report["coverage"]["characters_below_minimum"] == {}


def test_empirical_coverage_full_clean_fixture_reports_pass(tmp_path) -> None:
    data = DeckseerData.load(Path("data"))
    stats_path = tmp_path / "full_clean_stats.json"
    stats_path.write_text(json.dumps([_clean_stat_for(data, character) for character in _catalog_characters(data)]), encoding="utf-8")

    report = build_empirical_coverage_report(data, empirical_stats_paths=(stats_path,))

    assert report["status"] == "pass"
    assert report["summary"]["rows"] == 5
    assert report["summary"]["flags"] == 0
    assert report["coverage"]["missing_catalog_characters"] == []
    assert report["coverage"]["characters_below_minimum"] == {}


def test_empirical_coverage_missing_character_reports_review(tmp_path) -> None:
    data = DeckseerData.load(Path("data"))
    stats_path = tmp_path / "partial_clean_stats.json"
    stats_path.write_text(json.dumps([_clean_stat_for(data, "ironclad")]), encoding="utf-8")

    report = build_empirical_coverage_report(data, empirical_stats_paths=(stats_path,))

    assert report["status"] == "review"
    assert report["coverage"]["missing_catalog_characters"] == ["defect", "necrobinder", "regent", "silent"]


def test_empirical_coverage_audit_flags_report_review() -> None:
    data = DeckseerData.load(Path("data"))

    report = build_empirical_coverage_report(
        data,
        empirical_stats_paths=(Path("tests/fixtures/empirical/multi_class_conflict_stats.json"),),
    )

    assert report["status"] == "review"
    assert report["summary"]["flags"] == 6
    assert report["summary"]["flags_by_code"]["low_prior_strong_empirical"] == 3


def test_empirical_coverage_invalid_file_reports_fail(tmp_path) -> None:
    data = DeckseerData.load(Path("data"))
    stats_path = tmp_path / "invalid_stats.json"
    stats_path.write_text(json.dumps({"not": "a list"}), encoding="utf-8")

    report = build_empirical_coverage_report(data, empirical_stats_paths=(stats_path,))

    assert report["status"] == "fail"
    assert report["summary"]["failed_files"] == 1
    assert report["errors"][0]["path"] == str(stats_path)


def test_empirical_coverage_cli_json_includes_missing_characters(capsys) -> None:
    status = main(["empirical-coverage", "--format", "json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["coverage_type"] == "empirical_coverage"
    assert payload["status"] == "review"
    assert payload["coverage"]["missing_catalog_characters"] == []
    assert payload["summary"]["flags"] == 14
    assert payload["summary"]["rows"] == 18
    assert payload["coverage"]["provenance_gaps"]["missing_source_url"] == 0


def test_empirical_coverage_cli_text_shows_rows_and_caveats(capsys) -> None:
    status = main(["empirical-coverage", "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Empirical Coverage: REVIEW" in captured.out
    assert "Files: 6/6 loaded | Rows: 18 | Flags: 14" in captured.out
    assert "Provenance gaps:" in captured.out
    assert "Characters below target: none" in captured.out
    assert "Caveat:" in captured.out


def test_empirical_coverage_cli_fail_on_review_returns_failure(capsys) -> None:
    status = main(["empirical-coverage", "--fail-on-review"])

    captured = capsys.readouterr()

    assert status == 1
    assert "Empirical Coverage: REVIEW" in captured.out


def _catalog_characters(data: DeckseerData) -> list[str]:
    return sorted({card.character for card in data.cards_by_id.values() if card.character != "neutral"})


def _clean_stat_for(data: DeckseerData, character: str) -> dict:
    cards = sorted(
        (
            card
            for card in data.cards_by_id.values()
            if card.character == character and card.quality_prior >= 3 and card.source_patch is not None
        ),
        key=lambda card: card.id,
    )
    card = cards[0]
    return {
        "card_id": card.id,
        "character": card.character,
        "patch": card.source_patch,
        "source": "test reviewed empirical fixture",
        "sample_size": 500,
        "pick_rate": 0.4,
        "win_rate": 0.6,
        "impact": 0.08,
        "act": "all",
        "ascension": "all",
        "source_url": "https://sts2.fun/",
        "captured_at": "2026-05-23",
        "stat_definition": "test reviewed pick impact",
        "reviewer_notes": "Traceable test row.",
        "review_status": "accepted",
    }
