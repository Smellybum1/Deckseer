using Godot;
using MegaCrit.Sts2.Core.Modding;
using System;
using System.IO;
using System.Text.Json;

namespace DeckseerExporter.DeckseerExporterCode;

[ModInitializer(nameof(Initialize))]
public partial class MainFile : Node
{
    public const string ModId = "DeckseerExporter";
    private const string ExporterVersion = "0.1.0";

    public static MegaCrit.Sts2.Core.Logging.Logger Logger { get; } = new(ModId, MegaCrit.Sts2.Core.Logging.LogType.Generic);

    public static void Initialize()
    {
        WriteStaticStatusExport();
    }

    private static void WriteStaticStatusExport()
    {
        try
        {
            string exportDirectory = Path.Combine(
                System.Environment.GetFolderPath(System.Environment.SpecialFolder.LocalApplicationData),
                "Deckseer",
                "exports"
            );
            Directory.CreateDirectory(exportDirectory);

            string exportPath = Path.Combine(exportDirectory, "latest_state.json");
            string tempPath = Path.Combine(exportDirectory, "latest_state.tmp");
            string payload = JsonSerializer.Serialize(
                new
                {
                    game = "slay_the_spire_2",
                    screen_type = "exporter_status",
                    status = "ok",
                    export_metadata = new
                    {
                        source = "deckseer_exporter_mod",
                        exporter_version = ExporterVersion,
                        game_build = (string?)null,
                        game_patch = (string?)null,
                        exported_at = DateTimeOffset.UtcNow.ToString("O"),
                        requires_user_confirmation = false,
                        confidence = "high",
                        caveats = new[]
                        {
                            "Static exporter status only; no live run state is present.",
                            "Game patch/build metadata is not exported in the first static spike."
                        }
                    }
                },
                new JsonSerializerOptions { WriteIndented = true }
            );

            File.WriteAllText(tempPath, payload);
            File.Move(tempPath, exportPath, overwrite: true);
        }
        catch (Exception ex)
        {
            GD.PrintErr($"DeckseerExporter failed to write static status export: {ex.Message}");
        }
    }
}
