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
    foreach ($entry in (Get-Content -Raw -LiteralPath (Join-Path $packageRoot 'managed-files.json') | ConvertFrom-Json)) {
        $sourceFile = Get-Item -LiteralPath (Join-Path $packageRoot $entry)
        $relativePath = $entry.Substring('agents/'.Length)
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
    foreach ($advisor in @('_clayton', '_alan', '_jim')) {
        $localSource = Join-Path $cleanRoot "agents/$advisor/source.local.json"
        Set-Content -LiteralPath $localSource -Value '{"epub":"private-book-placeholder"}' -Encoding utf8
    }
    & $installer -Agent _clayton,_alan,_jim -Force
    foreach ($advisor in @('_clayton', '_alan', '_jim')) {
        $localSource = Join-Path $cleanRoot "agents/$advisor/source.local.json"
        Assert-True ((Get-Content -Raw -LiteralPath $localSource).Trim() -eq '{"epub":"private-book-placeholder"}') "Update changed private source for $advisor"
    }
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

    $singleBookRoot = Join-Path $testRoot 'single-book'
    $env:CODEX_HOME = $singleBookRoot
    & $installer -Agent _jim
    Assert-True (Test-Path -LiteralPath (Join-Path $singleBookRoot 'agents/_book_sources/epub.py')) 'Book advisor install omitted its shared reader.'
    Assert-True (Test-Path -LiteralPath (Join-Path $singleBookRoot 'agents/_jim/source.py')) 'Book advisor install omitted its entry point.'
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $singleBookRoot 'agents/_alan.toml'))) 'Single book install included another advisor.'

    # An ignored overlay in the source checkout must never become managed.
    $fixturePackage = Join-Path $testRoot 'fixture-package'
    $fixtureInvest = Join-Path $fixturePackage 'agents/_invest'
    New-Item -ItemType Directory -Path $fixtureInvest -Force | Out-Null
    Copy-Item -LiteralPath $installer -Destination (Join-Path $fixturePackage 'install.ps1')
    Set-Content -LiteralPath (Join-Path $fixturePackage 'managed-files.json') -Value '["agents/_invest.toml", "agents/_invest/core.md"]'
    Set-Content -LiteralPath (Join-Path $fixturePackage 'agents/_invest.toml') -Value '# fixture'
    Set-Content -LiteralPath (Join-Path $fixtureInvest 'core.md') -Value 'managed-core'
    Set-Content -LiteralPath (Join-Path $fixtureInvest 'knowledge-map.local.md') -Value 'source-private'
    Set-Content -LiteralPath (Join-Path $fixtureInvest 'private-note.md') -Value 'source-note'
    $env:CODEX_HOME = $cleanRoot
    & (Join-Path $fixturePackage 'install.ps1') -Agent _invest -Force
    Assert-True ((Get-Content -Raw -LiteralPath $overlay).Trim() -eq 'private-local-overlay') 'Source overlay overwrote destination overlay.'
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $cleanRoot 'agents/_invest/private-note.md'))) 'Unmanaged source note was installed.'
    $env:CODEX_HOME = Join-Path $testRoot 'fixture-clean'
    & (Join-Path $fixturePackage 'install.ps1') -Agent _invest
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $env:CODEX_HOME 'agents/_invest/knowledge-map.local.md'))) 'Source overlay leaked into clean installation.'

    # A missing managed source must fail before replacing any destination files.
    Set-Content -LiteralPath (Join-Path $fixturePackage 'agents/_invest.toml') -Value '# changed fixture'
    Remove-Item -LiteralPath (Join-Path $fixtureInvest 'core.md')
    $env:CODEX_HOME = $cleanRoot
    $beforeMissing = (Get-FileHash -LiteralPath (Join-Path $cleanRoot 'agents/_invest.toml')).Hash
    $failedAsExpected = $false
    try { & (Join-Path $fixturePackage 'install.ps1') -Agent _invest -Force }
    catch { $failedAsExpected = $true }
    Assert-True $failedAsExpected 'Missing managed source unexpectedly installed.'
    Assert-True ((Get-FileHash -LiteralPath (Join-Path $cleanRoot 'agents/_invest.toml')).Hash -eq $beforeMissing) 'Missing source left a partial update.'

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
