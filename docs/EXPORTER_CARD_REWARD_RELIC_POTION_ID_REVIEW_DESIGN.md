# Deckseer Exporter Card Reward Relic/Potion ID Review Design

Status: `repo_local_v0216_verified`

Prepared on 2026-05-24 after installed `v0.2.15` startup, visible reward-screen, and clear-state verification. The visible proof kept `screen_type: "exporter_status"`, mapped visible reward cards and deck cards completely, and refused the live export candidate with `unmapped_relic`.

## Goal

Define the smallest safe status-only diagnostic that can reveal enough relic and potion identity evidence to review live `card_reward` export blockers.

This design does not install a mod package, launch STS2, or approve live recommendation-ready export. ADR 6 is accepted, and repo-local `v0.2.16` implements the status-only diagnostic described here.

## Current Blocker

Installed `v0.2.15` proved:

- reward card mapping: 3 known / 0 unknown
- deck card mapping: 14 known / 0 unknown
- required run-state presence fields available during the visible reward screen
- relic count: 2
- potion count: 0
- live export candidate: `refused`
- refusal reason: `unmapped_relic`
- live export remained `screen_type: "exporter_status"`
- `recommend-export --confirmed` rejected the live file because status files are not recommendation input
- clear-state behavior cleared the review arrays and refused stale state

Because `v0.2.15` intentionally exports relic and potion counts only, the project cannot identify which relic IDs are blocking the candidate. Non-empty potion identity mapping is also unproven because the tested run had 0 potions.

## Proposed Diagnostic Shape

Repo-local `v0.2.16` adds a relic/potion identity review section under `export_metadata.diagnostics` while still writing only:

```json
{
  "screen_type": "exporter_status"
}
```

Allowed diagnostic keys:

```json
{
  "relic_potion_identity_review_probe": "ids_revealed_for_review",
  "relic_potion_identity_review_last_event": "rewards_screen_shown",
  "relic_identity_review_count": 2,
  "relic_identity_review_mapping_known_count": 1,
  "relic_identity_review_mapping_unknown_count": 1,
  "potion_identity_review_count": 0,
  "potion_identity_review_mapping_known_count": 0,
  "potion_identity_review_mapping_unknown_count": 0,
  "relic_identity_review_items": [
    {
      "position": 0,
      "public_model_id": "example_public_relic_id",
      "normalized_candidate_id": "example_public_relic_id",
      "deckseer_mapping_status": "known",
      "deckseer_id": "example_public_relic_id"
    }
  ],
  "potion_identity_review_items": [],
  "relic_potion_identity_review_error": null
}
```

The example values are placeholders, not observed live output.

## Allowed Fields

The diagnostic may reveal:

- stable review index or slot position
- public relic/potion identity string from the same public serialization route already compile-checked
- normalized candidate ID after deterministic normalization
- Deckseer mapping status: `known`, `unknown`, `duplicate`, or `invalid`
- Deckseer ID only when the normalized candidate exactly matches one reviewed Deckseer relic or potion ID
- relic and potion counts
- known and unknown mapping counts
- route/event name such as `rewards_screen_shown` or `reward_skipped`
- error type name if the diagnostic fails

## Forbidden Fields

The diagnostic must not export:

- `screen_type: "card_reward"`
- `screen_type: "relic_reward"` or live relic reward choices
- HP values
- gold values
- act, floor, or ascension values
- character ID
- map/path data
- selected-card identity
- selected/skipped action outcome beyond the existing clear-state event label
- relic display names, localized titles, rules text, rarity, roles, priors, effects, or scoring metadata
- potion display names, localized titles, rules text, roles, priors, effects, or scoring metadata
- recommendation-ready relic or potion arrays
- any payload accepted by `recommend-export` as recommendation input
- save/profile data or run-history file contents
- OCR, screenshots, watch mode, input automation, private-field reflection, publicizer workarounds, memory/process access, or packet inspection

## Mapping Rules

The exporter diagnostic may use deterministic normalization only:

- lower-case public IDs
- convert non-alphanumeric separators to underscores
- trim leading/trailing underscores

Known mappings should be checked against the existing Deckseer data snapshots:

- relic IDs from `data/relics/relics.json`
- potion IDs from `data/potions/potions.json`

Current reviewed IDs are intentionally sparse:

- relics: `burning_blood`, `akabeko`, `kunai`
- potions: `fire_potion`, `block_potion`

Unknown mappings are review evidence, not runtime failures and not approval to add data. Any data packet remains separate and must follow the normal reviewed metadata and accuracy guardrails.

## Lifecycle

When a visible card reward screen is active:

- emit relic/potion identity review diagnostics under `exporter_status`
- keep live export candidate refusal logic active
- keep both recommendation-write flags false

When the reward screen closes, is skipped, or is completed:

- clear relic and potion identity review items
- zero relic/potion identity review counts
- keep `screen_type: "exporter_status"`
- keep `recommend-export` rejection behavior

## Repo-Local v0.2.16 Verification

Completed before any install-check:

1. ADR 6 is accepted.
2. Repo-local build passes with 0 warnings and 0 errors.
3. `inspect-export` accepts a status fixture containing relic/potion identity review metadata.
4. `recommend-export --confirmed` rejects the same fixture because it is `exporter_status`.
5. Focused exporter status tests verify metadata preservation and refusal as recommendation input.

The repo-local implementation does not install the real STS2 mod package, does not launch STS2, does not write `screen_type: "card_reward"`, and does not change relic data, potion data, scoring, empirical data, accuracy expectations, recommendation behavior, or baselines.

## Installed v0.2.16 Startup Verification

The real STS2 mods-folder install-check was approved and installed `v0.2.16`.

Startup verification passed:

- installed manifest reports `version: "v0.2.16"`
- live export reports `exporter_version: "0.2.16"`
- live export remains `screen_type: "exporter_status"`
- `relic_potion_identity_review_probe: "not_observed"`
- relic identity review counts are zero
- potion identity review counts are zero
- relic and potion identity review item arrays are empty
- `card_reward_live_export_candidate: "refused"`
- refusal reasons are `no_visible_reward` and `missing_required_run_state_field`
- `card_reward_live_export_candidate_writes_recommendation_state: false`
- `inspect-export` accepts the live status file
- `recommend-export --confirmed` rejects the live file because it is still `exporter_status`

## Installed v0.2.16 Visible Reward-Screen Verification

On a human-opened visible three-card reward screen, installed `v0.2.16` stayed status-only and produced the intended relic/potion ID review diagnostic:

- live export remained `screen_type: "exporter_status"`
- live export reported `exporter_version: "0.2.16"`
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
- `inspect-export` accepts the live status file
- `recommend-export --confirmed` rejects the live file because it is still `exporter_status`

Relic identity review items:

- `RING_OF_THE_SNAKE` -> `ring_of_the_snake` -> unknown
- `LEAD_PAPERWEIGHT` -> `lead_paperweight` -> unknown

These IDs are review evidence only. This proof does not approve relic data changes, potion data changes, scoring changes, empirical changes, accuracy expectation changes, recommendation behavior changes, or live `card_reward` export.

## Installed v0.2.16 Clear-State Verification

After the reward screen was skipped/left, installed `v0.2.16` cleared relic/potion identity review diagnostics:

- live export remained `screen_type: "exporter_status"`
- live export reported `exporter_version: "0.2.16"`
- `relic_potion_identity_review_probe: "cleared"`
- `relic_potion_identity_review_last_event: "reward_skipped"`
- relic identity review counts were zero
- potion identity review counts were zero
- relic identity review items were empty
- potion identity review items were empty
- deck identity review items were empty
- card identity review items were empty
- `card_reward_run_state_runtime_probe: "cleared"`
- `card_reward_live_export_candidate: "refused"`
- `card_reward_live_export_refusal_reasons`: `stale_reward_screen`, `missing_required_run_state_field`
- unmapped reward, deck, relic, and potion counts were zero
- `card_reward_live_export_candidate_writes_recommendation_state: false`
- `inspect-export` accepts the live status file
- `recommend-export --confirmed` rejects the live file because it is still `exporter_status`

For a live install-check after explicit approval:

1. Startup emits no relic/potion identity review items.
2. A human-opened visible reward screen emits relic/potion identity review items under `exporter_status`.
3. The review items explain known/unknown mapping counts without exporting HP, gold, character, recommendation-ready relic arrays, recommendation-ready potion arrays, or `card_reward`.
4. Leaving/skipping/completing the reward screen clears relic/potion identity review items.
5. `inspect-export` accepts the live status file.
6. `recommend-export --confirmed` rejects the live file because it is still `exporter_status`.

## Stop Conditions

Stop before implementation if:

- ADR 6 is not accepted
- exact relic/potion identity proof requires private fields, reflection, publicizer workarounds, memory/process access, screenshots/OCR, save/profile reads, reward generation, input automation, or packet inspection
- the diagnostic would become accepted recommendation input
- the mapping depends on localized names or fuzzy matching
- implementation would require relic data changes, potion data changes, scoring changes, empirical changes, baseline changes, or recommendation behavior changes
- implementation would require live `card_reward`, live `relic_reward`, watch mode, or input automation

## Next Gate

The installed `v0.2.16` startup, visible reward-screen, and clear-state proof is complete. `docs/EXPORTER_CARD_REWARD_RELIC_POTION_MAPPING_REVIEW.md` records the revealed relic IDs as review evidence, and `docs/EXPORTER_CARD_REWARD_RELIC_DATA_REVIEW.md` records the reviewed metadata plus installed `v0.2.17` startup, visible reward-screen, and clear-state proof for `ring_of_the_snake` and `lead_paperweight`. Live `card_reward` export remains a separate implementation gate.
