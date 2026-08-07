Set WshShell = CreateObject("WScript.Shell")
startup = WshShell.SpecialFolders("Startup")

' ── 9router on 20128 (direct, no headroom proxy) ──
Set lnk = WshShell.CreateShortcut(startup & "\9router.lnk")
lnk.TargetPath = "C:\Users\Unicorn\AppData\Roaming\npm\9router.cmd"
lnk.Arguments = "-p 20128 --no-browser --skip-update"
lnk.WorkingDirectory = "C:\Users\Unicorn"
lnk.WindowStyle = 7    ' 7 = minimized
lnk.Description = "9router direct on 20128 (no headroom proxy)"
lnk.Save

WScript.Echo "9router.lnk created in Startup"