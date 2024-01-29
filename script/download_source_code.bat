@echo off

setlocal enabledelayedexpansion

:find_onedrive_mapping_folder
set "searchTerm=OneDrive "
set "OneDriveFolder=Documents"
for /d %%D in ("%USERPROFILE%\*") do (
    for %%F in ("%%~nxD") do (
        set "folderName=%%~nF"
        if /I "!folderName:~0,9!"=="!searchTerm!" (
            set "OneDriveFolder=%%~nF"
            goto :set_main_paths
        )
    )
)

:set_main_paths
set SOURCE_PATH=%USERPROFILE%\%OneDriveFolder%\automation_tool

:download_source_code
    echo --------------------------------------------------------------------------------------------------------------
    echo Start trying to install the source code at %SOURCE_PATH%

    if exist "%SOURCE_PATH%" (
        echo Already contains source at %SOURCE_PATH%
        goto :eof
    ) else (
        echo Start dumping temp download source .py
        (
            echo E^='~'
            echo B^=print
            echo import os as A^,requests as I^,zipfile as J
            echo H^='OneDrive '
            echo F^=A.path.expanduser^(E^)
            echo D^='Documents'
            echo for C in A.listdir^(F^):
            echo 	if A.path.isdir^(A.path.join^(F^,C^)^)and C.startswith^(H^):D^=C^;break
            echo G^='automation_tool'
            echo K^=A.path.join^(A.path.expanduser^(E^)^,D^,G^)
            echo def L^(^):
            echo 	if A.path.exists^(K^):B^('Already containing the source code'^)^;return
            echo 	L^=f^"https://github.com/hungdoan-tech/automation-tool/archive/main.zip^"^;B^('Start download source'^)^;H^=I.get^(L^)
            echo 	if H.status_code^=^=200:
            echo 		C^=A.path.join^(A.path.expanduser^(E^)^,D^)^;F^=A.path.join^(C^,'automated_task.zip'^)
            echo 		with open^(F^,'wb'^)as M:M.write^(H.content^)
            echo 		B^('Download source successfully'^)
            echo 		with J.ZipFile^(F^,'r'^)as N:N.extractall^(C^)
            echo 		A.rename^(A.path.join^(C^,'automation-tool-main'^)^,A.path.join^(C^,G^)^)^;A.remove^(F^)^;B^(f^"Extracted source code and placed it in ^{C^}^"^)
            echo 	else:B^('Failed to download the source'^)
            echo if __name__^=^='__main__':L^(^)
        ) > temporary_download_source.py

        echo Invoke temp download source .py
        call python temporary_download_source.py

        echo Invoke temp download source .py complete
        del temporary_download_source.py
    )

endlocal
:eof
