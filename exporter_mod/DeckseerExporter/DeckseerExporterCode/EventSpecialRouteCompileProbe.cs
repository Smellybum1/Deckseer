using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Events;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Nodes.Screens;
using MegaCrit.Sts2.Core.Nodes.Screens.CardSelection;
using MegaCrit.Sts2.Core.Nodes.Screens.Map;
using MegaCrit.Sts2.Core.Runs;

namespace DeckseerExporter.DeckseerExporterCode;

internal static class EventSpecialRouteCompileProbe
{
    public const string Status = "compiled_not_registered";

    public static readonly string[] VerifiedSymbolNames =
    {
        Symbol<NEventRoom>(nameof(NEventRoom.Create)),
        Symbol<NEventRoom>(nameof(NEventRoom.Layout)),
        Symbol<NEventRoom>(nameof(NEventRoom.CustomEventNode)),
        Symbol<NEventRoom>(nameof(NEventRoom.DefaultFocusedControl)),
        Symbol<NEventRoom>(nameof(NEventRoom._ExitTree)),
        Symbol<NEventLayout>(nameof(NEventLayout.SetEvent)),
        Symbol<NEventLayout>(nameof(NEventLayout.AddOptions)),
        Symbol<NEventLayout>(nameof(NEventLayout.ClearOptions)),
        Symbol<NEventLayout>(nameof(NEventLayout.OptionButtons)),
        Symbol<NEventLayout>(nameof(NEventLayout.DisableEventOptions)),
        Symbol<NEventLayout>(nameof(NEventLayout.DefaultFocusedControl)),
        Symbol<NEventLayout>(nameof(NEventLayout._ExitTree)),
        Symbol<NEventOptionButton>(nameof(NEventOptionButton.Event)),
        Symbol<NEventOptionButton>(nameof(NEventOptionButton.Option)),
        Symbol<NEventOptionButton>(nameof(NEventOptionButton.VoteContainer)),
        Symbol<NEventOptionButton>(nameof(NEventOptionButton._ExitTree)),
        Symbol<EventModel>(nameof(EventModel.CurrentOptions)),
        Symbol<EventModel>(nameof(EventModel.IsFinished)),
        Symbol<EventModel>(nameof(EventModel.LayoutType)),
        Symbol<EventModel>(nameof(EventModel.Node)),
        Symbol<EventOption>(nameof(EventOption.IsLocked)),
        Symbol<EventOption>(nameof(EventOption.IsProceed)),
        Symbol<EventOption>(nameof(EventOption.WillKillPlayer)),
        Symbol<EventOption>(nameof(EventOption.ShouldSaveChoiceToHistory)),
        Symbol<IRunState>(nameof(IRunState.CurrentRoom)),
        Symbol<NMapScreen>(nameof(NMapScreen.Open)),
        Symbol<NChooseARelicSelection>(nameof(NChooseARelicSelection.ShowScreen)),
        Symbol<NChooseARelicSelection>(nameof(NChooseARelicSelection._ExitTree)),
        Symbol<NChooseABundleSelectionScreen>(nameof(NChooseABundleSelectionScreen.ShowScreen)),
        Symbol<NChooseABundleSelectionScreen>(nameof(NChooseABundleSelectionScreen._ExitTree)),
        Symbol<NDeckEnchantSelectScreen>(nameof(NDeckEnchantSelectScreen.ShowScreen)),
        Symbol<NDeckEnchantSelectScreen>(nameof(NDeckEnchantSelectScreen.AfterOverlayShown)),
        Symbol<NDeckEnchantSelectScreen>(nameof(NDeckEnchantSelectScreen.AfterOverlayHidden))
    };

    private static string Symbol<T>(string memberName)
    {
        return $"{typeof(T).FullName}.{memberName}";
    }
}
