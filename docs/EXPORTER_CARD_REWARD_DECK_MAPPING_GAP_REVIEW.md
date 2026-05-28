# Deckseer Exporter Card Reward Deck Mapping Gap Review

Status: `dramatic_entrance_visible_verified`

Prepared on 2026-05-24 after installed `v0.2.11` status-only runtime presence verification.

## Scope

This note records the first live deck mapping gap observed by the runtime presence diagnostic. It is review evidence only.

It does not approve:

- live deck ID export
- `screen_type: "card_reward"` output from the exporter
- deck, relic, potion, HP, gold, character, act, floor, or ascension value export
- card data additions
- scoring, prior, role, empirical, accuracy, recommendation, or baseline changes
- watch mode, OCR, screenshot capture, input automation, memory/process access, packet inspection, save/profile modification, or game-file changes

## Observed Evidence

Installed `v0.2.11` stayed inside the status-only boundary on a human-opened visible reward screen:

- `screen_type: "exporter_status"`
- `exporter_version: "0.2.11"`
- `card_reward_run_state_runtime_probe: "incomplete"`
- `card_reward_run_state_runtime_last_event: "rewards_screen_shown"`
- run in progress, run state available, serializable run available, one player, and visible reward player present
- character, act, floor, ascension, gold, HP, deck, relics, and potions present
- deck count 14
- deck card ID read count 14
- deck mapping known count 3
- deck mapping unknown count 11
- relic count 2
- potion count 0
- `card_reward_run_state_writes_recommendation_state: false`
- no runtime probe error

The same live file remained `exporter_status`; `inspect-export` accepted it, and `recommend-export --confirmed` rejected it because status exports are not recommendation input.

After the reward screen was skipped/left, installed `v0.2.11` cleared the runtime readiness diagnostic:

- `card_reward_run_state_runtime_probe: "cleared"`
- runtime booleans false and counts zero
- visible reward counts zero
- card identity runtime counts zero
- `card_identity_review_items: []`

## What This Proves

The runtime presence path can see the required run-state field surfaces during a visible reward screen.

The exporter can count deck cards and count how many public card IDs normalize to the current status-diagnostic mapping snapshot.

The first tested live deck is not ready for a complete `card_reward` export because 11 of 14 deck card IDs are unknown to the mapping snapshot by count.

The exporter correctly refuses to mark the runtime probe as complete when deck mapping is incomplete.

## What This Does Not Prove

This result does not reveal which 11 deck cards were unknown.

It does not prove a Deckseer data defect for any specific card.

It does not prove that all known mapped deck cards have enough metadata for recommendation quality.

It does not approve exporting live deck IDs, guessing from visible labels, changing card data, or writing `screen_type: "card_reward"`.

It does not prove relic or potion ID mappings; `v0.2.11` reports only their counts.

## Review Interpretation

The 3-known/11-unknown deck count is a readiness blocker, not a runtime failure.

For a future complete live `card_reward` export, every live deck card ID must normalize to a reviewed Deckseer ID before the exporter can safely emit the existing advisor input shape.

Because the current diagnostic intentionally does not expose live deck IDs, the next review step cannot identify the exact missing cards from this file alone.

## v0.2.12 Deck ID Review Result

ADR 5 accepted a bounded status-only deck ID review diagnostic, and installed `v0.2.12` visible reward-screen verification identified the 3-known/11-unknown deck mapping count.

Known mappings:

- `NEUTRALIZE` -> `neutralize`
- `SURVIVOR` -> `survivor`
- `SLICE` -> `slice`

Unknown mappings:

- `STRIKE_SILENT` -> `strike_silent`, count 5
- `DEFEND_SILENT` -> `defend_silent`, count 5
- `DRAMATIC_ENTRANCE` -> `dramatic_entrance`, count 1

All observed deck cards were unupgraded.

The exporter still wrote only `screen_type: "exporter_status"`, `inspect-export` accepted the live file, and `recommend-export --confirmed` rejected it because status files are not recommendation input.

After the reward screen was skipped/left, installed `v0.2.12` reported `deck_identity_review_probe: "cleared"`, zeroed the deck identity review counts, and wrote `deck_identity_review_items: []`.

This result identifies the mapping gap but does not approve data changes, scoring changes, or live `card_reward` export.

## Repo-Local v0.2.13 Alias Decision

Repo-local `v0.2.13` resolves two reviewed public deck IDs to the existing manual advisor IDs:

- `STRIKE_SILENT` / `strike_silent` -> `strike`
- `DEFEND_SILENT` / `defend_silent` -> `defend`

This is an exporter status-diagnostic mapping normalization only. It does not add card data, change the `strike` or `defend` metadata, change scoring, change priors, change empirical rows, or write recommendation-ready run state.

The rationale is that current manual Silent examples already represent the Silent starter deck with `strike` x5 and `defend` x5. The live public IDs are class-specific strings for that same starter-card role in the observed deck, so mapping them to the existing manual IDs preserves current advisor behavior instead of introducing new data semantics.

Expected mapping impact for the observed 14-card deck:

- known deck cards: 13
- unknown deck cards: 1
- remaining unknown: `DRAMATIC_ENTRANCE` / `dramatic_entrance`

`DRAMATIC_ENTRANCE` remains blocked on a separate reviewed card-data packet. Do not infer card metadata or scoring from the public ID alone.

## Installed v0.2.13 Startup Result

The real STS2 mods-folder install-check was approved and `v0.2.13` installed successfully after STS2 was closed.

Startup verification passed:

- installed manifest reports `version: "v0.2.13"`
- live export reports `exporter_version: "0.2.13"`
- live export remains `screen_type: "exporter_status"`
- `card_reward_run_state_runtime_probe: "not_observed"`
- `deck_identity_review_probe: "not_observed"`
- `deck_identity_review_items: []`
- `card_reward_run_state_writes_recommendation_state: false`
- `inspect-export` accepts the live status file
- `recommend-export --confirmed` rejects the live file because it is still `exporter_status`

## Installed v0.2.13 Visible Reward-Screen Result

On a human-opened visible three-card reward screen, the live file still reported `screen_type: "exporter_status"` and `exporter_version: "0.2.13"`.

Deck identity review diagnostics reported:

- `deck_identity_review_probe: "ids_revealed_for_review"`
- `deck_identity_review_card_count: 14`
- `deck_identity_review_unique_card_count: 6`
- `deck_identity_review_mapping_known_count: 13`
- `deck_identity_review_mapping_unknown_count: 1`
- `deck_identity_review_error: null`

Known starter alias mappings:

- `STRIKE_SILENT` / `strike_silent` -> `strike`, count 5
- `DEFEND_SILENT` / `defend_silent` -> `defend`, count 5

Other known mappings:

- `NEUTRALIZE` -> `neutralize`
- `SURVIVOR` -> `survivor`
- `SLICE` -> `slice`

Remaining unknown mapping:

- `DRAMATIC_ENTRANCE` / `dramatic_entrance`, count 1

All observed deck cards were unupgraded.

The runtime presence diagnostic stayed protective:

- `card_reward_run_state_runtime_probe: "incomplete"`
- deck card ID read count 14
- deck mapping known count 13
- deck mapping unknown count 1
- `card_reward_run_state_writes_recommendation_state: false`

Visible reward identity review still mapped `CLOAK_AND_DAGGER`, `BOUNCING_FLASK`, and `INFINITE_BLADES` to reviewed Deckseer IDs.

`inspect-export` accepted the live status file. `recommend-export --confirmed` rejected it because it is still `exporter_status`.

## Installed v0.2.13 Clear-State Result

After the reward screen was skipped/left, the live file still reported `screen_type: "exporter_status"` and `exporter_version: "0.2.13"`.

Clear-state diagnostics reported:

- `card_reward_run_state_runtime_probe: "cleared"`
- `card_reward_run_state_runtime_last_event: "reward_skipped"`
- run-state booleans false and counts zero
- deck mapping known count 0
- deck mapping unknown count 0
- `deck_identity_review_probe: "cleared"`
- `deck_identity_review_items: []`
- `visible_card_reward_option_count: 0`
- `card_identity_review_probe: "cleared"`
- `card_identity_review_items: []`
- `card_reward_run_state_writes_recommendation_state: false`

`inspect-export` accepted the live clear-state file. `recommend-export --confirmed` rejected it because it is still `exporter_status`.

## Repo-Local v0.2.14 Dramatic Entrance Data Result

`docs/EXPORTER_CARD_REWARD_DRAMATIC_ENTRANCE_DATA_REVIEW.md` records the reviewed data decision for the remaining observed unknown deck mapping.

Repo-local changes:

- `data/cards/neutral.json` adds `dramatic_entrance` as a neutral/colorless 0-cost uncommon attack with 11 base AOE damage, 15 upgraded damage, `innate`, and `exhaust`.
- `quality_prior` stays `0.0` because this is seed identity/effect metadata, not a reviewed tier, empirical row, or scoring decision.
- repo-local `v0.2.14` adds `dramatic_entrance` to the exporter status-diagnostic mapping snapshot.

Expected mapping impact for the observed 14-card deck:

- deck mapping known count 14
- deck mapping unknown count 0

Installed `v0.2.14` startup verification passed while still writing only `screen_type: "exporter_status"`.

## Installed v0.2.14 Visible Reward-Screen Result

On a human-opened visible three-card reward screen, installed `v0.2.14` resolved the previously observed deck mapping gap while staying status-only:

- live export remained `screen_type: "exporter_status"`
- live export reported `exporter_version: "0.2.14"`
- `card_reward_run_state_runtime_probe: "run_state_seen"`
- deck card count and deck card ID read count were both 14
- deck mapping known count was 14
- deck mapping unknown count was 0
- `deck_identity_review_probe: "ids_revealed_for_review"`
- `deck_identity_review_mapping_known_count: 14`
- `deck_identity_review_mapping_unknown_count: 0`
- `DRAMATIC_ENTRANCE` mapped to `dramatic_entrance`
- `card_reward_run_state_writes_recommendation_state: false`

Visible reward identity review still mapped `CLOAK_AND_DAGGER`, `BOUNCING_FLASK`, and `INFINITE_BLADES` to reviewed Deckseer IDs.

`inspect-export` accepted the live status file. `recommend-export --confirmed` rejected it because it is still `exporter_status`.

## Safe Follow-Up Options

Safe next packets remain separate:

- Manual review packet: the user can provide the visible deck list or a manual run-state JSON, and Deckseer can compare it against existing card data without changing exporter behavior.
- Alias implementation packet: repo-local `v0.2.13` maps the reviewed Silent starter public IDs to existing manual starter IDs while keeping `DRAMATIC_ENTRANCE` unknown.
- Data packet: `docs/EXPORTER_CARD_REWARD_DRAMATIC_ENTRANCE_DATA_REVIEW.md` adds reviewed seed metadata for `dramatic_entrance`; future quality-prior changes still require reviewed tier, empirical, or scenario evidence.
- Export packet: only after complete deck/relic/potion mapping is proven and separately approved, implement `screen_type: "card_reward"` with `requires_user_confirmation: true`.

## Installed v0.2.14 Clear-State Result

After the reward screen was skipped/left, installed `v0.2.14` cleared the live review diagnostics while staying status-only:

- live export remained `screen_type: "exporter_status"`
- live export reported `exporter_version: "0.2.14"`
- `card_reward_run_state_runtime_probe: "cleared"`
- `card_reward_run_state_runtime_last_event: "reward_skipped"`
- run-state booleans false or absent
- deck card count 0
- deck mapping known count 0
- deck mapping unknown count 0
- `deck_identity_review_probe: "cleared"`
- `deck_identity_review_items: []`
- `visible_card_reward_option_count: 0`
- `card_identity_review_probe: "cleared"`
- `card_identity_review_items: []`
- `card_reward_run_state_writes_recommendation_state: false`

`inspect-export` accepted the live clear-state file. `recommend-export --confirmed` rejected it because it is still `exporter_status`.

## Current Blocker

At the time of this handoff, live `screen_type: "card_reward"` export still needed a separate approval packet even though the observed deck card mapping gap was resolved in the installed `v0.2.14` visible proof.

Follow-up, 2026-05-25: this blocker is historical. Later packets accepted ADR 4, resolved relic and potion mapping readiness, proved mixed reward freshness, and live-proved installed `v0.4.7` with a fully mapped confirmed card reward plus post-selection downgrade.
