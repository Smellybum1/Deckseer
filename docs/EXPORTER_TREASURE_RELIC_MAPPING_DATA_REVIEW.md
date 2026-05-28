# Deckseer Exporter Treasure Relic Mapping Data Review

Status: `v0.4.6_mapping_live_proof_passed`

Prepared on 2026-05-25 after installed `v0.4.5` safely refused a treasure relic export because `ACCURACY` and `HEART_OF_IRON` were unmapped.

## Scope

This packet adds minimal reviewed mapping/data coverage for the observed treasure proof gaps:

- `accuracy`
- `heart_of_iron`

It also updates the repo-local exporter status-diagnostic mapping snapshot.

It does not approve:

- card or potion scoring logic changes
- empirical rows
- accuracy or relic accuracy baseline changes
- recommendation API changes
- broader live proof claims beyond the observed v0.4.6 treasure run
- watch mode, OCR, input automation, memory/process tricks, packet inspection, or save/profile modification

## Reviewed Evidence

Live exporter evidence:

- installed `v0.4.5` observed `ACCURACY` -> `accuracy` as one unknown deck mapping.
- installed `v0.4.5` observed two `HEART_OF_IRON` -> `heart_of_iron` unknown potion mappings.
- the exporter stayed `screen_type: "exporter_status"` and confirmed `recommend-export` rejected the file.

Local installed STS2 `v0.106.1` evidence:

- `release_info.json` reports `version: "v0.106.1"` and commit `d3584805`.
- `SlayTheSpire2.pck` contains English localization for `ACCURACY.title`: `Accuracy`.
- `SlayTheSpire2.pck` contains English localization for `ACCURACY.description`, describing Shivs dealing additional damage.
- `SlayTheSpire2.pck` contains English localization for `HEART_OF_IRON.title`: `Heart of Iron`.
- `SlayTheSpire2.pck` contains English localization for `HEART_OF_IRON.description`, describing gaining Plating.

## Decision

Add a minimal Silent card record:

- `accuracy`: 1-cost uncommon Silent power, Shiv damage scaling tags and roles, neutral seed prior.

Add a minimal potion record:

- `heart_of_iron`: block/plating potion tags.

These are mapping and simplified-planning seeds. They do not model exact numeric values, potion target rules, timing, combat simulation, or potion advice.

## Exporter Mapping Impact

Repo-local `v0.4.6` adds:

- `accuracy` to the card status-diagnostic mapping snapshot.
- `heart_of_iron` to the potion status-diagnostic mapping snapshot.

Fixture coverage:

- `tests/fixtures/exporter_relic_reward_live_v046_treasure_mapped_state.json` includes the previously observed `accuracy` deck card and two `heart_of_iron` potions, inspects as `screen_type: "relic_reward"`, requires confirmation, and scores through Relic Choice V1 after `--confirmed`.
- `tests/fixtures/exporter_status_v046_treasure_relic_picked_state.json` captures the post-pickup downgrade side of the same installed proof: it remains `exporter_status`, clears visible identity diagnostics, and rejects confirmed recommendation.

## Verification

Packet verification:

- `data-health`: `PASS`.
- `inspect-export tests/fixtures/exporter_relic_reward_live_v046_treasure_mapped_state.json`: valid.
- confirmed `recommend-export tests/fixtures/exporter_relic_reward_live_v046_treasure_mapped_state.json --confirmed --format text`: scores `letter_opener`.
- `dotnet build exporter_mod\DeckseerExporter\DeckseerExporter.csproj`: 0 warnings / 0 errors.
- Build verification copied `v0.4.6` package files to the configured STS2 mods folder.
- Focused pytest for models, data summary, exporter state, and mapping snapshot: 107 passed.
- `accuracy-report --format text`: `PASS`, 9/9.
- `relic-accuracy-report --format text`: `PASS`, 6/6.
- triage-aware `qa`: `PASS`.
- full pytest: 389 passed.
- `git diff --check`: passed with CRLF warnings only.

Installed `v0.4.6` live verification:

- startup fallback wrote valid `exporter_status` with `exporter_version: "0.4.6"`.
- visible treasure wrote `screen_type: "relic_reward"` with `requires_user_confirmation: true`.
- live mapped state included `accuracy`, `colorless_potion`, two `heart_of_iron` potions, and `letter_opener`.
- unconfirmed `recommend-export` rejected the visible file until human confirmation.
- confirmed `recommend-export` scored `letter_opener`.
- after pickup, the file downgraded to `exporter_status`, visible identities cleared, and confirmed `recommend-export` rejected it.

## Next Gate

Future treasure edge cases should be handled as separate narrow packets with the same confirmation and clear-state checks.
