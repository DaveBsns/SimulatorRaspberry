# Getting Started
## General
### Clone the repository
```git clone https://github.com/DaveBsns/BicycleSimulatorData.git```

### Change directory into the root folder of the repository
```cd BicycleSimulatorData```

## Windows
### Create virtual python environment
```python -m venv .env```

### Run the virtual environment
```source ./.env/Scripts/activate```

### Install dependencies
```pip install -r requirements.txt```

### Navigate to data collection scripts
```cd collector_scripts```

### Start the data collection scripts
```./run_scrits.bat```

## Linux
### Create virtual python environment
```python -m venv .env```

### Run the virtual environment
```source ./.env/bin/activate```

### Install dependencies
```pip install -r requirements.txt```

### Control the docker container
```docker exec -it raspi-container /bin/bash```

## Further Information
### Enable bleak logging on Linux
Insert this command into the same console where you want to start the bleak script after to set the BLEAK_LOGGING environment variable.
```export BLEAK_LOGGING=1```

### Notes
- The script write_height.py in the archive folder does not work right now. More reverse Engineering to write on the Elite Rizer is required.
- If the simulator didn't start successfully turn the Tapo smart-plug on manually. 

