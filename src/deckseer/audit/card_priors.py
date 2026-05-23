from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from deckseer.data_loader import DeckseerData
from deckseer.models import CardData, DataError, ValidationError


EMPIRICAL_REVIEW_STATUSES = frozenset({"seed", "proposed", "accepted", "rejected"})


@dataclass(frozen=True)
class EmpiricalCardStat:
    card_id: str
    character: str
    patch: str
    source: str
    sample_size: int
    pick_rate: float
    win_rate: float
    impact: float
    act: str = "all"
    ascension: str = "all"
    source_url: str | None = None
    captured_at: str | None = None
    stat_definition: str | None = None
    reviewer_notes: str | None = None
    review_status: str = "seed"

    @classmethod
    def from_dict(cls, raw: Any, source_label: str) -> "EmpiricalCardStat":
        if not isinstance(raw, dict):
            raise ValidationError(f"{source_label} must be an object")
        return cls(
            card_id=_require_str(raw.get("card_id"), f"{source_label}.card_id"),
            character=_require_str(raw.get("character"), f"{source_label}.character"),
            patch=_require_str(raw.get("patch"), f"{source_label}.patch"),
            source=_require_str(raw.get("source"), f"{source_label}.source"),
            sample_size=_require_int(raw.get("sample_size"), f"{source_label}.sample_size"),
            pick_rate=_require_float(raw.get("pick_rate"), f"{source_label}.pick_rate"),
            win_rate=_require_float(raw.get("win_rate"), f"{source_label}.win_rate"),
            impact=_require_float(raw.get("impact"), f"{source_label}.impact"),
            act=_require_str(raw.get("act", "all"), f"{source_label}.act"),
            ascension=_require_str(raw.get("ascension", "all"), f"{source_label}.ascension"),
            source_url=_optional_str(raw.get("source_url"), f"{source_label}.source_url"),
            captured_at=_optional_str(raw.get("captured_at"), f"{source_label}.captured_at"),
            stat_definition=_optional_str(raw.get("stat_definition"), f"{source_label}.stat_definition"),
            reviewer_notes=_optional_str(raw.get("reviewer_notes"), f"{source_label}.reviewer_notes"),
            review_status=_review_status(raw.get("review_status", "seed"), f"{source_label}.review_status"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "card_id": self.card_id,
            "character": self.character,
            "patch": self.patch,
            "source": self.source,
            "sample_size": self.sample_size,
            "pick_rate": self.pick_rate,
            "win_rate": self.win_rate,
            "impact": self.impact,
            "act": self.act,
            "ascension": self.ascension,
            "source_url": self.source_url,
            "captured_at": self.captured_at,
            "stat_definition": self.stat_definition,
            "reviewer_notes": self.reviewer_notes,
            "review_status": self.review_status,
        }


@dataclass(frozen=True)
class AuditFlag:
    code: str
    severity: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
        }


@dataclass(frozen=True)
class CardPriorAuditRow:
    card_id: str
    name: str
    character: str
    quality_prior: float | None
    empirical_impact: float | None
    sample_size: int | None
    patch: str | None
    flags: tuple[AuditFlag, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "card_id": self.card_id,
            "name": self.name,
            "character": self.character,
            "quality_prior": self.quality_prior,
            "empirical_impact": self.empirical_impact,
            "sample_size": self.sample_size,
            "patch": self.patch,
            "flags": [flag.to_dict() for flag in self.flags],
        }


@dataclass(frozen=True)
class CardPriorAuditResult:
    audit_type: str
    empirical_source: str
    rows: tuple[CardPriorAuditRow, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "audit_type": self.audit_type,
            "empirical_source": self.empirical_source,
            "summary": _audit_summary(self.rows),
            "rows": [row.to_dict() for row in self.rows],
        }


def load_empirical_card_stats(path: Path) -> tuple[EmpiricalCardStat, ...]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw_stats = json.load(handle)
    except FileNotFoundError as exc:
        raise DataError(f"Empirical stats file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path} is not valid JSON: {exc}") from exc

    if not isinstance(raw_stats, list):
        raise ValidationError(f"{path} must contain a list of empirical card stat records")
    return tuple(EmpiricalCardStat.from_dict(raw, f"{path.name}[{index}]") for index, raw in enumerate(raw_stats))


def audit_card_priors(
    data: DeckseerData,
    stats: tuple[EmpiricalCardStat, ...],
    *,
    empirical_source: str,
    min_sample_size: int = 300,
) -> CardPriorAuditResult:
    rows = [_audit_stat(data.cards_by_id.get(stat.card_id), stat, min_sample_size) for stat in stats]
    rows.sort(key=lambda row: (0 if row.flags else 1, row.card_id))
    return CardPriorAuditResult(
        audit_type="card_prior_empirical_review",
        empirical_source=empirical_source,
        rows=tuple(rows),
    )


def _audit_stat(card: CardData | None, stat: EmpiricalCardStat, min_sample_size: int) -> CardPriorAuditRow:
    flags: list[AuditFlag] = []
    if card is None:
        flags.append(
            AuditFlag(
                code="missing_card_data",
                severity="warning",
                message="Empirical stat exists for a card missing from Deckseer data.",
            )
        )
        return CardPriorAuditRow(
            card_id=stat.card_id,
            name=stat.card_id,
            character=stat.character,
            quality_prior=None,
            empirical_impact=stat.impact,
            sample_size=stat.sample_size,
            patch=stat.patch,
            flags=tuple(flags),
        )

    if stat.sample_size < min_sample_size:
        flags.append(
            AuditFlag(
                code="small_sample_size",
                severity="info",
                message=f"Sample size below review threshold ({stat.sample_size} < {min_sample_size}); avoid changing priors from this alone.",
            )
        )
    if card.source_patch is None:
        flags.append(
            AuditFlag(
                code="missing_source_patch",
                severity="warning",
                message="Deckseer card prior has no source patch recorded.",
            )
        )
    elif card.source_patch != stat.patch:
        flags.append(
            AuditFlag(
                code="patch_mismatch",
                severity="warning",
                message=f"Deckseer prior patch {card.source_patch} differs from empirical patch {stat.patch}.",
            )
        )

    if stat.sample_size >= min_sample_size:
        if card.quality_prior >= 3 and stat.impact <= -0.03:
            flags.append(
                AuditFlag(
                    code="high_prior_weak_empirical",
                    severity="review",
                    message="High Deckseer prior conflicts with weak empirical impact.",
                )
            )
        if card.quality_prior <= 0 and stat.impact >= 0.06:
            flags.append(
                AuditFlag(
                    code="low_prior_strong_empirical",
                    severity="review",
                    message="Low Deckseer prior conflicts with strong empirical impact.",
                )
            )

    return CardPriorAuditRow(
        card_id=card.id,
        name=card.name,
        character=card.character,
        quality_prior=card.quality_prior,
        empirical_impact=stat.impact,
        sample_size=stat.sample_size,
        patch=stat.patch,
        flags=tuple(flags),
    )


def _audit_summary(rows: tuple[CardPriorAuditRow, ...]) -> dict[str, Any]:
    flagged_rows = [row for row in rows if row.flags]
    flags_by_code = Counter(flag.code for row in rows for flag in row.flags)
    flags_by_severity = Counter(flag.severity for row in rows for flag in row.flags)
    rows_by_character = Counter(row.character for row in rows)
    flagged_rows_by_character = Counter(row.character for row in flagged_rows)
    return {
        "rows": len(rows),
        "flagged_rows": len(flagged_rows),
        "clean_rows": len(rows) - len(flagged_rows),
        "flags": sum(flags_by_code.values()),
        "flags_by_code": _sort_counts(flags_by_code),
        "flags_by_severity": _sort_counts(flags_by_severity),
        "rows_by_character": _sort_counts(rows_by_character),
        "flagged_rows_by_character": _sort_counts(flagged_rows_by_character),
    }


def _sort_counts(counts: Counter[str]) -> dict[str, int]:
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _require_str(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{label} must be a non-empty string")
    return value


def _optional_str(value: Any, label: str) -> str | None:
    if value is None:
        return None
    return _require_str(value, label)


def _review_status(value: Any, label: str) -> str:
    status = _require_str(value, label)
    if status not in EMPIRICAL_REVIEW_STATUSES:
        allowed = ", ".join(sorted(EMPIRICAL_REVIEW_STATUSES))
        raise ValidationError(f"{label} must be one of: {allowed}")
    return status


def _require_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValidationError(f"{label} must be a non-negative integer")
    return value


def _require_float(value: Any, label: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValidationError(f"{label} must be a number")
    return float(value)
