# Empirical Drafts

This folder is for manually captured empirical stat drafts before they become active Deckseer review data.

Draft files are not discovered by `deckseer qa`, `deckseer audit-card-priors`, or `deckseer empirical-coverage`. They are checked explicitly:

```bash
deckseer empirical-worksheet-check data/empirical/drafts/necrobinder_sts2fun_capture_batch.json --format text
deckseer empirical-draft-check data/empirical/drafts/my_draft.json --format text
```

## First Capture Worksheet

`necrobinder_sts2fun_capture_template.json` is the first manual capture worksheet. It is intentionally incomplete and uses `null` for unknown source values. That means this command should fail until real reviewed STS2.fun values are entered:

```bash
deckseer empirical-draft-check data/empirical/drafts/necrobinder_sts2fun_capture_template.json --format text
```

Use the failure message as a fill-in checklist. Replace every `null` with an exact source value before promotion review.

`necrobinder_sts2fun_capture_batch.json` is a broader capture worksheet for the first Necrobinder pass. It tracks `unleash`, `bodyguard`, `forbidden_grimoire`, `sleight_of_flesh`, and `defy`.

`necrobinder_sts2fun_current_patch_triage_batch.json` is the focused current-patch follow-up worksheet for active triage targets: `forbidden_grimoire`, `defy`, and `sleight_of_flesh`. It now contains reviewed current-patch values captured from `https://sts2.fun/cards?character=NECROBINDER` with the current-patch dropdown selected instead of All Patches. It remains in drafts as the traceable source worksheet for `data/empirical/necrobinder_sts2fun_current_patch_reviewed.json`.

Cross-class current-patch worksheets are also available and now contain the first screenshot-reviewed v0.103 values:

- `ironclad_sts2fun_current_patch_capture_batch.json`: `shrug_it_off`, `pommel_strike`, `anger`
- `silent_sts2fun_current_patch_capture_batch.json`: `dagger_throw`, `backflip`, `footwork`
- `defect_sts2fun_current_patch_capture_batch.json`: `cold_snap`, `glacier`, `defragment`
- `regent_sts2fun_current_patch_capture_batch.json`: `astral_pulse`, `bulwark`, `spectrum_shift`

These files are draft records backing the promoted active current-patch empirical files for the four classes. Future capture batches should keep patch and numeric stats as `null` until exact current-patch STS2.fun values are copied manually; draft files are not active empirical evidence until explicitly promoted.

Use worksheet review and capture helpers when preparing future rows or reviewing the current traceable draft records:

```bash
deckseer empirical-capture-guide --character ironclad --format text
deckseer empirical-capture-guide --character silent --format text
deckseer empirical-capture-guide --character defect --format text
deckseer empirical-capture-guide --character regent --format text
deckseer empirical-capture-guide --character necrobinder --format text
deckseer empirical-capture-guide --character necrobinder --worksheet data/empirical/drafts/necrobinder_sts2fun_current_patch_triage_batch.json --format text
deckseer empirical-cross-class-capture-packet --format json
deckseer empirical-capture-packet data/empirical/drafts/ironclad_sts2fun_current_patch_capture_batch.json --format json
deckseer empirical-capture-packet data/empirical/drafts/necrobinder_sts2fun_capture_batch.json --format json
deckseer empirical-capture-packet data/empirical/drafts/necrobinder_sts2fun_current_patch_triage_batch.json --format json
deckseer empirical-worksheet-check data/empirical/drafts/ironclad_sts2fun_current_patch_capture_batch.json --format text
deckseer empirical-worksheet-check data/empirical/drafts/necrobinder_sts2fun_capture_batch.json --format text
deckseer empirical-worksheet-check data/empirical/drafts/necrobinder_sts2fun_current_patch_triage_batch.json --format text
```

For a single four-class capture session, use the combined packet instead of generating one packet per worksheet:

```bash
deckseer empirical-cross-class-capture-packet --format json
deckseer empirical-cross-class-apply-packet packet.json --format text
deckseer empirical-cross-class-apply-packet packet.json --format text --write
deckseer empirical-cross-class-readiness --format text
deckseer empirical-cross-class-promotion-preview --format text
```

The combined packet is still manual and preview-first. It does not read STS2.fun, scrape pages, activate empirical files by itself, or change scoring. Use readiness review after applying filled values to see which class worksheets are complete, then use promotion preview to see the exact active output file for each class before running any per-class promotion command.

Preview a row update before writing:

```bash
deckseer empirical-worksheet-fill data/empirical/drafts/necrobinder_sts2fun_capture_batch.json --entry-id necrobinder_unleash_sts2fun_capture --patch v0.103.0 --sample-size 1200 --pick-rate 0.42 --win-rate 0.58 --impact 0.08 --captured-at 2026-05-23 --stat-definition "Exact STS2.fun metric and filters." --format text
```

Write only after the preview looks right:

```bash
deckseer empirical-worksheet-fill data/empirical/drafts/necrobinder_sts2fun_capture_batch.json --entry-id necrobinder_unleash_sts2fun_capture --patch v0.103.0 --sample-size 1200 --pick-rate 0.42 --win-rate 0.58 --impact 0.08 --captured-at 2026-05-23 --stat-definition "Exact STS2.fun metric and filters." --write
```

After the worksheet reports ready for draft check, run strict validation:

```bash
deckseer empirical-draft-check data/empirical/drafts/necrobinder_sts2fun_capture_batch.json --format text
```

## Manual Capture Checklist

Before promoting a draft row to `data/empirical/*.json`, confirm:

- The source is traceable, such as a specific STS2.fun page URL.
- The game patch is visible or otherwise documented.
- The `card_id` matches Deckseer's local catalog.
- `sample_size`, `pick_rate`, `win_rate`, and `impact` are copied exactly from the reviewed source.
- `stat_definition` explains what the numbers mean.
- `captured_at` records the capture date.
- `reviewer_notes` explain filters, caveats, or why the row is useful.
- `deckseer empirical-draft-check ...` reports promotion ready.

Suggested STS2.fun capture flow:

1. Open the exact card/stat page you want to use.
2. Confirm the class, patch, filters, act/ascension slice, and stat definition shown by the site.
3. Copy the exact Deckseer `card_id`, patch, sample size, pick rate, win rate, impact, and source URL into the worksheet.
4. Set `captured_at` to the date you captured the row.
5. Add reviewer notes describing filters, page context, and any caveats.
6. Run `deckseer empirical-capture-guide --character <class> --format text` for row-specific command templates.
7. Generate a batch fill template with `deckseer empirical-capture-packet ... --format json` if collecting multiple rows from one worksheet, or `deckseer empirical-cross-class-capture-packet --format json` if collecting the Ironclad, Silent, Defect, and Regent rows together.
8. Run `deckseer empirical-worksheet-fill ...`, `deckseer empirical-worksheet-apply-packet ...`, or `deckseer empirical-cross-class-apply-packet ...` in preview mode.
9. Re-run the fill/apply command with `--write` after the preview looks correct.
10. Run `deckseer empirical-worksheet-check ...` until no null or missing fields remain.
11. For cross-class capture, run `deckseer empirical-cross-class-readiness --format text`.
12. For cross-class capture, run `deckseer empirical-cross-class-promotion-preview --format text`.
13. Run `deckseer empirical-draft-check ...`.
14. Preview promotion with `deckseer empirical-promote-draft ... --output data/empirical/<reviewed>.json`.
15. Write only after review with `--write`.

## Draft Shape

Use this structure when preparing a capture. Keep `null` for unknown values while drafting, but do not promote until every required value is filled:

```json
{
  "draft_type": "empirical_stat_draft",
  "entries": [
    {
      "id": "necrobinder_example_card_sts2fun_2026_05_23",
      "card_id": null,
      "character": "necrobinder",
      "patch": null,
      "source": "STS2.fun manual capture",
      "source_url": "https://sts2.fun/",
      "captured_at": null,
      "stat_definition": null,
      "reviewer_notes": "Record filters, page context, and any caveats.",
      "sample_size": null,
      "pick_rate": null,
      "win_rate": null,
      "impact": null,
      "act": "all",
      "ascension": "all",
      "review_status": "proposed"
    }
  ]
}
```

Do not commit placeholder numeric values as active empirical data. Empty coverage is better than untraceable or guessed stats.
