from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from deckseer.data_loader import DeckseerData
from deckseer.models import DataError, DeckseerError, ValidationError
from deckseer.relic_choice import RelicChoiceState, recommend_relic_choice


SUPPORTED_REVIEW_STATUSES = frozenset({"proposed", "accepted", "implemented", "rejected"})


@dataclass(frozen=True)
class RelicAccuracyScenario:
    id: str
    path: Path
    expected_top_choice: str
    expected_reason_keywords: tuple[str, ...]
    source: str
    review_status: str
    notes: str | None = None

    @classmethod
    def from_dict(cls, raw: Any, label: str) -> "RelicAccuracyScenario":
        data = _require_mapping(raw, label)
        expected_reason_keywords = tuple(
            _require_str(keyword, f"{label}.expected_reason_keywords[{index}]")
            for index, keyword in enumerate(
                _require_list(data.get("expected_reason_keywords"), f"{label}.expected_reason_keywords")
            )
        )
        if not expected_reason_keywords:
            raise ValidationError(f"{label}.expected_reason_keywords must include at least one keyword")
        review_status = _require_str(data.get("review_status"), f"{label}.review_status")
        if review_status not in SUPPORTED_REVIEW_STATUSES:
            allowed = ", ".join(sorted(SUPPORTED_REVIEW_STATUSES))
            raise ValidationError(f"{label}.review_status must be one of: {allowed}")
        return cls(
            id=_require_str(data.get("id"), f"{label}.id"),
            path=Path(_require_str(data.get("path"), f"{label}.path")),
            expected_top_choice=_require_str(data.get("expected_top_choice"), f"{label}.expected_top_choice"),
            expected_reason_keywords=expected_reason_keywords,
            source=_require_str(data.get("source"), f"{label}.source"),
            review_status=review_status,
            notes=_optional_str(data.get("notes"), f"{label}.notes"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "path": str(self.path),
            "expected_top_choice": self.expected_top_choice,
            "expected_reason_keywords": list(self.expected_reason_keywords),
            "source": self.source,
            "review_status": self.review_status,
            "notes": self.notes,
        }


def load_relic_accuracy_scenarios(path: Path) -> tuple[RelicAccuracyScenario, ...]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except FileNotFoundError as exc:
        raise DataError(f"Relic accuracy scenario manifest not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path} is not valid JSON: {exc}") from exc

    data = _require_mapping(raw, "relic accuracy manifest")
    if data.get("manifest_type") != "relic_accuracy_scenarios":
        raise ValidationError(f"{path}.manifest_type must be relic_accuracy_scenarios")
    scenarios = _require_list(data.get("scenarios"), f"{path}.scenarios")
    parsed = tuple(RelicAccuracyScenario.from_dict(item, f"{path}.scenarios[{index}]") for index, item in enumerate(scenarios))
    duplicate_ids = [scenario_id for scenario_id, count in Counter(scenario.id for scenario in parsed).items() if count > 1]
    if duplicate_ids:
        labels = ", ".join(sorted(duplicate_ids))
        raise ValidationError(f"{path}.scenarios contains duplicate scenario id(s): {labels}")
    return parsed


def build_relic_accuracy_report(data: DeckseerData, *, manifest_path: Path) -> dict[str, Any]:
    scenarios = load_relic_accuracy_scenarios(manifest_path)
    checks = [_score_scenario(scenario, data) for scenario in scenarios]
    failed = [check for check in checks if not check["passed"]]
    review_status_counts = _count_by_key(checks, "review_status")
    passed_by_review_status = _count_by_key([check for check in checks if check["passed"]], "review_status")
    failed_by_review_status = _count_by_key(failed, "review_status")
    return {
        "report_type": "relic_accuracy_report",
        "status": "fail" if failed else "pass",
        "manifest_path": str(manifest_path),
        "summary": {
            "scenarios": len(checks),
            "passed": len(checks) - len(failed),
            "failed": len(failed),
            "failed_scenario_ids": [check["id"] for check in failed],
            "review_status_counts": review_status_counts,
            "passed_by_review_status": passed_by_review_status,
            "failed_by_review_status": failed_by_review_status,
        },
        "scenarios": checks,
    }


def _score_scenario(scenario: RelicAccuracyScenario, data: DeckseerData) -> dict[str, Any]:
    try:
        state = RelicChoiceState.from_json_file(scenario.path)
        result = recommend_relic_choice(state, data)
    except (DeckseerError, OSError) as exc:
        return {
            **scenario.to_dict(),
            "passed": False,
            "actual_top_choice": None,
            "actual_top_score": None,
            "actual_confidence": None,
            "matched_reason_keywords": [],
            "missing_reason_keywords": list(scenario.expected_reason_keywords),
            "error": str(exc),
        }

    top_choice = result.ranked_choices[0]
    matched_keywords = [
        keyword
        for keyword in scenario.expected_reason_keywords
        if _keyword_matches(keyword, top_choice.reasoning)
    ]
    missing_keywords = [
        keyword
        for keyword in scenario.expected_reason_keywords
        if keyword not in matched_keywords
    ]
    passed = top_choice.choice == scenario.expected_top_choice and not missing_keywords
    return {
        **scenario.to_dict(),
        "passed": passed,
        "actual_top_choice": top_choice.choice,
        "actual_top_score": round(top_choice.score, 1),
        "actual_confidence": top_choice.confidence,
        "matched_reason_keywords": matched_keywords,
        "missing_reason_keywords": missing_keywords,
        "error": None,
    }


def _keyword_matches(keyword: str, reasoning: tuple[str, ...]) -> bool:
    needle = keyword.lower()
    return any(needle in reason.lower() for reason in reasoning)


def _count_by_key(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: Counter[str] = Counter(item[key] for item in items)
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{label} must be an object")
    return value


def _require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValidationError(f"{label} must be a list")
    return value


def _require_str(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{label} must be a non-empty string")
    return value


def _optional_str(value: Any, label: str) -> str | None:
    if value is None:
        return None
    return _require_str(value, label)
