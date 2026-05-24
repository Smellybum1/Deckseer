# Deckseer Project Status

Deckseer is currently a local, manual JSON-first decision-support coach for Slay the Spire 2. It ranks visible card reward options, always includes Skip, and explains the recommendation with deterministic run-needs scoring.

## Implemented

- Manual run-state JSON input for card reward advice.
- Deterministic card reward scoring with ranked choices, scores, reasoning, confidence, and risks.
- Run diagnosis helpers for deck shape, prioritized needs, HP pressure, act/floor phase, and region/path context.
- CLI commands for `recommend-card`, `recommend-relic`, `diagnose-run`, `check-run-data`, `check-runs`, `normalize-run`, `list-cards`, `data-summary`, `data-review`, `data-health`, `qa`, `qa-baseline`, `accuracy-report`, `relic-accuracy-report`, `audit-card-priors`, `empirical-coverage`, `empirical-intake`, `empirical-triage-report`, `empirical-current-patch-review`, `empirical-capture-guide`, `empirical-capture-packet`, `empirical-cross-class-capture-packet`, `empirical-cross-class-apply-packet`, `empirical-cross-class-readiness`, `empirical-cross-class-promotion-preview`, `empirical-worksheet-check`, `empirical-worksheet-fill`, `empirical-worksheet-apply-packet`, `empirical-draft-check`, `empirical-promote-draft`, `inspect-save`, `import-run`, `recommend-save`, `inspect-export`, `recommend-export`, and `exporter-toolchain-preflight`.
- Read-only import from plain JSON Slay the Spire 2 run-history files, with manual live-state fields supplied by the user.
- Read-only import from proposed Deckseer Exporter JSON files, with exporter metadata and caveats kept outside scoring. `inspect-export` accepts static exporter status, card reward, and relic reward files; `recommend-export` supports confirmed card reward and relic reward files.
- Read-only exporter toolchain preflight report for checking the local STS2 install, `.NET SDK`, STS2 templates, and Megadot/Godot visibility before exporter mod work.
- Static Slay the Spire 2 Deckseer Exporter mod spike under `exporter_mod/DeckseerExporter`, verified to write `screen_type: "exporter_status"` JSON that `inspect-export` accepts as valid.
- Exporter card reward API recon in `docs/EXPORTER_CARD_REWARD_API_RECON.md`, using a read-only local metadata probe to identify likely public reward/run-state surfaces before any live card reward export is implemented.
- JSON, text, and Markdown recommendation output.
- Strategy backlog for reviewed creator claims, tier-list sources, and empirical data ideas.
- Accuracy scenario manifest and report workflow for reviewed recommendation drift checks.
- Relic accuracy scenario manifest and report workflow for reviewed relic choice drift checks.
- Accuracy scenario intake checklist for converting reviewed real-run card reward decisions into regression fixtures without changing scoring first.
- Advice module decision brief for choosing the first broader surface after card rewards without committing runtime behavior.
- Relic choice design document for the first approved broader advice surface.
- Relic Choice V1 scorer, fixtures, and `recommend-relic` CLI for manual `screen_type: "relic_reward"` JSON.
- Relic metadata seed plan and reviewed V1 metadata on the existing three seed relics.
- Relic metadata expansion readiness guide for future tiny reviewed batches guarded by `relic-accuracy-report`.
- Empirical coverage report workflow for measuring active stats coverage by class and patch.
- Empirical intake queue for pending or closed source review notes that are not active audit evidence.
- Empirical triage manifest and report workflow for tracking active audit flags without changing scoring.
- Empirical current-patch review preview for checking whether a manual worksheet can resolve active triage items.
- Empirical capture guide for row-by-row manual Necrobinder STS2.fun capture instructions.
- Empirical capture packet workflow for batch manual capture sessions.
- Cross-class capture packet workflow for one combined manual fill-in packet covering Ironclad, Silent, Defect, and Regent.
- Cross-class readiness report for reviewing worksheet completeness and audit previews before promotion.
- Cross-class promotion preview for seeing the exact per-class active files that would be created without writing them.
- Empirical worksheet checker for reviewing incomplete manual capture batches without promoting them.
- Empirical worksheet fill preview/write command for safely updating one manual capture row at a time.
- Empirical draft checker for validating manually captured numeric rows before promotion.
- Empirical promotion preview for explicitly activating promotion-ready draft rows.
- Necrobinder STS2.fun capture worksheets for the first real traceable empirical seed.
- Current-patch STS2.fun capture worksheets and reviewed active empirical files for Ironclad, Silent, Defect, and Regent.
- Project-local agent guidance in `AGENTS.md`, plus the repo-native self-directed execution loop and ranked roadmap in `docs/EXECUTION_LOOP.md`.

## Current Data Coverage

Card metadata is hand-curated, intentionally incomplete, and designed for transparent heuristics rather than full combat simulation.

| Class | Seed Card Records |
| --- | ---: |
| Ironclad | 25 |
| Silent | 33 |
| Defect | 34 |
| Necrobinder | 40 |
| Regent | 42 |
| Neutral | 0 |

Relic and potion data exist as sparse seed files. The three current relic seed records now include Relic Choice V1 planning metadata: roles, weak priors, pick context, source patch, and source notes. The `recommend-relic` command uses that metadata for manual relic reward advice, while card reward scoring is unchanged. Empirical data support is intentionally conservative: active traceable numeric rows now cover all five catalog classes. Necrobinder has All Patches and current-patch STS2.fun rows for `forbidden_grimoire`, `sleight_of_flesh`, and `defy`; `unleash` and `bodyguard` remain omitted because they are starter/base cards with no normal reward pick stats on that table. Ironclad, Silent, Defect, and Regent now have current-patch STS2.fun rows promoted from screenshot-reviewed worksheets: Ironclad covers `shrug_it_off`, `pommel_strike`, and `anger`; Silent covers `dagger_throw`, `backflip`, and `footwork`; Defect covers `cold_snap`, `glacier`, and `defragment`; Regent covers `astral_pulse`, `bulwark`, and `spectrum_shift`. The source worksheets remain under `data/empirical/drafts/` as traceable capture records, and the promoted active files live under `data/empirical/*_sts2fun_current_patch_reviewed.json`. `empirical-coverage` no longer reports missing traceable class coverage, but it still reports `REVIEW` because active patch-context audit flags remain visible as review evidence. `data/empirical/triage.json` tracks all active flags: patch-context warnings are documented as non-blocking `resolved_no_change`, and there are no unresolved high-prior empirical conflicts. Forbidden Grimoire, Cold Snap, Astral Pulse, and Bulwark have each been converted into conservative prior calibrations from current-patch evidence while keeping their utility roles. `data/empirical/intake_queue.json` has no pending proposed source-review entries right now; its remaining Necrobinder note is closed as superseded by reviewed promoted rows. `data/empirical/drafts/` is reserved for manually captured draft rows, and the original Necrobinder batch worksheet remains available for future capture sessions. `empirical-promote-draft --allow-review-flags` can explicitly activate reviewed rows that should remain visible as audit review work. Legacy seed rows and artificial conflict cases live under `tests/fixtures/empirical/` so loader and audit behavior stay covered without fabricating active evidence. Accuracy scenarios live in `data/accuracy/scenarios.json` and currently cover nine reviewed card-reward calibration cases, including guards for `cold_snap`, `astral_pulse`, and `bulwark`.

## Current Boundaries

- No GUI.
- No OCR or screenshot reading.
- No live game capture.
- No gameplay automation, mouse input, keyboard input, memory reading, packet inspection, stealth, or anti-cheat bypass.
- No LLM dependency in the recommendation path.
- Save import is read-only and does not modify game files.

## Recommended Next Milestones

1. Self-directed execution: use `AGENTS.md` and `docs/EXECUTION_LOOP.md` to choose the highest-impact unblocked packet, run the default gates, and keep handoffs consistent.
2. Reviewed scenario expansion: use `docs/ACCURACY_SCENARIO_INTAKE.md` to add accepted real-run card-reward examples only when source states are reviewed and expected choices can be justified without changing scoring first.
3. Deckseer Exporter Mod next stage: the static in-game spike now works and is documented in `docs/EXPORTER_STATIC_MOD_SPIKE.md`. Deckseer can inspect the real mod-written `exporter_status` file, recommend from confirmed card/relic exporter JSON fixtures, and run `deckseer exporter-toolchain-preflight --format text` to repeat local readiness checks. `docs/EXPORTER_CARD_REWARD_API_RECON.md` identifies likely public reward/run-state surfaces; the next exporter packet should be a compile-time or diagnostic-only probe before writing any live card reward state. Watch mode has not been implemented.
4. Vision State Extractor design remains a future fallback/complement for screenshot-based visible state extraction.
5. Broader advice modules: relic choice is the approved first surface. `recommend-relic` now supports manual relic reward JSON, backed by `docs/RELIC_CHOICE_DESIGN.md`, `docs/RELIC_METADATA_SEED_PLAN.md`, `docs/RELIC_METADATA_EXPANSION_READINESS.md`, `tests/test_relic_choice.py`, and `relic-accuracy-report`. Deckseer can inspect and recommend from confirmed proposed `screen_type: "relic_reward"` exporter files. The next data-changing packet should add only a tiny reviewed relic metadata batch with matching relic accuracy scenarios.
6. Data QA maintenance: keep `data-health` passing as new card metadata, roles, and effects are added.

## Verification Snapshot

The expected health check for the current project is:

```bash
pytest
```

Manual smoke checks should include `qa`, which checks data health, example run-state coverage, recommendation smoke scoring, and empirical audit summaries:

```bash
deckseer data-summary --format text
deckseer data-summary --character ironclad --format text
deckseer data-summary --character silent --format text --show-gap-ids
deckseer data-review --flag seed_only_cards_with_neutral_quality_prior
deckseer data-health
deckseer qa
deckseer qa --run-paths examples/card_reward_basic.json
deckseer qa --check-recommendation-baseline
deckseer qa --check-accuracy
deckseer qa --check-recommendation-baseline --check-accuracy
deckseer qa --check-recommendation-baseline --check-accuracy --check-empirical-coverage
deckseer qa --check-recommendation-baseline --check-accuracy --check-empirical-triage
deckseer qa-baseline
deckseer accuracy-report --format text
deckseer relic-accuracy-report --format text
deckseer empirical-coverage --format text
deckseer empirical-intake --format text
deckseer empirical-triage-report --format text
deckseer empirical-current-patch-review data/empirical/drafts/necrobinder_sts2fun_current_patch_triage_batch.json --format text
deckseer empirical-capture-guide --character ironclad --format text
deckseer empirical-capture-guide --character silent --format text
deckseer empirical-capture-guide --character defect --format text
deckseer empirical-capture-guide --character regent --format text
deckseer empirical-capture-guide --character necrobinder --format text
deckseer empirical-capture-guide --character necrobinder --worksheet data/empirical/drafts/necrobinder_sts2fun_current_patch_triage_batch.json --format text
deckseer empirical-cross-class-capture-packet --format text
deckseer empirical-cross-class-apply-packet packet.json --format text
deckseer empirical-cross-class-readiness --format text
deckseer empirical-cross-class-promotion-preview --format text
deckseer empirical-capture-packet data/empirical/drafts/necrobinder_sts2fun_capture_batch.json --format text
deckseer empirical-capture-packet data/empirical/drafts/necrobinder_sts2fun_current_patch_triage_batch.json --format text
deckseer empirical-worksheet-apply-packet packet.json --worksheet data/empirical/drafts/necrobinder_sts2fun_capture_batch.json --format text
deckseer empirical-worksheet-check data/empirical/drafts/necrobinder_sts2fun_capture_batch.json --format text
deckseer empirical-worksheet-check data/empirical/drafts/necrobinder_sts2fun_current_patch_triage_batch.json --format text
deckseer empirical-worksheet-fill data/empirical/drafts/necrobinder_sts2fun_capture_batch.json --entry-id necrobinder_unleash_sts2fun_capture --patch v0.103.0 --format text
deckseer empirical-draft-check data/empirical/drafts/necrobinder_sts2fun_capture_template.json --format text
deckseer empirical-draft-check data/empirical/drafts/necrobinder_sts2fun_all_patches_reviewed.json --format text
deckseer empirical-draft-check tests/fixtures/empirical/valid_traceable_draft.json --format text
deckseer empirical-promote-draft tests/fixtures/empirical/valid_traceable_draft.json --output data/empirical/manual_preview.json
deckseer empirical-promote-draft data/empirical/drafts/necrobinder_sts2fun_all_patches_reviewed.json --output data/empirical/necrobinder_sts2fun_all_patches_reviewed.json --allow-review-flags
deckseer audit-card-priors tests/fixtures/empirical/legacy_multi_class_card_stats_sample.json --format text
deckseer audit-card-priors tests/fixtures/empirical/multi_class_conflict_stats.json --format text
deckseer inspect-export tests/fixtures/exporter_card_reward_state.json
deckseer inspect-export tests/fixtures/exporter_status_state.json
deckseer recommend-export tests/fixtures/exporter_card_reward_state.json --confirmed --format text
deckseer recommend-export tests/fixtures/exporter_relic_reward_state.json --confirmed --format text
deckseer exporter-toolchain-preflight --format text
deckseer recommend-relic tests/fixtures/relic_choice/elite_frontload.json --format text
deckseer recommend-card examples/card_reward_basic.json
deckseer recommend-card examples/card_reward_basic.json --format text
deckseer recommend-card examples/card_reward_basic.json --format markdown
```

There are now 18 active traceable empirical rows across All Patches and current-patch files. `deckseer qa --check-recommendation-baseline --check-accuracy` should report `REVIEW` with exit code 0 because raw active empirical audit flags are review prompts when triage is not checked, while recommendation baseline and accuracy scenarios still pass. `deckseer qa --check-recommendation-baseline --check-accuracy --check-empirical-triage` should report `PASS` because all active flags are triaged as non-blocking context. `deckseer qa --check-recommendation-baseline --check-accuracy --check-empirical-coverage` should report `REVIEW` because active patch-context audit flags remain, not because any catalog class lacks traceable rows. `deckseer empirical-capture-guide --character ironclad|silent|defect|regent --format text` should show the reviewed current-patch worksheet rows that back the active promoted files. `deckseer empirical-cross-class-readiness --format text` should report all four cross-class worksheets complete with audit flags, and `deckseer empirical-cross-class-promotion-preview --format text` should show the per-class active empirical output files and that `--allow-review-flags` is needed for review-promoted rows. `deckseer empirical-intake --format text` should report `PASS` when there are no proposed source-review notes; closed intake notes remain excluded from active evidence. `deckseer empirical-triage-report --format text` should show `PASS` with all active flags resolved as non-blocking patch-context warnings. `deckseer empirical-current-patch-review data/empirical/drafts/necrobinder_sts2fun_current_patch_triage_batch.json --format text` should report the three completed current-patch worksheet rows, active triage coverage, audit-preview flags, and Forbidden Grimoire ready rather than blocked. `deckseer empirical-capture-guide --character necrobinder --format text` should show row-by-row manual capture instructions without writing files, and `--worksheet data/empirical/drafts/necrobinder_sts2fun_current_patch_triage_batch.json` should focus that guide on the current-patch triage rows. `deckseer empirical-capture-packet ...` should print a fill-in packet, and `deckseer empirical-worksheet-apply-packet ...` should preview packet application unless `--write` is provided. `deckseer empirical-worksheet-check data/empirical/drafts/necrobinder_sts2fun_capture_batch.json --format text` should return a review summary with all remaining blanks. `deckseer empirical-worksheet-fill ...` previews worksheet changes and writes only with `--write`. `deckseer empirical-draft-check data/empirical/drafts/necrobinder_sts2fun_capture_template.json --format text` should return validation exit code 2 until real source values replace the worksheet `null`s. Conflict audit behavior is still covered by `tests/fixtures/empirical/`, and `deckseer audit-card-priors ... --fail-on-flags` should report failure when pointed at those conflict fixtures.
