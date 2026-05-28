# Deckseer Relic Choice Design

This document defines the first broader advice surface after card rewards: deterministic, manual JSON relic choice advice. The design, metadata seed, private scorer, public `recommend-relic` CLI, confirmed exporter recommendation, and relic accuracy report packets are now complete. Later ADR 7 and ADR 8 packets added human-confirmed live exporter support for normal and treasure relic rewards without changing card reward behavior or baselines.

## Goal

Relic Choice V1 should rank visible relic reward options for a known run state and explain the recommendation with the same local, deterministic, human-in-the-loop posture as card reward advice.

The first implementation should answer:

- Which visible relic option best fits this run?
- Why does it fit the current deck, class, act, and route pressure?
- What caveats should lower confidence?
- Which unknown or under-modeled relic metadata limits the recommendation?

## Non-Goals

Relic Choice V1 must not include:

- Watcher mode, OCR, screenshots, or unapproved exporter expansion.
- Gameplay automation, input control, memory/process tricks, packet inspection, stealth, or evasion.
- Combat simulation or exact relic trigger simulation.
- Path optimization or map branch ranking.
- Shop purchase optimization.
- Automatic relic data import.
- Changes to card reward scoring, card priors, empirical rows, recommendation baselines, or accepted accuracy scenarios.

## Proposed Input Shape

Relic choice should start as a manual JSON source, parallel to the existing card reward shape. It should reuse the current run-state fields and add a visible `relic_reward` list.

```json
{
  "game": "slay_the_spire_2",
  "screen_type": "relic_reward",
  "character": "ironclad",
  "act": 1,
  "floor": 16,
  "ascension": 0,
  "gold": 123,
  "hp": {
    "current": 42,
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
  "potions": [
    "fire_potion"
  ],
  "relic_reward": [
    "akabeko",
    "kunai"
  ],
  "run_context": {
    "act_region": "underdocks",
    "next_nodes": [
      "combat",
      "fire",
      "elite"
    ],
    "path_pressure": "elite_soon",
    "notes": [
      "Visible/manual state only."
    ]
  }
}
```

Open design decisions for implementation:

- Whether `screen_type` is required for manual relic inputs or only exporter-style inputs.
- Whether boss relic choices should use the same `relic_reward` field with a `reward_context` label.
- Whether duplicate-owned relics should be rejected, warned, or left to source validation.

Default recommendation: keep V1 permissive and explicit. Accept a manual `relic_reward` list, preserve unknown IDs as validation errors for reward options, and add caveats for existing owned relics that Deckseer cannot model.

## Proposed Output Shape

Relic advice should mirror the card reward result style without reusing card-specific names.

```json
{
  "decision_type": "relic_choice",
  "ranked_choices": [
    {
      "relic_id": "akabeko",
      "name": "Akabeko",
      "score": 42.0,
      "confidence": "medium",
      "reasons": [
        "Improves immediate frontload for an elite-pressure route."
      ],
      "risks": [
        "Relic metadata is simplified and does not model all trigger timing."
      ]
    }
  ],
  "caveats": [
    "Relic Choice V1 is tag-based and does not simulate combat."
  ]
}
```

Text output should be compact and familiar:

```text
Relic Choice
1. Akabeko (akabeko) - 42.0 [medium]
   Why: Improves immediate frontload for an elite-pressure route.
   Risks: Relic metadata is simplified and does not model all trigger timing.
```

## Relic Metadata V1

Current relic data only has `id`, `name`, and `tags`. Relic Choice V1 should introduce richer metadata only after a reviewed seed plan is approved.

Proposed optional fields:

- `roles`: strategy roles such as `frontload`, `defense`, `scaling`, `draw`, `energy`, `sustain`, `economy`, `deck_quality`, or `consistency`.
- `quality_prior`: weak baseline value, reviewed and patch-aware.
- `pick_context`: contexts where the relic is better, such as `early`, `elite_prep`, `low_hp`, `attack_dense`, `skill_dense`, `power_scaling`, or `boss_reward`.
- `source_patch`: patch or build the metadata was reviewed against.
- `source_notes`: compact review notes, not copied source text.
- `effects.extra`: simplified numbers only when reviewed, such as bonus damage, block, healing, gold, card draw, or trigger count.

Do not add these fields in bulk without reviewed source notes. The first metadata expansion should be small enough to audit by hand.

## Scoring Philosophy

Relic Choice V1 should be heuristic and transparent, not a combat solver.

Suggested scoring factors:

- **Run needs fit**: match relic roles/tags against diagnosed needs such as frontload, defense, scaling, consistency, sustain, or deck quality.
- **Deck shape fit**: reward overlap with deck tags/roles, such as attack density for attack relics or skill density for block/dexterity relics.
- **Class fit**: account for class themes only when metadata explicitly supports it.
- **Act and path pressure**: value immediate power more when an elite, boss, or low-HP route is near.
- **Owned relic synergy**: reward simple tag overlap with owned relics, but keep it secondary.
- **Quality prior**: use weak priors only as tie-breakers, with caveats when a relic does not address the top run need.
- **Unknown/under-modeled risk**: lower confidence when key relic effects are missing or simplified.

Avoid:

- Exact expected-value claims.
- Hidden information assumptions.
- Trigger simulation unless a future dedicated combat model exists.
- Letting generic relic quality silently override urgent run needs.

## Confidence Rules

High confidence:

- Reward relic metadata is complete enough for V1.
- The top relic clearly addresses the top diagnosed run need.
- The alternatives are lower fit or more speculative.
- No major unknown existing relic/deck metadata affects the decision.

Medium confidence:

- The top relic fits a meaningful need, but metadata is simplified.
- Alternatives are close or solve different needs.
- Existing relic synergy is shallow but understandable.

Low confidence:

- One or more reward relics are unknown or sparsely modeled.
- The decision depends on exact fight, map, shop, or boss information not present in the input.
- The top score is mostly generic quality rather than current-run fit.

## Validation Plan

Implementation validation:

1. Add a private relic choice model/scorer module. Completed in `src/deckseer/relic_choice.py`.
2. Add focused unit tests for score ordering, caveats, and confidence labels. Completed in `tests/test_relic_choice.py`.
3. Add two to four small fixture states under `tests/fixtures/relic_choice/`. Completed for frontload, sustain, and scaling contexts.
4. Keep fixtures proposed until expected picks are reviewed. Completed for the private scorer and CLI packets.
5. Run `pytest` and the standard Deckseer QA gate.

CLI validation:

- Confirm output wording is stable.
- Confirm unknown reward relic IDs fail clearly.
- Confirm unknown owned relic IDs become caveats rather than blockers.
- Confirm card reward commands and accuracy scenarios do not drift.

## Proposed Packet Sequence

1. **Design packet**: this document.
2. **Metadata review packet**: define a tiny reviewed relic metadata seed plan without changing advice behavior. Completed in `docs/RELIC_METADATA_SEED_PLAN.md`.
3. **Private scorer packet**: implement a non-public relic choice scorer with tests and fixtures. Completed in `src/deckseer/relic_choice.py`.
4. **CLI packet**: add a public command such as `recommend-relic` now that private scorer output is covered by focused tests. Completed with `recommend-relic`.
5. **Exporter contract packet**: document `screen_type: "relic_reward"` only after manual relic advice works. Completed in `docs/EXPORTER_MOD_DESIGN.md`.

## Stop Rules

Stop and ask before:

- Adding additional public relic choice commands or changing `recommend-relic` behavior.
- Adding or changing relic data beyond a tiny reviewed seed packet.
- Introducing new schema requirements for existing card reward inputs.
- Changing card reward scoring or run diagnosis behavior.
- Adding unapproved exporter behavior, OCR, vision, live capture, watcher, or game mod behavior.
- Adding dependencies.
- Making boss relic choice use a different input/output surface from normal relic rewards.

## Recommended Next Packet

The relic choice regression manifest is complete with `relic-accuracy-report`, and relic metadata expansion readiness is documented in `docs/RELIC_METADATA_EXPANSION_READINESS.md`. Reviewed expansion batches have added `ring_of_the_snake`, `lead_paperweight`, and `letter_opener`; installed exporter `v0.4.6` has live-proven confirmed treasure relic export for `letter_opener`. Future data-changing packets should remain tiny reviewed batches with matching relic accuracy scenarios.
