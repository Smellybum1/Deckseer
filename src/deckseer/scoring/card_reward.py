from __future__ import annotations

from dataclasses import dataclass

from deckseer.data_loader import DeckseerData
from deckseer.explain.deterministic import summarize_reasons, summarize_risks
from deckseer.models import ChoiceRecommendation, RecommendationResult, RunState
from deckseer.scoring.rules import DeckProfile, RuleScore, build_deck_profile, diagnose_run_needs, score_card_rules, score_skip_rules


@dataclass(frozen=True)
class _ScoredChoice:
    choice: str
    name: str
    score: float
    rules: list[RuleScore]


def recommend_card_reward(run: RunState, data: DeckseerData) -> RecommendationResult:
    offered_cards = data.cards_for_choices(run.card_reward)
    profile = build_deck_profile(run, data.cards_by_id)
    needs = diagnose_run_needs(run, profile)

    scored_cards: list[_ScoredChoice] = []
    for choice in run.card_reward:
        card = offered_cards[choice]
        rules = score_card_rules(card, run, profile, needs, data.relics_by_id)
        scored_cards.append(
            _ScoredChoice(
                choice=card.id,
                name=card.name,
                score=sum(rule.delta for rule in rules),
                rules=rules,
            )
        )

    best_offered_score = max(choice.score for choice in scored_cards)
    skip_rules = score_skip_rules(profile, needs, best_offered_score)
    scored_choices = [
        *scored_cards,
        _ScoredChoice(
            choice="skip",
            name="Skip",
            score=sum(rule.delta for rule in skip_rules),
            rules=skip_rules,
        ),
    ]
    scored_choices.sort(key=lambda item: (-item.score, item.choice))

    confidence = _recommendation_confidence(scored_choices, profile)
    ranked = tuple(
        ChoiceRecommendation(
            choice=item.choice,
            name=item.name,
            rank=index + 1,
            score=item.score,
            confidence=confidence,
            reasoning=summarize_reasons(item.rules),
            risks=summarize_risks(item.rules),
        )
        for index, item in enumerate(scored_choices)
    )
    return RecommendationResult(recommendation_type="card_reward", ranked_choices=ranked)


def _recommendation_confidence(scored_choices: list[_ScoredChoice], profile: DeckProfile) -> str:
    if profile.unknown_cards > 0:
        return "low"
    if len(scored_choices) < 2:
        return "low"
    gap = scored_choices[0].score - scored_choices[1].score
    if gap >= 15:
        return "high"
    if gap >= 5:
        return "medium"
    return "low"
