#!/bin/bash

# List of Python scripts to start
python_scripts=("read_speed.py")

# Loop through the scripts and start them
for script in "${python_scripts[@]}"; do
    nohup python3 "$script" > "${script%.py}.log" 2>&1 &
    echo "Started $script"
done

echo "All scripts started successfully."