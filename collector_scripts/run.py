import concurrent.futures
import subprocess
from p110_connect import connect_and_start_p100
import time


def execute_script(script):
    subprocess.run(["python", script])

python_scripts = ["direto_xr.py", "elite_rizer.py", "headwind.py", "master_collector.py"]
print("starting scripts...")
p100 = connect_and_start_p100()
# p100 = True
if(p100 == True):
    # Start the scripts concurrently using a ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(execute_script, script): script for script in python_scripts}
            # Wait for all scripts to complete or manually stop them
        try:
            for future in concurrent.futures.as_completed(futures):
                # If any exception occurred in the script, it will be raised here
                future.result()
        except KeyboardInterrupt:
            print("Stopping scripts...")
    
print("All scripts started successfully.")












# Additional cleanup or logging if needed
print("All scripts completed.")
