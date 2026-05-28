# Deckseer Exporter Card Reward Dramatic Entrance Data Review

Status: `installed_clear_verified`

Prepared on 2026-05-24 after installed `v0.2.13` reduced the observed live deck mapping gap to one unknown: `DRAMATIC_ENTRANCE` / `dramatic_entrance`.

## Scope

This packet adds reviewed seed metadata for `dramatic_entrance` so the exporter mapping snapshot can treat the observed public deck ID as known in a later repo-local exporter build.

It does not approve:

- live `screen_type: "card_reward"` export
- scoring logic changes
- empirical rows
- accuracy baseline changes
- recommendation API changes
- watch mode, OCR, input automation, memory/process tricks, packet inspection, or save/profile modification

## Reviewed Evidence

Local installed STS2 `v0.106.1` evidence:

- `release_info.json` reports `version: "v0.106.1"` and commit `d3584805`.
- `SlayTheSpire2.pck` contains English localization for `DRAMATIC_ENTRANCE.title`: `Dramatic Entrance`.
- `SlayTheSpire2.pck` contains English localization for `DRAMATIC_ENTRANCE.description`: `Deal {Damage:diff()} damage to ALL enemies.`
- `SlayTheSpire2.pck` contains a colorless asset path: `colorless/dramatic_entrance.png`.
- `SlayTheSpire2.pck` changelog text says damage changed from `15(20)` to `11(15)`.

External cross-check:

- Untapped.gg Slay the Spire 2 card page reports `Dramatic Entrance` as a 0-cost Uncommon Attack with `Innate`, `Deal 11 damage to ALL enemies`, and `Exhaust`, with upgraded damage 15.

## Decision

Add `data/cards/neutral.json` entry:

- `id`: `dramatic_entrance`
- `name`: `Dramatic Entrance`
- `character`: `neutral`
- `type`: `attack`
- `rarity`: `uncommon`
- `cost`: 0
- `tags`: `damage`, `aoe`, `free`, `innate`, `exhaust`
- `roles`: `frontload`, `aoe`, `burst`
- `quality_prior`: 0.0
- `pick_context`: `early`, `frontload`, `aoe`
- `source_patch`: `v0.106.1`
- `effects.damage`: 11
- `effects.extra.upgraded_damage`: 15

Use a neutral seed prior because this packet establishes identity and simplified effects only. It does not include a reviewed tier, empirical result, or accepted accuracy scenario.

## Repo-Local Exporter Mapping Impact

Repo-local `v0.2.14` adds `dramatic_entrance` to the status-diagnostic mapping snapshot.

Expected impact on the previously observed 14-card deck:

- `STRIKE_SILENT` x5 maps to `strike`
- `DEFEND_SILENT` x5 maps to `defend`
- `DRAMATIC_ENTRANCE` x1 maps to `dramatic_entrance`
- deck mapping known count becomes 14
- deck mapping unknown count becomes 0

## Installed v0.2.14 Startup Result

The real STS2 mods-folder install-check was approved and `v0.2.14` installed successfully.

Startup verification passed:

- installed manifest reports `version: "v0.2.14"`
- live export reports `exporter_version: "0.2.14"`
- live export remains `screen_type: "exporter_status"`
- `card_reward_run_state_runtime_probe: "not_observed"`
- `deck_identity_review_probe: "not_observed"`
- `deck_identity_review_items: []`
- `card_reward_run_state_writes_recommendation_state: false`
- `inspect-export` accepts the live status file
- `recommend-export --confirmed` rejects the live file because it is still `exporter_status`

## Installed v0.2.14 Visible Reward-Screen Result

On a human-opened visible three-card reward screen, the live file remained status-only:

- `screen_type: "exporter_status"`
- `exporter_version: "0.2.14"`
- `card_reward_run_state_runtime_probe: "run_state_seen"`
- `card_reward_run_state_runtime_last_event: "rewards_screen_shown"`
- deck card count 14
- deck card ID read count 14
- deck mapping known count 14
- deck mapping unknown count 0
- `deck_identity_review_probe: "ids_revealed_for_review"`
- `deck_identity_review_mapping_known_count: 14`
- `deck_identity_review_mapping_unknown_count: 0`
- `DRAMATIC_ENTRANCE` maps to `dramatic_entrance`
- `card_reward_run_state_writes_recommendation_state: false`

The visible reward choices also mapped under the existing status diagnostic:

- `CLOAK_AND_DAGGER` -> `cloak_and_dagger`
- `BOUNCING_FLASK` -> `bouncing_flask`
- `INFINITE_BLADES` -> `infinite_blades`

`inspect-export` accepted the live status file. `recommend-export --confirmed` rejected it because it is still `exporter_status`.

## Installed v0.2.14 Clear-State Result

After the reward screen was skipped/left, the live file remained status-only:

- `screen_type: "exporter_status"`
- `exporter_version: "0.2.14"`
- `card_reward_run_state_runtime_probe: "cleared"`
- `card_reward_run_state_runtime_last_event: "reward_skipped"`
- run-state booleans false or absent
- deck card count 0
- deck mapping known count 0
- deck mapping unknown count 0
- `deck_identity_review_probe: "cleared"`
- `deck_identity_review_items: []`
- `visible_card_reward_option_count: 0`
- `card_identity_review_probe: "cleared"`
- `card_identity_review_items: []`
- `card_reward_run_state_writes_recommendation_state: false`

`inspect-export` accepted the live clear-state file. `recommend-export --confirmed` rejected it because it is still `exporter_status`.

## Next Gate

The installed `v0.2.14` startup, visible reward-screen, and clear-state proof is complete. Any live `screen_type: "card_reward"` export remains a separate approval packet.
