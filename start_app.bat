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
set SCRIPT_PATH=%SOURCE_PATH%\script
set VENV_PATH=%SOURCE_PATH%\venv

echo - Checking Python is exist or not
call python --version 2>NUL
if %errorlevel%==0 (
    goto :check_virtual_env
) else (
    echo - Python is not installed in the machine, we will try to install
    call "%SCRIPT_PATH%"\install_python.bat
)

:check_virtual_env
echo - Check virtual environment is exist or not
if not exist "%VENV_PATH%" (
    echo Virtual Environment is missing, we will try to install
    call "%SCRIPT_PATH%"\create_virtual_env.bat
)

:check_source
echo - Checking source code is exist or not
if not exist "%SOURCE_PATH%" (
    echo Source code is missing, we will try to install
    call "%SCRIPT_PATH%"\download_source_code.bat
)

:invoke_file
echo - Invoking the entry point with virtual environment
call "%VENV_PATH%"\Scripts\activate

set LOCAL_ENTRY_POINT=%CD%
set IDEAL_ENTRY_POINT=%SOURCE_PATH%

if exist "%LOCAL_ENTRY_POINT%" (
    echo Try to find and invoke Entry Point at %LOCAL_ENTRY_POINT%
    set PYTHONPATH=%LOCAL_ENTRY_POINT%
    call python -m src.EntryPoint
    goto :deactivate_vir_env
)

echo Try to find and invoke ideal Entry Point at %IDEAL_ENTRY_POINT%
set PYTHONPATH=%LOCAL_ENTRY_POINT%
call python src.EntryPoint

:deactivate_vir_env
call "%VENV_PATH%"\Scripts\deactivate

endlocal
pause
:eof