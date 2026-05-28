# Deckseer Exporter Card Reward Relic/Potion Mapping Review

Status: `reviewed_data_followup_complete`

Prepared on 2026-05-24 after installed `v0.2.16` startup, visible reward-screen, and clear-state verification.

## Scope

This note records the mapping review handoff for the installed `v0.2.16` relic/potion ID review diagnostic. It is review evidence only.

It does not approve:

- live `screen_type: "card_reward"` export
- live `screen_type: "relic_reward"` export
- recommendation-ready relic or potion arrays
- further relic data additions beyond the reviewed `ring_of_the_snake` and `lead_paperweight` follow-up
- potion data additions
- relic or card scoring changes
- quality prior, role, tag, empirical, accuracy, recommendation, or baseline changes
- watch mode, OCR, screenshot capture, input automation, memory/process access, packet inspection, save/profile reads, or game-file changes

## Observed Evidence

Installed `v0.2.16` stayed inside the status-only boundary on a human-opened visible three-card reward screen:

- `screen_type: "exporter_status"`
- `exporter_version: "0.2.16"`
- `relic_potion_identity_review_probe: "ids_revealed_for_review"`
- `relic_potion_identity_review_last_event: "rewards_screen_shown"`
- `relic_identity_review_count: 2`
- `relic_identity_review_mapping_known_count: 0`
- `relic_identity_review_mapping_unknown_count: 2`
- `potion_identity_review_count: 0`
- `potion_identity_review_mapping_known_count: 0`
- `potion_identity_review_mapping_unknown_count: 0`
- `card_reward_live_export_candidate: "refused"`
- `card_reward_live_export_refusal_reasons`: `unmapped_relic`
- `card_reward_live_export_missing_fields: []`
- `card_reward_live_export_unmapped_reward_count: 0`
- `card_reward_live_export_unmapped_deck_count: 0`
- `card_reward_live_export_unmapped_relic_count: 2`
- `card_reward_live_export_unmapped_potion_count: 0`
- `card_reward_live_export_candidate_writes_recommendation_state: false`
- visible reward mapping remained 3 known / 0 unknown
- deck mapping remained 14 known / 0 unknown

`inspect-export` accepted the live status file. `recommend-export --confirmed` rejected it because status files are not recommendation input.

After the reward screen was skipped/left, installed `v0.2.16` cleared the diagnostic:

- `relic_potion_identity_review_probe: "cleared"`
- relic identity review counts were zero
- potion identity review counts were zero
- relic identity review items were empty
- potion identity review items were empty
- deck and card identity review items were empty
- unmapped reward, deck, relic, and potion counts were zero

## Review Items

| Position | Public model ID | Normalized candidate | Deckseer mapping status | Deckseer ID |
| ---: | --- | --- | --- | --- |
| 0 | `RING_OF_THE_SNAKE` | `ring_of_the_snake` | `unknown` | null |
| 1 | `LEAD_PAPERWEIGHT` | `lead_paperweight` | `unknown` | null |

No potion IDs were observed because the tested run had zero potions.

## Review Interpretation

The `v0.2.16` result proves the approved public serialization route can reveal current relic identity strings during a visible card reward screen and clear them after the reward screen closes.

The observed live `card_reward` candidate was blocked in the installed `v0.2.16` package because both current relic IDs were unknown to that installed mapping snapshot. Installed `v0.2.17` adds reviewed data and mapping snapshot coverage for both IDs; the visible proof reports candidate `ready` while still writing only `exporter_status`.

The result does not prove a recommendation behavior problem. It only identifies current relic data/mapping coverage gaps.

Unknown relic IDs should be handled as normal reviewed metadata candidates, not patched into the exporter as aliases and not used directly as recommendation input.

## Safe Follow-Up Options

Safe next packets remain separate:

- Potion identity proof packet: later verify non-empty potion belts through the same status-only diagnostic when a run naturally has potions.
- Live `card_reward` export implementation packet: use the ready-but-status-only `v0.2.17` candidate as the proof basis, preserving `requires_user_confirmation` and `recommend-export --confirmed` behavior.

## Current Blocker

At the time of this handoff, live `screen_type: "card_reward"` export still needed a separate implementation packet even though the observed visible reward, deck, and relic mappings were clean in installed `v0.2.17`.

Follow-up, 2026-05-25: this blocker is historical. Later packets accepted ADR 4, proved mixed reward freshness and mapping readiness, and live-proved installed `v0.4.7` with a fully mapped confirmed card reward plus post-selection downgrade.
