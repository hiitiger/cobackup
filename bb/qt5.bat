reg add "HKCR\*\shell\Qt5-vc" /ve /d Qt5-vc /f 
reg add "HKCR\*\shell\Qt5-vc\command" /ve /d "C:\Windows\System32\cmd.exe /A /Q /K C:\Qt\Qt5.9.3\5.9.3\msvc2015\bin\qtvars.bat vsvars cd %%1" /f
reg add "HKCR\Folder\shell\Qt5-vc" /ve /d Qt5-vc /f 
reg add "HKCR\Folder\shell\Qt5-vc\command" /ve /d "C:\Windows\System32\cmd.exe /A /Q /K C:\Qt\Qt5.9.3\5.9.3\msvc2015\bin\qtvars.bat vsvars cd %%1" /f