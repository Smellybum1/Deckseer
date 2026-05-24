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

- Read-only `exporter-toolchain-preflight` CLI command for repeatable local exporter readiness checks. The expected current state is `blocked_missing_toolchain` until `.NET SDK`, STS2 templates, and Megadot/Godot are visible.

### 1. Decompose The Large CLI Dispatcher

- Impact: high; `src/deckseer/cli.py` is large enough to slow future autonomous changes.
- Risk: medium; output text and exit-code regressions are possible.
- Dependencies: current full test suite.
- Likely files: `src/deckseer/cli.py`, new CLI submodules.
- Validation: full `pytest`; smoke commands for exporter, QA, empirical, and recommendation paths.
- Effort: medium.

### 2. Static Exporter Mod Spike

- Impact: high; proves the game-side bridge can write `screen_type: "exporter_status"`.
- Risk: high; depends on external toolchain, STS2 beta volatility, and local game files.
- Dependencies: `.NET SDK`, Megadot/Godot, and STS2 templates verified; explicit approval for local mod/game-file work.
- Likely files: future C# mod project files and exporter docs.
- Validation: game shows the mod in settings, written JSON passes `deckseer inspect-export`, no live state exported.
- Effort: large.

### 3. Exporter Card Reward Contract Spike

- Impact: high; first real low-friction recommendation input.
- Risk: high; needs safe mod APIs and stable card ID mapping.
- Dependencies: static exporter spike passing.
- Likely files: exporter mod source, exporter docs, exporter fixtures/tests if contract gaps appear.
- Validation: `inspect-export`, `recommend-export --confirmed`, scenario winners unchanged, full QA.
- Effort: large.

### 4. Expand Reviewed Accuracy Scenarios From Real Runs

- Impact: high; improves trust before scoring or exporter-driven workflows expand.
- Risk: medium; expected top choices require careful review.
- Dependencies: reviewed run states or user-provided examples.
- Likely files: `data/accuracy/scenarios.json`, `tests/fixtures/scenarios/`, and possibly card data only if a scenario reveals a reviewed defect.
- Validation: `accuracy-report --format text`, `qa --check-accuracy`, full pytest.
- Effort: medium.

### 5. Empirical Intake Cleanup

- Impact: medium; removes stale proposed intake and clarifies next data capture.
- Risk: low to medium; must not fabricate stats or change scoring.
- Dependencies: manual source review if promoting rows.
- Likely files: `data/empirical/intake_queue.json`, empirical docs, draft worksheets if new rows are captured.
- Validation: `empirical-intake`, `empirical-coverage`, `empirical-triage-report`, QA.
- Effort: small to medium.

### 6. Relic/Potion Advice Design Packet

- Impact: medium; broadens Deckseer beyond card rewards while keeping deterministic advice.
- Risk: medium; could sprawl into combat simulation if not bounded.
- Dependencies: decide first target: relic choice or potion usage.
- Likely files: design docs first; later `data/relics`, `data/potions`, and advice modules.
- Validation: docs-only first; later focused fixtures and CLI smoke tests.
- Effort: medium.

### 7. Vision State Extractor Design Packet

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
python -m deckseer.cli exporter-toolchain-preflight --format text
python -m deckseer.cli qa --check-recommendation-baseline --check-accuracy --check-empirical-triage
python -m deckseer.cli empirical-coverage --format text
python -m deckseer.cli accuracy-report --format text
python -m pytest
```

Expected healthy state:

- Triage-aware QA: `PASS`.
- Exporter toolchain preflight: `blocked_missing_toolchain` until external setup is completed.
- Empirical coverage: `REVIEW`, 18 rows, 14 `patch_mismatch` warnings unless intentionally changed.
- Accuracy report: `PASS`, 9/9 unless intentionally expanded.
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
- python -m deckseer.cli exporter-toolchain-preflight --format text
- python -m deckseer.cli qa --check-recommendation-baseline --check-accuracy --check-empirical-triage
- python -m deckseer.cli empirical-coverage --format text
- python -m deckseer.cli accuracy-report --format text
- python -m pytest

Expected healthy state:
- triage-aware QA PASS
- exporter toolchain preflight blocked_missing_toolchain until external setup is completed
- empirical coverage REVIEW with 18 rows and 14 patch_mismatch warnings unless intentionally changed
- accuracy PASS, 9/9 unless intentionally expanded
- pytest green

After each packet, update relevant docs, commit with a concise message, push main if configured, and leave a clear handoff: what changed, verification, current blocker, and recommended next task.
```
