using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Modding;
using MegaCrit.Sts2.Core.Runs;
using System.Collections.Generic;

namespace DeckseerExporter.DeckseerExporterCode;

internal sealed class DeckseerHookCompileProbeModel : SingletonModel
{
    public override bool ShouldReceiveCombatHooks => false;
}

internal static class HookModelCompileProbe
{
    public const string Status = "compiled_not_registered";

    public static readonly string[] VerifiedSymbolNames =
    {
        Symbol<RunHookSubscriptionDelegate>(nameof(RunHookSubscriptionDelegate.Invoke)),
        Symbol(typeof(ModHelper), nameof(ModHelper.SubscribeForRunStateHooks)),
        Symbol(typeof(ModHelper), nameof(ModHelper.IterateAllRunStateSubscribers)),
        Symbol(typeof(ModelDb), nameof(ModelDb.Contains)),
        Symbol(typeof(ModelDb), nameof(ModelDb.Inject)),
        Symbol(typeof(ModelDb), nameof(ModelDb.Singleton)),
        Symbol<AbstractModel>(nameof(AbstractModel.IsCanonical)),
        Symbol<AbstractModel>(nameof(AbstractModel.AssertCanonical))
    };

    public static void CompileOnlyRegisterRunHook()
    {
        ModHelper.SubscribeForRunStateHooks(MainFile.ModId, CompileOnlyGetRunHookModels);
    }

    private static IEnumerable<AbstractModel> CompileOnlyGetRunHookModels(RunState runState)
    {
        if (!ModelDb.Contains(typeof(DeckseerHookCompileProbeModel)))
        {
            ModelDb.Inject(typeof(DeckseerHookCompileProbeModel));
        }

        AbstractModel hookModel = ModelDb.Singleton<DeckseerHookCompileProbeModel>();
        hookModel.AssertCanonical();
        return new[] { hookModel };
    }

    private static string Symbol<T>(string memberName)
    {
        return $"{typeof(T).FullName}.{memberName}";
    }

    private static string Symbol(Type type, string memberName)
    {
        return $"{type.FullName}.{memberName}";
    }
}
