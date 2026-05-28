# Deckseer Exporter Card Reward ID Reveal Contract

Status: `installed_visible_reward_and_clear_verified`

Prepared on 2026-05-24 after the status-only `v0.2.8` ID-shape diagnostic, mapping review handoff, reviewed `infinite_blades` data follow-up, and repo-local mapping snapshot drift guard.

## Scope

This document defines the smallest diagnostic that can reveal enough live identity evidence to prove exact STS2-to-Deckseer card mapping before `screen_type: "card_reward"` export.

ADR 3 approved the bounded diagnostic, and the user explicitly approved installing `v0.2.9` into the real STS2 mods folder for an install-check/live status diagnostic review. This document does not approve live card reward export, recommendation-ready state export, watch mode, OCR, input automation, private access, scoring changes, or adapter behavior changes.

## Current Evidence

The status-only diagnostic proves:

- a visible reward screen can expose identity-shaped public card facts
- readable/direct/serialized counts can match the visible option count
- the repo-local mapping snapshot can count known and unknown mappings
- the exporter can avoid writing raw IDs, Deckseer IDs, names, selected-card identity, or run state

The installed `v0.2.9` diagnostic now proves the exact public STS2 model ID behind a visible choice and clears that review list after the reward screen closes, while still keeping the payload outside recommendation input. That is review evidence only; it does not approve `screen_type: "card_reward"` export or recommendation-ready live state.

## Proposed Diagnostic Shape

Repo-local `v0.2.9` adds a temporary `exporter_status` diagnostic mode that writes a bounded review list under `export_metadata.diagnostics`.

The file should remain:

```json
{
  "screen_type": "exporter_status"
}
```

The diagnostic may include only visible reward identity evidence:

```json
{
  "card_identity_review_probe": "ids_revealed_for_review",
  "card_identity_review_last_event": "rewards_screen_shown",
  "card_identity_review_option_count": 3,
  "card_identity_review_items": [
    {
      "position": 0,
      "public_model_id": "example_public_model_id",
      "normalized_candidate_id": "example_public_model_id",
      "deckseer_mapping_status": "known",
      "deckseer_id": "example_public_model_id",
      "upgraded": false,
      "upgrade_level": 0,
      "serialized_id_matches_direct_id": true
    }
  ]
}
```

The example keys are contract placeholders, not observed live values.

## Allowed Fields

The diagnostic may reveal:

- visible option position
- public `CardModel.Id` string representation
- normalized candidate ID after deterministic normalization
- Deckseer mapping status: `known`, `unknown`, `duplicate`, or `invalid`
- Deckseer ID only when the normalized candidate exactly matches a reviewed Deckseer card ID
- upgraded boolean and upgrade level
- whether `ToSerializable().Id` matches the direct public model ID
- route/event name such as `rewards_screen_shown` or `choose_card_screen_shown`

## Forbidden Fields

The diagnostic must still not export:

- selected-card identity
- skipped/selected action outcome
- deck contents
- HP, gold, act, floor, ascension, relics, potions, map, save/profile data, or run history
- card display names, localized titles, rules text, costs, rarity, type, tags, roles, priors, or effects
- any payload accepted by `recommend-export` as recommendation input
- `screen_type: "card_reward"`

## Rules

- Reveal identity evidence only for the currently visible reward choices observed through already-approved public screen routes.
- Keep the diagnostic under `exporter_status` so `recommend-export` continues to reject it.
- Require explicit user approval again before moving beyond `exporter_status` diagnostics or using revealed IDs as recommendation input.
- Keep the output user-visible and inspectable.
- Normalize deterministically; do not fuzzy-match inside the exporter.
- Unknown mappings remain review evidence, not runtime errors.
- If any identity field is missing, report a caveat and avoid guessing.
- Clear the review list when the public reward screen closes.

## Acceptance For A Future Approved Packet

Before using any revealed IDs for recommendation-ready export:

1. The diagnostic build compiles repo-local with 0 warnings and 0 errors.
2. `inspect-export` accepts the file as `exporter_status`.
3. `recommend-export` rejects the file because it is still status metadata.
4. A visible reward screen produces one review item per visible option.
5. Closing the screen clears the review list.
6. The reviewed public model IDs map deterministically to Deckseer IDs or explicit unknown caveats.
7. No selected-card identity, deck, HP, gold, relics, potions, save/profile data, OCR, watch mode, input automation, private access, or recommendation-ready run state is exported.

## Stop Conditions

Stop before implementation if:

- exact identity proof requires private fields, reflection, publicizer workarounds, memory/process access, screenshots/OCR, save/profile reads, reward generation, input automation, or packet inspection
- user confirmation is not available for a live diagnostic step
- the diagnostic would become accepted recommendation input
- the mapping depends on localized card names or fuzzy matching
- upgrade state cannot be represented without guessing

## Next Approval Gate

At the time of the `v0.2.9` visible-screen and clear-state checks, the next blocked step was a separate approval gate before any move from `exporter_status` diagnostics to `screen_type: "card_reward"` or any use of live IDs as recommendation input.

Follow-up, 2026-05-25: that approval gate is now superseded by accepted ADR 4 and the installed live proof sequence through `v0.4.7`. The ID reveal contract remains useful as the historical mapping-review boundary, but live `card_reward` export is no longer blocked on this step when the later freshness, mapping, confirmation, and clear-state gates pass.

## Repo-Local Implementation Result

Implemented repo-local on 2026-05-24 as exporter source `v0.2.9`; after explicit approval, the build was installed into the real STS2 mods folder and verified at startup, on a visible card reward screen, and after leaving the reward screen.

The exporter still writes `screen_type: "exporter_status"`. When a visible reward screen is observed through the approved public routes, diagnostics may include:

- `card_identity_review_probe`
- `card_identity_review_last_event`
- `card_identity_review_option_count`
- `card_identity_review_items`
- `card_identity_review_error`

Each review item includes visible option position, public model ID, normalized candidate ID, exact Deckseer mapping status, exact Deckseer ID only for known mappings, upgrade state, and whether the serialized ID matches the direct public model ID.

Verification:

- repo-local `dotnet build exporter_mod\DeckseerExporter\DeckseerExporter.csproj` passed with 0 warnings and 0 errors
- focused exporter status tests passed for the `v0.2.9` fixture
- real install-check build passed with 0 warnings and 0 errors
- installed manifest reports `version: "v0.2.9"`
- launched STS2 emitted valid `screen_type: "exporter_status"` with `exporter_version: "0.2.9"`
- startup status reported `card_identity_review_probe: "not_observed"` and an empty `card_identity_review_items` list, so no live IDs were exported during startup verification
- visible card reward status reported `card_identity_review_probe: "ids_revealed_for_review"` and three review items
- visible public model IDs were `CLOAK_AND_DAGGER`, `BOUNCING_FLASK`, and `INFINITE_BLADES`
- normalized candidates mapped to reviewed Deckseer IDs `cloak_and_dagger`, `bouncing_flask`, and `infinite_blades`
- all three visible cards were unupgraded and `serialized_id_matches_direct_id: true`
- after leaving/skipping the reward screen, status reported `card_identity_review_probe: "cleared"`, `card_identity_review_option_count: 0`, and `card_identity_review_items: []`
- `recommend-export --confirmed` rejected the live file because it is still `exporter_status`
