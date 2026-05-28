# Deckseer Exporter Treasure Relic Live Export Readiness

Status: `installed_v0.4.6_live_treasure_proof_passed`

Prepared on 2026-05-25 after installed `v0.4.4` verified reviewed `LETTER_OPENER` mapping and clear-state behavior while still refusing treasure relic live export. Updated after ADR 8 was accepted, installed `v0.4.5` verified safe treasure-route refusal plus post-pickup clear-state, and installed `v0.4.6` verified successful treasure `relic_reward` export on a fully mapped run.

## Scope

This note records readiness, repo-local implementation evidence, installed `v0.4.5` safe-refusal proof, and installed `v0.4.6` successful live proof for treasure-room relic export.

It does not approve:

- changing card or potion data for observed mapping gaps
- extending successful live treasure `relic_reward` export beyond the observed fully mapped v0.4.6 proof
- changing `recommend-export` confirmation behavior
- changing relic scoring, priors, roles, empirical data, accuracy expectations, or baselines
- watch mode, OCR, screenshot capture, input automation, memory/process tricks, packet inspection, save/profile modification, or live capture

## Proven

Installed `v0.4.4` proves these pieces are available through public, read-only exporter surfaces:

- the chest-specific route can observe a visible treasure relic through `NTreasureRoomRelicHolder.Initialize(RelicModel, IRunState)`
- public `RelicModel.Id` can reveal the visible treasure relic ID
- reviewed `LETTER_OPENER` maps to Deckseer ID `letter_opener`
- visible treasure relic diagnostics stay under `screen_type: "exporter_status"`
- `recommend-export --confirmed` rejects visible and cleared treasure status files
- picking the relic clears visible relic identity diagnostics through `treasure_relic_picked`

## Repo-Local v0.4.5 Implementation

ADR 8 is accepted. Repo-local exporter `v0.4.5` implements the treasure route contract:

- `treasure_relic_model_seen` plus `treasure_relic_holder_initialized` can become an eligible relic reward candidate.
- The public `IRunState` passed to `NTreasureRoomRelicHolder.Initialize(...)` satisfies the visible alignment gate only for the treasure route.
- Missing run-state fields, unmapped deck cards, unmapped owned relics, unmapped potions, unmapped reward relics, duplicate reward relics, stale treasure state, or payload validation errors still refuse export.
- The payload remains `screen_type: "relic_reward"` with `requires_user_confirmation: true`.
- The picked/closed treasure fixture remains `screen_type: "exporter_status"` and rejects confirmed recommendation.

Fixture coverage:

- `tests/fixtures/exporter_relic_reward_live_v045_treasure_state.json`
- `tests/fixtures/exporter_status_v045_treasure_relic_picked_state.json`

## Installed v0.4.5 Live Proof

Installed startup fallback passed:

- `screen_type: "exporter_status"`
- `exporter_version: "0.4.5"`
- `requires_user_confirmation: false`
- `inspect-export` accepted the file

Visible treasure proof was safely refused:

- `visible_reward_probe_status: "treasure_relic_model_seen"`
- `visible_reward_probe_last_event: "treasure_relic_holder_initialized"`
- `visible_relic_reward_option_count: 1`
- visible relic identity reported `public_model_id: "LETTER_OPENER"`
- visible relic mapping was known as `letter_opener`
- `relic_reward_live_export_candidate: "refused"`
- refusal reasons were `unmapped_deck_card` and `unmapped_potion`
- the unknown deck card was `ACCURACY` -> `accuracy`
- the unknown potions were two `HEART_OF_IRON` -> `heart_of_iron`
- confirmed `recommend-export` rejected the file as `exporter_status`

Post-pickup clear-state passed:

- `visible_reward_probe_status: "reward_screen_completed"`
- `visible_reward_probe_last_event: "treasure_relic_picked"`
- visible reward counts cleared to zero
- deck, relic, potion, card, and relic reward identity review arrays cleared
- `relic_reward_live_export_candidate: "refused"`
- refusal reasons were `stale_reward_screen` and `missing_required_run_state_field`
- confirmed `recommend-export` rejected the file as `exporter_status`

The observed `ACCURACY` and `HEART_OF_IRON` IDs are review evidence only. They do not approve card data changes, potion data changes, scoring changes, or another installed packet.

## Installed v0.4.6 Live Proof

Installed startup fallback passed:

- `screen_type: "exporter_status"`
- `exporter_version: "0.4.6"`
- `requires_user_confirmation: false`
- `inspect-export` accepted the file

Visible treasure proof passed:

- `screen_type: "relic_reward"`
- `exporter_version: "0.4.6"`
- `requires_user_confirmation: true`
- character `silent`, act 1, floor 10
- HP `61/70`
- gold `271`
- deck included mapped `accuracy`
- potions included `colorless_potion`, `heart_of_iron`, and `heart_of_iron`
- visible reward relic was `letter_opener`
- unconfirmed `recommend-export` rejected the file and required user confirmation
- confirmed `recommend-export` scored `letter_opener` through Relic Choice V1

Post-pickup clear-state passed:

- `screen_type: "exporter_status"`
- `exporter_version: "0.4.6"`
- `requires_user_confirmation: false`
- `visible_reward_probe_status: "reward_screen_completed"`
- `visible_reward_probe_last_event: "treasure_relic_picked"`
- visible reward counts cleared to zero
- card, deck, relic, potion, and relic reward identity review arrays cleared
- `relic_reward_live_export_candidate: "refused"`
- refusal reasons were `stale_reward_screen` and `missing_required_run_state_field`
- confirmed `recommend-export` rejected the file as `exporter_status`

Fixture coverage:

- `tests/fixtures/exporter_relic_reward_live_v046_treasure_mapped_state.json`
- `tests/fixtures/exporter_status_v046_treasure_relic_picked_state.json`

## Recommended Next Packet

The treasure route has now passed its first successful installed live proof. The next packet should be documentation/status consolidation or a small follow-up fixture if another treasure edge case appears; do not broaden exporter behavior without a separate approved packet.
