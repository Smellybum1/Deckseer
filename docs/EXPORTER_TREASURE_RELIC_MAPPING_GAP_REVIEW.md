# Deckseer Exporter Treasure Relic Mapping Gap Review

Status: `reviewed_followup_complete`

Prepared on 2026-05-25 after installed `v0.4.5` safely refused a visible treasure relic export because the current run had incomplete mapping coverage.

## Scope

This note records the observed mapping gaps from the installed `v0.4.5` treasure proof and hands them to a tiny reviewed data follow-up.

It does not approve:

- scoring logic changes
- empirical rows
- accuracy or relic accuracy baseline changes
- recommendation API changes
- watch mode, OCR, input automation, memory/process tricks, packet inspection, or save/profile modification

## Live Evidence

Installed `v0.4.5` observed a visible treasure relic screen:

- `screen_type: "exporter_status"`
- `exporter_version: "0.4.5"`
- `visible_reward_probe_status: "treasure_relic_model_seen"`
- visible relic identity: `LETTER_OPENER` -> `letter_opener`, known
- `relic_reward_live_export_candidate: "refused"`
- refusal reasons: `unmapped_deck_card`, `unmapped_potion`
- unknown deck identity: `ACCURACY` -> `accuracy`
- unknown potion identity: `HEART_OF_IRON` -> `heart_of_iron`, observed twice
- confirmed `recommend-export` rejected the file as `exporter_status`

Post-pickup clear-state passed:

- `visible_reward_probe_status: "reward_screen_completed"`
- `visible_reward_probe_last_event: "treasure_relic_picked"`
- identity review arrays cleared
- confirmed `recommend-export` rejected the file as `exporter_status`

## Reviewed Local Evidence

Local installed STS2 `v0.106.1` evidence:

- `release_info.json` reports `version: "v0.106.1"` and commit `d3584805`.
- `SlayTheSpire2.pck` contains English localization for `ACCURACY.title`: `Accuracy`.
- `SlayTheSpire2.pck` contains English localization for `ACCURACY.description`, describing Shivs dealing additional damage.
- `SlayTheSpire2.pck` contains English localization for `HEART_OF_IRON.title`: `Heart of Iron`.
- `SlayTheSpire2.pck` contains English localization for `HEART_OF_IRON.description`, describing gaining Plating.

## Follow-Up Decision

The reviewed mapping/data follow-up is complete in `docs/EXPORTER_TREASURE_RELIC_MAPPING_DATA_REVIEW.md`:

- `accuracy`: Silent power metadata for Shiv damage scaling.
- `heart_of_iron`: sparse potion metadata tagged as block/plating.

These records are identity and simplified-planning metadata only. They do not model exact numeric values, target rules, combat sequencing, or potion-advice behavior.

## Next Gate

Repo-local `v0.4.6` treats `ACCURACY` and `HEART_OF_IRON` as known. A later installed proof is still required before claiming successful live treasure `screen_type: "relic_reward"` export.
