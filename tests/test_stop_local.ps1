# Run from the project root: powershell -NoProfile -File tests/test_stop_local.ps1
# All process operations are mocked; this test never stops real services.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$testState = [pscustomobject]@{
    Stopped = [System.Collections.Generic.List[int]]::new()
    UnknownOwner = $null
}

function Get-NetTCPConnection {
    param($State, $LocalPort, $ErrorAction)
    [pscustomobject]@{ OwningProcess = $LocalPort }
}
function Get-CimInstance {
    param($ClassName, $Filter)
    if ($Filter -eq 'ProcessId=8010') { return $testState.UnknownOwner }
    [pscustomobject]@{
        CommandLine = "python --app-dir `"$projectRoot\backend`""
        ExecutablePath = $null
    }
}
function Stop-Process {
    param($Id)
    $testState.Stopped.Add($Id)
}

# A vanished process, unavailable metadata, and an unrelated process must all
# be preserved while the subsequent identifiable project process is stopped.
foreach ($unknownOwner in @(
    $null,
    [pscustomobject]@{ CommandLine = $null; ExecutablePath = $null },
    [pscustomobject]@{ CommandLine = 'unrelated service'; ExecutablePath = $null }
)) {
    $testState.UnknownOwner = $unknownOwner
    $testState.Stopped.Clear()
    & (Join-Path $projectRoot 'Stop-Local.ps1')
    if ($testState.Stopped.Count -ne 1 -or $testState.Stopped[0] -ne 3010) {
        throw 'Shutdown must skip the unknown owner and continue to the project process.'
    }
}
Write-Output 'PASS: unavailable and unrelated owners are preserved; project shutdown continues.'
