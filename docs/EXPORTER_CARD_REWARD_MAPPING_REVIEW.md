# Deckseer Exporter Card Reward Mapping Review

Status: `reviewed_card_data_follow_up_done`

Prepared on 2026-05-24 after the installed `v0.2.8` status-only ID-shape diagnostic observed a visible three-card reward with 2 known mappings and 1 unknown mapping by count only.

## Scope

This note records the mapping review handoff for the `v0.2.8` observation. It is review evidence only.

It does not approve:

- live card ID export
- `screen_type: "card_reward"` output from the exporter
- card data additions
- scoring, prior, role, empirical, accuracy, recommendation, or baseline changes
- watch mode, OCR, screenshot capture, input automation, memory/process access, packet inspection, save/profile modification, or game-file changes

## Observed Evidence

The installed exporter stayed inside the status-only boundary:

- `screen_type: "exporter_status"`
- `visible_card_reward_option_count: 3`
- `visible_card_identity_read_count: 3`
- `visible_card_identity_direct_id_count: 3`
- `visible_card_identity_serialized_id_count: 3`
- `visible_card_identity_mapping_known_count: 2`
- `visible_card_identity_mapping_unknown_count: 1`

The visible reward labels reported by the user were:

- `Cloak and Dagger`
- `Bouncing Flask`
- `Infinite Blades`

Deckseer currently has Silent card data for:

- `cloak_and_dagger`
- `bouncing_flask`

Deckseer does not currently have card data for:

- `infinite_blades`

This is enough to explain the 2-known / 1-unknown count as a likely data-coverage gap. It is not exact STS2 model ID proof, because the exporter intentionally did not reveal live raw IDs, Deckseer IDs, card names, or card text.

## Reviewed Card-Data Follow-Up

Completed on 2026-05-24 after explicit user approval.

Deckseer now has reviewed Silent seed metadata for `infinite_blades`, using the same local Silent `v0.102.0` tier-list source family as the existing Silent seed data plus a current card database check for the basic card shape. The repo-local status-diagnostic mapping snapshot was also updated so future repo-local diagnostics treat `infinite_blades` as known.

This follow-up did not install a mod package, update the real STS2 mods folder, export live IDs, change `screen_type`, add watch mode, or change scorer rules. The installed `v0.2.8` result remains historical evidence from the older snapshot.

The test suite now includes a catalog-versus-snapshot drift guard so future reviewed card-data additions must keep the repo-local status-diagnostic mapping snapshot current.

ADR 3 now accepts a bounded status-only ID-revealing diagnostic for exact mapping review. Installed `v0.2.9` implements it and passed visible-screen verification while remaining outside recommendation input.

## v0.2.9 Visible ID Review Result

The live `v0.2.9` visible-screen diagnostic wrote only `screen_type: "exporter_status"` and reported three review items:

| Position | Public model ID | Normalized candidate | Deckseer mapping status | Deckseer ID |
| ---: | --- | --- | --- | --- |
| 0 | `CLOAK_AND_DAGGER` | `cloak_and_dagger` | `known` | `cloak_and_dagger` |
| 1 | `BOUNCING_FLASK` | `bouncing_flask` | `known` | `bouncing_flask` |
| 2 | `INFINITE_BLADES` | `infinite_blades` | `known` | `infinite_blades` |

All three were unupgraded, and all three serialized IDs matched the direct public model IDs. After leaving/skipping the reward screen, the diagnostic reported `card_identity_review_probe: "cleared"` and `card_identity_review_items: []`. `recommend-export --confirmed` rejected the live file because it is still `exporter_status`.

## Review Conclusion

The `v0.2.8` result supports this handoff:

- The status-only ID-shape diagnostic can read identity-shaped facts for the visible reward screen through approved public routes.
- The embedded mapping snapshot can distinguish known versus unknown choices by count without exposing IDs.
- The observed unknown count was plausibly explained by missing Deckseer data for `infinite_blades`; the reviewed data follow-up has now filled that local coverage gap.
- At the time of this handoff, live card reward export was still blocked until the installed `v0.2.11` 3-known/11-unknown deck mapping gap had a reviewed resolution path and a later packet explicitly implemented the human-confirmed recommendation flow.
- `docs/EXPORTER_CARD_REWARD_DECK_MAPPING_GAP_REVIEW.md` records the installed `v0.2.11` deck mapping gap as count-only evidence. It does not identify the unknown deck cards because live deck IDs were intentionally not exported.

## Follow-Up Options

Safe next packets remain separate:

- Deck mapping gap review/design: decide whether to use a manual deck list, a separately approved deck-ID review diagnostic, or reviewed card-data packets before any live `card_reward` export.
- Card reward export packet: only after runtime presence is proven and reviewed, implement `screen_type: "card_reward"` with `requires_user_confirmation: true` and existing `inspect-export` before `recommend-export --confirmed` behavior.

## Current Blocker

At the time of this handoff, the exporter was expected to remain at `screen_type: "exporter_status"` until deck, relic, and potion mapping readiness was reviewed and a separate packet explicitly approved recommendation-ready export.

## Superseded Blocker Note

As of 2026-05-25, this blocker is historical. Later packets accepted the human-confirmed `card_reward` boundary in ADR 4, resolved the deck/relic/potion mapping gaps through reviewed diagnostics and data packets, and live-proved installed `v0.4.7` on a fully mapped mixed reward card screen with post-selection downgrade. This document remains the `v0.2.8` mapping-review handoff, not the current live-export blocker.
