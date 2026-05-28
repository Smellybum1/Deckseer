using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.Saves.Runs;
using System;
using System.Linq;

namespace DeckseerExporter.DeckseerExporterCode;

internal static class CardRewardLiveExportBuilder
{
    private static readonly string[] Caveats =
    {
        "Run inspect-export and confirm this live state before using recommend-export.",
        "Confirm the visible card reward, deck, HP, gold, relics, and potions before using this state.",
        "Live exporter map/path context is unknown/defaulted."
    };

    public static object? TryBuildPayload(
        ScreenObservationSnapshot observation,
        CardRewardLiveExportCandidateSnapshot candidate,
        string exporterVersion
    )
    {
        try
        {
            if (candidate.Candidate != "ready" || RunManager.Instance is null || !RunManager.Instance.IsInProgress)
            {
                return null;
            }

            if (
                observation.RewardCount > observation.CardRewardCount
                && (observation.LastEvent != "reward_collected" || candidate.MixedRewardFreshnessBlockers.Count > 0)
            )
            {
                return null;
            }

            SerializableRun? serializableRun = RunManager.Instance.ToSave(null);
            if (serializableRun is null || serializableRun.Players.Count != 1)
            {
                return null;
            }

            SerializablePlayer player = serializableRun.Players[0];
            string? character = NormalizeCharacterId(player.CharacterId?.Entry);
            if (character is null)
            {
                return null;
            }

            int act = serializableRun.CurrentActIndex + 1;
            int floor = serializableRun.FloorReached;
            int ascension = serializableRun.Ascension;
            if (act < 1 || floor < 0 || ascension < 0 || player.Gold < 0 || player.CurrentHp < 0 || player.MaxHp <= 0)
            {
                return null;
            }

            if (observation.CardIdentityReview.Items.Any(item => item.Upgraded || item.UpgradeLevel > 0))
            {
                return null;
            }

            string[] cardReward = observation.CardIdentityReview.Items
                .OrderBy(item => item.Position)
                .Select(item => item.MappingStatus == "known" ? item.DeckseerId : null)
                .OfType<string>()
                .ToArray();
            if (cardReward.Length == 0 || cardReward.Length != observation.CardRewardOptionCount)
            {
                return null;
            }

            if (observation.DeckIdentityReview.Items.Any(item => item.MappingStatus != "known" || item.DeckseerId is null))
            {
                return null;
            }

            object[] deck = observation.DeckIdentityReview.Items
                .GroupBy(item => new { item.DeckseerId, item.Upgraded })
                .OrderBy(group => group.Key.DeckseerId)
                .ThenBy(group => group.Key.Upgraded)
                .Select(group => new
                {
                    id = group.Key.DeckseerId!,
                    upgraded = group.Key.Upgraded,
                    count = group.Count()
                })
                .ToArray<object>();

            string[] relics = observation.RelicPotionIdentityReview.RelicItems
                .OrderBy(item => item.Position)
                .Select(item => item.MappingStatus == "known" ? item.DeckseerId : null)
                .OfType<string>()
                .ToArray();
            if (relics.Length != observation.CardRewardRunStateRuntime.RelicCount)
            {
                return null;
            }

            string[] potions = observation.RelicPotionIdentityReview.PotionItems
                .OrderBy(item => item.Position)
                .Select(item => item.MappingStatus == "known" ? item.DeckseerId : null)
                .OfType<string>()
                .ToArray();
            if (potions.Length != observation.CardRewardRunStateRuntime.PotionCount)
            {
                return null;
            }

            return new
            {
                game = "slay_the_spire_2",
                screen_type = "card_reward",
                character,
                act,
                floor,
                ascension,
                gold = player.Gold,
                hp = new
                {
                    current = player.CurrentHp,
                    max = player.MaxHp
                },
                deck,
                relics,
                potions,
                card_reward = cardReward,
                run_context = new
                {
                    next_node_type = "unknown",
                    path_pressure = "unknown",
                    notes = new[]
                    {
                        "Live exporter did not infer map/path context."
                    }
                },
                export_metadata = new
                {
                    source = "deckseer_exporter_mod",
                    exporter_version = exporterVersion,
                    game_build = (string?)null,
                    game_patch = (string?)null,
                    exported_at = DateTimeOffset.UtcNow.ToString("O"),
                    requires_user_confirmation = true,
                    confidence = "medium",
                    caveats = Caveats
                }
            };
        }
        catch (Exception ex)
        {
            MainFile.Logger.Error($"Deckseer live card_reward export refused after payload validation error: {ex.GetType().Name}");
            return null;
        }
    }

    private static string? NormalizeCharacterId(string? publicId)
    {
        if (publicId is null)
        {
            return null;
        }

        string? normalized = CardIdentityRuntimeProbe.NormalizePublicIdString(publicId);
        return normalized switch
        {
            "the_silent" => "silent",
            "silent" => "silent",
            "ironclad" => "ironclad",
            "defect" => "defect",
            "necrobinder" => "necrobinder",
            "regent" => "regent",
            _ => normalized
        };
    }
}
