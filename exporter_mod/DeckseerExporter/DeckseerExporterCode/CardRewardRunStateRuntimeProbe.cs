using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.Saves.Runs;
using System;
using System.Collections.Generic;
using System.Linq;

namespace DeckseerExporter.DeckseerExporterCode;

internal static class CardRewardRunStateRuntimeProbe
{
    public static CardRewardRunStateRuntimeSnapshot NotObserved(string lastEvent)
    {
        return new CardRewardRunStateRuntimeSnapshot(
            "not_observed",
            lastEvent,
            false,
            false,
            false,
            0,
            false,
            false,
            false,
            false,
            false,
            false,
            false,
            false,
            false,
            false,
            0,
            0,
            0,
            0,
            0,
            0,
            false,
            false,
            null
        );
    }

    public static CardRewardRunStateRuntimeSnapshot Cleared(string lastEvent)
    {
        CardRewardRunStateRuntimeSnapshot snapshot = NotObserved(lastEvent);
        return snapshot with { ProbeStatus = "cleared" };
    }

    public static CardRewardRunStateRuntimeSnapshot FromRunState(IRunState? runState, RewardsSet? rewardsSet, string lastEvent)
    {
        try
        {
            bool runInProgress = RunManager.Instance is not null && RunManager.Instance.IsInProgress;
            bool runStateAvailable = runState is not null;
            bool serializableRunAvailable = false;
            int playerCount = 0;
            bool singlePlayerAvailable = false;
            bool characterPresent = false;
            bool actPresent = false;
            bool floorPresent = false;
            bool ascensionPresent = false;
            bool goldPresent = false;
            bool hpPresent = false;
            bool deckPresent = false;
            bool relicsPresent = false;
            bool potionsPresent = false;
            int deckCardCount = 0;
            int deckCardIdReadCount = 0;
            int deckCardMappingKnownCount = 0;
            int deckCardMappingUnknownCount = 0;
            int relicCount = 0;
            int potionCount = 0;
            bool visibleRewardPlayerPresent = false;

            SerializableRun? serializableRun = null;
            if (RunManager.Instance is not null)
            {
                serializableRun = RunManager.Instance.ToSave(null);
            }

            if (serializableRun is not null)
            {
                serializableRunAvailable = true;
                playerCount = serializableRun.Players.Count;
                singlePlayerAvailable = playerCount == 1;

                if (singlePlayerAvailable)
                {
                    SerializablePlayer player = serializableRun.Players[0];
                    characterPresent = player.CharacterId is not null;
                    actPresent = serializableRun.CurrentActIndex >= 0;
                    floorPresent = serializableRun.FloorReached >= 0;
                    ascensionPresent = serializableRun.Ascension >= 0;
                    goldPresent = player.Gold >= 0;
                    hpPresent = player.CurrentHp >= 0 && player.MaxHp > 0;
                    deckPresent = player.Deck is not null;
                    relicsPresent = player.Relics is not null;
                    potionsPresent = player.Potions is not null;

                    deckCardCount = player.Deck?.Count ?? 0;
                    if (player.Deck is not null)
                    {
                        foreach (SerializableCard card in player.Deck)
                        {
                            if (card.Id is null)
                            {
                                deckCardMappingUnknownCount++;
                                continue;
                            }

                            deckCardIdReadCount++;
                            string? normalizedId = CardIdentityRuntimeProbe.NormalizePublicIdString(card.Id.Entry);
                            if (CardIdentityRuntimeProbe.IsKnownDeckseerCardId(normalizedId))
                            {
                                deckCardMappingKnownCount++;
                            }
                            else
                            {
                                deckCardMappingUnknownCount++;
                            }
                        }
                    }

                    relicCount = player.Relics?.Count ?? 0;
                    potionCount = player.Potions?.Count ?? 0;
                    visibleRewardPlayerPresent = rewardsSet?.Player is not null;
                }
            }

            bool serializableStateComplete =
                runInProgress
                && serializableRunAvailable
                && singlePlayerAvailable
                && characterPresent
                && actPresent
                && floorPresent
                && ascensionPresent
                && goldPresent
                && hpPresent
                && deckPresent
                && relicsPresent
                && potionsPresent
                && deckCardMappingUnknownCount == 0;

            bool complete = serializableStateComplete && runStateAvailable;
            string status = complete ? "run_state_seen" : "incomplete";
            if (!complete && serializableStateComplete)
            {
                status = "serializable_run_seen";
            }

            return new CardRewardRunStateRuntimeSnapshot(
                status,
                lastEvent,
                runInProgress,
                runStateAvailable,
                serializableRunAvailable,
                playerCount,
                singlePlayerAvailable,
                characterPresent,
                actPresent,
                floorPresent,
                ascensionPresent,
                goldPresent,
                hpPresent,
                deckPresent,
                relicsPresent,
                potionsPresent,
                deckCardCount,
                deckCardIdReadCount,
                deckCardMappingKnownCount,
                deckCardMappingUnknownCount,
                relicCount,
                potionCount,
                visibleRewardPlayerPresent,
                false,
                null
            );
        }
        catch (Exception ex)
        {
            return NotObserved(lastEvent) with { ProbeStatus = "probe_error", Error = ex.GetType().Name };
        }
    }
}

internal sealed record CardRewardRunStateRuntimeSnapshot(
    string ProbeStatus,
    string LastEvent,
    bool RunInProgress,
    bool RunStateAvailable,
    bool SerializableRunAvailable,
    int PlayerCount,
    bool SinglePlayerAvailable,
    bool CharacterPresent,
    bool ActPresent,
    bool FloorPresent,
    bool AscensionPresent,
    bool GoldPresent,
    bool HpPresent,
    bool DeckPresent,
    bool RelicsPresent,
    bool PotionsPresent,
    int DeckCardCount,
    int DeckCardIdReadCount,
    int DeckCardMappingKnownCount,
    int DeckCardMappingUnknownCount,
    int RelicCount,
    int PotionCount,
    bool VisibleRewardPlayerPresent,
    bool WritesRecommendationState,
    string? Error
);
