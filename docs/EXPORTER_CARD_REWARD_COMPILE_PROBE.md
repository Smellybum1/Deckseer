# Deckseer Exporter Card Reward Compile Probe

Status: `build_verified`

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

The build above writes only to the repo-local ignored `exporter_mod/local_mods/` package target. Installing this diagnostic build into the live STS2 `mods` folder remains a separate manual step because it modifies the local game install.

## Exporter Status Output

The source mod version is now `v0.2.0`. When this build is installed and loaded, it still writes only:

```json
{
  "game": "slay_the_spire_2",
  "screen_type": "exporter_status",
  "status": "ok"
}
```

The `export_metadata` block also includes diagnostic fields:

- `diagnostics.card_reward_api_probe: "compiled"`
- `diagnostics.verified_symbol_count`
- `diagnostics.verified_symbols`

These fields are status metadata only. They are not a card reward export and must not be treated as live run state.

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

## Next Packet

Recommended next packet: **Exporter Status Diagnostic Install Check** or **Card Reward Visibility Design**.

Use the install check if the immediate goal is to verify the `v0.2.0` diagnostic metadata in the real game-written `latest_state.json`. That requires explicit approval to write the updated mod package into the local STS2 `mods` folder.

Use the visibility design packet if staying repo-only. It should decide how to prove that `RewardsSet.Rewards` and `CardReward.Cards` correspond to the visible card reward screen without private-field reflection or gameplay mutation.
