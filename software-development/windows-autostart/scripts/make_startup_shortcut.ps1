# Create a per-user Windows "run at login" shortcut in the Startup folder.
# Run with: powershell.exe -NoProfile -ExecutionPolicy Bypass -File "<this file>"
# Edit the three values below for the target service.

$startup = [System.IO.Path]::Combine($env:APPDATA, 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
$lnkPath = Join-Path $startup 'lightweight-embeddings.lnk'   # <- shortcut filename

$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut($lnkPath)
$s.TargetPath       = 'C:\Projects\lightweight-embeddings\run_server.bat'   # <- .bat/.exe to launch
$s.WorkingDirectory = 'C:\Projects\lightweight-embeddings'                  # <- cwd
$s.Description       = 'lightweight-embeddings server bge-m3'              # <- NO parentheses
$s.WindowStyle       = 1                                                    # 1 normal, 7 minimized
$s.Save()
Write-Host "SHORTCUT CREATED at $lnkPath"
