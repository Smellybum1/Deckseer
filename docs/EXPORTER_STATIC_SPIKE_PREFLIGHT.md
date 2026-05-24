# Deckseer Exporter Static Spike Preflight

This preflight checks whether the next Deckseer Exporter packet can safely attempt a static Slay the Spire 2 mod that writes only `screen_type: "exporter_status"` JSON. It does not add mod source, build scripts, dependencies, live capture, or watcher behavior.

See `docs/EXPORTER_TOOLCHAIN_SETUP.md` for the repo-only setup checklist that must pass before adding static mod source.

## Readiness Result

Status: `blocked_missing_toolchain`

The local Slay the Spire 2 install was found and its current build metadata is readable, but the static mod spike should not start yet because the required C# modding toolchain is incomplete:

- `.NET` host/runtime is installed, but `dotnet --info` reports no installed SDKs.
- `dotnet new list Alchyr.Sts2.Templates` cannot run because no SDK is available.
- `godot` is not available on PATH.
- `megadot` is not available on PATH.

Secondary check still needed after toolchain setup: confirm the log directory is readable after a fresh game launch, because the app data root denied directory listing during this preflight.

## Local Game Findings

Checked on 2026-05-24.

Common paths checked first:

- `C:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2`: not found.
- `D:\SteamLibrary\steamapps\common\Slay the Spire 2`: not found.
- `D:\Slay the Spire 2`: not found.
- `D:\Slay the Spire`: exists, but contains notes/images, not the game install.

Steam registry metadata located the actual Steam install:

- Steam install: `D:\Games\Steam`
- Steam library file: `D:\Games\Steam\steamapps\libraryfolders.vdf`
- STS2 manifest: `D:\Games\Steam\steamapps\appmanifest_2868840.acf`
- STS2 install: `D:\Games\Steam\steamapps\common\Slay the Spire 2`

Steam manifest findings:

- App ID: `2868840`
- App name: `Slay the Spire 2`
- Install dir: `Slay the Spire 2`
- Build ID: `23372702`
- Branch/config: `public-beta`
- Last owner: `76561198030888875`

Install metadata from `release_info.json`:

- Version: `v0.106.1`
- Branch: `v0.106.1`
- Commit: `d3584805`
- Date: `2026-05-22T17:01:28-07:00`
- Main assembly hash: `1243315044`

The install root contains `SlayTheSpire2.exe`, `SlayTheSpire2.pck`, `release_info.json`, and `data_sts2_windows_x86_64`. The data directory includes C# runtime/modding-adjacent assemblies such as `GodotSharp.dll`, `0Harmony.dll`, `MonoMod.*`, and .NET host components, which is consistent with the public C# / Godot-style modding surface.

## Local Folder Findings

Expected mod target:

- `D:\Games\Steam\steamapps\common\Slay the Spire 2\mods`
- Current state: not present.

Expected Deckseer export target:

- `C:\Users\moxhe\AppData\Local\Deckseer\exports`
- Current state: not present.

Expected log target:

- `C:\Users\moxhe\AppData\Roaming\SlayTheSpire2\logs`
- Current state: path exists according to `Test-Path`, but listing the app data root returned access denied and direct log enumeration did not produce readable log entries in this preflight.

The static spike may create its own mod package and export directory in a later code-bearing packet, but this preflight intentionally did not create either folder.

## Public Reference Snapshot

Reviewed on 2026-05-24. Treat these details as volatile while STS2 is in Early Access.

- Steam news feed: <https://steamcommunity.com/app/2868840/allnews/?l=english>. Current public news shows active main/beta patching and notes that Steam Workshop support is still planned.
- STS2 patch notes / modding notes: <https://slaythespire.wiki.gg/wiki/Slay_the_Spire_2%3APatch_Notes>. Current patch context includes beta patching through `v0.106.x`.
- ModTemplate-StS2: <https://github.com/Alchyr/ModTemplate-StS2>.
- Modding Basics: <https://github-wiki-see.page/m/Alchyr/ModTemplate-StS2/wiki/Modding-Basics>. The template docs describe mod packages as colocated `.json`, `.dll`, and optional `.pck` files under a `mods` directory, with manifest fields including `id`, `has_pck`, `has_dll`, `min_game_version`, `dependencies`, and `affects_gameplay`.
- Setup: <https://github-wiki-see.page/m/Alchyr/ModTemplate-StS2/wiki/Setup>. The setup docs require a C# IDE, .NET SDK, Godot/Megadot, and the StS2 template; they also note that a project can remove the BaseLib package reference if it does not use BaseLib classes.

## Next Actions Before Mod Source

1. Install or expose a supported `.NET SDK` on PATH, then confirm `dotnet --info` lists at least one SDK.
2. Install or expose the current Megadot/Godot executable on PATH, or document its absolute path before adding a project file.
3. Install or verify `Alchyr.Sts2.Templates` with `dotnet new list Alchyr.Sts2.Templates`.
4. Decide whether the static status mod can avoid BaseLib; if it can, keep the first spike dependency-free.
5. After toolchain readiness, create only the smallest `DeckseerExporter` mod package needed to write:

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

Acceptance command for the later static spike:

```bash
deckseer inspect-export "%LOCALAPPDATA%\Deckseer\exports\latest_state.json"
```

## Safety Boundary

Allowed in the later static spike:

- Create a local mod package under the STS2 `mods` directory.
- Write a user-visible Deckseer JSON file under `%LOCALAPPDATA%\Deckseer\exports\`.
- Read only normal mod-accessible metadata needed for exporter version, game build, and game patch caveats.
- Read game logs for troubleshooting after the user launches the game.

Forbidden:

- Gameplay automation or input control.
- Memory reading outside normal mod-accessible game state.
- Process injection, packet inspection, stealth, evasion, or anti-cheat bypass.
- Live run-state export, card reward export, OCR, screenshots, save modification, profile modification, or watcher mode.
- Scoring, prior, empirical, or recommendation behavior changes in Deckseer.
