[CmdletBinding(SupportsShouldProcess)]
param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$packageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceRoot = Join-Path $packageRoot "agents"
$codexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$targetRoot = Join-Path $codexRoot "agents"

$items = @(
    "_factbot.toml",
    "_factbot",
    "_invest.toml",
    "_invest",
    "_mantou.toml",
    "_mantou",
    "_manuel.toml",
    "_manuel"
)

# Validate the complete operation before writing anything. This prevents a
# collision discovered late in the list from leaving a partial installation.
foreach ($item in $items) {
    $source = Join-Path $sourceRoot $item
    $target = Join-Path $targetRoot $item
    if (-not (Test-Path -LiteralPath $source)) {
        throw "Package source is missing: $source"
    }
    if ((Test-Path -LiteralPath $target) -and -not $Force) {
        throw "Target already exists: $target. Re-run with -Force to overwrite."
    }
}

if (-not $PSCmdlet.ShouldProcess($targetRoot, "Install managed Codex agent files")) {
    Write-Host "No files changed. Target would be $targetRoot"
    return
}

New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null

# Copy managed files to their exact relative paths. Copying a directory onto an
# existing directory would create _invest/_invest or _manuel/_manuel. File-level
# updates also preserve unmanaged local files such as knowledge-map.local.md.
foreach ($item in $items) {
    $source = Join-Path $sourceRoot $item
    if (Test-Path -LiteralPath $source -PathType Leaf) {
        $sourceFiles = @(Get-Item -LiteralPath $source -Force)
    }
    else {
        $sourceFiles = @(Get-ChildItem -LiteralPath $source -File -Recurse -Force)
    }
    foreach ($sourceFile in $sourceFiles) {
        $relativePath = $sourceFile.FullName.Substring($sourceRoot.Length).TrimStart('\', '/')
        $targetFile = Join-Path $targetRoot $relativePath
        $targetDirectory = Split-Path -Parent $targetFile
        New-Item -ItemType Directory -Path $targetDirectory -Force | Out-Null
        Copy-Item -LiteralPath $sourceFile.FullName -Destination $targetFile -Force:$Force
    }
}

Write-Host "Installed _factbot, _invest, _mantou, and _manuel to $targetRoot"
Write-Host "Restart Codex to reload custom agents."
