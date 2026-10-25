[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$packageRoot = Split-Path -Parent $PSScriptRoot
$installer = Join-Path $packageRoot 'install.ps1'
$sourceRoot = Join-Path $packageRoot 'agents'
$testRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("codex-agents-install-" + [guid]::NewGuid())
$previousCodexHome = $env:CODEX_HOME

function Assert-True {
    param(
        [bool]$Condition,
        [string]$Message
    )
    if (-not $Condition) {
        throw $Message
    }
}

function Assert-ManagedFilesMatch {
    param([string]$CodexRoot)

    $targetRoot = Join-Path $CodexRoot 'agents'
    foreach ($sourceFile in Get-ChildItem -LiteralPath $sourceRoot -File -Recurse -Force) {
        if ($sourceFile.Name -eq 'source.local.json' -or $sourceFile.Extension -eq '.pyc' -or
            $sourceFile.FullName -match '[/\\]__pycache__[/\\]') { continue }
        $relativePath = $sourceFile.FullName.Substring($sourceRoot.Length).TrimStart('\', '/')
        $targetFile = Join-Path $targetRoot $relativePath
        Assert-True (Test-Path -LiteralPath $targetFile -PathType Leaf) "Missing installed file: $relativePath"
        $sourceHash = (Get-FileHash -LiteralPath $sourceFile.FullName -Algorithm SHA256).Hash
        $targetHash = (Get-FileHash -LiteralPath $targetFile -Algorithm SHA256).Hash
        Assert-True ($sourceHash -eq $targetHash) "Installed file differs: $relativePath"
    }
}

try {
    New-Item -ItemType Directory -Path $testRoot | Out-Null

    $cleanRoot = Join-Path $testRoot 'clean'
    $env:CODEX_HOME = $cleanRoot
    & $installer
    Assert-ManagedFilesMatch $cleanRoot

    $overlay = Join-Path $cleanRoot 'agents/_invest/knowledge-map.local.md'
    Set-Content -LiteralPath $overlay -Value 'private-local-overlay' -Encoding utf8
    $wayneOverlay = Join-Path $cleanRoot 'agents/_wayne/source.local.json'
    Set-Content -LiteralPath $wayneOverlay -Value '{"epub":"private-placeholder"}' -Encoding utf8
    & $installer -Force
    Assert-ManagedFilesMatch $cleanRoot
    Assert-True ((Get-Content -Raw -LiteralPath $overlay).Trim() -eq 'private-local-overlay') 'Force update changed the private overlay.'
    Assert-True ((Get-Content -Raw -LiteralPath $wayneOverlay).Trim() -eq '{"epub":"private-placeholder"}') 'Force update changed the local book configuration.'
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $cleanRoot 'agents/_invest/_invest'))) 'Force update created nested _invest/_invest.'
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $cleanRoot 'agents/_manuel/_manuel'))) 'Force update created nested _manuel/_manuel.'

    $managedTarget = Join-Path $cleanRoot 'agents/_mantou.toml'
    Set-Content -LiteralPath $managedTarget -Value 'local-managed-change' -Encoding utf8
    $beforeWhatIf = (Get-FileHash -LiteralPath $managedTarget -Algorithm SHA256).Hash
    & $installer -Force -WhatIf
    $afterWhatIf = (Get-FileHash -LiteralPath $managedTarget -Algorithm SHA256).Hash
    Assert-True ($beforeWhatIf -eq $afterWhatIf) '-WhatIf changed a managed target file.'
    & $installer -Force
    Assert-ManagedFilesMatch $cleanRoot
    Assert-True ((Get-Content -Raw -LiteralPath $overlay).Trim() -eq 'private-local-overlay') 'Update after -WhatIf changed the private overlay.'

    $partialRoot = Join-Path $testRoot 'partial'
    $partialInvest = Join-Path $partialRoot 'agents/_invest'
    New-Item -ItemType Directory -Path $partialInvest -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $partialInvest 'existing.txt') -Value 'keep' -Encoding utf8
    $env:CODEX_HOME = $partialRoot
    $failedAsExpected = $false
    try {
        & $installer
    }
    catch {
        $failedAsExpected = $true
    }
    Assert-True $failedAsExpected 'A colliding install unexpectedly succeeded without -Force.'
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $partialRoot 'agents/_factbot.toml'))) 'Preflight failure left a partial installation.'
    Assert-True (Test-Path -LiteralPath (Join-Path $partialInvest 'existing.txt')) 'Preflight failure changed an existing file.'

    $selectiveRoot = Join-Path $testRoot 'selective'
    $env:CODEX_HOME = $selectiveRoot
    & $installer -Agent _wayne
    Assert-True (Test-Path -LiteralPath (Join-Path $selectiveRoot 'agents/_wayne/source.py')) 'Selective install missed the source reader.'
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $selectiveRoot 'agents/_manuel.toml'))) 'Selective install included an unselected agent.'
    $sentinel = Join-Path $selectiveRoot 'agents/_manuel.toml'
    Set-Content -LiteralPath $sentinel -Value 'preserve-other-agent' -Encoding utf8
    & $installer -Agent _wayne -Force
    Assert-True ((Get-Content -Raw -LiteralPath $sentinel).Trim() -eq 'preserve-other-agent') 'Selective update changed an unselected agent.'

    Write-Host 'INSTALL VALIDATION PASSED'
    Write-Host '- clean installation matches all packaged files'
    Write-Host '- forced update is idempotent and preserves private overlays'
    Write-Host '- WhatIf previews a forced update without changing managed files'
    Write-Host '- collision preflight performs no partial installation'
}
finally {
    $env:CODEX_HOME = $previousCodexHome
    if (Test-Path -LiteralPath $testRoot) {
        Remove-Item -LiteralPath $testRoot -Recurse -Force
    }
}
