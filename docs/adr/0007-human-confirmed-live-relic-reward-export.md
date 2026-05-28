# ADR 7: Human-Confirmed Live Relic Reward Export

Status: accepted

Date: 2026-05-25

## Context

Manual Relic Choice V1 is implemented, fixture-backed `screen_type: "relic_reward"` exporter imports are supported, and `recommend-export --confirmed` can score confirmed relic reward files through the existing relic choice scorer.

Installed exporter `v0.3.10` proves the card reward live-export boundary can stay read-only/export-only, confirmation-first, and stale-state-safe after the visible card reward selection screen closes. The next low-friction advisor surface is live relic reward export, but it expands live recommendation-ready output beyond card rewards and needs its own boundary before runtime implementation.

## Decision

Allow a future implementation packet to add a narrow live `screen_type: "relic_reward"` exporter mode only when all of these constraints hold:

- The active relic reward is observed through public, normal mod-accessible reward-screen state.
- The visible reward relic choices are normalized through reviewed Deckseer relic mappings.
- The export includes the existing Deckseer relic reward schema fields needed by `recommend-export`.
- `export_metadata.requires_user_confirmation` is always `true`.
- `recommend-export` continues to require the user to run `inspect-export`, compare the visible game state, and rerun with `--confirmed`.
- The exporter remains read-only/export-only and writes a local JSON file only.
- The exporter clears or downgrades away from `screen_type: "relic_reward"` when the reward screen closes, is skipped, or the relic reward is collected.
- Any missing run-state field, unmapped reward relic, unsupported duplicate reward, stale screen, or unsafe state falls back to `screen_type: "exporter_status"`.

The first implementation should be repo-local and fixture-tested before any install check. Live proof should verify startup fallback, visible relic reward export, unconfirmed rejection, confirmed recommendation after human review, and post-selection/close downgrade.

## Implementation Notes

Repo-local exporter `v0.4.0` implements the first live relic reward export path with fixture-tested confirmation gating and closed-state downgrade.

Installed `v0.4.0` startup fallback passed. A treasure chest relic live proof stayed safely as `exporter_status` because that screen did not trigger the normal reward-screen route; post-collect recommendation also rejected the status file.

Installed `v0.4.1` proves the treasure relic route as status-only: the visible chest relic screen reported `treasure_relic_model_seen`, refused live export with `treasure_relic_route_status_only`, and cleared after `treasure_relic_picked`. The identity diagnostic hit `CanonicalModelException`; installed `v0.4.2` fixes that exception by reading `RelicModel.CanonicalInstance` before serialization, but live proof still reported `public_model_id: null`. Installed `v0.4.3` reads public `RelicModel.Id` directly before serialization fallback, reveals `LETTER_OPENER` as an unmapped review-only treasure relic ID, rejects recommendation as `exporter_status`, and clears after pickup, still without live export promotion. Installed `v0.4.4` maps reviewed `letter_opener` in status diagnostics and live-verifies mapped treasure clear-state, still without live export promotion.

## Consequences

This extends the low-friction exporter path to the first broader advice module while reusing the existing relic choice scorer and confirmed exporter adapter.

The exported data surface remains smaller than card reward export because the advisor only needs visible relic choices plus the same run-state fields already proven for card rewards. The risk is different: relic reward visibility and collection routes may not match card reward routes, so stale-file behavior must be proven separately.

Live relic reward export does not approve watch mode, OCR, input automation, save/profile access, scoring changes, relic data expansion, boss relic special handling, or recommendation baseline changes.

## Alternatives Considered

- Keep relic reward advice manual-only: safest, but leaves the already-supported exporter relic fixture path unused for live play.
- Add watch mode first: rejected because command-driven human confirmation remains the boundary.
- Export relic IDs without run state: rejected because it would be incompatible with the current relic choice input shape and could produce misleading advice.
- Use save/profile files for relic reward state: rejected for this packet because the exporter boundary should remain live public API/read-only export, not save/profile import.

## Links

- `docs/EXPORTER_RELIC_REWARD_LIVE_EXPORT_DESIGN.md`
- `docs/RELIC_CHOICE_DESIGN.md`
- `docs/EXPORTER_MOD_DESIGN.md`
- `docs/adr/0001-preserve-human-confirmed-exporter-boundary.md`
- `docs/adr/0004-human-confirmed-live-card-reward-export.md`
