@echo off

REM List of Python scripts to start
set python_scripts=("direto_xr.py", "elite_rizer.py", "headwind.py", "master_collector.py")

REM Loop through the scripts and start them
for %%i in %python_scripts% do (
    start "" python %%i
    echo Started %%i
)

echo All scripts started successfully.