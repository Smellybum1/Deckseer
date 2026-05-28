# Deckseer Exporter Treasure Relic Mapping Review

Status: `reviewed_data_followup_complete`

Prepared on 2026-05-25 after installed `v0.4.3` startup, visible treasure relic, and post-pickup clear-state verification.

## Scope

This note records the mapping review handoff for the installed `v0.4.3` treasure relic status diagnostic. It is review evidence only.

The follow-up data packet is complete in `docs/EXPORTER_TREASURE_RELIC_DATA_REVIEW.md`.

This note did not approve:

- live `screen_type: "relic_reward"` export for treasure relics
- live `screen_type: "card_reward"` changes
- relic scoring, priors, tags, roles, accuracy scenarios, empirical rows, recommendation behavior, or baselines
- watch mode, OCR, screenshot capture, input automation, memory/process access, packet inspection, save/profile reads, or game-file changes

## Observed Evidence

Installed `v0.4.3` stayed inside the status-only boundary on a human-opened visible treasure chest relic screen:

- `screen_type: "exporter_status"`
- `exporter_version: "0.4.3"`
- `visible_reward_probe_status: "treasure_relic_model_seen"`
- `visible_reward_probe_last_event: "treasure_relic_holder_initialized"`
- `visible_relic_reward_option_count: 1`
- `relic_reward_live_export_candidate: "refused"`
- `relic_reward_live_export_refusal_reasons` included `treasure_relic_route_status_only`
- `relic_reward_identity_review_probe: "ids_revealed_for_review"`
- `relic_reward_identity_review_error: null`
- `relic_reward_identity_review_option_count: 1`
- `relic_reward_identity_review_mapping_known_count: 0`
- `relic_reward_identity_review_mapping_unknown_count: 1`
- `recommend-export --confirmed` rejected the live file because it was still `exporter_status`

Review item:

| Position | Public model ID | Normalized candidate | Deckseer mapping status | Deckseer ID |
| ---: | --- | --- | --- | --- |
| 0 | `LETTER_OPENER` | `letter_opener` | `unknown` | null |

After the relic was picked, installed `v0.4.3` cleared the diagnostic:

- `visible_reward_probe_status: "reward_screen_completed"`
- `visible_reward_probe_last_event: "treasure_relic_picked"`
- `visible_relic_reward_option_count: 0`
- `relic_reward_identity_review_probe: "cleared"`
- relic reward identity review counts were zero
- relic reward identity review items were empty
- `recommend-export --confirmed` rejected the cleared file because it was still `exporter_status`

## Review Interpretation

The result proves the public `RelicModel.Id` route can reveal a treasure relic identity string after `RelicModel.CanonicalInstance` and serialization failed to recover a non-null public ID in installed `v0.4.2`.

The result does not prove a recommendation behavior problem. It only identifies a relic data/mapping coverage gap for `LETTER_OPENER`.

Unknown treasure relic IDs should be handled as normal reviewed metadata candidates, not patched into the exporter as aliases and not used directly as recommendation input.

## Reviewed Data Follow-Up

Completed on 2026-05-25 after explicit user approval.

Deckseer now has reviewed relic metadata for `letter_opener`, based on installed STS2 `v0.106.1` pck localization and installed `v0.4.3` live public-ID evidence. Repo-local `v0.4.4` adds `letter_opener` to the relic status-diagnostic mapping snapshot while keeping treasure relics status-only.

This follow-up did not install a mod package, update the real STS2 mods folder, promote treasure relics to `screen_type: "relic_reward"`, add watch mode, or change scorer rules.

## Safe Follow-Up Options

Safe next packets remain separate:

- Optional installed `v0.4.4` check: verify the real mod reports `LETTER_OPENER` as known if another natural treasure relic screen offers it.
- Treasure relic live export promotion design: only after treasure route run-state alignment, mapping coverage, and stale-state behavior are separately accepted for recommendation-ready export.
- Additional treasure relic mapping review: repeat the status-only diagnostic when another natural chest relic appears.

## Current Blocker

Do not promote treasure relics to live `screen_type: "relic_reward"` from this note. The installed proof is intentionally diagnostic-only, and the reviewed data follow-up only resolves local metadata/mapping coverage.
