@echo off

REM check if argument is passed
if "%1"=="" (
    echo Please provide an argument
    exit \b
)

REM Run the python script
python main.py %1