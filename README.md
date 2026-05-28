# Deckseer

Deckseer is a local, developer-friendly decision-support coach prototype for Slay the Spire 2.

The v0 milestone reads a structured JSON run state, evaluates the current card reward choices plus Skip, and returns a deterministic ranked recommendation with scores, short reasoning, confidence, and caveats.

Deckseer v0 does not automate gameplay, read the screen, or depend on an LLM.

## Install for Local Development

```bash
python -m pip install -e ".[dev]"
```

## CLI Usage

JSON output is the default:

```bash
deckseer recommend-card examples/card_reward_basic.json
```

Find exact card IDs for manual JSON:

```bash
deckseer list-cards --character silent --query backflip --format text
```

Summarize local data coverage, hard metadata gaps, and softer review flags:

```bash
deckseer data-summary --format text
```

Focus the data summary on one class:

```bash
deckseer data-summary --character ironclad --format text
```

Show the card IDs behind text-mode metadata gaps and review flags:

```bash
deckseer data-summary --character silent --format text --show-gap-ids
```

Review flags separate direct-action cards with empty simplified effects from powers, so numeric effect cleanup can start with the most actionable cards first.

List the actual cards behind a review flag:

```bash
deckseer data-review --flag seed_only_cards_with_neutral_quality_prior
```

Run the pass/fail data hygiene gate for hard metadata gaps and blocking review flags:

```bash
deckseer data-health
```

Run project-native QA checks for data health and empirical audit summaries:

```bash
deckseer qa
deckseer qa --run-paths examples/card_reward_basic.json
deckseer qa --check-recommendation-baseline
deckseer qa --check-accuracy
deckseer qa --check-recommendation-baseline --check-accuracy --check-empirical-coverage
deckseer qa-baseline --output data/qa/recommendation_smoke_baseline.json
```

`qa` also smoke-scores checked run files so example coverage proves the recommendation engine still runs, not just that card IDs exist.
Text output lists each checked run file's current top recommendation for a quick strategy-drift glance.
Use `--check-recommendation-baseline` when you want QA to fail if example top choices drift from the checked-in baseline.
Use `--check-accuracy` when you want QA to include reviewed accuracy scenarios.
Use `--check-empirical-coverage` when you want QA to show whether active empirical stat coverage is traceable and class-complete.
Use `--check-empirical-triage` when you want QA to include whether active empirical flags have documented review decisions.
Use `qa-baseline` after reviewing intentional strategy drift to regenerate that baseline.

Review accuracy scenarios directly:

```bash
deckseer accuracy-report --format text
deckseer accuracy-report --fail-on-mismatch
deckseer relic-accuracy-report --format text
```

For stricter CI-style gates, use:

```bash
deckseer qa --fail-on-audit-flags
deckseer qa --strict
```

`--fail-on-audit-flags` turns empirical audit flags into a failing QA status.
`--strict` also checks the default recommendation baseline.
With active reviewed empirical rows, these stricter modes may report `REVIEW` or fail under `--fail-on-audit-flags` when raw audit flags are intentionally visible. `qa --check-empirical-triage` can pass when every active flag is triaged as `resolved_no_change`; it returns to `REVIEW` if any active flag is marked `needs_scenario`, `needs_current_patch`, or `resolved_change_planned`.

If you use a display name or typo in a reward, Deckseer will suggest likely IDs. For example, `Shrug It Off` points to `shrug_it_off`.

`normalize-run` only rewrites exact normalized matches, such as `Shrug It Off` to `shrug_it_off` or `pommel strike` to `pommel_strike`. Typos are reported with suggestions but are not silently changed.

Pretty text output:

```bash
deckseer recommend-card examples/card_reward_basic.json --format text
```

Rank a manual relic reward state:

```bash
deckseer recommend-relic tests/fixtures/relic_choice/elite_frontload.json --format text
```

Markdown output:

```bash
deckseer recommend-card examples/card_reward_basic.json --format markdown --include-diagnosis
```

Include the run diagnosis alongside the recommendation:

```bash
deckseer recommend-card examples/card_reward_basic.json --include-diagnosis
```

Inspect the deck profile and prioritized run needs without scoring the reward:

```bash
deckseer diagnose-run examples/card_reward_basic.json
```

Check whether a run JSON has all card metadata needed for scoring:

```bash
deckseer check-run-data examples/card_reward_basic.json
```

Normalize exact card display names in a run JSON to Deckseer IDs:

```bash
deckseer normalize-run examples/card_reward_basic.json --output normalized_run.json
```

Batch-check examples or several run JSON files:

```bash
deckseer check-runs examples
```

Silent example:

```bash
deckseer recommend-card examples/silent_card_reward_basic.json --format text
```

Defect example:

```bash
deckseer recommend-card examples/defect_card_reward_basic.json --format text
```

Necrobinder example:

```bash
deckseer recommend-card examples/necrobinder_card_reward_basic.json --format text
```

Regent example:

```bash
deckseer recommend-card examples/regent_card_reward_basic.json --format text
```

If the installed script directory is not on your PATH, use the module form:

```bash
python -m deckseer.cli recommend-card examples/card_reward_basic.json --format text
python -m deckseer.cli recommend-relic tests/fixtures/relic_choice/elite_frontload.json --format text
```

Use a custom data directory:

```bash
deckseer recommend-card examples/card_reward_basic.json --data-dir data
```

Review card priors against empirical-style stats:

```bash
deckseer audit-card-priors tests/fixtures/empirical/legacy_ironclad_card_stats_sample.json
deckseer audit-card-priors tests/fixtures/empirical/legacy_multi_class_card_stats_sample.json --format text
deckseer audit-card-priors tests/fixtures/empirical/multi_class_conflict_stats.json --format text
```

Review empirical coverage, intake source-review notes, and manual draft promotion:

```bash
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
deckseer empirical-capture-packet data/empirical/drafts/ironclad_sts2fun_current_patch_capture_batch.json --format text
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
```

The original Necrobinder STS2.fun batch worksheet remains intentionally incomplete because `unleash` and `bodyguard` are starter/base cards without normal reward-pick stats in the table. Active reviewed Necrobinder seeds now live in `data/empirical/necrobinder_sts2fun_all_patches_reviewed.json` and `data/empirical/necrobinder_sts2fun_current_patch_reviewed.json`, covering `forbidden_grimoire`, `sleight_of_flesh`, and `defy`. Active current-patch rows also exist for Ironclad, Silent, Defect, and Regent, promoted from screenshot-reviewed worksheets under `data/empirical/drafts/`. `empirical-cross-class-capture-packet`, `empirical-cross-class-apply-packet`, `empirical-cross-class-readiness`, and `empirical-cross-class-promotion-preview` remain available for future cross-class capture sessions. These are convenience wrappers around manual capture only; they do not scrape, promote active empirical rows by themselves, or change scoring. `empirical-current-patch-review` checks the Necrobinder current-patch worksheet against active triage before strict draft check or promotion preview. `empirical-triage-report` explains the active audit flags and next review actions; patch-context warnings are documented as non-blocking. Forbidden Grimoire, Cold Snap, Astral Pulse, and Bulwark have been conservatively calibrated from current-patch evidence while preserving their utility roles and scenario guards. Promotion preview remains separate from active scoring changes; `--allow-review-flags` is required when activating reviewed evidence that should remain visible as audit work.

Inspect a plain JSON Slay the Spire 2 run-history file:

```bash
deckseer inspect-save "C:\Users\moxhe\AppData\Roaming\SlayTheSpire2\steam\76561198030888875\profile1\saves\history\1779010086.run"
```

Create a Deckseer recommendation draft from a run-history file:

```bash
deckseer import-run "C:\path\to\run.run" --card-reward pommel_strike shrug_it_off anger --hp-current 52 --hp-max 80 --act 1 --floor 7
```

Recommend directly from a run-history file plus manual live-state fields:

```bash
deckseer recommend-save "C:\path\to\run.run" --card-reward pommel_strike shrug_it_off anger --hp-current 52 --hp-max 80 --act 1 --floor 7 --format text
```

Add `--include-diagnosis` to `recommend-card` or `recommend-save` when you want the deck profile and top run needs printed with the recommendation.

Run-history imports are read-only. Deckseer normalizes game IDs such as `CARD.STRIKE_IRONCLAD` to `strike`, but you should verify HP, floor, and visible card reward manually.

Deckseer requires metadata for offered reward cards, but it can still score a run when some existing deck cards are not modeled yet. Unknown deck-card metadata is reported in `diagnose-run` under `data_coverage`, and recommendations drop to low confidence until the missing cards are added to `data/cards/`.

Use `check-run-data` when adding new examples or imported runs. Missing reward-card metadata blocks scoring; missing existing-deck metadata only limits diagnosis quality and confidence.

Use `check-runs` to batch-audit a directory like `examples/` or a list of run-state JSON files. Coverage reports include suggestions when a missing card looks like a known card with different spacing, punctuation, or casing.

Shared Deckseer vocabulary lives in `docs/CONTEXT.md`. Hard-to-reverse or surprising project decisions live in `docs/adr/`. Keep these docs updated when a packet sharpens language such as exporter status, status-only diagnostics, visible reward screens, boundary decisions, or human-confirmation-first behavior.

Relic choice advice is a manual JSON-first V1 surface. `recommend-relic` accepts `screen_type: "relic_reward"`, validates visible reward relic IDs against `data/relics/relics.json`, ranks the offered relics, and returns the same JSON/text/Markdown recommendation shape used by card rewards. Unknown reward relics block scoring; unknown owned relics become recommendation risks and lower confidence. Relic Choice V1 is tag-based and does not simulate combat, exact trigger timing, boss relic special rules, or pathing.

Inspect a proposed Deckseer Exporter JSON file:

```bash
deckseer inspect-export tests/fixtures/exporter_card_reward_state.json
deckseer inspect-export tests/fixtures/exporter_status_state.json
```

Run a read-only alert pass over the latest exporter file:

```bash
deckseer export-alert
deckseer export-alert --once
```

`export-alert` watches by default. Use `--once` for a single check. It never recommends or chooses for you. It reads the exporter JSON and prints a loud terminal alert for recommendation-ready exports, true choose-relic overlay proof, unexpected special-route shapes, post-collection mapping gaps, unsupported reward shapes, or exporter diagnostic errors. Proven status-only routes such as deck-enchant grids and pre-collection mixed reward screens stay quiet by default. It is meant as a pause-and-call-Codex aid while playing, not as gameplay automation.
Alert output includes `Codex attention: yes/no`. Mapping gaps already present in the current local repo data are suppressed by default, which keeps the older installed exporter from repeatedly asking for already-reviewed IDs.

## Local MVP Daily Use

For normal play, start Slay the Spire 2 with the already-installed Deckseer Exporter, then start the repo-local play helper in another terminal:

```powershell
.\tools\deckseer-play.cmd
```

You can also double-click `start-deckseer-exporter.cmd` from the repo root. It starts the same read-only helper and keeps the window open if startup fails.

The helper starts `deckseer export-alert`, which watches by default. When it prints an important alert, pause in-game and inspect the exported state first:

```bash
deckseer inspect-export "%LOCALAPPDATA%\Deckseer\exports\latest_state.json"
```

Only after the visible game state matches the export, ask for advice with manual confirmation:

```bash
deckseer recommend-export "%LOCALAPPDATA%\Deckseer\exports\latest_state.json" --confirmed --format text
```

Tiny troubleshooting:

- No exporter file found: make sure STS2 is running with the installed exporter, then wait for `%LOCALAPPDATA%\Deckseer\exports\latest_state.json` to appear.
- Alert says no important state: Deckseer sees an idle or cleared exporter state; keep playing.
- Exporter status instead of card/relic reward: inspect the status only if the alert asks you to pause. Many status-only screens are expected and stay quiet.
- Mapping gap alert with `Codex attention: yes`: pause and ask Codex to inspect it. Do not use `recommend-export --confirmed` until the gap has a reviewed mapping/data follow-up. Pre-collection mixed reward screens wait until the non-card reward has been collected before alerting.
- Recommendation-ready alert with `Codex attention: no`: inspect the export, confirm it matches the visible screen, then run `recommend-export --confirmed --format text`.

Recommend from a proposed Deckseer Exporter JSON file:

```bash
deckseer recommend-export tests/fixtures/exporter_card_reward_state.json --confirmed --format text
deckseer recommend-export tests/fixtures/exporter_relic_reward_state.json --confirmed --format text
```

Check whether the local machine is ready for the future static exporter mod spike:

```bash
deckseer exporter-toolchain-preflight --format text
```

Exporter JSON imports are read-only and human-confirmation-first. Deckseer validates `screen_type: card_reward` and `screen_type: relic_reward`, preserves exporter caveats outside the scorer, and drops exporter metadata before ranking choices. `inspect-export` also accepts `screen_type: exporter_status` as a harmless static exporter-health contract. When a recommendation export has `requires_user_confirmation: true`, run `inspect-export` first and pass `--confirmed` only after checking the visible state. Installed `v0.3.10` exports mixed reward `card_reward` state after clean post-pickup freshness gates and downgrades after the card reward selection screen closes. Installed `v0.4.0` adds ADR 7 human-confirmed live `relic_reward` export for normal reward-screen relics. Installed `v0.4.1` observes treasure chest relics as status-only and clears after pickup. Installed `v0.4.2` fixes the treasure relic identity exception but reports a null public ID. Installed `v0.4.3` uses public `RelicModel.Id` directly and reveals `LETTER_OPENER` as an unmapped review-only treasure relic ID. Installed `v0.4.4` maps reviewed `letter_opener` and verifies mapped treasure clear-state while still refusing treasure export. Installed `v0.4.5` verifies the ADR 8 treasure route refusal contract when `ACCURACY` and `HEART_OF_IRON` are unmapped. Installed `v0.4.6` maps those gaps and live-proves confirmed treasure `relic_reward` export plus post-pickup downgrade. Installed `v0.4.7` adds reviewed mapping coverage for the Envenom card reward gaps, live-proves confirmed `card_reward` export after mixed reward gold pickup, and live-proves post-selection downgrade. Repo-local data and status-diagnostic mapping snapshots now also cover the later `v0.4.7` Finisher/Ricochet/Murder/Tea mapping subset; the real installed mod package was not changed. Event/special route classifier work is design-only in `docs/EXPORTER_EVENT_SPECIAL_ROUTE_CLASSIFIER_DESIGN.md` and proposed ADR 9; those routes remain `exporter_status` diagnostics, not recommendation input.

## State Sources

Deckseer keeps one advisor-ready card reward shape and lets different sources adapt into it:

```text
manual JSON
run-history import
exporter mod JSON
future OCR scan JSON
  -> current-state adapter
  -> card reward advisor
```

Implemented sources:

- **Manual JSON**: primary v0 workflow, loaded directly from a user-authored run-state file.
- **Run-history import**: read-only `.run` history parsing that can draft a recommendation input after you manually provide current HP, act, floor, and visible card reward.
- **Exporter JSON import**: read-only `latest_state.json` contract parsing through `inspect-export`, `export-alert`, and `recommend-export`. `inspect-export` accepts static exporter status files, card reward files, and relic reward files; `export-alert` can warn on important or unexpected exported states without recommending; `recommend-export` supports confirmed card reward and relic reward files. `exporter-toolchain-preflight` reports whether the local STS2 install and modding tools are ready for exporter mod work. These commands consume local files and metadata only.
- **Deckseer Exporter Mod**: preferred live-state path, read-only/export-only, writing local JSON for Deckseer to inspect. The static status spike lives under `exporter_mod/DeckseerExporter` and is documented in `docs/EXPORTER_STATIC_MOD_SPIKE.md`. The card reward API recon lives in `docs/EXPORTER_CARD_REWARD_API_RECON.md`, with compile and install-check results in `docs/EXPORTER_CARD_REWARD_COMPILE_PROBE.md` and the visibility proof sequence in `docs/EXPORTER_CARD_REWARD_VISIBILITY_DESIGN.md`. Installed `v0.3.0` startup fallback passed but mixed reward human confirmation failed because exported gold and potions were stale after non-card reward pickup. Installed `v0.3.1` refuses mixed reward screens with `mixed_reward_screen_state_may_change`; startup, mixed reward-screen, and clear-state verification pass. Installed `v0.3.2` startup passed but did not observe a post-pickup card-choice route in the mixed reward flow. Installed `v0.3.3` adds status-only `RewardCollectedFrom` serializable-run freshness diagnostics; startup, post-gold/potion pickup, and clear-state verification pass while remaining `exporter_status`. Installed `v0.3.4` adds a status-only mixed reward freshness readiness contract with blocker codes, without exporting live scalar values or recommendation-ready state. Installed `v0.3.5` refreshes relic/potion identity review from the post-pickup serializable run while still staying status-only; the live proof revealed `COLORLESS_POTION` -> `colorless_potion` as an unknown mapping. Installed `v0.3.6` adds reviewed `colorless_potion` seed data and status-diagnostic mapping coverage; live proof maps `COLORLESS_POTION` as known while still refusing mixed reward export on alignment/approval blockers. Installed `v0.3.7` retains active visible reward context across `reward_collected` so visible reward player context remains true in status diagnostics. Installed `v0.3.8` retains active run-state context across `reward_collected` as diagnostics only. Installed `v0.3.9` enables mixed reward `card_reward` export after clean post-pickup freshness gates. Installed `v0.3.10` adds the missing card reward selection clear-state hook and verifies closed card reward screens downgrade to `exporter_status`. Installed `v0.4.0` adds ADR 7 human-confirmed live `relic_reward` export for normal reward-screen relics. Installed `v0.4.1` observes treasure chest relics as status-only, refuses live export with `treasure_relic_route_status_only`, and clears after pickup; the live identity probe found a canonical model issue. Installed `v0.4.2` removes that exception but still reports a null public ID. Installed `v0.4.3` switches the diagnostic to public `RelicModel.Id`, reveals `LETTER_OPENER` as unknown review evidence, and clears after pickup. Installed `v0.4.4` maps reviewed `letter_opener` in status diagnostics, verifies the live mapped treasure clear-state path, and still refuses treasure relic live export. Installed `v0.4.5` safely refuses treasure export when deck or potion mappings are incomplete. Installed `v0.4.6` maps `ACCURACY` and `HEART_OF_IRON`, writes confirmed treasure `relic_reward` state on the observed fully mapped run, rejects unconfirmed recommendation, scores `letter_opener` after confirmation, and downgrades after pickup. Installed `v0.4.7` adds reviewed seed data and mapping coverage for `ENVENOM`, `MEMENTO_MORI`, `FASTEN`, and `BLOOD_VIAL`, writes valid startup `exporter_status`, live-proves confirmed `card_reward` export after 15-gold mixed reward pickup, and live-proves post-selection clear-state downgrade. Repo-local data and status-diagnostic mapping snapshots now additionally cover `FINISHER`, `RICOCHET`, `MURDER`, `TOOLS_OF_THE_TRADE`, `PINPOINT`, `ULTIMATE_DEFEND`, `PAELS_EYE`, `TEA_OF_DISCOURTESY`, `CENTENNIAL_PUZZLE`, `MR_STRUGGLES`, `SHURIKEN`, `ORICHALCUM`, `STRIKE_DUMMY`, and `BLESSING_OF_THE_FORGE` without changing the installed real mod package. Adapter contract fixtures cover unknown IDs, upgraded deck cards, confirmation gating, caveats, unsupported upgraded reward-object shape, live card and relic reward fixtures, closed-state fixtures, v0.4.1-v0.4.7 treasure/card reward fixtures, and v0.3.2-v0.3.8 freshness fixtures.

Planned sources:

- **Vision State Extractor**: screenshot/OCR fallback or complement when an exporter mod is unavailable, unwanted, or unreliable.

Source metadata and caveats stay outside the scorer. The recommendation engine receives the same validated card reward payload regardless of where the state came from.
Exporter mod implementation readiness notes live in `docs/EXPORTER_MOD_SURFACE_REVIEW.md`; the first in-game spike wrote only `screen_type: "exporter_status"`, and later guarded packets added confirmed card and relic reward exports.

## Input Shape

Card reward inputs are JSON files with run state, deck contents, current relics and potions, and the offered reward cards.

```json
{
  "game": "slay_the_spire_2",
  "character": "ironclad",
  "act": 1,
  "floor": 7,
  "ascension": 0,
  "gold": 123,
  "hp": {
    "current": 52,
    "max": 80
  },
  "deck": [
    {
      "id": "strike",
      "upgraded": false,
      "count": 4
    }
  ],
  "relics": [
    "burning_blood"
  ],
  "potions": [],
  "card_reward": [
    "pommel_strike",
    "shrug_it_off",
    "anger"
  ],
  "run_context": {
    "recent_damage": 12,
    "next_node_type": "unknown",
    "act_region": "underdocks",
    "upcoming_elites": [
      "skulking_colony",
      "terror_eel"
    ],
    "fought_elites": [],
    "next_nodes": [
      "combat",
      "fire",
      "elite"
    ],
    "fire_before_elite": true,
    "shop_before_elite": false,
    "path_pressure": "elite_soon",
    "boss": null,
    "notes": []
  }
}
```

Skip is always added by Deckseer and should not be included in `card_reward`.

Relic reward inputs use the same run-state fields with `screen_type: "relic_reward"` and a `relic_reward` list:

```json
{
  "game": "slay_the_spire_2",
  "screen_type": "relic_reward",
  "character": "ironclad",
  "act": 1,
  "floor": 7,
  "hp": {
    "current": 63,
    "max": 80
  },
  "deck": [
    {
      "id": "strike",
      "upgraded": false,
      "count": 3
    }
  ],
  "relics": [],
  "potions": [],
  "relic_reward": [
    "akabeko",
    "kunai"
  ]
}
```

All `run_context` fields are optional. The v0.2 context fields let manual JSON capture upcoming threats without requiring pathing automation:

- `act_region`: known region or route theme, such as `underdocks` or `overgrowth`
- `upcoming_elites`: elite fights the current route may face
- `fought_elites`: elite fights already seen this act
- `next_nodes`: visible upcoming node types in route order
- `fire_before_elite` and `shop_before_elite`: whether the route has those setup points before the next elite
- `path_pressure`: short label such as `elite_soon`, `forced_elite`, `boss_soon`, `safe`, or `unknown`

## Data Files

Card, relic, and potion data lives under `data/`. The first dataset is intentionally small and hand-curated. It only encodes metadata needed by the transparent v0 heuristic scorer.

Ironclad currently has the broadest sample coverage. Silent, Defect, Necrobinder, and Regent have initial practical seed sets covering starter-specific cards, early frontload, block, draw, class themes, and scaling cards. The card data includes curated slices from local tier lists, with simple roles and effects rather than full combat text.

Card data may include optional `roles` used by the run-needs scorer:

```json
{
  "id": "pommel_strike",
  "name": "Pommel Strike",
  "character": "ironclad",
  "type": "attack",
  "rarity": "common",
  "cost": 1,
  "tags": ["damage", "draw"],
  "roles": ["frontload", "draw", "consistency"],
  "quality_prior": 4.5,
  "pick_context": ["early", "frontload", "consistency"],
  "source_patch": "v0.102.0",
  "source_notes": ["Ironclad local tier list: S tier."],
  "upgrades_to": "pommel_strike_plus",
    "effects": {
      "damage": 9,
      "block": 0,
      "draw": 1,
      "energy": 0,
      "extra": {}
    }
}
```

Card priors are optional and intentionally weak. They can help close decisions, but run needs and context should dominate. A strong prior that misses the top diagnosed need should show up as a caveat rather than silently overriding the recommendation.

`effects.extra` is optional and can hold reviewed numeric effect metadata that does not fit the core `damage`, `block`, `draw`, and `energy` fields, such as poison, weak, vulnerable, strength changes, or x-cost markers. These values remain simplified metadata for transparent heuristics, not exact combat simulation rules.

Empirical-style stats under `data/empirical/` are active project review inputs for read-only audits. Active traceable rows now cover all five catalog classes: Necrobinder has All Patches and current-patch STS2.fun rows, and Ironclad, Silent, Defect, and Regent have screenshot-reviewed current-patch rows. Pending or closed source-review notes live in `data/empirical/intake_queue.json` and are not active evidence; `empirical-intake` reports `PASS` when no proposed intake work remains. Legacy seed rows and artificial conflict rows used to exercise audit behavior live under `tests/fixtures/empirical/`. The audit workflow flags cards for human review; it does not rewrite card data.
Audit output includes summary counts by flag code, severity, and character so review passes can be triaged before touching card priors.

## Scoring Philosophy

The v0 scorer is deterministic and rule-based. It first diagnoses run needs, then scores cards by how well they solve those needs. It combines:

- frontload, defense, scaling, consistency, energy, deck quality, and Skip pressure
- run context such as act, floor, and HP pressure
- simple tag synergy with the deck and relics
- weak, patch-aware card quality priors from reviewed sources
- a separate Skip score that rises when the deck is already large or fundamentals are covered

Generic card quality still matters, but it is intentionally secondary to the current run's needs. The rules are designed to be easy to inspect and change, not to be perfect strategy.

## Roadmap

### Current Focus: Manual Card Reward Advisor

Deckseer v0 stays focused on a small manual workflow:

- read structured JSON run-state files
- rank card reward choices, including Skip
- provide deterministic scores, reasoning, confidence, and caveats
- avoid GUI work, screen reading, gameplay automation, and LLM dependency

The core recommendation engine should remain usable without an LLM. Future explanation layers may help rewrite or expand reasoning, but they should not be required for scoring.

### Future Milestone: Deckseer Exporter Mod

The preferred long-term live-state path is a small Slay the Spire 2 companion mod that exports the current run and decision state to local JSON. Deckseer would read that exported JSON using the same decision engine and schemas as the manual v0 workflow.

The first static status spike is implemented under `exporter_mod/DeckseerExporter` and documented in `docs/EXPORTER_STATIC_MOD_SPIKE.md`. Installed `v0.4.7` contains the current guarded live card reward implementation, refuses mixed reward screens before non-card reward pickup, exports confirmed mixed reward `card_reward` state after freshness and mapping gates are clean, and downgrades back to `exporter_status` after the card reward selection screen closes. The exporter path should stay read-only and export-only:

- no mouse or keyboard automation
- no gameplay control
- no gameplay farming
- no memory reading outside normal mod-accessible game state
- no packet inspection
- no anti-cheat bypassing, stealth, or evasion
- user-visible local JSON output that can be inspected, confirmed, or edited

Planned data flow:

```text
Slay the Spire 2 companion mod
  -> exports current run state to local JSON
  -> Deckseer reads that JSON
  -> Deckseer recommends decisions
```

Example future exporter output shape:

```json
{
  "screen_type": "card_reward",
  "character": "ironclad",
  "act": 1,
  "floor": 8,
  "hp": {
    "current": 42,
    "max": 75
  },
  "gold": 113,
  "deck": [
    {
      "id": "strike",
      "upgraded": false,
      "count": 4
    }
  ],
  "relics": [
    "burning_blood"
  ],
  "potions": [
    "fire_potion"
  ],
  "card_reward": [
    "card_a",
    "card_b",
    "card_c"
  ],
  "export_metadata": {
    "source": "deckseer_exporter_mod",
    "requires_user_confirmation": true
  }
}
```

Exporter milestone breakdown:

- **Exporter 1: Modding Surface Research**: use `docs/EXPORTER_MOD_DESIGN.md` as the boundary and contract, then document how STS2 mods are packaged, loaded, and allowed to access current run state. Confirm whether a read-only exporter is viable before writing mod code.
- **Exporter 2: Static JSON Export Spike**: implemented. The local companion mod writes a harmless `screen_type: "exporter_status"` JSON file only.
- **Exporter 3: Card Reward API Recon**: completed. `docs/EXPORTER_CARD_REWARD_API_RECON.md` identifies likely public STS2 reward/run-state surfaces from local metadata before live export.
- **Exporter 4: Card Reward Compile Probe**: completed. The mod source compile-checks a narrower public API set while continuing to write only status/diagnostic JSON.
- **Exporter 5: Status Diagnostic Install Check**: completed after explicit approval. The installed `v0.2.0` build writes valid `exporter_status` JSON with compile-probe diagnostics only.
- **Exporter 6: Safe Hook-Model Compile Probe**: completed in repo-local `v0.2.1` source. The dormant probe proves the `SingletonModel` + `ModelDb.Inject` + `ModelDb.Singleton<T>()` path without registering a live hook or exporting live state.
- **Exporter 7: Card Reward Visibility Diagnostic**: installed `v0.2.8` verified, adapter contract hardening complete, and status-only ID diagnostics remain outside recommendation input. Rejected `v0.3.x` attempts, the active reward stack compile blocker, the follow-up active reward source research, and the ADR 2 public screen observation decision are documented in `docs/EXPORTER_CARD_REWARD_VISIBILITY_DESIGN.md`. Installed `v0.2.8` reports ID-shape counts for both public routes and observed a visible three-card reward with 2 known and 1 unknown mapping by count only. Installed `v0.2.9` implements the accepted ADR 3 ID-revealing status diagnostic for mapping review and passed visible-screen verification; installed `v0.2.10` adds the accepted ADR 4 status-only public run-state compile probe; installed `v0.2.11` adds a status-only runtime presence diagnostic and passes startup/visible/clear verification; installed `v0.2.12` adds the accepted ADR 5 status-only deck ID review diagnostic and passes startup verification; installed `v0.2.13` adds reviewed Silent starter aliases and passes startup/visible/clear verification; installed `v0.2.14` maps reviewed `dramatic_entrance` and passes startup/visible/clear verification; installed `v0.2.16` reveals relic/potion IDs under the accepted ADR 6 status-only boundary; installed `v0.2.17` maps the two reviewed relic IDs and reports a ready status-only candidate on the visible reward screen.
- **Exporter 8: Card Reward Export**: installed `v0.3.0` startup fallback passed but mixed reward confirmation failed on stale gold/potions. Installed `v0.3.1` refuses mixed reward screens and passes startup, mixed reward-screen, and clear-state verification. Installed `v0.3.2` startup passed but did not observe a post-pickup card-choice route in the mixed reward flow. Installed `v0.3.3` adds status-only reward-collected freshness diagnostics and passes startup, post-gold/potion pickup, and clear-state verification while staying non-recommendation-ready. Installed `v0.3.4` adds mixed reward freshness blocker diagnostics and passes startup, post-gold/potion pickup, and clear-state verification while staying non-recommendation-ready. Installed `v0.3.5` refreshes post-pickup potion identity review diagnostics and passes startup, post-gold/potion pickup, and clear-state verification while staying non-recommendation-ready. Installed `v0.3.6` maps reviewed `COLORLESS_POTION` -> `colorless_potion` in status diagnostics only and still refuses mixed reward export on alignment/approval blockers. Installed `v0.3.7` removes the visible reward player blocker in status diagnostics only. Installed `v0.3.8` removes the run-state context blocker in status diagnostics only. Installed `v0.3.9` enables mixed reward `card_reward` export only after clean post-pickup freshness gates and still requires confirmation. Installed `v0.3.10` fixes and verifies clear-state downgrade after card reward selection. Installed `v0.4.7` maps the Envenom/Predator/Memento Mori Silent gaps and live-proves confirmed mixed reward card export plus post-selection downgrade. Repo-local mapping data now covers the later Finisher/Ricochet/Murder/Tea status-only subset; no live install was changed.
- **Exporter 9: Relic Reward Export**: installed `v0.4.0` implements ADR 7 human-confirmed live `screen_type: "relic_reward"` export using the existing confirmed relic exporter adapter for normal reward-screen relics. Installed `v0.4.1` proves treasure chest relic observation and clear-state as status-only. Installed `v0.4.2` fixes the treasure relic identity exception but leaves public ID null in live proof. Installed `v0.4.3` uses public `RelicModel.Id`, proves `LETTER_OPENER` identity review as status-only, and clears after pickup. Installed `v0.4.4` adds reviewed `letter_opener` mapping coverage and live-verifies mapped treasure clear-state before treasure promotion. Installed `v0.4.5` accepts ADR 8's treasure readiness contract but safely refuses the observed run because `ACCURACY` and `HEART_OF_IRON` are unmapped. Installed `v0.4.6` maps those gaps and live-proves successful treasure `relic_reward` export with confirmation and post-pickup downgrade.
- **Exporter 10: Deckseer Watch Mode**: add an optional Deckseer CLI mode that reads the latest exported JSON and prints recommendations after user confirmation. A narrower read-only `export-alert` command now watches by default for pause-worthy state notifications only; it does not recommend.
- **Exporter 11: Broader Decision Export**: extend exported state for potion choices, pathing, shop, combat basics, and other advisor modules as they are added.

### Future Milestone: Vision State Extractor

Deckseer should eventually be able to read visible game information from screenshots and convert it into structured JSON game state that the existing decision engine can consume. This is a fallback or complementary path when a companion exporter mod is unavailable, unwanted, or unreliable. This milestone is for human-in-the-loop decision assistance only.

The Vision State Extractor must stay within these boundaries:

- screenshot-based reading of visible information only
- no mouse or keyboard automation
- no gameplay farming
- no memory reading
- no packet inspection
- no anti-cheat bypassing, stealth, or evasion
- user confirmation or editing before recommendations, especially when confidence is low

Planned approach:

- start with screenshot image files from disk
- classify the screen type first, such as `card_reward`, `map`, `shop`, `relic_reward`, `potion_reward`, `combat`, or `event`
- use fixed crop regions for known resolutions, starting with `1920x1080`
- OCR only small known UI regions, such as card title areas, HP, gold, and potion names
- use OpenCV template or icon matching for relics, potions, map nodes, enemy intents, and other visual elements
- output confidence scores and caveats with detected state

Potential future tools:

- screenshot capture from image files first, then optional PyAutoGUI or MSS
- DXcam later for Windows game capture if normal screenshots are too slow or unreliable
- Tesseract/pytesseract first for OCR
- EasyOCR or PaddleOCR later if game text is too stylized for Tesseract
- OpenCV for crops, preprocessing, template matching, and icon detection

Planned future folder layout, not implemented yet:

```text
src/deckseer/
  vision/
    __init__.py
    capture.py
    scan.py
    crop_regions.py
    preprocess.py
    ocr.py
    templates.py
    screen_classifier.py
    state_extractor.py
  vision/templates/
    screens/
    relics/
    potions/
    map_nodes/
    enemy_intents/
  vision/regions/
    1920x1080.json
    2560x1440.json
samples/
  screenshots/
    card_reward_001.png
    map_001.png
    shop_001.png
```

Future CLI example:

```bash
python -m deckseer.vision.scan samples/screenshots/card_reward_001.png
```

Expected future output shape:

```json
{
  "screen_type": "card_reward",
  "resolution": "1920x1080",
  "detected": {
    "card_options": [
      {
        "name": "Example Card A",
        "confidence": 0.91
      },
      {
        "name": "Example Card B",
        "confidence": 0.86
      },
      {
        "name": "Example Card C",
        "confidence": 0.77
      }
    ]
  },
  "caveats": [
    "Card 3 confidence is below threshold; user confirmation recommended."
  ]
}
```

Vision milestone breakdown:

- **Vision 1: Screenshot File Scanner**: read a screenshot from disk, detect basic screen type, apply fixed `1920x1080` crop regions, OCR the three card reward title regions, and output structured JSON. No live capture or input automation.
- **Vision 2: Screenshot-Assisted Card Advisor**: use detected card reward options as input to the existing recommendation engine, show detected state first, require user confirmation or editing, then produce a recommendation.
- **Vision 3: Icon/Template Matching**: add OpenCV template matching for relics, potions, map nodes, enemy intents, and screen classification. Store templates under `vision/templates` and report match confidence.
- **Vision 4: Live Screenshot Capture**: add optional screenshot capture using PyAutoGUI or MSS, and consider DXcam on Windows if needed. Still no automated clicking or gameplay control.
- **Vision 5: Broader State Extraction**: extract HP, max HP, gold, potions, relics, map node choices, shop inventory, and combat basics while preserving human confirmation before use.

Other future recommendation areas can include relic advice, potion advice, pathing, combat advice, run history, outcome learning, and optional LLM explanation.

Relic choice is the approved first broader advice surface after card rewards. The design boundary lives in `docs/RELIC_CHOICE_DESIGN.md`; `recommend-relic` supports manual JSON relic rewards, `recommend-export --confirmed` supports proposed relic exporter files, and `relic-accuracy-report` checks six reviewed relic-choice drift scenarios.
