# Deckseer Exporter Card Reward Run-State Symbol Review

Status: `runtime_probe_live_review_complete_deck_mapping_needed`

Prepared on 2026-05-24 after installed `v0.2.10` startup verification. Updated after repo-local `v0.2.11` runtime presence diagnostic implementation, installed startup verification, installed visible reward-screen verification, and clear-state verification.

## Question

Are the public run-state symbols verified by installed `v0.2.10` sufficient to implement a minimal human-confirmed live `screen_type: "card_reward"` export?

## Short Answer

No. They are necessary, but not sufficient.

Installed `v0.2.10` proves normal exporter source can compile references to the public and serializable run-state members needed by the future `card_reward` schema. It does not prove those members can be read safely at runtime during an active visible reward screen, that they refer to the correct current player, or that their IDs map cleanly to Deckseer IDs.

The next safe packet was another status-only diagnostic: a public run-state runtime presence probe. Repo-local `v0.2.11` now implements that probe and still writes only `screen_type: "exporter_status"`.

## Evidence Accepted

`v0.2.10` verifies compile visibility for:

- run manager/run state access: `RunManager.Instance`, `RunManager.IsInProgress`, `RunManager.ToSave`, `IRunState.ActFloor`, `IRunState.TotalFloor`, `IRunState.AscensionLevel`, `RunState.Players`
- serializable run fields: `SerializableRun.Players`, `SerializableRun.Ascension`, `SerializableRun.FloorReached`
- player fields: `SerializablePlayer.CharacterId`, `CurrentHp`, `MaxHp`, `Gold`, `Deck`, `Relics`, `Potions`
- item IDs: `SerializableCard.Id`, `SerializableCard.CurrentUpgradeLevel`, `SerializableRelic.Id`, `SerializablePotion.Id`

The installed startup check also proves:

- the installed manifest is `v0.2.10`
- the live file remains `screen_type: "exporter_status"`
- `card_reward_live_export_writes_recommendation_state` is `false`
- `recommend-export --confirmed` rejects the live file as `exporter_status`

## Gaps Before Live Export

The compile probe does not prove:

- `RunManager.Instance` is populated at the same time as the visible reward screen observation.
- `RunManager.IsInProgress` is true during the relevant screen.
- `RunManager.ToSave()` is side-effect free enough for this use, or whether a direct `IRunState` route should be preferred.
- `SerializableRun.Players` reliably contains exactly one player for Deckseer's current single-player assumption.
- `RewardsSet.Player` and the chosen serialized player point to the same visible player.
- `CharacterId`, card IDs, relic IDs, and potion IDs normalize to reviewed Deckseer IDs.
- deck counts and upgrade state can be represented in the existing `deck` schema without guessing.
- HP, gold, act, floor, and ascension values are current at the moment the visible reward screen is open.
- map/path context can be represented only as explicit unknown/default caveats.
- the exporter clears away from recommendation-ready state after screen close without stale run-state data.

## Required Runtime Proof

Before any `screen_type: "card_reward"` implementation, `v0.2.11` adds a status-only runtime presence diagnostic that reports only readiness facts and counts, not live run-state values.

Allowed diagnostics:

- `card_reward_run_state_runtime_probe`: `not_observed`, `run_state_seen`, `incomplete`, `probe_error`, or `cleared`
- whether a run is in progress
- whether a serializable run object is available
- player count
- whether a single player is available
- whether character, act, floor, ascension, gold, HP, deck, relic, and potion fields are present
- deck/relic/potion counts
- normalized mapping known/unknown counts for deck, relic, and potion IDs, without exporting the IDs themselves
- whether a visible reward player object is present
- a boolean that recommendation-ready state is not written

Forbidden diagnostics:

- deck card IDs
- relic IDs
- potion IDs
- HP values
- gold values
- act/floor/ascension values
- character ID
- selected-card identity or selected/skipped outcome
- `screen_type: "card_reward"`

## Acceptance Criteria For v0.2.11

- Repo-local build passes with 0 warnings and 0 errors. Done.
- `inspect-export` accepts a `v0.2.11` status fixture. Done.
- `recommend-export --confirmed` rejects the `v0.2.11` status fixture. Done.
- Startup status reports no recommendation-ready state. Done.
- On a human-opened visible reward screen, status reports whether required run-state fields are present. Done.
- Leaving the reward screen clears the runtime readiness diagnostic. Done.
- No live deck, HP, gold, relic, potion, save/profile, OCR, watch mode, input automation, or recommendation-ready run state is exported.

## Repo-Local v0.2.11 Result

Repo-local `v0.2.11` adds `CardRewardRunStateRuntimeProbe`, exposed only through status diagnostics:

- `card_reward_run_state_runtime_probe`
- run-state availability booleans
- player count and single-player availability
- required-field presence booleans for character, act, floor, ascension, gold, HP, deck, relics, and potions
- deck, relic, and potion counts
- deck card ID read, known-mapping, and unknown-mapping counts
- `card_reward_run_state_visible_reward_player_present`
- `card_reward_run_state_writes_recommendation_state: false`

The repo-local fixture remains `screen_type: "exporter_status"` and does not include live character IDs, HP values, gold values, act/floor/ascension values, deck IDs, relic IDs, potion IDs, selected-card identity, or selected/skipped outcome.

## Installed v0.2.11 Startup Result

The real STS2 mods-folder install-check was approved and `v0.2.11` installed successfully.

Startup status verification showed:

- installed manifest reports `version: "v0.2.11"`
- live export reports `exporter_version: "0.2.11"`
- live export remains `screen_type: "exporter_status"`
- `card_reward_run_state_runtime_probe: "not_observed"`
- `card_reward_run_state_runtime_last_event: "startup"`
- run-state booleans are false and counts are zero at startup
- `card_reward_run_state_writes_recommendation_state: false`
- visible reward/card identity diagnostics are not observed and review items are empty
- `inspect-export` accepts the live status file
- `recommend-export --confirmed` rejects the live file because it is still `exporter_status`

## Installed v0.2.11 Visible Reward-Screen Result

On a human-opened visible three-card reward screen, the live file still reported `screen_type: "exporter_status"` and `exporter_version: "0.2.11"`.

Runtime presence diagnostics reported:

- `card_reward_run_state_runtime_probe: "incomplete"`
- `card_reward_run_state_runtime_last_event: "rewards_screen_shown"`
- run in progress, run state available, serializable run available, one player, and visible reward player present
- character, act, floor, ascension, gold, HP, deck, relics, and potions present
- deck count 14, deck card ID read count 14
- deck mapping known count 3, unknown count 11
- relic count 2, potion count 0
- `card_reward_run_state_writes_recommendation_state: false`
- no runtime probe error

The `incomplete` status is expected and protective because the deck mapping unknown count is nonzero. The exporter did not write character ID, HP values, gold value, act/floor/ascension values, deck IDs, relic IDs, potion IDs, selected-card identity, selected/skipped outcome, or `screen_type: "card_reward"`.

Visible reward identity review diagnostics remained under the accepted ADR 3 `exporter_status` boundary. The observed reward IDs mapped to reviewed Deckseer IDs `cloak_and_dagger`, `bouncing_flask`, and `infinite_blades`.

`inspect-export` accepted the live status file. `recommend-export --confirmed` rejected it because it is still `exporter_status`.

## Installed v0.2.11 Clear-State Result

After the reward screen was skipped/left, the live file still reported `screen_type: "exporter_status"` and `exporter_version: "0.2.11"`.

Clear-state diagnostics reported:

- `card_reward_run_state_runtime_probe: "cleared"`
- `card_reward_run_state_runtime_last_event: "reward_skipped"`
- run-state booleans false and counts zero
- `card_reward_run_state_visible_reward_player_present: false`
- `card_reward_run_state_writes_recommendation_state: false`
- `visible_reward_probe_status: "reward_screen_completed"`
- visible reward counts zero
- card identity runtime probe cleared with all identity counts zero
- card identity review probe cleared with `card_identity_review_items: []`
- `screen_observation_error: null`

`inspect-export` accepted the live clear-state file. `recommend-export --confirmed` rejected it because it is still `exporter_status`.

## Remaining Blocker

Installed `v0.2.11` proves the required run-state fields are present at runtime and stale status clears after the reward screen closes. It also proves the first visible test run's deck mapping is incomplete by count only: 3 known and 11 unknown deck card IDs.

`docs/EXPORTER_CARD_REWARD_DECK_MAPPING_GAP_REVIEW.md` records this 3-known/11-unknown deck result as review evidence only.

ADR 5 accepts a status-only deck ID review diagnostic for resolving the unknown deck mappings, and installed `v0.2.12` implements it. Startup, visible reward-screen, and clear-state verification passed. Installed `v0.2.13` resolves the reviewed Silent starter aliases. Repo-local `v0.2.14` adds reviewed seed data for `dramatic_entrance` and includes it in the status-diagnostic mapping snapshot.

Do not write `screen_type: "card_reward"` until the deck mapping gap is reviewed and the live export packet has an explicit separate approval.

## Decision

The verified public symbols are not sufficient for live `card_reward` export yet.

Proceed next only after deciding whether to install-check repo-local `v0.2.14`, use a manual deck-list review, or design live export refusal behavior for unresolved relic/potion boundaries. Do not export recommendation-ready live state or change scoring as part of the completed runtime probe packet.
