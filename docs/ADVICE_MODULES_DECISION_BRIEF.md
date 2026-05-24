# Deckseer Advice Modules Decision Brief

This brief frames the next broader advice milestone after the manual card reward advisor. It does not add any runtime behavior, public CLI, schemas, scoring, card data, relic data, potion data, or baselines.

## Current State

Deckseer already accepts `relics` and `potions` in the manual run-state shape, but they are currently supporting context for card reward scoring rather than first-class advice surfaces.

Current local data is intentionally sparse:

- Relics: `burning_blood`, `akabeko`, and `kunai`.
- Potions: `fire_potion` and `block_potion`.
- The card reward scorer uses simple relic tag overlap for card synergy.
- There is no relic choice, potion usage, pathing, shop, or combat planner yet.

## Candidate First Surfaces

### Relic Choice Advice

Relic choice advice would rank visible relic reward options against the current run state.

- Impact: medium. Relic rewards are meaningful and relatively discrete.
- Risk: medium. Relic value depends on boss swaps, class mechanics, deck shape, and hidden future fights, but it can start with transparent tags.
- Data needed: relic IDs, names, tags, rough roles, source notes, and a small accepted scenario set.
- Likely inputs: current deck, character, act, floor, HP, relics owned, offered relic IDs, and optional run context.
- First safe output: ranked relic choices with reasoning, confidence, and caveats.
- Validation: fixture-based relic-choice scenarios, data-health coverage, and stable text/JSON rendering.
- Main caveat: sparse relic metadata makes this a data-expansion packet before it becomes a reliable advisor.

### Potion Usage Advice

Potion usage advice would say whether a held potion should be used in an upcoming or current fight.

- Impact: medium. Good potion use can save meaningful HP and helps elite planning.
- Risk: medium-high. Useful recommendations need enemy state, current hand, potion target rules, or at least a specific upcoming threat.
- Data needed: potion IDs, target restrictions, effect magnitude, fight context, and expected HP saved or damage pushed.
- Likely inputs: current HP, potions, enemy or upcoming elite context, current hand if combat-specific, and path pressure.
- First safe output: non-combat planning caveats such as "consider spending Fire Potion before this elite if lethal math or HP preservation matters."
- Validation: reviewed combat or elite-prep scenarios.
- Main caveat: exact potion usage can sprawl into combat simulation quickly.

### Pathing Advice

Pathing advice would compare visible map options.

- Impact: high later. Pathing strongly affects card reward value, relic count, upgrades, and survival.
- Risk: high. It needs visible map state, branch alternatives, rest sites, shops, elite possibilities, and route uncertainty.
- Data needed: map node schema, region/elite metadata, reward heuristics, and bailout rules.
- Likely inputs: current run state plus visible map branches.
- First safe output: route risk/reward notes rather than a single definitive pick.
- Validation: reviewed pathing scenarios.
- Main caveat: Deckseer has no map input surface yet.

### Combat Planning Advice

Combat planning would advise turn sequencing or fight plans.

- Impact: high later. Combat decisions drive HP preservation and run outcomes.
- Risk: very high. It needs hand, draw pile, discard pile, enemy intents, powers, relic triggers, and status effects.
- Data needed: much richer card, enemy, relic, and potion mechanics.
- Likely inputs: detailed combat state.
- First safe output: docs-only design until combat state exists.
- Validation: deterministic combat fixtures and reviewed expected turns.
- Main caveat: this is far outside the current simplified heuristic model.

## Recommendation

The lowest-risk first implementation target is **relic choice advice**, but only after a design packet defines the input contract and a small seed data plan.

Why relic choice first:

- It can reuse the existing local/manual JSON style without live capture.
- It is less dependent on exact turn-by-turn combat state than potion usage.
- It can start with transparent, tag-based reasoning similar to current card reward explanations.
- It provides a natural data-health path for expanding sparse relic metadata.

Potion usage should come after relic choice design unless the user specifically wants elite-prep potion planning first. Exact potion recommendations should wait for reviewed fight-context fixtures.

## Proposed Relic Choice V1 Boundary

Allowed:

- Manual JSON input only.
- Visible relic choice options only.
- Existing run-state fields plus a `relic_reward` list in a proposed design doc.
- Deterministic ranking with confidence and caveats.
- Sparse metadata warnings when a relic is unknown or under-modeled.
- Fixture-based tests before any public command is added.

Out of scope:

- Live game capture, watcher mode, OCR, or exporter expansion.
- Combat simulation.
- Map/path optimization.
- Shop economics beyond simple caveats.
- Automatic relic data import.
- Scoring changes to card reward advice.

## Proposed Relic Choice V1 Packet Sequence

1. **Relic Choice Design**: document input/output shape, scoring philosophy, metadata fields, confidence rules, and stop rules.
2. **Relic Metadata Seed Expansion**: add a small reviewed seed set only when source notes are available.
3. **Relic Choice Engine Spike**: add a private Python scorer and tests against fixtures, without a public CLI command if the surface is still unsettled.
4. **Relic Choice CLI**: add a public command only after fixture behavior and output wording are stable.
5. **Exporter Contract Extension**: only after the manual relic workflow works, design an exporter relic-choice screen contract.

## Decision Needed

Before implementation code starts, choose one:

- Start with relic choice advice.
- Start with potion planning advice.
- Keep broader advice deferred and focus on exporter/toolchain work.

Until that decision is made, the safest autonomous work is limited to documentation, readiness checks, and cleanup packets that preserve existing card reward behavior.
