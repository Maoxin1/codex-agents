[CmdletBinding()]
param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$packageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceRoot = Join-Path $packageRoot "agents"
$codexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$targetRoot = Join-Path $codexRoot "agents"

New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null

$items = @("_factbot.toml", "_mantou.toml", "_manuel.toml", "_manuel")
foreach ($item in $items) {
    $source = Join-Path $sourceRoot $item
    $target = Join-Path $targetRoot $item
    if ((Test-Path -LiteralPath $target) -and -not $Force) {
        throw "Target already exists: $target. Re-run with -Force to overwrite."
    }
    Copy-Item -LiteralPath $source -Destination $target -Recurse -Force:$Force
}

Write-Host "Installed _factbot, _mantou, and _manuel to $targetRoot"
Write-Host "Restart Codex to reload custom agents."
