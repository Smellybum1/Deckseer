# Deckseer Exporter Modding Surface Review

This review prepared the first Deckseer Exporter packet: a static, harmless Slay the Spire 2 mod spike that writes only `screen_type: "exporter_status"` JSON. That spike is now accepted; this document is not approval to export live run state yet.

See `docs/EXPORTER_STATIC_SPIKE_PREFLIGHT.md` for local Windows install, mod-folder, log-folder, and toolchain findings before attempting the static spike.
See `docs/EXPORTER_STATIC_MOD_SPIKE.md` for the accepted static mod result.
See `docs/EXPORTER_CARD_REWARD_API_RECON.md` for the current card reward API recon before attempting live reward export.

## Source Snapshot

Reviewed on 2026-05-24. Treat all STS2 modding details as volatile because the game is in Early Access and public modding support is still changing.

- Steam Slay the Spire 2 news feed: <https://steamcommunity.com/app/2868840/allnews/?l=english>. Current project updates show active beta/main branch patching and note that Steam Workshop support is still planned rather than the assumed default distribution path.
- Slay the Spire 2 patch notes / modding notes: <https://slaythespire.wiki.gg/wiki/Slay_the_Spire_2%3APatch_Notes>. Current notes include modding-related changes, including mod loading and manifest structure changes.
- Alchyr/ModTemplate-StS2 and its wiki: <https://github.com/Alchyr/ModTemplate-StS2>, <https://github-wiki-see.page/m/Alchyr/ModTemplate-StS2/wiki/Modding-Basics>, and <https://github-wiki-see.page/m/Alchyr/ModTemplate-StS2/wiki/Setup>. Current community template documentation for C# / Godot-style STS2 mods.

## Current Surface Summary

Community template documentation currently describes STS2 mods as a set of files kept together under a `mods` directory:

- `ModName.json`: manifest metadata.
- `ModName.dll`: code changes, when the mod has code.
- `ModName.pck`: text/assets, when the mod has assets.

The same documentation says Windows and Linux load mods from a `mods` directory in the Slay the Spire 2 install directory, while macOS uses an app-bundle path. This must be verified against the user's local install before writing or copying any files.

Current manifest examples include:

- stable mod `id`
- display `name`
- `author`
- `description`
- `version`
- booleans for `has_pck` and `has_dll`
- optional compatibility/dependency fields such as `min_game_version` and `dependencies`
- `affects_gameplay`

For Deckseer Exporter, `affects_gameplay` should be `false` unless local verification proves that an informational file-writing mod is treated differently. Setting this incorrectly may cause multiplayer or mod-list compatibility problems, so the static spike should avoid gameplay logic entirely.

## Likely Local Paths

These paths are starting points only:

- Game install: Steam library path ending in `steamapps/common/Slay the Spire 2/`.
- Mods folder: `steamapps/common/Slay the Spire 2/mods/`.
- Mod folder: `steamapps/common/Slay the Spire 2/mods/DeckseerExporter/`.
- Logs: community mod pages reference `%APPDATA%\SlayTheSpire2\logs`; verify this locally before relying on it.
- Deckseer output: `%LOCALAPPDATA%\Deckseer\exports\latest_state.json`.

The static spike should write only the Deckseer output file. It should not modify save files, profiles, settings, or game install files outside its own mod package.

## Required Static Output

The first spike succeeds only when Deckseer can inspect this shape:

```json
{
  "game": "slay_the_spire_2",
  "screen_type": "exporter_status",
  "status": "ok",
  "export_metadata": {
    "source": "deckseer_exporter_mod",
    "exporter_version": "0.1.0",
    "game_build": null,
    "game_patch": null,
    "exported_at": "2026-05-24T00:00:00Z",
    "requires_user_confirmation": false,
    "confidence": "high",
    "caveats": [
      "Static exporter status only; no live run state is present."
    ]
  }
}
```

Acceptance command:

```bash
deckseer inspect-export "%LOCALAPPDATA%\Deckseer\exports\latest_state.json"
```

`recommend-export` must reject this file because it is status-only and has no card reward.

## Static Spike Build Plan

The accepted static spike:

- verifies the local STS2 install and toolchain through `exporter-toolchain-preflight`
- creates the smallest local `DeckseerExporter` mod package from the current template surface
- uses an informational manifest with `affects_gameplay: false`
- writes `latest_state.json` via a temporary file plus replace/rename when the mod loads
- loads in-game as one mod and passes `deckseer inspect-export`

The static spike should not read the current run, deck, reward screen, relics, potions, HP, gold, map, save history, screen pixels, process memory, network traffic, or user input.

## Open Questions Before Code

- Which exact STS2 version/branch is installed locally: main or beta?
- Which template/runtime version matches the installed game build?
- Is BaseLib required for a no-content file-writing mod, or can the spike be dependency-free?
- Does the manifest require `id`, `has_dll`, `has_pck`, `affects_gameplay`, `min_game_version`, or dependency fields on the installed branch?
- Does the game expose a safe mod-load lifecycle hook before any run state is accessed?
- What is the actual local log path on this Windows install?
- Does the mod loader allow writing to `%LOCALAPPDATA%\Deckseer\exports\` without elevated permissions?
- Does the game require restart after adding or rebuilding a local mod?

## Safety Boundary

Allowed:

- Read normal mod-accessible metadata needed to write a static status file.
- Write user-visible Deckseer JSON under `%LOCALAPPDATA%\Deckseer\exports\`.
- Read game logs for troubleshooting after the user launches the game.

Forbidden:

- Gameplay automation, mouse input, keyboard input, controller input, or game-control hooks.
- Memory reading outside normal mod-accessible game state, process injection, packet inspection, stealth, evasion, or anti-cheat bypass.
- Live run-state export, card reward export, OCR, screenshots, save modification, profile modification, or watcher mode.
- Scoring, prior, empirical, or recommendation behavior changes in Deckseer.

## Next Handoff

The card reward API recon, compile probe, visibility diagnostics, mapping reviews, ADR 3 ID-reveal diagnostic, and ADR 4 live-export boundary are complete. Installed exporter `v0.4.7` live-proves human-confirmed mixed reward `card_reward` export after clean freshness and mapping gates, then downgrades to `exporter_status` after card reward selection closes. Watch mode, OCR, input automation, save/profile modification, and broader decision exports remain out of scope without separate approval.
