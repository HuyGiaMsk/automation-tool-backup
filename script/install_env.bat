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
set DEFAULT_INSTALL_PATH=%USERPROFILE%\AppData\Local\Programs\Python
set SOURCE_PATH=%USERPROFILE%\%OneDriveFolder%\automation_tool
set VENV_PATH=%SOURCE_PATH%\venv

:install_python
    echo --------------------------------------------------------------------------------------------------------------
    echo Start trying to install Python
    set PYTHON_VERSION=3.10.10

    call python --version 2>NUL
    if %errorlevel%==0 (
        echo Python is already installed at:
        call where python.exe
    ) else (
        mkdir %DEFAULT_INSTALL_PATH%
        echo Will install Python at %DEFAULT_INSTALL_PATH%
        curl -o python-installer.exe https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe
        python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 TargetDir=%DEFAULT_INSTALL_PATH%

        set python_script_path=%DEFAULT_INSTALL_PATH%\Python310\Scripts\
        set python_path=%DEFAULT_INSTALL_PATH%\Python310\
        setx PATH "%python_path%;%python_script_path%;%PATH%" /M
        echo Python has been added to the system PATH environment variable.
        del python-installer.exe
    )
    call python -m pip install --upgrade pip
    call pip install certifi
    call pip install requests==2.28.2

:download_source_code
    echo --------------------------------------------------------------------------------------------------------------
    echo Start trying to install the source code at %SOURCE_PATH%

    if exist "%SOURCE_PATH%" (
        echo Already contains source at %SOURCE_PATH%
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

:create_virtual_env
    echo --------------------------------------------------------------------------------------------------------------
    echo Start trying to install virtual environments

    if exist "%VENV_PATH%" (
        echo Virtual environment is already installed in %VENV_PATH%
    ) else (
        call python -m venv "%VENV_PATH%"
        call "%VENV_PATH%"\Scripts\activate

        echo Install defined packages
        pip install -r "%SOURCE_PATH%\requirements.txt"

        call "%VENV_PATH%"\Scripts\deactivate
        echo Install virtual env successfully at %VENV_PATH%
    )

echo --------------------------------------------------------------------------------------------------------------
echo Install completely
echo Please go to %SOURCE_PATH% which store to source code to read the guide in file README for understand the approach to run app

endlocal

pause

:eof
