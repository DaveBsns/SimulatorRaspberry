from matplotlib import pyplot as plt
import ast
from datetime import datetime

def get_log_dict_v1(line: str) -> tuple[float, dict] | None:
    """
    Reads a dictonary from a line of a logfile with format: <%Y-%m-%d %H:%M:%S,%f> <LOGLEVEL> <DICT> 
    Returns: tuple[unix timestamp, dictonary]
    """
    parts = line.split(" ", 3)

    if len(parts) != 4:
        return None
    
    date, time, loglevel, content = parts

    try:
        timestamp = datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M:%S,%f")
        timestamp_unix = timestamp.timestamp()
        content = content.lstrip().rstrip()
        content_dict = ast.literal_eval(content)
    except:
        return None
    
    return timestamp_unix, content_dict

def get_log_dict_v2(line: str) -> tuple[float, dict] | None:
    """
    Reads a dictonary from a line of a logfile with format: <LOGLEVEL>:<LOGGER>:<DICT> 
    Returns: tuple[unix timestamp, dictonary]
    """
    parts = line.split(":", 2)

    if len(parts) != 3:
        return None
    
    loglevel, logger, content = parts

    try:
        content = content.lstrip().rstrip()
        content_dict = ast.literal_eval(content)
        timestamp_unix = content_dict["time"]
    except:
        return None
    
    return timestamp_unix, content_dict



# Log Version 1
# log_dict_fn = get_log_dict_v1
# with open("delay_test_1.log.txt") as f:
#     data = f.readlines()

# Log Version 2
log_dict_fn = get_log_dict_v2
with open("delay_test_2.log.txt") as f:
    data = f.readlines()

# Generate lists of time and data
start_time = None
time = []
hall_speed = []
direto_speed = []

for line in data:
    result = log_dict_fn(line)

    if result is None:
        continue

    if start_time is None:
        start_time = result[0]
    
    time.append(result[0] - start_time)
    hall_speed.append(result[1].get("rotationValue"))
    direto_speed.append(result[1].get("diretoSpeed"))

# Plotting
fig = plt.figure()
plt.plot(time, hall_speed, label="Hall Effect Sensor [U/s]")
plt.plot(time, direto_speed, label="Direto Sensor [No Unit]")
plt.legend()
plt.xlabel("Time [s]")
plt.ylabel("Speed")
plt.show()

