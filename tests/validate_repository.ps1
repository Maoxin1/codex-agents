[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$packageRoot = Split-Path -Parent $PSScriptRoot
Push-Location $packageRoot

try {
    & (Join-Path $PSScriptRoot 'validate_install.ps1')

    $env:PYTHONIOENCODING = 'utf-8'
    $pythonChecks = @(
        @('tests/validate_content.py'),
        @('agents/_factbot/tests/validate_factbot.py'),
        @('-m', 'unittest', 'discover', '-s', 'agents/_invest/tests', '-p', 'test_*.py'),
        @('agents/_invest/tests/validate_invest.py'),
        @('agents/_mantou/tests/validate_mantou.py'),
        @('agents/_manuel/tests/validate_manuel.py')
    )
    foreach ($arguments in $pythonChecks) {
        & python @arguments
        if ($LASTEXITCODE) {
            throw "Python validation failed: python $($arguments -join ' ')"
        }
    }

    $parseErrors = @()
    Get-ChildItem -Recurse -Filter '*.ps1' | ForEach-Object {
        $tokens = $null
        $errors = $null
        [void][System.Management.Automation.Language.Parser]::ParseFile(
            $_.FullName,
            [ref]$tokens,
            [ref]$errors
        )
        $parseErrors += $errors
    }
    if ($parseErrors.Count) {
        $parseErrors | Format-List
        throw "PowerShell parsing failed with $($parseErrors.Count) error(s)."
    }

    Write-Host 'REPOSITORY VALIDATION PASSED'
}
finally {
    Pop-Location
}
