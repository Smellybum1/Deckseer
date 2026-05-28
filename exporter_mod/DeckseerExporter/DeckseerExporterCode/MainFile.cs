using Godot;
using MegaCrit.Sts2.Core.Modding;
using System;
using System.IO;
using System.Linq;
using System.Text.Json;

namespace DeckseerExporter.DeckseerExporterCode;

[ModInitializer(nameof(Initialize))]
public partial class MainFile : Node
{
    public const string ModId = "DeckseerExporter";
    private const string ExporterVersion = "0.4.7";

    public static MegaCrit.Sts2.Core.Logging.Logger Logger { get; } = new(ModId, MegaCrit.Sts2.Core.Logging.LogType.Generic);

    public static void Initialize()
    {
        ScreenObservationProbe.Register();
        WriteStaticStatusExport();
    }

    internal static void WriteStaticStatusExport()
    {
        try
        {
            ScreenObservationSnapshot screenObservation = ScreenObservationProbe.Snapshot();
            string exportDirectory = Path.Combine(
                System.Environment.GetFolderPath(System.Environment.SpecialFolder.LocalApplicationData),
                "Deckseer",
                "exports"
            );
            Directory.CreateDirectory(exportDirectory);

            string exportPath = Path.Combine(exportDirectory, "latest_state.json");
            string tempPath = Path.Combine(exportDirectory, "latest_state.tmp");
            CardRewardLiveExportCandidateSnapshot liveExportCandidate =
                CardRewardLiveExportCandidateProbe.FromObservation(screenObservation);
            RelicRewardLiveExportCandidateSnapshot relicRewardLiveExportCandidate =
                RelicRewardLiveExportCandidateProbe.FromObservation(screenObservation);
            object exportPayload =
                CardRewardLiveExportBuilder.TryBuildPayload(screenObservation, liveExportCandidate, ExporterVersion)
                ?? RelicRewardLiveExportBuilder.TryBuildPayload(screenObservation, relicRewardLiveExportCandidate, ExporterVersion)
                ?? new
                {
                    game = "slay_the_spire_2",
                    screen_type = "exporter_status",
                    status = "ok",
                    export_metadata = new
                    {
                        source = "deckseer_exporter_mod",
                        exporter_version = ExporterVersion,
                        game_build = (string?)null,
                        game_patch = (string?)null,
                        exported_at = DateTimeOffset.UtcNow.ToString("O"),
                        requires_user_confirmation = false,
                        confidence = "high",
                        caveats = new[]
                        {
                            "Exporter status diagnostics only; no live run state is present.",
                            "Game patch/build metadata is not exported in this diagnostic spike.",
                            "Card identity review diagnostics may include public model IDs for visible reward choices, but no recommendation-ready run state is exported.",
                            "Live card_reward export is available only when every validation gate passes; this status payload is not recommendation-ready.",
                            "Runtime run-state readiness diagnostics report booleans and counts only; no live run-state values are exported.",
                            "Deck identity review diagnostics may include public model IDs for deck cards, but no recommendation-ready run state is exported.",
                            "Relic and potion identity review diagnostics may include public model IDs for current relics and potions, but no recommendation-ready run state is exported.",
                            "Live relic_reward export is available only when every validation gate passes; this status payload is not recommendation-ready.",
                            "Event/special route diagnostics report active or cleared state and option counts only; no option IDs, option names, selected outcomes, or recommendation-ready state are exported."
                        },
                        diagnostics = new
                        {
                            card_reward_api_probe = CardRewardApiProbe.Status,
                            verified_symbol_count = CardRewardApiProbe.VerifiedSymbolNames.Length,
                            verified_symbols = CardRewardApiProbe.VerifiedSymbolNames,
                            event_special_route_compile_probe = EventSpecialRouteCompileProbe.Status,
                            event_special_route_verified_symbol_count = EventSpecialRouteCompileProbe.VerifiedSymbolNames.Length,
                            event_special_route_verified_symbols = EventSpecialRouteCompileProbe.VerifiedSymbolNames,
                            event_special_route_writes_recommendation_state = false,
                            event_special_route = new
                            {
                                probe_status = screenObservation.EventSpecialRoute.ProbeStatus,
                                last_event = screenObservation.EventSpecialRoute.LastEvent,
                                active = screenObservation.EventSpecialRoute.Active,
                                route_family = screenObservation.EventSpecialRoute.RouteFamily,
                                route_label = screenObservation.EventSpecialRoute.RouteLabel,
                                observation_source = screenObservation.EventSpecialRoute.ObservationSource,
                                visible_option_count = screenObservation.EventSpecialRoute.VisibleOptionCount,
                                clear_state = screenObservation.EventSpecialRoute.ClearState,
                                exports_recommendation_state = screenObservation.EventSpecialRoute.WritesRecommendationState,
                                blockers = screenObservation.EventSpecialRoute.Blockers,
                                error = screenObservation.EventSpecialRoute.Error
                            },
                            hook_model_compile_probe = HookModelCompileProbe.Status,
                            hook_model_verified_symbol_count = HookModelCompileProbe.VerifiedSymbolNames.Length,
                            hook_model_verified_symbols = HookModelCompileProbe.VerifiedSymbolNames,
                            card_reward_live_export_probe = CardRewardRunStateCompileProbe.Status,
                            card_reward_live_export_required_field_count = CardRewardRunStateCompileProbe.RequiredFieldNames.Length,
                            card_reward_live_export_required_fields = CardRewardRunStateCompileProbe.RequiredFieldNames,
                            card_reward_live_export_verified_symbol_count = CardRewardRunStateCompileProbe.VerifiedSymbolNames.Length,
                            card_reward_live_export_verified_symbols = CardRewardRunStateCompileProbe.VerifiedSymbolNames,
                            card_reward_live_export_writes_recommendation_state = false,
                            card_reward_live_export_candidate = liveExportCandidate.Candidate,
                            card_reward_live_export_refusal_reasons = liveExportCandidate.RefusalReasons,
                            card_reward_live_export_missing_fields = liveExportCandidate.MissingFields,
                            card_reward_live_export_unmapped_reward_count = liveExportCandidate.UnmappedRewardCount,
                            card_reward_live_export_unmapped_deck_count = liveExportCandidate.UnmappedDeckCount,
                            card_reward_live_export_unmapped_relic_count = liveExportCandidate.UnmappedRelicCount,
                            card_reward_live_export_unmapped_potion_count = liveExportCandidate.UnmappedPotionCount,
                            card_reward_live_export_mixed_reward_freshness_status = liveExportCandidate.MixedRewardFreshnessStatus,
                            card_reward_live_export_mixed_reward_freshness_blockers = liveExportCandidate.MixedRewardFreshnessBlockers,
                            card_reward_live_export_mixed_reward_freshness_writes_recommendation_state = false,
                            card_reward_live_export_candidate_writes_recommendation_state = liveExportCandidate.WritesRecommendationState,
                            relic_reward_live_export_candidate = relicRewardLiveExportCandidate.Candidate,
                            relic_reward_live_export_refusal_reasons = relicRewardLiveExportCandidate.RefusalReasons,
                            relic_reward_live_export_missing_fields = relicRewardLiveExportCandidate.MissingFields,
                            relic_reward_live_export_unmapped_reward_relic_count = relicRewardLiveExportCandidate.UnmappedRewardRelicCount,
                            relic_reward_live_export_unmapped_deck_count = relicRewardLiveExportCandidate.UnmappedDeckCount,
                            relic_reward_live_export_unmapped_owned_relic_count = relicRewardLiveExportCandidate.UnmappedOwnedRelicCount,
                            relic_reward_live_export_unmapped_potion_count = relicRewardLiveExportCandidate.UnmappedPotionCount,
                            relic_reward_live_export_candidate_writes_recommendation_state = relicRewardLiveExportCandidate.WritesRecommendationState,
                            card_reward_run_state_runtime_probe = screenObservation.CardRewardRunStateRuntime.ProbeStatus,
                            card_reward_run_state_runtime_last_event = screenObservation.CardRewardRunStateRuntime.LastEvent,
                            card_reward_run_state_run_in_progress = screenObservation.CardRewardRunStateRuntime.RunInProgress,
                            card_reward_run_state_available = screenObservation.CardRewardRunStateRuntime.RunStateAvailable,
                            card_reward_run_state_serializable_run_available = screenObservation.CardRewardRunStateRuntime.SerializableRunAvailable,
                            card_reward_run_state_player_count = screenObservation.CardRewardRunStateRuntime.PlayerCount,
                            card_reward_run_state_single_player_available = screenObservation.CardRewardRunStateRuntime.SinglePlayerAvailable,
                            card_reward_run_state_character_present = screenObservation.CardRewardRunStateRuntime.CharacterPresent,
                            card_reward_run_state_act_present = screenObservation.CardRewardRunStateRuntime.ActPresent,
                            card_reward_run_state_floor_present = screenObservation.CardRewardRunStateRuntime.FloorPresent,
                            card_reward_run_state_ascension_present = screenObservation.CardRewardRunStateRuntime.AscensionPresent,
                            card_reward_run_state_gold_present = screenObservation.CardRewardRunStateRuntime.GoldPresent,
                            card_reward_run_state_hp_present = screenObservation.CardRewardRunStateRuntime.HpPresent,
                            card_reward_run_state_deck_present = screenObservation.CardRewardRunStateRuntime.DeckPresent,
                            card_reward_run_state_relics_present = screenObservation.CardRewardRunStateRuntime.RelicsPresent,
                            card_reward_run_state_potions_present = screenObservation.CardRewardRunStateRuntime.PotionsPresent,
                            card_reward_run_state_deck_card_count = screenObservation.CardRewardRunStateRuntime.DeckCardCount,
                            card_reward_run_state_deck_card_id_read_count = screenObservation.CardRewardRunStateRuntime.DeckCardIdReadCount,
                            card_reward_run_state_deck_card_mapping_known_count = screenObservation.CardRewardRunStateRuntime.DeckCardMappingKnownCount,
                            card_reward_run_state_deck_card_mapping_unknown_count = screenObservation.CardRewardRunStateRuntime.DeckCardMappingUnknownCount,
                            card_reward_run_state_relic_count = screenObservation.CardRewardRunStateRuntime.RelicCount,
                            card_reward_run_state_potion_count = screenObservation.CardRewardRunStateRuntime.PotionCount,
                            card_reward_run_state_visible_reward_player_present = screenObservation.CardRewardRunStateRuntime.VisibleRewardPlayerPresent,
                            card_reward_run_state_writes_recommendation_state = screenObservation.CardRewardRunStateRuntime.WritesRecommendationState,
                            card_reward_run_state_error = screenObservation.CardRewardRunStateRuntime.Error,
                            deck_identity_review_probe = screenObservation.DeckIdentityReview.ProbeStatus,
                            deck_identity_review_last_event = screenObservation.DeckIdentityReview.LastEvent,
                            deck_identity_review_card_count = screenObservation.DeckIdentityReview.CardCount,
                            deck_identity_review_unique_card_count = screenObservation.DeckIdentityReview.UniqueCardCount,
                            deck_identity_review_mapping_known_count = screenObservation.DeckIdentityReview.MappingKnownCount,
                            deck_identity_review_mapping_unknown_count = screenObservation.DeckIdentityReview.MappingUnknownCount,
                            deck_identity_review_items = screenObservation.DeckIdentityReview.Items.Select(
                                item => new
                                {
                                    position = item.Position,
                                    public_model_id = item.PublicModelId,
                                    normalized_candidate_id = item.NormalizedCandidateId,
                                    deckseer_mapping_status = item.MappingStatus,
                                    deckseer_id = item.DeckseerId,
                                    upgraded = item.Upgraded,
                                    upgrade_level = item.UpgradeLevel
                                }
                            ).ToArray(),
                            deck_identity_review_error = screenObservation.DeckIdentityReview.Error,
                            relic_potion_identity_review_probe = screenObservation.RelicPotionIdentityReview.ProbeStatus,
                            relic_potion_identity_review_last_event = screenObservation.RelicPotionIdentityReview.LastEvent,
                            relic_identity_review_count = screenObservation.RelicPotionIdentityReview.RelicCount,
                            relic_identity_review_mapping_known_count = screenObservation.RelicPotionIdentityReview.RelicMappingKnownCount,
                            relic_identity_review_mapping_unknown_count = screenObservation.RelicPotionIdentityReview.RelicMappingUnknownCount,
                            relic_identity_review_items = screenObservation.RelicPotionIdentityReview.RelicItems.Select(
                                item => new
                                {
                                    position = item.Position,
                                    public_model_id = item.PublicModelId,
                                    normalized_candidate_id = item.NormalizedCandidateId,
                                    deckseer_mapping_status = item.MappingStatus,
                                    deckseer_id = item.DeckseerId
                                }
                            ).ToArray(),
                            potion_identity_review_count = screenObservation.RelicPotionIdentityReview.PotionCount,
                            potion_identity_review_mapping_known_count = screenObservation.RelicPotionIdentityReview.PotionMappingKnownCount,
                            potion_identity_review_mapping_unknown_count = screenObservation.RelicPotionIdentityReview.PotionMappingUnknownCount,
                            potion_identity_review_items = screenObservation.RelicPotionIdentityReview.PotionItems.Select(
                                item => new
                                {
                                    position = item.Position,
                                    public_model_id = item.PublicModelId,
                                    normalized_candidate_id = item.NormalizedCandidateId,
                                    deckseer_mapping_status = item.MappingStatus,
                                    deckseer_id = item.DeckseerId
                                }
                            ).ToArray(),
                            relic_potion_identity_review_error = screenObservation.RelicPotionIdentityReview.Error,
                            card_identity_mapping_probe = CardIdentityCompileProbe.Status,
                            card_identity_mapping_verified_symbol_count = CardIdentityCompileProbe.VerifiedSymbolNames.Length,
                            card_identity_mapping_verified_symbols = CardIdentityCompileProbe.VerifiedSymbolNames,
                            screen_observation_probe = screenObservation.RegistrationStatus,
                            screen_observation_verified_symbol_count = ScreenObservationProbe.VerifiedSymbolNames.Length,
                            screen_observation_verified_symbols = ScreenObservationProbe.VerifiedSymbolNames,
                            visible_reward_probe_status = screenObservation.ProbeStatus,
                            visible_reward_probe_last_event = screenObservation.LastEvent,
                            visible_reward_count = screenObservation.RewardCount,
                            visible_card_reward_count = screenObservation.CardRewardCount,
                            visible_relic_reward_count = screenObservation.RelicRewardCount,
                            visible_card_reward_option_count = screenObservation.CardRewardOptionCount,
                            visible_relic_reward_option_count = screenObservation.RelicRewardOptionCount,
                            visible_card_choice_option_count = screenObservation.CardChoiceOptionCount,
                            visible_card_choice_can_skip = screenObservation.CardChoiceCanSkip,
                            visible_reward_skip_disallowed = screenObservation.SkipDisallowed,
                            visible_reward_all_selected = screenObservation.AllRewardsSuccessfullySelected,
                            card_identity_runtime_probe = screenObservation.CardIdentityRuntime.ProbeStatus,
                            card_identity_runtime_last_event = screenObservation.CardIdentityRuntime.LastEvent,
                            visible_card_identity_read_count = screenObservation.CardIdentityRuntime.ReadCount,
                            visible_card_identity_direct_id_count = screenObservation.CardIdentityRuntime.DirectIdCount,
                            visible_card_identity_serialized_id_count = screenObservation.CardIdentityRuntime.SerializedIdCount,
                            visible_card_identity_nullable_serialized_id_count = screenObservation.CardIdentityRuntime.NullableSerializedIdCount,
                            visible_card_identity_upgraded_count = screenObservation.CardIdentityRuntime.UpgradedCount,
                            visible_card_identity_mapping_known_count = screenObservation.CardIdentityRuntime.MappingKnownCount,
                            visible_card_identity_mapping_unknown_count = screenObservation.CardIdentityRuntime.MappingUnknownCount,
                            visible_card_identity_duplicate_normalized_count = screenObservation.CardIdentityRuntime.DuplicateNormalizedCount,
                            visible_card_identity_error = screenObservation.CardIdentityRuntime.Error,
                            card_identity_review_probe = screenObservation.CardIdentityReview.ProbeStatus,
                            card_identity_review_last_event = screenObservation.CardIdentityReview.LastEvent,
                            card_identity_review_option_count = screenObservation.CardIdentityReview.OptionCount,
                            card_identity_review_items = screenObservation.CardIdentityReview.Items.Select(
                                item => new
                                {
                                    position = item.Position,
                                    public_model_id = item.PublicModelId,
                                    normalized_candidate_id = item.NormalizedCandidateId,
                                    deckseer_mapping_status = item.MappingStatus,
                                    deckseer_id = item.DeckseerId,
                                    upgraded = item.Upgraded,
                                    upgrade_level = item.UpgradeLevel,
                                    serialized_id_matches_direct_id = item.SerializedIdMatchesDirectId
                                }
                            ).ToArray(),
                            card_identity_review_error = screenObservation.CardIdentityReview.Error,
                            relic_reward_identity_review_probe = screenObservation.RelicRewardIdentityReview.ProbeStatus,
                            relic_reward_identity_review_last_event = screenObservation.RelicRewardIdentityReview.LastEvent,
                            relic_reward_identity_review_option_count = screenObservation.RelicRewardIdentityReview.OptionCount,
                            relic_reward_identity_review_mapping_known_count = screenObservation.RelicRewardIdentityReview.MappingKnownCount,
                            relic_reward_identity_review_mapping_unknown_count = screenObservation.RelicRewardIdentityReview.MappingUnknownCount,
                            relic_reward_identity_review_duplicate_normalized_count = screenObservation.RelicRewardIdentityReview.DuplicateNormalizedCount,
                            relic_reward_identity_review_items = screenObservation.RelicRewardIdentityReview.Items.Select(
                                item => new
                                {
                                    position = item.Position,
                                    public_model_id = item.PublicModelId,
                                    normalized_candidate_id = item.NormalizedCandidateId,
                                    deckseer_mapping_status = item.MappingStatus,
                                    deckseer_id = item.DeckseerId
                                }
                            ).ToArray(),
                            relic_reward_identity_review_error = screenObservation.RelicRewardIdentityReview.Error,
                            screen_observation_error = screenObservation.Error
                        }
                    }
                };
            string payload = JsonSerializer.Serialize(
                exportPayload,
                new JsonSerializerOptions { WriteIndented = true }
            );

            File.WriteAllText(tempPath, payload);
            File.Move(tempPath, exportPath, overwrite: true);
        }
        catch (Exception ex)
        {
            GD.PrintErr($"DeckseerExporter failed to write static status export: {ex.Message}");
        }
    }
}
