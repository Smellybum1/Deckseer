from __future__ import annotations

import json
from pathlib import Path

from deckseer.audit.card_priors import audit_card_priors, load_empirical_card_stats
from deckseer.cli import main
from deckseer.data_loader import DeckseerData
from deckseer.models import ValidationError


EMPIRICAL_FIXTURES = Path("tests/fixtures/empirical")


def _result_rows_by_id(stats_file: str = "ironclad_conflict_stats.json") -> dict:
    data = DeckseerData.load(Path("data"))
    stats_path = EMPIRICAL_FIXTURES / stats_file
    stats = load_empirical_card_stats(stats_path)
    result = audit_card_priors(data, stats, empirical_source=str(stats_path))
    return {row.card_id: row for row in result.rows}


def _audit_result(stats_file: str = "ironclad_conflict_stats.json"):
    data = DeckseerData.load(Path("data"))
    stats_path = EMPIRICAL_FIXTURES / stats_file
    stats = load_empirical_card_stats(stats_path)
    return audit_card_priors(data, stats, empirical_source=str(stats_path))


def test_empirical_stats_fixture_loads() -> None:
    stats = load_empirical_card_stats(EMPIRICAL_FIXTURES / "legacy_ironclad_card_stats_sample.json")

    assert len(stats) == 3
    assert stats[0].card_id == "pommel_strike"
    assert stats[0].impact == 0.07
    assert stats[0].review_status == "seed"
    assert stats[0].source_url is None


def test_multi_class_empirical_stats_fixture_loads() -> None:
    stats = load_empirical_card_stats(EMPIRICAL_FIXTURES / "legacy_multi_class_card_stats_sample.json")

    assert len(stats) == 3
    assert {stat.character for stat in stats} == {"defect", "regent", "silent"}
    assert stats[0].card_id == "adrenaline"


def test_empirical_stats_load_optional_provenance_fields(tmp_path) -> None:
    stats_path = tmp_path / "provenance_stats.json"
    stats_path.write_text(
        json.dumps(
            [
                {
                    "card_id": "adrenaline",
                    "character": "silent",
                    "patch": "v0.102.0",
                    "source": "test fixture",
                    "sample_size": 1400,
                    "pick_rate": 0.54,
                    "win_rate": 0.66,
                    "impact": 0.11,
                    "source_url": "https://sts2.fun/",
                    "captured_at": "2026-05-23",
                    "stat_definition": "pick win-rate impact",
                    "reviewer_notes": "Traceable test row.",
                    "review_status": "accepted",
                }
            ]
        ),
        encoding="utf-8",
    )

    stats = load_empirical_card_stats(stats_path)

    assert stats[0].source_url == "https://sts2.fun/"
    assert stats[0].captured_at == "2026-05-23"
    assert stats[0].stat_definition == "pick win-rate impact"
    assert stats[0].review_status == "accepted"


def test_empirical_stats_reject_invalid_review_status(tmp_path) -> None:
    stats_path = tmp_path / "bad_review_status.json"
    stats_path.write_text(
        json.dumps(
            [
                {
                    "card_id": "adrenaline",
                    "character": "silent",
                    "patch": "v0.102.0",
                    "source": "test fixture",
                    "sample_size": 1400,
                    "pick_rate": 0.54,
                    "win_rate": 0.66,
                    "impact": 0.11,
                    "review_status": "done",
                }
            ]
        ),
        encoding="utf-8",
    )

    try:
        load_empirical_card_stats(stats_path)
    except ValidationError as exc:
        assert "review_status must be one of" in str(exc)
    else:
        raise AssertionError("Expected invalid review_status to fail validation")


def test_audit_flags_missing_card_data() -> None:
    rows = _result_rows_by_id()

    codes = {flag.code for flag in rows["unknown_stat_card"].flags}

    assert "missing_card_data" in codes


def test_audit_flags_small_samples_without_conflict_review() -> None:
    rows = _result_rows_by_id()

    codes = {flag.code for flag in rows["barricade"].flags}

    assert "small_sample_size" in codes
    assert "low_prior_strong_empirical" not in codes


def test_audit_flags_patch_mismatch() -> None:
    rows = _result_rows_by_id()

    codes = {flag.code for flag in rows["demon_form"].flags}

    assert "patch_mismatch" in codes
    assert "low_prior_strong_empirical" in codes


def test_audit_clean_high_prior_strong_empirical_row_has_no_flags() -> None:
    rows = _result_rows_by_id()

    assert rows["offering"].flags == ()


def test_audit_cli_smoke(capsys) -> None:
    status = main(["audit-card-priors", "tests/fixtures/empirical/ironclad_conflict_stats.json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["audit_type"] == "card_prior_empirical_review"
    assert payload["summary"]["rows"] == 6
    assert payload["summary"]["flagged_rows"] == 3
    assert payload["summary"]["flags"] == 4
    assert payload["summary"]["flags_by_code"]["missing_card_data"] == 1
    assert any(row["card_id"] == "unknown_stat_card" for row in payload["rows"])


def test_audit_result_includes_character_and_summary_counts() -> None:
    payload = _audit_result("multi_class_conflict_stats.json").to_dict()
    rows_by_id = {row["card_id"]: row for row in payload["rows"]}

    assert rows_by_id["dash"]["character"] == "silent"
    assert payload["summary"] == {
        "rows": 7,
        "flagged_rows": 5,
        "clean_rows": 2,
        "flags": 6,
        "flags_by_code": {
            "low_prior_strong_empirical": 3,
            "high_prior_weak_empirical": 1,
            "patch_mismatch": 2,
        },
        "flags_by_severity": {
            "review": 4,
            "warning": 2,
        },
        "rows_by_character": {
            "defect": 2,
            "regent": 2,
            "silent": 2,
            "necrobinder": 1,
        },
        "flagged_rows_by_character": {
            "defect": 1,
            "necrobinder": 1,
            "regent": 2,
            "silent": 1,
        },
    }


def test_audit_cli_text_smoke(capsys) -> None:
    status = main(["audit-card-priors", "tests/fixtures/empirical/multi_class_conflict_stats.json", "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Card Prior Audit" in captured.out
    assert "Rows: 7 | Flagged: 5 | Flags: 6" in captured.out
    assert "Flags by code:" in captured.out
    assert "low_prior_strong_empirical: 3" in captured.out
    assert "Flags by severity:" in captured.out
    assert "review: 4" in captured.out
    assert "warning: 2" in captured.out
    assert "Flagged rows by character:" in captured.out
    assert "defragment - Defragment" in captured.out
    assert "review: high_prior_weak_empirical" in captured.out
    assert "Clean rows: adrenaline, glacier" in captured.out


def test_audit_cli_fail_on_flags_returns_failure(capsys) -> None:
    status = main(["audit-card-priors", "tests/fixtures/empirical/multi_class_conflict_stats.json", "--fail-on-flags"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 1
    assert payload["summary"]["flags"] == 6


def test_audit_cli_fail_on_flags_passes_clean_audit(tmp_path, capsys) -> None:
    stats_path = tmp_path / "clean_card_stats.json"
    stats_path.write_text(
        json.dumps(
            [
                {
                    "card_id": "adrenaline",
                    "character": "silent",
                    "patch": "v0.102.0",
                    "source": "test fixture",
                    "sample_size": 1400,
                    "pick_rate": 0.54,
                    "win_rate": 0.66,
                    "impact": 0.11,
                    "act": "all",
                    "ascension": "all",
                }
            ]
        ),
        encoding="utf-8",
    )

    status = main(["audit-card-priors", str(stats_path), "--fail-on-flags"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["summary"]["flags"] == 0


def test_multi_class_audit_flags_high_prior_weak_empirical() -> None:
    rows = _result_rows_by_id("multi_class_conflict_stats.json")

    codes = {flag.code for flag in rows["defragment"].flags}

    assert "high_prior_weak_empirical" in codes


def test_multi_class_audit_flags_low_prior_strong_empirical() -> None:
    rows = _result_rows_by_id("multi_class_conflict_stats.json")

    assert "low_prior_strong_empirical" in {flag.code for flag in rows["dash"].flags}
    assert "low_prior_strong_empirical" in {flag.code for flag in rows["scourge"].flags}


def test_multi_class_audit_flags_patch_mismatch() -> None:
    rows = _result_rows_by_id("multi_class_conflict_stats.json")

    codes = {flag.code for flag in rows["black_hole"].flags}

    assert "patch_mismatch" in codes
    assert "low_prior_strong_empirical" in codes


def test_multi_class_audit_clean_rows_have_no_flags() -> None:
    rows = _result_rows_by_id("multi_class_conflict_stats.json")

    assert rows["adrenaline"].flags == ()
    assert rows["glacier"].flags == ()
