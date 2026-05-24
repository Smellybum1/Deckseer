# Deckseer Exporter Static Mod Spike

Status: `accepted`

Checked on 2026-05-24 against local Slay the Spire 2 `public-beta`, game version `v0.106.1`, build `23372702`.

## Result

The first in-game Deckseer Exporter spike is implemented and locally verified. The game loads one local mod, `DeckseerExporter`, and the mod writes:

```text
%LOCALAPPDATA%\Deckseer\exports\latest_state.json
```

The written file uses only the static status contract:

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
    "requires_user_confirmation": false,
    "confidence": "high",
    "caveats": [
      "Static exporter status only; no live run state is present.",
      "Game patch/build metadata is not exported in the first static spike."
    ]
  }
}
```

Acceptance command:

```powershell
deckseer inspect-export "$env:LOCALAPPDATA\Deckseer\exports\latest_state.json"
```

Observed acceptance result:

- `valid: true`
- `screen_type: "exporter_status"`
- `source: "deckseer_exporter_mod"`
- `exporter_version: "0.1.0"`
- `status: "ok"`

## Implementation Notes

Source lives under `exporter_mod/DeckseerExporter`.

The mod was generated from `Alchyr.Sts2.Templates` and then narrowed for Deckseer:

- removed BaseLib dependency from the manifest and project references
- removed Harmony patching from the initializer
- set `affects_gameplay: false`
- set `has_pck: false` and `has_dll: true`
- writes through a temporary file before replacing `latest_state.json`

Local build/install requires:

- `.NET SDK 9`
- Godot/Megadot 4.5.1-compatible executable
- visible STS2 install at `D:\Games\Steam\steamapps\common\Slay the Spire 2`
- installed `Alchyr.Sts2.Templates`, verified by `dotnet new list alchyrsts2mod`

The template targets `net9.0`, matching the installed game's `sts2.runtimeconfig.json`.

## Safety Boundary

Implemented:

- writes static exporter health JSON only
- creates `%LOCALAPPDATA%\Deckseer\exports\` only when the mod loads
- installs only the mod package files under the STS2 `mods/DeckseerExporter` folder

Still forbidden:

- live run-state export
- card reward export
- relic reward export
- OCR or screenshot reading
- save/profile modification
- gameplay automation or input control
- memory/process tricks, packet inspection, stealth, or evasion
- Deckseer scoring, prior, empirical, or recommendation changes

## Next Packet

The next exporter packet should be a design/readiness pass for card reward export from safe normal mod-accessible APIs. It should identify the exact game APIs for visible screen type, character, act/floor, HP, gold, deck, relics, potions, and current reward choices before exporting any live run state.
