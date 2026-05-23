from __future__ import annotations

import json
from pathlib import Path

from deckseer.audit.card_priors import audit_card_priors, load_empirical_card_stats
from deckseer.cli import main
from deckseer.data_loader import DeckseerData
from deckseer.empirical_promotion import build_empirical_promotion_report
from deckseer.models import ValidationError
from deckseer.qa import discover_empirical_stats


FIXTURES = Path("tests/fixtures/empirical")


def test_promotion_ready_draft_previews_without_writing(tmp_path) -> None:
    data = DeckseerData.load(Path("data"))
    data_dir = tmp_path / "data"
    output_path = data_dir / "empirical" / "reviewed_stats.json"

    report = build_empirical_promotion_report(
        data,
        FIXTURES / "valid_traceable_draft.json",
        output_path=output_path,
        data_dir=data_dir,
    )

    assert report["status"] == "pass"
    assert report["write_requested"] is False
    assert report["wrote_file"] is False
    assert not output_path.exists()
    assert report["payload"][0]["card_id"] == "adrenaline"
    assert "id" not in report["payload"][0]


def test_promotion_write_creates_active_json_without_draft_ids(tmp_path) -> None:
    data = DeckseerData.load(Path("data"))
    data_dir = tmp_path / "data"
    output_path = data_dir / "empirical" / "reviewed_stats.json"

    report = build_empirical_promotion_report(
        data,
        FIXTURES / "valid_traceable_draft.json",
        output_path=output_path,
        data_dir=data_dir,
        write=True,
    )

    written = json.loads(output_path.read_text(encoding="utf-8"))

    assert report["status"] == "pass"
    assert report["wrote_file"] is True
    assert written == report["payload"]
    assert "id" not in written[0]
    assert written[0]["source_url"] == "https://sts2.fun/"


def test_non_ready_draft_is_refused_without_writing(tmp_path) -> None:
    data = DeckseerData.load(Path("data"))
    data_dir = tmp_path / "data"
    output_path = data_dir / "empirical" / "reviewed_stats.json"

    report = build_empirical_promotion_report(
        data,
        FIXTURES / "review_flag_traceable_draft.json",
        output_path=output_path,
        data_dir=data_dir,
        write=True,
    )

    assert report["status"] == "review"
    assert report["summary"]["promotion_ready"] is False
    assert report["wrote_file"] is False
    assert not output_path.exists()


def test_allow_review_flags_writes_review_evidence(tmp_path) -> None:
    data = DeckseerData.load(Path("data"))
    data_dir = tmp_path / "data"
    output_path = data_dir / "empirical" / "reviewed_stats.json"

    report = build_empirical_promotion_report(
        data,
        FIXTURES / "review_flag_traceable_draft.json",
        output_path=output_path,
        data_dir=data_dir,
        write=True,
        allow_review_flags=True,
    )

    written = json.loads(output_path.read_text(encoding="utf-8"))

    assert report["status"] == "review"
    assert report["summary"]["promotion_ready"] is False
    assert report["allow_review_flags"] is True
    assert report["wrote_file"] is True
    assert written == report["payload"]


def test_existing_output_is_refused_without_replace(tmp_path) -> None:
    data = DeckseerData.load(Path("data"))
    data_dir = tmp_path / "data"
    output_path = data_dir / "empirical" / "reviewed_stats.json"
    output_path.parent.mkdir(parents=True)
    output_path.write_text("[]\n", encoding="utf-8")

    try:
        build_empirical_promotion_report(
            data,
            FIXTURES / "valid_traceable_draft.json",
            output_path=output_path,
            data_dir=data_dir,
            write=True,
        )
    except ValidationError as exc:
        assert "Refusing to overwrite existing empirical file" in str(exc)
    else:
        raise AssertionError("Expected existing output to require replace")


def test_replace_allows_existing_output(tmp_path) -> None:
    data = DeckseerData.load(Path("data"))
    data_dir = tmp_path / "data"
    output_path = data_dir / "empirical" / "reviewed_stats.json"
    output_path.parent.mkdir(parents=True)
    output_path.write_text("[]\n", encoding="utf-8")

    report = build_empirical_promotion_report(
        data,
        FIXTURES / "valid_traceable_draft.json",
        output_path=output_path,
        data_dir=data_dir,
        write=True,
        replace=True,
    )

    assert report["wrote_file"] is True
    assert json.loads(output_path.read_text(encoding="utf-8"))[0]["card_id"] == "adrenaline"


def test_output_outside_empirical_dir_is_refused(tmp_path) -> None:
    data = DeckseerData.load(Path("data"))
    data_dir = tmp_path / "data"
    output_path = tmp_path / "outside.json"

    try:
        build_empirical_promotion_report(
            data,
            FIXTURES / "valid_traceable_draft.json",
            output_path=output_path,
            data_dir=data_dir,
        )
    except ValidationError as exc:
        assert "must be under" in str(exc)
    else:
        raise AssertionError("Expected unsafe output path to fail validation")


def test_output_under_drafts_dir_is_refused(tmp_path) -> None:
    data = DeckseerData.load(Path("data"))
    data_dir = tmp_path / "data"
    output_path = data_dir / "empirical" / "drafts" / "reviewed_stats.json"

    try:
        build_empirical_promotion_report(
            data,
            FIXTURES / "valid_traceable_draft.json",
            output_path=output_path,
            data_dir=data_dir,
        )
    except ValidationError as exc:
        assert "must not be under" in str(exc)
    else:
        raise AssertionError("Expected drafts output path to fail validation")


def test_promoted_file_is_discoverable_and_passes_audit(tmp_path) -> None:
    data = DeckseerData.load(Path("data"))
    data_dir = tmp_path / "data"
    output_path = data_dir / "empirical" / "reviewed_stats.json"
    build_empirical_promotion_report(
        data,
        FIXTURES / "valid_traceable_draft.json",
        output_path=output_path,
        data_dir=data_dir,
        write=True,
    )

    paths = discover_empirical_stats(data_dir)
    stats = load_empirical_card_stats(paths[0])
    audit = audit_card_priors(data, stats, empirical_source=str(paths[0]))

    assert paths == (output_path,)
    assert audit.to_dict()["summary"]["flags"] == 0


def test_empirical_promote_cli_preview_smoke(capsys) -> None:
    status = main(
        [
            "empirical-promote-draft",
            "tests/fixtures/empirical/valid_traceable_draft.json",
            "--output",
            "data/empirical/manual_preview.json",
        ]
    )

    captured = capsys.readouterr()

    assert status == 0
    assert "Empirical Promotion: PASS" in captured.out
    assert "Mode: preview | Wrote file: no | Review flags: blocked" in captured.out
    assert '"card_id": "adrenaline"' in captured.out
    assert not Path("data/empirical/manual_preview.json").exists()


def test_empirical_promote_cli_non_ready_returns_review(capsys) -> None:
    status = main(
        [
            "empirical-promote-draft",
            "tests/fixtures/empirical/review_flag_traceable_draft.json",
            "--output",
            "data/empirical/manual_preview.json",
        ]
    )

    captured = capsys.readouterr()

    assert status == 1
    assert "Empirical Promotion: REVIEW" in captured.out
    assert "Promotion ready: no" in captured.out

