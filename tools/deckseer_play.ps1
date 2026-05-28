param(
    [string]$StatePath = "",
    [switch]$Once,
    [switch]$Quiet,
    [switch]$ShowIdle,
    [string]$DataDir = "",
    [double]$Interval = 2.0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$defaultStatePath = "%LOCALAPPDATA%\Deckseer\exports\latest_state.json"
$stateDisplay = $defaultStatePath
if ($StatePath.Trim().Length -gt 0) {
    $stateDisplay = $StatePath
}

Write-Host "Deckseer local play helper"
Write-Host "Read-only: no game launch, no mod install, no input automation, no startup service."
Write-Host "Alerts say whether Codex attention is useful."
Write-Host ""
Write-Host "When an alert fires, pause in-game and inspect first:"
Write-Host "  deckseer inspect-export `"$stateDisplay`""
Write-Host "Then confirm manually before asking for advice:"
Write-Host "  deckseer recommend-export `"$stateDisplay`" --confirmed --format text"
Write-Host ""

$alertArgs = @("export-alert")
if ($StatePath.Trim().Length -gt 0) {
    $alertArgs += $StatePath
}
if ($Once) {
    $alertArgs += "--once"
}
if ($Quiet) {
    $alertArgs += "--quiet"
}
if ($ShowIdle) {
    $alertArgs += "--show-idle"
}
$dataDirDisplay = Join-Path $repoRoot "data"
if ($DataDir.Trim().Length -gt 0) {
    $dataDirDisplay = $DataDir
}
$alertArgs += "--data-dir"
$alertArgs += $dataDirDisplay
if ($Interval -ne 2.0) {
    $alertArgs += "--interval"
    $alertArgs += $Interval.ToString([Globalization.CultureInfo]::InvariantCulture)
}

$pythonCandidates = @()
if ($env:DECKSEER_PYTHON -and $env:DECKSEER_PYTHON.Trim().Length -gt 0) {
    $pythonCandidates += $env:DECKSEER_PYTHON
}

$repoVenvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (Test-Path -LiteralPath $repoVenvPython) {
    $pythonCandidates += $repoVenvPython
}

$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($null -ne $pythonCommand) {
    $pythonCandidates += $pythonCommand.Source
}

$bundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if (Test-Path -LiteralPath $bundledPython) {
    $pythonCandidates += $bundledPython
}

$previousPythonPath = $env:PYTHONPATH
try {
    $srcPath = Join-Path $repoRoot "src"
    if ($previousPythonPath -and $previousPythonPath.Trim().Length -gt 0) {
        $env:PYTHONPATH = "$srcPath;$previousPythonPath"
    } else {
        $env:PYTHONPATH = $srcPath
    }

    $deckseerCommand = Get-Command deckseer -ErrorAction SilentlyContinue
    if ($null -ne $deckseerCommand) {
        & $deckseerCommand.Source @alertArgs
        exit $LASTEXITCODE
    }

    foreach ($python in $pythonCandidates) {
        if ($python -and (Test-Path -LiteralPath $python)) {
            & $python -m deckseer.cli @alertArgs
            exit $LASTEXITCODE
        }
    }

    $pyCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($null -ne $pyCommand) {
        & $pyCommand.Source -3 -m deckseer.cli @alertArgs
        exit $LASTEXITCODE
    }
} finally {
    $env:PYTHONPATH = $previousPythonPath
}

Write-Error "Could not find deckseer, DECKSEER_PYTHON, repo .venv Python, python, bundled Python, or py launcher."
exit 1
