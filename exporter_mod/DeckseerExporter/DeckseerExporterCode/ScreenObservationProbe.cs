using HarmonyLib;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Multiplayer.Game;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Events;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Nodes.Screens;
using MegaCrit.Sts2.Core.Nodes.Screens.CardSelection;
using MegaCrit.Sts2.Core.Nodes.Screens.Map;
using MegaCrit.Sts2.Core.Nodes.Screens.TreasureRoomRelic;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Runs;
using System;
using System.Collections.Generic;
using System.Linq;

namespace DeckseerExporter.DeckseerExporterCode;

internal static class ScreenObservationProbe
{
    private static readonly object SyncRoot = new();
    private static string _registrationStatus = "not_registered";
    private static string _probeStatus = "not_observed";
    private static string _lastEvent = "startup";
    private static int _rewardCount;
    private static int _cardRewardCount;
    private static int _relicRewardCount;
    private static int _cardRewardOptionCount;
    private static int _relicRewardOptionCount;
    private static int _cardChoiceOptionCount;
    private static bool? _cardChoiceCanSkip;
    private static bool? _skipDisallowed;
    private static bool? _allRewardsSuccessfullySelected;
    private static CardIdentityRuntimeSnapshot _cardIdentityRuntimeSnapshot = CardIdentityRuntimeProbe.NotObserved("startup");
    private static CardIdentityReviewSnapshot _cardIdentityReviewSnapshot = CardIdentityRuntimeProbe.ReviewNotObserved("startup");
    private static CardRewardRunStateRuntimeSnapshot _cardRewardRunStateRuntimeSnapshot = CardRewardRunStateRuntimeProbe.NotObserved("startup");
    private static DeckIdentityReviewSnapshot _deckIdentityReviewSnapshot = DeckIdentityReviewProbe.NotObserved("startup");
    private static RelicPotionIdentityReviewSnapshot _relicPotionIdentityReviewSnapshot = RelicPotionIdentityReviewProbe.NotObserved("startup");
    private static RelicRewardIdentityReviewSnapshot _relicRewardIdentityReviewSnapshot = RelicRewardIdentityReviewProbe.NotObserved("startup");
    private static EventSpecialRouteSnapshot _eventSpecialRouteSnapshot = EventSpecialRouteSnapshot.NotObserved("startup");
    private static RewardsSet? _activeRewardsSet;
    private static IRunState? _activeRunState;
    private static string? _error;

    public static readonly string[] VerifiedSymbolNames =
    {
        Symbol<NRewardsScreen>(nameof(NRewardsScreen.ShowScreen)),
        Symbol<NRewardsScreen>(nameof(NRewardsScreen.RewardCollectedFrom)),
        Symbol<NRewardsScreen>(nameof(NRewardsScreen.RewardSkippedFrom)),
        Symbol<NCardRewardSelectionScreen>(nameof(NCardRewardSelectionScreen._ExitTree)),
        Symbol<NChooseACardSelectionScreen>(nameof(NChooseACardSelectionScreen.ShowScreen)),
        Symbol<NChooseACardSelectionScreen>(nameof(NChooseACardSelectionScreen._ExitTree)),
        Symbol<RewardsSet>(nameof(RewardsSet.Rewards)),
        Symbol<RewardsSet>(nameof(RewardsSet.DisallowSkipping)),
        Symbol<RewardsSet>(nameof(RewardsSet.AllRewardsSuccessfullySelected)),
        Symbol<CardReward>(nameof(CardReward.Cards)),
        Symbol<RelicReward>(nameof(RelicReward.Relic)),
        Symbol<RelicModel>(nameof(RelicModel.Id)),
        Symbol<RelicModel>(nameof(RelicModel.CanonicalInstance)),
        Symbol<RelicModel>(nameof(RelicModel.ToSerializable)),
        Symbol<NTreasureRoomRelicCollection>(nameof(NTreasureRoomRelicCollection.Initialize)),
        Symbol<NTreasureRoomRelicCollection>(nameof(NTreasureRoomRelicCollection._ExitTree)),
        Symbol<NTreasureRoomRelicHolder>(nameof(NTreasureRoomRelicHolder.Initialize)),
        Symbol<TreasureRoomRelicSynchronizer>(nameof(TreasureRoomRelicSynchronizer.PickRelicLocally)),
        Symbol<TreasureRoomRelicSynchronizer>(nameof(TreasureRoomRelicSynchronizer.SkipRelicLocally)),
        Symbol<TreasureRoomRelicSynchronizer>(nameof(TreasureRoomRelicSynchronizer.OnRoomExited)),
        Symbol<NEventRoom>(nameof(NEventRoom.Create)),
        Symbol<NEventRoom>(nameof(NEventRoom._ExitTree)),
        Symbol<NEventLayout>(nameof(NEventLayout.AddOptions)),
        Symbol<NEventLayout>(nameof(NEventLayout.ClearOptions)),
        Symbol<NEventLayout>(nameof(NEventLayout._ExitTree)),
        Symbol<NMapScreen>(nameof(NMapScreen.Open)),
        Symbol<NChooseARelicSelection>(nameof(NChooseARelicSelection.ShowScreen)),
        Symbol<NChooseARelicSelection>(nameof(NChooseARelicSelection._ExitTree)),
        Symbol<NChooseABundleSelectionScreen>(nameof(NChooseABundleSelectionScreen.ShowScreen)),
        Symbol<NChooseABundleSelectionScreen>(nameof(NChooseABundleSelectionScreen._ExitTree)),
        Symbol<NDeckEnchantSelectScreen>(nameof(NDeckEnchantSelectScreen.ShowScreen)),
        Symbol<NDeckEnchantSelectScreen>(nameof(NDeckEnchantSelectScreen.AfterOverlayShown)),
        Symbol<NDeckEnchantSelectScreen>(nameof(NDeckEnchantSelectScreen.AfterOverlayHidden))
    };

    public static void Register()
    {
        try
        {
            Harmony harmony = new($"{MainFile.ModId}.ScreenObservationProbe");
            harmony.PatchAll(typeof(ScreenObservationProbe).Assembly);
            lock (SyncRoot)
            {
                _registrationStatus = "registered";
                _error = null;
            }
        }
        catch (Exception ex)
        {
            lock (SyncRoot)
            {
                _registrationStatus = "registration_failed";
                _error = ex.Message;
            }

            MainFile.Logger.Error($"Deckseer screen observation probe failed to register: {ex.Message}");
        }
    }

    public static ScreenObservationSnapshot Snapshot()
    {
        lock (SyncRoot)
        {
            return new ScreenObservationSnapshot(
                _registrationStatus,
                _probeStatus,
                _lastEvent,
                _rewardCount,
                _cardRewardCount,
                _relicRewardCount,
                _cardRewardOptionCount,
                _relicRewardOptionCount,
                _cardChoiceOptionCount,
                _cardChoiceCanSkip,
                _skipDisallowed,
                _allRewardsSuccessfullySelected,
                _cardIdentityRuntimeSnapshot,
                _cardIdentityReviewSnapshot,
                _cardRewardRunStateRuntimeSnapshot,
                _deckIdentityReviewSnapshot,
                _relicPotionIdentityReviewSnapshot,
                _relicRewardIdentityReviewSnapshot,
                _eventSpecialRouteSnapshot,
                _error
            );
        }
    }

    public static void RecordRewardsScreenShown(RewardsSet rewardsSet, IRunState? runState)
    {
        try
        {
            int rewardCount = rewardsSet.Rewards.Count;
            CardReward[] cardRewards = rewardsSet.Rewards.OfType<CardReward>().ToArray();
            RelicReward[] relicRewards = rewardsSet.Rewards.OfType<RelicReward>().ToArray();
            CardModel[] cardChoices = cardRewards.SelectMany(reward => reward.Cards).ToArray();
            int optionCount = cardRewards.Sum(reward => reward.Cards.Count());

            lock (SyncRoot)
            {
                _probeStatus = cardRewards.Length > 0
                    ? "card_reward_model_seen"
                    : relicRewards.Length > 0
                        ? "relic_reward_model_seen"
                        : "no_reward_model";
                _lastEvent = "rewards_screen_shown";
                _rewardCount = rewardCount;
                _cardRewardCount = cardRewards.Length;
                _relicRewardCount = relicRewards.Length;
                _cardRewardOptionCount = optionCount;
                _relicRewardOptionCount = relicRewards.Length;
                _skipDisallowed = rewardsSet.DisallowSkipping;
                _allRewardsSuccessfullySelected = rewardsSet.AllRewardsSuccessfullySelected;
                _activeRewardsSet = rewardsSet;
                _activeRunState = runState;
                _cardIdentityRuntimeSnapshot = CardIdentityRuntimeProbe.FromCards(cardChoices, "rewards_screen_shown");
                _cardIdentityReviewSnapshot = CardIdentityRuntimeProbe.ReviewFromCards(cardChoices, "rewards_screen_shown");
                _cardRewardRunStateRuntimeSnapshot = CardRewardRunStateRuntimeProbe.FromRunState(runState, rewardsSet, "rewards_screen_shown");
                _deckIdentityReviewSnapshot = DeckIdentityReviewProbe.FromRunState(runState, "rewards_screen_shown");
                _relicPotionIdentityReviewSnapshot = RelicPotionIdentityReviewProbe.FromRunState(runState, "rewards_screen_shown");
                _relicRewardIdentityReviewSnapshot = RelicRewardIdentityReviewProbe.FromRewards(relicRewards, "rewards_screen_shown");
                _error = null;
            }
        }
        catch (Exception ex)
        {
            RecordProbeError(ex);
        }

        MainFile.WriteStaticStatusExport();
    }

    public static void RecordChooseCardScreenShown(IReadOnlyList<CardModel> cards, bool canSkip)
    {
        try
        {
            lock (SyncRoot)
            {
                _probeStatus = cards.Count > 0 ? "card_choice_screen_seen" : "empty_card_choice_screen";
                _lastEvent = "choose_card_screen_shown";
                _rewardCount = 0;
                _cardRewardCount = cards.Count > 0 ? 1 : 0;
                _relicRewardCount = 0;
                _cardRewardOptionCount = cards.Count;
                _relicRewardOptionCount = 0;
                _cardChoiceOptionCount = cards.Count;
                _cardChoiceCanSkip = canSkip;
                _skipDisallowed = !canSkip;
                _allRewardsSuccessfullySelected = null;
                _activeRewardsSet = null;
                _activeRunState = null;
                _cardIdentityRuntimeSnapshot = CardIdentityRuntimeProbe.FromCards(cards, "choose_card_screen_shown");
                _cardIdentityReviewSnapshot = CardIdentityRuntimeProbe.ReviewFromCards(cards, "choose_card_screen_shown");
                _cardRewardRunStateRuntimeSnapshot = CardRewardRunStateRuntimeProbe.FromRunState(null, null, "choose_card_screen_shown");
                _deckIdentityReviewSnapshot = DeckIdentityReviewProbe.NotObserved("choose_card_screen_shown");
                _relicPotionIdentityReviewSnapshot = RelicPotionIdentityReviewProbe.NotObserved("choose_card_screen_shown");
                _relicRewardIdentityReviewSnapshot = RelicRewardIdentityReviewProbe.NotObserved("choose_card_screen_shown");
                _error = null;
            }
        }
        catch (Exception ex)
        {
            RecordProbeError(ex);
        }

        MainFile.WriteStaticStatusExport();
    }

    public static void RecordTreasureRelicShown(RelicModel relic, IRunState? runState)
    {
        try
        {
            lock (SyncRoot)
            {
                _probeStatus = "treasure_relic_model_seen";
                _lastEvent = "treasure_relic_holder_initialized";
                _rewardCount = 1;
                _cardRewardCount = 0;
                _relicRewardCount = 1;
                _cardRewardOptionCount = 0;
                _relicRewardOptionCount = 1;
                _cardChoiceOptionCount = 0;
                _cardChoiceCanSkip = null;
                _skipDisallowed = false;
                _allRewardsSuccessfullySelected = null;
                _activeRewardsSet = null;
                _activeRunState = runState;
                _cardIdentityRuntimeSnapshot = CardIdentityRuntimeProbe.NotObserved("treasure_relic_holder_initialized");
                _cardIdentityReviewSnapshot = CardIdentityRuntimeProbe.ReviewNotObserved("treasure_relic_holder_initialized");
                _cardRewardRunStateRuntimeSnapshot = CardRewardRunStateRuntimeProbe.FromRunState(runState, null, "treasure_relic_holder_initialized");
                _deckIdentityReviewSnapshot = DeckIdentityReviewProbe.FromRunState(runState, "treasure_relic_holder_initialized");
                _relicPotionIdentityReviewSnapshot = RelicPotionIdentityReviewProbe.FromRunState(runState, "treasure_relic_holder_initialized");
                _relicRewardIdentityReviewSnapshot = RelicRewardIdentityReviewProbe.FromRelicModels(new[] { relic }, "treasure_relic_holder_initialized");
                _error = null;
            }
        }
        catch (Exception ex)
        {
            RecordProbeError(ex);
        }

        MainFile.WriteStaticStatusExport();
    }

    public static void RecordTreasureRelicCollectionCompleted(string eventName)
    {
        lock (SyncRoot)
        {
            if (_probeStatus == "treasure_relic_model_seen")
            {
                _probeStatus = "reward_screen_completed";
                _lastEvent = eventName;
                _rewardCount = 0;
                _cardRewardCount = 0;
                _relicRewardCount = 0;
                _cardRewardOptionCount = 0;
                _relicRewardOptionCount = 0;
                _cardChoiceOptionCount = 0;
                _cardChoiceCanSkip = null;
                _skipDisallowed = null;
                _allRewardsSuccessfullySelected = null;
                _activeRewardsSet = null;
                _activeRunState = null;
                _cardIdentityRuntimeSnapshot = CardIdentityRuntimeProbe.Cleared(eventName);
                _cardIdentityReviewSnapshot = CardIdentityRuntimeProbe.ReviewCleared(eventName);
                _cardRewardRunStateRuntimeSnapshot = CardRewardRunStateRuntimeProbe.Cleared(eventName);
                _deckIdentityReviewSnapshot = DeckIdentityReviewProbe.Cleared(eventName);
                _relicPotionIdentityReviewSnapshot = RelicPotionIdentityReviewProbe.Cleared(eventName);
                _relicRewardIdentityReviewSnapshot = RelicRewardIdentityReviewProbe.Cleared(eventName);
                _error = null;
            }
        }

        MainFile.WriteStaticStatusExport();
    }

    public static void RecordEventRoomShown()
    {
        lock (SyncRoot)
        {
            _eventSpecialRouteSnapshot = EventSpecialRouteSnapshot.RouteActive("event_room_created", null, "public_event_room");
            _error = null;
        }

        MainFile.WriteStaticStatusExport();
    }

    public static void RecordEventOptionsShown(IEnumerable<EventOption> options)
    {
        try
        {
            int optionCount = options.Count();
            lock (SyncRoot)
            {
                _eventSpecialRouteSnapshot = EventSpecialRouteSnapshot.RouteActive(
                    "event_layout_options_added",
                    optionCount,
                    "public_event_layout_options"
                );
                _error = null;
            }
        }
        catch (Exception ex)
        {
            RecordProbeError(ex);
        }

        MainFile.WriteStaticStatusExport();
    }

    public static void RecordRelicSelectionOverlayShown(IReadOnlyList<RelicModel> relics)
    {
        lock (SyncRoot)
        {
            _eventSpecialRouteSnapshot = EventSpecialRouteSnapshot.RouteActive(
                "choose_relic_selection_screen_shown",
                relics.Count,
                "public_choose_relic_selection_screen"
            );
            _error = null;
        }

        MainFile.WriteStaticStatusExport();
    }

    public static void RecordBundleSelectionOverlayShown(IReadOnlyList<IReadOnlyList<CardModel>> bundles)
    {
        lock (SyncRoot)
        {
            _eventSpecialRouteSnapshot = EventSpecialRouteSnapshot.RouteActive(
                "choose_bundle_selection_screen_shown",
                bundles.Count,
                "public_choose_bundle_selection_screen"
            );
            _error = null;
        }

        MainFile.WriteStaticStatusExport();
    }

    public static void RecordDeckEnchantSelectionScreenShown(IReadOnlyList<CardModel> cards)
    {
        lock (SyncRoot)
        {
            _eventSpecialRouteSnapshot = EventSpecialRouteSnapshot.RouteActive(
                "deck_enchant_selection_screen_shown",
                cards.Count,
                "public_deck_enchant_selection_screen",
                "post_event_card_choice",
                "deck_enchant_card_select"
            );
            _error = null;
        }

        MainFile.WriteStaticStatusExport();
    }

    public static void RecordEventOptionsCleared()
    {
        lock (SyncRoot)
        {
            _eventSpecialRouteSnapshot = EventSpecialRouteSnapshot.OptionsCleared("event_layout_options_cleared");
            _error = null;
        }

        MainFile.WriteStaticStatusExport();
    }

    public static void RecordEventRouteCleared(string eventName)
    {
        lock (SyncRoot)
        {
            _eventSpecialRouteSnapshot = EventSpecialRouteSnapshot.Cleared(eventName);
            _error = null;
        }

        MainFile.WriteStaticStatusExport();
    }

    public static void RecordRewardCollected()
    {
        lock (SyncRoot)
        {
            if (_probeStatus == "relic_reward_model_seen" && _cardRewardOptionCount == 0)
            {
                _probeStatus = "reward_screen_completed";
                _lastEvent = "reward_collected";
                _rewardCount = 0;
                _cardRewardCount = 0;
                _relicRewardCount = 0;
                _cardRewardOptionCount = 0;
                _relicRewardOptionCount = 0;
                _cardChoiceOptionCount = 0;
                _cardChoiceCanSkip = null;
                _skipDisallowed = null;
                _allRewardsSuccessfullySelected = null;
                _activeRewardsSet = null;
                _activeRunState = null;
                _cardIdentityRuntimeSnapshot = CardIdentityRuntimeProbe.Cleared("reward_collected");
                _cardIdentityReviewSnapshot = CardIdentityRuntimeProbe.ReviewCleared("reward_collected");
                _cardRewardRunStateRuntimeSnapshot = CardRewardRunStateRuntimeProbe.Cleared("reward_collected");
                _deckIdentityReviewSnapshot = DeckIdentityReviewProbe.Cleared("reward_collected");
                _relicPotionIdentityReviewSnapshot = RelicPotionIdentityReviewProbe.Cleared("reward_collected");
                _relicRewardIdentityReviewSnapshot = RelicRewardIdentityReviewProbe.Cleared("reward_collected");
                _error = null;
            }
            else
            {
                _lastEvent = "reward_collected";
                _cardRewardRunStateRuntimeSnapshot = CardRewardRunStateRuntimeProbe.FromRunState(_activeRunState, _activeRewardsSet, "reward_collected");
                if (_probeStatus == "card_reward_model_seen" && _cardRewardOptionCount > 0)
                {
                    _relicPotionIdentityReviewSnapshot = RelicPotionIdentityReviewProbe.FromCurrentSerializableRun("reward_collected");
                }
                _error = null;
            }
        }

        MainFile.WriteStaticStatusExport();
    }

    public static void RecordRewardsScreenCompleted(string eventName)
    {
        lock (SyncRoot)
        {
            _probeStatus = "reward_screen_completed";
            _lastEvent = eventName;
            _rewardCount = 0;
            _cardRewardCount = 0;
            _relicRewardCount = 0;
            _cardRewardOptionCount = 0;
            _relicRewardOptionCount = 0;
            _cardChoiceOptionCount = 0;
            _cardChoiceCanSkip = null;
            _skipDisallowed = null;
            _allRewardsSuccessfullySelected = null;
            _activeRewardsSet = null;
            _activeRunState = null;
            _cardIdentityRuntimeSnapshot = CardIdentityRuntimeProbe.Cleared(eventName);
            _cardIdentityReviewSnapshot = CardIdentityRuntimeProbe.ReviewCleared(eventName);
            _cardRewardRunStateRuntimeSnapshot = CardRewardRunStateRuntimeProbe.Cleared(eventName);
            _deckIdentityReviewSnapshot = DeckIdentityReviewProbe.Cleared(eventName);
            _relicPotionIdentityReviewSnapshot = RelicPotionIdentityReviewProbe.Cleared(eventName);
            _relicRewardIdentityReviewSnapshot = RelicRewardIdentityReviewProbe.Cleared(eventName);
            _error = null;
        }

        MainFile.WriteStaticStatusExport();
    }

    private static void RecordProbeError(Exception ex)
    {
        lock (SyncRoot)
        {
            _probeStatus = "probe_error";
            _lastEvent = "error";
            _cardIdentityRuntimeSnapshot = new CardIdentityRuntimeSnapshot("probe_error", "error", 0, 0, 0, 0, 0, 0, 0, 0, ex.GetType().Name);
            _cardIdentityReviewSnapshot = new CardIdentityReviewSnapshot("probe_error", "error", 0, Array.Empty<CardIdentityReviewItem>(), ex.GetType().Name);
            _cardRewardRunStateRuntimeSnapshot = CardRewardRunStateRuntimeProbe.NotObserved("error") with { ProbeStatus = "probe_error", Error = ex.GetType().Name };
            _deckIdentityReviewSnapshot = new DeckIdentityReviewSnapshot("probe_error", "error", 0, 0, 0, 0, Array.Empty<DeckIdentityReviewItem>(), ex.GetType().Name);
            _relicPotionIdentityReviewSnapshot = new RelicPotionIdentityReviewSnapshot(
                "probe_error",
                "error",
                0,
                0,
                0,
                0,
                0,
                0,
                Array.Empty<RelicPotionIdentityReviewItem>(),
                Array.Empty<RelicPotionIdentityReviewItem>(),
                ex.GetType().Name
            );
            _relicRewardIdentityReviewSnapshot = new RelicRewardIdentityReviewSnapshot(
                "probe_error",
                "error",
                0,
                0,
                0,
                0,
                Array.Empty<RelicRewardIdentityReviewItem>(),
                ex.GetType().Name
            );
            _eventSpecialRouteSnapshot = EventSpecialRouteSnapshot.ProbeError("error", ex.GetType().Name);
            _error = ex.Message;
        }
    }

    private static string Symbol<T>(string memberName)
    {
        return $"{typeof(T).FullName}.{memberName}";
    }
}

internal sealed record ScreenObservationSnapshot(
    string RegistrationStatus,
    string ProbeStatus,
    string LastEvent,
    int RewardCount,
    int CardRewardCount,
    int RelicRewardCount,
    int CardRewardOptionCount,
    int RelicRewardOptionCount,
    int CardChoiceOptionCount,
    bool? CardChoiceCanSkip,
    bool? SkipDisallowed,
    bool? AllRewardsSuccessfullySelected,
    CardIdentityRuntimeSnapshot CardIdentityRuntime,
    CardIdentityReviewSnapshot CardIdentityReview,
    CardRewardRunStateRuntimeSnapshot CardRewardRunStateRuntime,
    DeckIdentityReviewSnapshot DeckIdentityReview,
    RelicPotionIdentityReviewSnapshot RelicPotionIdentityReview,
    RelicRewardIdentityReviewSnapshot RelicRewardIdentityReview,
    EventSpecialRouteSnapshot EventSpecialRoute,
    string? Error
);

internal sealed record EventSpecialRouteSnapshot(
    string ProbeStatus,
    string LastEvent,
    bool Active,
    string? RouteFamily,
    string? RouteLabel,
    string ObservationSource,
    int? VisibleOptionCount,
    string ClearState,
    bool WritesRecommendationState,
    string[] Blockers,
    string? Error
)
{
    public static EventSpecialRouteSnapshot NotObserved(string lastEvent)
    {
        return new EventSpecialRouteSnapshot(
            "not_observed",
            lastEvent,
            false,
            null,
            null,
            "public_event_route_classifier",
            0,
            "cleared",
            false,
            Array.Empty<string>(),
            null
        );
    }

    public static EventSpecialRouteSnapshot RouteActive(
        string lastEvent,
        int? visibleOptionCount,
        string observationSource,
        string routeFamily = "event_special_choice",
        string? routeLabel = null
    )
    {
        return new EventSpecialRouteSnapshot(
            "event_special_route_seen",
            lastEvent,
            true,
            routeFamily,
            routeLabel,
            observationSource,
            visibleOptionCount,
            "active",
            false,
            new[] { "event_special_route_status_only" },
            null
        );
    }

    public static EventSpecialRouteSnapshot OptionsCleared(string lastEvent)
    {
        return new EventSpecialRouteSnapshot(
            "event_special_options_cleared",
            lastEvent,
            true,
            "event_special_choice",
            null,
            "public_event_layout_options",
            0,
            "unknown",
            false,
            new[] { "event_special_route_status_only" },
            null
        );
    }

    public static EventSpecialRouteSnapshot Cleared(string lastEvent)
    {
        return new EventSpecialRouteSnapshot(
            "cleared",
            lastEvent,
            false,
            null,
            null,
            "public_event_route_classifier",
            0,
            "cleared",
            false,
            Array.Empty<string>(),
            null
        );
    }

    public static EventSpecialRouteSnapshot ProbeError(string lastEvent, string error)
    {
        return new EventSpecialRouteSnapshot(
            "probe_error",
            lastEvent,
            false,
            null,
            null,
            "public_event_route_classifier",
            null,
            "unknown",
            false,
            new[] { "event_special_route_status_only" },
            error
        );
    }
}

[HarmonyPatch(typeof(NRewardsScreen), nameof(NRewardsScreen.ShowScreen))]
internal static class NRewardsScreenShowScreenPatch
{
    private static void Postfix(RewardsSet __0, IRunState __2)
    {
        ScreenObservationProbe.RecordRewardsScreenShown(__0, __2);
    }
}

[HarmonyPatch(typeof(NRewardsScreen), nameof(NRewardsScreen.RewardSkippedFrom))]
internal static class NRewardsScreenRewardSkippedPatch
{
    private static void Postfix()
    {
        ScreenObservationProbe.RecordRewardsScreenCompleted("reward_skipped");
    }
}

[HarmonyPatch(typeof(NRewardsScreen), nameof(NRewardsScreen.RewardCollectedFrom))]
internal static class NRewardsScreenRewardCollectedPatch
{
    private static void Postfix()
    {
        ScreenObservationProbe.RecordRewardCollected();
    }
}

[HarmonyPatch(typeof(NChooseACardSelectionScreen), nameof(NChooseACardSelectionScreen.ShowScreen))]
internal static class NChooseACardSelectionScreenShowScreenPatch
{
    private static void Postfix(IReadOnlyList<CardModel> __0, bool __1)
    {
        ScreenObservationProbe.RecordChooseCardScreenShown(__0, __1);
    }
}

[HarmonyPatch(typeof(NChooseACardSelectionScreen), nameof(NChooseACardSelectionScreen._ExitTree))]
internal static class NChooseACardSelectionScreenExitTreePatch
{
    private static void Postfix()
    {
        ScreenObservationProbe.RecordRewardsScreenCompleted("choose_card_screen_closed");
    }
}

[HarmonyPatch(typeof(NCardRewardSelectionScreen), nameof(NCardRewardSelectionScreen._ExitTree))]
internal static class NCardRewardSelectionScreenExitTreePatch
{
    private static void Postfix()
    {
        ScreenObservationProbe.RecordRewardsScreenCompleted("card_reward_selection_screen_closed");
    }
}

[HarmonyPatch(typeof(NTreasureRoomRelicHolder), nameof(NTreasureRoomRelicHolder.Initialize))]
internal static class NTreasureRoomRelicHolderInitializePatch
{
    private static void Postfix(RelicModel __0, IRunState __1)
    {
        ScreenObservationProbe.RecordTreasureRelicShown(__0, __1);
    }
}

[HarmonyPatch(typeof(TreasureRoomRelicSynchronizer), nameof(TreasureRoomRelicSynchronizer.PickRelicLocally))]
internal static class TreasureRoomRelicSynchronizerPickRelicLocallyPatch
{
    private static void Postfix()
    {
        ScreenObservationProbe.RecordTreasureRelicCollectionCompleted("treasure_relic_picked");
    }
}

[HarmonyPatch(typeof(TreasureRoomRelicSynchronizer), nameof(TreasureRoomRelicSynchronizer.SkipRelicLocally))]
internal static class TreasureRoomRelicSynchronizerSkipRelicLocallyPatch
{
    private static void Postfix()
    {
        ScreenObservationProbe.RecordTreasureRelicCollectionCompleted("treasure_relic_skipped");
    }
}

[HarmonyPatch(typeof(TreasureRoomRelicSynchronizer), nameof(TreasureRoomRelicSynchronizer.OnRoomExited))]
internal static class TreasureRoomRelicSynchronizerOnRoomExitedPatch
{
    private static void Postfix()
    {
        ScreenObservationProbe.RecordTreasureRelicCollectionCompleted("treasure_relic_collection_closed");
    }
}

[HarmonyPatch(typeof(NTreasureRoomRelicCollection), nameof(NTreasureRoomRelicCollection._ExitTree))]
internal static class NTreasureRoomRelicCollectionExitTreePatch
{
    private static void Postfix()
    {
        ScreenObservationProbe.RecordTreasureRelicCollectionCompleted("treasure_relic_collection_closed");
    }
}

[HarmonyPatch(typeof(NEventRoom), nameof(NEventRoom.Create))]
internal static class NEventRoomCreatePatch
{
    private static void Postfix()
    {
        ScreenObservationProbe.RecordEventRoomShown();
    }
}

[HarmonyPatch(typeof(NEventRoom), nameof(NEventRoom._ExitTree))]
internal static class NEventRoomExitTreePatch
{
    private static void Postfix()
    {
        ScreenObservationProbe.RecordEventRouteCleared("event_room_closed");
    }
}

[HarmonyPatch(typeof(NEventLayout), nameof(NEventLayout.AddOptions))]
internal static class NEventLayoutAddOptionsPatch
{
    private static void Postfix(IEnumerable<EventOption> __0)
    {
        ScreenObservationProbe.RecordEventOptionsShown(__0);
    }
}

[HarmonyPatch(typeof(NEventLayout), nameof(NEventLayout.ClearOptions))]
internal static class NEventLayoutClearOptionsPatch
{
    private static void Postfix()
    {
        ScreenObservationProbe.RecordEventOptionsCleared();
    }
}

[HarmonyPatch(typeof(NEventLayout), nameof(NEventLayout._ExitTree))]
internal static class NEventLayoutExitTreePatch
{
    private static void Postfix()
    {
        ScreenObservationProbe.RecordEventRouteCleared("event_layout_closed");
    }
}

[HarmonyPatch(typeof(NMapScreen), nameof(NMapScreen.Open))]
internal static class NMapScreenOpenPatch
{
    private static void Postfix()
    {
        ScreenObservationProbe.RecordEventRouteCleared("map_screen_opened");
    }
}

[HarmonyPatch(typeof(NChooseARelicSelection), nameof(NChooseARelicSelection.ShowScreen))]
internal static class NChooseARelicSelectionShowScreenPatch
{
    private static void Postfix(IReadOnlyList<RelicModel> __0)
    {
        ScreenObservationProbe.RecordRelicSelectionOverlayShown(__0);
    }
}

[HarmonyPatch(typeof(NChooseARelicSelection), nameof(NChooseARelicSelection._ExitTree))]
internal static class NChooseARelicSelectionExitTreePatch
{
    private static void Postfix()
    {
        ScreenObservationProbe.RecordEventRouteCleared("choose_relic_selection_screen_closed");
    }
}

[HarmonyPatch(typeof(NChooseABundleSelectionScreen), nameof(NChooseABundleSelectionScreen.ShowScreen))]
internal static class NChooseABundleSelectionScreenShowScreenPatch
{
    private static void Postfix(IReadOnlyList<IReadOnlyList<CardModel>> __0)
    {
        ScreenObservationProbe.RecordBundleSelectionOverlayShown(__0);
    }
}

[HarmonyPatch(typeof(NChooseABundleSelectionScreen), nameof(NChooseABundleSelectionScreen._ExitTree))]
internal static class NChooseABundleSelectionScreenExitTreePatch
{
    private static void Postfix()
    {
        ScreenObservationProbe.RecordEventRouteCleared("choose_bundle_selection_screen_closed");
    }
}

[HarmonyPatch(typeof(NDeckEnchantSelectScreen), nameof(NDeckEnchantSelectScreen.ShowScreen))]
internal static class NDeckEnchantSelectScreenShowScreenPatch
{
    private static void Postfix(IReadOnlyList<CardModel> __0)
    {
        ScreenObservationProbe.RecordDeckEnchantSelectionScreenShown(__0);
    }
}
