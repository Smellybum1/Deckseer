# ADR 6: Relic And Potion ID Review Diagnostic Boundary

Status: accepted

Date: 2026-05-24

## Context

Installed `v0.2.15` proves the refusal-first live export candidate path works while still writing only `screen_type: "exporter_status"`.

On the verified visible card reward screen, reward card IDs and deck card IDs were fully mapped, but the candidate correctly refused `card_reward` with `unmapped_relic` because relic IDs are not yet mapped or exported. Potion count was 0 in the tested run, so non-empty potion ID mapping is also unproven.

Count-only relic and potion diagnostics cannot identify which relics or potions need mapping review. Revealing those IDs would expand the status diagnostic boundary beyond ADR 5, which only allowed deck card identity review.

## Decision

Allow a future, separately approved `exporter_status` diagnostic that reveals the minimum relic and potion identity evidence needed for human mapping review.

The diagnostic must remain status-only and must:

- write `screen_type: "exporter_status"`
- expose relic and potion identity review items only while a visible card reward screen is active
- expose public relic/potion identity strings, normalized candidates, mapping status, Deckseer ID only for exact known mappings, and counts
- keep `recommend-export` rejection for status files
- require a separate implementation packet and a separate explicit approval before real STS2 mod install-check
- clear relic and potion identity review items when the reward screen closes, is skipped, or is completed
- avoid HP values, gold values, act/floor/ascension values, character ID, selected-card identity, selected/skipped outcome, save/profile data, OCR, watch mode, input automation, private access, and recommendation-ready run state

## Consequences

This would unblock exact review of the `v0.2.15` `unmapped_relic` refusal without jumping directly to live `card_reward` export.

It deliberately reveals more live identity information than the current count-only relic/potion diagnostics. The output remains user-visible, inspectable, and outside recommendation input.

The diagnostic can identify missing mapping or sparse data coverage, but it does not approve adding relic or potion data, changing scoring, changing relic choice behavior, or using the revealed IDs as recommendation input.

## Alternatives Considered

- Stay count-only: safest, but cannot identify which relic or potion IDs are blocking live export readiness.
- Ask for a manual relic/potion list: avoids expanding exporter diagnostics, but leaves the exporter mapping route unproven and vulnerable to transcription drift.
- Jump directly to `screen_type: "card_reward"`: rejected because it combines relic/potion ID reveal, live run-state values, and recommendation-ready export in one larger risk step.
- Use save/profile or run-history files to recover relic/potion IDs: rejected for this exporter packet because the exporter boundary should remain live public API/read-only export, not save/profile import.

## Links

- `docs/CONTEXT.md`
- `docs/EXPORTER_CARD_REWARD_LIVE_EXPORT_DESIGN.md`
- `docs/EXPORTER_CARD_REWARD_RELIC_POTION_ID_REVIEW_DESIGN.md`
- `docs/adr/0001-preserve-human-confirmed-exporter-boundary.md`
- `docs/adr/0004-human-confirmed-live-card-reward-export.md`
- `docs/adr/0005-deck-id-review-diagnostic-boundary.md`
