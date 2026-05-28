from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any

from deckseer.data_loader import DeckseerData
from deckseer.importers.exporter_state import inspect_exporter_state
from deckseer.models import DataError, ValidationError


DEFAULT_EXPORT_STATE = Path(os.environ.get("LOCALAPPDATA", ".")) / "Deckseer" / "exports" / "latest_state.json"


@dataclass(frozen=True)
class ExportAlert:
    severity: str
    code: str
    message: str
    detail: str | None = None
    codex_attention: bool = True
    next_step: str | None = None


@dataclass(frozen=True)
class ExportAlertCatalog:
    card_ids: frozenset[str]
    relic_ids: frozenset[str]
    potion_ids: frozenset[str]


@dataclass(frozen=True)
class ExportAlertReport:
    path: Path
    screen_type: str | None
    exported_at: str | None
    alerts: tuple[ExportAlert, ...]
    error: str | None = None

    @property
    def has_alerts(self) -> bool:
        return bool(self.alerts)

    def fingerprint(self) -> tuple[str | None, str | None, tuple[tuple[str, str, str, str | None, bool], ...], str | None]:
        return (
            self.screen_type,
            self.exported_at,
            tuple((alert.severity, alert.code, alert.message, alert.detail, alert.codex_attention) for alert in self.alerts),
            self.error,
        )


def load_export_alert_catalog(data_dir: Path | None) -> ExportAlertCatalog | None:
    if data_dir is None:
        return None
    try:
        data = DeckseerData.load(data_dir)
    except (DataError, ValidationError):
        return None
    return ExportAlertCatalog(
        card_ids=frozenset(data.cards_by_id),
        relic_ids=frozenset(data.relics_by_id),
        potion_ids=frozenset(data.potions_by_id),
    )


def evaluate_export_alerts(
    path: Path = DEFAULT_EXPORT_STATE,
    *,
    catalog: ExportAlertCatalog | None = None,
) -> ExportAlertReport:
    try:
        inspected = inspect_exporter_state(path)
    except (DataError, ValidationError) as exc:
        return ExportAlertReport(
            path=path,
            screen_type=None,
            exported_at=None,
            alerts=(ExportAlert("high", "exporter_state_unreadable", "Deckseer cannot read the exporter state.", str(exc)),),
            error=str(exc),
        )

    metadata = inspected.metadata
    diagnostics = _mapping(metadata.get("diagnostics"))
    alerts: list[ExportAlert] = []

    if inspected.screen_type == "card_reward":
        alerts.append(
            ExportAlert(
                "high",
                "card_reward_ready",
                "Card reward export is recommendation-ready. Pause and inspect before choosing.",
                codex_attention=False,
                next_step="Inspect the export, confirm the visible screen, then run recommend-export --confirmed.",
            )
        )
    elif inspected.screen_type == "relic_reward":
        alerts.append(
            ExportAlert(
                "high",
                "relic_reward_ready",
                "Relic reward export is recommendation-ready. Pause and inspect before choosing.",
                codex_attention=False,
                next_step="Inspect the export, confirm the visible screen, then run recommend-export --confirmed.",
            )
        )

    route = _mapping(diagnostics.get("event_special_route"))
    if route:
        alerts.extend(_event_route_alerts(route))

    alerts.extend(
        _refusal_alerts(
            diagnostics,
            "card_reward_live_export_refusal_reasons",
            "card_reward_export_blocked",
            catalog,
        )
    )
    alerts.extend(
        _refusal_alerts(
            diagnostics,
            "relic_reward_live_export_refusal_reasons",
            "relic_reward_export_blocked",
            catalog,
        )
    )
    alerts.extend(_diagnostic_error_alerts(diagnostics))

    return ExportAlertReport(
        path=path,
        screen_type=inspected.screen_type,
        exported_at=metadata.get("exported_at") if isinstance(metadata.get("exported_at"), str) else None,
        alerts=tuple(alerts),
    )


def render_export_alert_report(report: ExportAlertReport, *, loud: bool = True) -> str:
    prefix = "\a" if loud and report.has_alerts else ""
    if not report.has_alerts:
        return f"{prefix}Deckseer export alert: no important state detected.\nCodex attention: no."

    lines = [
        prefix + "!" * 72,
        "IMPORTANT DECKSEER EXPORTER STATE",
        "!" * 72,
        f"file: {report.path}",
    ]
    if report.screen_type is not None:
        lines.append(f"screen_type: {report.screen_type}")
    if report.exported_at is not None:
        lines.append(f"exported_at: {report.exported_at}")
    lines.append("")
    for alert in report.alerts:
        lines.append(f"[{alert.severity.upper()}] {alert.code}: {alert.message}")
        lines.append(f"  Codex attention: {'yes' if alert.codex_attention else 'no'}")
        if alert.detail:
            lines.append(f"  {alert.detail}")
        if alert.next_step:
            lines.append(f"  Next step: {alert.next_step}")
    lines.append("")
    if any(alert.codex_attention for alert in report.alerts):
        lines.append("Pause the run, then inspect the export before choosing or sending it to Codex.")
    else:
        lines.append("Pause only long enough to inspect and confirm before using Deckseer advice.")
    return "\n".join(lines)


def _event_route_alerts(route: dict[str, Any]) -> list[ExportAlert]:
    alerts: list[ExportAlert] = []
    if route.get("last_event") == "choose_relic_selection_screen_shown":
        alerts.append(
            ExportAlert(
                "high",
                "choose_relic_overlay_seen",
                "Choose-relic overlay detected. This is the rare proof target; pause before picking.",
                _route_detail(route),
                next_step="Send this export to Codex before choosing.",
            )
        )
        return alerts

    if route.get("active") is not True:
        return alerts

    last_event = route.get("last_event")
    source = route.get("observation_source")
    if last_event in {"choose_bundle_selection_screen_shown", "deck_enchant_selection_screen_shown"}:
        return alerts
    if source != "public_event_layout_options":
        alerts.append(
            ExportAlert(
                "medium",
                "unexpected_event_route_seen",
                "Unexpected event route shape detected. Pause if it looks interesting.",
                _route_detail(route),
                next_step="Send this export to Codex if the visible screen is new or surprising.",
            )
        )
    return alerts


def _refusal_alerts(
    diagnostics: dict[str, Any],
    key: str,
    code: str,
    catalog: ExportAlertCatalog | None,
) -> list[ExportAlert]:
    reasons = diagnostics.get(key)
    if not isinstance(reasons, list):
        return []
    if _is_pre_collection_mixed_reward_status(diagnostics, reasons):
        return []
    interesting: list[str] = []
    review_ids: list[str] = []
    locally_known_ids: list[str] = []
    for reason in reasons:
        reason_text = str(reason)
        if reason_text not in _REVIEW_WORTHY_REFUSAL_REASONS:
            continue
        if reason_text in _MAPPING_REFUSAL_REASONS:
            review = _mapping_reason_review(diagnostics, code, reason_text, catalog)
            review_ids.extend(review.review_ids)
            locally_known_ids.extend(review.locally_known_ids)
            if not review.should_alert:
                continue
        interesting.append(reason_text)
    if not interesting:
        return []
    detail_parts = ["reasons: " + ", ".join(interesting)]
    if review_ids:
        detail_parts.append("review ids: " + ", ".join(_unique_sorted(review_ids)))
    if locally_known_ids:
        detail_parts.append("already in local data: " + ", ".join(_unique_sorted(locally_known_ids)))
    return [
        ExportAlert(
            "medium",
            code,
            "Exporter found review-worthy mapping or shape blockers.",
            "; ".join(detail_parts),
            next_step="Send this export to Codex if the review ids are new or the screen matters.",
        ),
    ]


def _is_pre_collection_mixed_reward_status(diagnostics: dict[str, Any], reasons: list[Any]) -> bool:
    if "mixed_reward_screen_state_may_change" not in reasons:
        return False
    if diagnostics.get("card_reward_live_export_mixed_reward_freshness_status") == "awaiting_reward_collected":
        return True
    blockers = diagnostics.get("card_reward_live_export_mixed_reward_freshness_blockers")
    return isinstance(blockers, list) and "reward_collection_not_observed" in blockers


def _diagnostic_error_alerts(diagnostics: dict[str, Any]) -> list[ExportAlert]:
    alerts: list[ExportAlert] = []
    for key, value in diagnostics.items():
        if key.endswith("_error") and value:
            alerts.append(
                ExportAlert(
                    "medium",
                    "exporter_diagnostic_error",
                    "Exporter diagnostic reported an error.",
                    f"{key}: {value}",
                    next_step="Send this export to Codex.",
                )
            )
    return alerts


def _route_detail(route: dict[str, Any]) -> str:
    visible_count = route.get("visible_option_count")
    return (
        f"last_event={route.get('last_event')}, "
        f"source={route.get('observation_source')}, "
        f"visible_option_count={visible_count}"
    )


def _mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return json.loads(json.dumps(value))
    return {}


@dataclass(frozen=True)
class _MappingReasonReview:
    should_alert: bool
    review_ids: tuple[str, ...] = ()
    locally_known_ids: tuple[str, ...] = ()


_REVIEW_WORTHY_REFUSAL_REASONS = {
    "unknown_reward_card",
    "unknown_deck_card",
    "unmapped_relic",
    "unmapped_owned_relic",
    "unmapped_reward_relic",
    "unmapped_potion",
    "unsupported_upgraded_reward_card",
    "unsupported_reward_shape",
    "unknown_event_special_route",
}

_MAPPING_REFUSAL_REASONS = {
    "unknown_reward_card",
    "unknown_deck_card",
    "unmapped_relic",
    "unmapped_owned_relic",
    "unmapped_reward_relic",
    "unmapped_potion",
}

_REVIEW_ITEMS_BY_REASON = {
    "unknown_reward_card": "card_identity_review_items",
    "unknown_deck_card": "deck_identity_review_items",
    "unmapped_relic": "relic_identity_review_items",
    "unmapped_owned_relic": "relic_identity_review_items",
    "unmapped_reward_relic": "relic_reward_identity_review_items",
    "unmapped_potion": "potion_identity_review_items",
}

_COUNT_KEYS_BY_ALERT_CODE = {
    "card_reward_export_blocked": {
        "unknown_reward_card": "card_reward_live_export_unmapped_reward_count",
        "unknown_deck_card": "card_reward_live_export_unmapped_deck_count",
        "unmapped_relic": "card_reward_live_export_unmapped_relic_count",
        "unmapped_owned_relic": "card_reward_live_export_unmapped_relic_count",
        "unmapped_potion": "card_reward_live_export_unmapped_potion_count",
    },
    "relic_reward_export_blocked": {
        "unknown_deck_card": "relic_reward_live_export_unmapped_deck_count",
        "unmapped_relic": "relic_reward_live_export_unmapped_owned_relic_count",
        "unmapped_owned_relic": "relic_reward_live_export_unmapped_owned_relic_count",
        "unmapped_reward_relic": "relic_reward_live_export_unmapped_reward_relic_count",
        "unmapped_potion": "relic_reward_live_export_unmapped_potion_count",
    },
}


def _mapping_reason_review(
    diagnostics: dict[str, Any],
    alert_code: str,
    reason: str,
    catalog: ExportAlertCatalog | None,
) -> _MappingReasonReview:
    items = [
        item
        for item in _review_items(diagnostics, reason)
        if _is_unmapped_review_item(item)
    ]
    count = _unmapped_count(diagnostics, alert_code, reason)
    if not items:
        if count == 0:
            return _MappingReasonReview(should_alert=False)
        return _MappingReasonReview(should_alert=True)

    ids = tuple(_candidate_id(item) for item in items)
    candidate_ids = tuple(candidate_id for candidate_id in ids if candidate_id is not None)
    if catalog is None:
        return _MappingReasonReview(should_alert=True, review_ids=candidate_ids)

    catalog_ids = _catalog_ids_for_reason(catalog, reason)
    locally_known = tuple(candidate_id for candidate_id in candidate_ids if candidate_id in catalog_ids)
    needs_review = tuple(candidate_id for candidate_id in candidate_ids if candidate_id not in catalog_ids)
    missing_candidate_id = any(candidate_id is None for candidate_id in ids)
    return _MappingReasonReview(
        should_alert=bool(needs_review or missing_candidate_id),
        review_ids=needs_review,
        locally_known_ids=locally_known,
    )


def _review_items(diagnostics: dict[str, Any], reason: str) -> tuple[dict[str, Any], ...]:
    key = _REVIEW_ITEMS_BY_REASON.get(reason)
    if key is None:
        return ()
    raw_items = diagnostics.get(key)
    if not isinstance(raw_items, list):
        return ()
    return tuple(item for item in raw_items if isinstance(item, dict))


def _is_unmapped_review_item(item: dict[str, Any]) -> bool:
    status = item.get("deckseer_mapping_status")
    return status == "unknown" or item.get("deckseer_id") in (None, "")


def _candidate_id(item: dict[str, Any]) -> str | None:
    for key in ("normalized_candidate_id", "deckseer_id"):
        value = item.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _unmapped_count(diagnostics: dict[str, Any], alert_code: str, reason: str) -> int | None:
    key = _COUNT_KEYS_BY_ALERT_CODE.get(alert_code, {}).get(reason)
    if key is None:
        return None
    value = diagnostics.get(key)
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _catalog_ids_for_reason(catalog: ExportAlertCatalog, reason: str) -> frozenset[str]:
    if reason in {"unknown_reward_card", "unknown_deck_card"}:
        return catalog.card_ids
    if reason == "unmapped_potion":
        return catalog.potion_ids
    return catalog.relic_ids


def _unique_sorted(values: list[str]) -> list[str]:
    return sorted(set(values))
