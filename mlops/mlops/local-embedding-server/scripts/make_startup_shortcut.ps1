# Creates a Windows Startup .lnk that launches run_server.bat at login.
# Run from bash: powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/make_startup_shortcut.ps1
$startup = [System.IO.Path]::Combine($env:APPDATA, 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
$lnkPath = Join-Path $startup 'lightweight-embeddings.lnk'
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut($lnkPath)
$s.TargetPath = 'C:\Projects\lightweight-embeddings\run_server.bat'
$s.WorkingDirectory = 'C:\Projects\lightweight-embeddings'
$s.Description = 'lightweight-embeddings server bge-m3'
$s.WindowStyle = 1
$s.Save()
Write-Host "SHORTCUT CREATED at $lnkPath"
