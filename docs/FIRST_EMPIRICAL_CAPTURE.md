# First Empirical Capture

Deckseer's first real empirical seed came from manually reviewed STS2.fun values, not scraping or guessed data.

Completed first seed:

- Character: Necrobinder
- Source: STS2.fun
- Filter: All Patches, all runs, rarity/type All, Separate upgrades off, Min. 5 offers on
- Active file: `data/empirical/necrobinder_sts2fun_all_patches_reviewed.json`
- Cards: `forbidden_grimoire`, `sleight_of_flesh`, `defy`

Completed current-patch follow-up:

- Character: Necrobinder
- Source: STS2.fun
- Filter: Main v0.103 current, all runs, rarity/type All, Separate upgrades off, Min. 5 offers on
- Active file: `data/empirical/necrobinder_sts2fun_current_patch_reviewed.json`
- Source worksheet: `data/empirical/drafts/necrobinder_sts2fun_current_patch_triage_batch.json`
- Cards: `forbidden_grimoire`, `defy`, `sleight_of_flesh`

`unleash` and `bodyguard` are starter/base cards and were omitted because the STS2.fun card table does not provide normal reward-pick stats for them.

Completed cross-class current-patch seed:

- Characters: Ironclad, Silent, Defect, Regent
- Source: STS2.fun screenshots supplied by the user
- Filter: Main v0.103 current, all runs, Overview tab
- Active files:
  - `data/empirical/ironclad_sts2fun_current_patch_reviewed.json`
  - `data/empirical/silent_sts2fun_current_patch_reviewed.json`
  - `data/empirical/defect_sts2fun_current_patch_reviewed.json`
  - `data/empirical/regent_sts2fun_current_patch_reviewed.json`
- Cards:
  - Ironclad: `shrug_it_off`, `pommel_strike`, `anger`
  - Silent: `dagger_throw`, `backflip`, `footwork`
  - Defect: `cold_snap`, `glacier`, `defragment`
  - Regent: `astral_pulse`, `bulwark`, `spectrum_shift`

Those rows were promoted with `--allow-review-flags` so current-patch evidence remains active while audit prompts stay visible. Patch-context flags are triaged as non-blocking. `cold_snap`, `astral_pulse`, and `bulwark` now have conservative current-patch prior calibrations and scenario guards.

Future capture sessions can still use the original worksheet:

- Worksheet: `data/empirical/drafts/necrobinder_sts2fun_capture_batch.json`

## Workflow

Generate a fill-in packet:

```bash
deckseer empirical-capture-packet data/empirical/drafts/necrobinder_sts2fun_capture_batch.json --format json
```

Fill the packet manually from reviewed STS2.fun pages. Every row needs:

- `source_url`
- `patch`
- `sample_size`
- `pick_rate`
- `win_rate`
- `impact`
- `stat_definition`
- `captured_at`
- `reviewer_notes`

Preview applying the packet:

```bash
deckseer empirical-worksheet-apply-packet packet.json --worksheet data/empirical/drafts/necrobinder_sts2fun_capture_batch.json --format text
```

Write only after the preview looks right:

```bash
deckseer empirical-worksheet-apply-packet packet.json --worksheet data/empirical/drafts/necrobinder_sts2fun_capture_batch.json --write
```

Then run strict validation:

```bash
deckseer empirical-draft-check data/empirical/drafts/necrobinder_sts2fun_capture_batch.json --format text
```

Preview promotion:

```bash
deckseer empirical-promote-draft data/empirical/drafts/necrobinder_sts2fun_capture_batch.json --output data/empirical/necrobinder_sts2fun_reviewed.json
```

Write active empirical data only after review. If the reviewed evidence intentionally carries audit flags, use `--allow-review-flags` and keep the resulting QA status as review work:

```bash
deckseer empirical-promote-draft data/empirical/drafts/necrobinder_sts2fun_capture_batch.json --output data/empirical/necrobinder_sts2fun_reviewed.json --write --allow-review-flags
```

Finally check coverage:

```bash
deckseer empirical-coverage --format text
```

Current coverage should report 18 active traceable rows across all five classes and `REVIEW` because active audit flags remain review work.

Do not promote blank, guessed, synthetic, or untraceable values. Empty or partial active empirical coverage is better than untrustworthy evidence.
