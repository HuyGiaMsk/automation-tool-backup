# **Guide to run this automation tool** 
Please note that this tool is currently only use for Window, still not support for other operating systems

Please do not rename the source code folder or move it out of %OneDrive_Mapping_Folder%

Please don't run it while recording screen (recorder + automation tool make will make your machine be so slow)

Note the below %OneDrive_Mapping_Folder% could be **OneDrive - ABCXYZ** in your case
If you don't have any OneDrive mapping folder - then source would be placed in your folder Documents

### - If you encounter any issues with env, run this batch file _install_env_ to install env again
set OneDrive_Mapping_Folder=OneDrive - ABCXYZ
%USERPROFILE%\"%OneDrive_Mapping_Folder%"\automation_tool\script\install_env.bat

### - Navigate the shell (cmd) to the source code folder
set OneDrive_Mapping_Folder=OneDrive - ABCXYZ
cd %USERPROFILE%\"%OneDrive_Mapping_Folder%"\automation_tool

### - Provide mandatory info at .\input\InvokedClasses.properties and its subsequence properties file which stand for the setting of each running task 
notepad %USERPROFILE%\"%OneDrive_Mapping_Folder%"\automation_tool\input\InvokedClasses.properties

### - Perform the provided automation task by invoke _start_app_
%USERPROFILE%\"%OneDrive_Mapping_Folder%"\automation_tool\start_app.bat

### - After running, all the log will be stored at .\log
cd %USERPROFILE%\"%OneDrive_Mapping_Folder%"\automation_tool\log

You may need it if the running process encounter any issues, it will be helpful to investigate what happened and went wrong
