# Deckseer Exporter Toolchain Setup

This checklist prepares the local Windows machine for the future Deckseer Exporter static mod spike. It is repo-only documentation: do not add mod source, build files, generated template output, dependencies, live capture, or watch mode as part of this packet.

## Current Status

Checked on 2026-05-24.

Deckseer can already inspect `screen_type: "exporter_status"` fixture files, and the local Slay the Spire 2 install was found:

- STS2 install: `D:\Games\Steam\steamapps\common\Slay the Spire 2`
- Steam manifest: `D:\Games\Steam\steamapps\appmanifest_2868840.acf`
- Steam branch/config: `public-beta`
- Game version: `v0.106.1`
- Steam build ID: `23372702`
- Release commit: `d3584805`

The static status mod spike is no longer blocked. The local toolchain is now visible:

- `.NET SDK 9.0.314` is installed and supports the STS2 template's `net9.0` target.
- `.NET SDK 8.0.421` is also installed.
- `dotnet new list alchyrsts2mod` reports the `Empty Slay the Spire 2 Mod` template.
- `godot` is available through `D:\Codex\Godot\godot.cmd`.
- `megadot` is not available on PATH.

The accepted static spike is documented in `docs/EXPORTER_STATIC_MOD_SPIKE.md`.

## Required External Tools

Install or expose these tools before adding any mod source:

1. `.NET SDK`
   - Required so `dotnet new`, template install/list, restore, and build commands work.
   - The currently installed .NET host is not enough.
2. Megadot or matching Godot
   - The public STS2 template setup recommends the latest Megadot, or Godot of the same version as the latest Megadot release.
   - Prefer Megadot when available because it is the STS2-specific Godot distribution referenced by the template setup.
3. `Alchyr.Sts2.Templates`
   - Required for the community template path.
   - Install only after the .NET SDK is visible to `dotnet`.

Do not install tools from inside this repo packet. Installation should be an explicit local-machine setup step.

## Verification Commands

Deckseer now has a read-only wrapper for the local checks below:

```powershell
deckseer exporter-toolchain-preflight --format text
```

The preflight checks `PATH` for `megadot` or `godot`, then falls back to the known local Godot paths under `D:\Codex\Godot`. It does not install tools or create folders.

Expected ready state after toolchain setup:

- Status: `ready_for_static_spike`.
- Blockers: none.
- Warnings: none after the accepted static spike has created the local mod and export folders.

Run these commands after setup. They should be read-only except for whatever the external installer or template install already did.

Check .NET SDK visibility:

```powershell
dotnet --info
```

Expected ready state:

- Output includes at least one entry under `.NET SDKs installed`.
- Output no longer says `No SDKs were found.`

Check template visibility by the installed template short name:

```powershell
dotnet new list alchyrsts2mod
```

Expected ready state:

- Command exits successfully.
- Output lists `Empty Slay the Spire 2 Mod` with short name `alchyrsts2mod`.

If templates are not installed yet, install them after SDK readiness:

```powershell
dotnet new install Alchyr.Sts2.Templates
dotnet new list alchyrsts2mod
```

Check Megadot/Godot visibility:

```powershell
Get-Command megadot -ErrorAction SilentlyContinue | Select-Object Source,Version
Get-Command godot -ErrorAction SilentlyContinue | Select-Object Source,Version
```

Expected ready state:

- At least one command reports an executable path.
- If neither command is on PATH, record the absolute executable path before creating a future mod project.

Check local STS2 install metadata:

```powershell
Get-Content -LiteralPath 'D:\Games\Steam\steamapps\common\Slay the Spire 2\release_info.json'
```

Expected current state:

- `version`: `v0.106.1`
- `branch`: `v0.106.1`
- `commit`: `d3584805`

Check expected mod folder:

```powershell
Test-Path -LiteralPath 'D:\Games\Steam\steamapps\common\Slay the Spire 2\mods'
```

Expected current state:

- `True` is expected after the accepted static spike.
- The folder should contain only approved local mod package files.

Check expected Deckseer export folder:

```powershell
Test-Path -LiteralPath "$env:LOCALAPPDATA\Deckseer\exports"
```

Expected current state:

- `True` is expected after the accepted static spike has loaded once.
- The folder should contain the user-visible `latest_state.json` export.

## Future Mod Project Values

The accepted static mod spike uses these local values:

- Project/mod ID: `DeckseerExporter`
- STS2 install path: `D:\Games\Steam\steamapps\common\Slay the Spire 2`
- `Directory.Build.props` game path value: `D:\Games\Steam\steamapps\common\Slay the Spire 2`
- Mods folder: `D:\Games\Steam\steamapps\common\Slay the Spire 2\mods`
- Mod package folder: `D:\Games\Steam\steamapps\common\Slay the Spire 2\mods\DeckseerExporter`
- Export file: `%LOCALAPPDATA%\Deckseer\exports\latest_state.json`
- Manifest intent: `affects_gameplay: false`
- First export only: `screen_type: "exporter_status"`

The accepted static spike writes only this contract shape:

```json
{
  "game": "slay_the_spire_2",
  "screen_type": "exporter_status",
  "status": "ok",
  "export_metadata": {
    "source": "deckseer_exporter_mod",
    "exporter_version": "0.1.0",
    "game_build": "23372702",
    "game_patch": "v0.106.1",
    "exported_at": "2026-05-24T00:00:00Z",
    "requires_user_confirmation": false,
    "confidence": "high",
    "caveats": [
      "Static exporter status only; no live run state is present."
    ]
  }
}
```

Validate it with:

```powershell
deckseer inspect-export "$env:LOCALAPPDATA\Deckseer\exports\latest_state.json"
```

## Public Reference Snapshot

Reviewed on 2026-05-24. Treat these details as volatile while Slay the Spire 2 is in Early Access.

- Steam news feed: <https://steamcommunity.com/app/2868840/allnews/?l=english>. Current public news shows active beta/main patching and notes that Steam Workshop support is still planned.
- ModTemplate-StS2: <https://github.com/Alchyr/ModTemplate-StS2>.
- Modding Basics: <https://github-wiki-see.page/m/Alchyr/ModTemplate-StS2/wiki/Modding-Basics>. Current docs describe Windows/Linux mods as files under the STS2 install-local `mods` directory, and list manifest fields including `has_pck`, `has_dll`, `min_game_version`, `dependencies`, and `affects_gameplay`.
- Setup: <https://github-wiki-see.page/m/Alchyr/ModTemplate-StS2/wiki/Setup>. Current docs require a C# IDE, .NET SDK, Megadot or matching Godot, and the STS2 templates. They also note that a project can remove the BaseLib package reference if it does not use BaseLib classes.

## Safety Boundary

Allowed after setup:

- Create the smallest local `DeckseerExporter` mod package.
- Write a user-visible static status JSON file under `%LOCALAPPDATA%\Deckseer\exports\`.
- Read only normal mod-accessible metadata needed for exporter version, game build, and game patch caveats.
- Read game logs for troubleshooting after the user launches the game.

Forbidden:

- Gameplay automation or input control.
- Memory reading outside normal mod-accessible game state.
- Process injection, packet inspection, stealth, evasion, or anti-cheat bypass.
- Live run-state export, card reward export, OCR, screenshots, save modification, profile modification, or watcher mode.
- Scoring, prior, empirical, or recommendation behavior changes in Deckseer.
