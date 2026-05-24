from __future__ import annotations

import json
from pathlib import Path

from deckseer.cli import main
from deckseer.exporter_toolchain import CommandResult, _check_folder, build_exporter_toolchain_preflight


def test_exporter_toolchain_preflight_ready_when_game_and_tools_are_visible(tmp_path: Path) -> None:
    install = _write_fake_install(tmp_path)
    manifest = _write_fake_manifest(tmp_path)

    report = build_exporter_toolchain_preflight(
        sts2_install_path=install,
        steam_manifest_path=manifest,
        export_dir=tmp_path / "exports",
        command_runner=_ready_command_runner,
        which_runner=lambda name: f"C:/tools/{name}.exe" if name == "megadot" else None,
    )

    assert report["status"] == "ready_for_static_spike"
    assert report["ready"] is True
    assert report["summary"]["blockers"] == []
    assert report["checks"]["release_info"]["version"] == "v0.106.1"
    assert report["checks"]["steam_manifest"]["buildid"] == "23372702"


def test_exporter_toolchain_preflight_reports_missing_toolchain(tmp_path: Path) -> None:
    install = _write_fake_install(tmp_path)
    manifest = _write_fake_manifest(tmp_path)

    report = build_exporter_toolchain_preflight(
        sts2_install_path=install,
        steam_manifest_path=manifest,
        export_dir=tmp_path / "exports",
        command_runner=_missing_sdk_command_runner,
        which_runner=lambda _name: None,
    )

    assert report["status"] == "blocked_missing_toolchain"
    assert report["ready"] is False
    assert report["summary"]["blockers"] == ["dotnet_sdk", "sts2_template", "megadot_or_godot"]
    assert report["checks"]["sts2_template"]["skipped"] is True
    assert report["summary"]["warnings"] == ["mods_folder_missing", "deckseer_export_folder_missing"]


def test_exporter_toolchain_preflight_reports_missing_game(tmp_path: Path) -> None:
    report = build_exporter_toolchain_preflight(
        sts2_install_path=tmp_path / "missing",
        steam_manifest_path=tmp_path / "missing_manifest.acf",
        command_runner=_ready_command_runner,
        which_runner=lambda name: f"C:/tools/{name}.exe",
    )

    assert report["status"] == "blocked_missing_game"
    assert "sts2_install" in report["summary"]["blockers"]


def test_exporter_toolchain_preflight_reports_inaccessible_folder() -> None:
    check = _check_folder(_DeniedPath())

    assert check["ok"] is False
    assert check["path"] == "C:\\denied"
    assert check["exists"] is None
    assert "Access is denied" in check["error"]


def test_exporter_toolchain_preflight_cli_text_smoke(monkeypatch, capsys) -> None:
    monkeypatch.setattr("deckseer.cli_exporter.build_exporter_toolchain_preflight", lambda **_kwargs: _fake_report())

    status = main(["exporter-toolchain-preflight", "--format", "text"])

    captured = capsys.readouterr()

    assert status == 0
    assert "Exporter Toolchain Preflight: BLOCKED_MISSING_TOOLCHAIN" in captured.out
    assert "Blockers: dotnet_sdk" in captured.out


def test_exporter_toolchain_preflight_cli_json_smoke(monkeypatch, capsys) -> None:
    monkeypatch.setattr("deckseer.cli_exporter.build_exporter_toolchain_preflight", lambda **_kwargs: _fake_report())

    status = main(["exporter-toolchain-preflight", "--format", "json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert status == 0
    assert payload["preflight_type"] == "exporter_toolchain_preflight"
    assert payload["status"] == "blocked_missing_toolchain"


def _write_fake_install(tmp_path: Path) -> Path:
    install = tmp_path / "Slay the Spire 2"
    install.mkdir()
    (install / "SlayTheSpire2.exe").write_text("", encoding="utf-8")
    (install / "SlayTheSpire2.pck").write_text("", encoding="utf-8")
    (install / "release_info.json").write_text(
        json.dumps(
            {
                "version": "v0.106.1",
                "branch": "v0.106.1",
                "commit": "d3584805",
                "date": "2026-05-22T17:01:28-07:00",
                "main_assembly_hash": "1243315044",
            }
        ),
        encoding="utf-8",
    )
    return install


def _write_fake_manifest(tmp_path: Path) -> Path:
    manifest = tmp_path / "appmanifest_2868840.acf"
    manifest.write_text(
        '\n'.join(
            [
                '"AppState"',
                "{",
                '    "appid"        "2868840"',
                '    "name"        "Slay the Spire 2"',
                '    "installdir"        "Slay the Spire 2"',
                '    "buildid"        "23372702"',
                '    "BetaKey"        "public-beta"',
                "}",
            ]
        ),
        encoding="utf-8",
    )
    return manifest


class _DeniedPath:
    def exists(self) -> bool:
        raise PermissionError("Access is denied")

    def is_dir(self) -> bool:
        raise AssertionError("is_dir should not be called when exists fails")

    def __str__(self) -> str:
        return "C:\\denied"


def _ready_command_runner(command) -> CommandResult:
    if tuple(command) == ("dotnet", "--info"):
        return CommandResult(
            returncode=0,
            stdout=".NET SDKs installed:\n  9.0.100 [C:\\Program Files\\dotnet\\sdk]\n.NET runtimes installed:\n",
            stderr="",
        )
    if tuple(command) == ("dotnet", "new", "list", "alchyrsts2mod"):
        return CommandResult(
            returncode=0,
            stdout="Empty Slay the Spire 2 Mod  alchyrsts2mod  [C#]\n",
            stderr="",
        )
    return CommandResult(returncode=1, stdout="", stderr="unexpected command")


def _missing_sdk_command_runner(command) -> CommandResult:
    if tuple(command) == ("dotnet", "--info"):
        return CommandResult(returncode=0, stdout=".NET SDKs installed:\nNo SDKs were found.\n", stderr="")
    return CommandResult(returncode=1, stdout="", stderr="unexpected command")


def _fake_report() -> dict:
    return {
        "preflight_type": "exporter_toolchain_preflight",
        "status": "blocked_missing_toolchain",
        "ready": False,
        "paths": {
            "sts2_install": "D:\\Games\\Steam\\steamapps\\common\\Slay the Spire 2",
            "steam_manifest": "D:\\Games\\Steam\\steamapps\\appmanifest_2868840.acf",
            "mods_folder": "D:\\Games\\Steam\\steamapps\\common\\Slay the Spire 2\\mods",
            "deckseer_export_folder": "C:\\Users\\moxhe\\AppData\\Local\\Deckseer\\exports",
        },
        "checks": {
            "sts2_install": {"ok": True, "path": "D:\\Games\\Steam\\steamapps\\common\\Slay the Spire 2"},
            "release_info": {"ok": True, "version": "v0.106.1"},
            "steam_manifest": {"ok": True, "buildid": "23372702", "branch": "public-beta"},
            "dotnet_sdk": {"ok": False, "sdk_versions": []},
            "sts2_template": {"ok": False},
            "megadot": {"ok": False, "path": None},
            "godot": {"ok": False, "path": None},
            "mods_folder": {"ok": False, "path": "D:\\Games\\Steam\\steamapps\\common\\Slay the Spire 2\\mods"},
            "deckseer_export_folder": {"ok": False, "path": "C:\\Users\\moxhe\\AppData\\Local\\Deckseer\\exports"},
        },
        "summary": {
            "blockers": ["dotnet_sdk"],
            "warnings": ["mods_folder_missing"],
        },
        "caveats": ["Read-only preflight; no tools are installed and no folders are created."],
    }
