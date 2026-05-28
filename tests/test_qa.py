from __future__ import annotations

import json
from pathlib import Path

from deckseer.cli import main
from deckseer.data_loader import DeckseerData
from deckseer.qa import (
    build_project_qa,
    build_recommendation_smoke_baseline,
    discover_empirical_stats,
    discover_example_runs,
)


def test_discover_empirical_stats_excludes_intake_and_finds_active_reviewed_stats() -> None:
    paths = discover_empirical_stats(Path("data"))

    assert [path.name for path in paths] == [
        "defect_sts2fun_current_patch_reviewed.json",
        "ironclad_sts2fun_current_patch_reviewed.json",
        "necrobinder_sts2fun_all_patches_reviewed.json",
        "necrobinder_sts2fun_current_patch_reviewed.json",
        "regent_sts2fun_current_patch_reviewed.json",
        "silent_sts2fun_current_patch_reviewed.json",
    ]


def test_discover_example_runs_finds_example_fixtures() -> None:
    paths = discover_example_runs(Path("examples"))

    assert [path.name for path in paths] == [
        "card_reward_basic.json",
        "defect_card_reward_basic.json",
        "necrobinder_card_reward_basic.json",
        "regent_card_reward_basic.json",
        "silent_card_reward_basic.json",
    ]


def test_project_qa_reports_review_status_for_active_empirical_flags() -> None:
    data = DeckseerData.load(Path("data"))
    report = build_project_qa(
        data,
        empirical_stats_paths=discover_empirical_stats(Path("data")),
        run_paths=discover_example_runs(Path("examples")),
        recommendation_baseline_path=Path("data/qa/recommendation_smoke_baseline.json"),
    )

    assert report["qa_type"] == "project_qa"
    assert report["status"] == "review"
    assert report["summary"]["data_health_status"] == "pass"
    assert report["summary"]["run_files"] == 5
    assert report["summary"]["run_blocked_files"] == 0
    assert report["summary"]["recommendation_smoke_passed"] == 5
    assert report["summary"]["recommendation_smoke_failed"] == 0
    assert report["summary"]["recommendation_baseline_checked"] is True
    assert report["summary"]["recommendation_baseline_mismatches"] == 0
    assert report["summary"]["empirical_audits"] == 6
    assert report["summary"]["empirical_flags"] == 14
    assert report["summary"]["empirical_flags_by_severity"] == {"warning": 14}
    assert report["summary"]["empirical_flags_by_code"] == {"patch_mismatch": 14}
    assert report["summary"]["empirical_coverage_checked"] is False
    assert report["empirical_coverage"] is None
    assert report["summary"]["empirical_triage_checked"] is False
    assert report["empirical_triage"] is None


def test_recommendation_smoke_baseline_generation_matches_checked_in_baseline() -> None:
    data = DeckseerData.load(Path("data"))
    baseline = build_recommendation_smoke_baseline(data, run_paths=discover_example_runs(Path("examples")))
    expected = json.loads(Path("data/qa/recommendation_smoke_baseline.json").read_text(encoding="utf-8"))

    assert baseline == expected


def test_project_qa_fails_when_run_file_is_blocked(tmp_path) -> None:
    bad_run = tmp_path / "bad_run.json"
    bad_run.write_text(
        json.dumps(
            {
                "game": "slay_the_spire_2",
                "character": "ironclad",
                "act": 1,
                "floor": 1,
                "ascension": 0,
                "gold": 99,
                "hp": {"current": 70, "max": 80},
                "deck": [{"id": "strike", "upgraded": False, "count": 4}],
                "relics": [],
                "potions": [],
                "card_reward": ["not_a_real_card"],
            }
        ),
        encoding="utf-8",
    )
    data = DeckseerData.load(Path("data"))

    report = build_project_qa(data, empirical_stats_paths=(), run_paths=(bad_run,))

    assert report["status"] == "fail"
    assert report["summary"]["run_files"] == 1
    assert report["summary"]["run_blocked_files"] == 1
    assert report["summary"]["recommendation_smoke_passed"] == 0
    assert report["summary"]["recommendation_smoke_failed"] == 1
    assert "not_a_real_card" in report["recommendation_smoke"]["checks"][0]["error"]


def test_qa_cli_text_smoke(capsys) -> None:
    status = main(["qa", "--check-recommendation-baseline"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Project QA: REVIEW" in captured.out
    assert "Data health: pass (0 failures)" in captured.out
    assert "Run files: 5 | Blocked: 0 | Deck metadata gaps: 0" in captured.out
    assert "Recommendation smoke: 5 passed | 0 failed" in captured.out
    assert "Recommendation baseline: checked | Mismatches: 0" in captured.out
    assert "Recommendation smoke top choices:" in captured.out
    assert "examples\\card_reward_basic.json: shrug_it_off" in captured.out
    assert "Empirical audits: 6 | Flags: 14" in captured.out
    assert "Accuracy scenarios:" not in captured.out
    assert "Empirical flag severity: warning=14" in captured.out
    assert "Empirical flag codes: patch_mismatch=14" in captured.out


def test_qa_cli_json_smoke(capsys) -> None:
    status = main(["qa", "--format", "json", "--check-recommendation-baseline"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["qa_type"] == "project_qa"
    assert payload["status"] == "review"
    assert payload["summary"]["run_files"] == 5
    assert payload["summary"]["run_blocked_files"] == 0
    assert payload["summary"]["recommendation_smoke_passed"] == 5
    assert payload["summary"]["recommendation_smoke_failed"] == 0
    assert payload["summary"]["recommendation_baseline_checked"] is True
    assert payload["summary"]["recommendation_baseline_mismatches"] == 0
    assert payload["summary"]["accuracy_checked"] is False
    assert payload["summary"]["accuracy_passed"] == 0
    assert payload["summary"]["accuracy_failed"] == 0
    assert payload["accuracy_report"] is None
    assert payload["summary"]["empirical_coverage_checked"] is False
    assert payload["empirical_coverage"] is None
    assert payload["summary"]["empirical_triage_checked"] is False
    assert payload["empirical_triage"] is None
    assert payload["summary"]["empirical_flags"] == 14
    assert payload["summary"]["empirical_flags_by_severity"] == {"warning": 14}


def test_qa_cli_fails_on_recommendation_baseline_mismatch(tmp_path, capsys) -> None:
    baseline_path = tmp_path / "bad_baseline.json"
    baseline_path.write_text(
        json.dumps(
            {
                "baseline_type": "recommendation_smoke_baseline",
                "entries": [
                    {
                        "path": "examples/card_reward_basic.json",
                        "top_choice": "anger",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    status = main(["qa", "--recommendation-baseline", str(baseline_path)])

    captured = capsys.readouterr()

    assert status == 1
    assert "Project QA: FAIL" in captured.out
    assert "Recommendation baseline: checked | Mismatches: 1" in captured.out
    assert "expected anger, got shrug_it_off" in captured.out


def test_qa_cli_can_include_accuracy_summary(capsys) -> None:
    status = main(["qa", "--check-accuracy"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Project QA: REVIEW" in captured.out
    assert "Accuracy scenarios: 10 passed | 0 failed" in captured.out


def test_qa_cli_can_include_empirical_coverage_summary(capsys) -> None:
    status = main(["qa", "--check-empirical-coverage"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Project QA: REVIEW" in captured.out
    assert "Empirical coverage: review | Rows: 18 | Missing characters: 0" in captured.out
    assert "Empirical coverage below target:" not in captured.out


def test_qa_cli_can_include_empirical_triage_summary(capsys) -> None:
    status = main(["qa", "--check-empirical-triage"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Project QA: PASS" in captured.out
    assert "Empirical triage: pass | Active flags: 14 | Triaged: 14 | Missing: 0 | Open: 0" in captured.out


def test_project_qa_passes_with_resolved_empirical_triage_checked() -> None:
    data = DeckseerData.load(Path("data"))

    report = build_project_qa(
        data,
        empirical_stats_paths=discover_empirical_stats(Path("data")),
        empirical_triage_manifest_path=Path("data/empirical/triage.json"),
    )

    assert report["status"] == "pass"
    assert report["summary"]["empirical_triage_checked"] is True
    assert report["summary"]["empirical_triage_status"] == "pass"
    assert report["summary"]["empirical_triage_active_flags"] == 14
    assert report["summary"]["empirical_triage_triaged_flags"] == 14
    assert report["summary"]["empirical_triage_missing_entries"] == 0


def test_project_qa_reviews_when_empirical_coverage_has_active_flags() -> None:
    data = DeckseerData.load(Path("data"))

    report = build_project_qa(
        data,
        empirical_stats_paths=discover_empirical_stats(Path("data")),
        empirical_coverage_min_rows_per_character=1,
    )

    assert report["status"] == "review"
    assert report["summary"]["empirical_coverage_checked"] is True
    assert report["summary"]["empirical_coverage_status"] == "review"
    assert report["summary"]["empirical_coverage_rows"] == 18
    assert report["summary"]["empirical_coverage_missing_characters"] == 0


def test_project_qa_fails_when_accuracy_scenario_mismatches(tmp_path) -> None:
    manifest_path = tmp_path / "bad_accuracy_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "manifest_type": "accuracy_scenarios",
                "scenarios": [
                    {
                        "id": "bad_expected_choice",
                        "path": "tests/fixtures/scenarios/early_act1_low_frontload.json",
                        "expected_top_choice": "inflame",
                        "expected_reason_keywords": ["frontload"],
                        "source": "test fixture",
                        "review_status": "accepted",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    data = DeckseerData.load(Path("data"))

    report = build_project_qa(
        data,
        empirical_stats_paths=(),
        run_paths=(),
        accuracy_manifest_path=manifest_path,
    )

    assert report["status"] == "fail"
    assert report["summary"]["accuracy_passed"] == 0
    assert report["summary"]["accuracy_failed"] == 1
    assert report["accuracy_report"]["summary"]["failed_scenario_ids"] == ["bad_expected_choice"]


def test_qa_cli_explicit_recommendation_baseline_path_still_works(capsys) -> None:
    status = main(["qa", "--recommendation-baseline", "data/qa/recommendation_smoke_baseline.json"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Recommendation baseline: checked | Mismatches: 0" in captured.out


def test_qa_baseline_cli_prints_baseline(capsys) -> None:
    status = main(["qa-baseline"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["baseline_type"] == "recommendation_smoke_baseline"
    assert payload["entries"][0] == {
        "path": "examples/card_reward_basic.json",
        "top_choice": "shrug_it_off",
    }


def test_qa_baseline_cli_can_write_output(tmp_path, capsys) -> None:
    output_path = tmp_path / "recommendation_baseline.json"

    status = main(["qa-baseline", "--run-paths", "examples/card_reward_basic.json", "--output", str(output_path)])

    captured = capsys.readouterr()
    printed = json.loads(captured.out)
    written = json.loads(output_path.read_text(encoding="utf-8"))

    assert status == 0
    assert printed == written
    assert written == {
        "baseline_type": "recommendation_smoke_baseline",
        "entries": [
            {
                "path": "examples/card_reward_basic.json",
                "top_choice": "shrug_it_off",
            }
        ],
    }


def test_qa_cli_fail_on_audit_flags_fails_when_active_empirical_flags_exist(capsys) -> None:
    status = main(["qa", "--fail-on-audit-flags"])

    captured = capsys.readouterr()

    assert status == 1
    assert "Project QA: FAIL" in captured.out
    assert "Empirical audits: 6 | Flags: 14" in captured.out


def test_qa_cli_can_fail_on_explicit_conflict_audit_fixture(capsys) -> None:
    status = main(
        [
            "qa",
            "--empirical-stats",
            "tests/fixtures/empirical/multi_class_conflict_stats.json",
            "--fail-on-audit-flags",
        ]
    )

    captured = capsys.readouterr()

    assert status == 1
    assert "Project QA: FAIL" in captured.out
    assert "Empirical audits: 1 | Flags: 6" in captured.out


def test_qa_cli_strict_checks_baseline_and_fails_on_active_empirical_flags(capsys) -> None:
    status = main(["qa", "--strict"])

    captured = capsys.readouterr()

    assert status == 1
    assert "Project QA: FAIL" in captured.out
    assert "Recommendation baseline: checked | Mismatches: 0" in captured.out
    assert "Empirical audits: 6 | Flags: 14" in captured.out


def test_qa_cli_can_use_explicit_clean_empirical_stats(tmp_path, capsys) -> None:
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

    status = main(["qa", "--empirical-stats", str(stats_path), "--run-paths", "--fail-on-audit-flags"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Project QA: PASS" in captured.out
    assert "Recommendation smoke: 0 passed | 0 failed" in captured.out
    assert "Empirical audits: 1 | Flags: 0" in captured.out
