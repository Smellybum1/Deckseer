using MegaCrit.Sts2.Core.Hooks;
using MegaCrit.Sts2.Core.Modding;
using MegaCrit.Sts2.Core.Nodes.Rewards;
using MegaCrit.Sts2.Core.Nodes.Screens;
using MegaCrit.Sts2.Core.Nodes.Screens.CardSelection;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.Saves.Runs;

namespace DeckseerExporter.DeckseerExporterCode;

internal static class CardRewardApiProbe
{
    public const string Status = "compiled";

    public static readonly string[] VerifiedSymbolNames =
    {
        Symbol<RunManager>(nameof(RunManager.Instance)),
        Symbol<RunManager>(nameof(RunManager.IsInProgress)),
        Symbol<RunManager>(nameof(RunManager.ToSave)),
        Symbol<IRunState>(nameof(IRunState.ActFloor)),
        Symbol<IRunState>(nameof(IRunState.TotalFloor)),
        Symbol<IRunState>(nameof(IRunState.AscensionLevel)),
        Symbol<RunState>(nameof(RunState.Players)),
        Symbol<RewardsSet>(nameof(RewardsSet.Player)),
        Symbol<RewardsSet>(nameof(RewardsSet.Rewards)),
        Symbol<RewardsSet>(nameof(RewardsSet.AllRewardsSuccessfullySelected)),
        Symbol<Reward>(nameof(Reward.Player)),
        Symbol<Reward>(nameof(Reward.Description)),
        Symbol<Reward>(nameof(Reward.IsPopulated)),
        Symbol<Reward>(nameof(Reward.ParentRewardSet)),
        Symbol<CardReward>(nameof(CardReward.Cards)),
        Symbol<CardReward>(nameof(CardReward.CanSkip)),
        Symbol<CardReward>(nameof(CardReward.CanReroll)),
        Symbol<CardReward>(nameof(CardReward.IsPopulated)),
        Symbol<CardReward>(nameof(CardReward.ToSerializable)),
        Symbol<SerializableRun>(nameof(SerializableRun.Players)),
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
        Symbol<SerializablePotion>(nameof(SerializablePotion.Id)),
        Symbol<SerializableReward>(nameof(SerializableReward.RewardType)),
        Symbol<SerializableReward>(nameof(SerializableReward.OptionCount)),
        Symbol<NRewardsScreen>(nameof(NRewardsScreen.ScreenType)),
        Symbol<NRewardButton>(nameof(NRewardButton.Reward)),
        Symbol<NLinkedRewardSet>(nameof(NLinkedRewardSet.LinkedRewardSet)),
        Symbol<NCardRewardSelectionScreen>(nameof(NCardRewardSelectionScreen.ScreenType)),
        Symbol<NChooseACardSelectionScreen>(nameof(NChooseACardSelectionScreen.ScreenType)),
        Symbol(typeof(ModHelper), nameof(ModHelper.SubscribeForRunStateHooks)),
        Symbol(typeof(Hook), nameof(Hook.AfterModifyingCardRewardOptions)),
        Symbol(typeof(Hook), nameof(Hook.AfterModifyingRewards)),
        Symbol(typeof(Hook), nameof(Hook.AfterRewardTaken))
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
