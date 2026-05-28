# Deckseer Exporter Card Reward ID Diagnostic Design

Status: `id_reveal_follow_up_repo_local`

Prepared on 2026-05-24 after the installed `v0.2.4` count/clear diagnostic and repo-local `v0.2.5` card identity compile probe.

## Scope

This packet designs the next proof gate before any recommendation-ready live card reward export and records the installed status-only implementation result.

It does not approve recommendation-ready card reward export, live card ID export, Deckseer scoring changes, adapter behavior changes, watch mode, OCR, input automation, or any non-exporter state source.

The diagnostic described here must still write only:

```json
{
  "screen_type": "exporter_status"
}
```

## Goal

Prove whether public reward-screen and card-choice screen paths can derive stable, Deckseer-mappable card identity facts without exposing those identities to the advisor yet.

This diagnostic is deliberately between count-only visibility and real `screen_type: "card_reward"` export:

1. Count-only visibility proved the visible two-card reward screen can be observed.
2. Clear-state diagnostics proved the visible count can be reset when the screen closes.
3. Compile probes proved `CardModel.Id`, `CardModel.CurrentUpgradeLevel`, `CardModel.IsUpgraded`, and `CardModel.ToSerializable()` compile from normal mod source.
4. The next diagnostic should prove mapping quality by counts and status only.

## Approved Inputs

The diagnostic may read only `CardModel` values already exposed by these approved public observation routes:

```text
NRewardsScreen.ShowScreen(RewardsSet, Boolean, IRunState) via RewardsSet.Rewards -> CardReward.Cards
NChooseACardSelectionScreen.ShowScreen(IReadOnlyList<CardModel>, Boolean)
```

The diagnostic may call only public, already compile-proven card identity members:

- `CardModel.Id`
- `CardModel.CurrentUpgradeLevel`
- `CardModel.IsUpgraded`
- `CardModel.ToSerializable()`
- `SerializableCard.Id`
- `SerializableCard.CurrentUpgradeLevel`

The diagnostic may compare normalized IDs against Deckseer's local mapping table embedded in exporter source for this proof packet, or against a fixed generated mapping snapshot checked into the repo. That mapping must be treated as diagnostic evidence only, not scoring data.

## Allowed Output

The diagnostic may add status-only metadata fields under `export_metadata.diagnostics`, such as:

- `card_identity_runtime_probe`: `not_observed`, `card_choice_ids_seen`, `mapping_incomplete`, `probe_error`, or `cleared`
- `card_identity_runtime_last_event`
- `visible_card_identity_read_count`
- `visible_card_identity_direct_id_count`
- `visible_card_identity_serialized_id_count`
- `visible_card_identity_nullable_serialized_id_count`
- `visible_card_identity_upgraded_count`
- `visible_card_identity_mapping_known_count`
- `visible_card_identity_mapping_unknown_count`
- `visible_card_identity_duplicate_normalized_count`
- `visible_card_identity_error`

These fields must be counts, booleans, or status strings only. They must not contain raw STS2 IDs, Deckseer IDs, display names, card text, selected-card identity, or deck/run state.

## Forbidden Output

This diagnostic must not export:

- raw STS2 card IDs
- Deckseer-normalized card IDs
- card names or localized titles
- card text, costs, rarity, type, tags, or effects
- selected-card identity
- deck contents
- HP, gold, act, floor, ascension, relics, potions, map, save/profile data, or run history
- `screen_type: "card_reward"`
- any payload accepted by `recommend-export` as recommendation input

## Mapping Rules

For this diagnostic, "known" means a public `CardModel.Id` can be normalized by a deterministic mapping snapshot to an existing Deckseer card ID.

The mapping snapshot should be explicit and reviewed. Unknown mappings are not errors by themselves; they are evidence that live export is not ready for those choices.

The repo test suite includes a drift guard that compares Deckseer's current card catalog against the embedded status-diagnostic mapping snapshot. If a reviewed card-data packet adds a card, the repo-local snapshot must be updated in the same packet so future count-only diagnostics do not silently undercount known mappings. This guard is maintenance only; it does not approve exporting live IDs.

Recommended normalization sequence:

1. Convert the public model ID to a stable string using a documented, public string representation.
2. Normalize casing and separators using the same conservative style as existing Deckseer IDs.
3. Look up the normalized candidate in the mapping snapshot.
4. Count known, unknown, duplicate-normalized, nullable-serialized, and upgraded cards.

Do not guess from localized display names. Do not fuzzy-match inside the exporter. Fuzzy suggestions belong in Deckseer's offline inspection tooling, not the live exporter diagnostic.

## Manual Proof Matrix

When a later install-check is explicitly approved, test the diagnostic with this matrix:

| Situation | Expected diagnostic |
| --- | --- |
| Startup / no reward screen | `card_identity_runtime_probe: "not_observed"`, all identity counts zero |
| Visible two-card reward screen | read count 2, known plus unknown counts sum to 2 |
| Visible reward with upgraded card, if naturally encountered | upgraded count matches visible upgrade markers |
| Reward screen closes by choosing or skipping | `card_identity_runtime_probe: "cleared"` or existing close status, all identity counts zero |
| Unknown mapping encountered | unknown count is nonzero, no raw IDs exported |

Do not use gameplay automation to create these states. Do not reroll, generate rewards, inspect saves, or drive UI.

## Adapter Contract

The Deckseer adapter remains unchanged for this diagnostic:

- `inspect-export` accepts `screen_type: "exporter_status"` and preserves diagnostics as metadata.
- `recommend-export` rejects `exporter_status`.
- `recommend-export` still requires `--confirmed` for future `card_reward` exports that set `requires_user_confirmation: true`.
- Existing contract fixtures cover unknown IDs, upgraded deck cards, metadata caveats, missing confirmation, and unsupported upgraded reward-card object shape.

## Implementation Result

Implemented repo-local on 2026-05-24 as exporter source `v0.2.6`, then corrected through repo-local `v0.2.8` and install-checked after explicit approval.

The implementation observes only the already-approved public card-choice screen hook:

```text
NChooseACardSelectionScreen.ShowScreen(IReadOnlyList<CardModel>, Boolean)
```

The live `v0.2.7` install-check showed that a visible three-card reward screen could be observed through `NRewardsScreen.ShowScreen(RewardsSet, ...)` rather than `NChooseACardSelectionScreen.ShowScreen(...)`. Counts matched the visible screen, but identity counts remained zero because the ID-shape diagnostic only read the card-choice screen argument.

Repo-local `v0.2.8` therefore also reads the public `CardReward.Cards` models from the public `RewardsSet` argument already used for count-only visibility. For each card in either public route, it reads only compile-proven public identity members and maps `CardModel.Id.Entry` through an embedded Deckseer card ID snapshot. The game-written payload still uses `screen_type: "exporter_status"` and exports status/count fields only:

- `card_identity_runtime_probe`
- `card_identity_runtime_last_event`
- `visible_card_identity_read_count`
- `visible_card_identity_direct_id_count`
- `visible_card_identity_serialized_id_count`
- `visible_card_identity_nullable_serialized_id_count`
- `visible_card_identity_upgraded_count`
- `visible_card_identity_mapping_known_count`
- `visible_card_identity_mapping_unknown_count`
- `visible_card_identity_duplicate_normalized_count`
- `visible_card_identity_error`

It does not export raw STS2 IDs, Deckseer IDs, card names, selected-card identity, deck, HP, gold, relics, potions, save/profile data, OCR, watch mode, input automation, or recommendation-ready run state.

Verification:

- repo-local `dotnet build exporter_mod\DeckseerExporter\DeckseerExporter.csproj` passed with 0 warnings and 0 errors
- `inspect-export tests\fixtures\exporter_status_v028_reward_screen_identity_runtime_state.json` passed
- focused exporter-state tests passed: 31 tests

Live `v0.2.8` install-check result:

- installed manifest reported `version: "v0.2.8"`
- startup export stayed valid `screen_type: "exporter_status"` with zeroed idle diagnostics
- visible three-card reward screen reported `visible_card_reward_option_count: 3`
- identity diagnostics reported read/direct/serialized counts of 3
- mapping diagnostics reported 2 known and 1 unknown mapping by count only
- no raw STS2 IDs, Deckseer IDs, card names, selected-card identity, deck, HP, gold, relics, potions, save/profile data, OCR, watch mode, input automation, or recommendation-ready run state were exported

## Acceptance For A Later Mapping Packet

A future mapping packet should use the count-only unknown evidence to design an auditable mapping review path before any live card IDs are exported. It should preserve that:

- keeps `screen_type: "exporter_status"`
- writes no raw IDs and no Deckseer IDs
- reports only status/count diagnostics
- clears identity counts when the card-choice screen closes
- preserves `recommend-export` rejection for status exports
- reports known/unknown mapping counts on a visible card reward screen without exposing the underlying IDs

## Stop Conditions

Stop before implementation or install-check if:

- stable public string conversion for `CardModel.Id` is unclear
- mapping requires localized card names
- upgraded reward state cannot be counted without exporting IDs
- the diagnostic needs private fields, reflection, publicizer workarounds, memory/process access, OCR, screenshots, input automation, save/profile modification, reward generation, or packet inspection
- the implementation would change scoring, priors, empirical data, recommendation output, public CLI behavior, or adapter schemas

Stop before real `screen_type: "card_reward"` export until a separate explicit packet approves live card ID export and human-confirmed recommendation flow.

## ID Reveal Follow-Up

ADR 3 accepted a bounded, status-only ID-revealing diagnostic for mapping review. Installed exporter `v0.2.9` implements that diagnostic under `screen_type: "exporter_status"` and preserves `recommend-export` rejection for status files. Visible-screen verification passes for `CLOAK_AND_DAGGER`, `BOUNCING_FLASK`, and `INFINITE_BLADES`, all mapped to reviewed Deckseer IDs.
