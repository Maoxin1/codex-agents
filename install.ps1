[CmdletBinding(SupportsShouldProcess)]
param(
    [switch]$Force,
    [switch]$All,
    [ValidateSet('_factbot', '_invest', '_mantou', '_manuel', '_wayne', '_clayton', '_alan', '_jim')]
    [string[]]$Agent = @('_manuel', '_mantou')
)

$ErrorActionPreference = "Stop"
$packageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceRoot = Join-Path $packageRoot "agents"
$codexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$targetRoot = Join-Path $codexRoot "agents"

if ($All) {
    if ($PSBoundParameters.ContainsKey('Agent')) { throw 'Choose either -All or -Agent.' }
    $Agent = @('_factbot', '_invest', '_mantou', '_manuel', '_wayne', '_clayton', '_alan', '_jim')
}

$items = @($Agent | Select-Object -Unique | ForEach-Object { "${_}.toml"; $_ })
$dependencies = @('_book_sources')
if ('_manuel' -in $Agent) {
    $dependencies += @('_wayne', '_clayton', '_alan', '_jim') | Where-Object { $_ -notin $Agent }
    $items += $dependencies | Where-Object { $_ -ne '_book_sources' }
}
if (@($Agent | Where-Object { $_ -in @('_manuel', '_clayton', '_alan', '_jim') }).Count) {
    $items += '_book_sources'
}
foreach ($name in @('_wayne', '_clayton', '_alan', '_jim')) {
    if ($name -in $Agent -and -not (Test-Path -LiteralPath (Join-Path $targetRoot "$name.toml"))) {
        $dependencies += $name
    }
}

# Validate the complete operation before writing anything. This prevents a
# collision discovered late in the list from leaving a partial installation.
foreach ($item in $items) {
    $source = Join-Path $sourceRoot $item
    $target = Join-Path $targetRoot $item
    if (-not (Test-Path -LiteralPath $source)) {
        throw "Package source is missing: $source"
    }
    if ((Test-Path -LiteralPath $target) -and -not $Force -and $item -notin $dependencies) {
        throw "Target already exists: $target. Re-run with -Force to overwrite."
    }
}

# Only explicitly packaged files are managed; source checkout overlays stay private.
$manifest = @(Get-Content -Raw -LiteralPath (Join-Path $packageRoot 'managed-files.json') | ConvertFrom-Json)
$selectedFiles = @($manifest | Where-Object {
    $entry = $_
    @($items | Where-Object { $entry -eq "agents/$_" -or $entry.StartsWith("agents/$_/") }).Count -gt 0
})
foreach ($item in $items) {
    if (-not @($selectedFiles | Where-Object { $_ -eq "agents/$item" -or $_.StartsWith("agents/$item/") }).Count) {
        throw "No managed files listed for: $item"
    }
}
foreach ($entry in $selectedFiles) {
    if ($entry -notmatch '^agents/[A-Za-z0-9_./-]+$' -or $entry -match '(^|/)\.\.(/|$)' -or
        $entry -match '(^|/)(source\.local\.json|knowledge-map\.local\.md|context\.local\.md)$') {
        throw "Invalid managed file entry: $entry"
    }
    if (-not (Test-Path -LiteralPath (Join-Path $packageRoot $entry) -PathType Leaf)) {
        throw "Managed source is missing: $entry"
    }
}
$reusedFiles = @()
if (-not $Force) {
    foreach ($entry in $selectedFiles) {
        if (-not @($dependencies | Where-Object { $entry.StartsWith("agents/$_/") }).Count) { continue }
        $existing = Join-Path $codexRoot $entry
        if (Test-Path -LiteralPath $existing) {
            if (-not (Test-Path -LiteralPath $existing -PathType Leaf) -or
                (Get-FileHash -LiteralPath $existing).Hash -ne
                (Get-FileHash -LiteralPath (Join-Path $packageRoot $entry)).Hash) {
                throw "Shared dependency differs: $existing. Review the update and re-run with -Force."
            }
            $reusedFiles += $entry
        }
    }
}
if (-not $PSCmdlet.ShouldProcess($targetRoot, "Install managed Codex agent files")) {
    Write-Host "No files changed. Target would be $targetRoot"
    return
}
foreach ($entry in $selectedFiles) {
    if ($entry -in $reusedFiles) { continue }
    $targetFile = Join-Path $codexRoot $entry
    New-Item -ItemType Directory -Path (Split-Path -Parent $targetFile) -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $packageRoot $entry) -Destination $targetFile -Force:$Force
}

Write-Host "Installed $($Agent -join ', ') to $targetRoot"
Write-Host "Restart Codex to reload custom agents."
