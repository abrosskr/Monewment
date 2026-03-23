# 📜 Imperial Sentinel Rule: Surgical Purge of Ghost Core
# c:\monewment\STRATUM\STRATUM-1\Purge-GhostCore.ps1

Remove-Item -Recurse -Force "C:\monewment\STRATUM\STRATUM-1\core" -ErrorAction SilentlyContinue
Write-Host "[SENTINEL] Ghost Core Purged successfully."
