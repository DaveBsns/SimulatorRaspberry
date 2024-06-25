## Create virtual python environment
```python -m venv .env```

## Run the virtual environment
```source ./.env/bin/activate```

## Install dependencies
```pip install -r requirements.txt```

## Control the docker container
```docker exec -it raspi-container /bin/bash```

## Start all scripts
```cd collector_scripts```
```./run_scripts.bat```

## Enable bleak logging on Linux
Insert this command into the same console where you want to start the bleak script after to set the BLEAK_LOGGING environment variable.
```export BLEAK_LOGGING=1```

## Notes
The script write_height.py in the archive folder does not work right now. More reverse Engineering to write on the Elite Rizer is required.
