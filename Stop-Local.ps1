$ErrorActionPreference = 'Stop'
foreach ($port in @(8010,3010)) {
    $listener = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -First 1
    if (!$listener) { continue }
    $ownerPid = $listener.OwningProcess
    $owner = Get-CimInstance Win32_Process -Filter "ProcessId=$ownerPid"
    $commandLine = [string]$owner.CommandLine
    $executablePath = [string]$owner.ExecutablePath
    if (!($commandLine.Replace('/', '\').Contains($PSScriptRoot) -or $executablePath.Replace('/', '\').StartsWith($PSScriptRoot))) { Write-Warning "Leaving port $port alone: owner is not identifiable as this project."; continue }
    $fresh = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($fresh.OwningProcess -eq $ownerPid) { Stop-Process -Id $ownerPid; Write-Host "Stopped CareerPilot on $port." }
}
