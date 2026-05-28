# ADR 5: Deck ID Review Diagnostic Boundary

Status: Accepted

Date: 2026-05-24

## Context

Installed `v0.2.11` proved that the public runtime presence path can see required run-state field surfaces during a visible card reward screen. The exporter stayed status-only, cleared after the reward screen was skipped, and did not export live run-state values or recommendation-ready state.

The visible reward-screen runtime probe also reported `card_reward_run_state_deck_card_mapping_known_count: 3` and `card_reward_run_state_deck_card_mapping_unknown_count: 11`. That count-only result blocks live `screen_type: "card_reward"` export because Deckseer cannot safely emit a complete advisor input while most deck card IDs are unmapped.

Count-only deck mapping diagnostics cannot identify which deck cards need review. Revealing deck card IDs would expand the status diagnostic boundary beyond ADR 3, which only allowed visible reward card identity strings.

## Decision

Allow a future, separately approved `exporter_status` diagnostic that reveals the minimum deck card identity evidence needed for human mapping review.

The diagnostic must remain status-only and must:

- write `screen_type: "exporter_status"`
- expose deck identity review items only while a visible card reward screen is active
- expose public card identity strings for deck cards, normalized candidates, mapping status, Deckseer ID only for exact known mappings, upgraded state, and grouped counts
- keep `recommend-export` rejection for status files
- require user confirmation before implementation and a separate explicit approval before real STS2 mod install-check
- clear deck identity review items when the reward screen closes, is skipped, or is completed
- avoid HP values, gold values, act/floor/ascension values, character ID, relic IDs, potion IDs, selected-card identity, selected/skipped outcome, save/profile data, OCR, watch mode, input automation, private access, and recommendation-ready run state

## Consequences

This would unblock exact review of the 3-known/11-unknown deck mapping gap without jumping directly to live `card_reward` export.

It deliberately reveals more live identity information than `v0.2.11` count-only runtime diagnostics. The output remains user-visible, inspectable, and outside recommendation input.

The diagnostic can identify missing mapping or data coverage, but it does not approve adding card data, changing scoring, or using the revealed deck IDs as recommendation input.

## Alternatives Considered

- Stay count-only: safest, but cannot identify which deck IDs are unknown.
- Ask for a manual deck list: avoids expanding exporter diagnostics, but still leaves the exporter mapping route unproven and is vulnerable to manual transcription drift.
- Jump directly to `screen_type: "card_reward"`: rejected because it combines deck ID reveal, live run-state values, and recommendation-ready export in one larger risk step.
- Use save/profile or run-history files to recover deck IDs: rejected for this exporter packet because the exporter boundary should remain live public API/read-only export, not save/profile import.

## Links

- `docs/CONTEXT.md`
- `docs/EXPORTER_CARD_REWARD_DECK_MAPPING_GAP_REVIEW.md`
- `docs/EXPORTER_CARD_REWARD_DECK_ID_REVEAL_DESIGN.md`
- `docs/EXPORTER_CARD_REWARD_RUN_STATE_SYMBOL_REVIEW.md`
- `docs/EXPORTER_CARD_REWARD_LIVE_EXPORT_DESIGN.md`
- `docs/adr/0001-preserve-human-confirmed-exporter-boundary.md`
- `docs/adr/0003-card-reward-id-reveal-diagnostic-boundary.md`
- `docs/adr/0004-human-confirmed-live-card-reward-export.md`
