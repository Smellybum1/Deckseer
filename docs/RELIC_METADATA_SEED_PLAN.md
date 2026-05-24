# Deckseer Relic Metadata Seed Plan

This packet expands only the existing three seed relic records so Relic Choice V1 has enough reviewed metadata to support a private scorer. It does not add a relic advice engine, public CLI, fixtures, exporter support, card reward scoring changes, or baselines.

## Seed Scope

Current seed relics:

| Relic | V1 roles | Weak prior | Pick context | Notes |
| --- | --- | ---: | --- | --- |
| `burning_blood` | `sustain` | 3.0 | `low_hp`, `long_act` | Sustain and HP recovery context. |
| `akabeko` | `frontload` | 4.0 | `early`, `elite_prep`, `attack_dense` | Immediate frontload context. |
| `kunai` | `defense`, `scaling` | 4.0 | `attack_dense`, `skill_dense`, `long_act` | Attack-density payoff that can improve block over longer fights. |

The values are intentionally weak planning metadata. They are not exact expected value claims and do not model trigger timing.

## Metadata Fields

Relic Choice V1 seed records may use:

- `roles`: strategy roles for run-need matching.
- `quality_prior`: weak baseline value for tie-breaking.
- `pick_context`: simple contexts where the relic is more likely to fit.
- `source_patch`: `deckseer_relic_seed_v1` for this seed packet.
- `source_notes`: compact review notes that explain the simplified assumption.

The existing `tags` field remains the primary compatibility field for card reward relic synergy.

## Guardrails

- Do not add new relic IDs in this seed packet.
- Do not add numeric trigger effects until reviewed against current STS2 behavior.
- Do not change card reward scoring or its relic synergy logic.
- Do not make relic metadata health blocking yet.
- Keep unknown owned relics as future caveats rather than blockers for the planned scorer.

## Validation

Focused validation:

```bash
python -m pytest tests/test_models.py tests/test_data_summary.py
```

Project validation:

```bash
python -m deckseer.cli qa --check-recommendation-baseline --check-accuracy --check-empirical-triage
python -m pytest
```

Expected behavior remains unchanged for card reward advice.

## Next Packet

The next packet should implement a private relic choice scorer and tests against small fixtures. It should stay private until output wording, confidence, and caveats are stable.
