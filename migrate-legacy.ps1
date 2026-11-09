[CmdletBinding(SupportsShouldProcess)]
param()

$ErrorActionPreference = 'Stop'
$packageRoot = $PSScriptRoot
$codexRoot = [IO.Path]::GetFullPath($(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }))
$agentsRoot = Join-Path $codexRoot 'agents'
$hashes = Get-Content -Raw -LiteralPath (Join-Path $packageRoot 'migration/legacy-agent-hashes.json') | ConvertFrom-Json
$books = @{ _wayne = 'research'; _clayton = 'choice'; _alan = 'change'; _jim = 'jtbd' }
$backupRoot = Join-Path $codexRoot ('agent-migration-backups/' + [guid]::NewGuid().ToString())

# Refuse redirected paths; migration never traverses outside the selected Codex home.
function Assert-LocalPath([string]$Path) {
    $absolute = [IO.Path]::GetFullPath($Path)
    if (-not $absolute.StartsWith($codexRoot.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Migration path is outside Codex home: $absolute"
    }
    $cursor = $absolute
    while ($cursor) {
        if (Test-Path -LiteralPath $cursor) {
            if ((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Migration refuses a redirected path: $cursor"
            }
        }
        $parent = Split-Path -Parent $cursor
        if ($parent -eq $cursor) { break }
        $cursor = $parent
    }
}

# Plan the complete operation before changing files. Modified roles stay in place.
$retire = @()
$copies = @()
foreach ($property in $hashes.PSObject.Properties) {
    $name = $property.Name
    $config = Join-Path $agentsRoot "$name.toml"
    Assert-LocalPath $config
    if (Test-Path -LiteralPath $config) {
        if (-not (Test-Path -LiteralPath $config -PathType Leaf)) { throw "Expected a config file: $config" }
        $digest = (Get-FileHash -LiteralPath $config -Algorithm SHA256).Hash
        if ($digest -in $property.Value) {
            $retire += [pscustomobject]@{ Path = $config; Name = "$name.toml"; Hash = $digest }
        } else {
            Write-Warning "Preserved modified or unrecognized config: $config. Review it manually; migration is incomplete for this entrypoint."
        }
    }
    if ($books.ContainsKey($name)) {
        $source = Join-Path $agentsRoot "$name/source.local.json"
        $target = Join-Path $agentsRoot "_manuel/books/$($books[$name])/source.local.json"
        Assert-LocalPath $source
        Assert-LocalPath $target
        if (Test-Path -LiteralPath $source) {
            if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Expected a private config file: $source" }
            if (Test-Path -LiteralPath $target) {
                if (-not (Test-Path -LiteralPath $target -PathType Leaf) -or
                    (Get-FileHash -LiteralPath $source).Hash -ne (Get-FileHash -LiteralPath $target).Hash) {
                    Write-Warning "Preserved existing destination: $target. Resolve source configuration differences manually."
                }
            } else {
                $copies += [pscustomobject]@{ Source = $source; Target = $target; Name = "$name-source.local.json" }
            }
        }
    }
}
Assert-LocalPath $backupRoot
foreach ($item in $copies) {
    if ($PSCmdlet.ShouldProcess($item.Target, 'Back up and copy private source configuration; keep original')) {
        Assert-LocalPath $item.Source
        Assert-LocalPath $item.Target
        New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
        Copy-Item -LiteralPath $item.Source -Destination (Join-Path $backupRoot $item.Name)
        New-Item -ItemType Directory -Path (Split-Path -Parent $item.Target) -Force | Out-Null
        if (Test-Path -LiteralPath $item.Target) { throw "Destination appeared during migration: $($item.Target)" }
        Copy-Item -LiteralPath $item.Source -Destination $item.Target
    }
}
foreach ($item in $retire) {
    if ($PSCmdlet.ShouldProcess($item.Path, 'Back up and retire recognized legacy agent entrypoint')) {
        Assert-LocalPath $item.Path
        if ((Get-FileHash -LiteralPath $item.Path).Hash -ne $item.Hash) { throw "Config changed during migration: $($item.Path)" }
        New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
        $backup = Join-Path $backupRoot $item.Name
        Copy-Item -LiteralPath $item.Path -Destination $backup
        if ((Get-FileHash -LiteralPath $backup).Hash -ne $item.Hash) { throw 'Backup verification failed.' }
        Remove-Item -LiteralPath $item.Path
        Write-Host "Retired $($item.Name)"
    }
}
if (Test-Path -LiteralPath $backupRoot) { Write-Host "Backup: $backupRoot" }
Write-Host 'Old support directories and private files remain untouched. Restart Codex after migration.'
