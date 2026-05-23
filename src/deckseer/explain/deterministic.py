from __future__ import annotations

from deckseer.scoring.rules import RuleScore


def summarize_reasons(rules: list[RuleScore], *, limit: int = 3) -> tuple[str, ...]:
    low_signal_rules = {"starting_point", "rarity", "type", "cost", "quality_prior"}
    reasons: list[str] = []
    useful_rules = (
        rule
        for rule in rules
        if rule.reason and rule.delta > 0 and rule.name not in low_signal_rules
    )
    for rule in sorted(useful_rules, key=lambda item: item.delta, reverse=True):
        if rule.reason not in reasons:
            reasons.append(rule.reason)
        if len(reasons) >= limit:
            break
    if not reasons:
        reasons.append("No strong positive rule matched; this option is mostly baseline value.")
    return tuple(reasons)


def summarize_risks(rules: list[RuleScore], *, limit: int = 3) -> tuple[str, ...]:
    risks: list[str] = []
    for rule in sorted((rule for rule in rules if rule.risk), key=lambda item: item.delta):
        if rule.risk not in risks:
            risks.append(rule.risk)
        if len(risks) >= limit:
            break
    if not risks:
        risks.append("No major caveat detected by the v0 rule set.")
    return tuple(risks)
