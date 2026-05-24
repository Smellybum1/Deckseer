from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Callable, Sequence


DEFAULT_STS2_INSTALL = Path(r"D:\Games\Steam\steamapps\common\Slay the Spire 2")
DEFAULT_STEAM_MANIFEST = Path(r"D:\Games\Steam\steamapps\appmanifest_2868840.acf")


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


CommandRunner = Callable[[Sequence[str]], CommandResult]
WhichRunner = Callable[[str], str | None]


def build_exporter_toolchain_preflight(
    *,
    sts2_install_path: Path = DEFAULT_STS2_INSTALL,
    steam_manifest_path: Path = DEFAULT_STEAM_MANIFEST,
    export_dir: Path | None = None,
    command_runner: CommandRunner | None = None,
    which_runner: WhichRunner | None = None,
) -> dict:
    """Build a read-only status report for the future static exporter mod spike."""

    runner = command_runner or _run_command
    which = which_runner or shutil.which
    export_path = export_dir or _default_export_dir()

    install_check = _check_sts2_install(sts2_install_path)
    release_check = _read_release_info(sts2_install_path / "release_info.json")
    manifest_check = _read_steam_manifest(steam_manifest_path)
    dotnet_check = _check_dotnet_sdk(runner)
    template_check = _check_sts2_template(runner, dotnet_check)
    megadot_check = _check_executable("megadot", which)
    godot_check = _check_executable("godot", which)
    mods_folder_check = _check_folder(sts2_install_path / "mods")
    export_folder_check = _check_folder(export_path)

    checks = {
        "sts2_install": install_check,
        "release_info": release_check,
        "steam_manifest": manifest_check,
        "dotnet_sdk": dotnet_check,
        "sts2_template": template_check,
        "megadot": megadot_check,
        "godot": godot_check,
        "mods_folder": mods_folder_check,
        "deckseer_export_folder": export_folder_check,
    }

    blockers = _build_blockers(checks)
    warnings = _build_warnings(checks)
    status = _readiness_status(blockers)

    return {
        "preflight_type": "exporter_toolchain_preflight",
        "status": status,
        "ready": status == "ready_for_static_spike",
        "paths": {
            "sts2_install": str(sts2_install_path),
            "steam_manifest": str(steam_manifest_path),
            "mods_folder": str(sts2_install_path / "mods"),
            "deckseer_export_folder": str(export_path),
        },
        "checks": checks,
        "summary": {
            "blockers": blockers,
            "warnings": warnings,
        },
        "caveats": [
            "Read-only preflight; no tools are installed and no folders are created.",
            "The future static exporter spike must still avoid live run-state export, gameplay automation, and game-file modification outside its approved mod package.",
        ],
    }


def _check_sts2_install(path: Path) -> dict:
    exists = path.exists()
    exe = path / "SlayTheSpire2.exe"
    pck = path / "SlayTheSpire2.pck"
    release_info = path / "release_info.json"
    required = {
        "SlayTheSpire2.exe": exe.exists(),
        "SlayTheSpire2.pck": pck.exists(),
        "release_info.json": release_info.exists(),
    }
    ok = exists and all(required.values())
    return {
        "ok": ok,
        "exists": exists,
        "path": str(path),
        "required_files": required,
    }


def _read_release_info(path: Path) -> dict:
    if not path.exists():
        return {"ok": False, "path": str(path), "error": "release_info.json was not found"}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "path": str(path), "error": str(exc)}

    return {
        "ok": True,
        "path": str(path),
        "version": payload.get("version"),
        "branch": payload.get("branch"),
        "commit": payload.get("commit"),
        "date": payload.get("date"),
        "main_assembly_hash": payload.get("main_assembly_hash"),
    }


def _read_steam_manifest(path: Path) -> dict:
    if not path.exists():
        return {"ok": False, "path": str(path), "error": "Steam app manifest was not found"}
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return {"ok": False, "path": str(path), "error": str(exc)}

    return {
        "ok": True,
        "path": str(path),
        "appid": _acf_value(text, "appid"),
        "name": _acf_value(text, "name"),
        "installdir": _acf_value(text, "installdir"),
        "buildid": _acf_value(text, "buildid"),
        "branch": _acf_value(text, "BetaKey") or _acf_value(text, "userconfig"),
    }


def _check_dotnet_sdk(runner: CommandRunner) -> dict:
    result = runner(("dotnet", "--info"))
    stdout = result.stdout or ""
    stderr = result.stderr or ""
    combined = f"{stdout}\n{stderr}"
    sdk_versions = _parse_dotnet_sdk_versions(stdout)
    ok = result.returncode == 0 and bool(sdk_versions) and "No SDKs were found" not in combined
    return {
        "ok": ok,
        "command": "dotnet --info",
        "returncode": result.returncode,
        "sdk_versions": sdk_versions,
        "message": _first_relevant_line(combined),
    }


def _check_sts2_template(runner: CommandRunner, dotnet_check: dict) -> dict:
    if not dotnet_check["ok"]:
        return {
            "ok": False,
            "command": "dotnet new list Alchyr.Sts2.Templates",
            "skipped": True,
            "message": "Skipped because no .NET SDK is visible.",
        }

    result = runner(("dotnet", "new", "list", "Alchyr.Sts2.Templates"))
    combined = f"{result.stdout}\n{result.stderr}"
    lowered = combined.lower()
    ok = result.returncode == 0 and (
        "alchyr.sts2.templates" in lowered or "slay the spire" in lowered or "sts2" in lowered
    )
    return {
        "ok": ok,
        "command": "dotnet new list Alchyr.Sts2.Templates",
        "returncode": result.returncode,
        "skipped": False,
        "message": _first_relevant_line(combined),
    }


def _check_executable(name: str, which: WhichRunner) -> dict:
    path = which(name)
    return {
        "ok": path is not None,
        "command": name,
        "path": path,
    }


def _check_folder(path: Path) -> dict:
    return {
        "ok": path.exists() and path.is_dir(),
        "path": str(path),
        "exists": path.exists(),
    }


def _build_blockers(checks: dict) -> list[str]:
    blockers: list[str] = []
    if not checks["sts2_install"]["ok"] or not checks["release_info"]["ok"] or not checks["steam_manifest"]["ok"]:
        blockers.append("sts2_install")
    if not checks["dotnet_sdk"]["ok"]:
        blockers.append("dotnet_sdk")
    if not checks["sts2_template"]["ok"]:
        blockers.append("sts2_template")
    if not checks["megadot"]["ok"] and not checks["godot"]["ok"]:
        blockers.append("megadot_or_godot")
    return blockers


def _build_warnings(checks: dict) -> list[str]:
    warnings: list[str] = []
    if not checks["mods_folder"]["ok"]:
        warnings.append("mods_folder_missing")
    if not checks["deckseer_export_folder"]["ok"]:
        warnings.append("deckseer_export_folder_missing")
    return warnings


def _readiness_status(blockers: list[str]) -> str:
    if not blockers:
        return "ready_for_static_spike"
    if "sts2_install" in blockers:
        return "blocked_missing_game"
    return "blocked_missing_toolchain"


def _default_export_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "Deckseer" / "exports"
    return Path.home() / "AppData" / "Local" / "Deckseer" / "exports"


def _run_command(command: Sequence[str]) -> CommandResult:
    try:
        completed = subprocess.run(
            list(command),
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return CommandResult(returncode=1, stdout="", stderr=str(exc))
    return CommandResult(returncode=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)


def _acf_value(text: str, key: str) -> str | None:
    match = re.search(rf'"{re.escape(key)}"\s+"([^"]*)"', text)
    if match is None:
        return None
    return match.group(1)


def _parse_dotnet_sdk_versions(text: str) -> list[str]:
    lines = text.splitlines()
    versions: list[str] = []
    in_sdk_section = False
    for line in lines:
        stripped = line.strip()
        if stripped == ".NET SDKs installed:":
            in_sdk_section = True
            continue
        if in_sdk_section and stripped.startswith(".NET runtimes installed:"):
            break
        if in_sdk_section:
            match = re.match(r"([0-9][^\s]+)\s+\[", stripped)
            if match:
                versions.append(match.group(1))
    return versions


def _first_relevant_line(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return None
