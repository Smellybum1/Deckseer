# ADR 8: Treasure Relic Live Export Readiness Contract

Status: accepted

Date: 2026-05-25

## Context

ADR 7 accepted human-confirmed live `screen_type: "relic_reward"` export for normal public reward-screen relic rewards. Installed exporter `v0.4.0` implemented that route and stayed safe when a treasure chest relic did not use the normal reward-screen path.

Installed `v0.4.1` through `v0.4.4` then proved a separate public treasure route:

- `NTreasureRoomRelicHolder.Initialize(RelicModel, IRunState)` can observe the visible treasure relic.
- public `RelicModel.Id` can reveal the visible treasure relic ID.
- reviewed `LETTER_OPENER` maps to Deckseer ID `letter_opener`.
- treasure diagnostics clear after pickup.

The route still intentionally refuses live export with `treasure_relic_route_status_only`. The latest live proof also reported missing required run-state fields and an unmapped deck card, so mapped relic identity alone is not enough to promote treasure relics into recommendation-ready state.

## Decision

Treasure relic live export is accepted as a repo-local implementation packet only. It should extend the ADR 7 human-confirmed relic reward boundary with a treasure-specific readiness contract:

- `NTreasureRoomRelicHolder.Initialize(RelicModel, IRunState)` may be treated as the visible treasure relic source only after explicit acceptance of this ADR or a successor.
- The treasure route may satisfy visible reward alignment with the `IRunState` passed by that public method, but only when required run-state fields, deck identity, owned relic identity, potion identity, and reward relic identity all pass the same mapping gates as normal relic rewards.
- Missing run state, unmapped deck card, unmapped owned relic, unmapped potion, unmapped reward relic, duplicate reward relic, stale treasure state, or payload validation failure must continue to write `screen_type: "exporter_status"`.
- The exported payload must use the existing `screen_type: "relic_reward"` schema, set `export_metadata.requires_user_confirmation` to `true`, and remain rejected by `recommend-export` until the user confirms it.
- Treasure pickup, skip, room exit, or collection close must downgrade or remain at `screen_type: "exporter_status"` with cleared reward identity diagnostics.

Implementation should be repo-local and fixture-first before any install check.

## Consequences

This keeps the current installed `v0.4.4` behavior safe: treasure relics remain status-only until a later explicit install check is approved.

If accepted later, the route can reuse Relic Choice V1 and the existing confirmed exporter adapter without adding watch mode, OCR, input automation, save/profile modification, memory/process tricks, packet inspection, or scoring changes.

The hard part is proving that the chest-specific `IRunState` is fresh enough to replace the normal `RewardsSet` visible-player alignment gate. The promotion packet must include fixture coverage and live proof for both visible export and post-pickup downgrade.

## Outcome

Installed `v0.4.5` verified the refusal side of this contract: a visible treasure `LETTER_OPENER` stayed `exporter_status` when `ACCURACY` and `HEART_OF_IRON` mappings were incomplete, then cleared after pickup.

Installed `v0.4.6` verified the success side on a fully mapped treasure run: visible treasure wrote human-confirmed `screen_type: "relic_reward"`, unconfirmed `recommend-export` rejected it, confirmed recommendation scored `letter_opener`, and pickup downgraded back to `exporter_status` with cleared identity diagnostics.

## Links

- `docs/EXPORTER_TREASURE_RELIC_LIVE_EXPORT_READINESS.md`
- `docs/EXPORTER_TREASURE_RELIC_DATA_REVIEW.md`
- `docs/EXPORTER_RELIC_REWARD_LIVE_EXPORT_DESIGN.md`
- `docs/adr/0007-human-confirmed-live-relic-reward-export.md`
