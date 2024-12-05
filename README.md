# VR Bicycle Simulator Repository (HHN UniTyLab)

This Repo contains all Scripts to run the VR Bicylce Simulator in addtion to the Unity Project. 

## Hardware Sensor Overview

// IMAGE FROM BIKE SETUP

### Steering Sensor

<div style="display: flex; justify-content: space-evenly; align-items: center;">
  <img src="README_images/steering_sensor.png" alt="Steering Sensor Mount" width="300">
  <img src="README_images/handle_bar.png" alt="Handle Bar Mount" width="300">
</div>


The image on the left shows the mount of the Photoelelectrical Encoder to measure the steering angle - the right images shows the handle bar from the front. There are two boxes on the top of the handle bar. In this image the left box contains the Mircocontroller (ESP32) for the brake and the right box contains the Microcontroller (ESP32) for the Steering sensor.

### Brake Sensor

<div style="display: flex; justify-content: space-evenly; align-items: center;">
  <img src="README_images/brake_setup.png" alt="Steering Sensor Mount" width="200">
  <img src="README_images/brake_screws.png" alt="Handle Bar Mount" width="200">
  <img src="README_images/brake_block.png" alt="Handle Bar Mount" width="200">
</div>

Currently only the right hand brake is equipped with a sensor. The full setup is shown on the left image. The center images shows the mount of the hall sensor on the brake lever. If the brake sticks or does not work properly - make sure to check both screws are tight. 
The image on the right show the brake-block mounted in the V-brake - this block ensures a more realistc feeling of the brake lever.

**Important:** Make sure that the LED-light of the switch of the box is On - otherwise the brake sensor will be running with an older version!

### Elite Rizer

<div style="display: flex; justify-content: space-evenly; align-items: center;">
  <img src="README_images/rizer.png" alt="Steering Sensor Mount" width="400">
</div>

The Elite Rizer is used to adjust the height of the front axis occording to the incline in the Simulation. Be aware that this component needs to find the Zero points when being started.

### Direto 

<div style="display: flex; justify-content: space-evenly; align-items: center;">
  <img src="README_images/direto.png" alt="Steering Sensor Mount" width="400">
</div>

This component is responsible for measuring the speed of the pedals and adjusting the resistance of the pedals accourding to the incline in the simulation. 

### Roll 

<div style="display: flex; justify-content: space-evenly; align-items: center;">
  <img src="README_images/roll.png" alt="Steering Sensor Mount" width="400">
</div>

This (white) roll can be used to move backwards with the bicycle in the simulation. To go backwards the roll has to be kicked forwards.


## Repository Overview

- **`archive/`**: Archived files and scripts.
  
- **`collector_scripts/`**: Main directory for scripts handling data collection and Sensor scripts.
  
  - **`sensor_scripts/`**: Each Subdirectory contains a PlatformIO project - one for each mircocontroller (ESP32) utilising a sensor for data collection of the Bicycle setup. 

    - **`Arduino_Files/`** ---
    - **`Brake_Sensor/`** Hall sensor mounted on left brake lever (indirect brake force)
    - **`Gyro_Sensor/`** BNO055 mounted on Rocker plate (measure tilting)
    - **`Roll_Sensor/`** Roll sensor (for backward movement on bicycle)
    - **`Steering_Sensor/`** Photoelectric encoder (steering Angle)
  

  - `direto_xr.py` Script utilising BLE for reading speed from direto and writing resitance of direto
  - `elite_rizer.py` Script utilising BLE for writing front wheel height
  - `headwind.py` Script utilising BLE for writing headwind speed
  - `master_collector.py` Scripct for collecting data from microcontrollers (UDP) and sending data to Unity (UDP)
  - `master_receiver.py` Script for recieving data from Unity (UDP)
  - `p110_connect.py` Script for controlling smart plug (power supply for bicycle setup)
  - `UDP_tester.py` Srcipt for testing UDP functionality
  - `run_scripts.bat`: Batch script for running all scripts.