' ============================================================
' Create Headroom Proxy Autostart Shortcuts
' ============================================================
' Run: cscript //nologo create_headroom_autostart.vbs
' Creates .lnk files in user's Startup folder pointing to .cmd launchers
' ============================================================

Option Explicit

Dim WshShell, startup, hermesDir

Set WshShell = CreateObject("WScript.Shell")
startup = WshShell.SpecialFolders("Startup")
hermesDir = "C:\Users\Unicorn\AppData\Local\hermes"

Dim lnk

' --- Headroom 8787 (9router) ---
Set lnk = WshShell.CreateShortcut(startup & "\Headroom-8787.lnk")
lnk.TargetPath = hermesDir & "\headroom_start_8787.cmd"
lnk.WorkingDirectory = hermesDir
lnk.WindowStyle = 7  ' 7 = minimized
lnk.Description = "Headroom proxy 8787 -> 9router (localhost:20128) with compression"
lnk.Save

' --- Headroom 8788 (agentrouter) ---
Set lnk = WshShell.CreateShortcut(startup & "\Headroom-8788.lnk")
lnk.TargetPath = hermesDir & "\headroom_start_8788.cmd"
lnk.WorkingDirectory = hermesDir
lnk.WindowStyle = 7
lnk.Description = "Headroom proxy 8788 -> agentrouter.org with compression"
lnk.Save

WScript.Echo "Headroom autostart shortcuts created:"
WScript.Echo "  " & startup & "\Headroom-8787.lnk"
WScript.Echo "  " & startup & "\Headroom-8788.lnk"
WScript.Echo ""
WScript.Echo "They will start on next Windows login."
WScript.Echo "Shortcuts point to .cmd files (most reliable on Windows)."