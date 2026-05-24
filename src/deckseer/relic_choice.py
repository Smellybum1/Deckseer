from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any

from deckseer.data_loader import DeckseerData
from deckseer.models import (
    ChoiceRecommendation,
    DataError,
    DeckCard,
    Hp,
    RecommendationResult,
    RunContext,
    RunState,
    ValidationError,
    _require_int,
    _require_list,
    _require_mapping,
    _require_str,
)
from deckseer.scoring.rules import DeckProfile, RunNeed, build_deck_profile, diagnose_run_needs


@dataclass(frozen=True)
class RelicChoiceState:
    character: str
    act: int
    floor: int
    hp: Hp
    deck: tuple[DeckCard, ...]
    relics: tuple[str, ...]
    potions: tuple[str, ...]
    relic_reward: tuple[str, ...]
    game: str = "slay_the_spire_2"
    screen_type: str = "relic_reward"
    ascension: int = 0
    gold: int = 0
    run_context: RunContext = field(default_factory=RunContext)

    @classmethod
    def from_dict(cls, raw: Any) -> "RelicChoiceState":
        data = _require_mapping(raw, "relic choice state")
        deck = tuple(DeckCard.from_dict(item, index) for index, item in enumerate(_require_list(data.get("deck"), "deck")))
        relics = tuple(_require_str(item, f"relics[{index}]") for index, item in enumerate(_require_list(data.get("relics"), "relics")))
        potions = tuple(_require_str(item, f"potions[{index}]") for index, item in enumerate(_require_list(data.get("potions"), "potions")))
        relic_reward = tuple(
            _require_str(item, f"relic_reward[{index}]")
            for index, item in enumerate(_require_list(data.get("relic_reward"), "relic_reward"))
        )
        if not relic_reward:
            raise ValidationError("relic_reward must include at least one offered relic")
        if len(set(relic_reward)) != len(relic_reward):
            raise ValidationError("relic_reward must not include duplicate relic IDs")
        screen_type = _require_str(data.get("screen_type", "relic_reward"), "screen_type")
        if screen_type != "relic_reward":
            raise ValidationError("relic choice state must use screen_type relic_reward")
        return cls(
            game=_require_str(data.get("game", "slay_the_spire_2"), "game"),
            screen_type=screen_type,
            character=_require_str(data.get("character"), "character"),
            act=_require_int(data.get("act"), "act", minimum=1),
            floor=_require_int(data.get("floor"), "floor", minimum=0),
            ascension=_require_int(data.get("ascension", 0), "ascension", minimum=0),
            gold=_require_int(data.get("gold", 0), "gold", minimum=0),
            hp=Hp.from_dict(data.get("hp")),
            deck=deck,
            relics=relics,
            potions=potions,
            relic_reward=relic_reward,
            run_context=RunContext.from_dict(data.get("run_context")),
        )

    @classmethod
    def from_json_file(cls, path: Path) -> "RelicChoiceState":
        try:
            with path.open("r", encoding="utf-8") as handle:
                return cls.from_dict(json.load(handle))
        except json.JSONDecodeError as exc:
            raise ValidationError(f"{path} is not valid JSON: {exc}") from exc

    def to_run_proxy(self) -> RunState:
        return RunState(
            game=self.game,
            character=self.character,
            act=self.act,
            floor=self.floor,
            ascension=self.ascension,
            gold=self.gold,
            hp=self.hp,
            deck=self.deck,
            relics=self.relics,
            potions=self.potions,
            card_reward=("__relic_choice_placeholder__",),
            run_context=self.run_context,
        )


@dataclass(frozen=True)
class _ScoredRelic:
    choice: str
    name: str
    score: float
    reasons: tuple[str, ...]
    risks: tuple[str, ...]


def recommend_relic_choice(state: RelicChoiceState, data: DeckseerData) -> RecommendationResult:
    if state.game != "slay_the_spire_2":
        raise ValidationError("relic choice state only supports game slay_the_spire_2")

    missing_reward = sorted(relic_id for relic_id in state.relic_reward if relic_id not in data.relics_by_id)
    if missing_reward:
        raise DataError(f"Missing relic data for reward choices: {', '.join(missing_reward)}")

    run = state.to_run_proxy()
    profile = build_deck_profile(run, data.cards_by_id)
    needs = diagnose_run_needs(run, profile)
    contexts = _active_contexts(state, profile)
    owned_relics = [data.relics_by_id[relic_id] for relic_id in state.relics if relic_id in data.relics_by_id]
    unknown_owned = tuple(sorted(relic_id for relic_id in state.relics if relic_id not in data.relics_by_id))

    scored = [
        _score_relic(
            relic_id,
            data=data,
            profile=profile,
            needs=needs,
            contexts=contexts,
            owned_relics=owned_relics,
            unknown_owned=unknown_owned,
        )
        for relic_id in state.relic_reward
    ]
    scored.sort(key=lambda item: (-item.score, item.choice))

    confidence = _recommendation_confidence(scored, profile, needs, unknown_owned)
    return RecommendationResult(
        recommendation_type="relic_choice",
        ranked_choices=tuple(
            ChoiceRecommendation(
                choice=item.choice,
                name=item.name,
                rank=index + 1,
                score=item.score,
                confidence=confidence,
                reasoning=item.reasons,
                risks=item.risks,
            )
            for index, item in enumerate(scored)
        ),
    )


def _score_relic(
    relic_id: str,
    *,
    data: DeckseerData,
    profile: DeckProfile,
    needs: tuple[RunNeed, ...],
    contexts: frozenset[str],
    owned_relics: list[Any],
    unknown_owned: tuple[str, ...],
) -> _ScoredRelic:
    relic = data.relics_by_id[relic_id]
    solved_needs = _need_names_solved_by(relic.roles, relic.tags)
    top_need = needs[0] if needs else None
    score = 32 + relic.quality_prior * 2.0
    reasons: list[str] = ["Starts from a neutral relic-choice baseline."]
    risks: list[str] = ["Relic Choice V1 is tag-based and does not simulate combat."]

    for need in needs:
        if need.name in solved_needs:
            multiplier = 0.62 if need == top_need else 0.42
            delta = need.priority * multiplier
            score += delta
            reasons.append(need.reason)

    matching_contexts = sorted(relic.pick_context.intersection(contexts))
    if matching_contexts:
        delta = min(len(matching_contexts) * 5, 15)
        score += delta
        reasons.append(f"Fits current run context: {', '.join(matching_contexts)}.")

    deck_overlap = sorted(relic.tags.union(relic.roles).intersection(profile.tags.union(profile.roles)).difference({"damage", "block"}))
    if deck_overlap:
        score += min(len(deck_overlap) * 3, 9)
        reasons.append(f"Matches existing deck themes: {', '.join(deck_overlap)}.")

    owned_overlap = sorted(
        relic.tags.union(relic.roles).intersection(
            set().union(*(owned.tags.union(owned.roles) for owned in owned_relics)) if owned_relics else set()
        )
    )
    if owned_overlap:
        score += min(len(owned_overlap) * 2, 6)
        reasons.append(f"Matches current relic themes: {', '.join(owned_overlap)}.")

    if relic.quality_prior > 0:
        reasons.append("Reviewed relic prior says this is generally above-rate for V1.")
    if top_need is not None and top_need.name not in solved_needs:
        penalty = min(top_need.priority * 0.18, 8)
        score -= penalty
        risks.append(f"Does not directly solve the top diagnosed relic need: {top_need.name}.")
    if unknown_owned:
        risks.append(f"Unknown owned relic metadata may limit synergy review: {', '.join(unknown_owned)}.")

    return _ScoredRelic(
        choice=relic.id,
        name=relic.name,
        score=score,
        reasons=tuple(_dedupe(reasons)),
        risks=tuple(_dedupe(risks)),
    )


def _active_contexts(state: RelicChoiceState, profile: DeckProfile) -> frozenset[str]:
    contexts: set[str] = set()
    path_pressure = _normalized(state.run_context.path_pressure)
    if state.act == 1 and state.floor <= 12:
        contexts.add("early")
    if path_pressure in {"forced_elite", "elite_soon", "high"} or state.run_context.upcoming_elites:
        contexts.add("elite_prep")
    if state.hp.current / state.hp.max <= 0.50:
        contexts.add("low_hp")
    if state.act >= 2 or path_pressure in {"boss_soon", "late_act"}:
        contexts.add("long_act")
    if profile.damage_cards >= 5 or profile.damage_density >= 0.45:
        contexts.add("attack_dense")
    if profile.block_cards >= 5 or profile.block_density >= 0.40:
        contexts.add("skill_dense")
    return frozenset(contexts)


def _need_names_solved_by(roles: frozenset[str], tags: frozenset[str]) -> frozenset[str]:
    solved: set[str] = set()
    labels = roles.union(tags)
    if labels.intersection({"frontload", "damage"}):
        solved.add("frontload")
    if labels.intersection({"defense", "block", "dexterity"}):
        solved.add("defense")
    if labels.intersection({"scaling", "dexterity"}):
        solved.add("scaling")
    if labels.intersection({"consistency", "draw", "deck_quality"}):
        solved.add("consistency")
    if "energy" in labels:
        solved.add("energy_support")
    if labels.intersection({"sustain", "hp"}):
        solved.add("defense")
    return frozenset(solved)


def _recommendation_confidence(
    scored: list[_ScoredRelic],
    profile: DeckProfile,
    needs: tuple[RunNeed, ...],
    unknown_owned: tuple[str, ...],
) -> str:
    if profile.unknown_cards > 0 or unknown_owned:
        return "low"
    if len(scored) < 2:
        return "low"
    gap = scored[0].score - scored[1].score
    top_need = needs[0].name if needs else None
    top_solves_need = top_need is None or not any(f"top diagnosed relic need: {top_need}" in risk for risk in scored[0].risks)
    if gap >= 10 and top_solves_need:
        return "high"
    if gap >= 4:
        return "medium"
    return "low"


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _normalized(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip().lower().replace(" ", "_").replace("-", "_")
