# Exporter Relic Reward Live Export Design

Status: installed v0.4.6 treasure live proof passed

This document records the human-confirmed live `screen_type: "relic_reward"` exporter path after installed `v0.3.10` proved card reward stale-state downgrade. Installed `v0.4.6` has since live-proved the first fully mapped treasure `relic_reward` export and post-pickup downgrade.

## Goal

Reduce manual transcription for Relic Choice V1 while preserving Deckseer's boundaries:

- read-only/export-only exporter behavior
- user-visible local JSON
- explicit inspection and confirmation before recommendation
- no watch mode, OCR, input automation, save/profile modification, scoring changes, or relic data changes

## Existing Support

Deckseer already supports fixture-style relic reward exports:

- `inspect-export` accepts `screen_type: "relic_reward"`
- `recommend-export` dispatches confirmed relic reward files to the existing relic choice scorer
- unconfirmed relic reward files are rejected when `requires_user_confirmation` is true
- `relic-accuracy-report` guards the current six accepted relic choice scenarios

Installed exporter `v0.4.0` implements the first live relic reward export path for normal public reward-screen relic rewards. Live chest proof on 2026-05-25 showed treasure-room relics use a different public UI route and stayed safely as `exporter_status`. Installed `v0.4.1` observes that treasure relic route as status-only, refuses live export, and clears after pick. Installed `v0.4.2` removed the treasure relic identity exception but still produced `public_model_id: null`. Installed `v0.4.3` uses the public `RelicModel.Id` path directly before serialization fallback and live proof revealed `LETTER_OPENER` as an unmapped treasure relic ID. Installed `v0.4.4` maps reviewed `LETTER_OPENER` as known while continuing to refuse treasure relic live export. ADR 8 is accepted, installed `v0.4.5` verifies the treasure route readiness contract safely refuses incomplete mapping state and clears after pickup, and repo-local `v0.4.6` maps the observed `ACCURACY` and `HEART_OF_IRON` gaps.

## Export Contract

Live relic reward export should reuse the existing adapter-facing shape:

```json
{
  "game": "slay_the_spire_2",
  "screen_type": "relic_reward",
  "character": "silent",
  "act": 1,
  "floor": 8,
  "ascension": 0,
  "gold": 127,
  "hp": {
    "current": 70,
    "max": 70
  },
  "deck": [
    {
      "id": "strike",
      "upgraded": false,
      "count": 5
    }
  ],
  "relics": [
    "ring_of_the_snake"
  ],
  "potions": [
    "colorless_potion"
  ],
  "relic_reward": [
    "akabeko",
    "lead_paperweight"
  ],
  "run_context": {
    "next_node_type": "unknown",
    "path_pressure": "unknown",
    "notes": [
      "Live exporter did not infer map/path context."
    ]
  },
  "export_metadata": {
    "source": "deckseer_exporter_mod",
    "exporter_version": "0.4.0",
    "game_build": null,
    "game_patch": null,
    "exported_at": "2026-05-25T00:00:00Z",
    "requires_user_confirmation": true,
    "confidence": "medium",
    "caveats": [
      "Run inspect-export and confirm this live state before using recommend-export.",
      "Confirm the visible relic reward, deck, HP, gold, relics, and potions before using this state.",
      "Live exporter map/path context is unknown/defaulted."
    ]
  }
}
```

## Required Gates

The live exporter may write `screen_type: "relic_reward"` only when all required gates pass:

- a visible relic reward is observed through public reward-screen state
- run state and serializable run context are aligned with the visible reward player
- character, act, floor, ascension, gold, HP, deck, relics, and potions are present
- deck cards, owned relics, owned potions, and reward relics all map to Deckseer IDs
- the visible reward is not stale, already collected, skipped, or closed
- the reward relic list has at least one option and no duplicates
- `requires_user_confirmation` is true

Any failure writes `screen_type: "exporter_status"` with refusal diagnostics instead of a partial recommendation payload.

## Refusal Codes

Use stable refusal codes so fixtures and live proof can distinguish blockers:

- `no_visible_relic_reward`
- `stale_reward_screen`
- `missing_required_run_state_field`
- `unmapped_reward_relic`
- `mixed_reward_screen_state_may_change`
- `treasure_relic_route_status_only`
- `unmapped_owned_relic`
- `unmapped_potion`
- `unmapped_deck_card`
- `duplicate_reward_relic`
- `unsupported_reward_shape`

The status file may report counts and mapped known IDs according to existing review boundaries, but it must not become recommendation-ready.

## Clear-State Requirements

The exporter must downgrade away from `screen_type: "relic_reward"` when:

- the relic reward is collected
- the reward screen closes
- the reward screen is skipped
- a later screen replaces the visible reward

The closed-state file should be `screen_type: "exporter_status"`, clear reward identity arrays/counts, set the candidate to refused, and make `recommend-export --confirmed` reject the file.

## Verification Plan

Repo-local implementation must pass before install:

```bash
dotnet build exporter_mod/DeckseerExporter/DeckseerExporter.csproj
python -m deckseer.cli inspect-export tests/fixtures/exporter_relic_reward_live_v040_state.json
python -m deckseer.cli recommend-export tests/fixtures/exporter_relic_reward_live_v040_state.json --format text
python -m deckseer.cli recommend-export tests/fixtures/exporter_relic_reward_live_v040_state.json --confirmed --format text
python -m deckseer.cli inspect-export tests/fixtures/exporter_status_v040_relic_reward_closed_state.json
python -m pytest tests/test_exporter_state.py tests/test_relic_choice.py -q
git diff --check
```

Expected behavior:

- `inspect-export` accepts the live relic reward fixture
- unconfirmed `recommend-export` rejects the fixture
- confirmed `recommend-export` scores through the existing relic choice scorer
- closed/stale status fixtures are not recommendation-ready
- no card reward scoring, relic scoring, priors, empirical rows, or baselines change

## Repo-Local v0.4.0 Implementation

Repo-local `v0.4.0` adds:

- public `RelicReward.Relic` identity review for visible relic rewards
- refusal-first live relic reward candidate diagnostics under `exporter_status`
- live `screen_type: "relic_reward"` payload building only when the candidate is ready
- stale-state downgrade on relic reward collection, reward skip, or reward-screen close
- v0.4.0 live and closed-state fixtures
- focused exporter/relic regression tests for confirmation gating and closed-screen rejection

Repo-local verification on 2026-05-25:

- `dotnet build exporter_mod\DeckseerExporter\DeckseerExporter.csproj ...`: 0 warnings / 0 errors
- `inspect-export tests\fixtures\exporter_relic_reward_live_v040_state.json`: valid
- unconfirmed `recommend-export tests\fixtures\exporter_relic_reward_live_v040_state.json --format text`: rejected for missing confirmation
- confirmed `recommend-export tests\fixtures\exporter_relic_reward_live_v040_state.json --confirmed --format text`: scores through Relic Choice V1
- `inspect-export tests\fixtures\exporter_status_v040_relic_reward_closed_state.json`: valid status
- confirmed `recommend-export tests\fixtures\exporter_status_v040_relic_reward_closed_state.json --confirmed --format text`: rejected as `exporter_status`
- `pytest tests\test_exporter_state.py tests\test_relic_choice.py -q`: 70 passed

## Installed v0.4.0 Chest Proof

Installed `v0.4.0` startup wrote valid `exporter_status`.

A treasure chest relic screen was then live-tested. Opening the chest revealed a visible relic and did not auto-collect it, but the export file did not update from the previous `exporter_status`. Post-collect inspection also remained `exporter_status`, and `recommend-export --confirmed` rejected it with `got exporter_status`.

This is a safe negative proof:

- no stale `relic_reward` file was written
- no recommendation-ready live state was exported
- no input automation, OCR, memory/process access, save/profile access, or scoring changes were used
- local metadata identified a separate public chest route: `NTreasureRoomRelicHolder.Initialize(RelicModel, IRunState)` and `TreasureRoomRelicSynchronizer`

## Installed v0.4.1 Treasure Relic Status Probe

Installed `v0.4.1` adds a status-only treasure relic route observation:

- observes `NTreasureRoomRelicHolder.Initialize(RelicModel, IRunState)`
- records visible treasure relic identity review diagnostics under `exporter_status`
- refuses live `relic_reward` with `treasure_relic_route_status_only`
- clears on public treasure relic pick, skip, room-exit, or collection exit hooks
- does not write recommendation-ready state for treasure relics

Repo-local verification:

- `dotnet build exporter_mod\DeckseerExporter\DeckseerExporter.csproj ...`: 0 warnings / 0 errors
- `pytest tests\test_exporter_state.py -q`: 59 passed

Live proof:

- startup wrote valid `exporter_status` with `exporter_version: "0.4.1"`
- visible treasure relic screen wrote `exporter_status`
- `visible_reward_probe_status: "treasure_relic_model_seen"`
- `visible_relic_reward_option_count: 1`
- `relic_reward_live_export_candidate: "refused"`
- refusal reasons included `treasure_relic_route_status_only`
- clicking the relic cleared the visible reward state to `reward_screen_completed`
- `visible_relic_reward_option_count: 0`
- `relic_reward_identity_review_items: []`

The live visible identity probe hit `CanonicalModelException` because the holder exposes a non-canonical `RelicModel`.

## Installed v0.4.2 Canonical Treasure Relic Identity Proof

Repo-local `v0.4.2` attempted to resolve the treasure relic identity diagnostic by reading `RelicModel.CanonicalInstance` before calling `ToSerializable()`.

It remains status-only:

- treasure relics still refuse live export with `treasure_relic_route_status_only`
- `recommend-export --confirmed` still rejects the status fixture
- no scoring, relic data, baselines, watch mode, OCR, input automation, or live capture behavior changes

Repo-local verification:

- `dotnet build exporter_mod\DeckseerExporter\DeckseerExporter.csproj ...`: 0 warnings / 0 errors
- `inspect-export tests\fixtures\exporter_status_v042_treasure_relic_identity_state.json`: valid
- `recommend-export tests\fixtures\exporter_status_v042_treasure_relic_identity_state.json --confirmed --format text`: rejected as `exporter_status`
- `pytest tests\test_exporter_state.py -q`: 60 passed

Live proof after explicit install approval showed:

- startup wrote valid `exporter_status` with `exporter_version: "0.4.2"`
- visible treasure relic screen wrote `exporter_status`
- `visible_reward_probe_status: "treasure_relic_model_seen"`
- `visible_relic_reward_option_count: 1`
- `relic_reward_identity_review_probe: "ids_revealed_for_review"`
- `relic_reward_identity_review_error: null`
- the identity item still had `public_model_id: null`, `normalized_candidate_id: null`, and `deckseer_mapping_status: "invalid"`
- clicking the relic cleared the visible reward state to `reward_screen_completed`

This means `v0.4.2` fixed the exception but did not recover a usable public relic ID from the treasure holder model.

## Installed v0.4.3 Public RelicModel.Id Proof

Repo-local `v0.4.3` reads public `RelicModel.Id.Entry` directly, preferring `CanonicalInstance.Id.Entry` when present and falling back to serialization only after public model ID reads fail.

It remains status-only:

- treasure relics still refuse live export with `treasure_relic_route_status_only`
- `recommend-export --confirmed` still rejects the status fixture
- the new fixture proves the diagnostics can carry a public relic model ID and Deckseer mapping without becoming recommendation-ready
- no scoring, relic data, baselines, watch mode, OCR, input automation, or live capture behavior changes

Repo-local verification:

- `dotnet build exporter_mod\DeckseerExporter\DeckseerExporter.csproj ...`: 0 warnings / 0 errors
- `inspect-export tests\fixtures\exporter_status_v043_treasure_relic_model_id_state.json`: valid
- `recommend-export tests\fixtures\exporter_status_v043_treasure_relic_model_id_state.json --confirmed --format text`: rejected as `exporter_status`
- `pytest tests\test_exporter_state.py -q`: 61 passed
- `git diff --check`: passed with CRLF warnings only

Installed `v0.4.3` live proof after explicit install approval:

- startup wrote valid `exporter_status` with `exporter_version: "0.4.3"`
- visible treasure relic wrote `exporter_status`, not `relic_reward`
- `visible_reward_probe_status: "treasure_relic_model_seen"`
- `visible_relic_reward_option_count: 1`
- `relic_reward_identity_review_probe: "ids_revealed_for_review"`
- the visible identity item reported `public_model_id: "LETTER_OPENER"` and `normalized_candidate_id: "letter_opener"`
- `deckseer_mapping_status: "unknown"` and `deckseer_id: null`
- refusal reasons included `treasure_relic_route_status_only`
- confirmed `recommend-export` rejected the visible file as `exporter_status`
- after pickup, `visible_reward_probe_status: "reward_screen_completed"` and `visible_reward_probe_last_event: "treasure_relic_picked"`
- relic reward identity counts and items cleared to zero
- confirmed `recommend-export` rejected the closed file as `exporter_status`

`LETTER_OPENER` is review evidence only. This proof does not approve adding relic metadata, changing relic scoring, or promoting treasure relics to live `relic_reward` export.

The mapping handoff lives in `docs/EXPORTER_TREASURE_RELIC_MAPPING_REVIEW.md`, and the reviewed `letter_opener` data plus installed `v0.4.4` mapped treasure proof live in `docs/EXPORTER_TREASURE_RELIC_DATA_REVIEW.md`.

## Installed v0.4.4 Reviewed Letter Opener Mapping Proof

Installed `v0.4.4` adds reviewed `letter_opener` mapping coverage after the separate data-review packet.

It remains status-only:

- treasure relics still refuse live export with `treasure_relic_route_status_only`
- `recommend-export --confirmed` still rejects visible and cleared treasure status files
- no scoring logic, baselines, watch mode, OCR, input automation, or live capture behavior changes

Live proof after explicit install approval:

- startup wrote valid `exporter_status` with `exporter_version: "0.4.4"`
- visible treasure relic wrote `exporter_status`, not `relic_reward`
- `visible_reward_probe_status: "treasure_relic_model_seen"`
- `visible_relic_reward_option_count: 1`
- the visible identity item reported `public_model_id: "LETTER_OPENER"` and `normalized_candidate_id: "letter_opener"`
- `deckseer_mapping_status: "known"` and `deckseer_id: "letter_opener"`
- refusal reasons included `treasure_relic_route_status_only`
- confirmed `recommend-export` rejected the visible file as `exporter_status`
- after pickup, `visible_reward_probe_status: "reward_screen_completed"` and `visible_reward_probe_last_event: "treasure_relic_picked"`
- relic reward identity counts and items cleared to zero
- confirmed `recommend-export` rejected the closed file as `exporter_status`

Installed treasure relic live export proof remains pending. `docs/EXPORTER_TREASURE_RELIC_LIVE_EXPORT_READINESS.md` records the remaining live proof criteria before any successful treasure export claim.

## Repo-Local v0.4.5 Treasure Relic Export

ADR 8 accepts a narrow treasure route extension of ADR 7.

Repo-local `v0.4.5` changes the candidate probe so `treasure_relic_model_seen` plus `treasure_relic_holder_initialized` can become eligible for live `screen_type: "relic_reward"` export. The public `IRunState` passed to `NTreasureRoomRelicHolder.Initialize(...)` satisfies the treasure route's visible alignment gate, while all existing run-state, deck, owned relic, potion, reward relic, duplicate, stale-state, and payload validation gates still apply.

Fixture coverage:

- `tests/fixtures/exporter_relic_reward_live_v045_treasure_state.json` inspects as `relic_reward`, requires confirmation, and scores through Relic Choice V1 after `--confirmed`.
- `tests/fixtures/exporter_status_v045_treasure_relic_picked_state.json` remains `exporter_status`, clears reward identity diagnostics, and rejects confirmed recommendation.

Installed `v0.4.5` live proof:

- startup fallback wrote valid `exporter_status` with `exporter_version: "0.4.5"`
- visible treasure `LETTER_OPENER` mapped known as `letter_opener`
- candidate refused because the run had `unmapped_deck_card` and `unmapped_potion`
- the unknown mapping evidence was `ACCURACY` and two `HEART_OF_IRON` potions
- confirmed `recommend-export` rejected the visible file as `exporter_status`
- after pickup, visible reward diagnostics cleared and confirmed `recommend-export` rejected the closed file as `exporter_status`

This proves the route-specific refusal and clear-state behavior. It does not yet prove a successful live treasure `relic_reward` export because the tested run was not fully mapped.

## v0.4.6 Treasure Mapping Follow-Up

`v0.4.6` adds reviewed mapping coverage for the installed `v0.4.5` blockers:

- `ACCURACY` -> `accuracy`
- `HEART_OF_IRON` -> `heart_of_iron`

`tests/fixtures/exporter_relic_reward_live_v046_treasure_mapped_state.json` includes those IDs in a fully mapped treasure relic fixture. It inspects as `screen_type: "relic_reward"`, requires user confirmation, and scores through Relic Choice V1 after `--confirmed`.

Installed `v0.4.6` live proof passed:

- startup fallback wrote valid `exporter_status` with `exporter_version: "0.4.6"`.
- visible treasure wrote `screen_type: "relic_reward"` with confirmation required.
- the live mapped run included `accuracy`, `colorless_potion`, two `heart_of_iron` potions, and `letter_opener`.
- unconfirmed `recommend-export` rejected the file until human confirmation.
- confirmed `recommend-export` scored `letter_opener`.
- after pickup, the file downgraded to `exporter_status`, cleared visible reward identities, and rejected confirmed recommendation.

## Non-Goals

This design does not approve:

- watch mode
- OCR, screenshot reading, or live capture
- input automation
- save/profile modification
- memory/process tricks or packet inspection
- boss relic special scoring
- relic metadata expansion
- scoring or baseline changes
