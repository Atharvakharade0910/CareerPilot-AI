param([Parameter(Mandatory=$true)][string]$DumpFile)
pg_restore --clean --if-exists --dbname "$env:DATABASE_URL" $DumpFile
Write-Output "Restore completed"
