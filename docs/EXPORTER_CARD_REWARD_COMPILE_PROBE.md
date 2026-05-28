# Deckseer Exporter Card Reward Compile Probe

Status: `installed_status_verified`

Checked on 2026-05-24 against the local Slay the Spire 2 `public-beta`, game version `v0.106.1`, build `23372702`.

## Result

The exporter mod now contains a diagnostic-only compile probe for card reward export APIs:

```text
exporter_mod/DeckseerExporter/DeckseerExporterCode/CardRewardApiProbe.cs
```

The probe references candidate STS2 reward, run-state, save-like, screen, and hook symbols at compile time. It does not read live run state, visible card rewards, deck contents, relics, potions, HP, gold, map state, saves, screenshots, input, process memory, or network traffic.

The local build target passes:

```powershell
dotnet build exporter_mod\DeckseerExporter\DeckseerExporter.csproj "/p:Sts2Path=D:/Games/Steam/steamapps/common/Slay the Spire 2" "/p:ModsPath=D:/Codex/Deckseer/exporter_mod/local_mods/" "/p:GodotPath=D:/Codex/Godot/Godot_v4.5.1-stable_mono_win64.exe"
```

Observed result:

- `Build succeeded`
- `0 Warning(s)`
- `0 Error(s)`

The build above writes only to the repo-local ignored `exporter_mod/local_mods/` package target. Installing this diagnostic build into the live STS2 `mods` folder was verified separately after explicit approval.

## Exporter Status Output

The original compile-probe source version was `v0.2.1`; current installed exporter work has advanced to `v0.2.8`. All builds in this sequence still write only:

```json
{
  "game": "slay_the_spire_2",
  "screen_type": "exporter_status",
  "status": "ok"
}
```

The `export_metadata` block includes status-only diagnostic fields, depending on the installed version:

- `diagnostics.card_reward_api_probe: "compiled"`
- `diagnostics.verified_symbol_count`
- `diagnostics.verified_symbols`
- `diagnostics.hook_model_compile_probe: "compiled_not_registered"`
- `diagnostics.hook_model_verified_symbol_count`
- `diagnostics.hook_model_verified_symbols`
- screen observation counts
- ID-shape known/unknown counts

These fields are status metadata only. They are not a card reward export and must not be treated as live run state.

## Install Check Result

The `v0.2.0` diagnostic status build was installed into the local STS2 `mods/DeckseerExporter` package after explicit approval. The first install attempt failed because `SlayTheSpire2.exe` had the existing DLL locked. After closing the game, the install build succeeded with 0 warnings and 0 errors.

After launching STS2 once, the game-written export passed:

```powershell
python -m deckseer.cli inspect-export "$env:LOCALAPPDATA\Deckseer\exports\latest_state.json"
```

Observed acceptance result:

- `valid: true`
- `screen_type: "exporter_status"`
- `exporter_version: "0.2.0"`
- `status: "ok"`
- `diagnostics.card_reward_api_probe: "compiled"`
- `diagnostics.verified_symbol_count: 44`
- `diagnostics.verified_symbols` includes `RewardsSet.Rewards` and `CardReward.Cards`

The game-written file still exports no live card reward, relic reward, deck, HP, gold, save, screenshot, input, or process state. The newer `v0.2.1` source build has not been installed into the real STS2 mods folder.

## Public Symbols That Compile

The compile probe confirmed these categories are available from normal C# source:

- Run manager basics:
  - `RunManager.Instance`
  - `RunManager.IsInProgress`
  - `RunManager.ToSave`
- Run-state context:
  - `IRunState.ActFloor`
  - `IRunState.TotalFloor`
  - `IRunState.AscensionLevel`
  - `RunState.Players`
- Reward models:
  - `RewardsSet.Player`
  - `RewardsSet.Rewards`
  - `RewardsSet.AllRewardsSuccessfullySelected`
  - `Reward.Player`
  - `Reward.Description`
  - `Reward.IsPopulated`
  - `Reward.ParentRewardSet`
  - `CardReward.Cards`
  - `CardReward.CanSkip`
  - `CardReward.CanReroll`
  - `CardReward.IsPopulated`
  - `CardReward.ToSerializable`
- Save-like mapping helpers:
  - `SerializableRun.Players`
  - `SerializableRun.Ascension`
  - `SerializableRun.FloorReached`
  - `SerializablePlayer.CharacterId`
  - `SerializablePlayer.CurrentHp`
  - `SerializablePlayer.MaxHp`
  - `SerializablePlayer.Gold`
  - `SerializablePlayer.Deck`
  - `SerializablePlayer.Relics`
  - `SerializablePlayer.Potions`
  - `SerializableCard.Id`
  - `SerializableCard.CurrentUpgradeLevel`
  - `SerializableRelic.Id`
  - `SerializablePotion.Id`
  - `SerializableReward.RewardType`
  - `SerializableReward.OptionCount`
- Screen and hook names:
  - `NRewardsScreen.ScreenType`
  - `NRewardButton.Reward`
  - `NLinkedRewardSet.LinkedRewardSet`
  - `NCardRewardSelectionScreen.ScreenType`
  - `NChooseACardSelectionScreen.ScreenType`
  - `ModHelper.SubscribeForRunStateHooks`
  - `Hook.AfterModifyingCardRewardOptions`
  - `Hook.AfterModifyingRewards`
  - `Hook.AfterRewardTaken`

## Metadata-Visible But Not Public Enough

The recon metadata showed several members that did not compile from normal mod source:

- `RunManager.State`
- `Reward.RewardType`
- `CardReward.Options`
- `NRewardButton.GetReward`

This matters: future live export should prefer the symbols above that actually compile. Do not use private/publicizer/reflection workarounds for these members unless a later packet explicitly accepts the maintenance and safety risk.

## Safety Boundary

Still forbidden:

- live card reward export
- live relic reward export
- deck, HP, gold, map, save, or profile export
- gameplay automation or input control
- OCR or screenshot reading
- memory/process tricks, packet inspection, stealth, or evasion
- Deckseer scoring, prior, empirical, or recommendation changes

## Hook-Model Compile Probe Result

Repo-only metadata research and the follow-up compile probe have been recorded in `docs/EXPORTER_CARD_REWARD_VISIBILITY_DESIGN.md`. The important result is that run hook subscriptions return `IEnumerable<AbstractModel>`, while a hook-only custom listener can compile as a `SingletonModel` subclass registered and retrieved through engine-owned `ModelDb` lifecycle APIs.

The compile-only `v0.2.1` probe proves this public path:

- `DeckseerHookCompileProbeModel : SingletonModel`
- `ModelDb.Contains(typeof(DeckseerHookCompileProbeModel))`
- `ModelDb.Inject(typeof(DeckseerHookCompileProbeModel))`
- `ModelDb.Singleton<DeckseerHookCompileProbeModel>()`
- `ModHelper.SubscribeForRunStateHooks(MainFile.ModId, CompileOnlyGetRunHookModels)`

The probe is dormant. `MainFile.Initialize()` does not call `CompileOnlyRegisterRunHook()`, so no run hook is registered and no live reward state is observed. Do not retry direct construction of a custom `AbstractModel` subclass. `ModelDb.Get<T>()` and `ModelDb.Get(Type)` are metadata-visible but not public enough for normal mod source in this project configuration.

Adapter coverage now includes `tests/fixtures/exporter_status_v021_state.json`, which verifies that `inspect-export` accepts the `v0.2.1` status-only diagnostic payload and preserves the card reward and hook-model diagnostics as metadata without treating them as recommendation input.

The follow-up public screen observation diagnostics are documented in `docs/EXPORTER_CARD_REWARD_VISIBILITY_DESIGN.md`. The installed `v0.2.2` probe registered safely but did not observe the tested visible two-card reward screen through `NRewardsScreen.ShowScreen(...)`. Installed `v0.2.3` observes `NChooseACardSelectionScreen.ShowScreen(...)` and reported two card choices on the tested visible two-card reward screen. Installed `v0.2.4` clears those counts through public `NChooseACardSelectionScreen._ExitTree()` after the screen closes. Fixtures `tests/fixtures/exporter_status_v022_screen_observation_state.json`, `tests/fixtures/exporter_status_v023_card_choice_screen_state.json`, and `tests/fixtures/exporter_status_v024_card_choice_closed_state.json` verify that these diagnostics remain `exporter_status` metadata rather than recommendation input.

## Card Identity Compile Probe Result

Repo-local `v0.2.5` adds `CardIdentityCompileProbe` and keeps the exporter status-only. It proves normal mod source can compile this public path:

- `CardModel.Id`
- `CardModel.CurrentUpgradeLevel`
- `CardModel.IsUpgraded`
- `CardModel.ToSerializable()`
- `CardCreationResult.Card`
- `SerializableCard.Id`
- `SerializableCard.CurrentUpgradeLevel`

The first build showed `SerializableCard.Id` may be nullable, so the probe records that path as nullable and treats direct `CardModel.Id` as the primary model ID path. The final repo-local build passed with 0 warnings and 0 errors.

The status metadata reports `card_identity_mapping_probe: "compiled_not_exported"` and verified symbol names only. It does not export live card IDs, selected-card identity, deck, HP, gold, relics, potions, save data, OCR, watch mode, input automation, or recommendation-ready run state. `tests/fixtures/exporter_status_v025_card_identity_probe_state.json` verifies that `inspect-export` preserves the diagnostic metadata without treating it as recommendation input.

## Card Identity Contract Hardening Result

Completed repo-local on 2026-05-24. Adapter fixtures and tests now cover:

- unknown exported reward IDs require `--confirmed` first, then fail with missing card data
- upgraded deck cards are preserved by the current schema
- metadata caveats remain visible through `inspect-export`
- object-shaped upgraded reward cards are rejected until a later approved reward-upgrade schema exists

The focused exporter-state suite passed with 28 tests. This did not install a mod package, export live IDs, change scoring, change recommendation behavior, or alter card data.

## Card Identity Runtime Diagnostic Result

Repo-local `v0.2.6` added a status-only runtime diagnostic for the already-proven public card-choice screen path, and repo-local `v0.2.8` extends that same status-only diagnostic to the public `CardReward.Cards` models received through `NRewardsScreen.ShowScreen(RewardsSet, ...)`. It still writes only `screen_type: "exporter_status"` and exports no raw STS2 IDs, Deckseer IDs, card names, selected-card identity, deck, HP, gold, relics, potions, save/profile data, OCR, watch mode, input automation, or recommendation-ready run state.

The diagnostic reads only public `CardModel` identity members from `NChooseACardSelectionScreen.ShowScreen(IReadOnlyList<CardModel>, Boolean)` or public `CardReward.Cards` values from `NRewardsScreen.ShowScreen(RewardsSet, ...)`, then reports counts for readable IDs, serialized IDs, nullable serialized IDs, upgraded cards, known/unknown mapping results, and duplicate normalized IDs. The repo-local build passed with 0 warnings and 0 errors. `tests/fixtures/exporter_status_v028_reward_screen_identity_runtime_state.json` verifies that `inspect-export` preserves the diagnostic metadata without treating it as recommendation input. The focused exporter-state suite now passes with 31 tests.

The `v0.2.8` live install-check succeeded after explicit approval. On a visible three-card reward screen, the game-written status file reported option/read/direct/serialized counts of 3 and mapping counts of 2 known plus 1 unknown. The payload stayed `screen_type: "exporter_status"` and did not export IDs or names.

## Active Reward Source Research Result

Completed repo-only on 2026-05-24 with `tools/sts2_metadata_probe --signatures --accessibility`; no STS2 mod package was installed and the game was not launched.

A first status-only visibility diagnostic compile attempt found that the obvious active reward stack APIs are not public to normal mod source: `RewardsSetSynchronizer.LocalPlayer` and `RewardsSetSynchronizer.GetRewardStateForPlayer(...)` do not compile, even though metadata can see them. Before another live install attempt, find a public active `RewardsSet` source or another safe proof route that does not use private fields, publicizer workarounds, custom Godot callbacks, `RunManager.ToSave()`, OCR, watch mode, input automation, or process/memory tricks.

The follow-up research found no approved active reward source under that strict boundary:

- `RewardsSetSynchronizer` owns the active reward stack, but the local-player and stack accessors are private.
- Run hook methods can modify reward generation or observe a selected reward after the decision, but do not provide a clean pre-choice active `RewardsSet`.
- `RewardsCmd` methods generate or offer rewards and are not read-only diagnostics.
- `NRewardsScreen.ShowScreen(RewardsSet, Boolean, IRunState)` receives the exact visible reward set, but observing that public method requires a patch/hook boundary decision.

## Next Packet

Recommended next packet: **Card Reward Runtime Presence Probe Install-Check**.

`docs/EXPORTER_CARD_REWARD_ID_DIAGNOSTIC_DESIGN.md` records the installed `v0.2.8` result, `docs/EXPORTER_CARD_REWARD_MAPPING_REVIEW.md` records the reviewed mapping follow-up, and accepted ADR 3 allows installed `v0.2.9` to reveal public visible-card identity strings only inside `exporter_status` mapping-review diagnostics. The visible-screen check passed and mapped `CLOAK_AND_DAGGER`, `BOUNCING_FLASK`, and `INFINITE_BLADES` to reviewed Deckseer IDs, the clear-state check emptied `card_identity_review_items` after reward skip, and `recommend-export` still rejected the live file as `exporter_status`. Do not export `screen_type: "card_reward"` or proceed to recommendation-ready live export until a later packet explicitly approves those gates.

Accepted ADR 4 and `docs/EXPORTER_CARD_REWARD_LIVE_EXPORT_DESIGN.md` define the future human-confirmed live `card_reward` boundary. Installed `v0.2.10` adds a status-only public run-state compile probe for the required recommendation fields and still writes only `screen_type: "exporter_status"`. Startup verification passes, `card_reward_live_export_writes_recommendation_state` is `false`, and `recommend-export --confirmed` rejects the live file as `exporter_status`.

`docs/EXPORTER_CARD_REWARD_RUN_STATE_SYMBOL_REVIEW.md` concludes the compiled symbols are necessary but not sufficient for live export. Repo-local `v0.2.11` implements a status-only runtime presence diagnostic that reports readiness booleans and counts without exporting live run-state values. The next safe step is an explicitly approved live install-check of that status-only diagnostic.
