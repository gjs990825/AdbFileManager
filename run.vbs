Set WshShell = CreateObject("WScript.Shell") 
WshShell.Run "cmd /c python AdbFileManager.py", 0, True
Set WshShell = Nothing