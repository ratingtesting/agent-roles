# PowerShell Shortcut Patterns for Windows Autostart

## Create/Update Shortcut
```powershell
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\9router.lnk")
$Shortcut.TargetPath = "C:\Users\Unicorn\AppData\Roaming\npm\9router.cmd"
$Shortcut.Arguments = "-p 20128 --no-browser --skip-update"
$Shortcut.WorkingDirectory = "C:\Users\Unicorn"
$Shortcut.WindowStyle = 7  # minimized
$Shortcut.Description = "9router direct on 20128 (no headroom proxy)"
$Shortcut.Save()
```

## Verify Shortcut
```powershell
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\9router.lnk")
Write-Host "Target: $($Shortcut.TargetPath)"
Write-Host "Args: $($Shortcut.Arguments)"
Write-Host "WorkingDir: $($Shortcut.WorkingDirectory)"
Write-Host "Description: $($Shortcut.Description)"
Write-Host "WindowStyle: $($Shortcut.WindowStyle)"  # 1=normal, 3=max, 7=min
```

## Remove Shortcut
```powershell
Remove-Item "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Headroom-8787.lnk" -ErrorAction SilentlyContinue
Remove-Item "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Headroom-8788.lnk" -ErrorAction SilentlyContinue
```

## List All Startup Shortcuts
```powershell
Get-ChildItem "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\" *.lnk | ForEach-Object {
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($_.FullName)
    [PSCustomObject]@{
        Name = $_.BaseName
        Target = $Shortcut.TargetPath
        Args = $Shortcut.Arguments
        WorkDir = $Shortcut.WorkingDirectory
        Desc = $Shortcut.Description
    }
} | Format-Table -AutoSize
```

## Run via cmd (bypassing PowerShell parsing issues)
```cmd
cmd /c "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -ExecutionPolicy Bypass -File C:\path\to\script.ps1"
```