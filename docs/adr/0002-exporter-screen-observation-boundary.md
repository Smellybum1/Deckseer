# ADR 2: Decide Exporter Screen Observation Boundary

Status: accepted

Date: 2026-05-24

## Context

The card reward exporter path is blocked before any live `card_reward` export. Repo-only metadata and compile probes proved that `RewardsSet.Rewards` and `CardReward.Cards` are public enough to compile, and that a custom hook listener can be created through the engine-owned `SingletonModel` plus `ModelDb` path.

The remaining problem is visibility proof: Deckseer must prove that an observed reward model corresponds to the reward screen the player can see. The obvious active reward stack is not public enough from normal mod source. Run hooks are pre-generation or post-selection. Reward commands generate or offer rewards, so they are not passive diagnostics.

The closest precise source is public screen code:

- `NRewardsScreen.ShowScreen(RewardsSet, Boolean, IRunState)` receives the visible reward set.
- `NRewardButton.Reward` exposes a public getter after UI reward buttons exist.

Observing those public screen surfaces would require a method-observation technique such as a tiny Harmony postfix or equivalent screen-method hook. The current strict boundary says no patching-only access paths, so this cannot proceed without an explicit decision.

## Decision

Approve public screen observation for count-only diagnostics.

Deckseer may add a tiny public-method observation probe for `NRewardsScreen.ShowScreen(RewardsSet, Boolean, IRunState)` and related public reward-screen completion methods. This approval is limited to a status-only diagnostic and does not approve live card reward export.

The first approved probe must remain status-only:

- write only `screen_type: "exporter_status"`
- export no card IDs, card names, deck, HP, gold, relics, potions, save/profile data, or recommendation-ready run state
- record only count/caveat metadata, such as whether a card reward was seen and the visible option count
- avoid private-field reflection, publicizer workarounds, memory/process tricks, packet inspection, OCR, screenshot reading, input automation, and save/profile modification
- require explicit approval before installing into the real STS2 mods folder

Acceptance for the first live test would be:

- non-reward screens report no active card reward
- a visible card reward screen reports count-only diagnostics matching the visible option count
- leaving, selecting, or skipping the reward clears or changes the diagnostic
- `inspect-export` still validates the file as `exporter_status`

## Consequences

Approving public screen observation unblocks the safest known count-only visibility proof, but expands the exporter boundary to include method observation of public UI code.

This ADR approves repo-local implementation and build verification. It does not approve installing the diagnostic into the real STS2 mods folder; that remains a separate explicit approval gate.

## Links

- `docs/CONTEXT.md`
- `docs/EXPORTER_CARD_REWARD_VISIBILITY_DESIGN.md`
- `docs/EXPORTER_CARD_REWARD_COMPILE_PROBE.md`
- `docs/adr/0001-preserve-human-confirmed-exporter-boundary.md`
