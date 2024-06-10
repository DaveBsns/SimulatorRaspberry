@echo off

REM Set the Python script to be executed 5 seconds before others
set pre_execution_script="p110_connect.py"

ping 127.0.0.1 -n 50 > nul  REM pings to delay the script5

REM Set the list of Python scripts to start
set python_scripts=("direto_xr.py", "elite_rizer3.py", "headwind.py", "master_collector.py") 

REM Start the pre-execution script
start "" python %pre_execution_script%

REM Wait for the pre-execution script to complete
:wait_for_pre_execution
echo Pre execution script started
ping 127.0.0.1 -n 6 > nul
tasklist | find "python.exe" | findstr "%pre_execution_script%" > nul
if errorlevel 1 goto pre_execution_completed
goto wait_for_pre_execution

:pre_execution_completed
REM Wait for an additional 5 seconds
timeout 5 >NUL

REM Loop through the other scripts and start them
for %%i in %python_scripts% do (
    start "" python %%i
    echo Started %%i
)

echo All scripts started successfully.