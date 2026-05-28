using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Saves.Runs;
using System;
using System.Collections.Generic;
using System.Linq;

namespace DeckseerExporter.DeckseerExporterCode;

internal static class RelicRewardIdentityReviewProbe
{
    private static readonly HashSet<string> DeckseerRelicIds = new(StringComparer.Ordinal)
    {
        "akabeko",
        "blood_vial",
        "burning_blood",
        "kunai",
        "letter_opener",
        "lead_paperweight",
        "ring_of_the_snake"
    };

    public static RelicRewardIdentityReviewSnapshot NotObserved(string lastEvent)
    {
        return new RelicRewardIdentityReviewSnapshot(
            "not_observed",
            lastEvent,
            0,
            0,
            0,
            0,
            Array.Empty<RelicRewardIdentityReviewItem>(),
            null
        );
    }

    public static RelicRewardIdentityReviewSnapshot Cleared(string lastEvent)
    {
        return new RelicRewardIdentityReviewSnapshot(
            "cleared",
            lastEvent,
            0,
            0,
            0,
            0,
            Array.Empty<RelicRewardIdentityReviewItem>(),
            null
        );
    }

    public static RelicRewardIdentityReviewSnapshot FromRewards(IEnumerable<RelicReward> rewards, string lastEvent)
    {
        try
        {
            List<RelicRewardIdentityReviewItem> items = new();
            int knownCount = 0;
            int unknownCount = 0;
            int duplicateNormalizedCount = 0;
            HashSet<string> seenNormalizedIds = new(StringComparer.Ordinal);

            int position = 0;
            foreach (RelicReward reward in rewards)
            {
                string? publicModelId = reward.Relic?.ToSerializable()?.Id?.Entry;
                RelicRewardIdentityReviewItem item = BuildItem(position, publicModelId);
                items.Add(item);

                if (item.MappingStatus == "known")
                {
                    knownCount++;
                }
                else
                {
                    unknownCount++;
                }

                if (item.NormalizedCandidateId is not null && !seenNormalizedIds.Add(item.NormalizedCandidateId))
                {
                    duplicateNormalizedCount++;
                }

                position++;
            }

            return new RelicRewardIdentityReviewSnapshot(
                items.Count > 0 ? "ids_revealed_for_review" : "not_observed",
                lastEvent,
                items.Count,
                knownCount,
                unknownCount,
                duplicateNormalizedCount,
                items,
                null
            );
        }
        catch (Exception ex)
        {
            return new RelicRewardIdentityReviewSnapshot(
                "probe_error",
                lastEvent,
                0,
                0,
                0,
                0,
                Array.Empty<RelicRewardIdentityReviewItem>(),
                ex.GetType().Name
            );
        }
    }

    public static RelicRewardIdentityReviewSnapshot FromRelicModels(IEnumerable<RelicModel> relics, string lastEvent)
    {
        try
        {
            List<RelicRewardIdentityReviewItem> items = new();
            int knownCount = 0;
            int unknownCount = 0;
            int duplicateNormalizedCount = 0;
            HashSet<string> seenNormalizedIds = new(StringComparer.Ordinal);

            int position = 0;
            foreach (RelicModel relic in relics)
            {
                string? publicModelId = TryGetRelicModelId(relic);
                RelicRewardIdentityReviewItem item = BuildItem(position, publicModelId);
                items.Add(item);

                if (item.MappingStatus == "known")
                {
                    knownCount++;
                }
                else
                {
                    unknownCount++;
                }

                if (item.NormalizedCandidateId is not null && !seenNormalizedIds.Add(item.NormalizedCandidateId))
                {
                    duplicateNormalizedCount++;
                }

                position++;
            }

            return new RelicRewardIdentityReviewSnapshot(
                items.Count > 0 ? "ids_revealed_for_review" : "not_observed",
                lastEvent,
                items.Count,
                knownCount,
                unknownCount,
                duplicateNormalizedCount,
                items,
                null
            );
        }
        catch (Exception ex)
        {
            return new RelicRewardIdentityReviewSnapshot(
                "probe_error",
                lastEvent,
                0,
                0,
                0,
                0,
                Array.Empty<RelicRewardIdentityReviewItem>(),
                ex.GetType().Name
            );
        }
    }

    private static string? TryGetRelicModelId(RelicModel relic)
    {
        string? canonicalId = relic.CanonicalInstance?.Id?.Entry;
        if (!string.IsNullOrWhiteSpace(canonicalId))
        {
            return canonicalId;
        }

        string? directId = relic.Id?.Entry;
        if (!string.IsNullOrWhiteSpace(directId))
        {
            return directId;
        }

        try
        {
            SerializableRelic? serializable = relic.CanonicalInstance?.ToSerializable();
            return serializable?.Id?.Entry;
        }
        catch
        {
            try
            {
                SerializableRelic? serializable = relic.ToSerializable();
                return serializable?.Id?.Entry;
            }
            catch
            {
                return null;
            }
        }
    }

    private static RelicRewardIdentityReviewItem BuildItem(int position, string? publicModelId)
    {
        string? normalizedCandidateId = publicModelId is null
            ? null
            : CardIdentityRuntimeProbe.NormalizePublicIdString(publicModelId);
        string mappingStatus = "invalid";
        string? deckseerId = null;

        if (normalizedCandidateId is not null)
        {
            if (DeckseerRelicIds.Contains(normalizedCandidateId))
            {
                mappingStatus = "known";
                deckseerId = normalizedCandidateId;
            }
            else
            {
                mappingStatus = "unknown";
            }
        }

        return new RelicRewardIdentityReviewItem(position, publicModelId, normalizedCandidateId, mappingStatus, deckseerId);
    }
}

internal sealed record RelicRewardIdentityReviewSnapshot(
    string ProbeStatus,
    string LastEvent,
    int OptionCount,
    int MappingKnownCount,
    int MappingUnknownCount,
    int DuplicateNormalizedCount,
    IReadOnlyList<RelicRewardIdentityReviewItem> Items,
    string? Error
);

internal sealed record RelicRewardIdentityReviewItem(
    int Position,
    string? PublicModelId,
    string? NormalizedCandidateId,
    string MappingStatus,
    string? DeckseerId
);
