Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "powershell -ExecutionPolicy Bypass -File """ & Replace(WScript.ScriptFullName, "Start Smart Suite.vbs", "start_all.ps1") & """", 1, False
