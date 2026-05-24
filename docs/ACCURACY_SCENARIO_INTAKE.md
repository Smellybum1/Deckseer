# Deckseer Accuracy Scenario Intake

This checklist is for turning reviewed real-run card reward decisions into Deckseer accuracy scenarios. It is intentionally manual and conservative: scenario intake should improve calibration evidence without changing scoring, card priors, empirical rows, recommendation APIs, or baselines by itself.

## Goal

Accuracy scenarios should capture a specific visible card reward decision where a reviewer can explain the expected top pick from the run state. The scenario then becomes a regression guard for Deckseer's deterministic advisor.

Use this intake when:

- The run state is from a real run or a reviewed, realistic reconstruction.
- The visible reward choices, deck, HP, act, floor, and context are known.
- The expected pick can be justified from run needs, not only from generic card strength.
- The scenario adds coverage that is not already represented by the accepted manifest.

Do not use this intake when:

- The state is guessed from memory without enough deck/reward context.
- The expected pick depends on hidden information Deckseer cannot know.
- The goal is to force a desired scoring change before reviewing the recommendation.
- The scenario would require changing scoring, priors, card metadata, or baselines in the same packet.

## Evidence Checklist

Capture these fields before adding a scenario fixture:

- Source: save file path, exporter JSON, screenshot notes, or manually reviewed run description.
- Character, act, floor, ascension, HP, gold, deck, relics, potions, and visible reward choices.
- Run context that matters to the pick, such as region, next nodes, upcoming elites, boss, recent damage, path pressure, or shop/fire availability.
- Expected top choice and why it should beat the alternatives.
- Reasoning keywords that should appear in Deckseer's explanation.
- Review status and reviewer notes.
- Any caveats, especially missing deck-card metadata or uncertainty about path context.

## Scenario Review Steps

1. Create a manual run-state JSON fixture under `tests/fixtures/scenarios/`.
2. Run `deckseer check-run-data <fixture>` and resolve reward-card metadata gaps before scoring.
3. Run `deckseer recommend-card <fixture> --format text --include-diagnosis`.
4. Decide whether the current recommendation matches reviewed strategy for that state.
5. If it matches, add an accepted entry to `data/accuracy/scenarios.json`.
6. If it does not match, keep the scenario proposed or out of the accepted manifest until the scoring/data issue is reviewed in a separate packet.
7. Run `deckseer accuracy-report --format text`.
8. Run `deckseer qa --check-recommendation-baseline --check-accuracy --check-empirical-triage`.
9. Run `pytest`.

## Manifest Entry Template

Use stable, descriptive IDs that name the class and the decision pressure.

```json
{
  "id": "class_short_decision_pressure",
  "scenario_path": "tests/fixtures/scenarios/class_short_decision_pressure.json",
  "expected_top_choice": "card_id_or_skip",
  "expected_reasoning_keywords": [
    "frontload",
    "defense"
  ],
  "review_status": "accepted",
  "review_notes": "Reviewed real-run state. Explain why the expected pick is preferred over each alternative."
}
```

## Fixture Review Template

Use the existing manual card reward input shape. Keep only visible or reviewed state.

```json
{
  "game": "slay_the_spire_2",
  "character": "ironclad",
  "act": 1,
  "floor": 7,
  "ascension": 0,
  "gold": 0,
  "hp": {
    "current": 50,
    "max": 80
  },
  "deck": [
    {
      "id": "strike",
      "upgraded": false,
      "count": 4
    }
  ],
  "relics": [],
  "potions": [],
  "card_reward": [
    "pommel_strike",
    "shrug_it_off",
    "anger"
  ],
  "run_context": {
    "act_region": "underdocks",
    "next_nodes": [
      "combat",
      "fire",
      "elite"
    ],
    "upcoming_elites": [
      "skulking_colony",
      "terror_eel"
    ],
    "path_pressure": "elite_soon",
    "notes": [
      "Reviewed context only; do not include hidden or speculative state."
    ]
  }
}
```

## Acceptance Rules

- Accepted scenarios must pass `accuracy-report`.
- Proposed scenarios may be kept outside the manifest until reviewed.
- Do not update an accepted expected top choice just to make a report pass; first explain why the new choice is strategically better.
- Do not change scoring and add an accepted scenario in the same packet unless the task explicitly asks for that calibration change.
- Keep fixture names, manifest IDs, and review notes specific enough that future drift is understandable.

## Useful Commands

```bash
deckseer check-run-data tests/fixtures/scenarios/example.json
deckseer recommend-card tests/fixtures/scenarios/example.json --format text --include-diagnosis
deckseer accuracy-report --format text
deckseer qa --check-recommendation-baseline --check-accuracy --check-empirical-triage
pytest
```
