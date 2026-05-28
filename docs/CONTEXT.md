# Deckseer Context

Status: `active`

This document captures the shared language Deckseer uses across product discussion, docs, code, and future agent sessions. Keep it concise. Add terms when repeated explanation would otherwise be needed, or when fuzzy language could cause a boundary mistake.

## Product Frame

**Deckseer**

A local, deterministic, human-in-the-loop decision-support coach for Slay the Spire 2. Deckseer advises; it does not play the game.

**Advisor**

The deterministic recommendation path that ranks visible choices from structured state. The advisor is not an LLM, does not read the screen, and does not automate gameplay.

**Manual JSON**

The primary current workflow: the user supplies a structured JSON run state and visible reward options. Manual JSON remains the stable baseline even while exporter work advances.

**Human-confirmation-first**

Any non-manual state source must be inspectable before recommendation. If exporter metadata says `requires_user_confirmation: true`, `recommend-export` requires `--confirmed`.

## State Sources

**Run-history import**

Read-only parsing of plain `.run` history files. It can draft advisor input, but current live fields such as HP, floor, and visible rewards remain user-supplied.

**Exporter**

The proposed Slay the Spire 2 companion mod that writes local JSON for Deckseer. Exporter work must remain read-only/export-only and visible to the user.

**Exporter status**

`screen_type: "exporter_status"`. A harmless health/status payload from the exporter. It is not live run state and must not be treated as a recommendation input.

**Card reward export**

`screen_type: "card_reward"`. A live reward-state payload containing visible card reward IDs and enough proven run state for the existing adapter. Installed `v0.3.10` safely exports confirmed card rewards after mixed reward freshness gates and downgrades after card selection closes. Installed `v0.4.7` adds reviewed mapping coverage for `ENVENOM`, `MEMENTO_MORI`, `FASTEN`, and `BLOOD_VIAL`, live-proves confirmed `card_reward` export after the 15-gold mixed reward pickup, and live-proves post-selection downgrade back to `exporter_status`. Repo-local data and status-diagnostic snapshots now also cover the later `FINISHER` / `RICOCHET` / `MURDER` mapping subset from the same live run; the installed real mod package was not changed.

**Relic reward export**

`screen_type: "relic_reward"`. A fixture-backed export shape for visible relic choices. Deckseer can inspect and recommend from confirmed fixture-style files. ADR 7 accepts the human-confirmed live relic reward exporter boundary. Installed exporter `v0.4.1` observes treasure chest relics as status-only and clears after pickup. Installed `v0.4.2` removes the treasure relic identity exception but still reports a null public ID. Installed `v0.4.3` uses public `RelicModel.Id` directly, live-proves `LETTER_OPENER` as an unmapped review-only treasure relic ID, and still refuses live export. Installed `v0.4.4` maps reviewed `letter_opener` in status diagnostics and live-verifies mapped treasure clear-state. ADR 8 accepts a treasure route contract, installed `v0.4.5` safely refuses incomplete mapping state and clears after pickup, and installed `v0.4.6` proves successful treasure `relic_reward` export on a fully mapped run while preserving confirmation and post-pickup downgrade behavior.

**Vision state extractor**

A future screenshot/OCR fallback or complement. It is not part of current exporter work and requires explicit approval before implementation.

## Exporter Proof Terms

**Static spike**

The first exporter milestone: write a static `exporter_status` JSON file in-game and prove Deckseer can inspect it.

**Compile probe**

Repo-local source that references candidate STS2 APIs at compile time. A compile probe proves symbol availability only; it does not prove runtime visibility or correctness.

**Status-only diagnostic**

An exporter build that still writes only `screen_type: "exporter_status"` while adding diagnostic metadata. It may include counts/caveats when explicitly approved, but no card IDs or recommendation-ready live state.

**Visible reward screen**

The reward screen currently shown to the player. Exporter card reward work must prove that any observed reward model corresponds to this visible screen before exporting card IDs.

**Active RewardsSet source**

A public, read-only route to the currently visible `RewardsSet`. Current research has not found an approved source under the strict no-patching/no-UI-observation boundary.

**Boundary decision**

An explicit choice to allow, reject, or pause a route that changes project risk. Example: deciding whether a count-only public-method observation probe for `NRewardsScreen.ShowScreen(RewardsSet, ...)` is acceptable.

**Public screen observation**

An approved exporter visibility proof route that observes a public UI method such as `NRewardsScreen.ShowScreen(RewardsSet, ...)` without exporting card IDs or recommendation-ready live state. Approval is limited to count-only `exporter_status` diagnostics; see ADR 2.

**Card identity compile probe**

Repo-local exporter source that compile-checks public card identifier and upgrade-state paths such as `CardModel.Id` and `CardModel.CurrentUpgradeLevel`. It may report verified symbol names in `exporter_status` metadata, but it must not export live card IDs until a later explicitly approved packet.

**Status-Only ID-Shape Diagnostic**

Exporter source that reads public reward-screen or card-choice `CardModel` identity members and reports counts only, such as readable ID count, known/unknown mapping count, and upgraded count. It still writes `screen_type: "exporter_status"` and must not export raw STS2 IDs, Deckseer IDs, card names, selected-card identity, or recommendation-ready live state.

**Mapping review**

A repo-local review step that explains known/unknown exporter mapping counts without making the exporter reveal live IDs. Mapping review may compare user-visible labels and Deckseer data as evidence, but it must not guess inside the exporter or change scoring.

**ID-revealing diagnostic**

A temporary `exporter_status` diagnostic that reveals the minimum public card identity strings needed for human mapping review. ADR 3 accepts this diagnostic, installed `v0.2.9` has verified visible reward IDs and clear-state behavior, and it remains outside recommendation input.

**Deck ID review diagnostic**

An `exporter_status` diagnostic that reveals the minimum public deck card identity strings needed for human mapping review. ADR 5 accepts this boundary, installed `v0.2.12` implements it, installed `v0.2.13` adds reviewed Silent starter aliases for `STRIKE_SILENT` -> `strike` and `DEFEND_SILENT` -> `defend`, and repo-local `v0.2.14` adds the reviewed `DRAMATIC_ENTRANCE` -> `dramatic_entrance` mapping after the data review packet. It remains outside recommendation input and must not export HP, gold, act/floor/ascension, character, relic IDs, potion IDs, selected-card identity, or `screen_type: "card_reward"`.

**Relic/potion ID review diagnostic**

An `exporter_status` diagnostic that reveals the minimum public relic and potion identity strings needed for human mapping review. ADR 6 accepts this boundary, installed `v0.2.16` implements the ID reveal without writing recommendation-ready run state, and installed `v0.2.17` maps the reviewed `RING_OF_THE_SNAKE` -> `ring_of_the_snake` and `LEAD_PAPERWEIGHT` -> `lead_paperweight` IDs while still writing only `exporter_status`.

**Refusal-first live export**

The exporter computes and validates the full recommendation-ready payload before writing `screen_type: "card_reward"`. Any missing field, unmapped ID, stale screen, unsupported upgraded reward card, or unsafe state falls back to `screen_type: "exporter_status"` instead of writing partial advisor input.

**Mixed reward screen**

A reward flow that includes card choices plus other rewards such as gold, relics, or potions. Repo-local `v0.3.1` refuses live `card_reward` export for mixed reward screens because non-card reward pickup can change visible gold, relic, or potion state after the initial reward-screen observation.

**Post-pickup freshness probe**

Status-only diagnostics for mixed reward flows after non-card reward pickup. Installed `v0.3.2` checked `NChooseACardSelectionScreen.ShowScreen(...)` but did not fire on the observed route. Installed `v0.3.3` checks public `NRewardsScreen.RewardCollectedFrom(Control)`, refreshes serializable-run booleans/counts such as potion count, keeps `screen_type: "exporter_status"`, and does not export live scalar values or recommendation-ready state.

**Mixed reward freshness readiness contract**

Repo-local `v0.3.4` status-only diagnostics that summarize post-pickup readiness for mixed reward screens using stable blocker codes. The contract may say serializable counts were seen after `reward_collected`, but it still blocks live `card_reward` export until current run-state alignment, visible reward player alignment, potion identity mapping, and explicit mixed reward export approval are all resolved.

**Post-pickup potion identity review**

Installed `v0.3.5` status-only diagnostic that refreshes relic/potion identity review from the public serializable run after `reward_collected`, but only when a visible card reward observation is already active. It may reveal public potion IDs for human mapping review under ADR 6, but it must not export live `potions`, scalar run-state values, or recommendation-ready state. The first live proof revealed `COLORLESS_POTION` -> `colorless_potion` as unknown mapping evidence only.

**Reviewed colorless potion mapping**

Installed `v0.3.6` maps the reviewed `COLORLESS_POTION` -> `colorless_potion` evidence in the sparse potion catalog and exporter status-diagnostic mapping snapshot. It remains status-only, does not change scoring, potion advice, empirical data, baselines, or mixed reward live export approval, and still refuses mixed reward export on current-player/visible-reward-player alignment blockers.

**Reward-collected visible player context**

Installed `v0.3.7` kept the active public `RewardsSet` reference only while the reward screen remained active, so the status-only `reward_collected` probe could report that visible reward player context was still present after non-card reward pickup. It still did not export a visible player ID, live scalar values, top-level `potions`, or recommendation-ready state; run-state alignment remained blocked until the later `v0.3.8`/`v0.3.9` proofs.

**Reward-collected run-state context**

Installed `v0.3.8` kept the active public `IRunState` reference only while the reward screen remained active, so the status-only `reward_collected` probe could report that run-state context was still present after non-card reward pickup. It still did not export live scalar values, top-level `potions`, or recommendation-ready state; mixed reward live export remained blocked until explicit approval in the later `v0.3.9` packet.

**Mixed reward live card reward export**

Installed `v0.3.9` implements the explicit mixed reward export approval under ADR 4. Mixed reward screens still refuse before `reward_collected`, but after gold/potion pickup they may write `screen_type: "card_reward"` only when freshness gates are clean. Installed `v0.4.7` live-proves this path after a 15-gold pickup with all reward, deck, relic, and potion mappings known. The payload remains read-only/export-only, human-confirmation-first, and scorer-neutral.

**Card reward selection clear-state fix**

Installed `v0.3.10` adds the public `NCardRewardSelectionScreen._ExitTree()` close hook after the installed `v0.3.9` proof showed that selecting a card left the previous `card_reward` file stale. Live verification passed: after the card reward selection screen closed, the exporter downgraded to `exporter_status` with cleared diagnostics and `recommend-export --confirmed` rejected the closed-screen file. Installed `v0.4.7` reconfirmed this clear-state behavior after the Envenom/Predator/Memento Mori mixed reward proof.

**Event/special choice route gap**

Some visible choices in the live Silent run, including Pael, Tea Master, Doll relic, Amalgamator, shop-like choices, Potion Courier, Crystal Sphere, relic-looking event rows, and some post-event card choices, did not produce a fresh recommendation-ready exporter state in `v0.4.7`. Treat these as route-diagnosis evidence only. `TEA_OF_DISCOURTESY` is now mapped as sparse owned-relic data from local STS2 evidence, but Tea Master/event choice behavior remains separate from ordinary relic reward export until route behavior is reviewed. `docs/EXPORTER_EVENT_SPECIAL_ROUTE_CLASSIFIER_DESIGN.md` and ADR 9 define the status-only classifier shape; it does not approve option identity reveal or recommendation-ready event export. The repaired live deck-enchant diagnostic is installed, startup-verified as `screen_observation_probe: "registered"`, and active deck-enchant grid proof now shows `deck_enchant_selection_screen_shown` with 19 candidate cards as count-only status evidence. Relic-looking event rows inspected after that proof still used `public_event_layout_options`, not the pending `choose_relic_selection_screen_shown` overlay. User review now identifies multiplayer chest selection, where each player chooses one relic, as the likely source of the true choose-relic overlay. Future work should start with status-only diagnostics and reviewed mapping/data packets before any live export promotion.

**Exporter alert**

`deckseer export-alert`, a read-only CLI helper that inspects the user-visible exporter JSON and prints a loud terminal notification for pause-worthy states such as recommendation-ready card/relic exports, true choose-relic overlay proof, unexpected route shapes, new post-collection mapping gaps, unsupported reward shapes, or exporter diagnostic errors. Alert output labels `Codex attention: yes/no`, and mapping gaps already present in the current local repo data stay quiet even if the installed exporter mapping snapshot is older. Proven deck-enchant/status-only routes and pre-collection mixed reward screens are quiet by default. It watches the local JSON file by default and supports `--once` for a single check, but still does not read the screen, control gameplay, recommend choices, or modify game state.

**Deck-enchant diagnostic**

A status-only event/special route diagnostic for Self-Help Book style deck-enchantment card grids. The repaired installed build keeps only the public `NDeckEnchantSelectScreen.ShowScreen(...)` runtime hook and counts candidate cards without exporting card identities, enchantment identity, selected card, prompt text, or recommendation-ready state. It is not an ordinary card reward route.

**Live relic reward export boundary**

ADR 7 accepts a narrow live `screen_type: "relic_reward"` exporter mode using the existing confirmed relic exporter adapter. Installed `v0.4.0` observes normal visible relic reward options through public mod-accessible reward-screen state, requires user confirmation, refuses partial or stale state as `exporter_status`, and stays safe when a treasure chest relic uses a different route. Installed `v0.4.1` observes that treasure relic route as status-only, refuses live export with `treasure_relic_route_status_only`, and clears after pickup. Installed `v0.4.2` fixes the treasure relic identity exception but leaves the public ID null. Installed `v0.4.3` reads public `RelicModel.Id` directly before serialization fallback and live-proves non-null treasure relic identity while staying status-only. Installed `v0.4.4` proves reviewed treasure relic mapping coverage while still refusing live export. ADR 8 accepts treasure route promotion only when the public holder `IRunState`, run-state fields, deck, owned relics, potions, and reward relic all pass the same confirmation-first gates. Installed `v0.4.5` verifies this by refusing a mapped `LETTER_OPENER` treasure relic when `ACCURACY` and `HEART_OF_IRON` remain unmapped; installed `v0.4.6` maps those gaps and live-proves successful treasure `relic_reward` export on a fully mapped run.

**Treasure relic route**

The public chest-specific route for a visible treasure-room relic, separate from `NRewardsScreen.ShowScreen(...)`. Local metadata identifies `NTreasureRoomRelicHolder.Initialize(RelicModel, IRunState)` and `TreasureRoomRelicSynchronizer` as the first safe observation surface. Installed `v0.4.1` uses this for diagnostics only. Installed `v0.4.2` avoids `CanonicalModelException` while staying status-only, but the public ID remained null in live proof. Installed `v0.4.3` adds `RelicModel.Id` as the direct public identity source for the diagnostic, revealing `LETTER_OPENER` -> `letter_opener` as unknown mapping evidence. Installed `v0.4.4` marks `letter_opener` known after reviewed data, still status-only. Installed `v0.4.5` may promote this route to `screen_type: "relic_reward"` only when every ADR 8 gate passes; the first installed proof stayed `exporter_status` because mapping gates found `ACCURACY` and `HEART_OF_IRON` gaps. Installed `v0.4.6` maps those gaps and proves the route can export a confirmed `relic_reward`, then clear after pickup.

**Public run-state compile probe**

Exporter source that compile-checks public run-state and serializable run fields needed for a future human-confirmed `screen_type: "card_reward"` export. Installed `v0.2.10` adds this as `exporter_status` metadata only; it must not export live deck, HP, gold, relics, potions, or recommendation-ready state.

**Runtime presence diagnostic**

Exporter status-only diagnostic that checks whether public run-state fields are available during a visible reward screen by reporting booleans and counts only. Repo-local `v0.2.11` adds this probe; it must not export live character IDs, HP values, gold values, act/floor/ascension values, deck IDs, relic IDs, potion IDs, or recommendation-ready state.

## Safety Boundaries

**Read-only/export-only**

Exporter code may observe and write local JSON, but must not modify saves, profiles, reward generation, choices, input, network traffic, or process memory.

**No gameplay automation**

Deckseer must not click, type, choose rewards, farm runs, or control gameplay.

**No live capture**

No watch mode, OCR, screenshot reading, or live screen capture unless a future task explicitly authorizes that work.

**No private access workaround**

No private-field reflection, publicizer workaround, memory/process trick, or packet inspection for exporter state.

**No scoring drift**

Exporter and workflow packets must not change card scoring, priors, empirical data, accuracy expectations, recommendation behavior, or baselines unless the task explicitly asks for that and reviewed evidence supports it.

## Review And Evidence Terms

**Reviewed evidence**

A source, screenshot, run state, or scenario that has been inspected enough to justify changing data, scenarios, or expectations.

**Accuracy scenario**

A reviewed regression case that guards recommendation behavior for a card reward decision.

**Empirical row**

Traceable numeric evidence used for audit/review workflows. Empirical rows can inform review but do not automatically rewrite scoring.

**Triage-aware QA**

`qa --check-recommendation-baseline --check-accuracy --check-empirical-triage`. This is the preferred broad QA gate because it distinguishes unresolved empirical problems from documented non-blocking review flags.

**Patch mismatch warning**

An empirical audit flag showing evidence from a different patch context. Current healthy empirical coverage may still report `REVIEW` while these warnings remain visible.

## Documentation Rules

- Update this file when a term becomes repeated, overloaded, or important to safety.
- Prefer existing terms in new docs and code names.
- If a decision is hard to reverse, surprising without context, or a real tradeoff, add a short ADR under `docs/adr/`.
- Do not use this file for long design notes; link to the relevant doc instead.
