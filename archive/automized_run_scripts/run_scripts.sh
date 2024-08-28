#!/bin/bash

# Set the Python script to be executed 5 seconds before others
pre_execution_script="p110_connect.py"

# Set the list of Python scripts to start
python_scripts=("direto_xr.py" "elite_rizer.py" "headwind.py" "master_collector.py")
# python_scripts=("master_collector.py")

# Start the pre-execution script
python "$pre_execution_script" &

# Wait for the pre-execution script to complete
while ps | grep -v grep | grep -q "python $pre_execution_script"; do
    sleep 15
done

# Wait for an additional 5 seconds
sleep 10

# Loop through the other scripts and start them
for script in "${python_scripts[@]}"; do
    python "$script" &
    echo "Started $script"
done

echo "All scripts started successfully."
