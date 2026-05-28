from __future__ import annotations

import re
from pathlib import Path

from deckseer.data_loader import DeckseerData


CARD_SNAPSHOT_SOURCE = Path("exporter_mod/DeckseerExporter/DeckseerExporterCode/CardIdentityRuntimeProbe.cs")
RELIC_POTION_SNAPSHOT_SOURCE = Path("exporter_mod/DeckseerExporter/DeckseerExporterCode/RelicPotionIdentityReviewProbe.cs")


def test_exporter_status_mapping_snapshot_covers_deckseer_card_ids() -> None:
    data = DeckseerData.load(data_dir=Path("data"))
    snapshot_ids = _extract_deckseer_card_ids(CARD_SNAPSHOT_SOURCE)

    missing_ids = sorted(set(data.cards_by_id) - snapshot_ids)

    assert missing_ids == []


def test_exporter_status_mapping_snapshot_includes_reviewed_public_id_aliases() -> None:
    aliases = _extract_deckseer_card_id_aliases(CARD_SNAPSHOT_SOURCE)

    assert aliases["strike_ironclad"] == "strike"
    assert aliases["defend_ironclad"] == "defend"
    assert aliases["strike_silent"] == "strike"
    assert aliases["defend_silent"] == "defend"


def test_exporter_status_mapping_snapshot_covers_deckseer_relic_ids() -> None:
    data = DeckseerData.load(data_dir=Path("data"))
    snapshot_ids = _extract_deckseer_relic_ids(RELIC_POTION_SNAPSHOT_SOURCE)

    missing_ids = sorted(set(data.relics_by_id) - snapshot_ids)

    assert missing_ids == []


def test_exporter_status_mapping_snapshot_covers_deckseer_potion_ids() -> None:
    data = DeckseerData.load(data_dir=Path("data"))
    snapshot_ids = _extract_deckseer_potion_ids(RELIC_POTION_SNAPSHOT_SOURCE)

    missing_ids = sorted(set(data.potions_by_id) - snapshot_ids)

    assert missing_ids == []


def _extract_deckseer_card_ids(path: Path) -> set[str]:
    source = path.read_text(encoding="utf-8")
    match = re.search(
        r"private static readonly HashSet<string> DeckseerCardIds = new\(StringComparer\.Ordinal\)\s*\{(?P<body>.*?)\};",
        source,
        re.DOTALL,
    )
    assert match is not None, "Could not find DeckseerCardIds mapping snapshot"

    return set(re.findall(r'"([^"]+)"', match.group("body")))


def _extract_deckseer_card_id_aliases(path: Path) -> dict[str, str]:
    source = path.read_text(encoding="utf-8")
    match = re.search(
        r"private static readonly IReadOnlyDictionary<string, string> DeckseerCardIdAliases = new Dictionary<string, string>\(StringComparer\.Ordinal\)\s*\{(?P<body>.*?)\};",
        source,
        re.DOTALL,
    )
    assert match is not None, "Could not find DeckseerCardIdAliases mapping snapshot"

    return dict(re.findall(r'\["([^"]+)"\]\s*=\s*"([^"]+)"', match.group("body")))


def _extract_deckseer_relic_ids(path: Path) -> set[str]:
    source = path.read_text(encoding="utf-8")
    match = re.search(
        r"private static readonly HashSet<string> DeckseerRelicIds = new\(StringComparer\.Ordinal\)\s*\{(?P<body>.*?)\};",
        source,
        re.DOTALL,
    )
    assert match is not None, "Could not find DeckseerRelicIds mapping snapshot"

    return set(re.findall(r'"([^"]+)"', match.group("body")))


def _extract_deckseer_potion_ids(path: Path) -> set[str]:
    source = path.read_text(encoding="utf-8")
    match = re.search(
        r"private static readonly HashSet<string> DeckseerPotionIds = new\(StringComparer\.Ordinal\)\s*\{(?P<body>.*?)\};",
        source,
        re.DOTALL,
    )
    assert match is not None, "Could not find DeckseerPotionIds mapping snapshot"

    return set(re.findall(r'"([^"]+)"', match.group("body")))
