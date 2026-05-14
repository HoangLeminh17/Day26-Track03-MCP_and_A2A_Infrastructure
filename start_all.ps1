$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$pythonExe = $venvPython

if (-not (Test-Path $pythonExe)) {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $pythonCmd) {
        throw "Could not find Python. Activate your conda environment or install dependencies first."
    }
    $pythonExe = $pythonCmd.Source
}

$processes = @()

function Start-ServiceProcess {
    param(
        [string]$Module,
        [string]$Label,
        [int]$DelaySeconds = 0
    )

    Write-Host "Starting $Label..."
    $proc = Start-Process `
        -FilePath $pythonExe `
        -ArgumentList @("-m", $Module) `
        -WorkingDirectory $projectRoot `
        -PassThru

    $script:processes += [PSCustomObject]@{
        Label = $Label
        Process = $proc
    }

    if ($DelaySeconds -gt 0) {
        Start-Sleep -Seconds $DelaySeconds
    }
}

try {
    Start-ServiceProcess -Module "registry" -Label "Registry service on port 10000" -DelaySeconds 2
    Start-ServiceProcess -Module "tax_agent" -Label "Tax Agent on port 10102"
    Start-ServiceProcess -Module "compliance_agent" -Label "Compliance Agent on port 10103" -DelaySeconds 3
    Start-ServiceProcess -Module "law_agent" -Label "Law Agent on port 10101" -DelaySeconds 3
    Start-ServiceProcess -Module "customer_agent" -Label "Customer Agent on port 10100"

    Write-Host ""
    Write-Host "All services started:"
    Write-Host "  Registry:         http://localhost:10000"
    Write-Host "  Customer Agent:   http://localhost:10100"
    Write-Host "  Law Agent:        http://localhost:10101"
    Write-Host "  Tax Agent:        http://localhost:10102"
    Write-Host "  Compliance Agent: http://localhost:10103"
    Write-Host ""
    Write-Host "Run the test client in another terminal with:"
    Write-Host "  $pythonExe .\test_client.py"
    Write-Host ""
    Write-Host "Press Ctrl+C here to stop all services."

    while ($true) {
        Start-Sleep -Seconds 2
        foreach ($entry in $processes) {
            if ($entry.Process.HasExited) {
                throw "$($entry.Label) exited unexpectedly with code $($entry.Process.ExitCode)."
            }
        }
    }
}
finally {
    foreach ($entry in $processes) {
        if (-not $entry.Process.HasExited) {
            Stop-Process -Id $entry.Process.Id
        }
    }
}
