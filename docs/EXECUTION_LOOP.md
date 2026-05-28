# Deckseer Execution Loop

This document is the standing handoff for self-directed Deckseer work. Use it at the start of each autonomous run to choose the next small packet, stay inside project guardrails, and finish with reproducible verification.

## Current Goal

Deckseer is a local, deterministic, human-in-the-loop decision-support coach for Slay the Spire 2. The current product goal is to keep the manual JSON card reward advisor stable while moving toward a read-only/export-only companion exporter that writes user-visible JSON for Deckseer to inspect.

Healthy baseline:

- Working tree should start clean unless the current handoff explicitly identifies intentional local changes.
- Current handoff exception: branch `main` is ahead of `origin/main` by 4 local commits, and the worktree contains intentional uncommitted exporter/docs/test/data changes. Do not revert them and do not push unless explicitly asked.
- A local Codex skill, `deckseer-local-mvp-workflow`, exists at `C:\Users\moxhe\.codex\skills\deckseer-local-mvp-workflow`. Use it when available to keep Deckseer packets aligned with the current guardrails.
- `pytest` should pass.
- `deckseer qa --check-recommendation-baseline --check-accuracy --check-empirical-triage` should report `PASS`.
- `deckseer empirical-coverage --format text` is expected to report `REVIEW` while patch-context warnings remain visible.
- `deckseer accuracy-report --format text` should report `PASS` with ten accepted scenarios unless scenario coverage is intentionally expanded.

## Start Sequence

At the start of each run:

1. Use `$deckseer-local-mvp-workflow` if it is available in the session, then read `README.md`, `docs/PROJECT_STATUS.md`, `docs/CONTEXT.md`, this file, relevant ADRs under `docs/adr/`, exporter docs, `docs/ACCURACY_REVIEW.md`, `docs/EMPIRICAL_REVIEW.md`, and `docs/strategy_backlog.md`.
2. Check `git status --short` and recent commits.
3. Run the narrowest relevant health check for the candidate task.
4. Pick the highest-impact unblocked task from the roadmap below.
5. Keep the packet small enough to verify in one pass.

## Guardrails

- Preserve Deckseer as local, deterministic, human-in-the-loop decision support.
- Do not add gameplay automation, input control, memory/process tricks, packet inspection, stealth/evasion, live capture, OCR, or watch mode unless the current task explicitly allows it.
- Do not install external tools or modify game files without explicit approval.
- Do not change scoring, card priors, roles, empirical data, or recommendation behavior unless backed by reviewed scenario/empirical evidence and stated in the task.
- Keep exporter work read-only/export-only and user-confirmation-first.
- Prefer docs/design or read-only preflight packets when external toolchain work is blocked.
- Use narrow tests first, then full QA before handoff.

## Roadmap

Completed:

- Read-only `exporter-toolchain-preflight` CLI command for repeatable local exporter readiness checks. The expected current state is `ready_for_static_spike` when `.NET SDK`, STS2 templates, and Megadot/Godot are visible.
- First CLI decomposition slice: exporter command handling and registration now live in `src/deckseer/cli_exporter.py`, with `src/deckseer/cli.py` still preserving the public entrypoint.
- Second CLI decomposition slice: run-history save command handling and registration now live in `src/deckseer/cli_save.py`, preserving `inspect-save`, `import-run`, and `recommend-save`.
- Third CLI decomposition slice: single-file manual run-state command handling and registration now live in `src/deckseer/cli_run_state.py`, preserving `recommend-card`, `diagnose-run`, `check-run-data`, and `normalize-run`.
- Fourth CLI decomposition slice: catalog/data command handling and registration now live in `src/deckseer/cli_data.py`, preserving `list-cards`, `data-summary`, `data-review`, and `data-health`.
- Fifth CLI decomposition slice: review report command handling and registration now live in `src/deckseer/cli_review.py`, preserving `accuracy-report` and `audit-card-priors`.
- Sixth CLI decomposition slice: project QA command handling, batch run checks, and shared run-path helpers now live in `src/deckseer/cli_qa.py`, preserving `qa`, `qa-baseline`, and `check-runs`.
- Seventh CLI decomposition slice: read-only empirical overview command handling and registration now live in `src/deckseer/cli_empirical_overview.py`, preserving `empirical-coverage`, `empirical-intake`, `empirical-triage-report`, and `empirical-current-patch-review`.
- Eighth CLI decomposition slice: empirical worksheet, capture packet, cross-class readiness, and draft promotion command handling now live in `src/deckseer/cli_empirical_workflow.py`, preserving preview/write behavior and public CLI output.
- Large CLI dispatcher decomposition is complete for the current roadmap; `src/deckseer/cli.py` should remain a thin public entrypoint and command-order facade.
- Empirical intake cleanup: the stale initial Necrobinder proposed intake note is closed as superseded by reviewed promoted rows, and `empirical-intake` now reflects no pending proposed source-review work.
- Accuracy scenario intake readiness: `docs/ACCURACY_SCENARIO_INTAKE.md` now defines the evidence checklist, fixture template, review steps, and acceptance rules for future real-run scenario expansion.
- Advice module decision brief: `docs/ADVICE_MODULES_DECISION_BRIEF.md` now compares relic choice, potion usage, pathing, and combat planning, and recommends relic choice as the lowest-risk first broader advice target after explicit approval.
- Relic choice design packet: `docs/RELIC_CHOICE_DESIGN.md` now defines the proposed manual JSON input shape, output shape, metadata fields, scoring philosophy, confidence rules, validation plan, and stop rules without runtime changes.
- Relic metadata seed packet: `docs/RELIC_METADATA_SEED_PLAN.md` documents the tiny V1 seed, and the existing three relic records now carry roles, weak priors, pick context, and source notes without changing card reward behavior.
- Private relic choice scorer packet: `src/deckseer/relic_choice.py` can load manual `screen_type: "relic_reward"` JSON and rank the three seed relics with focused fixtures, without adding public CLI behavior.
- Relic choice CLI packet: `recommend-relic` now ranks manual relic reward JSON using JSON, text, or Markdown output, while card reward/exporter behavior remains unchanged.
- Relic exporter contract packet: `docs/EXPORTER_MOD_DESIGN.md` now documents a proposed future `screen_type: "relic_reward"` JSON shape and fixture without enabling live capture or scoring from exporter relic files.
- Inspect-only relic export adapter packet: `inspect-export` now accepts `screen_type: "relic_reward"` files and summarizes visible relic choices while `recommend-export` still rejects them.
- Confirmed relic export recommendation packet: `recommend-export` now dispatches confirmed `screen_type: "relic_reward"` files through the relic choice scorer.
- Relic choice regression manifest packet: `relic-accuracy-report` checks six accepted Relic Choice V1 scenarios before relic metadata expands further.
- Relic metadata expansion readiness packet: `docs/RELIC_METADATA_EXPANSION_READINESS.md` defines the safe intake workflow for future tiny reviewed relic batches without changing data yet.
- Exporter static mod spike: `exporter_mod/DeckseerExporter` now builds a local STS2 mod that writes only `screen_type: "exporter_status"` JSON, and the real mod-written file passes `inspect-export`.
- Exporter card reward API recon: `docs/EXPORTER_CARD_REWARD_API_RECON.md` documents likely public reward, run-state, save-like, and hook surfaces from local `sts2.dll` metadata without implementing live export.
- Exporter card reward compile probe: `exporter_mod/DeckseerExporter/DeckseerExporterCode/CardRewardApiProbe.cs` verifies a narrower public API set and `docs/EXPORTER_CARD_REWARD_COMPILE_PROBE.md` records members that are metadata-visible but not public enough.
- Exporter card reward visibility design: `docs/EXPORTER_CARD_REWARD_VISIBILITY_DESIGN.md` defines the proof sequence for showing public card choice data corresponds to the visible card reward screen before live export. The first custom-node, timer, and direct-run-hook attempts were rejected and rolled back to `v0.2.0`; the `v0.2.1` repo-local safe hook-model compile probe proves the `SingletonModel` + `ModelDb.Inject` + `ModelDb.Singleton<T>()` path without registering a live hook. ADR 2 approved count-only public screen observation. Installed `v0.2.2` registered safely but did not observe the tested visible two-card reward screen through `NRewardsScreen.ShowScreen(...)`; installed `v0.2.3` observes `NChooseACardSelectionScreen.ShowScreen(...)` and reports count-only diagnostics matching the visible two-card reward screen while still writing only `screen_type: "exporter_status"`. Installed `v0.2.4` clears those count-only diagnostics through public `NChooseACardSelectionScreen._ExitTree()` after the card-choice screen closes. Repo-local `v0.2.5` compile-checks `CardModel.Id`, upgrade state, and `ToSerializable()` identity surfaces without exporting live IDs. Installed `v0.2.7` proved a visible three-card reward can report counts through `NRewardsScreen.ShowScreen(...)` while identity counts stay zero. Installed `v0.2.8` adds status-only ID-shape count diagnostics for both public routes without exporting raw STS2 IDs or Deckseer IDs, and observed a visible three-card reward with 2 known and 1 unknown mapping by count only. Adapter contract fixtures now cover unknown IDs, upgraded deck cards, confirmation gating, caveats, and unsupported upgraded reward-object shape.
- Exporter card reward mapping review design: `docs/EXPORTER_CARD_REWARD_MAPPING_REVIEW_DESIGN.md` explains how to review the installed `v0.2.8` 2-known/1-unknown count without exporting live IDs, guessing from localized names inside the exporter, changing scoring, or adding card data in the exporter packet.
- Exporter card reward mapping review handoff: `docs/EXPORTER_CARD_REWARD_MAPPING_REVIEW.md` records the installed `v0.2.8` 2-known/1-unknown result as review evidence only. The visible labels explained the unknown count as a likely `infinite_blades` data-coverage gap; the reviewed card-data follow-up is now complete, but this still does not approve scoring drift or live-ID export changes.
- Exporter status mapping snapshot drift guard: `tests/test_exporter_mapping_snapshot.py` verifies the repo-local status-diagnostic mapping snapshot covers every current Deckseer card ID, so future reviewed card-data additions do not silently reduce known-mapping counts.
- Exporter card reward ID reveal contract: `docs/EXPORTER_CARD_REWARD_ID_REVEAL_CONTRACT.md` and accepted ADR 3 define the smallest status-only diagnostic that may reveal public card identity strings for mapping review. Installed `v0.2.9` visible-screen and clear-state verification passes, still as `exporter_status`; the observed three visible IDs mapped to `cloak_and_dagger`, `bouncing_flask`, and `infinite_blades`, then cleared after reward skip.
- Exporter card reward live export design: `docs/EXPORTER_CARD_REWARD_LIVE_EXPORT_DESIGN.md` and accepted ADR 4 define the human-confirmed `screen_type: "card_reward"` export boundary. Installed `v0.2.10` implements a status-only public run-state compile probe; installed `v0.3.10` implements mixed reward live export after clean post-pickup freshness gates and fixes the observed stale file after the card reward selection screen closes.
- Exporter card reward run-state symbol review: `docs/EXPORTER_CARD_REWARD_RUN_STATE_SYMBOL_REVIEW.md` concludes the `v0.2.10` symbols are necessary but not sufficient for live export. Installed `v0.2.11` implements a status-only runtime presence diagnostic; startup, visible reward-screen, and clear-state verification have passed the status-only boundary.
- Exporter card reward runtime presence probe: installed `v0.2.11` reports run-state readiness booleans and counts only under `screen_type: "exporter_status"`, with no live values or recommendation-ready state exported.
- Exporter card reward deck mapping gap review: `docs/EXPORTER_CARD_REWARD_DECK_MAPPING_GAP_REVIEW.md` records the installed `v0.2.11` 3-known/11-unknown live deck mapping count as review evidence only.
- Exporter card reward deck ID review diagnostic: ADR 5 is accepted, and installed `v0.2.12` implements a status-only deck ID reveal diagnostic. Startup, visible reward-screen, and clear-state verification passed; the unknown deck mappings were `STRIKE_SILENT` x5, `DEFEND_SILENT` x5, and `DRAMATIC_ENTRANCE` x1. Installed `v0.2.13` startup, visible reward-screen, and clear-state verification pass; it maps the reviewed Silent starter aliases to existing manual `strike`/`defend` IDs. Installed `v0.2.14` startup, visible reward-screen, and clear-state verification pass after adding reviewed seed data for `dramatic_entrance` and including it in the exporter status-diagnostic mapping snapshot; the visible proof reported 14 known deck mappings and 0 unknown deck mappings while still writing only `exporter_status`, then clear-state proof zeroed review diagnostics. Installed `v0.2.15` startup, visible reward-screen, and clear-state verification pass for refusal-first live export candidate diagnostics under `exporter_status`; visible proof refuses only because relic IDs remain unmapped/count-only, and clear-state proof clears diagnostics and refuses stale state. ADR 6 is accepted, and installed `v0.2.16` startup, visible reward-screen, and clear-state verification pass for the next status-only relic/potion ID review boundary.
- Exporter card reward relic/potion mapping review: `docs/EXPORTER_CARD_REWARD_RELIC_POTION_MAPPING_REVIEW.md` records the installed `v0.2.16` visible relic identity result as review evidence. `docs/EXPORTER_CARD_REWARD_RELIC_DATA_REVIEW.md` records the reviewed `ring_of_the_snake` and `lead_paperweight` metadata packet plus installed `v0.2.17` startup, visible reward-screen, and clear-state proof. The visible `v0.2.17` candidate is ready but still status-only; no potion IDs were observed.
- Exporter card reward live export implementation: repo-local `v0.3.0` wrote `screen_type: "card_reward"` only when the refusal-first candidate was ready, included `requires_user_confirmation: true`, exported only Deckseer IDs plus required scalar run-state fields, refused upgraded visible reward cards until a reward-upgrade contract exists, and fell back to `exporter_status` otherwise. Installed `v0.3.0` startup fallback passed, but the visible mixed reward proof failed human confirmation because exported gold and potions were stale after reward pickup. Installed `v0.3.1` now refuses mixed reward screens with `mixed_reward_screen_state_may_change`; startup, mixed reward-screen, and clear-state verification pass. Installed `v0.3.2` startup passed but did not observe a post-pickup card-choice route in the mixed reward flow. Installed `v0.3.3` adds status-only `RewardCollectedFrom` serializable-run freshness diagnostics and passes startup, post-gold/potion pickup, and clear-state verification. Installed `v0.3.4` adds status-only mixed reward freshness blocker diagnostics and passes startup, post-gold/potion pickup, and clear-state verification. Installed `v0.3.5` refreshes post-pickup relic/potion identity review from the serializable run and passes startup, post-gold/potion pickup, and clear-state verification; observed `COLORLESS_POTION` -> `colorless_potion` remains an unknown mapping. Installed `v0.3.6` maps that reviewed potion ID as known in status diagnostics and still refuses mixed reward export on alignment/approval blockers. Installed `v0.3.7` carries active public `RewardsSet` context across `reward_collected` so visible reward player context remains true while run-state alignment stays blocked. Installed `v0.3.8` carries active public `IRunState` context across `reward_collected` for diagnostics only. Installed `v0.3.9` allows mixed reward `card_reward` export after clean post-pickup freshness gates and still requires user confirmation; clear-state downgrade after card selection failed because the live route closes through `NCardRewardSelectionScreen._ExitTree()`. Installed `v0.3.10` adds that missing public hook and passes startup, visible `card_reward`, post-selection `exporter_status` downgrade, and closed-screen recommendation rejection checks.
- Exporter relic reward live export implementation: installed `v0.4.0` implements ADR 7 human-confirmed `screen_type: "relic_reward"` export for normal reward-screen relics. Installed `v0.4.1` proves treasure chest relic observation and clear-state as status-only using public chest relic surfaces. Installed `v0.4.2` fixes the treasure relic identity exception but still reports a null public ID in live proof. Installed `v0.4.3` uses public `RelicModel.Id` directly, reveals `LETTER_OPENER` -> `letter_opener` as unknown review evidence, keeps treasure relics status-only, and has a mapping handoff in `docs/EXPORTER_TREASURE_RELIC_MAPPING_REVIEW.md`. The reviewed `letter_opener` metadata, repo-local `v0.4.4` mapping snapshot update, installed `v0.4.4` startup proof, and installed mapped treasure clear-state proof are recorded in `docs/EXPORTER_TREASURE_RELIC_DATA_REVIEW.md`.
- Exporter treasure relic live export readiness: `docs/EXPORTER_TREASURE_RELIC_LIVE_EXPORT_READINESS.md` records why installed `v0.4.4` stayed status-only despite mapped identity and clear-state proof. ADR 8 is accepted, installed `v0.4.5` verifies the treasure route readiness contract safely refuses incomplete mapping state and clears after pickup, and installed `v0.4.6` proves successful treasure `relic_reward` export on a fully mapped run while preserving confirmation and post-pickup downgrade behavior.
- Exporter card reward live mapping gap review: `docs/EXPORTER_CARD_REWARD_LIVE_MAPPING_GAP_REVIEW.md` records the installed `v0.4.6` refusal for a visible Silent card reward screen with unknown reward cards `ENVENOM` and `MEMENTO_MORI`, unknown deck card `FASTEN`, and unknown owned relic `BLOOD_VIAL`. The reviewed data follow-up is installed/live-proven in `v0.4.7`: confirmed `card_reward` export after mixed reward gold pickup and post-selection downgrade both passed. The reviewed Envenom/Predator/Memento Mori state is now accepted as `silent_v047_envenom_attack_payoff_guard`, guarded by a narrow attack/Shiv payoff calibration and duplicate-copy pressure check.
- Later `v0.4.7` live coaching handoff: the same Silent run exposed more review-only exporter gaps after the accepted Envenom scenario. A later normal card reward screen remained `exporter_status` and revealed unmapped reward IDs `FINISHER`, `RICOCHET` (`Ricochet+`), and `MURDER`; the user took Finisher after tooltip review. The same status payload reported unmapped deck IDs `TOOLS_OF_THE_TRADE`, `PINPOINT`, and `ULTIMATE_DEFEND`, unmapped relic IDs `PAELS_EYE`, `TEA_OF_DISCOURTESY`, `CENTENNIAL_PUZZLE`, `MR_STRUGGLES`, `SHURIKEN`, `ORICHALCUM`, and `STRIKE_DUMMY`, and unmapped potion ID `BLESSING_OF_THE_FORGE`. Reviewed mapping/data subsets are now complete for those IDs, including `TEA_OF_DISCOURTESY` as sparse owned-relic mapping coverage. Event/special choice routes such as Pael, Tea Master, Doll relic, Amalgamator, shop-like choices, and some post-event card choices are documented as a route-diagnosis matrix; they still need status-only route classification before they can be exporter recommendation states.
- Exporter status diagnostic install check: the `v0.2.0` diagnostic status build was installed after explicit approval, launched in STS2, and the game-written `latest_state.json` passed `inspect-export` with compile-probe diagnostics.
- Read-only exporter alert helper: `export-alert` watches a local exporter JSON file by default and prints loud terminal alerts for pause-worthy exported states such as recommendation-ready rewards, true choose-relic overlay proof, unexpected special-route shapes, post-collection mapping gaps, unsupported reward shapes, or exporter diagnostic errors. Proven deck-enchant/status-only routes and pre-collection mixed reward screens are quiet by default. `--once` runs a single check. It does not recommend, confirm, read the screen, or control gameplay.
- Context and ADR workflow: `docs/CONTEXT.md` captures shared Deckseer vocabulary, `docs/adr/` records hard-to-reverse or surprising decisions, ADR 1 preserves the human-confirmed exporter boundary, and ADR 2 approves count-only public screen observation diagnostics.
- Codex workflow skill: `deckseer-local-mvp-workflow` was created under `C:\Users\moxhe\.codex\skills` as a SkillOpt-inspired compact checklist for future Deckseer sessions. It is outside the repo and contains no runtime code.

### 0. Fresh Thread Local-MVP Handoff

- Impact: high; ensures a new thread starts from the current live-MVP posture without redoing the handoff archaeology.
- Status: ready for the next thread. Branch `main` remains ahead of origin by 4 local commits, and the worktree remains intentionally dirty with exporter/docs/test/data work. Do not revert, commit, push, or update the real STS2 mods folder unless the user explicitly asks.
- Current live path: run STS2 normally with the already-installed exporter, run `tools\deckseer-play.cmd` or double-click `start-deckseer-exporter.cmd`, and pause only for loud `export-alert` states. Proven deck-enchant/status-only, pre-collection mixed reward states, and mapping gaps already covered by current local repo data are quiet by default; true choose-relic overlay proof, unexpected route shapes, new post-collection mapping gaps, unsupported shapes, diagnostic errors, and recommendation-ready reward exports remain important. Alert output labels whether Codex attention is useful.
- Installed exporter: still the live-proven `v0.4.7` package unless explicitly updated later. Repo-local mappings/data now include the recent Ironclad alert gaps, but those repo-local exporter source changes are not installed in the real mods folder.
- Next best packet: continue normal live-play validation with the restarted helper. If a loud alert fires, inspect `%LOCALAPPDATA%\Deckseer\exports\latest_state.json`; if it is a new useful proof shape, add a compact fixture/assertion; if it is a mapping gap, review evidence and add seed mappings/data without scoring drift.
- Verification already run for the latest alert-policy packet: focused `tests/test_exporter_state.py` reported `118 passed`, Wood Carvings deck-enchant smoke reported no important state, and `git diff --check` passed with existing LF-to-CRLF warnings.

### 0a. Latest v0.4.7 Live-Run Mapping Handoff

- Impact: high; converts the newest live proof failures into a clear, bounded next packet.
- Risk: medium; seed data must be reviewed from local STS2 evidence or another suitable source and must not become scoring drift.
- Dependencies: local STS2 localization/model evidence, screenshots/tooltips from the live run, and the latest `exporter_status` diagnostics.
- Likely files: Silent card data, relic/potion seed data, exporter mapping snapshot tests/fixtures, `docs/EXPORTER_CARD_REWARD_LIVE_MAPPING_GAP_REVIEW.md`, and focused model/exporter tests.
- Validation: `data-health`, focused model tests, exporter mapping snapshot tests, `accuracy-report`, `relic-accuracy-report`, triage-aware QA, and `git diff --check`.
- Effort: small to medium if split into mapping-only subsets.
- Status: completed for the reviewed mapping subsets and route documentation follow-up. Local data and repo-local status-diagnostic mapping snapshots now cover `FINISHER`, `RICOCHET`, `MURDER`, `TOOLS_OF_THE_TRADE`, `PINPOINT`, `ULTIMATE_DEFEND`, `PAELS_EYE`, `TEA_OF_DISCOURTESY`, `CENTENNIAL_PUZZLE`, `MR_STRUGGLES`, `SHURIKEN`, `ORICHALCUM`, `STRIKE_DUMMY`, and `BLESSING_OF_THE_FORGE`. Treat event/special route handling as a separate follow-up because route behavior is more ambiguous. `docs/EXPORTER_EVENT_SPECIAL_ROUTE_CLASSIFIER_DESIGN.md` and ADR 9 define the status-only route classifier shape, fixture expectations, no-recommendation boundary, public surface review, repo-local compile probe/runtime diagnostics, live startup proof, active event/special route proofs, and the repaired deck-enchant diagnostic. Installed `v0.4.7` event-route diagnostics have captured Ancient, Choose-a-Pack, Ranwid, Doll Room, Vakuu, Zen Weaver, Self-Help Book, Loot card-choice, Brain Leech, Sapphire Seed, Potion Courier, Crystal Sphere, and relic-looking event rows as `exporter_status` with no option identity or recommendation-ready state. Doll Room's "Take Some Time" follow-up, Vakuu's relic/consequence options, the puppet relic offer, and the weapon-gift relic offer all used `public_event_layout_options`, not the `NChooseARelicSelection` overlay hook. The Self-Help Book follow-up card-selection grid stayed status-only but did not populate the current card-choice counts, proving an unobserved post-event card-selection surface. The repaired live deck-enchant diagnostic is installed and active deck-enchant grid proof now reports `deck_enchant_selection_screen_shown`, `post_event_card_choice`, `deck_enchant_card_select`, and 19 candidate cards as count-only status evidence. Active choose-relic overlay proof is still pending; user review now suggests the likely route is a human-controlled multiplayer chest where each player chooses a relic, not ordinary solo treasure or relic-looking event rows. Do not promote live export by default.
- Guardrail: no scoring, priors, empirical rows, accuracy expectations, recommendation baselines, exporter behavior, live install, watch mode, OCR, input automation, or game-file changes unless explicitly approved.

### 1. Expand Reviewed Accuracy Scenarios From Real Runs

- Impact: high; improves trust before scoring or exporter-driven workflows expand.
- Risk: medium; expected top choices require careful review.
- Dependencies: reviewed run states or user-provided examples.
- Likely files: `data/accuracy/scenarios.json`, `tests/fixtures/scenarios/`, and possibly card data only if a scenario reveals a reviewed defect.
- Validation: `accuracy-report --format text`, `qa --check-accuracy`, full pytest.
- Effort: medium.
- Status: complete for the current Envenom-vs-Predator-vs-Memento-Mori candidate. Installed `v0.4.7` captured a fully mapped recommendation-ready state, and `silent_v047_envenom_attack_payoff_guard` now accepts Envenom as the expected top choice after reviewed scenario intake.

### 1a. Review Latest Card Reward Mapping Gaps

- Impact: high; unblocks the latest user-provided real-run card reward state for future accuracy-scenario review.
- Risk: medium; data additions must stay seed-level unless source evidence justifies more.
- Dependencies: local STS2 metadata or another reviewed source for `ENVENOM`, `MEMENTO_MORI`, `FASTEN`, and `BLOOD_VIAL`.
- Likely files: Silent card data, relic data, exporter mapping snapshots, focused model/mapping tests, and `docs/EXPORTER_CARD_REWARD_LIVE_MAPPING_GAP_REVIEW.md`.
- Validation: data-health, focused model and exporter mapping tests, `accuracy-report`, `relic-accuracy-report`, triage-aware QA.
- Effort: small to medium.
- Status: completed and installed/live-proven as `v0.4.7`, including post-selection clear-state downgrade. Do not change scoring, empirical rows, or baselines.

### 2. Exporter Status Diagnostic Install Check

- Impact: high; verifies the `v0.2.0` diagnostic status build in the real game-written export file.
- Risk: medium; modifies the local STS2 `mods/DeckseerExporter` package and requires a game relaunch.
- Dependencies: explicit approval to update the local STS2 mod package.
- Likely files: no repo source changes unless docs need observed-output updates.
- Validation: install build to the STS2 mods folder, launch from Steam, accept Load Mods if prompted, inspect `%LOCALAPPDATA%\Deckseer\exports\latest_state.json`.
- Effort: small.
- Guardrail: still no live card reward export; status/diagnostic metadata only.
- Status: completed; observed `exporter_version: "0.2.0"` and `diagnostics.card_reward_api_probe: "compiled"` in the game-written status file.

### 3. Exporter Card Reward Safe Hook Compile Probe

- Impact: high; unblocks a safer future visibility diagnostic by proving hook model registration before live installation.
- Risk: medium; compile-only exporter source changes avoid another runtime user-run risk.
- Dependencies: local STS2 metadata and the existing `v0.2.0` status-only exporter source.
- Likely files: exporter mod source and `docs/EXPORTER_CARD_REWARD_VISIBILITY_DESIGN.md`.
- Validation: local `dotnet build` to the repo-local mods target; exporter remains status-only; no game launch or live mod install.
- Effort: small to medium.
- Guardrail: no card IDs, deck, HP, gold, relics, potions, recommendation export, watch mode, OCR, or input automation.
- Status: completed in repo-local source as `v0.2.1`; the installed package remains rolled back to `v0.2.0`.

### 4. Exporter Card Reward Visibility Diagnostic

- Impact: high; proves public reward models track the visible card reward screen before exposing card IDs.
- Risk: high; prior custom Godot callback and direct `AbstractModel` hook attempts caused runtime errors.
- Dependencies: ADR 2 accepted count-only public screen observation, the installed `v0.2.2` check showed the tested visible reward screen uses a different public card-choice path, and the installed `v0.2.3` diagnostic matched that visible screen with count-only diagnostics.
- Likely files: exporter mod source and `docs/EXPORTER_CARD_REWARD_VISIBILITY_DESIGN.md`.
- Validation: installed diagnostic status file reports no card reward outside reward screens and option counts on visible card reward screens; `inspect-export` still accepts only `screen_type: "exporter_status"`.
- Effort: medium.
- Guardrail: no card IDs, deck, HP, gold, relics, potions, recommendation export, watch mode, OCR, or input automation.
- Status: installed `v0.2.8` reports status-only ID-shape counts for both public routes and still exports no IDs or names. Installed `v0.2.9` visible-screen and clear-state verification passes for the accepted ADR 3 ID-revealing status diagnostic, still as `exporter_status` and still outside recommendation input. The observed IDs were `CLOAK_AND_DAGGER`, `BOUNCING_FLASK`, and `INFINITE_BLADES`, mapped to reviewed Deckseer IDs `cloak_and_dagger`, `bouncing_flask`, and `infinite_blades`, then cleared after reward skip. Do not export `screen_type: "card_reward"` yet.

### 5. Exporter Card Reward Runtime Presence Probe

- Impact: high; first real low-friction recommendation input.
- Risk: medium-high; must prove required run-state fields are present at runtime without exporting their live values or recommendation-ready state.
- Dependencies: installed `v0.2.10` public run-state compile probe and `docs/EXPORTER_CARD_REWARD_RUN_STATE_SYMBOL_REVIEW.md`.
- Likely files: exporter mod source, exporter docs, exporter status fixture/tests.
- Validation: repo-local build, `inspect-export` status fixture, focused exporter tests, `git diff --check`.
- Effort: small to medium.
- Guardrail: no `screen_type: "card_reward"` yet, no watch mode, OCR, input automation, scoring/data changes, or game-state mutation.
- Status: installed `v0.2.11` startup, visible reward-screen, and clear-state verification passed as `exporter_status` only. The visible reward-screen runtime probe reported required fields present but `incomplete` because deck mapping counts were 3 known and 11 unknown. The review-only deck mapping gap handoff is complete, installed `v0.2.12` startup, visible reward-screen, and clear-state verification passed for the accepted ADR 5 deck ID review diagnostic, installed `v0.2.13` startup, visible reward-screen, and clear-state verification pass while resolving the Silent starter aliases, installed `v0.2.14` startup, visible reward-screen, and clear-state verification pass after mapping `dramatic_entrance`, installed `v0.2.15` startup, visible reward-screen, and clear-state verification pass for refusal-first candidate diagnostics under `exporter_status`, installed `v0.2.16` startup, visible reward-screen, and clear-state verification pass for relic/potion ID review diagnostics, and installed `v0.2.17` startup, visible reward-screen, and clear-state verification pass after mapping reviewed relic IDs. Installed `v0.3.0` startup fallback passed but mixed reward live export failed human confirmation due stale gold/potions. Installed `v0.3.1` startup, mixed reward-screen, and clear-state verification pass by staying status-only on mixed reward screens. Installed `v0.3.2` startup passed but did not observe a post-pickup card-choice route in the mixed reward flow. Installed `v0.3.3` proves reward collection can refresh serializable-run booleans/counts without exporting values. Installed `v0.3.4` adds mixed reward freshness status/blocker diagnostics. Installed `v0.3.5` proves post-pickup relic/potion identity review from the serializable run and revealed `COLORLESS_POTION` -> `colorless_potion` as unknown mapping evidence. Installed `v0.3.6` maps `COLORLESS_POTION` known as `colorless_potion`, reducing unmapped potion count to 0. Installed `v0.3.7` keeps visible reward player context present after `reward_collected`; mixed reward export remains blocked by run-state alignment and explicit approval. Installed `v0.3.8` keeps run-state context present after `reward_collected` in status diagnostics only. Installed `v0.3.9` approves mixed reward `card_reward` export after clean post-pickup freshness gates and passed startup, pre-pickup refusal, post-pickup export, unconfirmed rejection, and confirmed recommendation checks, but clear-state downgrade after card selection failed. Installed `v0.3.10` fixes that route with `NCardRewardSelectionScreen._ExitTree()` and passes live closed-screen downgrade plus recommendation rejection checks.

### 6. Relic Reward Live Export Packet

- Impact: high; extends the proven exporter path to the first broader advice module.
- Risk: medium-high; must prove visible relic reward observation and stale-state downgrade separately from card rewards.
- Dependencies: ADR 7 accepted, manual relic choice scorer, confirmed relic exporter adapter, installed `v0.3.10` card reward clear-state proof.
- Likely files: exporter mod source, exporter docs, exporter status/relic fixtures, and focused exporter/relic tests.
- Validation: repo-local build, `inspect-export` live relic fixture, unconfirmed rejection, confirmed recommendation, closed-state rejection, focused pytest, `git diff --check`.
- Effort: medium.
- Guardrail: no watch mode, OCR, input automation, scoring/data changes, save/profile access, or live install without explicit install step.
- Status: installed `v0.4.6` treasure live proof passed. Installed `v0.4.5` removed the route-only refusal only when all ADR 8 gates pass; that proof refused because `ACCURACY` and two `HEART_OF_IRON` potions were unmapped, then cleared after pickup. `v0.4.6` maps those gaps, adds fully mapped visible and post-pickup treasure fixtures, writes live `screen_type: "relic_reward"` on the observed fully mapped treasure screen, rejects unconfirmed recommendation, scores `letter_opener` after confirmation, and downgrades after pickup.
- Readiness note: `docs/EXPORTER_TREASURE_RELIC_LIVE_EXPORT_READINESS.md` records the successful live proof and the remaining guardrail that future treasure edge cases need their own narrow packets.

### 7. Relic/Potion Advice Design Packet

- Impact: medium; broadens Deckseer beyond card rewards while keeping deterministic advice.
- Risk: medium; could sprawl into combat simulation if not bounded.
- Dependencies: reviewed candidate relic evidence is needed before data expansion.
- Likely files: `data/relics/relics.json`, `data/relic_accuracy/scenarios.json`, relic fixtures, and relic metadata docs.
- Validation: data-health, `relic-accuracy-report`, `recommend-relic`, and standard QA.
- Effort: medium.
- Status: reviewed expansion complete for `ring_of_the_snake`, `lead_paperweight`, and `letter_opener`; future data-changing packets should still stay tiny, reviewed, and guarded by relic accuracy scenarios.

### 8. Vision State Extractor Design Packet

- Impact: medium; useful fallback if exporter tooling remains blocked.
- Risk: medium-high; OCR/capture can invite complexity and UX ambiguity.
- Dependencies: explicit confirmation that vision should compete with exporter work.
- Likely files: design docs first; later `src/deckseer/vision/`.
- Validation: fixture screenshot-only tests if implemented; no live capture initially.
- Effort: medium to large.

## Stop Or Ask Rules

Ask before:

- Installing external tools.
- Modifying STS2 install files, save files, profile files, or app data outside the repo.
- Adding C# mod source or deciding whether the mod lives in this repo or a separate package.
- Adding new public CLI commands unless the task explicitly asks for them.
- Changing scoring, card priors, roles, tags, empirical data, recommendation APIs, or baselines.
- Starting vision/OCR/live capture work.

Stop and report if:

- The working tree has unrelated changes that conflict with the task.
- Verification fails and the fix would broaden the packet beyond the requested scope.
- Public sources or local STS2 metadata contradict the exporter setup docs.

## Default Verification

Use the bundled Python runtime if plain `python` is not on PATH.

```bash
python -m deckseer.cli inspect-export tests/fixtures/exporter_status_state.json
python -m deckseer.cli recommend-export tests/fixtures/exporter_card_reward_state.json --confirmed --format text
python -m deckseer.cli recommend-export tests/fixtures/exporter_relic_reward_state.json --confirmed --format text
python -m deckseer.cli exporter-toolchain-preflight --format text
python -m deckseer.cli recommend-relic tests/fixtures/relic_choice/elite_frontload.json --format text
python -m deckseer.cli qa --check-recommendation-baseline --check-accuracy --check-empirical-triage
python -m deckseer.cli empirical-coverage --format text
python -m deckseer.cli accuracy-report --format text
python -m deckseer.cli relic-accuracy-report --format text
python -m pytest
```

Expected healthy state:

- Triage-aware QA: `PASS`.
- Exporter toolchain preflight: `ready_for_static_spike` when `.NET SDK`, STS2 templates, and Megadot/Godot are visible.
- Empirical coverage: `REVIEW`, 18 rows, 14 `patch_mismatch` warnings unless intentionally changed.
- Accuracy report: `PASS`, 10/10 unless intentionally expanded.
- Relic accuracy report: `PASS`, 6/6 unless intentionally expanded.
- Pytest: green.

## Done Criteria

Each packet should finish with:

- Relevant docs updated.
- Shared vocabulary or ADRs updated when the packet sharpens project language or records a hard decision.
- Focused tests run first when code changes.
- Full verification run for shared behavior or public-surface changes.
- Commit only when requested or configured for the packet; push only when explicitly requested.
- Final handoff that states what changed, verification results, current blocker, and recommended next task.

## Goal Mode Prompt

```text
You are working on Deckseer in D:\Codex\Deckseer.

Operate as a self-directed execution loop. Start each run by reading README.md, docs/PROJECT_STATUS.md, docs/CONTEXT.md, docs/EXECUTION_LOOP.md if present, relevant docs/adr records, exporter docs, accuracy/empirical docs, git status, and recent commits. Pick the highest-impact unblocked task that fits the guardrails. Prefer small focused packets.

Guardrails:
- Preserve Deckseer as local, deterministic, human-in-the-loop decision support.
- Do not add gameplay automation, input control, memory/process tricks, packet inspection, stealth/evasion, live capture, OCR, or watch mode unless the current task explicitly allows it.
- Do not install external tools or modify game files without explicit approval.
- Do not change scoring, card priors, roles, empirical data, or recommendation behavior unless backed by reviewed scenario/empirical evidence and stated in the task.
- Keep exporter work read-only/export-only and user-confirmation-first.
- Prefer docs/design or read-only preflight packets when external toolchain is blocked.
- Use narrow tests first, then full QA before handoff.

Default verification:
- python -m deckseer.cli inspect-export tests/fixtures/exporter_status_state.json
- python -m deckseer.cli recommend-export tests/fixtures/exporter_card_reward_state.json --confirmed --format text
- python -m deckseer.cli recommend-export tests/fixtures/exporter_relic_reward_state.json --confirmed --format text
- python -m deckseer.cli exporter-toolchain-preflight --format text
- python -m deckseer.cli recommend-relic tests/fixtures/relic_choice/elite_frontload.json --format text
- python -m deckseer.cli qa --check-recommendation-baseline --check-accuracy --check-empirical-triage
- python -m deckseer.cli empirical-coverage --format text
- python -m deckseer.cli accuracy-report --format text
- python -m deckseer.cli relic-accuracy-report --format text
- python -m pytest

Expected healthy state:
- triage-aware QA PASS
- exporter toolchain preflight ready_for_static_spike when local toolchain remains visible
- empirical coverage REVIEW with 18 rows and 14 patch_mismatch warnings unless intentionally changed
- accuracy PASS, 10/10 unless intentionally expanded
- relic accuracy PASS, 6/6 unless intentionally expanded
- pytest green

After each packet, update relevant docs, commit only when requested or configured for the packet, push only when explicitly requested, and leave a clear handoff: what changed, verification, current blocker, and recommended next task.
```
