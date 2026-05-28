# Deckseer Exporter Card Reward Live Export Design

Status: `installed_v047_mixed_reward_card_reward_live_proof_passed`

Prepared on 2026-05-24 after installed `v0.2.9` visible-screen and clear-state verification. ADR 4 is accepted, installed `v0.2.10` implements the status-only public run-state compile probe, installed `v0.2.11` implements the status-only runtime presence diagnostic, and installed `v0.2.14` completes the observed deck mapping proof while still exporting only status diagnostics. Updated on 2026-05-25 after installed `v0.4.7` live-proved a fully mapped mixed reward `card_reward` export and post-selection downgrade.

## Goal

Define the smallest safe move from status-only diagnostics to live `screen_type: "card_reward"` export.

The live export should reduce manual transcription while preserving Deckseer's human-confirmed recommendation boundary.

## Non-Goals

This design and the installed status-only probes through `v0.2.14` do not implement live export and do not approve:

- watch mode
- OCR or screenshots
- input automation
- memory/process access
- packet inspection
- save/profile modification
- recommendation scoring changes
- card prior, empirical, accuracy baseline, or data changes
- relic reward live export

## Current Proof

Installed `v0.2.9` proves:

- `NRewardsScreen.ShowScreen(RewardsSet, ...)` can identify the active visible card reward screen.
- The visible reward contained three card choices.
- Public IDs were `CLOAK_AND_DAGGER`, `BOUNCING_FLASK`, and `INFINITE_BLADES`.
- Normalized IDs mapped to reviewed Deckseer IDs `cloak_and_dagger`, `bouncing_flask`, and `infinite_blades`.
- Direct and serialized public IDs matched.
- The review list cleared after reward skip.
- `recommend-export --confirmed` rejected the live file because it remained `exporter_status`.

## Current Installed State

Installed `v0.4.7` is the current live-proven card reward exporter:

- startup writes valid `screen_type: "exporter_status"`
- mixed reward screens still refuse before non-card rewards are collected
- after the observed 15-gold pickup, the Envenom / Predator / Memento Mori reward wrote confirmed `screen_type: "card_reward"`
- reward, deck, owned relic, and potion mapping gates were all clean
- `recommend-export` rejected the unconfirmed file and ran only with `--confirmed`
- after card reward selection closed, the exporter downgraded to `screen_type: "exporter_status"` and stale confirmed recommendation was rejected

Before scenario intake, the observed recommendation ranked Skip, Predator, Memento Mori, then Envenom. That ordering was treated as review evidence only until the separate accepted accuracy packet added `silent_v047_envenom_attack_payoff_guard`.

## Proposed `card_reward` Shape

The first live export should use the existing importer schema:

```json
{
  "game": "slay_the_spire_2",
  "screen_type": "card_reward",
  "character": "silent",
  "act": 1,
  "floor": 7,
  "ascension": 0,
  "gold": 123,
  "hp": {
    "current": 52,
    "max": 80
  },
  "deck": [
    {
      "id": "strike",
      "upgraded": false,
      "count": 4
    }
  ],
  "relics": [],
  "potions": [],
  "card_reward": [
    "cloak_and_dagger",
    "bouncing_flask",
    "infinite_blades"
  ],
  "run_context": {
    "next_node_type": "unknown",
    "path_pressure": "unknown",
    "notes": [
      "Live exporter did not infer map/path context."
    ]
  },
  "export_metadata": {
    "source": "deckseer_exporter_mod",
    "exporter_version": "0.3.0",
    "game_build": null,
    "game_patch": null,
    "exported_at": "2026-05-24T00:00:00Z",
    "requires_user_confirmation": true,
    "confidence": "medium",
    "caveats": [
      "User must confirm the visible card reward, deck, HP, gold, relics, and potions before using this state."
    ]
  }
}
```

The example values are placeholders, not observed live output.

## Allowed Sources

The implementation may read:

- visible card reward choices from the already-approved public screen observation routes
- public `CardModel.Id`, `IsUpgraded`, `CurrentUpgradeLevel`, and `ToSerializable()` identity surfaces for visible choices
- public run-state or serialization APIs that the compile probe already verifies, if they provide required fields without private access or mutation

The implementation may write:

- one local JSON file in the existing Deckseer export directory
- `screen_type: "card_reward"` only while a visible card reward is actively observed and all required fields are present

## Required Refusals

The exporter should refuse to emit `screen_type: "card_reward"` and fall back to `exporter_status` with caveats if:

- no visible card reward screen is active
- any visible card reward ID is unknown, duplicate, invalid, or missing
- any required run-state field cannot be read without guessing
- deck cards cannot be normalized to reviewed Deckseer IDs
- HP, max HP, character, act, floor, relics, or potions are unavailable
- the reward screen has closed, been skipped, or already completed
- public APIs would require private fields, reflection workarounds, memory/process access, OCR, save/profile reads, input automation, or reward generation

## Refusal-First Readiness Contract

The first live export implementation should compute every field, validate the full payload, and then choose one of two outputs:

- `screen_type: "card_reward"` when every gate below passes.
- `screen_type: "exporter_status"` with refusal diagnostics when any gate fails.

Partial `card_reward` output is not allowed. A payload missing HP, gold, deck, relics, potions, character, act, floor, or visible reward choices must remain status-only instead of relying on scorer caveats.

| Gate | Current evidence | `card_reward` write condition | Refusal behavior |
| --- | --- | --- | --- |
| Active visible reward screen | Installed `v0.2.9` through `v0.2.14` observe and clear the public reward route. | Public reward route is active and current. | Fall back to `exporter_status`; clear recommendation-ready fields. |
| Visible reward card IDs | Installed `v0.2.9` and later map the observed visible choices. | Every visible choice maps to a reviewed Deckseer ID, with no invalid or duplicate IDs. | Report unknown/invalid/duplicate count under diagnostics only. |
| Deck card IDs | Installed `v0.2.14` maps the observed 14-card deck with 14 known / 0 unknown. | Every deck card maps to a reviewed Deckseer ID, preserving count and upgrade state. | Report deck mapping counts and stay `exporter_status`. |
| Character, act, floor, ascension, gold, HP | `v0.2.10` compiles public symbols and `v0.2.11` observes required-field presence by boolean only. | Values are read from public run-state APIs, are internally valid, and can be serialized into the existing importer shape. | Report the missing or invalid field names without exporting their live values. |
| Relics | `v0.2.11` and later report relic count only; no relic ID mapping proof exists yet. | Every current relic ID is read from public APIs and maps to Deckseer relic IDs, or the current relic list is proven empty. | Refuse `card_reward`; report relic count and mapping status only. |
| Potions | `v0.2.11` and later report potion count only; observed count was 0 in the tested run. | Potion IDs are read and mapped when count is nonzero, or count is zero and exports as an empty list. | Refuse `card_reward` when count is nonzero and IDs cannot be read or mapped. |
| Run context | No map/path context is exported. | Unknown/default path context is allowed only with an explicit caveat. | Do not refuse solely for unknown path context. |
| Human confirmation | Existing importer supports `requires_user_confirmation`. | `export_metadata.requires_user_confirmation` is always `true`. | Refuse implementation if this cannot be guaranteed. |
| Stale-state clearing | Installed `v0.2.12` through `v0.2.14` clear status diagnostics after reward skip/leave. | The exporter downgrades away from `card_reward` immediately when the reward screen closes or changes. | Write only `exporter_status` after close, skip, completion, or stale-screen detection. |

Recommended refusal diagnostic keys for the next implementation packet:

- `card_reward_live_export_candidate: "ready" | "refused"`
- `card_reward_live_export_refusal_reasons`: list of short stable reason codes
- `card_reward_live_export_missing_fields`: list of required schema fields not safely readable
- `card_reward_live_export_unmapped_reward_count`
- `card_reward_live_export_unmapped_deck_count`
- `card_reward_live_export_unmapped_relic_count`
- `card_reward_live_export_unmapped_potion_count`
- `card_reward_live_export_writes_recommendation_state`: `false` for all refusal/status paths

Reason codes should stay stable enough for tests and handoffs, for example:

- `no_visible_reward`
- `unknown_reward_card`
- `unknown_deck_card`
- `missing_required_run_state_field`
- `unmapped_relic`
- `unmapped_potion`
- `stale_reward_screen`
- `unsupported_public_api_surface`
- `unsupported_upgraded_reward_card`
- `mixed_reward_screen_state_may_change`

## Required Caveats

Every live `card_reward` export must include:

- `requires_user_confirmation: true`
- a caveat telling the user to run `inspect-export` first
- a caveat telling the user to confirm visible reward choices and run state before `recommend-export --confirmed`
- a caveat when map/path context is unknown or defaulted

## Lifecycle

When a visible reward screen is active and complete run-state fields are available:

- write `screen_type: "card_reward"`
- include only current visible reward choices
- include no selected-card identity
- include no selected/skipped action outcome

When the reward screen closes, is skipped, or no longer has a valid visible reward:

- stop writing `screen_type: "card_reward"`
- write `screen_type: "exporter_status"` or a non-recommendation status payload
- clear visible reward identity diagnostics

## Verification Plan

Repo-local implementation must pass:

```bash
dotnet build exporter_mod\DeckseerExporter\DeckseerExporter.csproj "/p:Sts2Path=D:/Games/Steam/steamapps/common/Slay the Spire 2" "/p:ModsPath=D:/Codex/Deckseer/exporter_mod/local_mods/" "/p:GodotPath=D:/Codex/Godot/Godot_v4.5.1-stable_mono_win64.exe"
python -m deckseer.cli inspect-export tests/fixtures/exporter_card_reward_state.json
python -m deckseer.cli recommend-export tests/fixtures/exporter_card_reward_state.json --confirmed --format text
python -m deckseer.cli qa --check-recommendation-baseline --check-accuracy --check-empirical-triage
python -m pytest tests/test_exporter_state.py tests/test_exporter_mapping_snapshot.py -q
git diff --check
```

Live install-check must be separate and explicitly approved. The live check order should be:

1. Install `v0.3.0` only after approval.
2. Launch STS2 and verify startup still emits non-recommendation status.
3. On a human-opened visible card reward screen, run `inspect-export`.
4. Verify the summary matches the visible state before any recommendation.
5. Run `recommend-export` without `--confirmed` and confirm it rejects the file.
6. Only after human visual review, run `recommend-export --confirmed`.
7. Leave the reward screen and verify the file no longer exports recommendation-ready card reward state.

## Repo-Local v0.3.0 Live Export Result

Repo-local `v0.3.0` implements the first guarded `screen_type: "card_reward"` writer. It builds the live payload only when the existing refusal-first candidate is `ready`; otherwise it preserves the `screen_type: "exporter_status"` diagnostic fallback.

The live payload exports only Deckseer IDs and existing scalar run-state fields:

- character, act, floor, ascension, gold, HP
- grouped deck IDs with upgrade state and counts
- current relic and potion Deckseer IDs
- visible card reward Deckseer IDs
- `run_context` with unknown/defaulted path context
- `export_metadata.requires_user_confirmation: true`

It does not export raw STS2 public IDs, card names, selected-card identity, selected/skipped outcome, save/profile data, OCR, input automation, watch mode, or private data. Upgraded visible reward cards refuse with `unsupported_upgraded_reward_card` until the importer has an explicit reward-upgrade contract.

Repo-local verification passed:

- exporter mod build: 0 warnings / 0 errors
- `inspect-export tests/fixtures/exporter_card_reward_live_v030_state.json`
- `recommend-export tests/fixtures/exporter_card_reward_live_v030_state.json` rejects without `--confirmed`
- `recommend-export tests/fixtures/exporter_card_reward_live_v030_state.json --confirmed --format text`
- `pytest tests/test_exporter_state.py -q`

This packet does not install `v0.3.0` into the real STS2 mods folder. Installed `v0.2.17` remains the last live-proved package until a separate install-check is approved.

## Installed v0.3.0 Mixed Reward Failure

The approved `v0.3.0` install-check proved startup status fallback, then produced a live `screen_type: "card_reward"` on a visible three-card reward screen:

- visible choices: `cloak_and_dagger`, `bouncing_flask`, `infinite_blades`
- exported HP: 70/70
- exported floor: 3
- exported relics: `ring_of_the_snake`, `lead_paperweight`
- exported gold: 114
- exported potions: []

Human visual confirmation rejected the payload because the visible UI showed 127 gold and a potion in the belt. This is a failed live proof. `recommend-export --confirmed` was not run.

The likely cause is stale scalar state from a mixed reward flow: the exporter wrote on the initial reward screen before later gold/potion reward collection changed the visible run state. Because the exporter does not continuously refresh state or observe a post-reward-collection card-choice event that carries the full current run state, `v0.3.0` is not safe for mixed reward screens.

## Installed v0.3.1 Mixed Reward Refusal

Installed `v0.3.1` adds a conservative refusal gate:

- if the observed reward set contains non-card rewards, live `card_reward` export refuses with `mixed_reward_screen_state_may_change`
- the payload builder has the same backstop and falls back to `exporter_status`

This preserves the human-confirmation-first boundary after the failed `v0.3.0` proof. A future implementation can revisit mixed reward export only after it can refresh HP/gold/potions/relics at the exact visible card-choice moment.

Startup verification passed:

- installed manifest reports `version: "v0.3.1"`
- live export reports `exporter_version: "0.3.1"`
- live export remains `screen_type: "exporter_status"`
- `card_reward_live_export_candidate: "refused"`
- refusal reasons: `no_visible_reward`, `missing_required_run_state_field`
- `inspect-export` accepts the live status file
- `recommend-export --confirmed` rejects the live file because it is `exporter_status`

Visible mixed reward-screen verification passed:

- live export remained `screen_type: "exporter_status"`
- `card_reward_live_export_candidate: "refused"`
- `card_reward_live_export_refusal_reasons`: `mixed_reward_screen_state_may_change`
- missing required fields were empty
- unmapped reward, deck, relic, and potion counts were zero
- visible reward count was 3
- visible card reward count was 1
- visible card reward option count was 3
- runtime run-state probe reported `run_state_seen`
- `recommend-export --confirmed` rejected the live file because it was `exporter_status`

Clear-state verification passed:

- live export remained `screen_type: "exporter_status"`
- `card_reward_live_export_refusal_reasons`: `stale_reward_screen`, `missing_required_run_state_field`
- visible reward counts cleared to zero
- run-state runtime probe cleared
- deck identity review probe cleared
- card identity review probe cleared
- relic/potion identity review probe cleared
- `recommend-export --confirmed` rejected the live file because it was `exporter_status`

## Repo-Local v0.3.2 Post-Pickup Freshness Probe

Repo-local `v0.3.2` adds a status-only freshness probe for `NChooseACardSelectionScreen.ShowScreen(...)`. This route is important because mixed reward flows can show the card-choice screen after the user has already collected gold, relic, or potion rewards.

The probe does not export live run-state values. It reads the public serializable run at card-choice screen time and reports only booleans and counts under status diagnostics:

- `card_reward_run_state_runtime_probe: "serializable_run_seen"` when a fresh serializable run is available without an `IRunState` argument
- field-presence booleans for character, act, floor, ascension, gold, HP, deck, relics, and potions
- deck card count and mapping known/unknown counts
- relic and potion counts
- `card_reward_run_state_writes_recommendation_state: false`

Because the card-choice screen route still has no current `RewardsSet.Player` and no `IRunState` argument, the live export candidate remains refused with `no_visible_reward` and `missing_required_run_state_field`. The status fixture verifies that no `character`, `gold`, `hp`, `deck`, `relics`, `potions`, or recommendation-ready `card_reward` fields appear in the top-level payload, and no raw scalar values or potion IDs are added to diagnostics.

Repo-local verification passed:

- exporter mod build: 0 warnings / 0 errors
- `inspect-export tests/fixtures/exporter_status_v032_post_pickup_freshness_state.json`
- `recommend-export --confirmed` rejects the fixture because it is `exporter_status`
- `pytest tests/test_exporter_state.py tests/test_exporter_mapping_snapshot.py -q`

Installed `v0.3.2` startup verification passed, but the mixed reward screen did not trigger `NChooseACardSelectionScreen.ShowScreen(...)` after gold and potion rewards were collected. The export remained on the original `rewards_screen_shown` event, so `v0.3.2` stayed safe but did not prove post-pickup freshness for the observed mixed reward flow.

## Installed v0.3.3 Reward-Collected Freshness Probe

Installed `v0.3.3` adds a status-only refresh on the public `NRewardsScreen.RewardCollectedFrom(Control)` method. This is the first route targeted at the exact moment non-card rewards are clicked on a mixed reward screen.

When a reward is collected, the exporter:

- keeps the existing visible reward/card counts and card identity review diagnostics
- updates `visible_reward_probe_last_event` to `reward_collected`
- refreshes the runtime run-state probe from `RunManager.ToSave(null)`
- reports only booleans and counts, including potion count
- keeps `screen_type: "exporter_status"`
- keeps `card_reward_live_export_candidate` refused
- does not export live gold, HP, deck, relic IDs, potion IDs, or recommendation-ready `card_reward`

The expected refusal reasons after a gold/potion pickup on a mixed screen are:

- `mixed_reward_screen_state_may_change`
- `missing_required_run_state_field`
- `unmapped_potion` when potion count is nonzero but no post-pickup potion ID review item is available

Repo-local verification passed:

- exporter mod build: 0 warnings / 0 errors
- `inspect-export tests/fixtures/exporter_status_v033_reward_collected_freshness_state.json`
- `recommend-export --confirmed` rejects the fixture because it is `exporter_status`
- `pytest tests/test_exporter_state.py tests/test_exporter_mapping_snapshot.py -q`

The real STS2 mods-folder install-check was approved and passed:

- installed manifest reports `version: "v0.3.3"`
- startup live export reports `exporter_version: "0.3.3"` and remains `screen_type: "exporter_status"`
- after the user picked gold and potion rewards before choosing a card, `visible_reward_probe_last_event` reported `reward_collected`
- post-pickup runtime probe reported `serializable_run_seen`, `card_reward_run_state_serializable_run_available: true`, `card_reward_run_state_gold_present: true`, `card_reward_run_state_potions_present: true`, and `card_reward_run_state_potion_count: 1`
- candidate stayed `refused` with `mixed_reward_screen_state_may_change`, `missing_required_run_state_field`, and `unmapped_potion`
- after leaving the reward screen, live export remained `exporter_status`, reported `reward_skipped`, cleared visible reward counts to zero, cleared review item arrays, and refused with stale-state diagnostics
- no live gold value, HP value, deck, relic IDs, potion IDs, or recommendation-ready `card_reward` was exported

## Installed v0.3.4 Mixed Reward Readiness Contract

Installed `v0.3.4` adds status-only mixed reward freshness diagnostics to make the remaining post-pickup blockers explicit:

- `card_reward_live_export_mixed_reward_freshness_status`
- `card_reward_live_export_mixed_reward_freshness_blockers`
- `card_reward_live_export_mixed_reward_freshness_writes_recommendation_state`

For the observed post-gold/potion pickup shape, the status is `reward_collected_serializable_counts_seen`, while blockers are:

- `run_state_not_aligned`
- `visible_reward_player_not_aligned`
- `potion_identity_not_mapped_after_refresh`
- `mixed_reward_live_export_not_approved`

This does not export live gold, HP, deck, relic IDs, potion IDs, or recommendation-ready card reward state. It keeps the candidate refused and leaves mixed reward `card_reward` export blocked until current player alignment, potion identity mapping, scalar freshness, and the mixed reward export boundary are explicitly resolved.

Repo-local verification passed:

- exporter mod build: 0 warnings / 0 errors
- `inspect-export tests/fixtures/exporter_status_v034_mixed_reward_readiness_state.json`
- `recommend-export --confirmed` rejects the fixture because it is `exporter_status`
- `pytest tests/test_exporter_state.py tests/test_exporter_mapping_snapshot.py -q`

The real STS2 mods-folder install-check was approved and passed:

- installed manifest reports `version: "v0.3.4"`
- startup live export reports `exporter_version: "0.3.4"`, remains `screen_type: "exporter_status"`, and reports mixed reward freshness `not_applicable`
- after the user picked gold and potion rewards before choosing a card, `visible_reward_probe_last_event` reported `reward_collected`
- post-pickup runtime probe reported `serializable_run_seen`, `card_reward_run_state_gold_present: true`, `card_reward_run_state_potions_present: true`, and `card_reward_run_state_potion_count: 1`
- mixed reward freshness status reported `reward_collected_serializable_counts_seen`
- mixed reward freshness blockers were `run_state_not_aligned`, `visible_reward_player_not_aligned`, `potion_identity_not_mapped_after_refresh`, and `mixed_reward_live_export_not_approved`
- candidate stayed `refused` with `mixed_reward_screen_state_may_change`, `missing_required_run_state_field`, and `unmapped_potion`
- after leaving the reward screen, live export remained `exporter_status`, reported `reward_skipped`, cleared visible reward counts to zero, cleared review item arrays, and returned mixed reward freshness status to `not_applicable`
- no live gold value, HP value, deck, relic IDs, potion IDs, or recommendation-ready `card_reward` was exported

## Installed v0.3.5 Post-Pickup Potion Identity Review

Installed `v0.3.5` refreshes the existing ADR 6 relic/potion identity review diagnostic from the public serializable run after `NRewardsScreen.RewardCollectedFrom(Control)`.

The refresh only runs when the previous observation is an active visible card reward screen. It still writes only `screen_type: "exporter_status"` and does not export live scalar values, top-level `potions`, or recommendation-ready `card_reward`.

The fixture `tests/fixtures/exporter_status_v035_reward_collected_potion_identity_state.json` captures the intended status-only shape:

- `relic_potion_identity_review_probe: "ids_revealed_for_review"`
- `relic_potion_identity_review_last_event: "reward_collected"`
- `potion_identity_review_count: 1`
- `potion_identity_review_mapping_unknown_count: 1`
- `potion_identity_review_items[0].public_model_id: "COLORLESS_POTION"`
- `potion_identity_review_items[0].normalized_candidate_id: "colorless_potion"`
- no top-level `potions`, live gold, HP, or recommendation-ready card reward

Repo-local verification passed:

- exporter mod build: 0 warnings / 0 errors
- `inspect-export tests/fixtures/exporter_status_v035_reward_collected_potion_identity_state.json`
- `recommend-export --confirmed` rejects the fixture because it is `exporter_status`
- `pytest tests/test_exporter_state.py tests/test_exporter_mapping_snapshot.py -q`

The real STS2 mods-folder install-check was approved and passed:

- installed manifest reports `version: "v0.3.5"`
- startup live export reports `exporter_version: "0.3.5"`, remains `screen_type: "exporter_status"`, and reports relic/potion review `not_observed`
- after the user picked gold and potion rewards before choosing a card, `visible_reward_probe_last_event` reported `reward_collected`
- post-pickup relic/potion review reported `ids_revealed_for_review` with last event `reward_collected`
- observed potion ID was `COLORLESS_POTION`
- normalized potion candidate was `colorless_potion`
- potion mapping status was `unknown`
- candidate stayed `refused` with `mixed_reward_screen_state_may_change`, `missing_required_run_state_field`, and `unmapped_potion`
- after leaving the reward screen, live export remained `exporter_status`, reported `reward_skipped`, and cleared relic/potion review items
- no live gold value, HP value, top-level `potions`, or recommendation-ready `card_reward` was exported

## Installed v0.3.6 Colorless Potion Mapping

Installed `v0.3.6` records the reviewed `COLORLESS_POTION` -> `colorless_potion` mapping as a tiny potion data seed and adds it to the exporter status-diagnostic mapping snapshot.

The fixture `tests/fixtures/exporter_status_v036_colorless_potion_mapping_state.json` verifies the expected status-only shape:

- `screen_type: "exporter_status"`
- `exporter_version: "0.3.6"`
- `potion_identity_review_mapping_known_count: 1`
- `potion_identity_review_mapping_unknown_count: 0`
- `potion_identity_review_items[0].deckseer_id: "colorless_potion"`
- `card_reward_live_export_unmapped_potion_count: 0`
- mixed reward freshness blockers are still `run_state_not_aligned`, `visible_reward_player_not_aligned`, and `mixed_reward_live_export_not_approved`
- no live gold value, HP value, top-level `potions`, or recommendation-ready `card_reward` is exported

The real STS2 mods-folder install-check passed:

- installed manifest reports `version: "v0.3.6"`
- startup live export reports `exporter_version: "0.3.6"` and remains `screen_type: "exporter_status"`
- on a visible card reward screen after gold and potion pickup, `visible_reward_probe_last_event` reported `reward_collected`
- potion identity review reported `COLORLESS_POTION` -> `colorless_potion` as `known`
- `card_reward_live_export_unmapped_potion_count: 0`
- candidate stayed `refused` with `mixed_reward_screen_state_may_change` and `missing_required_run_state_field`
- mixed reward freshness blockers were `run_state_not_aligned`, `visible_reward_player_not_aligned`, and `mixed_reward_live_export_not_approved`
- no live gold value, HP value, top-level `potions`, or recommendation-ready `card_reward` was exported
- `recommend-export --confirmed` rejected the live file because it remained `exporter_status`

## Installed v0.3.9 Mixed Reward Live Export

Installed `v0.3.9` implements the explicit mixed reward live export approval under ADR 4.

The mixed reward `card_reward` export gate is narrow:

- mixed reward screens still refuse before `reward_collected`
- post-`reward_collected` mixed reward screens can export only when required run-state booleans, visible reward player context, serializable run data, deck/relic/potion mapping, and reward card mapping are all clean
- exported files remain `requires_user_confirmation: true`
- unconfirmed `recommend-export` remains blocked
- the exported payload uses the existing `screen_type: "card_reward"` adapter contract and does not change scoring

The fixture `tests/fixtures/exporter_card_reward_live_v039_mixed_reward_state.json` verifies the adapter-facing shape:

- `screen_type: "card_reward"`
- `exporter_version: "0.3.9"`
- `requires_user_confirmation: true`
- `card_reward`: `cloak_and_dagger`, `bouncing_flask`, `infinite_blades`
- `potions`: `colorless_potion`
- `inspect-export` reports the fixture valid
- `recommend-export` rejects the fixture without `--confirmed`
- `recommend-export --confirmed` scores it through the existing card reward scorer

The real STS2 mods-folder install-check passed:

- installed manifest reports `version: "v0.3.9"`
- startup live export reports `exporter_version: "0.3.9"` and remains `screen_type: "exporter_status"`
- startup status has no top-level `card_reward`, `gold`, `hp`, or `potions`
- on the initial mixed reward screen before picking gold/potion, `visible_reward_probe_last_event` reported `rewards_screen_shown`
- the pre-pickup mixed reward screen remained `screen_type: "exporter_status"`
- pre-pickup mixed freshness status was `awaiting_reward_collected`
- pre-pickup mixed freshness blockers were `reward_collection_not_observed`
- pre-pickup `recommend-export --confirmed` rejected the live file because it remained `exporter_status`
- after picking the gold and potion rewards and opening the card choices, the live file wrote `screen_type: "card_reward"`
- post-pickup export reported `requires_user_confirmation: true`
- post-pickup export reported `character: "silent"`, `act: 1`, `floor: 3`, `ascension: 0`, `gold: 127`, and HP `70/70`
- post-pickup export reported card choices `cloak_and_dagger`, `bouncing_flask`, and `infinite_blades`
- post-pickup export reported relics `ring_of_the_snake` and `lead_paperweight`
- post-pickup export reported potion `colorless_potion`
- `inspect-export` reported the post-pickup file valid
- unconfirmed `recommend-export` rejected the post-pickup file because user confirmation was required
- after human confirmation that the visible state matched, `recommend-export --confirmed --format text` succeeded and recommended `cloak_and_dagger`
- closing the card reward screen after selecting a card did not downgrade the export; the live file remained the previous `screen_type: "card_reward"` and could still be recommended with `--confirmed`

This packet does not change scoring, watch mode, automation, or any recommendation behavior.

## Installed v0.3.10 Card Reward Selection Clear-State Fix

Installed `v0.3.10` fixes the stale `card_reward` file observed after the installed `v0.3.9` clear-state proof.

The live log showed `Player 1 selected card reward`, but the exporter did not write a close-state file afterward. Metadata review showed the mixed reward card-choice route uses `NCardRewardSelectionScreen`, which has its own public `_ExitTree()` method. Earlier clear-state coverage only patched `NChooseACardSelectionScreen._ExitTree()`, so it missed this route.

The fix adds a status-only close hook:

- `NCardRewardSelectionScreen._ExitTree()` records `card_reward_selection_screen_closed`
- the exporter writes `screen_type: "exporter_status"`
- `visible_reward_probe_status` becomes `reward_screen_completed`
- visible card reward counts and review item arrays are cleared
- the candidate refuses with `stale_reward_screen`

The fixture `tests/fixtures/exporter_status_v0310_card_reward_selection_closed_state.json` verifies that the closed-screen shape is not recommendation-ready and contains no top-level `card_reward`, `gold`, `hp`, or `potions`.

Live install verification passed after explicit approval:

- startup wrote valid `screen_type: "exporter_status"` with `exporter_version: "0.3.10"`
- the visible card reward screen wrote valid `screen_type: "card_reward"` for `cloak_and_dagger`, `bouncing_flask`, and `infinite_blades`
- after selecting a card and closing the selection screen, the live file downgraded to `screen_type: "exporter_status"`
- the close-state diagnostics reported `visible_reward_probe_last_event: "card_reward_selection_screen_closed"`
- run-state, card identity, deck identity, relic identity, and potion identity diagnostics were cleared
- confirmed `recommend-export` rejected the closed-screen file because it was `exporter_status`

## Installed v0.3.7 Reward-Collected Visible Player Context

Installed `v0.3.7` retains the active public `RewardsSet` while the reward screen remains active and reuses it for the status-only `reward_collected` runtime probe.

This is not a live export approval. It only lets the existing boolean diagnostic distinguish a missing `IRunState` argument from missing visible reward context after a gold or potion pickup.

The fixture `tests/fixtures/exporter_status_v037_reward_collected_visible_player_state.json` verifies the expected status-only shape:

- `screen_type: "exporter_status"`
- `exporter_version: "0.3.7"`
- `visible_reward_probe_last_event: "reward_collected"`
- `card_reward_run_state_runtime_probe: "serializable_run_seen"`
- `card_reward_run_state_available: false`
- `card_reward_run_state_visible_reward_player_present: true`
- `card_reward_live_export_missing_fields`: `run_state`
- mixed reward freshness blockers are `run_state_not_aligned` and `mixed_reward_live_export_not_approved`
- `card_reward_live_export_unmapped_potion_count: 0`
- no visible reward player ID, live gold value, HP value, top-level `potions`, or recommendation-ready `card_reward` is exported

The active `RewardsSet` reference is cleared when the card-choice path is observed or when the reward screen is skipped, closed, or completed.

The real STS2 mods-folder install-check passed:

- installed manifest reports `version: "v0.3.7"`
- startup live export reports `exporter_version: "0.3.7"` and remains `screen_type: "exporter_status"`
- on a visible card reward screen after gold/potion pickup, `visible_reward_probe_last_event` reported `reward_collected`
- `card_reward_run_state_runtime_probe: "serializable_run_seen"`
- `card_reward_run_state_available: false`
- `card_reward_run_state_serializable_run_available: true`
- `card_reward_run_state_visible_reward_player_present: true`
- `card_reward_live_export_missing_fields`: `run_state`
- `card_reward_live_export_mixed_reward_freshness_blockers`: `run_state_not_aligned`, `mixed_reward_live_export_not_approved`
- `card_reward_live_export_unmapped_potion_count: 0`
- `COLORLESS_POTION` still maps known as `colorless_potion`
- no live gold value, HP value, top-level `potions`, or recommendation-ready `card_reward` was exported
- `recommend-export --confirmed` rejected the live file because it remained `exporter_status`

## Installed v0.3.8 Reward-Collected Run-State Context

Installed `v0.3.8` retains the active public `IRunState` while the reward screen remains active and reuses it for the status-only `reward_collected` runtime probe.

This is not a live export approval. It only lets the existing boolean diagnostic distinguish a missing `IRunState` argument from missing run-state context after a gold or potion pickup.

The fixture `tests/fixtures/exporter_status_v038_reward_collected_run_state_context_state.json` verifies the expected status-only shape:

- `screen_type: "exporter_status"`
- `exporter_version: "0.3.8"`
- `visible_reward_probe_last_event: "reward_collected"`
- `card_reward_run_state_runtime_probe: "run_state_seen"`
- `card_reward_run_state_available: true`
- `card_reward_run_state_serializable_run_available: true`
- `card_reward_run_state_visible_reward_player_present: true`
- `card_reward_live_export_refusal_reasons`: `mixed_reward_screen_state_may_change`
- `card_reward_live_export_missing_fields`: empty
- mixed reward freshness blockers are only `mixed_reward_live_export_not_approved`
- `card_reward_live_export_unmapped_potion_count: 0`
- no visible reward player ID, live gold value, HP value, top-level `potions`, or recommendation-ready `card_reward` is exported

The active `IRunState` reference is cleared when the card-choice path is observed or when the reward screen is skipped, closed, or completed.

The real STS2 mods-folder install-check passed:

- installed manifest reports `version: "v0.3.8"`
- startup live export reports `exporter_version: "0.3.8"` and remains `screen_type: "exporter_status"`
- startup status has no top-level `card_reward`, `gold`, `hp`, or `potions`
- `recommend-export --confirmed` rejects the startup file because it remains `exporter_status`
- on a visible card reward screen after gold/potion pickup, `visible_reward_probe_last_event` reported `reward_collected`
- `visible_card_reward_option_count: 3`
- `card_reward_run_state_runtime_probe: "run_state_seen"`
- `card_reward_run_state_available: true`
- `card_reward_run_state_serializable_run_available: true`
- `card_reward_run_state_visible_reward_player_present: true`
- `card_reward_live_export_missing_fields`: empty
- `card_reward_live_export_mixed_reward_freshness_blockers`: `mixed_reward_live_export_not_approved`
- `card_reward_live_export_unmapped_potion_count: 0`
- no live gold value, HP value, top-level `potions`, or recommendation-ready `card_reward` was exported
- `recommend-export --confirmed` rejected the live file because it remained `exporter_status`

## v0.2.10 Status Probe Result

Installed `v0.2.10` adds `CardRewardRunStateCompileProbe`, which writes status-only diagnostics:

- `card_reward_live_export_probe: "run_state_symbols_compiled_not_exported"`
- `card_reward_live_export_required_fields`
- `card_reward_live_export_verified_symbols`
- `card_reward_live_export_writes_recommendation_state: false`

The probe verifies public symbols for the future `card_reward` schema fields: character, act, floor, ascension, gold, HP, deck IDs/upgrades, relic IDs, and potion IDs. It still writes only `screen_type: "exporter_status"` and does not export live deck, HP, gold, relics, potions, or recommendation-ready state.

The real STS2 install-check passed after explicit approval:

- installed manifest reports `version: "v0.2.10"`
- startup status reports `exporter_version: "0.2.10"`
- startup status reports `card_reward_live_export_probe: "run_state_symbols_compiled_not_exported"`
- startup status reports `card_reward_live_export_writes_recommendation_state: false`
- startup status keeps `visible_card_reward_option_count: 0` and `card_identity_review_items: []`
- `recommend-export --confirmed` rejects the live file because it is still `exporter_status`

## Symbol Review Result

`docs/EXPORTER_CARD_REWARD_RUN_STATE_SYMBOL_REVIEW.md` records the post-`v0.2.10` review. The public symbols are necessary but not sufficient for live `card_reward` export because they do not prove runtime availability, current-player alignment, mapping cleanliness, or stale-state behavior during an active reward screen.

The next safe proof is a status-only `v0.2.11` runtime presence diagnostic. Repo-local `v0.2.11` now reports readiness booleans and counts only, not live run-state values or recommendation-ready state.

## v0.2.11 Runtime Probe Result

`v0.2.11` adds `CardRewardRunStateRuntimeProbe`, which is wired through existing visible reward screen observation and still writes only `screen_type: "exporter_status"`.

The status diagnostic reports run-state readiness booleans and counts, including player count, required-field presence, deck/relic/potion counts, deck mapping known/unknown counts, visible reward player presence, and `card_reward_run_state_writes_recommendation_state: false`.

The repo-local fixture and tests verify that no live character ID, HP value, gold value, act/floor/ascension value, deck ID, relic ID, potion ID, selected-card identity, selected/skipped outcome, or recommendation-ready state is exported.

The real STS2 install-check was approved and startup verification passed:

- installed manifest reports `version: "v0.2.11"`
- startup live export reports `exporter_version: "0.2.11"`
- startup live export remains `screen_type: "exporter_status"`
- `card_reward_run_state_runtime_probe: "not_observed"`
- `card_reward_run_state_writes_recommendation_state: false`
- `inspect-export` accepts the live status file
- `recommend-export --confirmed` rejects the live file because it is still `exporter_status`

Visible reward-screen verification also passed the status-only boundary:

- live export remained `screen_type: "exporter_status"`
- required run-state field-presence booleans were true
- runtime probe reported `incomplete` because deck mapping counts were 3 known and 11 unknown
- visible reward card identities mapped to `cloak_and_dagger`, `bouncing_flask`, and `infinite_blades` under the accepted ADR 3 review diagnostic
- no live character ID, HP value, gold value, act/floor/ascension value, deck ID, relic ID, potion ID, selected-card identity, selected/skipped outcome, or recommendation-ready state was exported
- `recommend-export --confirmed` rejected the live file because it remained `exporter_status`

`docs/EXPORTER_CARD_REWARD_DECK_MAPPING_GAP_REVIEW.md` records the 3-known/11-unknown deck result as review evidence only. It does not identify the unknown deck cards because `v0.2.11` intentionally did not export live deck IDs.

ADR 5 accepts a status-only deck ID review diagnostic to resolve this mapping gap, and installed `v0.2.12` implements it. Startup, visible reward-screen, and clear-state verification passed. Installed `v0.2.13` resolves `STRIKE_SILENT` and `DEFEND_SILENT` to the existing manual `strike` and `defend` IDs. Repo-local `v0.2.14` adds reviewed seed data for `dramatic_entrance` and includes it in the status-diagnostic mapping snapshot.

Clear-state verification passed:

- live export remained `screen_type: "exporter_status"`
- `card_reward_run_state_runtime_probe: "cleared"`
- run-state booleans and counts cleared to false/zero
- visible reward counts cleared to zero
- card identity runtime probe cleared to zero counts
- card identity review probe cleared with `card_identity_review_items: []`
- `recommend-export --confirmed` rejected the live file because it remained `exporter_status`

## v0.2.14 Mapping Readiness Result

Installed `v0.2.14` startup, visible reward-screen, and clear-state verification passed.

Visible reward-screen verification reported:

- live export remained `screen_type: "exporter_status"`
- `card_reward_run_state_runtime_probe: "run_state_seen"`
- deck card count 14
- deck card ID read count 14
- deck mapping known count 14
- deck mapping unknown count 0
- `deck_identity_review_mapping_known_count: 14`
- `deck_identity_review_mapping_unknown_count: 0`
- visible reward choices mapped to `cloak_and_dagger`, `bouncing_flask`, and `infinite_blades`
- `card_reward_run_state_writes_recommendation_state: false`

Clear-state verification then reported:

- live export remained `screen_type: "exporter_status"`
- `card_reward_run_state_runtime_probe: "cleared"`
- `card_reward_run_state_runtime_last_event: "reward_skipped"`
- deck and visible reward counts zero
- deck and card identity review items cleared
- `card_reward_run_state_writes_recommendation_state: false`

This completes the observed deck and visible reward mapping proof for the tested run. It does not prove relic ID mapping, potion ID mapping for non-empty potion belts, or safe serialization of live scalar values into the recommendation-ready schema.

## Repo-Local v0.2.15 Refusal Candidate Result

Repo-local `v0.2.15` adds status-only live export candidate/refusal diagnostics. It still writes only:

```json
{
  "screen_type": "exporter_status"
}
```

New diagnostic keys:

- `card_reward_live_export_candidate`
- `card_reward_live_export_refusal_reasons`
- `card_reward_live_export_missing_fields`
- `card_reward_live_export_unmapped_reward_count`
- `card_reward_live_export_unmapped_deck_count`
- `card_reward_live_export_unmapped_relic_count`
- `card_reward_live_export_unmapped_potion_count`
- `card_reward_live_export_candidate_writes_recommendation_state`

The fixture `tests/fixtures/exporter_status_v0215_live_export_candidate_refusal_state.json` captures the intended current refusal shape for the observed `v0.2.14` readiness state:

- visible reward card mapping count is clean
- deck card mapping count is clean
- required run-state presence booleans are clean
- relic count is 2, but relic IDs are not mapped or exported
- candidate status is `refused`
- refusal reason is `unmapped_relic`
- `card_reward_live_export_writes_recommendation_state: false`
- `card_reward_live_export_candidate_writes_recommendation_state: false`

Repo-local verification passed:

- exporter mod build: 0 warnings / 0 errors
- `inspect-export tests/fixtures/exporter_status_v0215_live_export_candidate_refusal_state.json`
- `recommend-export --confirmed` rejects the fixture because it is still `exporter_status`
- focused exporter metadata test for the `v0.2.15` fixture

This packet does not implement live `screen_type: "card_reward"` export.

The real STS2 mods-folder install-check was approved and startup verification passed:

- installed manifest reports `version: "v0.2.16"`
- live export reports `exporter_version: "0.2.16"`
- live export remains `screen_type: "exporter_status"`
- `relic_potion_identity_review_probe: "not_observed"`
- relic identity review counts are zero
- potion identity review counts are zero
- relic and potion identity review item arrays are empty
- `card_reward_live_export_candidate: "refused"`
- `card_reward_live_export_refusal_reasons`: `no_visible_reward`, `missing_required_run_state_field`
- `card_reward_live_export_candidate_writes_recommendation_state: false`
- `inspect-export` accepts the live status file
- `recommend-export --confirmed` rejects the live file because it is still `exporter_status`

Visible reward-screen verification also passed the status-only boundary:

- live export remained `screen_type: "exporter_status"`
- live export reported `exporter_version: "0.2.16"`
- `relic_potion_identity_review_probe: "ids_revealed_for_review"`
- relic identity review counts were 0 known / 2 unknown
- potion identity review counts were 0 known / 0 unknown
- `card_reward_live_export_candidate: "refused"`
- refusal reason was `unmapped_relic`
- missing required fields were empty
- unmapped reward and deck counts were zero
- unmapped relic count was 2
- unmapped potion count was 0
- visible reward mapping remained 3 known / 0 unknown
- deck mapping remained 14 known / 0 unknown
- `card_reward_live_export_candidate_writes_recommendation_state: false`
- `inspect-export` accepts the live status file
- `recommend-export --confirmed` rejects the live file because it is still `exporter_status`

Relic identity review items were:

- `RING_OF_THE_SNAKE` -> `ring_of_the_snake` -> unknown
- `LEAD_PAPERWEIGHT` -> `lead_paperweight` -> unknown

These IDs are review evidence only, not approval to change data or scoring.

Clear-state verification then passed:

- live export remained `screen_type: "exporter_status"`
- live export reported `exporter_version: "0.2.16"`
- `relic_potion_identity_review_probe: "cleared"`
- `relic_potion_identity_review_last_event: "reward_skipped"`
- relic and potion identity review counts were zero
- relic and potion identity review item arrays were empty
- deck and card identity review item arrays were empty
- `card_reward_run_state_runtime_probe: "cleared"`
- `card_reward_live_export_candidate: "refused"`
- `card_reward_live_export_refusal_reasons`: `stale_reward_screen`, `missing_required_run_state_field`
- unmapped reward, deck, relic, and potion counts were zero
- `card_reward_live_export_candidate_writes_recommendation_state: false`
- `inspect-export` accepts the live status file
- `recommend-export --confirmed` rejects the live file because it is still `exporter_status`

## Installed v0.2.15 Startup Result

The real STS2 mods-folder install-check was approved and `v0.2.15` installed successfully after STS2 was closed.

Startup verification passed:

- installed manifest reports `version: "v0.2.15"`
- live export reports `exporter_version: "0.2.15"`
- live export remains `screen_type: "exporter_status"`
- `card_reward_live_export_candidate: "refused"`
- `card_reward_live_export_refusal_reasons`: `no_visible_reward`, `missing_required_run_state_field`
- `card_reward_live_export_missing_fields` includes startup-safe unavailable run-state fields
- unmapped reward, deck, relic, and potion counts are all 0
- `card_reward_live_export_candidate_writes_recommendation_state: false`
- `card_reward_run_state_runtime_probe: "not_observed"`
- `deck_identity_review_probe: "not_observed"`
- `visible_card_reward_option_count: 0`
- `card_identity_review_probe: "not_observed"`
- `card_reward_run_state_writes_recommendation_state: false`
- `inspect-export` accepts the live status file
- `recommend-export --confirmed` rejects the live file because it is still `exporter_status`

## Installed v0.2.15 Visible Reward-Screen Result

On a human-opened visible three-card reward screen, installed `v0.2.15` stayed status-only and produced the intended refusal-first candidate result:

- live export remained `screen_type: "exporter_status"`
- live export reported `exporter_version: "0.2.15"`
- `card_reward_live_export_candidate: "refused"`
- `card_reward_live_export_refusal_reasons`: `unmapped_relic`
- `card_reward_live_export_missing_fields: []`
- `card_reward_live_export_unmapped_reward_count: 0`
- `card_reward_live_export_unmapped_deck_count: 0`
- `card_reward_live_export_unmapped_relic_count: 2`
- `card_reward_live_export_unmapped_potion_count: 0`
- `card_reward_live_export_candidate_writes_recommendation_state: false`
- `card_reward_run_state_runtime_probe: "run_state_seen"`
- deck card count 14
- deck mapping known count 14
- deck mapping unknown count 0
- visible reward option count 3
- visible reward mapping known count 3
- visible reward mapping unknown count 0
- `card_reward_run_state_writes_recommendation_state: false`

Visible reward choices mapped to:

- `CLOAK_AND_DAGGER` -> `cloak_and_dagger`
- `BOUNCING_FLASK` -> `bouncing_flask`
- `INFINITE_BLADES` -> `infinite_blades`

Deck identity review still mapped all 14 observed deck cards, including the reviewed Silent starter aliases and `DRAMATIC_ENTRANCE` -> `dramatic_entrance`.

`inspect-export` accepted the live status file. `recommend-export --confirmed` rejected it because it is still `exporter_status`.

## Installed v0.2.15 Clear-State Result

After the reward screen was skipped/left, installed `v0.2.15` cleared the live review diagnostics and refused the live export candidate for stale/no-current reward state:

- live export remained `screen_type: "exporter_status"`
- live export reported `exporter_version: "0.2.15"`
- `card_reward_live_export_candidate: "refused"`
- `card_reward_live_export_refusal_reasons`: `stale_reward_screen`, `missing_required_run_state_field`
- `card_reward_live_export_unmapped_reward_count: 0`
- `card_reward_live_export_unmapped_deck_count: 0`
- `card_reward_live_export_unmapped_relic_count: 0`
- `card_reward_live_export_unmapped_potion_count: 0`
- `card_reward_live_export_candidate_writes_recommendation_state: false`
- `card_reward_run_state_runtime_probe: "cleared"`
- `card_reward_run_state_runtime_last_event: "reward_skipped"`
- deck, relic, potion, and visible reward counts are zero
- `deck_identity_review_probe: "cleared"`
- `deck_identity_review_items: []`
- `card_identity_review_probe: "cleared"`
- `card_identity_review_items: []`
- `card_reward_run_state_writes_recommendation_state: false`

`inspect-export` accepted the live clear-state file. `recommend-export --confirmed` rejected it because it is still `exporter_status`.

## Repo-Local v0.2.16 Relic/Potion Identity Review Result

ADR 6 is accepted, and repo-local `v0.2.16` adds a status-only relic/potion ID review diagnostic. It still writes only:

```json
{
  "screen_type": "exporter_status"
}
```

New diagnostic keys include:

- `relic_potion_identity_review_probe`
- `relic_potion_identity_review_last_event`
- `relic_identity_review_count`
- `relic_identity_review_mapping_known_count`
- `relic_identity_review_mapping_unknown_count`
- `relic_identity_review_items`
- `potion_identity_review_count`
- `potion_identity_review_mapping_known_count`
- `potion_identity_review_mapping_unknown_count`
- `potion_identity_review_items`
- `relic_potion_identity_review_error`

Repo-local verification passed:

- exporter mod build: 0 warnings / 0 errors
- `inspect-export tests/fixtures/exporter_status_v0216_relic_potion_identity_review_state.json`
- `recommend-export --confirmed` rejects the fixture because it is still `exporter_status`
- focused exporter metadata test for the `v0.2.16` fixture

This packet does not implement live `screen_type: "card_reward"` export and does not install the repo-local build into the real STS2 mods folder.

## Open Questions

- Which public run-state source should supply deck, HP, gold, relics, potions, act, floor, and character without reading save/profile files?
- Can all future deck cards be normalized with the same deterministic mapping used for reward cards, beyond the observed `v0.2.14` deck?
- Should upgraded reward cards remain represented as plain IDs for V1, with upgrade state deferred, or should live export wait until the importer supports reward-card objects?
- What exact caveat should be shown when map/path context remains unknown?
- Installed `v0.2.17` maps the two reviewed relic IDs from the `v0.2.16` proof and reports a ready status-only candidate on the visible reward screen.

## Next Packet

The mixed reward card reward path is implemented and live-proven through installed `v0.4.7`, including the post-selection downgrade that fixed the stale-file failure first found in `v0.3.9`.

The Envenom / Predator / Memento Mori state has been accepted as `silent_v047_envenom_attack_payoff_guard` after user-approved scenario-intake and scoring review. Future card reward packets should use the same boundary: only accept real-run states after source context and expected-choice review, and do not change broader scoring rules, card priors, empirical rows, recommendation baselines, watch mode, OCR, input automation, or exporter behavior without a separately approved packet.
