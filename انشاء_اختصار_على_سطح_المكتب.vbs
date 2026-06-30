' This script creates a desktop shortcut for the launcher
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = oWS.SpecialFolders("Desktop") & "\نظام البناء.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = WScript.ScriptFullName
oLink.TargetPath = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\")) & "تشغيل_الموقع.bat"
oLink.WorkingDirectory = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\") - 1)
oLink.Description = "نظام إدارة تكاليف البناء"
oLink.WindowStyle = 1
oLink.Save
MsgBox "تم إنشاء الاختصار على سطح المكتب بنجاح!" & Chr(10) & "يمكنك الآن النقر عليه مباشرة لتشغيل الموقع.", 64, "تم"
