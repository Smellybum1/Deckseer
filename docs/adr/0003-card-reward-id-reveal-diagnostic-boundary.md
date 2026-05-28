# ADR 3: Decide Card Reward ID Reveal Diagnostic Boundary

Status: Accepted

Date: 2026-05-24

## Context

The installed `v0.2.8` exporter diagnostic remains status-only and does not export raw STS2 IDs, Deckseer IDs, card names, selected-card identity, or recommendation-ready run state. It proved that a visible reward screen can produce identity-shaped counts and known/unknown mapping counts through approved public screen observation routes.

The mapping review and reviewed `infinite_blades` follow-up resolved the observed data-coverage gap, and a repo-local drift guard now checks that the status-diagnostic mapping snapshot covers Deckseer's current card catalog.

The remaining blocker before live `card_reward` export is exact mapping proof. Count-only diagnostics cannot prove which public STS2 model ID corresponds to each visible reward choice. Revealing those IDs would change the exporter boundary and needs an explicit decision.

## Decision

Allow a temporary `exporter_status` diagnostic that reveals the minimum visible reward card identity evidence needed for human mapping review.

The diagnostic remains status-only and must:

- write `screen_type: "exporter_status"`
- expose identity review items only for currently visible reward choices
- keep `recommend-export` rejection for status files
- require user confirmation before implementation and a separate explicit approval before real STS2 mod install-check
- avoid selected-card identity, deck, HP, gold, relics, potions, save/profile data, OCR, watch mode, input automation, private access, and recommendation-ready run state

## Consequences

This would unblock exact mapping review and reduce risk before `screen_type: "card_reward"` export.

It also reveals live card identity strings for visible choices, which is a deliberate expansion beyond count-only diagnostics. This ADR accepts repo-local implementation and build verification only. Installing into the real STS2 mods folder remains a separate explicit approval gate.

## Alternatives Considered

- Stay count-only: safest, but cannot prove exact STS2 model IDs.
- Add card data from visible labels only: can explain some unknown counts, but does not prove exporter mapping.
- Jump directly to `card_reward` export: rejected because it combines identity reveal, recommendation input, and run-state export into one larger risk step.

## Links

- `docs/CONTEXT.md`
- `docs/EXPORTER_CARD_REWARD_ID_REVEAL_CONTRACT.md`
- `docs/EXPORTER_CARD_REWARD_MAPPING_REVIEW.md`
- `docs/EXPORTER_CARD_REWARD_ID_DIAGNOSTIC_DESIGN.md`
- `docs/adr/0001-preserve-human-confirmed-exporter-boundary.md`
- `docs/adr/0002-exporter-screen-observation-boundary.md`
