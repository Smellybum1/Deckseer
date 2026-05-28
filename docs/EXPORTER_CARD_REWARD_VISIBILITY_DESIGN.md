# Deckseer Exporter Card Reward Visibility Design

Status: `id_reveal_diagnostic_repo_local`

Prepared on 2026-05-24 after the diagnostic compile probe against local Slay the Spire 2 `public-beta`, game version `v0.106.1`, build `23372702`.

## Scope

This packet defines how to prove that normal mod-accessible reward APIs correspond to the visible card reward screen before Deckseer exports live card reward state.

It does not implement exporter code, install a mod package, export card choices, export run state, change Deckseer scoring, or add watch mode.

Accepted guardrails still apply:

- no gameplay automation or input control
- no OCR, screenshots, live capture, watch mode, memory/process tricks, packet inspection, stealth, or evasion
- no save/profile modification
- no private-field reflection or publicizer workarounds
- public screen observation is allowed only for the count-only `exporter_status` diagnostic approved in ADR 2
- no Deckseer scoring, prior, empirical, accuracy, or recommendation changes
- all future card reward exports must remain read-only/export-only and `requires_user_confirmation: true`

## Question To Prove

Before emitting `screen_type: "card_reward"`, the exporter needs evidence for three claims:

1. `RewardsSet.Rewards` contains the currently offered reward models for the reward screen the player can see.
2. Each visible card reward is represented by a `CardReward` whose `Cards` collection contains the same choices shown in the UI.
3. The available card identifiers can be converted to Deckseer IDs without guessing or changing recommendation behavior.

The compile probe answered only "can source code reference these members?" It did not prove runtime visibility or identifier mapping.

## Public API Baseline

Future proof work should stay on the public symbols that compiled in `CardRewardApiProbe`:

- `RunManager.Instance`
- `RunManager.IsInProgress`
- `RunManager.ToSave`
- `RewardsSet.Rewards`
- `Reward.IsPopulated`
- `Reward.Description`
- `Reward.ParentRewardSet`
- `CardReward.Cards`
- `CardReward.CanSkip`
- `CardReward.CanReroll`
- `CardReward.IsPopulated`
- `CardReward.ToSerializable`
- `SerializableRun.Players`
- `SerializablePlayer.CharacterId`
- `SerializablePlayer.CurrentHp`
- `SerializablePlayer.MaxHp`
- `SerializablePlayer.Gold`
- `SerializablePlayer.Deck`
- `SerializablePlayer.Relics`
- `SerializablePlayer.Potions`
- `SerializableCard.Id`

Avoid these metadata-visible members because they did not compile from normal mod source:

- `RunManager.State`
- `Reward.RewardType`
- `CardReward.Options`
- `NRewardButton.GetReward`

## Proof Sequence

### 1. Install-Check Current Diagnostic Build

Install-check the existing `v0.2.0` diagnostic status build only after explicit user approval because it updates the local STS2 `mods/DeckseerExporter` package.

Acceptance:

- the game writes `screen_type: "exporter_status"`
- `diagnostics.card_reward_api_probe` is `compiled`
- `diagnostics.verified_symbols` includes `RewardsSet.Rewards` and `CardReward.Cards`
- no card choices, deck, HP, gold, relics, potions, save data, or screen data are exported

### 2. Add A Visibility-Only Diagnostic Build

After the status install-check passes, a later repo packet may add a second diagnostic build that still writes `screen_type: "exporter_status"` only. Its output should answer whether a public reward model is present without becoming a recommendation input.

Allowed diagnostic fields:

- exporter version
- game patch/build if available through already-safe status metadata
- `is_run_in_progress`
- `visible_reward_probe_status`, such as `not_in_run`, `no_reward_model`, `card_reward_model_seen`, or `unknown`
- count-only card reward facts, such as card reward count and option count
- caveats explaining that no card IDs or run state are exported

Not allowed in this diagnostic stage:

- card IDs or card names
- deck contents
- relics or potions
- HP, gold, act, floor, ascension, or path state
- automatic Deckseer recommendation
- any call path that mutates rewards, rerolls options, selects cards, or drives UI

Acceptance:

- opening a normal non-reward room reports no card reward model
- opening a visible card reward screen reports a card reward model and the visible option count
- leaving or selecting the reward clears or changes the diagnostic status
- the exported file remains valid under `inspect-export`

### 3. Manual Visibility Comparison

When the visibility-only build exists, test it with a tiny manual matrix:

| Situation | Expected diagnostic |
| --- | --- |
| Main menu or no run | no run or no reward model |
| Normal room without reward | no card reward model |
| Card reward with 3 visible cards | card reward model seen, option count 3 |
| Card reward with skip disabled or special count, if naturally encountered | count and skip diagnostics match visible UI |
| After reward is taken or skipped | no active card reward model or all rewards selected |

This comparison should be documented with observed outputs, but not promoted to `screen_type: "card_reward"` yet.

### 4. Identifier Mapping Probe

Only after the count/visibility proof passes should a later packet inspect card identity mapping. That packet should still be explicit and human-confirmed because it starts exposing live card choice identifiers.

Minimum acceptance before `screen_type: "card_reward"`:

- card IDs are stable public model IDs, not localized display text
- upgraded card state is available or safely represented
- each exported reward card ID either maps exactly to a Deckseer card ID or appears in caveats as unknown
- Deckseer `inspect-export` shows the exported choices before `recommend-export --confirmed` can score them
- no private-field reflection or UI-driving code is needed

## Stop Conditions

Stop before live card reward export if:

- visible card reward detection requires private fields or reflection
- the only available hook requires modifying reward options
- `CardReward.Cards` does not track the visible reward screen after rerolls, skips, or special reward counts
- public model IDs do not map safely to Deckseer IDs
- `RunManager.ToSave()` appears to write files, mutate state, or expose stale data
- the proof needs screenshots, OCR, input automation, save editing, process memory, or packet inspection

## Initial Next Packet Result

The original next packet was the `v0.2.0` status diagnostic install-check. It completed after explicit approval and verified the installed exporter still wrote only `screen_type: "exporter_status"`.

## Attempted Visibility Diagnostics

Checked on 2026-05-24 against the local Slay the Spire 2 `public-beta`, game version `v0.106.1`, build `23372702`.

The first implementation attempts were rejected and rolled back:

- `v0.3.0` used a custom Godot `Node` for polling. The game initialized the mod, but Godot bridge calls on the custom node produced repeated `ArgumentException` log entries, and the export file stayed at the startup baseline.
- `v0.3.1` replaced the custom node with a built-in Godot `Timer`, but the callback route still did not produce a live updated visibility export.
- `v0.3.2` used `ModHelper.SubscribeForRunStateHooks`, but constructing `CardRewardVisibilityHookModel : AbstractModel` directly caused `DuplicateModelException` during run load. This is unsafe for user runs and must not be reinstalled.

The local STS2 mod package was rolled back to the known-good `v0.2.0` status-only build. The rollback was verified with `inspect-export`: `valid: true`, `screen_type: "exporter_status"`, `exporter_version: "0.2.0"`, and no live run state.

Do not retry custom Godot polling nodes, built-in timer callbacks from the initializer, or direct `AbstractModel` construction for run hook subscription. The next visibility packet should first research the proper ModelDb-backed way to create a mod hook model, or choose another public observation path that does not attach custom Godot callbacks or instantiate canonical models directly.

## Safe Hook-Model Research

Checked repo-only on 2026-05-24 with `tools/sts2_metadata_probe --signatures`; no STS2 mod package was installed and the game was not launched.

Relevant local metadata findings:

| Surface | Observed signature or member | Implication |
| --- | --- | --- |
| `ModHelper.SubscribeForRunStateHooks` | `Void SubscribeForRunStateHooks(String, RunHookSubscriptionDelegate)` | The subscription API is available, but the earlier failure showed the returned models must be created the game's way. |
| `RunHookSubscriptionDelegate` | `IEnumerable<AbstractModel> Invoke(RunState)` | A subscriber returns hook models, not ad hoc callbacks. |
| `ModHelper.IterateAllRunStateSubscribers` | `IEnumerable<AbstractModel> IterateAllRunStateSubscribers(RunState)` | The game later iterates those returned models as canonical hook listeners. |
| `ModelDb` | `Contains(Type)`, `Inject(Type)`, `Singleton<T>()` | The safe hook compile probe proves a public singleton registration/retrieval path for hook-only listener models. |
| `AbstractModel` | `Id`, `IsCanonical`, `InitId(ModelId)`, `AssertCanonical()`, `MutableClone()` | Model identity/canonical state is managed by the engine. Directly constructing a subclass bypasses that lifecycle. |
| `SingletonModel` | Base type accepted by `ModelDb.Singleton<T>()` | Custom hook listener probes should use this category instead of arbitrary `AbstractModel` subclasses. |
| `ModHelper.AddModelToPool` | `AddModelToPool()`, `AddModelToPool(Type, Type)` | This may be for card/relic/potion pool content and is not yet proven to be the right hook-only registration path. |

Conclusion:

- Do not construct a custom `AbstractModel` subclass directly inside a run hook subscription.
- Use a custom `SingletonModel` subclass for hook-only listener probes.
- Register the singleton model type with `ModelDb.Inject(typeof(...))` and retrieve it with `ModelDb.Singleton<T>()`.
- Treat `ModHelper.AddModelToPool` as unproven for hook-only listeners.
- Keep the installed exporter at `v0.2.0` until explicit approval for another live install-check.

## Safe Hook-Model Compile Probe Result

The repo-local `v0.2.1` source build now includes `DeckseerHookCompileProbeModel : SingletonModel` and `HookModelCompileProbe`.

The compile-only probe proves this public path:

1. `ModelDb.Contains(typeof(DeckseerHookCompileProbeModel))`
2. `ModelDb.Inject(typeof(DeckseerHookCompileProbeModel))`
3. `ModelDb.Singleton<DeckseerHookCompileProbeModel>()`
4. `hookModel.AssertCanonical()`
5. `ModHelper.SubscribeForRunStateHooks(MainFile.ModId, CompileOnlyGetRunHookModels)`

The probe is intentionally dormant: `MainFile.Initialize()` does not call `CompileOnlyRegisterRunHook()`, so the source build still writes only a static `screen_type: "exporter_status"` payload. The new diagnostic metadata reports `hook_model_compile_probe: "compiled_not_registered"`.

`ModelDb.Get<T>()` and `ModelDb.Get(Type)` remain metadata-visible but not public enough for normal mod source in this project configuration; do not use them for the next live diagnostic.

## Status-Only Visibility Diagnostic Compile Attempt

Attempted after explicit approval on 2026-05-24, but stopped before live install.

The proven singleton hook path can register a hook listener, but the next required count source did not compile from normal mod source:

- `RunManager.Instance.RewardsSetSynchronizer.LocalPlayer` is metadata-visible but not public enough.
- `RunManager.Instance.RewardsSetSynchronizer.GetRewardStateForPlayer(...)` is metadata-visible but not public enough.
- `Player` exposes deck, relic, potion, gold, and run-state properties, but no public active reward stack.
- `Reward.ParentRewardSet` exposes only a `LinkedRewardSet`, not the owning `RewardsSet`.

Because the visibility diagnostic cannot currently count the active visible reward set without private fields, publicizer access, custom Godot UI polling, or save-like fallback state, it was not installed into the real STS2 mods folder.

## Active Reward Source Research

Checked repo-only on 2026-05-24 with `tools/sts2_metadata_probe --signatures --accessibility`; no STS2 mod package was installed and the game was not launched.

The remaining public-looking reward sources split into five categories:

| Surface | Finding | Result |
| --- | --- | --- |
| `RewardsSetSynchronizer` | `BeginRewardsSet(RewardsSet)`, `IsRewardsSetCompleted(...)`, and `GetNextRewardIds()` are public, but `LocalPlayer`, `GetRewardStateForPlayer(...)`, and the reward stack are private. | Blocked for read-only active reward inspection from normal mod source. |
| Run hooks | `ModifyRewards(IRunState, Player, List<Reward>, AbstractRoom)` and `AfterModifyingRewards()` can participate in reward generation, while `AfterRewardTaken(Player, Reward)` receives a selected reward after the decision. Card reward option hooks see generation inputs/options. | Insufficient for proving the currently visible reward screen before the user chooses. |
| Screen nodes | `NRewardsScreen.ShowScreen(RewardsSet, Boolean, IRunState)` is public and receives the exact `RewardsSet`; `NRewardButton.Reward` has a public getter. | Useful evidence, but observing it would require a UI method patch or live Godot node traversal/callback path. Both are outside the current guardrails. |
| Reward commands | `RewardsCmd.GenerateForRoomEnd(...)`, `GenerateCustom(...)`, `OfferForRoomEnd(...)`, and `OfferCustom(...)` are public. | Unsafe for diagnostics because they generate or offer rewards instead of passively reading an existing visible reward. |
| Save-like state | `RunManager.ToSave()` compiles, but it is save-like fallback state rather than proof of the live visible reward screen. | Still excluded from the visibility proof route. |

Conclusion:

- No approved public active `RewardsSet` observation route was found under the original strict boundary.
- ADR 2 approved a count-only public screen observation diagnostic for `NRewardsScreen.ShowScreen(RewardsSet, ...)`.
- The diagnostic must still export only `screen_type: "exporter_status"` plus count/caveat metadata.

## Public Screen Observation Probe Result

Implemented repo-local on 2026-05-24 as exporter source `v0.2.2`, then install-checked after explicit approval.

The diagnostic uses Harmony to observe public reward-screen methods:

- `NRewardsScreen.ShowScreen(RewardsSet, Boolean, IRunState)`
- `NRewardsScreen.RewardCollectedFrom(Control)`
- `NRewardsScreen.RewardSkippedFrom(Control)`

The probe writes only `screen_type: "exporter_status"` and count-only diagnostics:

- `screen_observation_probe`
- `visible_reward_probe_status`
- `visible_reward_probe_last_event`
- `visible_reward_count`
- `visible_card_reward_count`
- `visible_card_reward_option_count`
- skip/all-selected booleans and caveats

It does not export card IDs, card names, deck, HP, gold, relics, potions, save/profile data, or recommendation-ready run state. The repo-local exporter build passed with 0 warnings and 0 errors, and `inspect-export` accepts the new `tests/fixtures/exporter_status_v022_screen_observation_state.json` fixture as status metadata only.

## v0.2.2 Install-Check Result

Installed after explicit approval on 2026-05-24.

The real STS2 mod package was updated to `v0.2.2`, the game launched, and the startup export passed `inspect-export`:

- `screen_type: "exporter_status"`
- `exporter_version: "0.2.2"`
- `screen_observation_probe: "registered"`
- `visible_reward_probe_status: "not_observed"`
- no card IDs, card names, deck, HP, gold, relics, potions, save/profile data, OCR, watch mode, or input automation

On a visible card reward screen showing two card choices, the export remained at the startup state (`not_observed`, zero counts). Local metadata then showed the visible "Choose a Card" UI is likely routed through `NChooseACardSelectionScreen.ShowScreen(IReadOnlyList<CardModel>, Boolean)`, not `NRewardsScreen.ShowScreen(RewardsSet, ...)`.

Conclusion: `v0.2.2` proves the status-only screen observation probe can register safely, but it does not observe the visible card reward screen path encountered in this manual test.

## Card Choice Screen Observation Probe Result

Implemented repo-local on 2026-05-24 as exporter source `v0.2.3`, then install-checked after explicit approval.

The diagnostic keeps the `v0.2.2` reward-screen observation and adds count-only observation for:

- `NChooseACardSelectionScreen.ShowScreen(IReadOnlyList<CardModel>, Boolean)`

The new diagnostics remain status metadata only:

- `visible_reward_probe_status: "card_choice_screen_seen"` when a public card-choice screen is shown
- `visible_card_reward_option_count`
- `visible_card_choice_option_count`
- `visible_card_choice_can_skip`

The repo-local exporter build passed with 0 warnings and 0 errors. `inspect-export` accepts `tests/fixtures/exporter_status_v023_card_choice_screen_state.json`, and focused exporter-state tests pass.

## v0.2.3 Install-Check Result

Installed after explicit approval on 2026-05-24.

The real STS2 mod package was updated to `v0.2.3`, the game launched, and the startup export passed `inspect-export`:

- `screen_type: "exporter_status"`
- `exporter_version: "0.2.3"`
- `screen_observation_probe: "registered"`
- `screen_observation_verified_symbols` includes `NChooseACardSelectionScreen.ShowScreen`
- `visible_reward_probe_status: "not_observed"`
- zero reward/card counts
- no card IDs, card names, deck, HP, gold, relics, potions, save/profile data, OCR, watch mode, or input automation

On the same visible card reward screen showing two card choices (`Panic Button`, `Dramatic Entrance`) and Skip, the game-written status file reported:

- `visible_reward_probe_status: "card_choice_screen_seen"`
- `visible_reward_probe_last_event: "choose_card_screen_shown"`
- `visible_card_reward_count: 1`
- `visible_card_reward_option_count: 2`
- `visible_card_choice_option_count: 2`
- `visible_card_choice_can_skip: true`
- `visible_reward_skip_disallowed: false`

Conclusion: the public `NChooseACardSelectionScreen.ShowScreen(...)` path corresponds to this visible two-card reward screen for count-only diagnostics. This still does not approve exporting card IDs or recommendation-ready live run state.

## Card Choice Clear-State Probe Result

Implemented repo-local on 2026-05-24 as exporter source `v0.2.4`, then install-checked after explicit approval.

The diagnostic keeps the `v0.2.3` card-choice screen observation and adds a count-clearing public lifecycle observation:

- `NChooseACardSelectionScreen._ExitTree()`

When this hook fires, the exporter writes another `screen_type: "exporter_status"` payload with:

- `visible_reward_probe_status: "reward_screen_completed"`
- `visible_reward_probe_last_event: "choose_card_screen_closed"`
- reward/card/card-choice counts reset to zero
- skip and all-selected fields reset to null

This is intentionally not proof of which card was selected or whether Skip was chosen. It only proves a repo-local compile path for clearing stale count-only diagnostics when the public card-choice screen closes.

The repo-local exporter build passed with 0 warnings and 0 errors. `inspect-export` accepts `tests/fixtures/exporter_status_v024_card_choice_closed_state.json`, and focused exporter-state tests pass.

## v0.2.4 Install-Check Result

Installed after explicit approval on 2026-05-24.

The real STS2 mod package was updated to `v0.2.4`, the game launched, and the startup export passed `inspect-export`:

- `screen_type: "exporter_status"`
- `exporter_version: "0.2.4"`
- `screen_observation_probe: "registered"`
- `screen_observation_verified_symbols` includes `NChooseACardSelectionScreen._ExitTree`
- `visible_reward_probe_status: "not_observed"`
- zero reward/card counts
- no card IDs, card names, deck, HP, gold, relics, potions, save/profile data, OCR, watch mode, or input automation

After the user manually closed a visible card reward screen by selecting or skipping, the game-written status file reported:

- `visible_reward_probe_status: "reward_screen_completed"`
- `visible_reward_probe_last_event: "choose_card_screen_closed"`
- `visible_reward_count: 0`
- `visible_card_reward_count: 0`
- `visible_card_reward_option_count: 0`
- `visible_card_choice_option_count: 0`
- `visible_card_choice_can_skip: null`
- `visible_reward_skip_disallowed: null`
- `visible_reward_all_selected: null`

Conclusion: the public `NChooseACardSelectionScreen._ExitTree()` path can clear stale count-only diagnostics after the tested card reward screen closes. This still does not approve exporting card IDs, selected-card identity, skip identity, or recommendation-ready live run state.

## Card Identity Compile Probe Result

Implemented repo-local on 2026-05-24 as exporter source `v0.2.5`; no `v0.2.5` STS2 mod package has been installed.

The compile-only probe proves these public identity and upgrade-state paths from the card-choice model surface:

- `CardModel.Id`
- `CardModel.CurrentUpgradeLevel`
- `CardModel.IsUpgraded`
- `CardModel.ToSerializable()`
- `CardCreationResult.Card`
- `SerializableCard.Id`
- `SerializableCard.CurrentUpgradeLevel`

The initial build showed `SerializableCard.Id` may be nullable under the current C# annotations, so the probe records the serialized ID path as nullable while treating `CardModel.Id` as the primary direct model ID path. After that adjustment, the repo-local exporter build passed with 0 warnings and 0 errors.

The probe writes only status metadata:

- `card_identity_mapping_probe: "compiled_not_exported"`
- `card_identity_mapping_verified_symbol_count`
- `card_identity_mapping_verified_symbols`

It does not export live card IDs, card names, selected-card identity, deck, HP, gold, relics, potions, save/profile data, OCR, watch mode, input automation, or recommendation-ready run state. `inspect-export` accepts `tests/fixtures/exporter_status_v025_card_identity_probe_state.json`, and focused exporter-state tests pass.

## Card Identity Contract Hardening Result

Completed repo-local on 2026-05-24; no STS2 mod package was installed and the game was not launched.

Adapter fixtures now cover the pre-live-ID contract:

- `tests/fixtures/exporter_card_reward_unknown_id_state.json`
- `tests/fixtures/exporter_card_reward_upgraded_deck_state.json`
- `tests/fixtures/exporter_card_reward_upgraded_reward_object_state.json`

Focused tests verify:

- `recommend-export` requires `--confirmed` before attempting to score unknown exported IDs.
- after `--confirmed`, unknown reward IDs fail clearly with missing card data instead of producing a recommendation.
- upgraded deck cards are preserved by the current schema.
- metadata caveats remain outside the scorer and are surfaced by `inspect-export`.
- object-shaped upgraded reward cards are rejected until a later approved schema change supports reward-card upgrade state.

This packet intentionally does not change scoring, recommendation behavior, public CLI semantics, card priors, empirical data, exporter live output, watch mode, OCR, input automation, or game files.

## Status-Only Card Identity Runtime Diagnostic Result

Implemented repo-local on 2026-05-24 as exporter source `v0.2.6`, install-checked as `v0.2.7`, then corrected and install-checked as `v0.2.8` after explicit approval.

The diagnostic extends the proven `NChooseACardSelectionScreen.ShowScreen(IReadOnlyList<CardModel>, Boolean)` observation path with ID-shape counts only. It reads public `CardModel.Id.Entry`, `CardModel.CurrentUpgradeLevel`, `CardModel.IsUpgraded`, and `CardModel.ToSerializable()` values, compares normalized entries to an embedded Deckseer card ID snapshot, and writes only counts/status fields under `export_metadata.diagnostics`.

The `v0.2.7` live install-check revealed that the tested visible three-card reward screen updated through `NRewardsScreen.ShowScreen(RewardsSet, ...)`, not the card-choice screen hook. The installed exporter stayed valid and status-only, and count-only visibility matched the visible screen (`visible_card_reward_option_count: 3`), but identity counts stayed zero. Repo-local `v0.2.8` now computes the same status-only identity counts from public `CardReward.Cards` when the reward-screen route is the observed route.

The `v0.2.8` live install-check succeeded on the same visible three-card reward screen. The game-written status file reported `visible_card_reward_option_count: 3`, identity read/direct/serialized counts of 3, and mapping counts of 2 known and 1 unknown. It remained `screen_type: "exporter_status"` and did not export raw STS2 IDs, Deckseer IDs, card names, selected-card identity, deck, HP, gold, relics, potions, save/profile data, OCR, watch mode, input automation, or recommendation-ready run state. The repo-local exporter build passed with 0 warnings and 0 errors. `inspect-export` accepts `tests/fixtures/exporter_status_v028_reward_screen_identity_runtime_state.json`, and focused exporter-state tests pass.

## Recommended Next Packet

Do not proceed directly to recommendation-ready live export yet. `docs/EXPORTER_CARD_REWARD_ID_REVEAL_CONTRACT.md` defines the accepted ADR 3 status-only ID reveal diagnostic, installed as `v0.2.9` after explicit approval. Visible-screen and clear-state verification pass: the observed public model IDs were `CLOAK_AND_DAGGER`, `BOUNCING_FLASK`, and `INFINITE_BLADES`, all mapped to reviewed Deckseer IDs while the file remained `exporter_status`, then cleared after reward skip.

Acceptance:

- the exporter still writes only `screen_type: "exporter_status"`
- no raw STS2 card IDs or Deckseer IDs are exported
- the mapping review explains how to audit unknowns without guessing from localized names
- no scoring, priors, empirical data, recommendation behavior, watch mode, OCR, input automation, or game-file modification changes are added

The `v0.2.9` visible-screen and clear-state checks are complete. Stop before any exporter writes `screen_type: "card_reward"` unless a later packet explicitly approves recommendation-ready export.
