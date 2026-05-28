# ADR 4: Human-Confirmed Live Card Reward Export

Status: accepted

Date: 2026-05-24

## Context

Installed exporter `v0.2.9` proves the public visible reward route can expose exact card identities for the active card reward screen. The proof stayed under `screen_type: "exporter_status"`, mapped `CLOAK_AND_DAGGER`, `BOUNCING_FLASK`, and `INFINITE_BLADES` to reviewed Deckseer IDs, and cleared the review list after the reward screen was skipped.

Deckseer already has a confirmed `screen_type: "card_reward"` importer and `recommend-export --confirmed` flow for fixture JSON. Moving the live exporter from diagnostics to recommendation-ready card reward state is the next major boundary change because it would export live run state fields, not only visible reward metadata.

## Decision

Allow a future implementation packet to add a narrow live `screen_type: "card_reward"` exporter mode only when all of these constraints hold:

- The active card reward is observed through the already-approved public visible-screen routes.
- The reward choices come from the visible public `CardModel.Id` values, normalized through the reviewed mapping snapshot.
- The export includes the existing Deckseer card reward schema fields needed by `recommend-export`.
- `export_metadata.requires_user_confirmation` is always `true`.
- `recommend-export` continues to require the user to run `inspect-export`, compare the visible game state, and rerun with `--confirmed`.
- The exporter remains read-only/export-only and writes a local JSON file only.
- The exporter clears or downgrades away from `screen_type: "card_reward"` when the reward screen closes.

The first live implementation should be installed only after a repo-local build and fixture test pass. Live proof must first verify `inspect-export` output, then verify `recommend-export` rejects the file without `--confirmed`, and only then run a confirmed recommendation after the user has reviewed the visible state.

Implementation note, 2026-05-25: installed `v0.3.9` extends the accepted boundary to mixed reward screens only after the installed `v0.3.8` proof showed post-pickup `reward_collected` diagnostics with run state, visible reward player context, serializable run data, mapped relics, and mapped potions all aligned. Mixed reward export remains blocked before `reward_collected`, and exported `card_reward` files still require user confirmation.

Follow-up note, 2026-05-25: installed `v0.3.10` fixes the first stale-file failure found under this ADR. The mixed reward card-choice route closes through public `NCardRewardSelectionScreen._ExitTree()`, so the exporter now downgrades to `screen_type: "exporter_status"` with cleared diagnostics after card reward selection closes. The closed-screen file is intentionally not recommendation-ready, and `recommend-export --confirmed` rejects it.

## Consequences

This enables the first low-friction live recommendation input, but it expands the exported data surface from visible card identities to run-state fields such as character, floor, HP, deck, relics, potions, and gold.

The human-confirmation gate becomes more important, not less. Exported state can be stale, incomplete, or wrong if the game route changes, the player leaves the screen, or public run-state serialization omits fields Deckseer expects.

The first implementation may need conservative caveats and may need to refuse export if any required run-state field cannot be read without private access or guessing.

## Alternatives Considered

- Keep `v0.2.9` as the final exporter state and require manual JSON entry: safest, but leaves the exporter path unable to reduce transcription.
- Export visible card IDs only as `card_reward` without deck/HP/run context: lower data surface, but incompatible with the current recommendation model and likely to produce misleading advice.
- Use save/profile files as a fallback for missing run state: rejected for this packet because the exporter boundary should remain live public API/read-only export, not save/profile import.
- Add watch mode around the latest export file: rejected; human confirmation stays explicit and command-driven.

## Links

- `docs/EXPORTER_CARD_REWARD_LIVE_EXPORT_DESIGN.md`
- `docs/EXPORTER_CARD_REWARD_ID_REVEAL_CONTRACT.md`
- `docs/EXPORTER_CARD_REWARD_MAPPING_REVIEW.md`
- `docs/EXECUTION_LOOP.md`
