from __future__ import annotations

import json
from pathlib import Path

from deckseer.cli import main
from deckseer.data_loader import DeckseerData
from deckseer.normalization import normalize_run_payload


def _data() -> DeckseerData:
    return DeckseerData.load(Path("data"))


def _payload() -> dict:
    return {
        "character": "ironclad",
        "act": 1,
        "floor": 4,
        "hp": {"current": 70, "max": 80},
        "deck": [
            {"id": "Strike", "upgraded": False, "count": 2},
            {"id": "Defend", "upgraded": False, "count": 4},
            {"id": "Bash", "upgraded": False, "count": 1},
        ],
        "relics": [],
        "potions": [],
        "card_reward": ["Pommel Strike", "Shrug It Off", "anger"],
    }


def test_normalize_run_payload_rewrites_exact_display_names() -> None:
    report = normalize_run_payload(_payload(), _data())

    assert report["changed"] is True
    assert report["unresolved"] == []
    assert report["payload"]["deck"][0]["id"] == "strike"
    assert report["payload"]["card_reward"] == ["pommel_strike", "shrug_it_off", "anger"]
    assert {"field": "card_reward[0]", "from": "Pommel Strike", "to": "pommel_strike"} in report["changes"]


def test_normalize_run_payload_reports_typos_without_rewriting() -> None:
    payload = _payload()
    payload["card_reward"] = ["defragmant", "Shrug It Off"]

    report = normalize_run_payload(payload, _data())

    assert report["payload"]["card_reward"] == ["defragmant", "shrug_it_off"]
    assert report["unresolved"][0]["field"] == "card_reward[0]"
    assert report["unresolved"][0]["suggestions"][0] == "defragment"


def test_normalize_run_cli_writes_payload_and_prints_report(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "run.json"
    output_path = tmp_path / "normalized.json"
    input_path.write_text(json.dumps(_payload()), encoding="utf-8")

    status = main(["normalize-run", str(input_path), "--output", str(output_path)])

    captured = capsys.readouterr()
    report = json.loads(captured.out)
    normalized = json.loads(output_path.read_text(encoding="utf-8"))

    assert status == 0
    assert report["normalization_type"] == "run_card_ids"
    assert normalized["deck"][0]["id"] == "strike"
    assert normalized["card_reward"] == ["pommel_strike", "shrug_it_off", "anger"]
