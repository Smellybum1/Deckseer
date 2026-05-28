# Deckseer Exporter Card Reward Relic Data Review

Status: `installed_clear_verified`

Prepared on 2026-05-24 after installed `v0.2.16` revealed `RING_OF_THE_SNAKE` and `LEAD_PAPERWEIGHT` as the two unknown relic mappings blocking the status-only live export candidate.

## Scope

This packet adds a tiny reviewed relic metadata batch for Relic Choice V1 and updates the repo-local exporter status-diagnostic mapping snapshot.

The original data packet did not approve:

- live `screen_type: "card_reward"` export
- live `screen_type: "relic_reward"` export
- installing or modifying the real STS2 mods folder
- scoring logic changes
- card data, potion data, empirical rows, card accuracy baselines, or recommendation API changes
- watch mode, OCR, screenshot capture, input automation, memory/process tricks, packet inspection, or save/profile modification

## Reviewed Evidence

Local installed STS2 `v0.106.1` evidence:

- `release_info.json` reports `version: "v0.106.1"` and commit `d3584805`.
- `SlayTheSpire2.pck` contains English localization for `RING_OF_THE_SNAKE.title`: `Ring of the Snake`.
- `SlayTheSpire2.pck` contains English localization for `RING_OF_THE_SNAKE.description`, describing additional draw at the start of combat.
- `SlayTheSpire2.pck` contains English localization for `LEAD_PAPERWEIGHT.title`: `Lead Paperweight`.
- `SlayTheSpire2.pck` contains English localization for `LEAD_PAPERWEIGHT.description`, describing a pickup choice of one of two Colorless cards added to the deck.
- Installed `v0.2.16` status diagnostics revealed the live public IDs `RING_OF_THE_SNAKE` and `LEAD_PAPERWEIGHT`, normalized to `ring_of_the_snake` and `lead_paperweight`.

## Decision

Add `data/relics/relics.json` records:

- `ring_of_the_snake`: draw/consistency metadata, weak positive prior, early/elite-prep/consistency contexts.
- `lead_paperweight`: colorless/deck-quality/card-add metadata, weak positive prior, early/consistency contexts.

Add accepted relic accuracy scenarios:

- `early_consistency_ring`: expects `ring_of_the_snake`.
- `colorless_deck_quality`: expects `lead_paperweight`.

The metadata remains simplified planning metadata. It does not model exact draw counts, colorless card-pool EV, starter-relic ownership rules, or trigger timing.

## Repo-Local Exporter Mapping Impact

Repo-local `v0.2.17` adds `ring_of_the_snake` and `lead_paperweight` to the relic status-diagnostic mapping snapshot.

Expected impact on the previously observed visible reward-screen run after a separately approved install-check:

- `RING_OF_THE_SNAKE` maps to `ring_of_the_snake`
- `LEAD_PAPERWEIGHT` maps to `lead_paperweight`
- relic mapping known count becomes 2
- relic mapping unknown count becomes 0

The exporter still writes only `screen_type: "exporter_status"` in this packet.

## Verification

Packet verification:

- `recommend-relic tests\fixtures\relic_choice\early_consistency_ring.json --format text`: `ring_of_the_snake` ranked first.
- `recommend-relic tests\fixtures\relic_choice\colorless_deck_quality.json --format text`: `lead_paperweight` ranked first.
- `relic-accuracy-report --format text`: `PASS`, 5/5.
- `data-health`: `PASS`.
- `dotnet build exporter_mod\DeckseerExporter\DeckseerExporter.csproj "/p:ModsPath=D:/Codex/Deckseer/exporter_mod/local_mods/"`: 0 warnings / 0 errors.
- `qa --check-recommendation-baseline --check-accuracy --check-empirical-triage`: `PASS`.
- `accuracy-report --format text`: `PASS`, 9/9.
- `empirical-coverage --format text`: `REVIEW`, 18 rows, 14 `patch_mismatch` warnings.
- `pytest -q --basetemp .codex_pytest_tmp_full_relicdata -p no:cacheprovider`: 357 passed.
- `git diff --check`: passed with CRLF warnings only.

## Installed v0.2.17 Startup Result

The real STS2 mods-folder install-check was separately approved and `v0.2.17` installed successfully.

Startup verification passed:

- installed manifest reports `version: "v0.2.17"`
- live export reports `exporter_version: "0.2.17"`
- live export remains `screen_type: "exporter_status"`
- `relic_potion_identity_review_probe: "not_observed"`
- relic and potion identity review counts are zero
- `card_reward_live_export_candidate: "refused"`
- refusal reasons include `no_visible_reward` and `missing_required_run_state_field`
- `card_reward_live_export_candidate_writes_recommendation_state: false`
- `inspect-export` accepts the live status file
- `recommend-export --confirmed` rejects the live file because it is still `exporter_status`

## Installed v0.2.17 Visible Reward-Screen Result

On a human-opened visible three-card reward screen, installed `v0.2.17` stayed status-only and produced the intended mapping-ready candidate result:

- live export remains `screen_type: "exporter_status"`
- `card_reward_live_export_candidate: "ready"`
- `card_reward_live_export_refusal_reasons: []`
- `card_reward_live_export_missing_fields: []`
- unmapped reward, deck, relic, and potion counts are all zero
- `card_reward_live_export_candidate_writes_recommendation_state: false`
- required run-state field presence diagnostics are true
- deck mapping is 14 known / 0 unknown
- relic mapping is 2 known / 0 unknown
- potion count is 0
- visible reward mapping is 3 known / 0 unknown
- `inspect-export` accepts the live status file
- `recommend-export --confirmed` rejects the live file because it is still `exporter_status`

Reviewed relic mappings:

- `RING_OF_THE_SNAKE` -> `ring_of_the_snake`
- `LEAD_PAPERWEIGHT` -> `lead_paperweight`

Visible reward choices remained:

- `CLOAK_AND_DAGGER` -> `cloak_and_dagger`
- `BOUNCING_FLASK` -> `bouncing_flask`
- `INFINITE_BLADES` -> `infinite_blades`

## Installed v0.2.17 Clear-State Result

After the reward screen was skipped/left, installed `v0.2.17` cleared the live review diagnostics while staying status-only:

- live export remains `screen_type: "exporter_status"`
- `card_reward_live_export_candidate: "refused"`
- refusal reasons include `stale_reward_screen` and `missing_required_run_state_field`
- unmapped reward, deck, relic, and potion counts are all zero
- `card_reward_live_export_candidate_writes_recommendation_state: false`
- `card_reward_run_state_runtime_probe: "cleared"`
- `visible_reward_probe_status: "reward_screen_completed"`
- deck, relic, potion, and card identity review items are empty
- deck, relic, potion, and card identity review counts are zero
- `inspect-export` accepts the live status file
- `recommend-export --confirmed` rejects the live file because it is still `exporter_status`

## Next Gate

The installed `v0.2.17` startup, visible reward-screen, and clear-state proof is complete. A later packet may implement live `screen_type: "card_reward"` only if it preserves the human-confirmed boundary and keeps `recommend-export` confirmation behavior covered by fixtures.
