using System.Collections.Generic;
using System.Linq;

namespace DeckseerExporter.DeckseerExporterCode;

internal static class RelicRewardLiveExportCandidateProbe
{
    public static RelicRewardLiveExportCandidateSnapshot FromObservation(ScreenObservationSnapshot observation)
    {
        List<string> refusalReasons = new();
        List<string> missingFields = new();

        bool normalRewardScreenActive =
            observation.ProbeStatus == "relic_reward_model_seen"
            && observation.RelicRewardOptionCount > 0
            && observation.LastEvent == "rewards_screen_shown";
        bool treasureRelicActive =
            observation.ProbeStatus == "treasure_relic_model_seen"
            && observation.RelicRewardOptionCount > 0
            && observation.LastEvent == "treasure_relic_holder_initialized";
        bool rewardScreenActive = normalRewardScreenActive || treasureRelicActive;

        if (!rewardScreenActive)
        {
            if (observation.LastEvent is "reward_collected" or "reward_skipped" or "choose_card_screen_closed" or "card_reward_selection_screen_closed" or "treasure_relic_picked" or "treasure_relic_skipped" or "treasure_relic_collection_closed"
                || observation.ProbeStatus == "reward_screen_completed")
            {
                refusalReasons.Add("stale_reward_screen");
            }
            else
            {
                refusalReasons.Add("no_visible_relic_reward");
            }
        }

        int unmappedRewardRelicCount = observation.RelicRewardIdentityReview.MappingUnknownCount;
        if (rewardScreenActive && unmappedRewardRelicCount > 0)
        {
            refusalReasons.Add("unmapped_reward_relic");
        }

        if (rewardScreenActive && observation.RelicRewardIdentityReview.DuplicateNormalizedCount > 0)
        {
            refusalReasons.Add("duplicate_reward_relic");
        }

        if (rewardScreenActive && observation.RewardCount > observation.RelicRewardCount)
        {
            refusalReasons.Add("mixed_reward_screen_state_may_change");
        }

        CardRewardRunStateRuntimeSnapshot runState = observation.CardRewardRunStateRuntime;
        bool visibleRewardAlignmentPresent = normalRewardScreenActive
            ? runState.VisibleRewardPlayerPresent
            : treasureRelicActive
                ? runState.RunStateAvailable
                : runState.VisibleRewardPlayerPresent;
        AddMissingField(missingFields, "run_in_progress", runState.RunInProgress);
        AddMissingField(missingFields, "run_state", runState.RunStateAvailable);
        AddMissingField(missingFields, "serializable_run", runState.SerializableRunAvailable);
        AddMissingField(missingFields, "single_player", runState.SinglePlayerAvailable);
        AddMissingField(missingFields, "character", runState.CharacterPresent);
        AddMissingField(missingFields, "act", runState.ActPresent);
        AddMissingField(missingFields, "floor", runState.FloorPresent);
        AddMissingField(missingFields, "ascension", runState.AscensionPresent);
        AddMissingField(missingFields, "gold", runState.GoldPresent);
        AddMissingField(missingFields, "hp", runState.HpPresent);
        AddMissingField(missingFields, "deck", runState.DeckPresent);
        AddMissingField(missingFields, "relics", runState.RelicsPresent);
        AddMissingField(missingFields, "potions", runState.PotionsPresent);
        AddMissingField(missingFields, "visible_reward_player", visibleRewardAlignmentPresent);

        if (missingFields.Count > 0)
        {
            refusalReasons.Add("missing_required_run_state_field");
        }

        int unmappedDeckCount = runState.DeckCardMappingUnknownCount;
        if (unmappedDeckCount > 0)
        {
            refusalReasons.Add("unmapped_deck_card");
        }

        RelicPotionIdentityReviewSnapshot relicPotionReview = observation.RelicPotionIdentityReview;
        int unmappedOwnedRelicCount = rewardScreenActive
            ? relicPotionReview.RelicMappingUnknownCount
            : 0;
        if (rewardScreenActive && runState.RelicCount > 0 && relicPotionReview.RelicCount == 0)
        {
            unmappedOwnedRelicCount = runState.RelicCount;
        }

        if (unmappedOwnedRelicCount > 0)
        {
            refusalReasons.Add("unmapped_owned_relic");
        }

        int unmappedPotionCount = rewardScreenActive
            ? relicPotionReview.PotionMappingUnknownCount
            : 0;
        if (rewardScreenActive && runState.PotionCount > 0 && relicPotionReview.PotionCount == 0)
        {
            unmappedPotionCount = runState.PotionCount;
        }

        if (unmappedPotionCount > 0)
        {
            refusalReasons.Add("unmapped_potion");
        }

        string[] distinctReasons = refusalReasons.Distinct().ToArray();
        string candidateStatus = distinctReasons.Length == 0 ? "ready" : "refused";

        return new RelicRewardLiveExportCandidateSnapshot(
            candidateStatus,
            distinctReasons,
            missingFields.ToArray(),
            unmappedRewardRelicCount,
            unmappedDeckCount,
            unmappedOwnedRelicCount,
            unmappedPotionCount,
            false
        );
    }

    private static void AddMissingField(List<string> missingFields, string fieldName, bool present)
    {
        if (!present)
        {
            missingFields.Add(fieldName);
        }
    }
}

internal sealed record RelicRewardLiveExportCandidateSnapshot(
    string Candidate,
    IReadOnlyList<string> RefusalReasons,
    IReadOnlyList<string> MissingFields,
    int UnmappedRewardRelicCount,
    int UnmappedDeckCount,
    int UnmappedOwnedRelicCount,
    int UnmappedPotionCount,
    bool WritesRecommendationState
);
