$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$logRoot = Join-Path $projectRoot 'private/logs'
New-Item -ItemType Directory -Force $logRoot | Out-Null
# Resume this workspace's isolated database when it is present.
$localCluster = [IO.Path]::GetFullPath((Join-Path $projectRoot '../../work/pgdata'))
$pgCtl = 'C:/Program Files/PostgreSQL/18/bin/pg_ctl.exe'
if (!(Get-NetTCPConnection -State Listen -LocalPort 55432 -ErrorAction SilentlyContinue) -and (Test-Path (Join-Path $localCluster 'PG_VERSION')) -and (Test-Path $pgCtl)) {
    & $pgCtl -D $localCluster -l (Join-Path $logRoot 'postgres.log') -o '-p 55432 -h 127.0.0.1' start
    if ($LASTEXITCODE -ne 0) { throw 'Could not start the local CareerPilot database.' }
}
foreach ($port in @(8010,3010)) {
    $listener = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($listener) {
        $owner = Get-CimInstance Win32_Process -Filter "ProcessId=$($listener.OwningProcess)"
        if (!($owner.CommandLine.Replace('/', '\').Contains($projectRoot) -or $owner.ExecutablePath.Replace('/', '\').StartsWith($projectRoot))) { throw "Port $port is occupied. Check its owner before starting." }
        Write-Host "CareerPilot is already listening on $port."
    } else {
        if ($port -eq 8010) {
            $exe = Join-Path $projectRoot 'backend/.venv/Scripts/python.exe'
            Start-Process $exe -ArgumentList '-m','uvicorn','app.main:app','--app-dir',('"'+(Join-Path $projectRoot 'backend')+'"'),'--host','127.0.0.1','--port','8010' -WorkingDirectory (Join-Path $projectRoot 'backend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logRoot 'backend.log') -RedirectStandardError (Join-Path $logRoot 'backend-error.log')
        } else {
            $next = Join-Path $projectRoot 'frontend/node_modules/next/dist/bin/next'
            Start-Process 'node' -ArgumentList ('"'+$next+'"'),'start','-p','3010','-H','127.0.0.1' -WorkingDirectory (Join-Path $projectRoot 'frontend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logRoot 'frontend.log') -RedirectStandardError (Join-Path $logRoot 'frontend-error.log')
        }
    }
}
Write-Host 'Open http://localhost:3010. PostgreSQL must already be running and npm run build must have completed.'
