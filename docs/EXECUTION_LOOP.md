# Deckseer Execution Loop

This document is the standing handoff for self-directed Deckseer work. Use it at the start of each autonomous run to choose the next small packet, stay inside project guardrails, and finish with reproducible verification.

## Current Goal

Deckseer is a local, deterministic, human-in-the-loop decision-support coach for Slay the Spire 2. The current product goal is to keep the manual JSON card reward advisor stable while moving toward a read-only/export-only companion exporter that writes user-visible JSON for Deckseer to inspect.

Healthy baseline:

- Working tree should start clean.
- `pytest` should pass.
- `deckseer qa --check-recommendation-baseline --check-accuracy --check-empirical-triage` should report `PASS`.
- `deckseer empirical-coverage --format text` is expected to report `REVIEW` while patch-context warnings remain visible.
- `deckseer accuracy-report --format text` should report `PASS` with nine accepted scenarios unless scenario coverage is intentionally expanded.

## Start Sequence

At the start of each run:

1. Read `README.md`, `docs/PROJECT_STATUS.md`, this file, exporter docs, `docs/ACCURACY_REVIEW.md`, `docs/EMPIRICAL_REVIEW.md`, and `docs/strategy_backlog.md`.
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
- Relic choice regression manifest packet: `relic-accuracy-report` checks three accepted Relic Choice V1 scenarios before relic metadata expands further.
- Relic metadata expansion readiness packet: `docs/RELIC_METADATA_EXPANSION_READINESS.md` defines the safe intake workflow for future tiny reviewed relic batches without changing data yet.
- Exporter static mod spike: `exporter_mod/DeckseerExporter` now builds a local STS2 mod that writes only `screen_type: "exporter_status"` JSON, and the real mod-written file passes `inspect-export`.
- Exporter card reward API recon: `docs/EXPORTER_CARD_REWARD_API_RECON.md` documents likely public reward, run-state, save-like, and hook surfaces from local `sts2.dll` metadata without implementing live export.
- Exporter card reward compile probe: `exporter_mod/DeckseerExporter/DeckseerExporterCode/CardRewardApiProbe.cs` verifies a narrower public API set and `docs/EXPORTER_CARD_REWARD_COMPILE_PROBE.md` records members that are metadata-visible but not public enough.

### 1. Expand Reviewed Accuracy Scenarios From Real Runs

- Impact: high; improves trust before scoring or exporter-driven workflows expand.
- Risk: medium; expected top choices require careful review.
- Dependencies: reviewed run states or user-provided examples.
- Likely files: `data/accuracy/scenarios.json`, `tests/fixtures/scenarios/`, and possibly card data only if a scenario reveals a reviewed defect.
- Validation: `accuracy-report --format text`, `qa --check-accuracy`, full pytest.
- Effort: medium.
- Status: blocked until a reviewed real-run state and expected top choice are available.

### 2. Exporter Status Diagnostic Install Check

- Impact: high; verifies the `v0.2.0` diagnostic status build in the real game-written export file.
- Risk: medium; modifies the local STS2 `mods/DeckseerExporter` package and requires a game relaunch.
- Dependencies: explicit approval to update the local STS2 mod package.
- Likely files: no repo source changes unless docs need observed-output updates.
- Validation: install build to the STS2 mods folder, launch from Steam, accept Load Mods if prompted, inspect `%LOCALAPPDATA%\Deckseer\exports\latest_state.json`.
- Effort: small.
- Guardrail: still no live card reward export; status/diagnostic metadata only.

### 3. Exporter Card Reward Contract Spike

- Impact: high; first real low-friction recommendation input.
- Risk: high; needs visible-screen proof and stable card ID mapping before export.
- Dependencies: Exporter Status Diagnostic Install Check or a repo-only Card Reward Visibility Design packet.
- Likely files: exporter mod source, exporter docs, exporter fixtures/tests if contract gaps appear.
- Validation: `inspect-export`, `recommend-export --confirmed`, scenario winners unchanged, full QA.
- Effort: large.

### 4. Relic/Potion Advice Design Packet

- Impact: medium; broadens Deckseer beyond card rewards while keeping deterministic advice.
- Risk: medium; could sprawl into combat simulation if not bounded.
- Dependencies: reviewed candidate relic evidence is needed before data expansion.
- Likely files: `data/relics/relics.json`, `data/relic_accuracy/scenarios.json`, relic fixtures, and relic metadata docs.
- Validation: data-health, `relic-accuracy-report`, `recommend-relic`, and standard QA.
- Effort: medium.
- Status: readiness complete; next data-changing packet is blocked until a tiny reviewed relic candidate batch is available.

### 5. Vision State Extractor Design Packet

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
- Accuracy report: `PASS`, 9/9 unless intentionally expanded.
- Relic accuracy report: `PASS`, 3/3 unless intentionally expanded.
- Pytest: green.

## Done Criteria

Each packet should finish with:

- Relevant docs updated.
- Focused tests run first when code changes.
- Full verification run for shared behavior or public-surface changes.
- Commit and push to `main` when configured.
- Final handoff that states what changed, verification results, current blocker, and recommended next task.

## Goal Mode Prompt

```text
You are working on Deckseer in D:\Codex\Deckseer.

Operate as a self-directed execution loop. Start each run by reading README.md, docs/PROJECT_STATUS.md, docs/EXECUTION_LOOP.md if present, exporter docs, accuracy/empirical docs, git status, and recent commits. Pick the highest-impact unblocked task that fits the guardrails. Prefer small focused packets.

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
- accuracy PASS, 9/9 unless intentionally expanded
- relic accuracy PASS, 3/3 unless intentionally expanded
- pytest green

After each packet, update relevant docs, commit with a concise message, push main if configured, and leave a clear handoff: what changed, verification, current blocker, and recommended next task.
```
