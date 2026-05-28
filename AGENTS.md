# Deckseer Agent Instructions

These instructions apply to work in this repository. If they conflict with system, developer, or explicit user instructions, follow the higher-priority instruction.

## Project Goal

Deckseer is a local, deterministic, human-in-the-loop decision-support coach for Slay the Spire 2. Preserve the manual JSON card reward advisor while moving carefully toward read-only/export-only state sources such as the proposed Deckseer Exporter.

Core boundaries:

- No gameplay automation, input control, memory/process tricks, packet inspection, stealth/evasion, anti-cheat bypass, live capture, OCR, or watch mode unless a task explicitly authorizes that work.
- No external tool installation or game-file modification without explicit user approval.
- No scoring, card prior, role, tag, empirical data, recommendation API, or baseline changes unless the task explicitly calls for them and reviewed scenario/empirical evidence supports them.
- Keep exporter work read-only/export-only and user-confirmation-first.

## Default Operating Mode

- Prefer small, focused work packets over broad "do everything" batches.
- During implementation, run the narrowest relevant check first.
- Read the smallest set of files needed to act safely; expand context when architecture, persistence, security, data flow, or cross-module behavior is affected.
- Keep repeated workflows in project guidance such as this file and `docs/EXECUTION_LOOP.md` rather than repasting long instructions into each thread.
- Use subagents only when explicitly asked for delegation or parallel agent work.
- Treat architecture, data integrity, security-sensitive work, persistence, and broad refactors as high-care work.

## Task Workflow

- For ambiguous or multi-file work, identify success criteria before editing.
- Direct execution is fine for obvious small tasks.
- For bug fixes, prefer adding or updating a focused regression check when practical.
- Before non-trivial edits, state assumptions, success criteria, likely files touched, narrow verification, and rollback notes.
- Push back when a requested approach is overcomplicated, risky, or inconsistent with Deckseer's boundaries.

## Implementation Discipline

- Prefer the smallest change that satisfies the request.
- Touch only files needed for the task.
- Match existing style, naming, and local patterns.
- Avoid new abstractions, dependencies, broad refactors, renames, moves, or reorganizations unless requested or clearly justified.
- Every changed line should trace to the current request, a required verification fix, or cleanup caused by the task's own changes.
- Do not reformat unrelated files or clean up pre-existing dead code unless explicitly asked.
- If unrelated issues are found, mention them instead of silently fixing them.

## Ambiguity And Assumptions

- Do not hide ambiguity.
- If multiple interpretations exist, state them briefly and either ask or proceed with the lowest-risk interpretation.
- If proceeding under uncertainty, clearly state the assumption being made.
- Ask before irreversible, high-risk, security-sensitive, data-destructive, or broad architectural changes.

## Dependency, Command, And Local Data Discipline

- Do not add new dependencies unless necessary; explain why existing code or built-in platform features are insufficient first.
- Prefer established, maintained packages over obscure or unnecessary packages.
- Ask before adding dependencies that affect auth, payments, security, networking, deployment, persistence, or user data.
- Keep approval requests narrow and reusable.
- Avoid destructive commands unless explicitly requested and clearly justified.
- Be careful with commands that delete files, rewrite history, change permissions, modify secrets, or affect global machine state.
- Never print, commit, or expose secrets, API keys, tokens, credentials, cookies, or private environment values.
- Do not modify `.env`, `.env.local`, or secret/config files unless explicitly asked.
- Preserve local user data by default.
- Ask before changing persistence formats, migrations, backups, or user-generated data.

## Autonomous Roadmap Execution

When the user asks to "advance the project", "continue the roadmap", "work autonomously", "pick the next task", "do the next packet", or similar, operate as a self-directed execution loop even if Goal Mode is unavailable.

Start each autonomous run by reading:

- `AGENTS.md`
- `README.md`
- `docs/PROJECT_STATUS.md`
- `docs/CONTEXT.md`
- `docs/EXECUTION_LOOP.md`
- relevant ADRs under `docs/adr/`
- exporter docs under `docs/EXPORTER_*`
- `docs/ACCURACY_REVIEW.md`
- `docs/EMPIRICAL_REVIEW.md`
- `docs/strategy_backlog.md`
- any `PLAN.md`, `TODO*`, `ROADMAP*`, issue files, tests, or recent logs that are present

Then:

1. Run `git status --short --branch` before editing.
2. Rank available work by project impact, user value, dependency-unblocking value, risk, and effort.
3. Pick the highest-impact unblocked task that does not require user input.
4. Work on one small packet at a time.
5. A packet means one feature slice, one refactor, one bug fix, one proof path, or one documentation/update task.

Before non-trivial edits, state:

- packet goal
- why this is the best next task
- acceptance criteria
- likely files touched
- narrow verification path
- rollback notes

Make the smallest useful change that satisfies the acceptance criteria. Run focused verification first, then broader checks when shared behavior, CLI behavior, generated artifacts, or core paths change. Update the roadmap, progress log, or relevant planning document after each completed packet.

If the user explicitly asked for autonomous continuation, continue packet-by-packet within the same session until blocked, context is running low, the approved task queue is complete, or the user asks to stop. Otherwise, finish the requested packet and report the next recommended packet.

## Stop And Ask

Stop and ask the user only when a decision materially changes:

- architecture
- product direction
- data model
- public API or CLI behavior
- auth/security posture
- payments, pricing, deployment, or external accounts
- persistence semantics or migrations
- major user experience behavior

Also stop and ask when:

- requirements conflict
- validation cannot be run or repeatedly fails for unclear reasons
- secrets, credentials, paid services, deployment access, or external accounts are required
- a new dependency is needed
- external tool installation or STS2 game-file modification is needed
- C# exporter mod source would be added or the mod repository/package location must be decided
- scoring, priors, empirical data, or baselines would change
- vision/OCR/live capture work would begin
- the approved autonomous task queue is complete
- context is getting too long to safely continue

## Git Rules

- Commit only after verification passes and the diff contains only intended changes.
- Do not push unless the user explicitly asks, the current task explicitly includes pushing, or the active project workflow has already established that the completed packet should be published.
- If commits are not requested, leave changes uncommitted and summarize the diff.
- Never revert user changes unless explicitly asked.

## Reporting After Each Packet

Report:

- what changed
- why it was chosen
- files changed
- verification run and results
- risks or follow-ups
- next recommended packet

Do not claim success for checks that were not run. If verification cannot run, explain why and provide the exact command the user should run. If manual testing is needed, describe the smallest useful manual test.

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

- triage-aware QA: `PASS`
- exporter toolchain preflight: `READY_FOR_STATIC_SPIKE` or equivalent ready status when local toolchain remains visible
- empirical coverage: `REVIEW`, 18 rows, 14 `patch_mismatch` warnings unless intentionally changed
- accuracy report: `PASS`, 10/10 unless intentionally expanded
- relic accuracy report: `PASS`, 6/6 unless intentionally expanded
- pytest: green
