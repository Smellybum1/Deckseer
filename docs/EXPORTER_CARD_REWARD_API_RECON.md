# Deckseer Exporter Card Reward API Recon

Status: `recon_complete`

Checked on 2026-05-24 against the local Slay the Spire 2 `public-beta`, game version `v0.106.1`, build `23372702`.

## Scope

This packet identifies likely safe, normal mod-accessible APIs for future visible card reward export. It does not implement live run-state export.

The accepted exporter safety boundary still applies:

- no gameplay automation or input control
- no memory/process tricks, packet inspection, stealth, or evasion
- no OCR, screenshots, or watch mode
- no save/profile modification
- no Deckseer scoring, prior, empirical, or recommendation changes
- no live card, relic, deck, potion, HP, gold, or map export in this packet

## Evidence Source

The recon used the local STS2 assembly metadata only:

```powershell
dotnet run --project tools\sts2_metadata_probe -- "D:\Games\Steam\steamapps\common\Slay the Spire 2\data_sts2_windows_x86_64\sts2.dll" "<regex>"
```

The probe reads `sts2.dll` with `System.Reflection.Metadata` and does not load or execute game code. It exists to make future patch-sensitive API reviews repeatable before changing the in-game mod.

Important limitation: metadata confirms type and member names, but not enough behavioral detail to start exporting live state. The next packet should compile against the candidate APIs and, if needed, log only diagnostic availability.

## Confirmed Candidate Surfaces

### Reward Models

Likely primary path:

- `MegaCrit.Sts2.Core.Rewards.RewardsSet`
  - `Player`
  - `Rewards`
  - `AllRewardsSuccessfullySelected`
  - `GenerateRewardsFor`
  - `Offer`
- `MegaCrit.Sts2.Core.Rewards.Reward`
  - `Player`
  - `RewardType`
  - `Description`
  - `IsPopulated`
  - `SuccessfullySelected`
  - `ParentRewardSet`
  - `ToSerializable`
- `MegaCrit.Sts2.Core.Rewards.CardReward`
  - `Cards`
  - `Options`
  - `RerollOptions`
  - `CanSkip`
  - `CanReroll`
  - `IsPopulated`
  - `AfterGenerated`
  - `ToSerializable`

This is the most promising export source because `CardReward` appears to carry the generated visible choices directly.

### Reward Screens And Nodes

Useful screen-observation path:

- `MegaCrit.Sts2.Core.Nodes.Screens.NRewardsScreen`
  - `_runState`
  - `_rewardsSet`
  - `_rewardButtons`
  - `ScreenType`
  - `RewardCollectedFrom`
  - `RewardSkippedFrom`
- `MegaCrit.Sts2.Core.Nodes.Rewards.NRewardButton`
  - `Reward`
  - `SetReward`
  - `GetReward`
- `MegaCrit.Sts2.Core.Nodes.Rewards.NLinkedRewardSet`
  - `LinkedRewardSet`
  - `SetReward`
  - `GetReward`
- `MegaCrit.Sts2.Core.Nodes.Screens.CardSelection.NCardRewardSelectionScreen`
  - `_options`
  - `_extraOptions`
  - `ShowScreen`
  - `RefreshOptions`
  - `SelectCard`

This path may be useful to verify that a reward is currently visible, but it includes private fields. Avoid relying on private-field reflection for live export unless a later packet explicitly accepts that maintenance risk.

### Run State And Save-Like Data

Likely context source:

- `MegaCrit.Sts2.Core.Runs.RunManager`
  - `Instance`
  - `State`
  - `IsInProgress`
  - `RewardsSetSynchronizer`
  - `RunStarted`, `RoomEntered`, `RoomExited`, `ActEntered`
  - `ToSave`
- `MegaCrit.Sts2.Core.Runs.IRunState`
  - `ActFloor`
  - `TotalFloor`
  - `AscensionLevel`
  - `CurrentRoom`
  - `CurrentMapPoint`
  - `CurrentMapPointHistoryEntry`
  - `ContainsCard`
  - `LoadCard`
- `MegaCrit.Sts2.Core.Runs.RunState`
  - `Players`
  - `ActFloor`
  - `TotalFloor`
  - `AscensionLevel`

Likely Deckseer mapping helpers:

- `MegaCrit.Sts2.Core.Saves.SerializableRun`
  - `Players`
  - `Ascension`
  - `CurrentActIndex`
  - `FloorReached`
- `MegaCrit.Sts2.Core.Saves.Runs.SerializablePlayer`
  - `CharacterId`
  - `CurrentHp`
  - `MaxHp`
  - `Gold`
  - `Deck`
  - `Relics`
  - `Potions`
- `MegaCrit.Sts2.Core.Saves.Runs.SerializableCard`
  - `Id`
  - `CurrentUpgradeLevel`
  - `FloorAddedToDeck`
- `MegaCrit.Sts2.Core.Saves.Runs.SerializableRelic`
  - `Id`
  - `FloorAddedToDeck`
- `MegaCrit.Sts2.Core.Saves.Runs.SerializablePotion`
  - `Id`
  - `SlotIndex`
- `MegaCrit.Sts2.Core.Saves.Runs.SerializableReward`
  - `RewardType`
  - `PredeterminedModelId`
  - `SpecialCard`
  - `CardPoolIds`
  - `OptionCount`

These save-like structures are attractive because their property names already match Deckseer's manual JSON needs. The next packet should verify whether `RunManager.ToSave()` or related serializers can be called safely from the exporter without changing game state.

### Hook And Modding Surfaces

Potential observation hooks:

- `MegaCrit.Sts2.Core.Modding.ModHelper`
  - `SubscribeForRunStateHooks`
  - `SubscribeForCombatStateHooks`
  - `IterateAllRunStateSubscribers`
- `MegaCrit.Sts2.Core.Hooks.Hook`
  - `AfterModifyingCardRewardOptions`
  - `AfterModifyingRewards`
  - `AfterRewardTaken`
  - `ModifyCardRewardCreationOptions`
  - `ModifyCardRewardAlternatives`
  - `TryModifyCardRewardOptions`
  - `ShouldAllowSelectingMoreCardRewards`
- `MegaCrit.Sts2.Core.Models.AbstractModel`
  - corresponding override methods for the same hook names

Hooks with "Modify" in the name must be treated carefully. The exporter may observe data passed through a hook, but it must not mutate reward options or influence selection behavior.

## Recommended Export Strategy

The safest likely path is:

1. Use normal run-state hooks or run manager events only to know when a run or reward screen may have changed.
2. Read `RunManager.Instance.State` for run context.
3. Read visible reward data from `RewardsSet.Rewards` and `CardReward.Cards` only after verifying a card reward is currently offered.
4. Convert cards, deck, relics, and potions through public IDs from save-like serializable models.
5. Write a Deckseer `screen_type: "card_reward"` JSON file only after a later packet proves the fields compile and map cleanly.
6. Keep `requires_user_confirmation: true` for all card reward exports.

Do not use screen private fields as the first live export path. Keep them as a diagnostic fallback if public model access cannot prove visibility.

## Next Packet

Recommended next packet from this recon was **Exporter Card Reward Compile Probe**. That follow-up is now complete; see `docs/EXPORTER_CARD_REWARD_COMPILE_PROBE.md`.

Acceptance criteria:

- Build-only or diagnostic-only C# changes in the exporter mod.
- Compile references to candidate types and public properties.
- If runtime diagnostics are added, write only static/status-style metadata such as available API names and caveats, not live card choices or run state.
- No card reward export contract is emitted yet.
- The existing `screen_type: "exporter_status"` file remains valid.
- `dotnet build` passes and Deckseer health checks remain green.

Stop before implementing live card reward export if:

- the only viable reward source requires private-field reflection
- hook signatures require mutating reward options
- card IDs from reward objects differ from Deckseer's catalog IDs
- calling `RunManager.ToSave()` or similar helpers appears to mutate state or perform file I/O
- multiplayer or synchronizer APIs become necessary for single-player visible reward export

## Compile Probe Follow-Up

The compile probe is now documented in `docs/EXPORTER_CARD_REWARD_COMPILE_PROBE.md`. It confirmed that several metadata-visible members are not normal public C# API:

- `RunManager.State`
- `Reward.RewardType`
- `CardReward.Options`
- `NRewardButton.GetReward`

Future exporter work should prefer the public symbols that compiled cleanly and avoid private/publicizer/reflection workarounds unless explicitly approved in a later packet.

## Verification Commands

```powershell
dotnet run --project tools\sts2_metadata_probe -- "D:\Games\Steam\steamapps\common\Slay the Spire 2\data_sts2_windows_x86_64\sts2.dll" "CardReward|RewardsSet|NRewardsScreen|RunManager|SerializablePlayer"
dotnet build exporter_mod\DeckseerExporter\DeckseerExporter.csproj "/p:Sts2Path=D:/Games/Steam/steamapps/common/Slay the Spire 2" "/p:ModsPath=D:/Codex/Deckseer/exporter_mod/local_mods/" "/p:GodotPath=D:/Codex/Godot/Godot_v4.5.1-stable_mono_win64.exe"
deckseer inspect-export "$env:LOCALAPPDATA\Deckseer\exports\latest_state.json"
```
