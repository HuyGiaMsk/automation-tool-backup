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
set VENV_PATH=%SOURCE_PATH%\venv

:create_virtual_env
    echo --------------------------------------------------------------------------------------------------------------
    echo Start trying to install virtual environments

    if exist "%VENV_PATH%" (
        echo Virtual environment is already installed in %VENV_PATH%
        goto :eof
    ) else (
        call python -m venv "%VENV_PATH%"
        call "%VENV_PATH%"\Scripts\activate

        echo Install defined packages
        pip install -r "%SOURCE_PATH%\requirements.txt"

        call "%VENV_PATH%"\Scripts\deactivate
        echo Install virtual env successfully at %VENV_PATH%
    )

endlocal
:eof