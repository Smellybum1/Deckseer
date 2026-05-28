# Deckseer Exporter Card Reward Deck ID Reveal Design

Status: `v0214_clear_verified`

Prepared on 2026-05-24 after installed `v0.2.11` reported a 3-known/11-unknown live deck mapping count under `screen_type: "exporter_status"`. Updated after ADR 5 acceptance, repo-local `v0.2.12` implementation, installed startup verification, installed visible reward-screen verification, clear-state verification, and repo-local `v0.2.13` Silent starter alias mapping.

## Goal

Define the smallest safe diagnostic that can reveal enough deck identity evidence to review live deck mapping gaps before any `screen_type: "card_reward"` export.

This design does not install a mod package, launch STS2, or approve live recommendation-ready export.

## Current Blocker

Installed `v0.2.11` proved:

- runtime run-state fields are present during a visible reward screen
- deck count can be read
- deck card IDs can be counted
- the current mapping snapshot can count known and unknown deck mappings
- clear-state behavior works after the reward screen is skipped or left

The same proof also showed:

- deck count 14
- deck card ID read count 14
- deck mapping known count 3
- deck mapping unknown count 11

Because `v0.2.11` intentionally did not export live deck IDs, the project cannot identify the 11 unknown deck cards from the status file alone.

## Proposed Diagnostic Shape

Repo-local `v0.2.12` adds a `deck_identity_review` section under `export_metadata.diagnostics` while still writing only:

```json
{
  "screen_type": "exporter_status"
}
```

Allowed diagnostic keys:

```json
{
  "deck_identity_review_probe": "ids_revealed_for_review",
  "deck_identity_review_last_event": "rewards_screen_shown",
  "deck_identity_review_card_count": 14,
  "deck_identity_review_unique_card_count": 9,
  "deck_identity_review_mapping_known_count": 3,
  "deck_identity_review_mapping_unknown_count": 11,
  "deck_identity_review_items": [
    {
      "position": 0,
      "public_model_id": "example_public_model_id",
      "normalized_candidate_id": "example_public_model_id",
      "deckseer_mapping_status": "known",
      "deckseer_id": "example_public_model_id",
      "upgraded": false,
      "upgrade_level": 0
    }
  ],
  "deck_identity_review_error": null
}
```

The example values are placeholders, not observed live output.

## Allowed Fields

The diagnostic may reveal:

- deck position or stable review index
- public deck card identity string from the same public serialization route used by `v0.2.11`
- normalized candidate ID after deterministic normalization
- Deckseer mapping status: `known`, `unknown`, `duplicate`, or `invalid`
- Deckseer ID only when the normalized candidate exactly matches one reviewed Deckseer card ID
- upgraded boolean and upgrade level
- total deck count
- unique normalized candidate count
- known and unknown mapping counts
- route/event name such as `rewards_screen_shown` or `reward_skipped`
- error type name if the diagnostic fails

## Forbidden Fields

The diagnostic must not export:

- `screen_type: "card_reward"`
- HP values
- gold values
- act, floor, or ascension values
- character ID
- relic IDs
- potion IDs
- map/path data
- selected-card identity
- selected/skipped action outcome beyond the existing clear-state event label
- card display names, localized titles, rules text, cost, rarity, type, tags, roles, priors, effects, or scoring metadata
- recommendation-ready deck objects
- any payload accepted by `recommend-export` as recommendation input
- save/profile data or run-history file contents
- OCR, screenshots, watch mode, input automation, private-field reflection, publicizer workarounds, memory/process access, or packet inspection

## Rules

- Keep the diagnostic under `exporter_status` so `recommend-export` continues to reject it.
- Reveal deck identity evidence only while a visible card reward screen is active.
- Clear deck identity review items when the reward screen closes, is skipped, or is completed.
- Normalize deterministically; do not fuzzy-match inside the exporter.
- Unknown mappings are review evidence, not runtime errors.
- Do not infer missing IDs from visible labels or localized names.
- Do not add or change Deckseer card data inside the exporter packet.
- Do not convert the diagnostic output into a `card_reward` fixture without a separate live export packet.

## Acceptance For A Future Approved Packet

Before any install-check:

1. ADR 5 is accepted.
2. Repo-local build passes with 0 warnings and 0 errors.
3. `inspect-export` accepts a status fixture containing deck identity review metadata.
4. `recommend-export --confirmed` rejects the same fixture because it is `exporter_status`.
5. Focused exporter status tests verify metadata preservation and refusal as recommendation input.
6. `git diff --check` passes.

For a live install-check after explicit approval:

1. Startup emits no deck identity review items.
2. A human-opened visible reward screen emits deck identity review items under `exporter_status`.
3. The review items explain known/unknown mapping counts without exporting HP, gold, character, relic IDs, potion IDs, or recommendation-ready state.
4. Leaving/skipping/completing the reward screen clears `deck_identity_review_items`.
5. `inspect-export` accepts the live status file.
6. `recommend-export --confirmed` rejects the live file because it is still `exporter_status`.

## Stop Conditions

Stop before implementation if:

- ADR 5 is superseded, narrowed, or no longer accepted.
- exact deck identity proof requires private fields, reflection, publicizer workarounds, memory/process access, screenshots/OCR, save/profile reads, reward generation, input automation, or packet inspection
- the diagnostic would become accepted recommendation input
- the mapping depends on localized card names or fuzzy matching
- upgraded state cannot be represented without guessing
- implementation would require card data, scoring, empirical, baseline, or recommendation behavior changes

## Repo-Local v0.2.12 Result

ADR 5 was accepted, and repo-local `v0.2.12` implements the deck ID review diagnostic under `screen_type: "exporter_status"`.

The new diagnostic writes:

- `deck_identity_review_probe`
- `deck_identity_review_last_event`
- `deck_identity_review_card_count`
- `deck_identity_review_unique_card_count`
- `deck_identity_review_mapping_known_count`
- `deck_identity_review_mapping_unknown_count`
- `deck_identity_review_items`
- `deck_identity_review_error`

Each review item contains position, public model ID, normalized candidate ID, mapping status, Deckseer ID only for exact known mappings, upgraded boolean, and upgrade level.

Repo-local verification passed:

- `dotnet build exporter_mod\DeckseerExporter\DeckseerExporter.csproj` with 0 warnings and 0 errors
- `inspect-export tests/fixtures/exporter_status_v0212_deck_identity_review_state.json`
- `recommend-export --confirmed` rejects the `v0.2.12` fixture because it is still `exporter_status`
- focused exporter tests pass

## Installed v0.2.12 Startup Result

The real STS2 mods-folder install-check was approved and `v0.2.12` installed successfully.

Startup status verification showed:

- installed manifest reports `version: "v0.2.12"`
- live export reports `exporter_version: "0.2.12"`
- live export remains `screen_type: "exporter_status"`
- `deck_identity_review_probe: "not_observed"`
- `deck_identity_review_last_event: "startup"`
- `deck_identity_review_card_count: 0`
- `deck_identity_review_unique_card_count: 0`
- `deck_identity_review_mapping_known_count: 0`
- `deck_identity_review_mapping_unknown_count: 0`
- `deck_identity_review_items: []`
- `deck_identity_review_error: null`
- `card_reward_run_state_writes_recommendation_state: false`
- `inspect-export` accepts the live status file
- `recommend-export --confirmed` rejects the live file because it is still `exporter_status`

## Installed v0.2.12 Visible Reward-Screen Result

On a human-opened visible three-card reward screen, the live file still reported `screen_type: "exporter_status"` and `exporter_version: "0.2.12"`.

Deck identity review diagnostics reported:

- `deck_identity_review_probe: "ids_revealed_for_review"`
- `deck_identity_review_last_event: "rewards_screen_shown"`
- `deck_identity_review_card_count: 14`
- `deck_identity_review_unique_card_count: 6`
- `deck_identity_review_mapping_known_count: 3`
- `deck_identity_review_mapping_unknown_count: 11`
- `deck_identity_review_error: null`

Known deck mappings:

| Public model ID | Normalized candidate | Count | Deckseer ID |
| --- | --- | ---: | --- |
| `NEUTRALIZE` | `neutralize` | 1 | `neutralize` |
| `SURVIVOR` | `survivor` | 1 | `survivor` |
| `SLICE` | `slice` | 1 | `slice` |

Unknown deck mappings:

| Public model ID | Normalized candidate | Count |
| --- | --- | ---: |
| `STRIKE_SILENT` | `strike_silent` | 5 |
| `DEFEND_SILENT` | `defend_silent` | 5 |
| `DRAMATIC_ENTRANCE` | `dramatic_entrance` | 1 |

All observed deck cards were unupgraded.

The same status file reported required run-state field presence and retained the protective runtime status:

- `card_reward_run_state_runtime_probe: "incomplete"`
- deck card ID read count 14
- deck mapping known count 3
- deck mapping unknown count 11
- `card_reward_run_state_writes_recommendation_state: false`

Visible reward identity review still mapped `CLOAK_AND_DAGGER`, `BOUNCING_FLASK`, and `INFINITE_BLADES` to reviewed Deckseer IDs.

`inspect-export` accepted the live status file. `recommend-export --confirmed` rejected it because it is still `exporter_status`.

This result is review evidence only. It does not approve card data changes, scoring changes, recommendation-ready export, or `screen_type: "card_reward"`.

## Installed v0.2.12 Clear-State Result

After the reward screen was skipped/left, the live file still reported `screen_type: "exporter_status"` and `exporter_version: "0.2.12"`.

Clear-state diagnostics reported:

- `deck_identity_review_probe: "cleared"`
- `deck_identity_review_last_event: "reward_skipped"`
- `deck_identity_review_card_count: 0`
- `deck_identity_review_unique_card_count: 0`
- `deck_identity_review_mapping_known_count: 0`
- `deck_identity_review_mapping_unknown_count: 0`
- `deck_identity_review_items: []`
- `deck_identity_review_error: null`
- `card_reward_run_state_runtime_probe: "cleared"`
- visible reward counts zero
- card identity review probe cleared with `card_identity_review_items: []`
- `card_reward_run_state_writes_recommendation_state: false`

`inspect-export` accepted the live clear-state file. `recommend-export --confirmed` rejected it because it is still `exporter_status`.

## Repo-Local v0.2.13 Alias Result

Repo-local `v0.2.13` maps the reviewed Silent starter public IDs to existing manual advisor IDs:

- `STRIKE_SILENT` -> `strike`
- `DEFEND_SILENT` -> `defend`

The alias packet is status-diagnostic mapping normalization only. It does not add card data, change scoring, change priors, change empirical rows, or export recommendation-ready state.

The expected result for the observed 14-card deck is 13 known deck cards and 1 remaining unknown deck card. `DRAMATIC_ENTRANCE` remains unknown and blocked on a separate reviewed card-data packet.

## Installed v0.2.13 Startup Result

The real STS2 mods-folder install-check was approved and `v0.2.13` installed successfully after closing STS2 to release the previously locked exporter DLL.

Startup verification passed:

- installed manifest reports `version: "v0.2.13"`
- live export reports `exporter_version: "0.2.13"`
- live export remains `screen_type: "exporter_status"`
- `deck_identity_review_probe: "not_observed"`
- `deck_identity_review_items: []`
- `card_reward_run_state_runtime_probe: "not_observed"`
- `card_reward_run_state_writes_recommendation_state: false`
- `inspect-export` accepts the live status file
- `recommend-export --confirmed` rejects the live file because it is still `exporter_status`

## Installed v0.2.13 Visible Reward-Screen Result

On a human-opened visible three-card reward screen, the live file still reported `screen_type: "exporter_status"` and `exporter_version: "0.2.13"`.

The alias decision behaved as expected:

- `deck_identity_review_mapping_known_count: 13`
- `deck_identity_review_mapping_unknown_count: 1`
- `STRIKE_SILENT` / `strike_silent` -> `strike`, count 5
- `DEFEND_SILENT` / `defend_silent` -> `defend`, count 5
- remaining unknown: `DRAMATIC_ENTRANCE` / `dramatic_entrance`, count 1

The runtime presence diagnostic remained incomplete because of that one unknown deck mapping and continued to report `card_reward_run_state_writes_recommendation_state: false`.

Visible reward identity review still mapped `CLOAK_AND_DAGGER`, `BOUNCING_FLASK`, and `INFINITE_BLADES` to reviewed Deckseer IDs. `inspect-export` accepted the live status file, and `recommend-export --confirmed` rejected it because it is still `exporter_status`.

## Installed v0.2.14 Clear-State Result

After the reward screen was skipped/left, installed `v0.2.14` cleared the deck ID review diagnostic while staying status-only:

- live export remained `screen_type: "exporter_status"`
- live export reported `exporter_version: "0.2.14"`
- `deck_identity_review_probe: "cleared"`
- `deck_identity_review_card_count: 0`
- `deck_identity_review_mapping_known_count: 0`
- `deck_identity_review_mapping_unknown_count: 0`
- `deck_identity_review_items: []`
- `card_reward_run_state_runtime_probe: "cleared"`
- `visible_card_reward_option_count: 0`
- `card_identity_review_probe: "cleared"`
- `card_identity_review_items: []`
- `card_reward_run_state_writes_recommendation_state: false`

`inspect-export` accepted the live clear-state file, and `recommend-export --confirmed` rejected it because it is still `exporter_status`.

## Installed v0.2.13 Clear-State Result

After the reward screen was skipped/left, the live file still reported `screen_type: "exporter_status"` and `exporter_version: "0.2.13"`.

The clear-state behavior stayed protective:

- `card_reward_run_state_runtime_probe: "cleared"`
- run-state booleans false and counts zero
- `deck_identity_review_probe: "cleared"`
- `deck_identity_review_items: []`
- visible reward counts zero
- `card_identity_review_probe: "cleared"`
- `card_identity_review_items: []`
- `card_reward_run_state_writes_recommendation_state: false`

`inspect-export` accepted the live clear-state file, and `recommend-export --confirmed` rejected it because it is still `exporter_status`.

## Repo-Local v0.2.14 Data Result

`docs/EXPORTER_CARD_REWARD_DRAMATIC_ENTRANCE_DATA_REVIEW.md` adds reviewed seed metadata for `dramatic_entrance` from local STS2 `v0.106.1` evidence and an external card-page cross-check.

Repo-local `v0.2.14` adds `dramatic_entrance` to the exporter status-diagnostic mapping snapshot. This should turn the previously observed 14-card deck from 13 known / 1 unknown to 14 known / 0 unknown after a separately approved live install-check.

The data packet keeps `quality_prior: 0.0`; it does not change scoring logic, empirical rows, accuracy baselines, or recommendation behavior.

## Installed v0.2.14 Startup Result

The real STS2 mods-folder install-check was approved and `v0.2.14` installed successfully.

Startup verification passed:

- installed manifest reports `version: "v0.2.14"`
- live export reports `exporter_version: "0.2.14"`
- live export remains `screen_type: "exporter_status"`
- `deck_identity_review_probe: "not_observed"`
- `deck_identity_review_items: []`
- `card_reward_run_state_runtime_probe: "not_observed"`
- `card_reward_run_state_writes_recommendation_state: false`
- `inspect-export` accepts the live status file
- `recommend-export --confirmed` rejects the live file because it is still `exporter_status`

## Installed v0.2.14 Visible Reward-Screen Result

On a human-opened visible three-card reward screen, installed `v0.2.14` stayed inside the deck ID review boundary:

- live export remained `screen_type: "exporter_status"`
- live export reported `exporter_version: "0.2.14"`
- `deck_identity_review_probe: "ids_revealed_for_review"`
- `deck_identity_review_card_count: 14`
- `deck_identity_review_unique_card_count: 6`
- `deck_identity_review_mapping_known_count: 14`
- `deck_identity_review_mapping_unknown_count: 0`
- `DRAMATIC_ENTRANCE` mapped to `dramatic_entrance`
- `card_reward_run_state_runtime_probe: "run_state_seen"`
- deck card ID read count 14
- deck mapping known count 14
- deck mapping unknown count 0
- `card_reward_run_state_writes_recommendation_state: false`

Visible reward identity review still mapped `CLOAK_AND_DAGGER`, `BOUNCING_FLASK`, and `INFINITE_BLADES` to reviewed Deckseer IDs. `inspect-export` accepted the live status file, and `recommend-export --confirmed` rejected it because it is still `exporter_status`.

## Next Gate

The installed `v0.2.14` deck ID review proof is complete for startup, visible reward-screen, and clear-state behavior. `docs/EXPORTER_CARD_REWARD_LIVE_EXPORT_DESIGN.md` now records the refusal-first readiness contract. The next safe packet is a repo-local candidate/refusal diagnostic under `exporter_status`, or a separately approved live `card_reward` export packet.
