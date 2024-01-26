import subprocess
from p110_connect import connect_and_start_p100
from direto_xr import scan_and_connect_direto
from elite_rizer import scan_and_connect_rizer
from headwind import scan_and_connect_headwind
# from master_collector import handle_data
import asyncio
import time

async def headwind():
    await scan_and_connect_headwind()

async def direto():
    await asyncio.sleep(10)
    await scan_and_connect_direto()

async def rizer():
    await asyncio.sleep(15)
    await scan_and_connect_rizer()

# async def master_collector():
    # await asyncio.sleep(20)
    # await handle_data()
    # subprocess.run(["python", "master_collector.py"])


async def main():
        
        headwind_task = asyncio.create_task(headwind())
        direto_task = asyncio.create_task(direto())
        rizer_task = asyncio.create_task(rizer())
        # collector_task = asyncio.create_task(master_collector())
        
        # Wait for all tasks to complete
        await asyncio.gather(headwind_task, direto_task, rizer_task) # , collector_task

# python_scripts = ["direto_xr.py", "elite_rizer.py", "headwind.py", "master_collector.py"]
print("starting...")
p100 = connect_and_start_p100()
if(p100 == True):
    if __name__ == "__main__":
        asyncio.run(main())
    
print("All scripts started successfully.")






