# Deckseer Exporter Card Reward Mapping Review Design

Status: `review_handoff_logged`

Prepared on 2026-05-24 after the installed `v0.2.8` status-only ID-shape diagnostic reported a visible three-card reward with 2 known mappings and 1 unknown mapping by count only.

## Scope

This packet designs how to review exporter card ID mapping gaps before any live card ID export.

It does not implement exporter code, install a mod package, launch STS2, export raw STS2 IDs, export Deckseer IDs, add card data, change scoring, change priors, change empirical data, change recommendation behavior, add watch mode, add OCR, add screenshot capture, add input automation, or modify saves/profile data.

## Evidence From v0.2.8

The installed `v0.2.8` diagnostic stayed inside the status-only boundary:

- `screen_type: "exporter_status"`
- `visible_card_reward_option_count: 3`
- `visible_card_identity_read_count: 3`
- `visible_card_identity_direct_id_count: 3`
- `visible_card_identity_serialized_id_count: 3`
- `visible_card_identity_mapping_known_count: 2`
- `visible_card_identity_mapping_unknown_count: 1`
- no raw STS2 IDs, Deckseer IDs, card names, selected-card identity, deck, HP, gold, relics, potions, or recommendation-ready run state

The user-visible reward screen showed `Cloak and Dagger`, `Bouncing Flask`, and `Infinite Blades`. At observation time, Deckseer had card data for `cloak_and_dagger` and `bouncing_flask`, but not `infinite_blades`. This explained the 2 known / 1 unknown count without requiring the exporter to reveal the live model ID.

Treat this as review evidence only. It does not approve adding `infinite_blades` card data, changing scoring, or exporting live card IDs.

## Mapping Review Principles

- Keep status diagnostics count-only until a later explicit packet approves live ID export.
- Prefer public model IDs over localized display names for actual exporter mapping.
- Use visible labels only as human review context, not as an exporter mapping source.
- Unknown mappings are readiness evidence, not runtime errors.
- Do not fuzzy-match inside the exporter.
- Do not silently guess unknown IDs.
- Track upgrade state separately from card identity.
- Keep mapping evidence outside recommendation scoring until the card is reviewed in Deckseer's data.

## Proposed Mapping Artifacts

A later repo-local packet may add mapping artifacts that are not recommendation inputs:

- `docs/EXPORTER_CARD_REWARD_MAPPING_REVIEW.md`: human-readable review log for observed mapping gaps.
- `exporter_mod/DeckseerExporter/DeckseerExporterCode/CardIdentityMappingSnapshot.cs`: explicit status-diagnostic mapping snapshot used only for known/unknown counts.
- `tests/fixtures/exporter_status_*_mapping_review_state.json`: status-only fixtures with count diagnostics.

Do not add raw live STS2 IDs from a run to fixtures unless a later packet explicitly approves an ID-revealing diagnostic. If an offline STS2 model ID catalog is generated from local game files, mark it as review evidence and keep it separate from recommendation data.

## Review Workflow

1. Confirm the status-only diagnostic reports counts that match the visible screen.
2. Compare the visible card labels provided by the user with `data/cards/*.json` to identify likely missing Deckseer card data.
3. Check whether the missing card should be added to Deckseer data through the normal reviewed card-data workflow.
4. If the card data exists but the mapping count is still unknown, design a separate explicit mapping probe that reveals the minimum necessary identifier evidence.
5. Keep the exporter at `screen_type: "exporter_status"` until the mapping contract is reviewed.

This workflow can explain an unknown count, but it cannot prove the exact STS2 model ID for the unknown card. Exact ID proof requires a later explicit packet because it starts exposing live identity information.

## Allowed Next Packet

The next safe implementation packet is repo-local and data-neutral:

- add a review-only note for the `v0.2.8` observed mapping gap
- add or update tests only for status metadata preservation
- do not add card metadata
- do not update the exporter to emit IDs
- do not install another mod package

## Review Handoff Result

The review-only handoff note now lives in `docs/EXPORTER_CARD_REWARD_MAPPING_REVIEW.md`.

It records that the installed `v0.2.8` status-only diagnostic observed 3 visible options, 3 identity-shaped reads, 2 known mappings, and 1 unknown mapping by count only. The visible labels reported by the user were `Cloak and Dagger`, `Bouncing Flask`, and `Infinite Blades`; at observation time, Deckseer had data for `cloak_and_dagger` and `bouncing_flask`, but not `infinite_blades`.

That explains the unknown count as a likely data-coverage gap, but it is not exact STS2 model ID proof and does not approve adding card data, changing scoring, or exporting live IDs.

## Stop Conditions

Stop before proceeding if the next step would:

- export raw STS2 IDs, Deckseer IDs, display names, or card text from the live exporter
- change `screen_type` from `exporter_status` to `card_reward`
- add or change card data, scoring, priors, empirical rows, baselines, or accuracy expectations
- depend on screenshots, OCR, live capture, watch mode, input automation, save/profile modification, private-field reflection, publicizer workarounds, memory/process access, or packet inspection
- treat visible labels as automatic mapping truth rather than reviewed evidence
