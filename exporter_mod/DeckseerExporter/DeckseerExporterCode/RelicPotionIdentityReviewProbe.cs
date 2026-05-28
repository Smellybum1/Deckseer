using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.Saves.Runs;
using System;
using System.Collections.Generic;

namespace DeckseerExporter.DeckseerExporterCode;

internal static class RelicPotionIdentityReviewProbe
{
    private static readonly HashSet<string> DeckseerRelicIds = new(StringComparer.Ordinal)
    {
        "akabeko",
        "blood_vial",
        "burning_blood",
        "centennial_puzzle",
        "kunai",
        "letter_opener",
        "lead_paperweight",
        "lost_coffer",
        "mr_struggles",
        "orichalcum",
        "paels_eye",
        "ring_of_the_snake",
        "shuriken",
        "strike_dummy",
        "tea_of_discourtesy"
    };

    private static readonly HashSet<string> DeckseerPotionIds = new(StringComparer.Ordinal)
    {
        "attack_potion",
        "block_potion",
        "blessing_of_the_forge",
        "colorless_potion",
        "fire_potion",
        "heart_of_iron"
    };

    public static RelicPotionIdentityReviewSnapshot NotObserved(string lastEvent)
    {
        return new RelicPotionIdentityReviewSnapshot(
            "not_observed",
            lastEvent,
            0,
            0,
            0,
            0,
            0,
            0,
            Array.Empty<RelicPotionIdentityReviewItem>(),
            Array.Empty<RelicPotionIdentityReviewItem>(),
            null
        );
    }

    public static RelicPotionIdentityReviewSnapshot Cleared(string lastEvent)
    {
        return new RelicPotionIdentityReviewSnapshot(
            "cleared",
            lastEvent,
            0,
            0,
            0,
            0,
            0,
            0,
            Array.Empty<RelicPotionIdentityReviewItem>(),
            Array.Empty<RelicPotionIdentityReviewItem>(),
            null
        );
    }

    public static RelicPotionIdentityReviewSnapshot FromRunState(IRunState? runState, string lastEvent)
    {
        try
        {
            if (runState is null || RunManager.Instance is null || !RunManager.Instance.IsInProgress)
            {
                return NotObserved(lastEvent);
            }

            SerializableRun? serializableRun = RunManager.Instance.ToSave(null);
            return FromSerializableRun(serializableRun, lastEvent);
        }
        catch (Exception ex)
        {
            return new RelicPotionIdentityReviewSnapshot(
                "probe_error",
                lastEvent,
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
        }
    }

    public static RelicPotionIdentityReviewSnapshot FromCurrentSerializableRun(string lastEvent)
    {
        try
        {
            if (RunManager.Instance is null || !RunManager.Instance.IsInProgress)
            {
                return NotObserved(lastEvent);
            }

            return FromSerializableRun(RunManager.Instance.ToSave(null), lastEvent);
        }
        catch (Exception ex)
        {
            return new RelicPotionIdentityReviewSnapshot(
                "probe_error",
                lastEvent,
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
        }
    }

    private static RelicPotionIdentityReviewSnapshot FromSerializableRun(SerializableRun? serializableRun, string lastEvent)
    {
        if (serializableRun is null || serializableRun.Players.Count != 1)
        {
            return NotObserved(lastEvent);
        }

        SerializablePlayer player = serializableRun.Players[0];
        List<RelicPotionIdentityReviewItem> relicItems = new();
        List<RelicPotionIdentityReviewItem> potionItems = new();
        int relicKnownCount = 0;
        int relicUnknownCount = 0;
        int potionKnownCount = 0;
        int potionUnknownCount = 0;

        if (player.Relics is not null)
        {
            for (int index = 0; index < player.Relics.Count; index++)
            {
                RelicPotionIdentityReviewItem item = BuildItem(index, player.Relics[index].Id?.Entry, DeckseerRelicIds);
                relicItems.Add(item);
                CountMapping(item, ref relicKnownCount, ref relicUnknownCount);
            }
        }

        if (player.Potions is not null)
        {
            for (int index = 0; index < player.Potions.Count; index++)
            {
                RelicPotionIdentityReviewItem item = BuildItem(index, player.Potions[index].Id?.Entry, DeckseerPotionIds);
                potionItems.Add(item);
                CountMapping(item, ref potionKnownCount, ref potionUnknownCount);
            }
        }

        string status = relicItems.Count > 0 || potionItems.Count > 0 ? "ids_revealed_for_review" : "not_observed";
        return new RelicPotionIdentityReviewSnapshot(
            status,
            lastEvent,
            relicItems.Count,
            relicKnownCount,
            relicUnknownCount,
            potionItems.Count,
            potionKnownCount,
            potionUnknownCount,
            relicItems,
            potionItems,
            null
        );
    }

    private static RelicPotionIdentityReviewItem BuildItem(int position, string? publicModelId, HashSet<string> knownIds)
    {
        string? normalizedCandidateId = publicModelId is null
            ? null
            : CardIdentityRuntimeProbe.NormalizePublicIdString(publicModelId);
        string mappingStatus = "invalid";
        string? deckseerId = null;

        if (normalizedCandidateId is not null)
        {
            if (knownIds.Contains(normalizedCandidateId))
            {
                mappingStatus = "known";
                deckseerId = normalizedCandidateId;
            }
            else
            {
                mappingStatus = "unknown";
            }
        }

        return new RelicPotionIdentityReviewItem(position, publicModelId, normalizedCandidateId, mappingStatus, deckseerId);
    }

    private static void CountMapping(RelicPotionIdentityReviewItem item, ref int knownCount, ref int unknownCount)
    {
        if (item.MappingStatus == "known")
        {
            knownCount++;
        }
        else
        {
            unknownCount++;
        }
    }
}

internal sealed record RelicPotionIdentityReviewSnapshot(
    string ProbeStatus,
    string LastEvent,
    int RelicCount,
    int RelicMappingKnownCount,
    int RelicMappingUnknownCount,
    int PotionCount,
    int PotionMappingKnownCount,
    int PotionMappingUnknownCount,
    IReadOnlyList<RelicPotionIdentityReviewItem> RelicItems,
    IReadOnlyList<RelicPotionIdentityReviewItem> PotionItems,
    string? Error
);

internal sealed record RelicPotionIdentityReviewItem(
    int Position,
    string? PublicModelId,
    string? NormalizedCandidateId,
    string MappingStatus,
    string? DeckseerId
);
