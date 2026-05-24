# Deckseer Exporter Mod

This folder contains the first Slay the Spire 2 companion mod spike for Deckseer.

The current mod is intentionally static and harmless:

- writes `%LOCALAPPDATA%\Deckseer\exports\latest_state.json`
- exports only `screen_type: "exporter_status"`
- does not read live run state, deck state, rewards, relics, potions, HP, gold, input, memory, screenshots, saves, or profiles
- does not automate gameplay or control the game
- sets `affects_gameplay: false`

## Local Build

Build from the repository root:

```powershell
dotnet build exporter_mod\DeckseerExporter\DeckseerExporter.csproj "/p:Sts2Path=D:/Games/Steam/steamapps/common/Slay the Spire 2" "/p:ModsPath=D:/Codex/Deckseer/exporter_mod/local_mods/" "/p:GodotPath=D:/Codex/Godot/Godot_v4.5.1-stable_mono_win64.exe"
```

`exporter_mod/local_mods/` is ignored by git and is only a local build target.

## Local Install

Install the static mod package into the local game install:

```powershell
dotnet build exporter_mod\DeckseerExporter\DeckseerExporter.csproj "/p:Sts2Path=D:/Games/Steam/steamapps/common/Slay the Spire 2" "/p:ModsPath=D:/Games/Steam/steamapps/common/Slay the Spire 2/mods/" "/p:GodotPath=D:/Codex/Godot/Godot_v4.5.1-stable_mono_win64.exe"
```

Launch Slay the Spire 2 from Steam, accept the game's **Load Mods** prompt for the local `DeckseerExporter` mod, and relaunch if the game asks.

## Acceptance Check

After the game reports that it is running modded with one loaded mod:

```powershell
deckseer inspect-export "$env:LOCALAPPDATA\Deckseer\exports\latest_state.json"
```

The expected result is `valid: true`, `screen_type: "exporter_status"`, and `status: "ok"`.
