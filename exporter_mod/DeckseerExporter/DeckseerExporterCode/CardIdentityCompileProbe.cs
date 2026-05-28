using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Saves.Runs;

namespace DeckseerExporter.DeckseerExporterCode;

internal static class CardIdentityCompileProbe
{
    public const string Status = "compiled_not_exported";

    public static readonly string[] VerifiedSymbolNames =
    {
        Symbol<CardModel>(nameof(CardModel.Id)),
        Symbol<CardModel>(nameof(CardModel.CurrentUpgradeLevel)),
        Symbol<CardModel>(nameof(CardModel.IsUpgraded)),
        Symbol<CardModel>(nameof(CardModel.ToSerializable)),
        Symbol<CardCreationResult>(nameof(CardCreationResult.Card)),
        Symbol<SerializableCard>(nameof(SerializableCard.Id)),
        Symbol<SerializableCard>(nameof(SerializableCard.CurrentUpgradeLevel))
    };

    public static CardIdentityCompileSnapshot CompileOnlyReadCardIdentity(CardModel card, CardCreationResult creationResult)
    {
        ModelId directId = card.Id;
        int directUpgradeLevel = card.CurrentUpgradeLevel;
        bool directIsUpgraded = card.IsUpgraded;
        SerializableCard serialized = card.ToSerializable();
        ModelId? serializedId = serialized.Id;
        int serializedUpgradeLevel = serialized.CurrentUpgradeLevel;
        CardModel creationResultCard = creationResult.Card;

        return new CardIdentityCompileSnapshot(
            directId,
            directUpgradeLevel,
            directIsUpgraded,
            serializedId,
            serializedUpgradeLevel,
            creationResultCard.Id
        );
    }

    private static string Symbol<T>(string memberName)
    {
        return $"{typeof(T).FullName}.{memberName}";
    }
}

internal sealed record CardIdentityCompileSnapshot(
    ModelId DirectId,
    int DirectUpgradeLevel,
    bool DirectIsUpgraded,
    ModelId? SerializedId,
    int SerializedUpgradeLevel,
    ModelId CreationResultCardId
);
