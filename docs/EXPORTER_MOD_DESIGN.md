# Deckseer Exporter Mod Design

Deckseer Exporter is a Slay the Spire 2 companion mod path that writes local JSON for Deckseer to inspect. The first in-game spike is implemented, and installed `v0.4.7` can write human-confirmed live `screen_type: "card_reward"` files after clean post-pickup freshness and mapping gates, then downgrade to `exporter_status` after the card reward selection screen closes. Installed `v0.4.0` implements the ADR 7 live `screen_type: "relic_reward"` boundary for normal reward-screen relics. Installed `v0.4.1` proves treasure chest relic observation and clear-state as status-only. Installed `v0.4.2` fixes the treasure relic identity exception but reports a null public ID. Installed `v0.4.3` uses public `RelicModel.Id` directly for that diagnostic and reveals `LETTER_OPENER` as an unmapped review-only treasure relic ID. Installed `v0.4.4` maps reviewed `letter_opener` while keeping treasure relics status-only, and installed `v0.4.6` live-proves a fully mapped treasure `relic_reward` export with post-pickup downgrade. Watch mode and broader decision exports are not implemented.

## Goals

- Export current run state through normal mod-accessible game state.
- Keep the exporter read-only and export-only.
- Preserve Deckseer's existing manual JSON card reward input as the compatibility target.
- Make exported files user-visible, inspectable, and editable before recommendation.
- Carry source metadata and caveats outside the scorer so recommendations stay deterministic.

## Non-Goals

- No gameplay automation, gameplay control, farming, or decision execution.
- No mouse input, keyboard input, controller input, or UI driving.
- No packet inspection, memory reading outside normal mod-accessible game state, process injection, stealth, evasion, or anti-cheat bypass.
- No OCR, screenshot capture, image recognition, or vision fallback.
- No watch mode, scoring rules, card priors, roles, tags, or recommendation API changes.
- No automatic calibration from exported state.

## Modding Surface Research Questions

Before writing mod code, the first implementation packet must confirm:

- How Slay the Spire 2 mods are packaged, loaded, configured, and logged.
- Which public or normal mod-accessible APIs expose current character, deck, relics, potions, HP, gold, floor, act, ascension, and screen state.
- Whether the current reward screen exposes stable card identifiers that can be mapped to Deckseer card IDs without reading rendered text.
- Whether the mod can write a local JSON file to a user-visible path without elevated permissions.
- How game patch/build and exporter version can be captured for troubleshooting.
- How to avoid partial writes so Deckseer never reads a half-written export.

If these checks show that a field is not safely available through normal mod APIs, the exporter should omit it or mark it with a caveat rather than use unsafe techniques.

See `docs/EXPORTER_MOD_SURFACE_REVIEW.md`, `docs/EXPORTER_CARD_REWARD_VISIBILITY_DESIGN.md`, and `docs/EXPORTER_CARD_REWARD_MAPPING_REVIEW_DESIGN.md` for the current exporter handoff before attempting recommendation-ready card reward export.

## Proposed Local Output

The exporter should write a single latest-state JSON file plus optional rotated debug snapshots after users opt into them. The proposed default path is:

```text
%LOCALAPPDATA%\Deckseer\exports\latest_state.json
```

The implementation should write to a temporary file first, then atomically replace `latest_state.json` when possible. The file should be plain JSON, not compressed or hidden, so the user can inspect or edit it before Deckseer reads it.

## Export Contracts

The first harmless export target is `screen_type: "exporter_status"` because it proves the exporter loaded and wrote a local file without exposing live run state. The first recommendation export target is `screen_type: "card_reward"` because it maps directly to Deckseer's original advisor. A proposed follow-on target is `screen_type: "relic_reward"`, matching the manual `recommend-relic` surface after card reward export is proven.

## Static Status Export Contract

The static exporter status contract is the required bridge before live run-state export. `inspect-export` accepts this shape; `recommend-export` rejects it because there is no card reward to score.

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

## Card Reward Export Contract

```json
{
  "game": "slay_the_spire_2",
  "screen_type": "card_reward",
  "character": "ironclad",
  "act": 1,
  "floor": 8,
  "ascension": 0,
  "gold": 113,
  "hp": {
    "current": 42,
    "max": 75
  },
  "deck": [
    {
      "id": "strike",
      "upgraded": false,
      "count": 4
    }
  ],
  "relics": [
    "burning_blood"
  ],
  "potions": [
    "fire_potion"
  ],
  "card_reward": [
    "card_a",
    "card_b",
    "card_c"
  ],
  "run_context": {
    "next_node_type": "unknown",
    "act_region": null,
    "upcoming_elites": [],
    "fought_elites": [],
    "next_nodes": [],
    "fire_before_elite": null,
    "shop_before_elite": null,
    "path_pressure": "unknown",
    "boss": null,
    "notes": []
  },
  "export_metadata": {
    "source": "deckseer_exporter_mod",
    "exporter_version": "0.1.0",
    "game_build": null,
    "game_patch": null,
    "exported_at": "2026-05-24T00:00:00Z",
    "requires_user_confirmation": true,
    "confidence": "medium",
    "caveats": [
      "User should confirm visible card reward before using this state."
    ]
  }
}
```

## Relic Reward Export Contract

This is the Deckseer-side source format for visible relic reward screens. Installed exporter `v0.4.0` can build this shape when normal reward-screen relic candidate gates pass. Treasure chest relics use a separate public route: installed `v0.4.1` observed that route as status-only, `v0.4.2` removed the identity exception but did not recover a public ID, `v0.4.3` switched the diagnostic to public `RelicModel.Id`, `v0.4.4` proved reviewed `letter_opener` mapping coverage, and installed `v0.4.6` live-proved fully mapped treasure `relic_reward` export with post-pickup downgrade. Deckseer-side support remains human-confirmation-first.

```json
{
  "game": "slay_the_spire_2",
  "screen_type": "relic_reward",
  "character": "ironclad",
  "act": 1,
  "floor": 7,
  "ascension": 0,
  "gold": 112,
  "hp": {
    "current": 63,
    "max": 80
  },
  "deck": [
    {
      "id": "strike",
      "upgraded": false,
      "count": 3
    }
  ],
  "relics": [],
  "potions": [],
  "relic_reward": [
    "akabeko",
    "kunai"
  ],
  "run_context": {
    "act_region": "overgrowth",
    "upcoming_elites": [
      "berdonis"
    ],
    "path_pressure": "elite_soon",
    "notes": []
  },
  "export_metadata": {
    "source": "deckseer_exporter_mod",
    "exporter_version": "0.1.0",
    "game_build": null,
    "game_patch": null,
    "exported_at": "2026-05-24T00:00:00Z",
    "requires_user_confirmation": true,
    "confidence": "medium",
    "caveats": [
      "User should confirm visible relic reward before using this state."
    ]
  }
}
```

### Field Notes

- `game` should stay `slay_the_spire_2` to match current Deckseer run-state files.
- `screen_type` identifies the decision surface and should be `card_reward` for card reward export or `relic_reward` for relic reward export.
- `character`, `act`, `floor`, `ascension`, `gold`, `hp`, `deck`, `relics`, `potions`, `card_reward`, and `relic_reward` should use the same logical meanings as the manual input shapes.
- `deck` entries should be normalized to Deckseer card IDs where safely possible, with `upgraded` and `count`.
- `relics`, `potions`, `card_reward`, and `relic_reward` should use Deckseer IDs. Unknown IDs should be left visible with caveats rather than silently guessed.
- `run_context` is optional and should only include fields that can be safely derived from normal mod-accessible state.
- `export_metadata` is for adapter and UI review only. It must not affect scoring directly.

## Mapping to Deckseer

Deckseer should continue to score the same advisor-ready card reward payload it already accepts. The exporter adapter:

1. Read `latest_state.json`.
2. Check `game` and `screen_type`.
3. For `exporter_status`, inspect metadata and status only.
4. For `card_reward` and `relic_reward`, preserve `export_metadata` for display or caveats.
5. Convert recommendation exports into the existing manual input shape for that decision surface.
6. Require `recommend-export --confirmed` before recommendation when `requires_user_confirmation` is true.

Skip should not appear in `card_reward`; Deckseer adds Skip internally.

## Failure and Caveat Handling

The exporter should prefer explicit caveats over guessing. Examples:

- Unsupported or unknown screen type.
- Reward card ID could not be normalized.
- Reward relic ID could not be normalized.
- Deck, relic, or potion item is unknown to Deckseer.
- Optional path context is unavailable.
- Export is stale or was produced by an older game patch.
- The modding surface cannot safely expose a requested field.

Deckseer should treat these as review warnings for the user, not as scoring inputs.

## Milestone Sequence

1. **Modding Surface Research**: confirm packaging, load path, accessible state APIs, local file write path, and safe identifier mapping.
2. **Static JSON Export Spike**: implemented. Write a harmless `screen_type: "exporter_status"` file only.
3. **Card Reward Export**: installed `v0.4.7` live-proves the card reward contract above on a fully mapped mixed reward screen after non-card reward pickup, with confirmation required and post-selection downgrade.
4. **Deckseer Import Adapter**: implemented for confirmed card and relic exporter JSON, converting into the existing manual input shapes after user confirmation.
5. **Relic Reward Export**: installed `v0.4.0` implements the visible relic reward contract for normal reward screens after manual relic advice and card reward exporter support became stable. Installed `v0.4.1` adds status-only treasure relic route observation after chest proof showed a separate route. Installed `v0.4.2` removes the canonical identity exception but leaves the public ID null. Installed `v0.4.3` uses public `RelicModel.Id` directly for that route and live-proves clear-state after pickup. Installed `v0.4.4` adds reviewed `letter_opener` mapping coverage before treasure promotion. Installed `v0.4.6` maps the remaining observed deck/potion gaps and live-proves a fully mapped treasure `relic_reward` export with confirmation and post-pickup downgrade.
6. **Optional Watch Mode**: add a CLI helper only after the static export and adapter are stable.
7. **Broader Decision Exports**: consider potion, pathing, shop, and combat surfaces after simpler reward paths are proven.

## Acceptance Criteria for Exporter 1

- The design clearly preserves read-only/export-only boundaries.
- The proposed JSON contract maps to the existing manual card reward input without changing scoring.
- Unsafe or unavailable fields have an explicit caveat path.
- The next code packet can start with a static JSON export spike without making Deckseer depend on the mod.
