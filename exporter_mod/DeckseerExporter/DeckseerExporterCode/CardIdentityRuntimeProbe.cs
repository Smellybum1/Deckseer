using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Saves.Runs;
using System;
using System.Collections.Generic;
using System.Text;

namespace DeckseerExporter.DeckseerExporterCode;

internal static class CardIdentityRuntimeProbe
{
    private static readonly HashSet<string> DeckseerCardIds = new(StringComparer.Ordinal)
    {
        "acrobatics",
        "accuracy",
        "adrenaline",
        "afterimage",
        "anger",
        "anticipate",
        "armaments",
        "arsenal",
        "astral_pulse",
        "backflip",
        "backstab",
        "ball_lightning",
        "banshees_cry",
        "barrage",
        "barricade",
        "bash",
        "battle_trance",
        "beam_cell",
        "biased_cognition",
        "big_bang",
        "black_hole",
        "blade_dance",
        "bludgeon",
        "blur",
        "body_slam",
        "bodyguard",
        "bone_shards",
        "boot_sequence",
        "bouncing_flask",
        "buffer",
        "bulwark",
        "bundle_of_joy",
        "calcify",
        "calculated_gamble",
        "call_of_the_void",
        "capacitor",
        "celestial_might",
        "charge",
        "charge_battery",
        "child_of_the_stars",
        "chill",
        "claw",
        "cloak_and_dagger",
        "cloak_of_stars",
        "clothesline",
        "cold_snap",
        "collision_course",
        "compile_driver",
        "conqueror",
        "convergence",
        "coolheaded",
        "corruption",
        "crash_landing",
        "crescent_spear",
        "dagger_spray",
        "dagger_throw",
        "danse_macabre",
        "dark_embrace",
        "darkness",
        "dash",
        "deadly_poison",
        "deathbringer",
        "deaths_door",
        "debilitate",
        "defend",
        "deflect",
        "defragment",
        "defy",
        "demesne",
        "demon_form",
        "devour_life",
        "dirge",
        "dodge_and_roll",
        "dominate",
        "dramatic_entrance",
        "dualcast",
        "dying_star",
        "echo_form",
        "eidolon",
        "end_of_days",
        "enfeebling_touch",
        "envenom",
        "eradicate",
        "escape_plan",
        "fasten",
        "fear",
        "feel_no_pain",
        "fiend_fire",
        "finisher",
        "flame_barrier",
        "flatten",
        "footwork",
        "forbidden_grimoire",
        "friendship",
        "ftl",
        "gamma_blast",
        "gather_light",
        "genetic_algorithm",
        "glacier",
        "glow",
        "go_for_the_eyes",
        "grave_warden",
        "guards",
        "headbutt",
        "hidden_cache",
        "hologram",
        "hyperbeam",
        "impervious",
        "inflame",
        "infinite_blades",
        "iron_wave",
        "kingly_kick",
        "leap",
        "leg_sweep",
        "lethality",
        "machine_learning",
        "malaise",
        "memento_mori",
        "meteor_shower",
        "misery",
        "murder",
        "necromastery",
        "negative_pulse",
        "neurosurge",
        "neutralize",
        "noxious_fumes",
        "null",
        "offering",
        "orbit",
        "overclock",
        "pagestorm",
        "parry",
        "particle_wall",
        "patter",
        "perfected_strike",
        "photon_cut",
        "piercing_wail",
        "pillar_of_creation",
        "pinpoint",
        "poisoned_stab",
        "poke",
        "pommel_strike",
        "predator",
        "prepared",
        "putrefy",
        "quadcast",
        "quasar",
        "radiate",
        "rattle",
        "reanimate",
        "refine_blade",
        "reflect",
        "ricochet",
        "royal_gamble",
        "royalties",
        "sacrifice",
        "scourge",
        "second_wind",
        "setup_strike",
        "shared_fate",
        "shining_strike",
        "shroud",
        "shrug_it_off",
        "sic_em",
        "skim",
        "sleight_of_flesh",
        "slice",
        "solar_strike",
        "spectrum_shift",
        "squeeze",
        "strike",
        "sucker_punch",
        "sunder",
        "supermassive",
        "survivor",
        "sweeping_beam",
        "synchronize",
        "tactician",
        "tools_of_the_trade",
        "thunderclap",
        "turbo",
        "tyranny",
        "ultimate_defend",
        "unleash",
        "uppercut",
        "void_form",
        "well_laid_plans",
        "whirlwind",
        "wraith_form",
        "wrought_in_war",
        "zap"
    };

    private static readonly IReadOnlyDictionary<string, string> DeckseerCardIdAliases = new Dictionary<string, string>(StringComparer.Ordinal)
    {
        ["defend_ironclad"] = "defend",
        ["defend_silent"] = "defend",
        ["strike_ironclad"] = "strike",
        ["strike_silent"] = "strike"
    };

    public static CardIdentityRuntimeSnapshot NotObserved(string lastEvent)
    {
        return new CardIdentityRuntimeSnapshot("not_observed", lastEvent, 0, 0, 0, 0, 0, 0, 0, 0, null);
    }

    public static CardIdentityReviewSnapshot ReviewNotObserved(string lastEvent)
    {
        return new CardIdentityReviewSnapshot("not_observed", lastEvent, 0, Array.Empty<CardIdentityReviewItem>(), null);
    }

    public static CardIdentityRuntimeSnapshot Cleared(string lastEvent)
    {
        return new CardIdentityRuntimeSnapshot("cleared", lastEvent, 0, 0, 0, 0, 0, 0, 0, 0, null);
    }

    public static CardIdentityReviewSnapshot ReviewCleared(string lastEvent)
    {
        return new CardIdentityReviewSnapshot("cleared", lastEvent, 0, Array.Empty<CardIdentityReviewItem>(), null);
    }

    public static CardIdentityRuntimeSnapshot FromCards(IReadOnlyList<CardModel> cards, string lastEvent)
    {
        try
        {
            int directIdCount = 0;
            int serializedIdCount = 0;
            int nullableSerializedIdCount = 0;
            int upgradedCount = 0;
            int knownCount = 0;
            int unknownCount = 0;
            int duplicateNormalizedCount = 0;
            HashSet<string> normalizedIds = new(StringComparer.Ordinal);

            foreach (CardModel card in cards)
            {
                string? normalizedDirectId = NormalizeModelId(card.Id);
                if (normalizedDirectId is null)
                {
                    unknownCount++;
                }
                else
                {
                    directIdCount++;
                    if (!normalizedIds.Add(normalizedDirectId))
                    {
                        duplicateNormalizedCount++;
                    }

                    if (ResolveDeckseerCardId(normalizedDirectId) is not null)
                    {
                        knownCount++;
                    }
                    else
                    {
                        unknownCount++;
                    }
                }

                if (card.IsUpgraded || card.CurrentUpgradeLevel > 0)
                {
                    upgradedCount++;
                }

                SerializableCard serialized = card.ToSerializable();
                if (serialized.Id is null)
                {
                    nullableSerializedIdCount++;
                }
                else
                {
                    serializedIdCount++;
                }
            }

            string status = unknownCount > 0 ? "mapping_incomplete" : "card_choice_ids_seen";
            if (cards.Count == 0)
            {
                status = "not_observed";
            }

            return new CardIdentityRuntimeSnapshot(
                status,
                lastEvent,
                cards.Count,
                directIdCount,
                serializedIdCount,
                nullableSerializedIdCount,
                upgradedCount,
                knownCount,
                unknownCount,
                duplicateNormalizedCount,
                null
            );
        }
        catch (Exception ex)
        {
            return new CardIdentityRuntimeSnapshot("probe_error", lastEvent, 0, 0, 0, 0, 0, 0, 0, 0, ex.GetType().Name);
        }
    }

    public static CardIdentityReviewSnapshot ReviewFromCards(IReadOnlyList<CardModel> cards, string lastEvent)
    {
        try
        {
            List<CardIdentityReviewItem> items = new();
            HashSet<string> normalizedIds = new(StringComparer.Ordinal);

            for (int index = 0; index < cards.Count; index++)
            {
                CardModel card = cards[index];
                string publicModelId = card.Id.Entry;
                string? normalizedCandidateId = NormalizeIdString(publicModelId);
                string mappingStatus = "invalid";
                string? deckseerId = null;

                if (normalizedCandidateId is not null)
                {
                    bool duplicate = !normalizedIds.Add(normalizedCandidateId);
                    if (duplicate)
                    {
                        mappingStatus = "duplicate";
                    }
                    else if (ResolveDeckseerCardId(normalizedCandidateId) is string resolvedDeckseerId)
                    {
                        mappingStatus = "known";
                        deckseerId = resolvedDeckseerId;
                    }
                    else
                    {
                        mappingStatus = "unknown";
                    }
                }

                SerializableCard serialized = card.ToSerializable();
                bool serializedIdMatchesDirectId = serialized.Id is not null && serialized.Id.Entry == publicModelId;

                items.Add(
                    new CardIdentityReviewItem(
                        index,
                        publicModelId,
                        normalizedCandidateId,
                        mappingStatus,
                        deckseerId,
                        card.IsUpgraded,
                        card.CurrentUpgradeLevel,
                        serializedIdMatchesDirectId
                    )
                );
            }

            string status = cards.Count > 0 ? "ids_revealed_for_review" : "not_observed";
            return new CardIdentityReviewSnapshot(status, lastEvent, cards.Count, items, null);
        }
        catch (Exception ex)
        {
            return new CardIdentityReviewSnapshot("probe_error", lastEvent, 0, Array.Empty<CardIdentityReviewItem>(), ex.GetType().Name);
        }
    }

    private static string? NormalizeModelId(ModelId modelId)
    {
        return NormalizeIdString(modelId.Entry);
    }

    public static bool IsKnownDeckseerCardId(string? normalizedId)
    {
        return ResolveDeckseerCardId(normalizedId) is not null;
    }

    public static string? ResolveDeckseerCardId(string? normalizedId)
    {
        if (normalizedId is null)
        {
            return null;
        }

        if (DeckseerCardIds.Contains(normalizedId))
        {
            return normalizedId;
        }

        return DeckseerCardIdAliases.TryGetValue(normalizedId, out string? deckseerId) ? deckseerId : null;
    }

    public static string? NormalizePublicIdString(string raw)
    {
        return NormalizeIdString(raw);
    }

    private static string? NormalizeIdString(string raw)
    {
        if (string.IsNullOrWhiteSpace(raw))
        {
            return null;
        }

        StringBuilder builder = new();
        bool previousWasSeparator = false;
        foreach (char character in raw.Trim())
        {
            if (char.IsLetterOrDigit(character))
            {
                builder.Append(char.ToLowerInvariant(character));
                previousWasSeparator = false;
            }
            else if (!previousWasSeparator)
            {
                builder.Append('_');
                previousWasSeparator = true;
            }
        }

        string normalized = builder.ToString().Trim('_');
        if (normalized.EndsWith("_plus", StringComparison.Ordinal))
        {
            normalized = normalized[..^5];
        }

        return normalized.Length == 0 ? null : normalized;
    }
}

internal sealed record CardIdentityRuntimeSnapshot(
    string ProbeStatus,
    string LastEvent,
    int ReadCount,
    int DirectIdCount,
    int SerializedIdCount,
    int NullableSerializedIdCount,
    int UpgradedCount,
    int MappingKnownCount,
    int MappingUnknownCount,
    int DuplicateNormalizedCount,
    string? Error
);

internal sealed record CardIdentityReviewSnapshot(
    string ProbeStatus,
    string LastEvent,
    int OptionCount,
    IReadOnlyList<CardIdentityReviewItem> Items,
    string? Error
);

internal sealed record CardIdentityReviewItem(
    int Position,
    string PublicModelId,
    string? NormalizedCandidateId,
    string MappingStatus,
    string? DeckseerId,
    bool Upgraded,
    int UpgradeLevel,
    bool SerializedIdMatchesDirectId
);
