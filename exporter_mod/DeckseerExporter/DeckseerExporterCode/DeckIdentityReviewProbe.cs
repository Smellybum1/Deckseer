using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.Saves.Runs;
using System;
using System.Collections.Generic;

namespace DeckseerExporter.DeckseerExporterCode;

internal static class DeckIdentityReviewProbe
{
    public static DeckIdentityReviewSnapshot NotObserved(string lastEvent)
    {
        return new DeckIdentityReviewSnapshot("not_observed", lastEvent, 0, 0, 0, 0, Array.Empty<DeckIdentityReviewItem>(), null);
    }

    public static DeckIdentityReviewSnapshot Cleared(string lastEvent)
    {
        return new DeckIdentityReviewSnapshot("cleared", lastEvent, 0, 0, 0, 0, Array.Empty<DeckIdentityReviewItem>(), null);
    }

    public static DeckIdentityReviewSnapshot FromRunState(IRunState? runState, string lastEvent)
    {
        try
        {
            if (runState is null || RunManager.Instance is null || !RunManager.Instance.IsInProgress)
            {
                return NotObserved(lastEvent);
            }

            SerializableRun? serializableRun = RunManager.Instance.ToSave(null);
            if (serializableRun is null || serializableRun.Players.Count != 1)
            {
                return NotObserved(lastEvent);
            }

            IReadOnlyList<SerializableCard>? deck = serializableRun.Players[0].Deck;
            if (deck is null)
            {
                return NotObserved(lastEvent);
            }

            List<DeckIdentityReviewItem> items = new();
            HashSet<string> uniqueNormalizedIds = new(StringComparer.Ordinal);
            int knownCount = 0;
            int unknownCount = 0;

            for (int index = 0; index < deck.Count; index++)
            {
                SerializableCard card = deck[index];
                string? publicModelId = card.Id?.Entry;
                string? normalizedCandidateId = publicModelId is null
                    ? null
                    : CardIdentityRuntimeProbe.NormalizePublicIdString(publicModelId);
                string mappingStatus = "invalid";
                string? deckseerId = null;

                if (normalizedCandidateId is not null)
                {
                    uniqueNormalizedIds.Add(normalizedCandidateId);
                    if (CardIdentityRuntimeProbe.ResolveDeckseerCardId(normalizedCandidateId) is string resolvedDeckseerId)
                    {
                        mappingStatus = "known";
                        deckseerId = resolvedDeckseerId;
                        knownCount++;
                    }
                    else
                    {
                        mappingStatus = "unknown";
                        unknownCount++;
                    }
                }
                else
                {
                    unknownCount++;
                }

                items.Add(
                    new DeckIdentityReviewItem(
                        index,
                        publicModelId,
                        normalizedCandidateId,
                        mappingStatus,
                        deckseerId,
                        card.CurrentUpgradeLevel > 0,
                        card.CurrentUpgradeLevel
                    )
                );
            }

            string status = deck.Count > 0 ? "ids_revealed_for_review" : "not_observed";
            return new DeckIdentityReviewSnapshot(status, lastEvent, deck.Count, uniqueNormalizedIds.Count, knownCount, unknownCount, items, null);
        }
        catch (Exception ex)
        {
            return new DeckIdentityReviewSnapshot("probe_error", lastEvent, 0, 0, 0, 0, Array.Empty<DeckIdentityReviewItem>(), ex.GetType().Name);
        }
    }
}

internal sealed record DeckIdentityReviewSnapshot(
    string ProbeStatus,
    string LastEvent,
    int CardCount,
    int UniqueCardCount,
    int MappingKnownCount,
    int MappingUnknownCount,
    IReadOnlyList<DeckIdentityReviewItem> Items,
    string? Error
);

internal sealed record DeckIdentityReviewItem(
    int Position,
    string? PublicModelId,
    string? NormalizedCandidateId,
    string MappingStatus,
    string? DeckseerId,
    bool Upgraded,
    int UpgradeLevel
);
