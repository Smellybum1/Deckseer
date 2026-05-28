using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.Saves.Runs;
using System;

namespace DeckseerExporter.DeckseerExporterCode;

internal static class CardRewardRunStateCompileProbe
{
    public const string Status = "run_state_symbols_compiled_not_exported";

    public static readonly string[] RequiredFieldNames =
    {
        "character",
        "act",
        "floor",
        "ascension",
        "gold",
        "hp.current",
        "hp.max",
        "deck",
        "deck.id",
        "deck.upgraded",
        "relics",
        "potions"
    };

    public static readonly string[] VerifiedSymbolNames =
    {
        Symbol<RunManager>(nameof(RunManager.Instance)),
        Symbol<RunManager>(nameof(RunManager.IsInProgress)),
        Symbol<RunManager>(nameof(RunManager.ToSave)),
        Symbol<IRunState>(nameof(IRunState.ActFloor)),
        Symbol<IRunState>(nameof(IRunState.TotalFloor)),
        Symbol<IRunState>(nameof(IRunState.AscensionLevel)),
        Symbol<RunState>(nameof(RunState.Players)),
        Symbol<SerializableRun>(nameof(SerializableRun.Players)),
        Symbol<SerializableRun>(nameof(SerializableRun.CurrentActIndex)),
        Symbol<SerializableRun>(nameof(SerializableRun.Ascension)),
        Symbol<SerializableRun>(nameof(SerializableRun.FloorReached)),
        Symbol<SerializablePlayer>(nameof(SerializablePlayer.CharacterId)),
        Symbol<SerializablePlayer>(nameof(SerializablePlayer.CurrentHp)),
        Symbol<SerializablePlayer>(nameof(SerializablePlayer.MaxHp)),
        Symbol<SerializablePlayer>(nameof(SerializablePlayer.Gold)),
        Symbol<SerializablePlayer>(nameof(SerializablePlayer.Deck)),
        Symbol<SerializablePlayer>(nameof(SerializablePlayer.Relics)),
        Symbol<SerializablePlayer>(nameof(SerializablePlayer.Potions)),
        Symbol<SerializableCard>(nameof(SerializableCard.Id)),
        Symbol<SerializableCard>(nameof(SerializableCard.CurrentUpgradeLevel)),
        Symbol<SerializableRelic>(nameof(SerializableRelic.Id)),
        Symbol<SerializablePotion>(nameof(SerializablePotion.Id))
    };

    private static string Symbol<T>(string memberName)
    {
        return $"{typeof(T).FullName}.{memberName}";
    }

    private static string Symbol(Type type, string memberName)
    {
        return $"{type.FullName}.{memberName}";
    }
}
