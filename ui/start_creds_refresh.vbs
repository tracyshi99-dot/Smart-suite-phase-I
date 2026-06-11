Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\Users\yujiashi\Desktop\SmartSuite_Phase1\ui\refresh_creds.ps1", 0, False
