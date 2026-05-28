# Deckseer ADRs

Architectural decision records capture non-obvious project decisions that future sessions should not have to rediscover.

Write an ADR only when the decision is:

- hard or annoying to reverse
- surprising without context
- the result of a real tradeoff
- important to Deckseer's safety, data, CLI, exporter, or recommendation boundaries

Keep ADRs short. Use this shape:

```markdown
# ADR N: Title

Status: accepted | proposed | superseded

Date: YYYY-MM-DD

## Context

What made the decision necessary?

## Decision

What did we choose?

## Consequences

What gets easier, harder, blocked, or deferred?

## Links

- Related docs, code, or verification.
```

Use `docs/CONTEXT.md` for shared vocabulary. Use ADRs for decisions.

## Records

- ADR 1: `0001-preserve-human-confirmed-exporter-boundary.md`
- ADR 2: `0002-exporter-screen-observation-boundary.md`
- ADR 3: `0003-card-reward-id-reveal-diagnostic-boundary.md`
- ADR 4: `0004-human-confirmed-live-card-reward-export.md`
- ADR 5: `0005-deck-id-review-diagnostic-boundary.md`
- ADR 6: `0006-relic-potion-id-review-diagnostic-boundary.md`
- ADR 7: `0007-human-confirmed-live-relic-reward-export.md`
- ADR 8: `0008-treasure-relic-live-export-readiness-contract.md`
- ADR 9: `0009-status-only-event-special-route-classifier.md`
