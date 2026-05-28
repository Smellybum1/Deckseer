# Deckseer Accuracy Review

Deckseer is currently focused on calibration quality, not new input surfaces. The advisor is stable enough to check whether recommendations match reviewed high-level play patterns for specific run states.

## Current QA Snapshot

- `pytest` passes across the current suite (`395 passed` at the latest verification).
- `deckseer data-health` reports `PASS`.
- `deckseer qa --check-recommendation-baseline --check-accuracy` reports `REVIEW` because active empirical rows intentionally surface audit flags while recommendation baseline and accuracy checks pass.
- `deckseer qa --check-recommendation-baseline --check-accuracy --check-empirical-triage` reports `PASS` because all active empirical flags are triaged as non-blocking context.
- Current card coverage is 180 hand-curated records across Ironclad, Silent, Defect, Necrobinder, Regent, and Neutral.
- `deckseer accuracy-report` checks the reviewed scenario manifest and currently passes all ten scenarios.
- Active empirical coverage has 18 traceable rows across all five classes, with 14 audit flags: all patch-context warnings.

## Accuracy Boundaries

- Manual JSON remains the source of truth for v0.
- Empirical stats are review prompts, not automatic rewrites.
- Creator notes and tier lists become compact claims, scenarios, card metadata, or tests only after review.
- Scoring should remain deterministic, explainable, and run-needs first.
- No OCR, exporter mod, GUI, live capture, automation, or LLM dependency is part of this calibration pass.

## Known Scoring Limits

- Card data is simplified metadata, not full combat rules text.
- Relic and potion modeling is sparse.
- Synergy scoring is intentionally shallow and mostly tag/role based.
- Current scenario coverage is hand-authored and should be expanded with reviewed real-run examples.
- Active empirical values are manually reviewed samples, not production-quality STS2.fun imports.
- Artificial empirical conflict rows live under `tests/fixtures/empirical/`, not active project data.

## Empirical Flag Triage

| Flag | Meaning | Current use | Review action |
| --- | --- | --- | --- |
| `low_prior_strong_empirical` | A card has a neutral/low prior but strong empirical impact. | Review prompt only. | Check patch, sample size, class context, and whether the card needs a higher prior or narrower pick context. |
| `high_prior_weak_empirical` | A card has a high prior but weak empirical impact. | Review prompt only. | Check whether the card is overvalued, context-dependent, or hurt by patch drift. |
| `patch_mismatch` | Deckseer metadata and empirical source use different patches. | Warning. | Do not change priors until the patch mismatch is resolved or explicitly accepted. |
| `missing_card_data` | Empirical stats reference a card missing from local data. | Warning. | Add reviewed card metadata before using that stat for calibration. |
| `small_sample_size` | Sample size is below the audit threshold. | Info. | Avoid changing priors from this stat alone. |

## Review Queue

1. Grow scenario fixtures from hand-authored cases into reviewed examples from actual runs.
2. Keep `qa --check-recommendation-baseline` stable while intentional scoring changes are reviewed through `qa-baseline`.
3. Defer live STS2.fun ingestion until manual evidence review remains stable across more calibration passes.
4. Keep exporter-derived scenarios human-confirmed and review-only until their expected choices are accepted.
5. Watch the accepted `silent_v047_envenom_attack_payoff_guard` scenario for future drift. It guards a narrow attack/Shiv payoff calibration where Envenom should beat duplicate Predator and low-fit Memento Mori in the reviewed late Act 1 Silent state.

## Scenario Review Workflow

Reviewed calibration scenarios live in `data/accuracy/scenarios.json`. Each entry points to a normal Deckseer run-state JSON file, records the expected top choice, and lists reasoning keywords that should appear in the recommendation.

Manifest entries must use unique IDs, include at least one expected reasoning keyword, and use a `review_status` of `proposed`, `accepted`, `implemented`, or `rejected`. Relative scenario paths are resolved from the project working directory; absolute paths are allowed for local review manifests.

Use `docs/ACCURACY_SCENARIO_INTAKE.md` when turning a real-run decision into a new scenario. The intake checklist records the required source context, fixture review steps, and acceptance rules. Scenario intake should not change scoring, card priors, empirical data, recommendation APIs, or baselines by itself.

Use the standalone report when reviewing recommendation drift:

```bash
deckseer accuracy-report --format text
deckseer accuracy-report --format json
deckseer accuracy-report --fail-on-mismatch
```

Use QA integration only when you explicitly want project QA to include scenario drift:

```bash
deckseer qa --check-accuracy
```

Normal `deckseer qa` does not run accuracy scenarios. This keeps routine data-health and empirical review checks stable while allowing intentional scoring changes to be reviewed separately.

Update scenario expectations only after reviewing the changed recommendation and deciding that the new top choice better matches the scenario. If the change is intentional, update the manifest and keep the scenario fixture itself available for `recommend-card` smoke checks.

The accuracy report summary includes total passed/failed scenarios, failed scenario IDs, review-status counts, and pass/fail counts by review status. Treat mismatches as review work: either fix the scoring/data issue or update the scenario expectation with a note explaining why the new recommendation is preferred.
