# Exporter Card Reward Colorless Potion Mapping Review

Status: `installed_v036_colorless_potion_mapping_verified`

This note records the review handoff for the installed `v0.3.5` post-pickup potion identity proof and the tiny reviewed data/mapping follow-up. It remains review-only and does not approve live recommendation export from mixed reward screens.

## Evidence

Installed `v0.3.5` stayed status-only after the user picked gold and potion rewards before reaching the card reward choice.

Observed diagnostic evidence:

- `screen_type: "exporter_status"`
- `visible_reward_probe_last_event: "reward_collected"`
- `card_reward_run_state_runtime_probe: "serializable_run_seen"`
- `card_reward_run_state_potion_count: 1`
- `relic_potion_identity_review_probe: "ids_revealed_for_review"`
- `potion_identity_review_count: 1`
- `potion_identity_review_items[0].public_model_id: "COLORLESS_POTION"`
- `potion_identity_review_items[0].normalized_candidate_id: "colorless_potion"`
- `potion_identity_review_items[0].deckseer_mapping_status: "unknown"`

No live gold value, HP value, top-level `potions`, recommendation-ready `card_reward`, selected-card identity, save/profile data, OCR, watch mode, input automation, memory/process access, or packet inspection was exported.

## Reviewed Follow-Up

Repo-local `v0.3.6` adds `colorless_potion` to Deckseer's sparse potion catalog and to the exporter status-diagnostic potion mapping snapshot.

The data record is intentionally minimal:

- id: `colorless_potion`
- name: `Colorless Potion`
- tag: `card_generation`

This is a mapping/data-health seed only. It does not model exact potion behavior, target rules, combat value, scoring, priors, empirical evidence, accuracy baselines, or recommendation behavior.

## v0.3.6 Install-Check Result

The real STS2 mods-folder install-check was approved and passed. Startup verification reported:

- `screen_type: "exporter_status"`
- `exporter_version: "0.3.6"`
- `visible_reward_probe_status: "not_observed"`
- `card_reward_live_export_candidate: "refused"`
- no top-level `card_reward`, live gold, HP, or `potions`

On a visible card reward screen after the user picked gold and potion rewards, with Colorless Potion in the potion belt, installed `v0.3.6` reported:

- `visible_reward_probe_status: "card_reward_model_seen"`
- `visible_reward_probe_last_event: "reward_collected"`
- `visible_card_reward_option_count: 3`
- `card_reward_run_state_runtime_probe: "serializable_run_seen"`
- `card_reward_run_state_potion_count: 1`
- `relic_potion_identity_review_probe: "ids_revealed_for_review"`
- `potion_identity_review_count: 1`
- `potion_identity_review_items[0].public_model_id: "COLORLESS_POTION"`
- `potion_identity_review_items[0].normalized_candidate_id: "colorless_potion"`
- `potion_identity_review_mapping_known_count: 1`
- `potion_identity_review_mapping_unknown_count: 0`
- `potion_identity_review_items[0].deckseer_id: "colorless_potion"`
- `card_reward_live_export_unmapped_potion_count: 0`
- `card_reward_live_export_refusal_reasons`: `mixed_reward_screen_state_may_change`, `missing_required_run_state_field`
- `card_reward_live_export_mixed_reward_freshness_blockers`: `run_state_not_aligned`, `visible_reward_player_not_aligned`, `mixed_reward_live_export_not_approved`
- `card_reward_live_export_candidate_writes_recommendation_state: false`
- no top-level `card_reward`, live gold, HP, or `potions`
- `recommend-export --confirmed` rejected the live file because it remained `exporter_status`

## Next Step

Continue with current-player/visible-reward-player alignment design before revisiting mixed reward `card_reward` export. Do not enable mixed reward recommendation-ready export until the remaining alignment blockers are resolved and explicitly approved.
