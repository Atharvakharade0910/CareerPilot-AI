param([string]$OutputDir = "./backups")
New-Item -ItemType Directory -Force $OutputDir | Out-Null
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
pg_dump "$env:DATABASE_URL" --format=custom --file (Join-Path $OutputDir "careerpilot-$stamp.dump")
Write-Output "Backup written to $OutputDir"
