[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$packageRoot = Split-Path -Parent $PSScriptRoot
$installer = Join-Path $packageRoot 'install.ps1'
$testRoot = Join-Path ([IO.Path]::GetTempPath()) ('codex-agents-install-' + [guid]::NewGuid())
$previousCodexHome = $env:CODEX_HOME
function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}
function Assert-Roles([string]$Root, [string[]]$Names) {
    $actual = @(Get-ChildItem -LiteralPath (Join-Path $Root 'agents') -Filter '*.toml' | Select-Object -ExpandProperty BaseName)
    Assert-True ((($actual | Sort-Object) -join ',') -eq (($Names | Sort-Object) -join ',')) "Unexpected installed roles: $actual"
}
function Assert-ManagedFilesMatch([string]$Root) {
    foreach ($entry in (Get-Content -Raw (Join-Path $packageRoot 'managed-files.json') | ConvertFrom-Json)) {
        $target = Join-Path $Root $entry
        Assert-True (Test-Path -LiteralPath $target -PathType Leaf) "Missing: $entry"
        Assert-True ((Get-FileHash -LiteralPath $target).Hash -eq (Get-FileHash -LiteralPath (Join-Path $packageRoot $entry)).Hash) "Mismatch: $entry"
    }
}
try {
    New-Item -ItemType Directory -Path $testRoot | Out-Null
    $env:CODEX_HOME = Join-Path $testRoot 'clean'
    & $installer
    Assert-Roles $env:CODEX_HOME @('_manuel', '_mantou')
    Assert-ManagedFilesMatch $env:CODEX_HOME
    foreach ($book in @('research', 'choice', 'change', 'jtbd')) {
        Assert-True (Test-Path -LiteralPath (Join-Path $env:CODEX_HOME "agents/_manuel/books/$book/source.py")) "Missing reader: $book"
    }
    $private = Join-Path $env:CODEX_HOME 'agents/_manuel/context.local.md'
    $source = Join-Path $env:CODEX_HOME 'agents/_manuel/books/choice/source.local.json'
    $unmanaged = Join-Path $env:CODEX_HOME 'agents/_manuel/custom-note.md'
    Set-Content -LiteralPath $private -Value 'synthetic-context'
    Set-Content -LiteralPath $source -Value '{"epub":"synthetic-book"}'
    Set-Content -LiteralPath $unmanaged -Value 'synthetic-note'
    $toml = Join-Path $env:CODEX_HOME 'agents/_mantou.toml'
    Set-Content -LiteralPath $toml -Value 'synthetic-local-change'
    & $installer -Force -WhatIf
    Assert-True ((Get-Content -Raw $toml).Trim() -eq 'synthetic-local-change') 'WhatIf changed TOML.'
    & $installer -Force
    Assert-ManagedFilesMatch $env:CODEX_HOME
    Assert-Roles $env:CODEX_HOME @('_manuel', '_mantou')
    Assert-True ((Get-Content -Raw $private).Trim() -eq 'synthetic-context') 'Private context changed.'
    Assert-True ((Get-Content -Raw $source).Trim() -eq '{"epub":"synthetic-book"}') 'Source overlay changed.'
    Assert-True ((Get-Content -Raw $unmanaged).Trim() -eq 'synthetic-note') 'Unmanaged note changed.'
    Assert-True (-not (Test-Path (Join-Path $env:CODEX_HOME 'agents/_manuel/_manuel'))) 'Nested package created.'
    foreach ($name in @('_manuel', '_mantou')) {
        $env:CODEX_HOME = Join-Path $testRoot $name
        & $installer -Agent $name
        Assert-Roles $env:CODEX_HOME @($name)
        & $installer -Agent $name -Force
        Assert-Roles $env:CODEX_HOME @($name)
    }
    $env:CODEX_HOME = Join-Path $testRoot 'explicit-pair'
    & $installer -Agent _mantou,_manuel,_manuel
    Assert-Roles $env:CODEX_HOME @('_manuel', '_mantou')
    foreach ($name in @('_wayne', '_clayton', '_alan', '_jim', '_factbot', '_invest')) {
        $env:CODEX_HOME = Join-Path $testRoot "rejected-$name"
        $failed = $false
        try { & $installer -Agent $name } catch { $failed = $true }
        Assert-True $failed "Retired role accepted: $name"
        Assert-True (-not (Test-Path -LiteralPath $env:CODEX_HOME)) 'Rejected role left files.'
    }
    $env:CODEX_HOME = Join-Path $testRoot 'rejected-all'
    $failed = $false
    try { & $installer -All } catch { $failed = $true }
    Assert-True $failed 'Retired All option accepted.'
    Assert-True (-not (Test-Path -LiteralPath $env:CODEX_HOME)) 'Rejected All option left files.'
    $env:CODEX_HOME = Join-Path $testRoot 'collision'
    New-Item -ItemType Directory -Path (Join-Path $env:CODEX_HOME 'agents/_mantou') -Force | Out-Null
    $failed = $false
    try { & $installer } catch { $failed = $true }
    Assert-True $failed 'Collision unexpectedly succeeded.'
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $env:CODEX_HOME 'agents/_manuel.toml'))) 'Collision left partial installation.'
    $fixture = Join-Path $testRoot 'fixture'
    New-Item -ItemType Directory -Path (Join-Path $fixture 'agents/_manuel') -Force | Out-Null
    Copy-Item -LiteralPath $installer -Destination (Join-Path $fixture 'install.ps1')
    Set-Content -LiteralPath (Join-Path $fixture 'managed-files.json') -Value '["agents/_manuel.toml","agents/_manuel/core.md"]'
    Set-Content -LiteralPath (Join-Path $fixture 'agents/_manuel.toml') -Value '# synthetic'
    Set-Content -LiteralPath (Join-Path $fixture 'agents/_manuel/core.md') -Value 'public-core'
    Set-Content -LiteralPath (Join-Path $fixture 'agents/_manuel/context.local.md') -Value 'source-private'
    Set-Content -LiteralPath (Join-Path $fixture 'agents/_manuel/private-note.md') -Value 'source-private-note'
    $env:CODEX_HOME = Join-Path $testRoot 'fixture-target'
    & (Join-Path $fixture 'install.ps1') -Agent _manuel
    Assert-True (-not (Test-Path (Join-Path $env:CODEX_HOME 'agents/_manuel/context.local.md'))) 'Private overlay leaked.'
    Assert-True (-not (Test-Path (Join-Path $env:CODEX_HOME 'agents/_manuel/private-note.md'))) 'Unlisted note leaked.'
    $before = (Get-FileHash (Join-Path $env:CODEX_HOME 'agents/_manuel.toml')).Hash
    Set-Content -LiteralPath (Join-Path $fixture 'agents/_manuel.toml') -Value '# changed'
    Remove-Item -LiteralPath (Join-Path $fixture 'agents/_manuel/core.md')
    $failed = $false
    try { & (Join-Path $fixture 'install.ps1') -Agent _manuel -Force } catch { $failed = $true }
    Assert-True $failed 'Missing source unexpectedly installed.'
    Assert-True ((Get-FileHash (Join-Path $env:CODEX_HOME 'agents/_manuel.toml')).Hash -eq $before) 'Missing source left partial update.'
    Write-Host 'INSTALL VALIDATION PASSED: exactly two roles; supported selections; retired options rejected; overlays, preview and preflight preserved.'
}
finally {
    $env:CODEX_HOME = $previousCodexHome
    $resolved = [IO.Path]::GetFullPath($testRoot)
    $tempPrefix = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
    if (-not $resolved.StartsWith($tempPrefix, [StringComparison]::OrdinalIgnoreCase) -or (Split-Path -Leaf $resolved) -notlike 'codex-agents-install-*') { throw 'Unsafe cleanup path.' }
    if (Test-Path -LiteralPath $resolved) { Remove-Item -LiteralPath $resolved -Recurse -Force }
}
