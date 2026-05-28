# Deckseer Exporter Treasure Relic Data Review

Status: `installed_mapped_clear_verified`

Prepared on 2026-05-25 after installed `v0.4.3` revealed `LETTER_OPENER` as an unknown treasure relic mapping.

## Scope

This packet adds a tiny reviewed relic metadata record for Relic Choice V1 and updates the repo-local exporter status-diagnostic mapping snapshot.

The original data packet did not approve:

- live `screen_type: "relic_reward"` export for treasure relics
- live `screen_type: "card_reward"` changes
- installing or modifying the real STS2 mods folder
- relic scoring logic changes
- card data, potion data, empirical rows, card accuracy baselines, or recommendation API changes
- watch mode, OCR, screenshot capture, input automation, memory/process tricks, packet inspection, or save/profile modification

## Reviewed Evidence

Local installed STS2 `v0.106.1` evidence:

- `SlayTheSpire2.pck` contains English localization for `LETTER_OPENER.title`: `Letter Opener`.
- `SlayTheSpire2.pck` contains English localization for `LETTER_OPENER.description`, describing damage to all enemies after playing a threshold number of Skills in one turn.
- Installed `v0.4.3` status diagnostics revealed the live public ID `LETTER_OPENER`, normalized to `letter_opener`, on a visible treasure relic screen.
- Installed `v0.4.3` stayed status-only, refused live export with `treasure_relic_route_status_only`, and cleared after pickup.

## Decision

Add a `data/relics/relics.json` record:

- `letter_opener`: damage/AoE/skill-payoff metadata, weak positive prior, skill-dense and long-act contexts.

Add an accepted relic accuracy scenario:

- `skill_dense_letter_opener`: expects `letter_opener`.

The metadata remains simplified planning metadata. It does not model the exact Skill threshold, damage value, combat timing, enemy count, or turn-by-turn Skill sequencing.

## Exporter Mapping Impact

Repo-local `v0.4.4` adds `letter_opener` to the relic status-diagnostic mapping snapshot.

The installed `v0.4.4` mapped treasure proof verified:

- `LETTER_OPENER` maps to `letter_opener`
- treasure relic mapping known count becomes 1
- treasure relic mapping unknown count becomes 0
- treasure relics still write only `screen_type: "exporter_status"` unless a separate promotion packet is approved

## Verification

Packet verification:

- `recommend-relic tests\fixtures\relic_choice\skill_dense_letter_opener.json --format text`: `letter_opener` ranked first.
- `relic-accuracy-report --format text`: `PASS`, 6/6.
- `dotnet build exporter_mod\DeckseerExporter\DeckseerExporter.csproj ...`: 0 warnings / 0 errors.
- `inspect-export tests\fixtures\exporter_status_v044_treasure_relic_letter_opener_state.json`: valid status.
- confirmed `recommend-export tests\fixtures\exporter_status_v044_treasure_relic_letter_opener_state.json --confirmed --format text`: rejected as `exporter_status`.
- `pytest tests\test_relic_choice.py tests\test_relic_accuracy_report.py tests\test_models.py tests\test_exporter_state.py -q`: 100 passed.

## Installed v0.4.4 Startup Result

The real STS2 mods-folder install-check was separately approved and `v0.4.4` installed successfully.

Startup verification passed:

- installed manifest reports `version: "v0.4.4"`
- live export reports `exporter_version: "0.4.4"`
- live export remains `screen_type: "exporter_status"`
- `visible_reward_probe_status: "not_observed"`
- `visible_relic_reward_option_count: 0`
- `relic_reward_live_export_candidate: "refused"`
- refusal reasons include `no_visible_relic_reward` and `missing_required_run_state_field`
- `relic_reward_live_export_candidate_writes_recommendation_state: false`
- `inspect-export` accepts the live status file

No visible treasure relic was tested in this install-check.

## Installed v0.4.4 Treasure Relic Mapping Proof

A later live treasure chest proof with installed `v0.4.4` verified the reviewed mapping:

- live export remained `screen_type: "exporter_status"`
- `exporter_version: "0.4.4"`
- `visible_reward_probe_status: "treasure_relic_model_seen"`
- `visible_reward_probe_last_event: "treasure_relic_holder_initialized"`
- `visible_relic_reward_option_count: 1`
- `relic_reward_identity_review_probe: "ids_revealed_for_review"`
- `relic_reward_identity_review_option_count: 1`
- `relic_reward_identity_review_mapping_known_count: 1`
- `relic_reward_identity_review_mapping_unknown_count: 0`
- the visible identity item reported `public_model_id: "LETTER_OPENER"` and `normalized_candidate_id: "letter_opener"`
- `deckseer_mapping_status: "known"` and `deckseer_id: "letter_opener"`
- `relic_reward_live_export_candidate: "refused"`
- refusal reasons included `treasure_relic_route_status_only`
- `relic_reward_live_export_candidate_writes_recommendation_state: false`
- confirmed `recommend-export` rejected the visible file as `exporter_status`

After pickup, installed `v0.4.4` cleared the treasure relic diagnostics:

- `visible_reward_probe_status: "reward_screen_completed"`
- `visible_reward_probe_last_event: "treasure_relic_picked"`
- `visible_relic_reward_option_count: 0`
- `relic_reward_identity_review_probe: "cleared"`
- relic reward identity counts and items cleared to zero
- confirmed `recommend-export` rejected the closed file as `exporter_status`

This proof validates local mapping coverage only. It does not promote treasure relics to live `screen_type: "relic_reward"`.

## Next Gate

The installed `v0.4.4` startup and `LETTER_OPENER` treasure mapping proof is complete. Promoting treasure relics to live `screen_type: "relic_reward"` remains a separate packet that requires explicit approval. `docs/EXPORTER_TREASURE_RELIC_LIVE_EXPORT_READINESS.md` records the remaining blockers and acceptance criteria.
