Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """c:\Users\yujiashi\Desktop\SmartSuite_Phase1\ui\.venv\Scripts\python.exe"" -m http.server 8080 --directory ""c:\Users\yujiashi\Desktop\SmartSuite_Phase1\ui""", 0, False
