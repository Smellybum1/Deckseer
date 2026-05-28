# ADR 9: Status-Only Event/Special Route Classifier

Status: accepted

Date: 2026-05-25

## Context

Installed exporter `v0.4.7` is live-proven for confirmed mixed reward `card_reward` export and post-selection downgrade, and installed `v0.4.6` is live-proven for confirmed treasure `relic_reward` export and post-pickup downgrade. Later live coaching evidence showed several event/special choice surfaces that did not become recommendation-ready exporter states: Pael, Tea Master, Doll relic selection, Amalgamator, shop-like choices, and some post-event card choices.

Those routes are riskier than ordinary card/relic reward screens because they may carry event state, shop economy, selection semantics, or post-event transitions that are not covered by the accepted card and relic reward export boundaries.

Subsequent installed `v0.4.7` status-only diagnostics captured Ancient, Choose-a-Pack, Ranwid, Doll Room, Vakuu, Zen Weaver, Self-Help Book, Loot card-choice, Brain Leech, Sapphire Seed, Potion Courier, Crystal Sphere, and relic-looking event rows without promoting any of them to recommendation input. A repaired deck-enchant diagnostic is installed and startup-verified as `screen_observation_probe: "registered"`, and active deck-enchant grid proof now reports `deck_enchant_selection_screen_shown` as count-only status evidence. Relic-looking event rows inspected after that proof still used `public_event_layout_options`; active proof for `choose_relic_selection_screen_shown` remains pending.

## Decision

Allow separately approved implementation packets to add status-only event/special route classifiers.

The classifier must:

- write only `screen_type: "exporter_status"`
- report route-shape diagnostics only, such as active/inactive state, coarse route kind, public observation source, visible option count when available, clear-state status, and blocker codes
- keep `recommend-export` rejection for status files
- avoid reward option IDs, reward option names, selected-option identity, selected/skipped outcome, run-state scalar values, save/profile data, OCR, watch mode, input automation, private access, and recommendation-ready card/relic state
- require a separate implementation packet and a separate explicit approval before real STS2 mod install-check
- clear or downgrade the route diagnostics when the event/special surface closes or changes

Fixture packets must use captured `exporter_status` payloads only. Do not fabricate event/special route evidence.

## Consequences

This creates a safe proof path for event/special screens without promoting them to recommendation input. It should make future live evidence easier to classify and hand off while preserving the human-confirmation exporter boundary.

It deliberately does not approve live event advice, shop advice, post-event card export, option identity reveal, scorer changes, priors, empirical rows, recommendation baselines, or installed mod changes.

Future promotion from route diagnostics to any recommendation-ready export requires a separate ADR or accepted design note for the specific route family.

## Links

- `docs/EXPORTER_EVENT_SPECIAL_ROUTE_CLASSIFIER_DESIGN.md`
- `docs/EXPORTER_CARD_REWARD_LIVE_MAPPING_GAP_REVIEW.md`
- `docs/CONTEXT.md`
- `docs/adr/0001-preserve-human-confirmed-exporter-boundary.md`
- `docs/adr/0002-exporter-screen-observation-boundary.md`
- `docs/adr/0004-human-confirmed-live-card-reward-export.md`
- `docs/adr/0007-human-confirmed-live-relic-reward-export.md`
