# ADR 1: Preserve Human-Confirmed Exporter Boundary

Status: accepted

Date: 2026-05-24

## Context

Deckseer is moving from manual JSON toward a Slay the Spire 2 companion exporter. The exporter is valuable because it can reduce manual transcription, but it also creates the main project risk: accidentally turning a deterministic advisor into live capture, automation, or unreviewed game-state ingestion.

The current exporter spike writes only `screen_type: "exporter_status"`. Deckseer can already inspect fixture-style card and relic reward exports, but live card reward export has not been proven.

## Decision

Exporter work stays read-only/export-only and human-confirmation-first.

Specifically:

- `exporter_status` is health metadata only, not recommendation input.
- Live `card_reward` export must wait for visible-screen proof and card ID mapping proof.
- `recommend-export` must require explicit `--confirmed` when exporter metadata requires user confirmation.
- Exporter packets must not add watch mode, OCR, screenshot reading, input automation, memory/process access, packet inspection, save/profile modification, or scoring changes.
- A new live observation route that changes this risk profile requires an explicit boundary decision before implementation or install testing.

## Consequences

This slows the exporter path, but keeps Deckseer trustworthy and easy to audit. At the time this ADR was accepted, the project could continue improving manual advisor workflows, fixtures, and docs while exporter visibility remained blocked.

Follow-up, 2026-05-25: the original visibility boundary question was resolved by later accepted ADRs and installed proofs. ADR 2 accepted count-only public screen observation, ADR 3 accepted a status-only ID-revealing diagnostic for mapping review, ADR 4 accepted human-confirmed live `card_reward` export, ADR 7 accepted human-confirmed live `relic_reward` export, and ADR 8 accepted the treasure relic readiness contract. Installed `v0.4.7` is live-proven for confirmed mixed reward `card_reward` export with post-selection downgrade. The preserving rule from this ADR still applies: exporter state remains read-only/export-only and human-confirmation-first.

## Links

- `docs/CONTEXT.md`
- `docs/EXPORTER_CARD_REWARD_VISIBILITY_DESIGN.md`
- `docs/EXPORTER_CARD_REWARD_COMPILE_PROBE.md`
- `docs/EXECUTION_LOOP.md`
