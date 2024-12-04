import json

def compare_data_lists(file1, file2):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)

    differences = []

    for service_uuid, subdata in data1.items():

        for charac in subdata:

            if (charac["data"] != get_dict_by_uuid(data2[service_uuid], charac["uuid"])["data"]):

                print("Change in JSON found:")
                print("Characterisic: ",charac["uuid"])
                print("Steering left:",charac["data"])
                print("Steering middle:", get_dict_by_uuid(data2[service_uuid], charac["uuid"])["data"])

def get_dict_by_uuid(characteristics, target_uuid):
    return next((char for char in characteristics if char['uuid'] == target_uuid), None)

# Usage
file1 = "left_ble_device_data.json"
file2 = "middle_ble_device_data.json"

differences = compare_data_lists(file1, file2)
#print_differences(differences)





