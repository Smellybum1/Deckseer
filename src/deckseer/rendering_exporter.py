from __future__ import annotations

import json


def render_exporter_toolchain_preflight(report: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2)

    checks = report["checks"]
    release = checks["release_info"]
    manifest = checks["steam_manifest"]
    dotnet = checks["dotnet_sdk"]
    template = checks["sts2_template"]
    megadot = checks["megadot"]
    godot = checks["godot"]
    summary = report["summary"]
    release_label = release.get("version") or "unknown"
    build_label = manifest.get("buildid") or "unknown"
    branch_label = manifest.get("branch") or release.get("branch") or "unknown"
    sdk_label = ", ".join(dotnet.get("sdk_versions") or []) if dotnet["ok"] else "missing"
    engine_paths = [check["path"] for check in (megadot, godot) if check["ok"]]
    engine_label = ", ".join(engine_paths) if engine_paths else "missing"

    lines = [
        f"Exporter Toolchain Preflight: {report['status'].upper()}",
        f"STS2 install: {_ok_label(checks['sts2_install']['ok'])} ({checks['sts2_install']['path']})",
        f"Release: {release_label} | Build: {build_label} | Branch: {branch_label}",
        f".NET SDK: {sdk_label}",
        f"STS2 template: {_ok_label(template['ok'])}",
        f"Megadot/Godot: {engine_label}",
        f"Mods folder: {_ok_label(checks['mods_folder']['ok'])} ({checks['mods_folder']['path']})",
        f"Deckseer export folder: {_ok_label(checks['deckseer_export_folder']['ok'])} ({checks['deckseer_export_folder']['path']})",
    ]
    lines.append(f"Blockers: {', '.join(summary['blockers']) if summary['blockers'] else 'none'}")
    lines.append(f"Warnings: {', '.join(summary['warnings']) if summary['warnings'] else 'none'}")
    for caveat in report.get("caveats", []):
        lines.append(f"Caveat: {caveat}")
    return "\n".join(lines)


def _ok_label(ok: bool) -> str:
    return "ok" if ok else "missing"
