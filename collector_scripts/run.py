import subprocess
import time
from p110_connect import connect_and_start_p100

python_scripts = ["direto_xr.py", "elite_rizer.py", "master_collector.py", "headwind.py"] # , "headwind.py"
print("starting scripts...")
subprocesses = []

p100 = connect_and_start_p100()
# p100 = True
if p100:
    # Loop through the other scripts and start them
    for script in python_scripts:
        process = subprocess.Popen(["python", script])
        subprocesses.append(process)
        print(f"Started {script}")
        time.sleep(15)

try:
    # Keep the script running until interrupted by the user
    while True:
        pass
except KeyboardInterrupt:
    # Handle KeyboardInterrupt (Ctrl+C) to terminate subprocesses
    print("\nTerminating subprocesses...")
    for process in subprocesses:
        process.terminate()
    print("All scripts terminated.")












# Additional cleanup or logging if needed
print("All scripts completed.")
