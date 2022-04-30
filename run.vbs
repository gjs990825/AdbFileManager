Set WshShell = CreateObject("WScript.Shell") 
WshShell.Run "cmd /c runner.cmd", 0, True
Set WshShell = Nothing