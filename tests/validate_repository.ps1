[CmdletBinding()]
param(
    [switch]$AllowModelOverride
)

$ErrorActionPreference = 'Stop'
$packageRoot = Split-Path -Parent $PSScriptRoot
Push-Location $packageRoot

try {
    $pythonCommand = Get-Command 'python' -ErrorAction SilentlyContinue
    $pythonArguments = @()
    if ($null -eq $pythonCommand) {
        $pythonCommand = Get-Command 'py' -ErrorAction SilentlyContinue
        $pythonArguments = @('-3')
    }
    if ($null -eq $pythonCommand) {
        throw "Python 3.11 or later is required. Install Python and expose either 'python' or the Windows 'py' launcher."
    }

    & (Join-Path $PSScriptRoot 'validate_install.ps1')

    $env:PYTHONIOENCODING = 'utf-8'
    $pythonChecks = @(
        @('tests/validate_content.py'),
        @('-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py'),
        @('agents/_factbot/tests/validate_factbot.py'),
        @('-m', 'unittest', 'discover', '-s', 'agents/_invest/tests', '-p', 'test_*.py'),
        @('agents/_invest/tests/validate_invest.py'),
        @('agents/_mantou/tests/validate_mantou.py'),
        @('agents/_manuel/tests/validate_manuel.py')
    )
    foreach ($arguments in $pythonChecks) {
        if ($AllowModelOverride -and $arguments[0] -like 'agents/*/tests/validate_*.py') {
            $arguments += '--allow-model-override'
        }
        & $pythonCommand.Source @pythonArguments @arguments
        if ($LASTEXITCODE) {
            throw "Python validation failed: $($pythonCommand.Name) $($pythonArguments + $arguments -join ' ')"
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
