# ADR 10: Read-Only Export Alert CLI

## Status

Accepted

## Context

The active choose-relic overlay proof for `NChooseARelicSelection` may be rare, unused, or future-facing. Natural play should not be warped around hunting it, but if the state appears while the user is already running Deckseer, Deckseer should make it obvious enough for the user to pause and ask Codex to inspect the export.

The same applies to other pause-worthy exporter states: recommendation-ready card/relic exports, active special overlays, mapping gaps, unsupported reward shapes, and exporter diagnostic errors.

## Decision

Add a read-only `deckseer export-alert` CLI command. The command watches by default; `--once` provides the opt-out single-check path.

The command may:

- read a user-visible exporter JSON file
- run once or poll that file
- print a loud terminal alert and ring the terminal bell by default
- identify pause-worthy state from existing exported JSON diagnostics

The command must not:

- read the game screen, use OCR, or capture screenshots
- send gameplay input or automate choices
- read process memory, packets, saves, or profiles
- modify STS2 files, exporter files, saves, profiles, or Deckseer data
- recommend a choice or bypass `recommend-export --confirmed`
- install notification dependencies

## Consequences

This gives the user a practical pause signal while keeping the exporter boundary read-only/export-only and human-confirmation-first.

It is not the full Deckseer Watch Mode milestone because it does not produce recommendations, auto-confirm state, or drive gameplay. Future OS-native notifications or recommendation-watch behavior require a separate design packet if they add dependencies, background services, or broader user interaction.

## Alternatives considered

- Rely only on manual pauses: safest but likely to miss rare surfaces.
- Add OS-native toast notifications now: useful, but it adds platform behavior and possible dependency/tooling questions that are not needed for the first alert path.
- Promote event/special routes to recommendation exports: rejected; route semantics remain unproven.
