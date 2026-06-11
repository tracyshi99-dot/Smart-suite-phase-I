Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c cd /d C:\Users\yujiashi\Desktop\SmartSuite_Phase1\ui && .venv\Scripts\streamlit.exe run app.py --server.headless true", 0, False
