using System.Collections.Generic;
using System.Linq;

namespace DeckseerExporter.DeckseerExporterCode;

internal static class CardRewardLiveExportCandidateProbe
{
    public static CardRewardLiveExportCandidateSnapshot FromObservation(ScreenObservationSnapshot observation)
    {
        List<string> refusalReasons = new();
        List<string> missingFields = new();

        bool rewardScreenActive =
            observation.ProbeStatus == "card_reward_model_seen"
            && observation.CardRewardOptionCount > 0
            && observation.LastEvent is "rewards_screen_shown" or "reward_collected";

        if (!rewardScreenActive)
        {
            if (observation.LastEvent is "reward_skipped" or "choose_card_screen_closed" || observation.ProbeStatus == "reward_screen_completed")
            {
                refusalReasons.Add("stale_reward_screen");
            }
            else
            {
                refusalReasons.Add("no_visible_reward");
            }
        }

        int unmappedRewardCount =
            observation.CardIdentityRuntime.MappingUnknownCount
            + observation.CardIdentityRuntime.DuplicateNormalizedCount;
        if (rewardScreenActive && unmappedRewardCount > 0)
        {
            refusalReasons.Add("unknown_reward_card");
        }

        if (rewardScreenActive && observation.CardIdentityRuntime.UpgradedCount > 0)
        {
            refusalReasons.Add("unsupported_upgraded_reward_card");
        }

        CardRewardRunStateRuntimeSnapshot runState = observation.CardRewardRunStateRuntime;
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
        AddMissingField(missingFields, "visible_reward_player", runState.VisibleRewardPlayerPresent);

        if (missingFields.Count > 0)
        {
            refusalReasons.Add("missing_required_run_state_field");
        }

        int unmappedDeckCount = runState.DeckCardMappingUnknownCount;
        if (unmappedDeckCount > 0)
        {
            refusalReasons.Add("unknown_deck_card");
        }

        RelicPotionIdentityReviewSnapshot relicPotionReview = observation.RelicPotionIdentityReview;
        int unmappedRelicCount = rewardScreenActive
            ? relicPotionReview.RelicMappingUnknownCount
            : 0;
        if (rewardScreenActive && runState.RelicCount > 0 && relicPotionReview.RelicCount == 0)
        {
            unmappedRelicCount = runState.RelicCount;
        }

        if (unmappedRelicCount > 0)
        {
            refusalReasons.Add("unmapped_relic");
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

        MixedRewardFreshnessSnapshot mixedRewardFreshness =
            AssessMixedRewardFreshness(observation, rewardScreenActive, unmappedPotionCount);
        if (rewardScreenActive && observation.RewardCount > observation.CardRewardCount && mixedRewardFreshness.Blockers.Count > 0)
        {
            refusalReasons.Add("mixed_reward_screen_state_may_change");
        }

        string[] distinctReasons = refusalReasons.Distinct().ToArray();
        string candidateStatus = distinctReasons.Length == 0 ? "ready" : "refused";

        return new CardRewardLiveExportCandidateSnapshot(
            candidateStatus,
            distinctReasons,
            missingFields.ToArray(),
            unmappedRewardCount,
            unmappedDeckCount,
            unmappedRelicCount,
            unmappedPotionCount,
            mixedRewardFreshness.Status,
            mixedRewardFreshness.Blockers,
            false
        );
    }

    private static MixedRewardFreshnessSnapshot AssessMixedRewardFreshness(
        ScreenObservationSnapshot observation,
        bool rewardScreenActive,
        int unmappedPotionCount
    )
    {
        if (!rewardScreenActive || observation.RewardCount <= observation.CardRewardCount)
        {
            return new MixedRewardFreshnessSnapshot("not_applicable", System.Array.Empty<string>());
        }

        List<string> blockers = new();
        if (observation.LastEvent != "reward_collected")
        {
            blockers.Add("reward_collection_not_observed");
            return new MixedRewardFreshnessSnapshot("awaiting_reward_collected", blockers.ToArray());
        }

        CardRewardRunStateRuntimeSnapshot runState = observation.CardRewardRunStateRuntime;
        if (!runState.SerializableRunAvailable)
        {
            blockers.Add("serializable_run_not_available");
        }

        if (!runState.RunStateAvailable)
        {
            blockers.Add("run_state_not_aligned");
        }

        if (!runState.VisibleRewardPlayerPresent)
        {
            blockers.Add("visible_reward_player_not_aligned");
        }

        if (!runState.GoldPresent || !runState.HpPresent || !runState.DeckPresent || !runState.RelicsPresent || !runState.PotionsPresent)
        {
            blockers.Add("serializable_required_counts_incomplete");
        }

        if (unmappedPotionCount > 0)
        {
            blockers.Add("potion_identity_not_mapped_after_refresh");
        }

        string status = runState.SerializableRunAvailable
            ? "reward_collected_serializable_counts_seen"
            : "reward_collected_incomplete";
        return new MixedRewardFreshnessSnapshot(status, blockers.Distinct().ToArray());
    }

    private static void AddMissingField(List<string> missingFields, string fieldName, bool present)
    {
        if (!present)
        {
            missingFields.Add(fieldName);
        }
    }
}

internal sealed record CardRewardLiveExportCandidateSnapshot(
    string Candidate,
    IReadOnlyList<string> RefusalReasons,
    IReadOnlyList<string> MissingFields,
    int UnmappedRewardCount,
    int UnmappedDeckCount,
    int UnmappedRelicCount,
    int UnmappedPotionCount,
    string MixedRewardFreshnessStatus,
    IReadOnlyList<string> MixedRewardFreshnessBlockers,
    bool WritesRecommendationState
);

internal sealed record MixedRewardFreshnessSnapshot(
    string Status,
    IReadOnlyList<string> Blockers
);
