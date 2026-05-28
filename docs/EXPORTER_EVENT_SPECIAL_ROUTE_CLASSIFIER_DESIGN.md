# Exporter Event/Special Route Classifier Design

Status: `deck_enchant_active_proven_choose_relic_pending`

Date: 2026-05-25

## Scope

This document defines a status-only classifier for event/special choice screens observed during the installed `v0.4.7` live run. The current implementation adds C# runtime diagnostics only under `screen_type: "exporter_status"`. It now has live startup proof, active Act 2 Ancient screen proof, live `map_screen_opened` clear proof, live-loaded startup proof for choose-relic/choose-bundle overlay classifiers, active event-layout proofs, repaired live startup proof for the deck-enchant diagnostic with `screen_observation_probe: "registered"`, active deck-enchant grid proof for `deck_enchant_selection_screen_shown`, and repeated negative checks showing relic-like/potion-like event rows still use `public_event_layout_options`. Active choose-relic overlay proof is still pending; user review now identifies the multiplayer chest flow, where each player chooses a relic, as the likely source of `NChooseARelicSelection` rather than ordinary solo treasure or relic-looking event rows. It does not add scoring changes, mapping changes, empirical rows, accuracy expectations, recommendation baselines, watch mode, OCR, input automation, memory/process access, packet inspection, save/profile modification, multiplayer automation, or recommendation-ready event export.

The classifier is meant to answer one narrow question: "What kind of non-ordinary route is currently visible, and did it clear?" It is not a recommendation export.

## Repo-Local Surface Review

Reviewed on 2026-05-25 with the repo metadata probe against the local STS2 `v0.106.1` assembly. This was a static symbol review only; it did not install or run the exporter.

Commands used:

```powershell
dotnet run --project tools\sts2_metadata_probe -- "D:\Games\Steam\steamapps\common\Slay the Spire 2\data_sts2_windows_x86_64\sts2.dll" "MegaCrit.Sts2.Core.Nodes.Events.NEvent|MegaCrit.Sts2.Core.Nodes.Events.NAncient|MegaCrit.Sts2.Core.Nodes.Events.Custom.NFakeMerchant|NEventOptionButton|NEventLayout|NAncientEventLayout|NEventRoom|NMerchantRoom|NMerchantButton" --signatures --accessibility
dotnet run --project tools\sts2_metadata_probe -- "D:\Games\Steam\steamapps\common\Slay the Spire 2\data_sts2_windows_x86_64\sts2.dll" "NChooseARelicSelection|NChooseABundle|ChooseABundle|CardSelectCmd|RelicSelectCmd" --signatures --accessibility
dotnet run --project tools\sts2_metadata_probe -- "D:\Games\Steam\steamapps\common\Slay the Spire 2\data_sts2_windows_x86_64\sts2.dll" "MegaCrit.Sts2.Core.Nodes.Screens.Shops.NMerchant|MerchantInventory|MerchantEntry|MerchantRoom" --signatures --accessibility
dotnet run --project tools\sts2_metadata_probe -- "D:\Games\Steam\steamapps\common\Slay the Spire 2\data_sts2_windows_x86_64\sts2.dll" "MegaCrit.Sts2.Core.Nodes.Screens.CardSelection" --signatures --accessibility
dotnet run --project tools\sts2_metadata_probe -- "D:\Games\Steam\steamapps\common\Slay the Spire 2\data_sts2_windows_x86_64\sts2.dll" "SelfHelp|Self.Help|Book|Enchantment|Enchant" --signatures --accessibility
```

Candidate public surfaces:

| Candidate surface | Public members found | Safe status-only use | Do not use for this classifier |
| --- | --- | --- | --- |
| `MegaCrit.Sts2.Core.Nodes.Rooms.NEventRoom` | `Create(EventModel, IRunState, Boolean)`, `_ExitTree()`, `Layout`, `CustomEventNode`, `DefaultFocusedControl` | Mark an event route active/cleared and classify custom-vs-standard event room. | Event choice recommendation, selected outcome, private fields such as `_event`. |
| `MegaCrit.Sts2.Core.Nodes.Events.NEventLayout` | `SetEvent(EventModel)`, `AddOptions(IEnumerable<EventOption>)`, `ClearOptions()`, `OptionButtons`, `DisableEventOptions()`, `_ExitTree()` | Count visible event options and report `event_special_choice` while staying `exporter_status`. | Option titles, descriptions, text keys, relics, or chosen option. |
| `MegaCrit.Sts2.Core.Nodes.Events.NEventOptionButton` | `Create(EventModel, EventOption, Int32)`, `Event`, `Option`, `VoteContainer`, `_ExitTree()` | Cross-check that option buttons exist. Count only; the `Index` getter is private. | Reading `Option` content, selected option, votes, or option index as recommendation evidence. |
| `MegaCrit.Sts2.Core.Nodes.Screens.Map.NMapScreen` | `Open(Boolean)`, `Close(Boolean)`, `CleanUp()`, `Opened`, `Closed` | Clear stale event/special route diagnostics when the public map screen opens. | Map advice, path recommendation, room selection, or save/profile state. |
| `MegaCrit.Sts2.Core.Nodes.Events.Custom.NFakeMerchant` | `Initialize(EventModel)`, `_EnterTree()`, `_ExitTree()`, `CurrentScreenContext`, `Inventory`, `MerchantButton` | Classify fake-merchant/shop-like event route as status-only. | Item IDs, prices, purchase status, or shop advice. |
| `MegaCrit.Sts2.Core.Nodes.Screens.NChooseARelicSelection` | `ShowScreen(IReadOnlyList<RelicModel>)`, `_ExitTree()`, `RelicsSelected()` | Count top-level relic choices for a true choose-relic overlay, now suspected to come from multiplayer chest selection, and clear on exit. | Relic IDs/names, selected relic, multiplayer control, or relic recommendation export. |
| `MegaCrit.Sts2.Core.Nodes.Screens.CardSelection.NChooseABundleSelectionScreen` | `ShowScreen(IReadOnlyList<IReadOnlyList<CardModel>>)`, `_ExitTree()`, `CardsSelected()` | Count bundles for bundle-like event choices, if observed. | Card IDs/names inside bundles or selected bundle. |
| `MegaCrit.Sts2.Core.Nodes.Screens.CardSelection.NChooseACardSelectionScreen` | Already proven: `ShowScreen(IReadOnlyList<CardModel>, Boolean)`, `_ExitTree()` | Classify as `post_event_card_choice` only when preceded by an active event route and no active ordinary reward route. | Treating every choose-card screen as ordinary card reward. |
| `MegaCrit.Sts2.Core.Nodes.Screens.CardSelection.NDeckEnchantSelectScreen` | `ShowScreen(IReadOnlyList<CardModel>, EnchantmentModel, Int32, CardSelectorPrefs)`, `AfterOverlayShown()`, `AfterOverlayHidden()`, inherited grid behavior | Repo-local status-only runtime hook for Self-Help Book's type-filtered deck enchantment grid. Count candidate cards only from `ShowScreen`. | Card IDs/names, chosen card, enchantment ID/name, prompt text, selected outcome, card recommendation export. |
| `MegaCrit.Sts2.Core.Nodes.Screens.CardSelection.NDeckCardSelectScreen` | `Create(IReadOnlyList<CardModel>, CardSelectorPrefs)`, `AfterOverlayShown()`, `AfterOverlayHidden()` | Candidate for generic deck card selection/removal screens after separate proof. | Card IDs/names, selected card, removal advice, event recommendation export. |
| `MegaCrit.Sts2.Core.Nodes.Screens.CardSelection.NDeckUpgradeSelectScreen` and `NDeckTransformSelectScreen` | `ShowScreen(...)` methods for upgrade/transform deck choices | Candidate family members for future status-only deck-selection classification. | Upgrade/transform recommendation export or selected card identity. |
| `MegaCrit.Sts2.Core.Nodes.Rooms.NMerchantRoom` and `NMerchantInventory` | `Create(MerchantRoom, IReadOnlyList<Player>)`, `OpenInventory()`, `_ExitTree()`, `Initialize(MerchantInventory, MerchantDialogueSet)`, `Open()`, `IsOpen`, `InventoryClosed`, `GetAllSlots()` | Classify shop-like route open/closed and optionally slot count. | Item IDs, costs, purchase state, inventory recommendation, or economy advice. |

Rejected or deferred surfaces:

- `CardSelectCmd` and `RelicSelectCmd`: useful for understanding flow, but they are selection commands rather than passive public UI observation surfaces.
- `EventSynchronizer` and shared event messages: they expose voting/chosen-option flow and should not be used for a status classifier.
- `EventOption` details such as `TextKey`, `Title`, `Description`, `Relic`, `WasChosen`, or `HistoryName`: public enough to inspect, but outside the classifier because they reveal option identity or outcome.
- Merchant entries and inventory item models: public enough for item review, but this packet is route classification only and does not approve shop advice.

Implementation order:

1. Add a repo-local compile probe for event-room/layout clear-state symbols only: `NEventRoom.Create`, `NEventRoom._ExitTree`, `NEventLayout.AddOptions`, `NEventLayout.ClearOptions`, and `NEventLayout._ExitTree`. Completed on 2026-05-25.
2. Add count-only status diagnostics for event layout active/cleared state, with `route_label: null` unless a public room/event ID source is proven without private access. Completed repo-locally on 2026-05-25.
3. Add a repo-local map-open clear trigger for `NMapScreen.Open(Boolean)` after live evidence showed map return did not refresh the event route status. Completed repo-locally and installed after explicit approval on 2026-05-25. Startup proof shows the map-clear diagnostic build live-loaded with 26 verified symbols, and live map-screen proof shows `map_screen_opened` clears the status route.
4. Add overlay classifiers for `NChooseARelicSelection` and `NChooseABundleSelectionScreen`, counting only top-level options. Completed repo-locally on 2026-05-26 and live-loaded after explicit approval; active choose-bundle proof exists, while active choose-relic proof is still pending and likely needs a human-controlled multiplayer chest context.
5. Add a repo-local compile probe and status-only runtime hook for `NDeckEnchantSelectScreen.ShowScreen(...)` before any live install. Completed repo-locally on 2026-05-26; the Self-Help Book follow-up fixture proves the prior installed build did not observe that deck-enchantment grid.
6. Add shop-like open/closed classification for `NFakeMerchant`, `NMerchantRoom`, and `NMerchantInventory` only after the event classifier is fixture-backed.

## Repo-Local Compile Probe Result

Accepted on 2026-05-25:

- Added `EventSpecialRouteCompileProbe` as a dormant compile probe under `exporter_mod/DeckseerExporter`.
- Verified public event route symbols for `NEventRoom`, `NEventLayout`, `NEventOptionButton`, `EventModel`, `EventOption`, and `IRunState.CurrentRoom`.
- Added static status metadata keys for the probe so a future repo-local status build can show `event_special_route_compile_probe: "compiled_not_registered"` and `event_special_route_writes_recommendation_state: false`.

This is not a recommendation route. It does not export option IDs/names, export selected outcomes, change game files, or promote event/special screens to recommendation input.

## Repo-Local Runtime Diagnostic Result

Accepted on 2026-05-25:

- Added status-only runtime hooks for `NEventRoom.Create`, `NEventRoom._ExitTree`, `NEventLayout.AddOptions`, `NEventLayout.ClearOptions`, and `NEventLayout._ExitTree`.
- Added `diagnostics.event_special_route` to static status payloads with active state, route family, null route label, public observation source, visible option count, clear state, blocker codes, and `exports_recommendation_state: false`.
- Kept the classifier count-only. It does not read or export event option `TextKey`, title, description, relic, history name, votes, selected option, selected/skipped outcome, HP, gold, deck, relics, potions, or recommendation-ready card/relic state.
- Verified repo-local build with `ModsPath` redirected inside the workspace so the real STS2 mods folder was not modified; the build passed with 0 warnings and 0 errors.

## Live Startup Diagnostic Proof

Accepted on 2026-05-25 after explicit approval:

- Installed the status-only diagnostic build into the real STS2 `DeckseerExporter` mod folder. The installed DLL hash matched the workspace build hash, and the DLL contained the new event route diagnostic strings.
- Relaunched STS2 and captured a fresh raw `exporter_status` payload with the event route caveat present, `event_special_route_compile_probe: "compiled_not_registered"`, `event_special_route_verified_symbol_count: 25`, `screen_observation_verified_symbol_count: 25`, and `diagnostics.event_special_route.exports_recommendation_state: false`.
- Added compact fixture `tests/fixtures/exporter_status_v047_event_special_route_startup_state.json` from that captured startup payload and focused assertions proving `inspect-export` preserves the status diagnostics while `recommend-export --confirmed` rejects the status payload.

## Live Active Route Proof

Accepted on 2026-05-25 from human-navigated live evidence:

- While the user was on the Act 2 Ancient choice screen, the raw exporter payload stayed `screen_type: "exporter_status"` and reported `diagnostics.event_special_route.probe_status: "event_special_route_seen"`.
- The active route was classified as `route_family: "event_special_choice"`, `observation_source: "public_event_layout_options"`, `visible_option_count: 3`, `clear_state: "active"`, and `exports_recommendation_state: false`.
- The route blocker was `event_special_route_status_only`; no option IDs, option names, selected option, deck, HP, gold, or recommendation-ready state were exported.
- Added compact fixture `tests/fixtures/exporter_status_v047_event_special_route_ancient_active_state.json` and focused assertions proving `inspect-export` preserves the active status diagnostics while `recommend-export --confirmed` rejects the status payload.
- After the user made an Ancient choice, a second live payload remained active and status-only with `visible_option_count: 1`. This is captured in `tests/fixtures/exporter_status_v047_event_special_route_ancient_post_choice_state.json` to distinguish "post-choice but still visible" from a cleared route.
- After the user returned to the map, `latest_state.json` did not refresh; it still contained the post-choice one-option active payload. No exporter/Harmony error appeared in the latest STS2 log. Treat map return as unresolved clear-state evidence rather than a successful clear proof.

Clear-state proof after leaving an event/special choice screen is still pending. The repo-local `NMapScreen.Open(Boolean)` trigger should be live-proven before adding cleared fixtures. Do not add active or cleared route fixtures from synthetic payloads; use captured `exporter_status` payloads only.

## Repo-Local Map Clear Trigger

Accepted repo-locally on 2026-05-25:

- Reviewed public map/room-transition surfaces and selected `NMapScreen.Open(Boolean)` as the narrow clear trigger because the public map screen opening directly represents the route no longer being visible.
- Added `NMapScreen.Open(Boolean)` to the event-special compile probe and screen-observation verified symbols.
- Added a Harmony postfix that calls `RecordEventRouteCleared("map_screen_opened")`, writing only status diagnostics with `active: false`, `visible_option_count: 0`, `clear_state: "cleared"`, `exports_recommendation_state: false`, and no option identity or outcome fields.
- Verified the repo-local build with `ModsPath` redirected inside the workspace: 0 warnings and 0 errors; the real STS2 mods folder was not modified by this packet.

## Live Map-Clear Build Load Proof

Accepted on 2026-05-25 after explicit approval:

- Installed the `NMapScreen.Open(Boolean)` diagnostic build into the real STS2 `DeckseerExporter` mod folder. The installed DLL hash matched the workspace build hash, and the installed DLL contained `map_screen_opened`, `NMapScreen`, and `NMapScreenOpenPatch`.
- Relaunched STS2 and captured a fresh startup `exporter_status` payload with `event_special_route_verified_symbol_count: 26`, `screen_observation_verified_symbol_count: 26`, and `MegaCrit.Sts2.Core.Nodes.Screens.Map.NMapScreen.Open` present in both verified-symbol lists.
- The captured route remained status-only: `probe_status: "not_observed"`, `last_event: "startup"`, `active: false`, `clear_state: "cleared"`, `exports_recommendation_state: false`, and no option identity or selected-outcome fields.
- Added compact fixture `tests/fixtures/exporter_status_v047_event_special_route_map_clear_startup_state.json` and focused assertions for the live-loaded map-clear diagnostic build.

## Live Map-Clear Proof

Accepted on 2026-05-26 from a human-continued run that opened on the map:

- The captured payload stayed `screen_type: "exporter_status"` and `exporter_version: "0.4.7"`.
- `diagnostics.event_special_route.probe_status` was `"cleared"` and `last_event` was `"map_screen_opened"`.
- The route remained non-recommendation: `active: false`, `visible_option_count: 0`, `clear_state: "cleared"`, `exports_recommendation_state: false`, and no option IDs, option names, selected option, deck, HP, gold, or recommendation-ready state were exported.
- Added compact fixture `tests/fixtures/exporter_status_v047_event_special_route_map_cleared_state.json` and focused assertions for the live clear shape.

This proves the public map-open trigger clears stale event/special route diagnostics. It does not make event/special screens recommendation-ready.

## Repo-Local Overlay Classifier Result

Accepted repo-locally on 2026-05-26:

- Added `NChooseARelicSelection.ShowScreen(IReadOnlyList<RelicModel>)` and `_ExitTree()` to the event-special compile probe and screen-observation verified symbols.
- Added `NChooseABundleSelectionScreen.ShowScreen(IReadOnlyList<IReadOnlyList<CardModel>>)` and `_ExitTree()` to the event-special compile probe and screen-observation verified symbols.
- The runtime hooks count only top-level relic choices or bundles and write `event_special_route` status diagnostics with `route_family: "event_special_choice"`, `exports_recommendation_state: false`, and `event_special_route_status_only`.
- The hooks do not export relic IDs, relic names, card IDs, card names, bundle contents, selected option identity, selected outcome, costs, deck, HP, gold, or recommendation-ready state.
- Exit hooks clear the status route with `choose_relic_selection_screen_closed` or `choose_bundle_selection_screen_closed`.

## Live Overlay Classifier Build Load Proof

Accepted on 2026-05-26 after explicit approval:

- Installed the choose-relic/choose-bundle overlay classifier build into the real STS2 `DeckseerExporter` mod folder. The installed DLL hash matched the workspace build hash, and the installed DLL contained the new overlay screen classes and status event names.
- Relaunched STS2 and captured a fresh startup `exporter_status` payload with `event_special_route_verified_symbol_count: 30`, `screen_observation_verified_symbol_count: 30`, and the four overlay symbols present in the verified-symbol lists:
  - `MegaCrit.Sts2.Core.Nodes.Screens.NChooseARelicSelection.ShowScreen`
  - `MegaCrit.Sts2.Core.Nodes.Screens.NChooseARelicSelection._ExitTree`
  - `MegaCrit.Sts2.Core.Nodes.Screens.CardSelection.NChooseABundleSelectionScreen.ShowScreen`
  - `MegaCrit.Sts2.Core.Nodes.Screens.CardSelection.NChooseABundleSelectionScreen._ExitTree`
- The captured route remained status-only: `probe_status: "not_observed"`, `last_event: "startup"`, `active: false`, `clear_state: "cleared"`, `exports_recommendation_state: false`, and no option identity or selected-outcome fields.
- Added compact fixture `tests/fixtures/exporter_status_v047_event_special_route_overlay_startup_state.json` and focused assertions for the live-loaded overlay classifier build.

Live active-screen proof for `choose_relic_selection_screen_shown` is pending. Use human-navigated evidence only; do not fabricate overlay active fixtures.

Working route hypothesis as of 2026-05-28:

- The user identified STS2 multiplayer chest flow as the likely source: when a multiplayer chest opens, there is one relic per player and each player chooses a relic.
- This explains why solo treasure chests use `NTreasureRoomRelicHolder` and why relic-looking event rows have repeatedly reported `public_event_layout_options` instead of the true choose-relic overlay.
- Future proof should come from an explicitly human-controlled multiplayer context if the user chooses to run one. This note does not approve gameplay automation, multiplayer coordination tooling, real mod-folder changes, option identity export, selected relic export, or recommendation-ready relic export.

## Live Bundle Overlay Proof

Accepted on 2026-05-26 from a human-paused "Choose a Pack" screen:

- The captured payload stayed `screen_type: "exporter_status"` and did not become recommendation-ready.
- The event route snapshot reported `probe_status: "event_special_route_seen"`, `last_event: "choose_bundle_selection_screen_shown"`, `observation_source: "public_choose_bundle_selection_screen"`, `visible_option_count: 2`, `clear_state: "active"`, and `exports_recommendation_state: false`.
- No bundle card IDs, card names, bundle contents, selected bundle, selected outcome, HP, gold, deck, relics, potions, or recommendation-ready state were exported through the event route diagnostics.
- Prior reward/card diagnostics remained cleared or refused as stale, with `card_reward_live_export_candidate_writes_recommendation_state: false`.
- Added compact fixture `tests/fixtures/exporter_status_v047_event_special_route_bundle_active_state.json` and focused assertions for the active two-pack bundle overlay shape.

This proves the choose-bundle overlay hook can count top-level packs while preserving the status-only boundary.

## Live Ranwid Relic Event Proof

Accepted on 2026-05-26 from a human-paused Ranwid the Elder screen with three relic-award options:

- The captured payload stayed `screen_type: "exporter_status"` and did not become recommendation-ready.
- The event route snapshot reported `probe_status: "event_special_route_seen"`, `last_event: "event_layout_options_added"`, `observation_source: "public_event_layout_options"`, `visible_option_count: 3`, `clear_state: "active"`, and `exports_recommendation_state: false`.
- This did not use the choose-relic overlay hook; it is an event-layout route that offers relic outcomes.
- No option IDs, option names, relic IDs, relic names, selected option, selected outcome, HP, gold, deck, relics, potions, or recommendation-ready state were exported through the event route diagnostics.
- Added compact fixture `tests/fixtures/exporter_status_v047_event_special_route_ranwid_relic_active_state.json` and focused assertions for the active three-option relic-event shape.

This is evidence for event-layout relic-award choices, not proof of `NChooseARelicSelection`.

## Live Doll Room Relic-Options Event Proof

Accepted on 2026-05-26 from a human-paused Doll Room follow-up after choosing "Take Some Time":

- The captured payload stayed `screen_type: "exporter_status"` and did not become recommendation-ready.
- The event route snapshot reported `probe_status: "event_special_route_seen"`, `last_event: "event_layout_options_added"`, `observation_source: "public_event_layout_options"`, `visible_option_count: 2`, `clear_state: "active"`, and `exports_recommendation_state: false`.
- This did not use the `NChooseARelicSelection` overlay hook; the visible Doll relic choices are still represented as event-layout options in the installed build.
- No option IDs, option names, relic IDs, relic names, selected option, selected outcome, HP, gold, deck, relics, potions, or recommendation-ready state were exported through the event route diagnostics.
- Added compact fixture `tests/fixtures/exporter_status_v047_event_special_route_doll_room_relic_options_state.json` and focused assertions for the active two-option Doll relic event-layout shape.

This narrows the pending choose-relic overlay proof: Doll Room's visible relic-choice follow-up is useful event-layout relic-choice evidence, but it is not proof of `NChooseARelicSelection`.

## Live Vakuu Relic-Options Event Proof

Accepted on 2026-05-26 from a human-paused Vakuu event screen with three visible relic/consequence choices:

- The captured payload stayed `screen_type: "exporter_status"` and did not become recommendation-ready.
- The event route snapshot reported `probe_status: "event_special_route_seen"`, `last_event: "event_layout_options_added"`, `observation_source: "public_event_layout_options"`, `visible_option_count: 3`, `clear_state: "active"`, and `exports_recommendation_state: false`.
- This is another event-layout relic-choice route, not a proof of the `NChooseARelicSelection` overlay hook.
- No option IDs, option names, relic IDs, relic names, selected option, selected outcome, HP, gold, deck, relics, potions, or recommendation-ready state were exported through the event route diagnostics.
- Added compact fixture `tests/fixtures/exporter_status_v047_event_special_route_vakuu_relic_options_state.json` and focused assertions for the active three-option relic event-layout shape.

## Live Zen Weaver Event Proof

Accepted on 2026-05-26 from a human-paused Zen Weaver screen with three event-layout options:

- The captured payload stayed `screen_type: "exporter_status"` and did not become recommendation-ready.
- The event route snapshot reported `probe_status: "event_special_route_seen"`, `last_event: "event_layout_options_added"`, `observation_source: "public_event_layout_options"`, `visible_option_count: 3`, `clear_state: "active"`, and `exports_recommendation_state: false`.
- This event includes card-add and card-remove outcomes in visible text, but the diagnostic remains count-only and does not export option identity or outcome details.
- No option IDs, option names, card IDs, card names, selected option, selected outcome, costs, deck, HP, gold, relics, potions, or recommendation-ready state were exported through the event route diagnostics.
- Added compact fixture `tests/fixtures/exporter_status_v047_event_special_route_zen_weaver_active_state.json` and focused assertions for the active three-option card-editing event shape.

This strengthens ordinary event-layout route coverage. It is not proof of `NChooseARelicSelection`.

## Live Self-Help Book Event Proof

Accepted on 2026-05-26 from a human-paused Self-Help Book screen with three event-layout options:

- The captured payload stayed `screen_type: "exporter_status"` and did not become recommendation-ready.
- The event route snapshot reported `probe_status: "event_special_route_seen"`, `last_event: "event_layout_options_added"`, `observation_source: "public_event_layout_options"`, `visible_option_count: 3`, `clear_state: "active"`, and `exports_recommendation_state: false`.
- The visible options appear to lead to type-filtered card enchantment choices, so the follow-up screen may be useful post-event card-selection evidence if captured separately.
- No option IDs, option names, card IDs, card names, selected option, selected outcome, costs, deck, HP, gold, relics, potions, or recommendation-ready state were exported through the event route diagnostics.
- Added compact fixture `tests/fixtures/exporter_status_v047_event_special_route_self_help_book_active_state.json` and focused assertions for the active three-option enchantment event shape.

This strengthens event-layout route coverage and points to a potential follow-up card-selection route proof. It is not proof of `NChooseARelicSelection`.

## Live Self-Help Book Card-Select Follow-Up Evidence

Accepted on 2026-05-26 from the human-paused card-selection grid opened after choosing a Self-Help Book attack enchantment option:

- The captured payload stayed `screen_type: "exporter_status"` and did not become recommendation-ready.
- The event route snapshot reported `probe_status: "event_special_options_cleared"`, `last_event: "event_layout_options_cleared"`, `visible_option_count: 0`, `clear_state: "unknown"`, and `exports_recommendation_state: false`.
- The visually active card grid did not populate the current `NChooseACardSelectionScreen`-based status counts: `visible_card_choice_option_count` and `card_identity_review_option_count` were both 0.
- This proves the Self-Help Book follow-up uses a card-selection surface not covered by the existing ordinary reward/card-choice hooks.
- Added compact fixture `tests/fixtures/exporter_status_v047_event_special_route_self_help_book_card_select_state.json` and focused assertions for the status-only unobserved-card-grid shape.

This is a useful design gap, not a live export failure. A future packet should review the public surface for this type-filtered deck card selection before adding any runtime hook.

## Repo-Local Self-Help Book Card-Select Surface Review

Accepted repo-locally on 2026-05-26 after the Self-Help Book card-select fixture proved the installed `v0.4.7` hooks did not observe the visible deck grid.

Reviewed with the local metadata probe against the installed STS2 assembly. This packet did not install or run the exporter.

Key findings:

- The visually active follow-up grid is best matched by `MegaCrit.Sts2.Core.Nodes.Screens.CardSelection.NDeckEnchantSelectScreen`, not `NChooseACardSelectionScreen`.
- `NDeckEnchantSelectScreen` exposes public `ShowScreen(IReadOnlyList<CardModel>, EnchantmentModel, Int32, CardSelectorPrefs)`, plus public overlay lifecycle methods `AfterOverlayShown()` and `AfterOverlayHidden()`.
- The deck enchantment flow is driven by `CardSelectCmd.FromDeckForEnchantment(...)`, which is useful explanatory evidence but remains command flow, not the preferred passive observation surface.
- `CardSelectorPrefs` exposes public prompt/min/max/cancelable properties, including `EnchantSelectionPrompt`, but prompt text should remain out of the diagnostic because it can reveal option purpose beyond a count-only route classifier.
- `EnchantmentModel` exposes public ID/name/description/card properties, but those must not be exported in this classifier. At most a future status-only packet should count candidate cards and optionally report a generic route label such as `deck_enchant_card_select`.

Runtime packet result:

1. Added a repo-local status-only runtime hook that records `route_family: "post_event_card_choice"`, `route_label: "deck_enchant_card_select"`, `visible_option_count` from the `IReadOnlyList<CardModel>` count, `exports_recommendation_state: false`, and `event_special_route_status_only`.
2. The hook does not read or export candidate card IDs/names, selected card, enchantment ID/name, prompt text, HP, gold, deck, relics, potions, or recommendation-ready state.
3. Live install remains separate and requires explicit approval before modifying the real STS2 mod folder.

Do not promote this to card reward export. This is deck-state mutation selection, not an ordinary card reward.

## Repo-Local Deck Enchant Compile Probe Result

Accepted repo-locally on 2026-05-26:

- Added `NDeckEnchantSelectScreen.ShowScreen`, `NDeckEnchantSelectScreen.AfterOverlayShown`, and `NDeckEnchantSelectScreen.AfterOverlayHidden` to `EventSpecialRouteCompileProbe.VerifiedSymbolNames`.
- Added the same three symbols to `ScreenObservationProbe.VerifiedSymbolNames` so a future installed status build can prove the deck-enchant surface is visible to normal exporter source.
- Did not add a Harmony patch, runtime observer, option identity export, card identity export, selected-card export, enchantment identity export, recommendation state, or live install.
- Verified with repo-local `dotnet build` while redirecting `ModsPath` to `D:\Codex\Deckseer\.tmp_deck_enchant_compile_mods\`; build passed with 0 warnings and 0 errors, and the real STS2 mods folder was not modified.

This compile probe proves symbol availability only. It does not prove that the runtime hook will fire on the Self-Help Book grid.

## Repo-Local Deck Enchant Runtime Diagnostic Result

Accepted repo-locally on 2026-05-26:

- Added `NDeckEnchantSelectScreen.ShowScreen(...)` as a status-only route hook.
- The hook writes only `diagnostics.event_special_route` under `screen_type: "exporter_status"` with `last_event: "deck_enchant_selection_screen_shown"`, `route_family: "post_event_card_choice"`, `route_label: "deck_enchant_card_select"`, `observation_source: "public_deck_enchant_selection_screen"`, candidate count, `exports_recommendation_state: false`, and `event_special_route_status_only`.
- The hook does not export card IDs, card names, selected card, enchantment ID/name/description, prompt text, costs, deck, HP, gold, relics, potions, or recommendation-ready state.
- Verified repo-local build with `ModsPath` redirected inside the workspace; the real STS2 mods folder was not modified.

This proves the runtime hook compiles locally. Live install and registration proof are recorded below, but human-paused Self-Help Book card-grid proof is still needed before adding a live active deck-enchant fixture.

## Live Deck Enchant Diagnostic Repair

Accepted on 2026-05-26 after the first installed deck-enchant diagnostic build loaded 33 verified symbols but failed screen-observer registration.

- The failure occurred during Harmony registration with `Patching exception in method null`.
- The repair removed the live `NDeckEnchantSelectScreen.AfterOverlayHidden()` Harmony patch while keeping the compile-proven symbol listed for future review.
- The repaired runtime diagnostic keeps only the status-only `NDeckEnchantSelectScreen.ShowScreen(...)` hook, which is sufficient to prove the visible Self-Help Book card grid count.
- Clear-state proof for deck-enchant selection remains pending and should use a separately reviewed public surface.

## Live Deck Enchant Registration Proof

Accepted on 2026-05-26 after explicit approval and a repaired install into the real STS2 `DeckseerExporter` mod folder:

- Installed files hash-matched the repaired workspace build:
  - `DeckseerExporter.dll`: `8427AE4D2C9417AEF2C3E2BBDE68A29749FC9BD6D60DCC084AC08DB14E95ECD1`
  - `DeckseerExporter.pdb`: `B26808FB7852DCA188DA5D1537F48A38B32AF6FB53DC63B2DE5DA3DBB32979B1`
  - `DeckseerExporter.json`: `7FD859ECC7955BAEB91EB703A6A63A0F6AB9A01B3FCE0BA9516B6EA55FB4D60F`
- After STS2 restart, the live `exporter_status` payload reported `screen_observation_probe: "registered"` and `screen_observation_error: null`.
- The live payload reported `screen_observation_verified_symbol_count: 33`, including `NDeckEnchantSelectScreen.ShowScreen`, `NDeckEnchantSelectScreen.AfterOverlayShown`, and `NDeckEnchantSelectScreen.AfterOverlayHidden` as compile-visible symbols.
- The active screen at proof time was a Vakuu event-layout route with `visible_option_count: 3`; it proved registration health, not the deck-enchant `ShowScreen` hook firing.
- This registration proof was later superseded by the live Sapphire Seed deck-enchant grid proof below. A future Self-Help Book grid can still be useful as a second confirmation, but it is no longer the primary manual proof target.

## Live Deck Enchant Active Grid Proof

Accepted on 2026-05-26 from a human-paused Sapphire Seed `Sown` deck-enchant grid:

- The captured payload stayed `screen_type: "exporter_status"` and did not become recommendation-ready.
- The event route snapshot reported `probe_status: "event_special_route_seen"`, `last_event: "deck_enchant_selection_screen_shown"`, `route_family: "post_event_card_choice"`, `route_label: "deck_enchant_card_select"`, `observation_source: "public_deck_enchant_selection_screen"`, `visible_option_count: 19`, `clear_state: "active"`, and `exports_recommendation_state: false`.
- Ordinary card-choice and card-identity review counts remained 0, proving this is the repaired deck-enchant hook rather than the ordinary reward/card-choice route.
- No candidate card IDs, card names, enchantment ID/name, selected card, prompt text, deck, HP, gold, relics, potions, or recommendation-ready state were exported.
- Added compact fixture `tests/fixtures/exporter_status_v047_event_special_route_deck_enchant_active_state.json` and focused assertions for the active deck-enchant shape.

Clear-state proof for deck-enchant selection remains pending and should use a separately reviewed public surface.

## Live Wood Carvings Deck Enchant Confirmation

Accepted on 2026-05-27 from a human-paused Wood Carvings `Slither` deck-enchant grid:

- The first Wood Carvings option screen produced an alert as an event/special route, but it did not need a reload because the follow-up grid provided the higher-value proof.
- The captured follow-up payload stayed `screen_type: "exporter_status"` and did not become recommendation-ready.
- The event route snapshot reported `probe_status: "event_special_route_seen"`, `last_event: "deck_enchant_selection_screen_shown"`, `route_family: "post_event_card_choice"`, `route_label: "deck_enchant_card_select"`, `observation_source: "public_deck_enchant_selection_screen"`, `visible_option_count: 12`, `clear_state: "active"`, and `exports_recommendation_state: false`.
- Ordinary card-choice and card-identity review counts remained 0, proving this is the repaired deck-enchant hook rather than ordinary reward/card-choice export.
- No candidate card IDs, card names, enchantment ID/name, selected card, prompt text, deck, HP, gold, relics, potions, or recommendation-ready state were exported.
- Added compact fixture `tests/fixtures/exporter_status_v047_event_special_route_wood_carvings_deck_enchant_state.json` and focused assertions for the active 12-candidate Wood Carvings deck-enchant shape.

This is a second active deck-enchant confirmation after Sapphire Seed. It remains status-only and does not approve event/special recommendations.

## Live Event Room Closed Clear Proof

Accepted on 2026-05-27 from the current live `latest_state.json` after no active choose-relic overlay was available:

- The captured payload stayed `screen_type: "exporter_status"` and did not become recommendation-ready.
- The event route snapshot reported `probe_status: "cleared"`, `last_event: "event_room_closed"`, `active: false`, `visible_option_count: 0`, `clear_state: "cleared"`, and `exports_recommendation_state: false`.
- Ordinary card/relic reward export candidates remained refused, visible reward counts were zero, and confirmed `recommend-export` rejected the payload as `exporter_status`.
- Added compact fixture `tests/fixtures/exporter_status_v047_event_special_route_event_room_closed_state.json` and focused assertions for this event-room close clear-state shape.

This is a stale-route guard for the event/special classifier. It is not active proof for `NChooseARelicSelection`.

## Additional Live Non-Target Event-Layout Checks

Accepted as handoff evidence on 2026-05-27 from human-paused live screens inspected with the installed `v0.4.7` status diagnostics after the deck-enchant proof.

- Potion Courier reported `last_event: "event_layout_options_added"`, `observation_source: "public_event_layout_options"`, and `visible_option_count: 2`.
- Crystal Sphere reported `last_event: "event_layout_options_added"`, `observation_source: "public_event_layout_options"`, and `visible_option_count: 2`.
- Relic-looking event rows, including the puppet relic offer and the weapon-gift relic offer, reported `last_event: "event_layout_options_added"`, `observation_source: "public_event_layout_options"`, and `visible_option_count: 3`.
- These are useful negative checks for the pending relic-overlay proof: visible relic outcomes inside event rows are not enough. The desired active proof still needs `last_event: "choose_relic_selection_screen_shown"` and `observation_source: "public_choose_relic_selection_screen"`.
- Self-Help Book's option screen remained a normal three-option `public_event_layout_options` event route. A follow-up deck-enchant grid can provide optional second confirmation for `deck_enchant_selection_screen_shown`, but Sapphire Seed already fixture-backed the active deck-enchant route.

An external seed report for Darv the Hoarder exists for Regent Ascension 10 (`W5954K46C1`), but the user's mod-mode profile is currently back at Ascension 0. New user review suggests solo natural play may not produce `NChooseARelicSelection`; the most plausible future proof is a human-controlled multiplayer chest where the overlay appears naturally, with the same pause-and-inspect boundary.

## Live Loot Card Status Evidence

Accepted on 2026-05-26 from a human-paused "Loot! Add a card to your deck" screen:

- The captured payload stayed `screen_type: "exporter_status"` and did not become recommendation-ready.
- The event route snapshot reported `probe_status: "event_special_options_cleared"`, `last_event: "event_layout_options_cleared"`, `route_family: "event_special_choice"`, `visible_option_count: 0`, `clear_state: "unknown"`, and `exports_recommendation_state: false`.
- The ordinary reward observer also saw `visible_reward_probe_status: "card_reward_model_seen"`, `visible_reward_count: 2`, and `visible_card_reward_option_count: 6`, confirming this is a post-event/loot card-choice gap rather than the choose-relic or choose-bundle overlay path.
- Live export correctly refused recommendation state with `unknown_reward_card`, `unknown_deck_card`, and `unmapped_relic` blockers. Review-only IDs included reward `CLEANSE`, deck `STRIKE_IRONCLAD`/`DEFEND_IRONCLAD`, and owned relic `KALEIDOSCOPE`.
- Added compact fixture `tests/fixtures/exporter_status_v047_event_special_route_loot_card_status_state.json` and focused assertions for the status-only route shape.

This is evidence for a future post-event/loot card-choice route design. Do not promote it to live `card_reward` export without a separate design packet covering freshness, mapping, and visible-run alignment.

## Live Brain Leech Event Proof

Accepted on 2026-05-26 from a human-paused Brain Leech event screen:

- The captured payload stayed `screen_type: "exporter_status"` and did not become recommendation-ready.
- The event route snapshot reported `probe_status: "event_special_route_seen"`, `last_event: "event_layout_options_added"`, `route_family: "event_special_choice"`, `visible_option_count: 2`, `clear_state: "active"`, and `exports_recommendation_state: false`.
- No option IDs, option names, selected option, selected outcome, HP, gold, deck, relics, potions, or recommendation-ready state were exported through the event route diagnostics.
- Prior reward/card diagnostics remained cleared or refused as stale, with `card_reward_live_export_candidate_writes_recommendation_state: false`.
- Added compact fixture `tests/fixtures/exporter_status_v047_event_special_route_brain_leech_active_state.json` and focused assertions for the active two-option event route shape.
- After the user left the event and returned to the map, the captured payload reported `probe_status: "cleared"`, `last_event: "map_screen_opened"`, `active: false`, `visible_option_count: 0`, `clear_state: "cleared"`, and no event route blockers. Added `tests/fixtures/exporter_status_v047_event_special_route_brain_leech_map_cleared_state.json`.

This is a clean proof that ordinary event-choice screens can be counted as active status-only route evidence without leaking option identity or promoting recommendations.

## Observed Route Families

| Route family | Examples from live handoff | Current recommendation status |
| --- | --- | --- |
| `event_special_choice` | Pael, Tea Master, Doll relic selection, Amalgamator, Potion Courier, Crystal Sphere, relic-looking event rows | Status-only evidence; not recommendation-ready. Relic-looking event rows do not prove `NChooseARelicSelection`. |
| `shop_like_choice` | Event or shop-like relic/card/potion choices | Status-only evidence; shop economy context is outside current reward contracts. |
| `post_event_card_choice` | Card choices after event resolution | Status-only evidence until freshness and visible-reward alignment are proven. |
| `ordinary_reward_route` | Proven card/relic reward routes | Already handled by existing card/relic reward boundaries when all gates pass. |
| `unknown_choice_route` | Any public choice surface that cannot be classified safely | Status-only evidence with an explicit unknown blocker. |

## Proposed Status Shape

The classifier writes only `screen_type: "exporter_status"` and places route diagnostics under `diagnostics.event_special_route`.

Proposed shape:

```json
{
  "screen_type": "exporter_status",
  "diagnostics": {
    "event_special_route": {
      "active": true,
      "route_family": "event_special_choice",
      "route_label": "tea_master",
      "observation_source": "public_screen_route_classifier",
      "visible_option_count": 2,
      "clear_state": "active",
      "exports_recommendation_state": false,
      "blockers": ["event_special_route_status_only"]
    }
  }
}
```

Field rules:

- `active`: true only while the public event/special route surface is currently visible.
- `route_family`: one of `event_special_choice`, `shop_like_choice`, `post_event_card_choice`, `ordinary_reward_route`, or `unknown_choice_route`.
- `route_label`: optional coarse label only when the public route surface makes it clear without private access or guessing. Use `null` for uncertain surfaces. This label must not expose reward option IDs, reward option names, selected option identity, or selected/skipped outcome.
- `observation_source`: the public observation path, for example `public_screen_route_classifier`.
- `visible_option_count`: integer count only when the public UI route exposes it safely; otherwise `null`.
- `clear_state`: `active`, `cleared`, or `unknown`.
- `exports_recommendation_state`: always false for this diagnostic.
- `blockers`: include `event_special_route_status_only`; include `unknown_event_special_route` when the classifier cannot identify the family.

Clear-state payloads should either omit `diagnostics.event_special_route` or report:

```json
{
  "screen_type": "exporter_status",
  "diagnostics": {
    "event_special_route": {
      "active": false,
      "route_family": null,
      "route_label": null,
      "observation_source": "public_screen_route_classifier",
      "visible_option_count": 0,
      "clear_state": "cleared",
      "exports_recommendation_state": false,
      "blockers": []
    }
  }
}
```

## Fixture Expectations

Do not add synthetic route fixtures. Startup and active Ancient fixture coverage now exists for the live-installed status-only diagnostic. Cleared route fixtures should use captured `exporter_status` payloads from the real exporter or from repo-local exporter output only after a separately approved implementation packet exists.

Minimum future fixture set:

- `exporter_status_event_special_route_active_state.json`: event/special surface active, `screen_type` remains `exporter_status`, blocker includes `event_special_route_status_only`, and `recommend-export` rejects it.
- `exporter_status_event_special_route_cleared_state.json`: same route after close/selection/transition, active is false or diagnostics are absent, and `recommend-export` rejects it.
- `exporter_status_unknown_choice_route_state.json`: ambiguous public choice surface, family is `unknown_choice_route`, blocker includes `unknown_event_special_route`, and no option identities are exported.

Suggested assertions:

- `inspect-export` accepts the files as status diagnostics.
- `recommend-export --confirmed` rejects every event/special status fixture.
- No route fixture contains top-level card reward, relic reward, deck, relic, potion, HP, gold, selected outcome, option IDs, or option names.
- Active and cleared fixtures prove stale route diagnostics do not remain active after the visible route closes.

## Route Matrix

| Observed surface | Proposed route family | Allowed diagnostic evidence | Still blocked |
| --- | --- | --- | --- |
| Pael | `event_special_choice` | active state, coarse label if public, option count if public, status-only blocker | card/relic recommendation export, option identity reveal |
| Tea Master | `event_special_choice` | active state, `tea_master` label if public, option count if public, status-only blocker | Tea choice recommendation; `tea_of_discourtesy` remains owned-relic mapping only |
| Doll relic selection | `event_special_choice` | active state, coarse label if public, option count if public, status-only blocker | relic-choice recommendation export |
| Amalgamator | `event_special_choice` | active state, coarse label if public, option count if public, status-only blocker | event recommendation export |
| Shop-like choices | `shop_like_choice` | active state, coarse label if public, option count if public, status-only blocker | shop economy advice and reward export |
| Post-event card choices | `post_event_card_choice` | active state, option count if public, status-only blocker | card reward export until freshness and visible alignment are proven |

## Implementation Gate

Before any further C# packet:

1. Keep ADR 9 proposed or explicitly accept it.
2. Use the reviewed candidate surfaces above; add a compile probe before any runtime diagnostic.
3. Confirm the route classifier still avoids option IDs/names, item IDs/names, costs, votes, and selected outcomes.
4. Add repo-local tests for status parsing/rejection using captured payloads.
5. Ask for explicit approval before installing or modifying the real STS2 mod folder.

Promotion from this classifier to recommendation-ready event/special export is out of scope and requires a separate route-specific ADR or design note.
