# Deckseer Relic Metadata Expansion Readiness

This document defines the safe intake path for expanding Relic Choice V1 beyond the three seed relics. It is a readiness packet only: it does not add relic records, change priors, change scoring, alter exporter behavior, or add live capture.

## Goal

Future relic metadata expansion should improve `recommend-relic` coverage without turning the relic scorer into an unsupported combat simulator. Each new relic should be traceable, conservative, and guarded by at least one reviewed relic-choice scenario before it is treated as reliable advice.

## Intake Requirements

Each candidate relic needs:

- `id`, `name`, and simple `tags`.
- Reviewed `roles` chosen from the existing V1 vocabulary where possible: `frontload`, `defense`, `scaling`, `draw`, `energy`, `sustain`, `economy`, `deck_quality`, or `consistency`.
- Conservative `quality_prior`, defaulting to `0.0` when evidence is unclear.
- `pick_context` only when the context is explicit and reviewable, such as `early`, `elite_prep`, `low_hp`, `attack_dense`, `skill_dense`, `long_act`, or `boss_reward`.
- `source_patch` and short `source_notes` that identify the review basis without copying source text.
- At least one accepted relic accuracy scenario when the new relic is expected to alter a recommendation.

## Expansion Workflow

1. Create a small draft batch of no more than five relics.
2. Add only metadata that can be reviewed from local notes, user-provided evidence, or explicitly cited public sources.
3. Keep priors weak; use roles and context fit to explain recommendations.
4. Add or update relic-choice fixtures before changing expectations.
5. Add accepted entries to `data/relic_accuracy/scenarios.json` only after reviewing `recommend-relic --format text`.
6. Run `relic-accuracy-report --format text` and keep all accepted relic scenarios passing.
7. Run `data-health`, `recommend-relic`, standard QA, and full pytest before committing.

## Stop Rules

Stop and ask before:

- Adding more than five relics in one packet.
- Adding exact trigger simulation, combat math, or boss relic special rules.
- Adding new relic role vocabulary not already documented.
- Changing existing relic priors or roles without a reviewed scenario explaining the drift.
- Using exporter, OCR, live capture, game files, or external installs as part of metadata intake.
- Changing card reward scoring, card priors, empirical rows, or accepted card accuracy expectations.

## Validation Commands

```bash
python -m deckseer.cli data-health
python -m deckseer.cli recommend-relic tests/fixtures/relic_choice/elite_frontload.json --format text
python -m deckseer.cli relic-accuracy-report --format text
python -m deckseer.cli qa --check-recommendation-baseline --check-accuracy --check-empirical-triage
python -m deckseer.cli empirical-coverage --format text
python -m deckseer.cli accuracy-report --format text
python -m pytest
```

Expected current state:

- `data-health`: `PASS`.
- `relic-accuracy-report`: `PASS`, 6/6.
- Triage-aware QA: `PASS`.
- Empirical coverage: `REVIEW` with 18 rows and 14 `patch_mismatch` warnings.
- Card accuracy: `PASS`, 10/10.

## Recommended Next Packet

The next implementation packet may add the first reviewed relic metadata batch only if the candidate relics have source notes and the packet includes matching relic accuracy scenarios. If no reviewed candidates are available, keep relic metadata unchanged and work on exporter toolchain readiness or reviewed card accuracy intake instead.
