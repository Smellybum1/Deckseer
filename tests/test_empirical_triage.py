from __future__ import annotations

import json
from pathlib import Path

from deckseer.cli import main
from deckseer.data_loader import DeckseerData
from deckseer.empirical_triage import build_empirical_triage_report, load_empirical_triage
from deckseer.models import ValidationError
from deckseer.qa import discover_empirical_stats


TRIAGE = Path("data/empirical/triage.json")


def test_empirical_triage_manifest_loads_seeded_entries() -> None:
    entries = load_empirical_triage(TRIAGE)

    assert len(entries) == 14
    assert {entry.status for entry in entries} == {"resolved_no_change"}
    assert any(entry.card_id == "forbidden_grimoire" and entry.flag_code == "patch_mismatch" for entry in entries)


def test_empirical_triage_manifest_rejects_duplicate_ids(tmp_path) -> None:
    manifest = tmp_path / "triage.json"
    payload = _manifest_payload()
    payload["entries"][1]["id"] = payload["entries"][0]["id"]
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_empirical_triage(manifest)
    except ValidationError as exc:
        assert "duplicate empirical triage ids" in str(exc)
    else:
        raise AssertionError("Expected duplicate triage ids to fail validation")


def test_empirical_triage_manifest_rejects_unsupported_status(tmp_path) -> None:
    manifest = tmp_path / "triage.json"
    payload = _manifest_payload()
    payload["entries"][0]["status"] = "done-ish"
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_empirical_triage(manifest)
    except ValidationError as exc:
        assert "status must be one of" in str(exc)
    else:
        raise AssertionError("Expected unsupported triage status to fail validation")


def test_empirical_triage_report_matches_current_active_flags() -> None:
    data = DeckseerData.load(Path("data"))

    report = build_empirical_triage_report(
        data,
        empirical_stats_paths=discover_empirical_stats(Path("data")),
        triage_manifest_path=TRIAGE,
    )

    assert report["report_type"] == "empirical_triage_report"
    assert report["status"] == "pass"
    assert report["summary"]["active_flags"] == 14
    assert report["summary"]["triaged_flags"] == 14
    assert report["summary"]["resolved_active_flags"] == 14
    assert report["summary"]["unresolved_active_flags"] == 0
    assert report["summary"]["missing_triage_entries"] == 0
    assert report["summary"]["stale_triage_entries"] == 0
    assert report["summary"]["statuses_by_active_flag"] == {
        "resolved_no_change": 14,
    }
    assert report["summary"]["unresolved_statuses_by_active_flag"] == {}
    assert report["summary"]["flags_by_code"] == {"patch_mismatch": 14}


def test_empirical_triage_report_reviews_unresolved_active_statuses(tmp_path) -> None:
    data = DeckseerData.load(Path("data"))

    for unresolved_status in ("needs_current_patch", "needs_scenario", "resolved_change_planned"):
        manifest = tmp_path / f"{unresolved_status}.json"
        payload = _manifest_payload()
        payload["entries"][0]["status"] = unresolved_status
        manifest.write_text(json.dumps(payload), encoding="utf-8")

        report = build_empirical_triage_report(
            data,
            empirical_stats_paths=discover_empirical_stats(Path("data")),
            triage_manifest_path=manifest,
        )

        assert report["status"] == "review"
        assert report["summary"]["resolved_active_flags"] == 13
        assert report["summary"]["unresolved_active_flags"] == 1
        assert report["summary"]["unresolved_statuses_by_active_flag"] == {unresolved_status: 1}


def test_empirical_triage_report_detects_missing_entry(tmp_path) -> None:
    data = DeckseerData.load(Path("data"))
    manifest = tmp_path / "triage.json"
    payload = _manifest_payload()
    payload["entries"] = payload["entries"][:-1]
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    report = build_empirical_triage_report(
        data,
        empirical_stats_paths=discover_empirical_stats(Path("data")),
        triage_manifest_path=manifest,
    )

    assert report["status"] == "review"
    assert report["summary"]["missing_triage_entries"] == 1
    assert report["summary"]["resolved_active_flags"] == 13
    assert report["summary"]["unresolved_active_flags"] == 1
    assert report["summary"]["unresolved_statuses_by_active_flag"] == {"missing_triage": 1}
    assert report["missing_triage"][0]["card_id"] == "spectrum_shift"


def test_empirical_triage_report_detects_stale_entry(tmp_path) -> None:
    data = DeckseerData.load(Path("data"))
    manifest = tmp_path / "triage.json"
    payload = _manifest_payload()
    payload["entries"].append(
        {
            "id": "stale_old_flag",
            "empirical_file": "data/empirical/necrobinder_sts2fun_all_patches_reviewed.json",
            "card_id": "not_active_anymore",
            "flag_code": "patch_mismatch",
            "status": "resolved_no_change",
            "decision": "Stale test entry.",
            "next_action": "Remove this stale triage row.",
            "reviewer_notes": "Fixture only.",
            "reviewed_at": "2026-05-23",
        }
    )
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    report = build_empirical_triage_report(
        data,
        empirical_stats_paths=discover_empirical_stats(Path("data")),
        triage_manifest_path=manifest,
    )

    assert report["status"] == "review"
    assert report["summary"]["stale_triage_entries"] == 1
    assert report["stale_triage"][0]["id"] == "stale_old_flag"


def test_empirical_triage_cli_json_includes_summary(capsys) -> None:
    status = main(["empirical-triage-report", "--format", "json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["summary"]["active_flags"] == 14
    assert payload["summary"]["triaged_flags"] == 14
    assert payload["summary"]["resolved_active_flags"] == 14
    assert payload["summary"]["unresolved_active_flags"] == 0
    assert payload["missing_triage"] == []
    assert payload["stale_triage"] == []
    assert "next_actions" in payload["summary"]


def test_empirical_triage_cli_text_names_forbidden_grimoire(capsys) -> None:
    status = main(["empirical-triage-report", "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Empirical Triage: PASS" in captured.out
    assert "Active flags: 14 | Triaged: 14 | Resolved: 14 | Unresolved: 0 | Missing: 0 | Stale: 0 | Open: 0" in captured.out
    assert "forbidden_grimoire - Forbidden Grimoire [patch_mismatch, resolved_no_change]" in captured.out
    assert "Use data/empirical/necrobinder_sts2fun_current_patch_reviewed.json for patch-specific Forbidden Grimoire review." in captured.out
    assert "high_prior_weak_empirical" not in captured.out


def test_empirical_triage_cli_fail_on_open_returns_failure(tmp_path, capsys) -> None:
    manifest = tmp_path / "triage.json"
    payload = _manifest_payload()
    payload["entries"][0]["status"] = "open"
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    status = main(["empirical-triage-report", "--manifest", str(manifest), "--fail-on-open"])

    captured = capsys.readouterr()

    assert status == 1
    assert "Open: 1" in captured.out


def _manifest_payload() -> dict:
    return json.loads(TRIAGE.read_text(encoding="utf-8"))
