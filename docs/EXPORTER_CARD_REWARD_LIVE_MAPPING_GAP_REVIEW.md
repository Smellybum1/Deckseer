# Deckseer Exporter Card Reward Live Mapping Gap Review

Status: `latest_v047_event_route_gap_reviewed`

Prepared on 2026-05-25 after installed `v0.4.6` observed a visible Silent card reward screen but safely refused live `card_reward` export because current mapping coverage was incomplete.

## Scope

This note records review-only handoffs for live card reward mapping gaps and later event/special route gaps. It does not approve data, scoring, or exporter behavior changes unless a reviewed follow-up section explicitly says so.

It does not approve:

- card, relic, or potion data additions
- card prior, role, tag, empirical, accuracy, recommendation, or baseline changes
- treating this state as an accepted accuracy scenario
- changing exporter confirmation behavior
- watch mode, OCR, screenshot capture, input automation, memory/process tricks, packet inspection, save/profile modification, or game-file changes

## Observed Evidence

The installed exporter stayed protective:

- `screen_type: "exporter_status"`
- `exporter_version: "0.4.6"`
- `card_reward_live_export_candidate: "refused"`
- refusal reasons: `unknown_reward_card`, `unknown_deck_card`, `unmapped_relic`
- `card_reward_live_export_unmapped_reward_count: 2`
- `card_reward_live_export_unmapped_deck_count: 1`
- `card_reward_live_export_unmapped_relic_count: 1`
- `card_reward_live_export_unmapped_potion_count: 0`
- `card_reward_live_export_candidate_writes_recommendation_state: false`

Visible reward identity review:

| Position | Public model ID | Normalized candidate | Deckseer mapping status | Deckseer ID |
| ---: | --- | --- | --- | --- |
| 0 | `ENVENOM` | `envenom` | `unknown` | null |
| 1 | `PREDATOR` | `predator` | `known` | `predator` |
| 2 | `MEMENTO_MORI` | `memento_mori` | `unknown` | null |

The user screenshot matched the visible reward labels:

- Envenom
- Predator
- Memento Mori

Additional current-run mapping gaps:

| Surface | Public model ID | Normalized candidate | Deckseer mapping status |
| --- | --- | --- | --- |
| Deck card | `FASTEN` | `fasten` | `unknown` |
| Owned relic | `BLOOD_VIAL` | `blood_vial` | `unknown` |

Potion mapping was complete for the observed state:

- `COLORLESS_POTION` -> `colorless_potion`
- `HEART_OF_IRON` -> `heart_of_iron`

## User Review Note

The user intended to pick Envenom.

Rationale, summarized:

- Predator was already in the deck.
- Memento Mori looked weak in this context.
- Envenom had worked well for the user with Shivs in prior runs.
- Envenom is rare and may not appear again.
- The next path was a question-mark room followed by an elite.

This note is useful future scenario context, but the state is not accuracy-scenario-ready while reward, deck, and relic mappings are incomplete.

## Review Interpretation

The exporter behaved correctly by refusing recommendation-ready `card_reward` output when any required mapping gate failed.

The observed gaps are normal reviewed-data candidates:

- `envenom`
- `memento_mori`
- `fasten`
- `blood_vial`

Any follow-up should review local STS2 metadata or another suitable source before adding records. If added, keep the packet small, preserve weak/neutral priors unless reviewed evidence justifies more, update exporter mapping snapshots, and run data-health plus focused exporter mapping tests.

## Reviewed Follow-Up

Accepted on 2026-05-25:

- Added seed-level Silent card records for `envenom`, `memento_mori`, and `fasten` from local STS2 `v0.106.1` localization and the installed `v0.4.6` diagnostic proof.
- Added seed-level relic metadata for `blood_vial` from local STS2 `v0.106.1` localization and the installed `v0.4.6` diagnostic proof.
- Kept the three new Silent card priors neutral and marked them as seed metadata only; no scoring rules, empirical rows, accuracy expectations, or recommendation baselines changed.
- Updated repo-local exporter status-diagnostic mapping snapshots and bumped repo-local source to `v0.4.7`.
- Installed `v0.4.7` after explicit approval and verified startup writes a valid `exporter_status` payload with `exporter_version: "0.4.7"`.
- Live-proved `v0.4.7` on the same Envenom/Predator/Memento Mori reward route after the 15-gold mixed reward was collected. The exporter wrote confirmed `screen_type: "card_reward"` with all reward, deck, relic, and potion mappings known.
- Live-proved the post-selection clear-state route: after the card reward selection screen closed, `v0.4.7` downgraded to `screen_type: "exporter_status"`, cleared reward/deck/relic/potion identity diagnostics, and rejected confirmed recommendation.

Before scenario intake, the observed Envenom reward screen was review evidence only. The then-current confirmed recommendation ranked Skip first, Predator second, Memento Mori third, and Envenom fourth; that mismatch became the review input for the accepted accuracy scenario below.

## Recommended Next Packet

Scenario-intake review on 2026-05-25 created `tests/fixtures/scenarios/silent_v047_envenom_predator_memento_mori_review.json` as a manual run-state fixture.

The expected-choice decision is accepted:

- Human review favored Envenom because Predator was already owned, Memento Mori looked weak, Envenom had worked well with Shivs, Envenom is rare, and the path showed an event before an elite.
- The manual scenario fixture adds the reviewed event-before-elite path context and accepts Envenom as the top choice.
- The scoring follow-up adds a narrow attack/Shiv payoff calibration for `attack_payoff` cards and a modest duplicate-copy pressure risk for already-owned non-scaling payoff cards in larger decks.

The accepted manifest entry is `silent_v047_envenom_attack_payoff_guard`. This packet does not approve broader Envenom buffs beyond attack/Shiv payoff support.

The completed live proof verified `screen_type: "card_reward"` with:

- no unmapped reward cards
- no unmapped deck cards
- no unmapped owned relics
- no unmapped potions

Future packets should not change scoring rules, empirical rows, accuracy expectations, recommendation baselines, watch mode, OCR, input automation, or exporter behavior beyond the already reviewed mapping snapshot coverage unless separately approved.

## Later v0.4.7 Live-Run Follow-Up

After the accepted Envenom scenario packet, the same live Silent run continued as coaching/review evidence only. No additional scoring, data, baseline, or exporter behavior changes are approved by this note.

The installed `v0.4.7` exporter remained protective. On a later normal card reward screen, the latest `latest_state.json` was still `screen_type: "exporter_status"` rather than recommendation-ready `card_reward`.

Observed refusal context:

- `exporter_version: "0.4.7"`
- `card_reward_live_export_candidate: "refused"`
- refusal reasons included `unknown_reward_card`, `unsupported_upgraded_reward_card`, `unknown_deck_card`, `unmapped_relic`, `unmapped_potion`, and `mixed_reward_screen_state_may_change`
- visible card reward count was 3
- visible reward identities were revealed for mapping review only

Visible reward identity review:

| Position | Public model ID | Normalized candidate | Deckseer mapping status | Notes |
| ---: | --- | --- | --- | --- |
| 0 | `FINISHER` | `finisher` | `unknown` | User took Finisher after review. |
| 1 | `RICOCHET` | `ricochet` | `unknown` | Upgraded visible reward card: `Ricochet+`. |
| 2 | `MURDER` | `murder` | `unknown` | Tooltip observed: 3-cost attack, deals 1 plus 1 per card drawn this combat. |

Current run-state mapping gaps also observed in the same status payload:

| Surface | Public model ID | Normalized candidate |
| --- | --- | --- |
| Deck card | `TOOLS_OF_THE_TRADE` | `tools_of_the_trade` |
| Deck card | `PINPOINT` | `pinpoint` |
| Deck card | `ULTIMATE_DEFEND` | `ultimate_defend` |
| Owned relic | `PAELS_EYE` | `paels_eye` |
| Owned relic | `TEA_OF_DISCOURTESY` | `tea_of_discourtesy` |
| Owned relic | `CENTENNIAL_PUZZLE` | `centennial_puzzle` |
| Owned relic | `MR_STRUGGLES` | `mr_struggles` |
| Owned relic | `SHURIKEN` | `shuriken` |
| Owned relic | `ORICHALCUM` | `orichalcum` |
| Owned relic | `STRIKE_DUMMY` | `strike_dummy` |
| Potion | `BLESSING_OF_THE_FORGE` | `blessing_of_the_forge` |

Additional live coaching observations:

- Event/special choice screens such as Pael, Tea Master, Doll relic selection, Amalgamator, and some post-event card choices were better handled from screenshots because the exporter often remained on status/closed-state diagnostics rather than a fresh recommendation-ready card reward.
- Shop relic/card review surfaced likely future mapping candidates including `centennial_puzzle`, `red_mask`, and `gnarled_hammer`; only `centennial_puzzle` was bought in the live run.
- A later boss reward screen showed Fan of Knives, Shadowmeld, and Echoing Slash; this was not exported as a confirmed recommendation-ready payload during this handoff pass.

Historical recommended next packet before the mapping subset:

1. Do a reviewed mapping/data packet for the latest `v0.4.7` live-run gaps only if local STS2 evidence or another reviewed source is available.
2. Keep the packet data-only/status-snapshot-only; do not change scoring, priors, empirical rows, accuracy expectations, recommendation baselines, or exporter behavior.
3. Prefer the highest-unblocking subset first: `finisher`, `ricochet`, `murder`, `tools_of_the_trade`, `pinpoint`, `ultimate_defend`, `paels_eye`, `centennial_puzzle`, `mr_struggles`, `shuriken`, `orichalcum`, `strike_dummy`, and `blessing_of_the_forge`.
4. Separately document, but do not implement without approval, the event/special choice route gap where visible choices are not becoming recommendation-ready exporter states.

## Reviewed v0.4.7 Mapping Subset

Accepted on 2026-05-25:

- Added seed-level Silent card records for `finisher`, `ricochet`, `murder`, `tools_of_the_trade`, and `pinpoint` from local STS2 `v0.106.1` pck localization plus installed `v0.4.7` diagnostic proof.
- Added seed-level neutral/special card metadata for `ultimate_defend` from local STS2 `v0.106.1` pck localization plus installed `v0.4.7` diagnostic proof.
- Added seed-level relic metadata for `paels_eye`, `centennial_puzzle`, `mr_struggles`, `shuriken`, `orichalcum`, and `strike_dummy` from local STS2 `v0.106.1` pck localization plus installed `v0.4.7` diagnostic proof.
- Added sparse potion metadata for `blessing_of_the_forge` from local STS2 `v0.106.1` pck localization plus installed `v0.4.7` diagnostic proof.
- Updated repo-local exporter status-diagnostic mapping snapshots so future status payloads can count those IDs as known after a repo-local build, while leaving the installed real mod package untouched.

That mapping subset left `tea_of_discourtesy` for a separate follow-up because the live handoff identified Tea Master/event-choice behavior as a route gap. It also did not approve scoring, priors beyond neutral seed metadata, empirical rows, accuracy expectations, recommendation baselines, exporter behavior changes, live install, watch mode, OCR, input automation, memory/process tricks, packet inspection, save/profile modification, or game-file changes.

## Event/Special Route Diagnosis Review

Accepted on 2026-05-25 as a documentation-only route diagnosis packet.

The current proven exporter routes are ordinary visible reward routes:

- Confirmed `screen_type: "card_reward"` after clean mixed reward freshness gates, including the installed `v0.4.7` Envenom/Predator/Memento Mori proof.
- Confirmed `screen_type: "relic_reward"` for normal relic rewards and the installed `v0.4.6` fully mapped treasure relic proof.
- Post-selection and post-pickup downgrade back to `screen_type: "exporter_status"` for the proven card and treasure relic routes.

The remaining event/special screens are not recommendation-ready exporter states. Treat them as route evidence only until a later status-only diagnostic packet records a public observation surface and clear-state behavior.

| Observed surface | Current exporter output/evidence | Why it is not recommendation-ready | Safest next proof |
| --- | --- | --- | --- |
| Pael event/special choice | Live coaching was handled from screenshots/status evidence, not a fresh confirmed reward export. | The visible choice route is not proven to be an ordinary `card_reward` or `relic_reward` route. | Add a status-only route classifier that reports event/special route kind and clear-state, without IDs or live recommendation payload. |
| Tea Master / `TEA_OF_DISCOURTESY` | `TEA_OF_DISCOURTESY` appeared as an owned-relic mapping gap in the same live-run diagnostics. | The identity can be mapped from local STS2 evidence, but Tea Master choice behavior is still event-route evidence rather than an ordinary relic reward route. | Use `tea_of_discourtesy` only as owned-relic mapping coverage for now; add a Tea route diagnostic before any recommendation-ready event export. |
| Doll relic selection | Live coaching evidence only; no confirmed exporter recommendation payload. | The selection shape may be event-specific rather than a normal reward relic route. | Status-only route observation that distinguishes selection screen, option count, and closed-state behavior. |
| Amalgamator | Live coaching evidence only; no confirmed exporter recommendation payload. | The choice may mix event state and reward-like choices outside the approved reward contracts. | Status-only route observation before any identity reveal or recommendation export. |
| Shop-like choices | Live coaching surfaced future mapping candidates such as `centennial_puzzle`, `red_mask`, and `gnarled_hammer`; only `centennial_puzzle` was bought and mapped in the first subset. | Shop choice advice would require shop/path economy context outside current card/relic reward contracts. | Keep shop-like screens out of live export; if needed, write a separate design note for shop advice. |
| Post-event card choices | Some post-event card choices were better handled from screenshots because the exporter remained on status/closed-state diagnostics. | The route is not proven to carry the same freshness and visible-reward alignment as ordinary card rewards. | Status-only route classifier plus clear-state proof before any card identity reveal or live export promotion. |

No repo-local fixture was added in this packet because the repository does not currently contain captured event/special `exporter_status` payloads with enough route-specific diagnostics to assert. Future fixture work should use captured status payloads only; do not fabricate event route evidence.

This review does not approve a live mod install, C# exporter behavior change, scoring change, empirical row, accuracy expectation, recommendation baseline, watch mode, OCR, input automation, memory/process trick, packet inspection, save/profile modification, or game-file change.

Follow-up design packet: `docs/EXPORTER_EVENT_SPECIAL_ROUTE_CLASSIFIER_DESIGN.md` and proposed ADR 9 define a future status-only route classifier shape for these event/special screens. That design still writes only `exporter_status` and does not approve route recommendation export, option identity reveal, live install, or game-file changes.

## Reviewed Tea Mapping Follow-Up

Accepted on 2026-05-25:

- Added sparse relic metadata for `tea_of_discourtesy` from local STS2 `v0.106.1` pck localization plus installed `v0.4.7` diagnostic proof.
- Kept the record neutral and seed-only: tags capture that it is a Dazed/status/drawback event relic, with no role that solves a relic-choice need.
- Updated the repo-local relic/potion status-diagnostic mapping snapshot so future repo-local builds can count `TEA_OF_DISCOURTESY` as known.

This is a mapping/data packet only. Tea Master and other event/special choice routes remain status-only route gaps; this does not approve event export, live install, scorer changes, priors, empirical rows, accuracy expectations, recommendation baselines, watch mode, OCR, input automation, memory/process tricks, packet inspection, save/profile modification, or game-file changes.

## Local MVP Ironclad Alert Mapping Follow-Up

Accepted on 2026-05-27 after `deckseer export-alert` fired during a human-controlled Ironclad run on a mixed loot screen.

The live exporter correctly stayed protective as `screen_type: "exporter_status"` and refused recommendation-ready `card_reward` output. Refusal reasons included `unknown_reward_card`, `unknown_deck_card`, `unmapped_relic`, and `mixed_reward_screen_state_may_change`.

Observed review-only identities:

| Surface | Public model ID | Normalized candidate | Follow-up |
| --- | --- | --- | --- |
| Visible reward card | `HEADBUTT` | `headbutt` | Already mapped. |
| Visible reward card | `PERFECTED_STRIKE` | `perfected_strike` | Added seed Ironclad card metadata. |
| Visible reward card | `THUNDERCLAP` | `thunderclap` | Added seed Ironclad card metadata. |
| Visible reward card | `DOMINATE` | `dominate` | Added seed Ironclad card metadata after normal hallway reward alert. |
| Visible reward card | `ARMAMENTS` | `armaments` | Added seed Ironclad card metadata after mixed gold/card reward alert. |
| Visible reward card | `SETUP_STRIKE` | `setup_strike` | Added seed Ironclad card metadata after mixed gold/card reward alert. |
| Deck card alias | `STRIKE_IRONCLAD` | `strike_ironclad` | Added repo-local exporter alias to existing `strike`. |
| Deck card alias | `DEFEND_IRONCLAD` | `defend_ironclad` | Added repo-local exporter alias to existing `defend`. |
| Owned relic | `LOST_COFFER` | `lost_coffer` | Added sparse relic metadata. |
| Carried potion | `ATTACK_POTION` | `attack_potion` | Added sparse potion metadata after post-pickup alert. |

Local STS2 `v0.106.1` pck localization provided title/description evidence for `PERFECTED_STRIKE`, `THUNDERCLAP`, `STRIKE_IRONCLAD`, `DEFEND_IRONCLAD`, and `LOST_COFFER`. This packet updates repo-local data and status-diagnostic mapping snapshots only. It does not install a new exporter build, change the real STS2 mods folder, approve scoring-rule changes, empirical rows, accuracy expectations, recommendation baselines, OCR/live capture, input automation, save/profile changes, or game-file changes.

After the user took the potion but before opening the card reward, the same screen wrote a second status alert with the same card/deck/relic blockers plus `unmapped_potion`. The status-only potion identity review revealed `ATTACK_POTION` -> `attack_potion`, so the sparse potion catalog and repo-local relic/potion mapping snapshot now include `attack_potion`. The installed exporter is still `v0.4.7` until an explicit mod-folder install is approved later.
