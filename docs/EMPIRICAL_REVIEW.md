# Deckseer Empirical Review

Deckseer treats empirical card stats as review evidence, not automatic scoring authority. The audit workflow should help identify cards worth reviewing while keeping recommendation changes deliberate and testable.

## Data Categories

- `data/empirical/`: active project review inputs. This directory may contain no active stat files until traceable rows are reviewed and promoted.
- `data/empirical/triage.json`: active audit-flag triage notes. These records explain review status and next actions; they do not resolve evidence or change scoring by themselves.
- `data/empirical/intake_queue.json`: pending or closed empirical review notes. These entries are not active stats and are excluded from routine empirical audits.
- `data/empirical/drafts/`: manually captured numeric draft files and incomplete capture worksheets. These are checked explicitly before promotion and are not active stats.
- `tests/fixtures/empirical/`: artificial audit fixtures. These files intentionally include missing cards, patch mismatches, small samples, and prior/stat conflicts so tests can exercise the audit engine.

Do not place deliberately broken audit examples in `data/empirical/`. Active empirical files are allowed to contain review flags only when the project intentionally tracks them as either unresolved review work or reviewed non-blocking context.

## Review Rules

- No card prior, role, tag, or scoring rule changes are made automatically from empirical stats.
- Patch mismatches must be resolved or explicitly documented before changing a prior.
- Small sample rows should not drive changes by themselves.
- High win rate or impact is observational evidence, not proof that the card caused wins.
- If a stat suggests a scoring or prior change, add or update an accuracy scenario before changing behavior when practical.
- Active empirical rows must be traceable to a real reviewed source. Do not add synthetic, guessed, or placeholder STS2.fun rows to `data/empirical/`.
- Active empirical rows may carry audit flags only when the evidence is intentionally accepted as review work. Use `empirical-promote-draft --allow-review-flags --write` for that explicit path.
- Every intentionally active audit flag should have a triage record before changing card priors or scoring.
- Triage statuses document next review work only; they do not make All Patches evidence equivalent to current-patch evidence.
- Numeric seed rows without provenance belong in `tests/fixtures/empirical/`, not active project data.
- Intake entries must not include numeric fields such as `sample_size`, `pick_rate`, `win_rate`, or `impact`; those belong only in active empirical files after review.
- Use `review_status: "rejected"` for source notes that are closed, superseded, or unsuitable for active empirical promotion. Use `proposed` only for concrete source-review work that is still pending.

## Intake Checklist

Before adding a real empirical row to `data/empirical/`, capture enough context for future review:

- Source URL or local source file.
- Game patch shown by the source.
- Character and exact Deckseer `card_id`.
- Stat definition, such as pick win rate, delta, impact, or other source-provided metric.
- Sample size and any filters, such as act, ascension, leaderboard slice, or date range.
- Capture date.
- Reviewer notes explaining why the row is suitable for active review data.

## Intake Workflow

1. Add a pending entry to `data/empirical/intake_queue.json` when a concrete candidate source or class coverage gap is identified. Keep stale or superseded notes closed as `rejected` so `empirical-intake` reflects only real pending review work.
2. For the first real Necrobinder seed, fill `data/empirical/drafts/necrobinder_sts2fun_capture_batch.json` from specific reviewed STS2.fun pages.
   For the current-patch Forbidden Grimoire follow-up, use `data/empirical/drafts/necrobinder_sts2fun_current_patch_triage_batch.json`, open `https://sts2.fun/cards?character=NECROBINDER`, and select the current-patch dropdown instead of All Patches before copying values.
   For cross-class coverage, use the current-patch worksheets for Ironclad, Silent, Defect, and Regent under `data/empirical/drafts/`. The first screenshot-reviewed current-patch rows for those four classes have been promoted; the same workflow remains available for future rows.
3. Review the source manually and capture exact numeric stats, patch, sample size, filters, source URL, and stat definition in a draft file under `data/empirical/drafts/`.
4. Run `deckseer empirical-capture-guide --character necrobinder --format text` for row-by-row capture instructions.
5. Run `deckseer empirical-capture-packet path/to/draft.json --format json` to create a batch fill template when collecting multiple rows.
   For the four non-Necrobinder class worksheets, run `deckseer empirical-cross-class-capture-packet --format json` to create one combined fill-in packet for Ironclad, Silent, Defect, and Regent.
6. Run `deckseer empirical-worksheet-check path/to/draft.json --format text` while rows are incomplete.
7. Use `deckseer empirical-worksheet-fill path/to/draft.json --entry-id <id> ...` for one row, `deckseer empirical-worksheet-apply-packet packet.json --worksheet path/to/draft.json` for a filled single-worksheet packet, or `deckseer empirical-cross-class-apply-packet packet.json` for the combined cross-class packet.
8. Re-run fill/apply commands with `--write` only after previews look correct.
9. For current-patch triage worksheets, run `deckseer empirical-current-patch-review path/to/draft.json --format text` to confirm coverage, patch suitability, and remaining blockers.
10. For the cross-class worksheets, run `deckseer empirical-cross-class-readiness --format text` to see which class worksheets are ready for strict draft validation and whether any audit flags would appear.
11. Run `deckseer empirical-cross-class-promotion-preview --format text` to preview the active output file for each complete class worksheet.
12. Run `deckseer empirical-draft-check path/to/draft.json --format text` to preview strict validation and audit flags once the worksheet has no blanks.
13. Preview the active payload with `deckseer empirical-promote-draft path/to/draft.json --output data/empirical/reviewed_stats.json`.
14. Write the active file only after review with `deckseer empirical-promote-draft path/to/draft.json --output data/empirical/reviewed_stats.json --write`.
    If reviewed rows intentionally produce audit flags, add `--allow-review-flags`; QA remains `REVIEW` until those flags are triaged, and can pass with `--check-empirical-triage` only when all active flags are `resolved_no_change`.
15. Run `deckseer empirical-coverage --format text` to check active coverage and provenance gaps.
16. Run `deckseer empirical-triage-report --format text` to confirm active audit flags have explicit next actions.
17. Keep triage unresolved until current-patch evidence and scenario review justify a documented no-change or change-planned decision.

## Routine Commands

```bash
deckseer qa --check-recommendation-baseline --check-accuracy
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
deckseer qa --check-recommendation-baseline --check-accuracy --check-empirical-coverage
deckseer qa --check-recommendation-baseline --check-accuracy --check-empirical-triage
deckseer audit-card-priors tests/fixtures/empirical/legacy_multi_class_card_stats_sample.json --format text
deckseer audit-card-priors tests/fixtures/empirical/multi_class_conflict_stats.json --format text
```

The active project QA command reports `REVIEW` while active empirical flags remain unresolved, even when recommendation baselines and accuracy scenarios pass. Conflict behavior remains covered by the test-only fixtures.

`empirical-coverage` reports how much active empirical data exists by class and patch. A `REVIEW` status can be healthy when it is calling out active audit flags or a known coverage gap, such as a class with no reviewed rows yet.

`empirical-intake` reports pending and closed candidate notes. A `PASS` result means there are no proposed intake entries waiting for review. These notes are intentionally excluded from `qa`, `audit-card-priors`, and active `empirical-coverage` scans until promoted.

`empirical-triage-report` cross-checks active empirical audit flags against `data/empirical/triage.json`. Missing, stale, open, `needs_current_patch`, `needs_scenario`, or `resolved_change_planned` entries keep the report in `REVIEW`. A report can pass with active flags only when every matched active flag is `resolved_no_change`, meaning reviewed and accepted as non-blocking context. `--fail-on-open` is available when you want open or untriaged flags to fail the command.

`empirical-current-patch-review` checks a manually filled current-patch worksheet against active triage entries. It reports missing/null fields, blocks All Patches rows from resolving current-patch work, and runs a strict draft/audit preview only after the worksheet is complete. It is read-only and does not promote rows or change scoring.

`empirical-capture-guide` prints row-by-row manual capture instructions for class-specific STS2.fun worksheets. It does not scrape, write files, or activate empirical data.
It supports default worksheets for Ironclad, Silent, Defect, Necrobinder, and Regent. Use `--worksheet data/empirical/drafts/necrobinder_sts2fun_current_patch_triage_batch.json` for the focused current-patch triage batch covering Forbidden Grimoire, Defy, and Sleight of Flesh.

`empirical-capture-packet` prints a batch fill-in packet. `empirical-worksheet-apply-packet` previews or explicitly writes a filled packet into a worksheet. Both are local manual-capture helpers only.

`empirical-cross-class-capture-packet` prints one combined fill-in packet for the Ironclad, Silent, Defect, and Regent current-patch worksheets. `empirical-cross-class-apply-packet` previews or explicitly writes the filled packet back to those draft worksheets class by class. These commands do not read the web, scrape STS2.fun, activate empirical evidence, or change recommendations.

`empirical-cross-class-readiness` reviews the four cross-class worksheets after capture packet application. It reports completeness, remaining blanks, strict draft-check readiness, audit-preview flags for complete worksheets, and the next promotion-preview command to run. It is read-only.

`empirical-cross-class-promotion-preview` aggregates per-class promotion previews for the four cross-class worksheets. It reports blocked worksheets, output paths, audit flags, and whether `--allow-review-flags` would be needed. It is preview-only and never writes active empirical files.

`empirical-draft-check` validates manually captured numeric rows and previews the card-prior audit result. It does not write active empirical data.

`empirical-worksheet-check` reviews incomplete capture worksheets and reports every missing or null required field. It is the right command while manually filling STS2.fun values.

`empirical-worksheet-fill` previews updates to one worksheet row and writes only when `--write` is provided. It validates that the row's `card_id` exists in Deckseer's local catalog.

Incomplete worksheets are expected to fail strict draft validation until all `null` fields are replaced with real reviewed values. Completed worksheets may still report `REVIEW` when their audit preview has flags. The intended seed path is: check worksheet, preview fill, write fill, run strict draft check, preview promotion, then explicitly write only after review.

`empirical-promote-draft` previews the exact active empirical JSON payload from a promotion-ready draft. It writes only when `--write` is provided, and promotion still does not change scoring or card priors by itself.

The active traceable empirical set now includes Necrobinder plus current-patch Ironclad, Silent, Defect, and Regent rows. Necrobinder uses STS2.fun's card table for `forbidden_grimoire`, `sleight_of_flesh`, and `defy`; `unleash` and `bodyguard` are omitted because they are starter/base cards with no normal reward pick stats in that table. The cross-class rows were manually captured from user-provided current v0.103 screenshots and promoted with `--allow-review-flags` so audit prompts stay visible. Forbidden Grimoire, Cold Snap, Astral Pulse, and Bulwark have each been converted into conservative local prior calibrations from current-patch evidence, supported by scenario guards; these changed card metadata only, not scoring rules or recommendation APIs. Remaining active audit flags are patch-context warnings triaged as non-blocking `resolved_no_change`.
