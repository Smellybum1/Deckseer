from __future__ import annotations

from dataclasses import dataclass

from deckseer.models import CardData, RunState, TaggedData


@dataclass(frozen=True)
class RuleScore:
    name: str
    delta: float
    reason: str | None = None
    risk: str | None = None


@dataclass(frozen=True)
class DeckProfile:
    size: int
    known_cards: int
    unknown_cards: int
    unknown_card_ids: tuple[str, ...]
    damage_cards: int
    block_cards: int
    draw_cards: int
    energy_cards: int
    scaling_cards: int
    tags: frozenset[str]
    roles: frozenset[str]
    average_cost: float
    damage_density: float
    block_density: float
    draw_density: float
    scaling_density: float
    hp_ratio: float
    phase: str


@dataclass(frozen=True)
class RunNeed:
    name: str
    priority: float
    reason: str
    unresolved_risk: str


def build_deck_profile(run: RunState, cards_by_id: dict[str, CardData]) -> DeckProfile:
    size = 0
    damage_cards = 0
    block_cards = 0
    draw_cards = 0
    energy_cards = 0
    scaling_cards = 0
    tags: set[str] = set()
    roles: set[str] = set()
    total_cost = 0
    known_cards = 0
    unknown_cards = 0
    unknown_card_ids: set[str] = set()

    for deck_card in run.deck:
        card = cards_by_id.get(deck_card.id)
        count = deck_card.count
        size += count
        if card is None:
            unknown_cards += count
            unknown_card_ids.add(deck_card.id)
            continue

        known_cards += count
        tags.update(card.tags)
        roles.update(card.roles)
        total_cost += card.cost * count
        card_roles = _roles_for(card)
        if "frontload" in card_roles or card.type == "attack" or card.effects.damage > 0:
            damage_cards += count
        if "block" in card_roles or card.effects.block > 0:
            block_cards += count
        if "draw" in card_roles or "consistency" in card_roles or card.effects.draw > 0:
            draw_cards += count
        if "energy" in card_roles or card.effects.energy > 0:
            energy_cards += count
        if "scaling" in card_roles or card.type == "power":
            scaling_cards += count

    average_cost = total_cost / known_cards if known_cards else 0
    hp_ratio = run.hp.current / run.hp.max
    return DeckProfile(
        size=size,
        known_cards=known_cards,
        unknown_cards=unknown_cards,
        unknown_card_ids=tuple(sorted(unknown_card_ids)),
        damage_cards=damage_cards,
        block_cards=block_cards,
        draw_cards=draw_cards,
        energy_cards=energy_cards,
        scaling_cards=scaling_cards,
        tags=frozenset(tags),
        roles=frozenset(roles),
        average_cost=average_cost,
        damage_density=damage_cards / size if size else 0,
        block_density=block_cards / size if size else 0,
        draw_density=draw_cards / size if size else 0,
        scaling_density=scaling_cards / size if size else 0,
        hp_ratio=hp_ratio,
        phase=_phase_for(run),
    )


def build_deck_stats(run: RunState, cards_by_id: dict[str, CardData]) -> DeckProfile:
    return build_deck_profile(run, cards_by_id)


def diagnose_run_needs(run: RunState, profile: DeckProfile) -> tuple[RunNeed, ...]:
    needs = [
        _frontload_need(run, profile),
        _defense_need(run, profile),
        _scaling_need(run, profile),
        _consistency_need(run, profile),
        _energy_need(profile),
        _deck_quality_need(profile),
        _skip_pressure_need(profile),
    ]
    return tuple(sorted((need for need in needs if need.priority > 0), key=lambda need: (-need.priority, need.name)))


def score_card_rules(
    card: CardData,
    run: RunState,
    profile: DeckProfile,
    needs: tuple[RunNeed, ...],
    relics_by_id: dict[str, TaggedData],
) -> list[RuleScore]:
    rules: list[RuleScore] = [RuleScore("starting_point", 28, "Starts from a neutral card-pick baseline.")]
    rules.extend(_base_quality_rules(card))
    rules.extend(_quality_prior_rules(card))
    rules.extend(_need_fit_rules(card, run, profile, needs))
    rules.extend(_run_context_rules(card, run, profile))
    rules.extend(_synergy_rules(card, run, profile, relics_by_id))
    rules.extend(_copy_shape_rules(card, run, profile))
    rules.extend(_risk_rules(card, run, profile, needs))
    return rules


def score_skip_rules(
    profile: DeckProfile,
    needs: tuple[RunNeed, ...],
    best_offered_score: float,
) -> list[RuleScore]:
    rules = [RuleScore("skip_baseline", 36, "Skipping preserves deck quality and avoids adding low-impact cards.")]
    need_map = {need.name: need for need in needs}

    skip_need = need_map.get("skip_pressure")
    if skip_need is not None:
        rules.append(RuleScore("skip_pressure", skip_need.priority, skip_need.reason))

    if profile.size <= 12:
        rules.append(RuleScore("small_deck", -8, None, "Small decks often still need high-fit additions."))

    unresolved = [need for need in needs if need.name in {"frontload", "defense", "scaling"} and need.priority >= 18]
    for need in unresolved:
        rules.append(RuleScore(f"skip_unresolved_{need.name}", -need.priority * 0.45, None, need.unresolved_risk))

    if best_offered_score < 56:
        rules.append(RuleScore("weak_offer", 12, "Offered cards do not strongly solve the diagnosed run needs."))
    elif best_offered_score >= 72:
        rules.append(RuleScore("strong_offer", -12, None, "At least one offered card appears to solve a meaningful run need."))

    return rules


def _frontload_need(run: RunState, profile: DeckProfile) -> RunNeed:
    priority = 0.0
    region = _normalized(run.run_context.act_region)
    upcoming = _normalized_set(run.run_context.upcoming_elites)
    path_pressure = _normalized(run.run_context.path_pressure)
    if run.act == 1 and run.floor <= 10:
        priority += 16
    if profile.damage_cards < 5:
        priority += 18
    if profile.damage_density < 0.35:
        priority += 8
    if run.act == 1 and run.run_context.upcoming_elites:
        priority += 8
    if region == "overgrowth":
        priority += 12
    if region == "underdocks":
        priority -= 10
    if upcoming.intersection({"berdonis", "byrdonis", "bygone_effigy", "phrog_parasite", "frog_parasite"}):
        priority += 8
    if path_pressure in {"forced_elite", "elite_soon", "high"}:
        priority += 6
    if run.run_context.fire_before_elite is False and run.run_context.upcoming_elites:
        priority += 3
    if run.act >= 2 and profile.damage_cards >= 6:
        priority -= 10
    return RunNeed(
        "frontload",
        max(priority, 0),
        "Run needs frontload: current damage density may not handle near-term fights cleanly.",
        "Skipping may leave the deck short on near-term damage.",
    )


def _defense_need(run: RunState, profile: DeckProfile) -> RunNeed:
    priority = 0.0
    region = _normalized(run.run_context.act_region)
    upcoming = _normalized_set(run.run_context.upcoming_elites)
    path_pressure = _normalized(run.run_context.path_pressure)
    if profile.block_cards < 4:
        priority += 18
    if profile.block_density < 0.30:
        priority += 10
    if region == "underdocks":
        priority += 30
    if upcoming.intersection({"skulking_colony", "terror_eel", "phantasmal_gardener", "phantasmal_gardener"}):
        priority += 10
    if profile.hp_ratio <= 0.50:
        priority += 12
    elif profile.hp_ratio <= 0.65:
        priority += 6
    if run.run_context.recent_damage is not None and run.run_context.recent_damage >= 18:
        priority += 8
    if path_pressure in {"forced_elite", "elite_soon", "high"} and profile.hp_ratio <= 0.70:
        priority += 4
    return RunNeed(
        "defense",
        priority,
        "Run needs defense: block density and HP pressure point toward survival risk.",
        "Skipping may leave the deck short on defensive consistency.",
    )


def _scaling_need(run: RunState, profile: DeckProfile) -> RunNeed:
    priority = 0.0
    path_pressure = _normalized(run.run_context.path_pressure)
    if run.act >= 2 and profile.scaling_cards == 0:
        priority += 24
    if run.act >= 2 and profile.scaling_density < 0.08:
        priority += 8
    if run.act == 1 and run.floor >= 12 and profile.scaling_cards == 0:
        priority += 10
    if run.run_context.boss is not None and run.floor >= 10 and profile.scaling_cards == 0:
        priority += 4
    if run.act == 1 and run.floor <= 8:
        priority -= 8
    if run.act == 1 and path_pressure in {"forced_elite", "elite_soon", "high"}:
        priority -= 4
    return RunNeed(
        "scaling",
        max(priority, 0),
        "Run needs scaling: longer fights are approaching and the deck lacks a growth plan.",
        "Skipping may delay finding a long-fight scaling plan.",
    )


def _consistency_need(run: RunState, profile: DeckProfile) -> RunNeed:
    priority = 0.0
    path_pressure = _normalized(run.run_context.path_pressure)
    if profile.draw_cards == 0 and profile.size >= 10:
        priority += 12
    if profile.size >= 18:
        priority += 8
    elif profile.size >= 14:
        priority += 4
    if profile.average_cost >= 1.35:
        priority += 4
    if run.act >= 2:
        priority += 4
    if path_pressure in {"boss_soon", "late_act", "high"} and profile.size >= 14:
        priority += 4
    return RunNeed(
        "consistency",
        priority,
        "Run needs consistency: draw or deck control helps find the important cards on time.",
        "Skipping may preserve size, but it does not improve access to key cards.",
    )


def _energy_need(profile: DeckProfile) -> RunNeed:
    priority = 0.0
    if profile.average_cost >= 1.60:
        priority += 16
    elif profile.average_cost >= 1.35:
        priority += 10
    if profile.energy_cards == 0 and profile.average_cost >= 1.35:
        priority += 4
    return RunNeed(
        "energy_support",
        priority,
        "Run needs energy support: the current curve may strain three-energy turns.",
        "Skipping may leave the deck clunky on expensive turns.",
    )


def _deck_quality_need(profile: DeckProfile) -> RunNeed:
    priority = 0.0
    if profile.size >= 18:
        priority += 8
    if profile.size >= 24:
        priority += 8
    return RunNeed(
        "deck_quality",
        priority,
        "Run needs deck quality: additions should clearly improve draw density or solve a real gap.",
        "Taking a merely fine card may dilute the deck.",
    )


def _skip_pressure_need(profile: DeckProfile) -> RunNeed:
    priority = 0.0
    if profile.size >= 24:
        priority += 24
    elif profile.size >= 18:
        priority += 12
    if profile.damage_cards >= 6 and profile.block_cards >= 5 and profile.scaling_cards >= 1:
        priority += 8
    return RunNeed(
        "skip_pressure",
        priority,
        "Deck bloat pressure is real; Skip is live if the offer does not solve a specific problem.",
        "A pick needs to justify the extra draw variance.",
    )


def _base_quality_rules(card: CardData) -> list[RuleScore]:
    rarity_bonus = {
        "starter": 0,
        "common": 3,
        "uncommon": 4,
        "rare": 5,
    }.get(card.rarity, 2)

    cost_bonus = 0
    if card.cost == 0:
        cost_bonus = 3
    elif card.cost == 1:
        cost_bonus = 2
    elif card.cost >= 3:
        cost_bonus = -3

    type_bonus = 1 if card.type in {"attack", "skill", "power"} else 0

    return [
        RuleScore("rarity", rarity_bonus, f"{card.rarity.title()} card baseline quality."),
        RuleScore("cost", cost_bonus, f"{card.cost}-cost card affects the deck curve."),
        RuleScore("type", type_bonus, f"{card.type.title()} card has a small role baseline."),
    ]


def _quality_prior_rules(card: CardData) -> list[RuleScore]:
    if card.quality_prior == 0:
        return []

    delta = max(min(card.quality_prior * 1.5, 7.5), -7.5)
    if card.quality_prior > 0:
        return [RuleScore("quality_prior", delta, "Reviewed card prior says this is generally above-rate.")]
    return [RuleScore("quality_prior", delta, None, "Reviewed card prior flags this as below-rate unless it solves a specific problem.")]


def _need_fit_rules(
    card: CardData,
    run: RunState,
    profile: DeckProfile,
    needs: tuple[RunNeed, ...],
) -> list[RuleScore]:
    rules: list[RuleScore] = []
    roles = _roles_for(card)
    need_map = {need.name: need for need in needs}

    if "frontload" in roles:
        need = need_map.get("frontload")
        if need is not None:
            rules.append(RuleScore("need_frontload", need.priority * 0.72, need.reason))
        if card.effects.damage:
            rules.append(RuleScore("frontload_amount", min(card.effects.damage * 0.45, 7), "Provides immediate damage output."))

    if "block" in roles:
        need = need_map.get("defense")
        if need is not None:
            rules.append(RuleScore("need_defense", need.priority * 0.78, need.reason))
        if card.effects.block:
            rules.append(RuleScore("block_amount", min(card.effects.block * 0.45, 6), "Improves defensive consistency."))

    if "scaling" in roles:
        need = need_map.get("scaling")
        if need is not None:
            rules.append(RuleScore("need_scaling", need.priority * 0.82, need.reason))
        if run.act >= 2:
            rules.append(RuleScore("later_scaling", 5, "Scaling matters more as fights get longer."))
    if "niche" in roles and not _has_niche_support(card, profile):
        rules.append(RuleScore("unsupported_niche", -18, None, "Niche payoff card needs clearer deck support before it is worth taking."))

    if roles.intersection({"draw", "consistency", "deck_control"}):
        need = need_map.get("consistency")
        if need is not None:
            rules.append(RuleScore("need_consistency", need.priority * 0.65, need.reason))
        rules.append(RuleScore("draw", 5, "Card access improves consistency."))

    if "energy" in roles:
        need = need_map.get("energy_support")
        if need is not None:
            rules.append(RuleScore("need_energy", need.priority * 0.75, need.reason))
        rules.append(RuleScore("energy", 5, "Energy support can improve turn flexibility."))

    if profile.size >= 24:
        rules.append(RuleScore("deck_bloat_penalty", -14, None, "Large deck raises the bar for adding another card."))
    elif profile.size >= 18:
        rules.append(RuleScore("deck_quality_bar", -6, None, "Moderately large deck makes low-impact additions riskier."))

    return rules


def _run_context_rules(card: CardData, run: RunState, profile: DeckProfile) -> list[RuleScore]:
    rules: list[RuleScore] = []
    roles = _roles_for(card)
    region = _normalized(run.run_context.act_region)
    upcoming = _normalized_set(run.run_context.upcoming_elites)
    path_pressure = _normalized(run.run_context.path_pressure)

    if run.act == 1 and run.floor <= 10 and "frontload" in roles:
        rules.append(RuleScore("early_frontload", 5, "Early Act 1 rewards efficient frontload."))
    if region == "overgrowth" and "frontload" in roles:
        rules.append(RuleScore("overgrowth_frontload", 9, "Overgrowth elite prep rewards raw damage and efficient fights."))
    if region == "underdocks" and "block" in roles:
        rules.append(RuleScore("underdocks_block", 13, "Underdocks elite prep rewards block and careful timing."))
    if upcoming.intersection({"berdonis", "byrdonis", "bygone_effigy", "phrog_parasite", "frog_parasite"}) and "frontload" in roles:
        rules.append(RuleScore("damage_elite_prep", 7, "Upcoming elite context asks for a stronger damage plan."))
    if upcoming.intersection({"skulking_colony", "terror_eel", "phantasmal_gardener"}) and "block" in roles:
        rules.append(RuleScore("block_elite_prep", 7, "Upcoming elite context asks for stronger block coverage."))
    if path_pressure in {"forced_elite", "elite_soon", "high"} and "frontload" in roles:
        rules.append(RuleScore("path_pressure_frontload", 4, "Path pressure makes immediate fight strength more valuable."))
    if profile.hp_ratio <= 0.5 and "block" in roles:
        rules.append(RuleScore("low_hp_block", 5, "Low HP increases the value of immediate defense."))
    if run.act >= 2 and roles.intersection({"draw", "consistency", "deck_control"}):
        rules.append(RuleScore("later_consistency", 3, "Later acts reward consistency tools."))
    if run.run_context.boss and run.floor >= 10 and "scaling" in roles:
        rules.append(RuleScore("boss_prep_scaling", 5, "Known boss context raises the value of a clear scaling plan."))
    if profile.block_cards == 0 and "frontload" in roles and run.hp.current < run.hp.max:
        rules.append(RuleScore("no_block_caveat", -4, None, "More damage does not fix the current lack of block."))

    return rules


def _synergy_rules(
    card: CardData,
    run: RunState,
    profile: DeckProfile,
    relics_by_id: dict[str, TaggedData],
) -> list[RuleScore]:
    rules: list[RuleScore] = []
    meaningful_overlap = card.tags.intersection(profile.tags).difference({"damage", "block"})
    role_overlap = card.roles.intersection(profile.roles).difference({"frontload", "block"})
    overlap = meaningful_overlap.union(role_overlap)
    if overlap:
        labels = ", ".join(sorted(overlap))
        rules.append(RuleScore("deck_synergy", min(len(overlap) * 3, 9), f"Supports existing deck themes: {labels}."))

    relic_tags: set[str] = set()
    for relic_id in run.relics:
        relic = relics_by_id.get(relic_id)
        if relic is not None:
            relic_tags.update(relic.tags)
    relic_overlap = card.tags.union(card.roles).intersection(relic_tags)
    if relic_overlap:
        labels = ", ".join(sorted(relic_overlap))
        rules.append(RuleScore("relic_synergy", min(len(relic_overlap) * 4, 10), f"Matches current relic themes: {labels}."))

    if "attack_payoff" in card.tags and profile.damage_cards >= 8:
        delta = min(profile.damage_cards * 1.2, 16)
        rules.append(RuleScore("attack_payoff_density", delta, "Attack density gives this payoff enough triggers."))
    if (
        "attack_payoff" in card.tags
        and "shiv" in card.pick_context
        and ("shiv" in profile.tags or "shiv" in profile.roles)
    ):
        rules.append(RuleScore("shiv_payoff_support", 15, "Existing Shiv support makes attack-triggered payoff more credible."))

    return rules


def _copy_shape_rules(card: CardData, run: RunState, profile: DeckProfile) -> list[RuleScore]:
    owned_count = sum(deck_card.count for deck_card in run.deck if deck_card.id == card.id)
    if owned_count == 0:
        return []
    if profile.size < 18:
        return []
    if card.roles.intersection({"scaling", "deck_control", "energy"}):
        return []
    return [
        RuleScore(
            "duplicate_copy_pressure",
            -8,
            None,
            "The deck already owns this card; another copy needs a clearer reason in a larger deck.",
        )
    ]


def _risk_rules(
    card: CardData,
    run: RunState,
    profile: DeckProfile,
    needs: tuple[RunNeed, ...],
) -> list[RuleScore]:
    rules: list[RuleScore] = []
    roles = _roles_for(card)
    top_need = needs[0] if needs else None

    if top_need is not None and top_need.name not in _need_names_solved_by(roles):
        rules.append(
            RuleScore(
                "misses_top_need",
                -min(top_need.priority * 0.18, 8),
                None,
                f"Does not directly solve the top diagnosed need: {top_need.name}.",
            )
        )
        if card.quality_prior >= 3:
            rules.append(
                RuleScore(
                    "premium_misses_top_need",
                    0,
                    None,
                    f"Strong card prior, but this pick still misses the top diagnosed need: {top_need.name}.",
                )
            )
    if card.cost >= 2 and run.act == 1:
        rules.append(RuleScore("expensive_early", -3, None, "Two-cost cards can be awkward before energy support."))
    if card.type == "power" and run.act == 1 and run.floor <= 8:
        rules.append(RuleScore("slow_power", -5, None, "Early hallway fights may punish slower setup cards."))
    if profile.draw_cards == 0 and card.cost >= 2:
        rules.append(RuleScore("no_draw_expensive", -2, None, "Expensive cards are less reliable without card draw."))

    return rules


def _roles_for(card: CardData) -> frozenset[str]:
    roles = set(card.roles)
    if card.type == "attack" or "damage" in card.tags or card.effects.damage > 0:
        roles.add("frontload")
    if "block" in card.tags or card.effects.block > 0:
        roles.add("block")
    if "draw" in card.tags or card.effects.draw > 0:
        roles.update({"draw", "consistency"})
    if "energy" in card.tags or card.effects.energy > 0:
        roles.add("energy")
    if card.type == "power" or card.tags.intersection({"scaling", "strength", "dexterity"}):
        roles.add("scaling")
    return frozenset(roles)


def _need_names_solved_by(roles: frozenset[str]) -> frozenset[str]:
    solved: set[str] = set()
    if "frontload" in roles:
        solved.add("frontload")
    if "block" in roles:
        solved.add("defense")
    if "scaling" in roles:
        solved.add("scaling")
    if roles.intersection({"draw", "consistency", "deck_control"}):
        solved.add("consistency")
    if "energy" in roles:
        solved.add("energy_support")
    return frozenset(solved)


def _has_niche_support(card: CardData, profile: DeckProfile) -> bool:
    if "block_payoff" in card.roles or "block_scaling" in card.pick_context:
        return profile.block_cards >= 7 or "block_payoff" in profile.roles
    return False


def _phase_for(run: RunState) -> str:
    if run.act == 1 and run.floor <= 10:
        return "early_act_1"
    if run.act == 1:
        return "late_act_1"
    if run.act == 2:
        return "act_2"
    return "late_run"


def _normalized(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip().lower().replace(" ", "_").replace("-", "_")


def _normalized_set(values: tuple[str, ...]) -> frozenset[str]:
    return frozenset(_normalized(value) for value in values)
